#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import Tuber
from Tuber import TuberLogger
from Tuber import TuberMessageError, TuberIOError

from argparse import ArgumentParser
from configparser import ConfigParser
import time
import sys


def makeAdapter(type, direction, **kwargs):
    if type == 'gts':
        if direction == 'input':
            host, port = kwargs['bind'].split(':')
        else:
            host, port = kwargs['connect'].split(':')
        port = int(port)
        return Tuber.TCPAdapter(direction, host, port)
    elif type == 'kafka':
        bootstrap_servers = kwargs.pop('bootstrap_servers').split(',')
        topic = kwargs.pop('topic')
        return Tuber.KafkaAdapter(direction, bootstrap_servers, topic, **kwargs)
    elif type == 'null':
        return Tuber.NullAdapter(direction)
    else:
        raise ValueError('Unsupported type: {}'.format(type))


def main():
    TuberLogger.info('Starting')

    receiver = None
    sender = None

    try:
        # parse command line options
        arg_parser = ArgumentParser()
        arg_parser.add_argument("tube")
        arg_parser.add_argument("--config", "-c", default="/etc/tuber.ini")
        args = arg_parser.parse_args()

        # parse config file
        config = ConfigParser()
        config.read(args.config)

        output_conf = {key: value for (key, value) in config.items('{}:output'.format(args.tube))}
        output_type = output_conf.pop('type')

        input_conf = {key: value for (key, value) in config.items('{}:input'.format(args.tube))}
        input_type = input_conf.pop('type')

        # create our adapters
        sender = makeAdapter(output_type, 'output', **output_conf)
        receiver = makeAdapter(input_type, 'input', **input_conf)
    except Exception as e:
        TuberLogger.exception(e)
        sys.stderr.write(str(e) + '\n')
        sys.stderr.write('Stacktrace logged\n')
    else:
        try:
            while True:
                msg = None

                while True:
                    try:
                        msg = receiver.receive()
                    except TuberMessageError as e:
                        TuberLogger.error('Error processing message {}: {}'.format(msg.ahl, e))
                        break
                    except TuberIOError as e:
                        TuberLogger.error('{}: retrying in 5 seconds'.format(e))
                        time.sleep(5)
                    else:
                        TuberLogger.info('{} received from {}'.format(msg.ahl, receiver))
                        break

                if not msg:
                    continue

                while True:
                    try:
                        sender.send(msg)
                    except TuberMessageError as e:
                        TuberLogger.error('Error processing message {}: {}'.format(msg.ahl, e))
                        break
                    except TuberIOError as e:
                        TuberLogger.error('{}: retrying in 5 seconds'.format(e))
                        time.sleep(5)
                    else:
                        TuberLogger.info('{} delivered to {}'.format(msg.ahl, sender))
                        break


        except Exception as e:
            TuberLogger.exception(e)
            sys.exit(1)

    TuberLogger.info('Shutting down')
