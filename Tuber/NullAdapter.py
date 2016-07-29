#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tuber import BaseAdapter, TuberLogger

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
        return None

    def send(self, message):
        pass
