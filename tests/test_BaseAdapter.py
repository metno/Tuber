#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import unittest

from Tuber.Message import Message
from Tuber.BaseAdapter import BaseAdapter
from Tuber import TuberMessageError

dummy_msgstring = b'# Header=value\nTTAA00 CCCC 000000\r\r\nDummy'


class MockedBaseAdapter(BaseAdapter):
    """
    Override unimplemented functions with dummies
    """
    
    def _send(self, message):
        pass

    def receive(self):
        return Message(dummy_msgstring)


class TestBaseAdapter(unittest.TestCase):
    
    def test_detect_duplicate(self):
        a = MockedBaseAdapter('output')
        a.send(Message(dummy_msgstring))
        with self.assertRaises(TuberMessageError):
            a.send(Message(dummy_msgstring))
