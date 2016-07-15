#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import re
import hashlib

from Tuber import TuberMessageError

class Message:
    re_ahl = re.compile(br'[A-Z]{4}\d{2} [A-Z]{4} \d{6}( [A-Z]{3})?')
    re_header = re.compile(r'^#(.*)=(.*)')

    def __init__(self, raw_message):
        m = self.re_ahl.search(raw_message)
        if not m:
            raise TuberMessageError('No ahl found in {}...'.format(raw_message[:20]))
        self.ahl = raw_message[m.start():m.end()]
        self.ahl = self.ahl.decode('ascii', 'ignore')
        self.wmobulletin = raw_message[m.start():]

        self.headers = {}
        raw_headers = raw_message[:m.start()].decode('ascii', 'ignore')
        for line in raw_headers.splitlines():
            m = self.re_header.search(line)
            if not m:
                raise TuberMessageError('Unable to parse header {}...'.format(line[:20]))
            self.set_header(m.group(1), m.group(2))

        self.hash = hashlib.md5(self.wmobulletin).digest()

    def set_header(self, key, value):
        self.headers[key.lower().strip()] = (key, value)

    def get_header(self, key):
        return self.headers[key.lower().strip()][1]

    def serialize(self):
        serialized = b''
        for v in self.headers.values():
            header = '# ' + v[0] + '=' + v[1]
            serialized = serialized + header.encode('ascii', 'ignore') + b'\n'
        serialized = serialized + self.wmobulletin
        return serialized
