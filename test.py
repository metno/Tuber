#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys

import Tuber

if __name__ == "__main__":
    
    while True:
        sender = Tuber.TCPAdapter('output', '10.99.3.117', 15000)
        receiver = Tuber.TCPAdapter('input', '0.0.0.0', 15000)

        for msg in receiver:
            ahl = Tuber.findAHL(msg)
            sys.stderr.write('{} received\n'.format(ahl.group(0)))

            try:
                sender.send(msg)
                sys.stderr.write('{} sent\n'.format(ahl.group(0)))
            except ConnectionError as e:
                sys.stderr.write('{}\n'.format(e))
                receiver._connect()
