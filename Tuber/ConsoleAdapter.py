#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tuber import BaseAdapter
import time

class ConsoleAdapter(BaseAdapter):
    """
    An adapter that 'sends' by printing to stdout. Useful for testing/debugging.
    """

    def __init__(self, direction): #pylint: disable=E1003
        super().__init__(direction)  #pylint: disable=E1004
        self.url = 'stdout'

    def receive(self):
        while True:
            time.sleep(60)

    def send(self, message):
        delimiter = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print(delimiter)
        print(repr(message))
        print(delimiter)
