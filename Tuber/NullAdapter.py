#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tuber import BaseAdapter, TuberLogger
import time

class NullAdapter(BaseAdapter):
    """
    An adapter that produces nothing and discards all
    messages. Useful for testing/debugging.
    """

    def __init__(self, direction): #pylint: disable=E1003
        super().__init__(direction)  #pylint: disable=E1004
        if direction == 'input':
            TuberLogger.info('Using NullAdapter for input')
        else:
            TuberLogger.info('Using NullAdapter for output')

    def receive(self):
        while True:
            time.sleep(60)

    def send(self, message):
        pass
