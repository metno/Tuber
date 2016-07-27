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
import signal


class SignalHandler():

    def __init__(self):
        self.signal_caught = False
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal(self, signum, frame):
        TuberLogger.info('Received signal {}'.format(signum))
        self.signal_caught = True


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

        # deal with SIGTERM and SIGINT
        signal_handler = SignalHandler()
    except Exception as e:
        TuberLogger.exception(e)
        sys.stderr.write(str(e) + '\n')
        sys.stderr.write('Stacktrace logged\n')
    else:
        try:
            msg = None
            while not signal_handler.signal_caught:
                while not msg and not signal_handler.signal_caught:
                    try:
                        msg = receiver.receive()
                        TuberLogger.info('{} received from {}'.format(msg.ahl, receiver))
                    except TuberMessageError as e:
                        TuberLogger.error('Error processing message {}: {}'.format(msg.ahl, e))
                        break
                    except TuberIOError as e:
                        TuberLogger.error('{}: retrying in 5 seconds'.format(e))
                        time.sleep(5)

                while msg:
                    try:
                        sender.send(msg)
                        TuberLogger.info('{} delivered to {}'.format(msg.ahl, sender))
                        msg = None
                    except TuberMessageError as e:
                        TuberLogger.error('Error processing message {}: {}'.format(msg.ahl, e))
                        msg = None
                        break
                    except TuberIOError as e:
                        TuberLogger.error('{}: retrying in 5 seconds'.format(e))
                        time.sleep(5)

        except Exception as e:
            TuberLogger.exception(e)
            sys.exit(1)

    TuberLogger.info('Shutting down')
