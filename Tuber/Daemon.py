#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import Tuber
from Tuber import TuberLogger
from Tuber import TuberMessageError, TuberIOError, TuberUserError

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from argparse import ArgumentParser
import time
import sys
import signal
import collections

class SignalException(Exception):
    def __init__(self, signum):
        signal_names = collections.defaultdict(lambda : "Unkown signal",
                                               ((2, "SIGINT"),
                                                (14, "SIGALRM"),
                                                (15, "SIGTERM")))

        if sys.version_info.major == 3:
            super().__init__('Receivced ' + signal_names[signum]) #pylint: disable=E1004
        else:
            super(SignalException, self).__init__('Receivced ' + signal_names[signum])
        self.signum = signum


def handle_signal(signum, frame):
    raise SignalException(signum)


def makeAdapter(type, direction, **kwargs):
    try:
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
            raise TuberUserError('Unsupported type: {}'.format(type))
    except KeyError as e:
        raise TuberUserError('Missing key {} in configuration file for {} {} adapter'.format(
            str(e), type, direction))


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
        config = configparser.ConfigParser()
        config.read(args.config)

        output_conf = {key: value for (key, value) in config.items('{}:output'.format(args.tube))}
        if 'type' not in output_conf:
            raise TuberUserError('Type not set in section {}:output'.format(args.tube))
        output_type = output_conf.pop('type')

        input_conf = {key: value for (key, value) in config.items('{}:input'.format(args.tube))}
        if 'type' not in input_conf:
            raise TuberUserError('Type not set in section {}:input'.format(args.tube))
        input_type = input_conf.pop('type')

        # create our adapters
        sender = makeAdapter(output_type, 'output', **output_conf)
        receiver = makeAdapter(input_type, 'input', **input_conf)

        # deal with SIGTERM and SIGINT
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    except (TuberIOError, TuberUserError, configparser.Error) as e:
        sys.stderr.write(str(e) + '\n')
        TuberLogger.error(e)
    except Exception as e:
        sys.stderr.write(e.__class__.__name__ + ': ' + str(e) + '\n')
        TuberLogger.exception(e)
    else:
        # start forwarding messages
        done = False
        msg = None
        while True:
            try:
                if not msg and not done:
                    msg = receiver.receive()
                    TuberLogger.info('{} received from {}'.format(msg.ahl, receiver))

                if msg:
                    sender.send(msg)
                    TuberLogger.info('{} delivered to {}'.format(msg.ahl, sender))
                    msg = None

                if done:
                    break

            except TuberMessageError as e:
                TuberLogger.error("Dropping message. Reason: " + str(e))
                msg = None
            except TuberIOError as e:
                TuberLogger.error('{}: retrying in 5 seconds'.format(e))
                time.sleep(5)
            except SignalException as e:
                TuberLogger.info(str(e))
                if e.signum != 14:
                    # break out of the loop when we have sent the current msg
                    done = True
                    # set an alarm in case the last send() takes too long
                    signal.alarm(1)
                else:
                    sys.exit(1)
            except Exception as e:
                TuberLogger.exception(e)
                sys.exit(1)

    TuberLogger.info('Shutting down')
