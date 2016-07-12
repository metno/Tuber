#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import Tuber
from Tuber import TuberLogger, WMOBulletin

from argparse import ArgumentParser
from urllib.parse import urlsplit

def makeAdapter(url, direction):
    split = urlsplit(url)

    if split.scheme == 'gts':
        return Tuber.TCPAdapter(direction, split.hostname, split.port)
    elif split.scheme == 'kafka':
        topic = split.path[1:] # remove the leading slash
        return Tuber.KafkaAdapter(direction, split.hostname, split.port, topic)
    else:
        raise ArgumentError("Unsupported protocol {} in {}: ".format(split.scheme, url))

def main():
    TuberLogger.info('Starting')

    parser = ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()

    while True:
        try:
            sender = makeAdapter(args.destination, 'output')
            receiver = makeAdapter(args.source, 'input')

            for msg in receiver:
                ahl = WMOBulletin.findAHL(msg).decode('ascii', 'ignore')
                TuberLogger.info('received {}'.format(ahl))

                sender.send(msg)
                TuberLogger.info('sent {}'.format(ahl))

        except ConnectionError as e:
            TuberLogger.error(str(e))
        except Exception as e:
            TuberLogger.exception(e)
