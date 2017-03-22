#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import unittest

from Tuber.Message import Message
from Tuber import TuberMessageError

class TestMessage(unittest.TestCase):

    raw_message_with_headers = b"""# queue-time=2016-07-13T12:30:26.996266+0000
SADL32 EDZO 130020\r\r
METAR EDDB 130020Z 36003KT CAVOK 17/11 Q1011 NOSIG=
"""

    def test_parse(self):
        """
        Test if we get any exceptions when parsing a message with headers.
        """
        m = Message(self.raw_message_with_headers)

    def test_invalid_ahl(self):
        with self.assertRaises(TuberMessageError):
            Message(b"""# queue-time=2016-07-13T12:30:26.996266+0000
SADL32 EDZO\r\r
METAR EDDB 130020Z 36003KT CAVOK 17/11 Q1011 NOSIG=
""")

    def test_invalid_header(self):
        with self.assertRaises(TuberMessageError):
            Message(b"""missing-hash=2016-07-13T12:30:26.996266+0000
SADL32 EDZO 130020\r\r
METAR EDDB 130020Z 36003KT CAVOK 17/11 Q1011 NOSIG=
""")

    def test_missing_CR(self):
        with self.assertRaises(TuberMessageError):
            Message(b"""# queue-time=2016-07-13T12:30:26.996266+0000
SADL32 EDZO
METAR EDDB 130020Z 36003KT CAVOK 17/11 Q1011 NOSIG=
""")

if __name__ == '__main__':
    unittest.main()
