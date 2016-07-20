#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import Tuber
from Tuber import TuberLogger
from Tuber import TuberMessageError, TuberIOError

from argparse import ArgumentParser
from urllib.parse import urlsplit
import time
import sys

def makeAdapter(url, direction):
    split = urlsplit(url)

    if split.scheme == 'gts':
        return Tuber.TCPAdapter(direction, split.hostname, split.port)
    elif split.scheme == 'kafka':
        topic = split.path[1:] # remove the leading slash
        return Tuber.KafkaAdapter(direction, split.hostname, split.port, topic)
    elif split.scheme == 'null':
        return Tuber.NullAdapter(direction)
    else:
        raise ArgumentError("Unsupported protocol {} in {}: ".format(split.scheme, url))


def main():
    TuberLogger.info('Starting')

    parser = ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()


    receiver = None
    sender = None
    try:
        sender = makeAdapter(args.destination, 'output')
        receiver = makeAdapter(args.source, 'input')
    except TuberIOError as e:
        TuberLogger.error(e)
        sys.stderr.write(str(e) + '\n')
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
