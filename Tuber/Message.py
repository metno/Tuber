#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import re
import hashlib

from Tuber import TuberMessageError

class Message:
    re_ahl = re.compile(br'[A-Z]{4}\d{2} [A-Z]{4} \d{6}( [A-Z]{3})?')

    def __init__(self, raw_message):
        # find ahl
        m = self.re_ahl.search(raw_message)
        if not m:
            raise TuberMessageError('No ahl found in {}...'.format(raw_message[:100]))
        self.ahl = raw_message[m.start():m.end()]
        self.ahl = self.ahl.decode('ascii', 'ignore')
        self.wmobulletin = raw_message[m.start():]

        # parse headers
        self.headers = []
        raw_headers = raw_message[:m.start()]
        for raw_line in raw_headers.splitlines():
            line = raw_line.strip()
            if not line: # ignore empty lines
                continue
            if not b'#' in line:
                raise TuberMessageError('Expected a header, found: "{}"'.format(line))
            if re.match(rb'[#]+$', line): # ignore border lines
                continue
            self.headers.append(line)

        # build md5 hash
        self.hash = hashlib.md5(self.wmobulletin).digest() #pylint: disable=E1101

    def add_header(self, header):
        self.headers.append(b'# ' + bytes(header.strip(), 'ascii', 'ignore'))

    def serialize(self):
        serialized = b'\n'.join(self.headers) + b'\n'
        return  serialized + self.wmobulletin
