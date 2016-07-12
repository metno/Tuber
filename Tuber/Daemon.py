#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import Tuber

from argparse import ArgumentParser
from urllib.parse import urlsplit

def makeAdapter(url, direction):
    split = urlsplit(url)

    if split.scheme == 'gts':
        return Tuber.TCPAdapter(direction, split.hostname, split.port)
    else:
        raise ArgumentError("Unsupported protocol {} in {}: ".format(split.scheme, url))

def main():
    parser = ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()

    while True:
        try:
            sender = makeAdapter(args.destination, 'output')
            receiver = makeAdapter(args.source, 'input')

            for msg in receiver:
                sender.send(msg)

        except ConnectionError as e:
            sys.stderr.write(str(e))
