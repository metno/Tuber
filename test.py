#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import Tuber

if __name__ == "__main__":
    sender = Tuber.TCPAdapter('output', '10.99.3.117', 15000)
    receiver = Tuber.TCPAdapter('input', '0.0.0.0', 15000)
    
    for msg in receiver:
        print(msg)
        print('\n##########################\n')
        sender.send(msg)
