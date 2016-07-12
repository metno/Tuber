#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from Tuber.BaseAdapter import BaseAdapter
from Tuber import TuberParseError, TuberIncompleteMessage

import socket
import sys
import errno
import time
import re
import string

class TCPAdapter(BaseAdapter):
    """
    Adapter for communicating with GTS TCP sockets
    """

    re_message_start = re.compile(rb'^\x01\r\r\n(?P<csn>\d{0,5})\r\r\n')
    re_message_end = re.compile(rb'\r\r\n\x03$')


    def __init__(self, direction, host, port):
        super().__init__(direction)
        self.host = host
        self.port = port

        self.csn_digits = 3

        self._socket = None
        self._buffer = b''
        self._csn = 0

        self._connect()

    def receive(self):
        while True:
            chunk = self._socket.recv(4096)
            print('received: {}'.format(chunk))
            if len(chunk) == 0:
                sys.stderr.write('Remote host closed the connection\n')

            self._buffer = self._buffer + chunk
            if len(self._buffer) == 0:
                raise StopIteration('All remaining messages proccessed')

            try:
                msg = self._parse_message()
                return msg
            except TuberIncompleteMessage: #raised when we do not have a complete message in the buffer
                pass
            except Exception as e:
                sys.stderr.write('Error parsing message: {}\n'.format(e))

    def send(self, message):
        message = bytes(message)
        csn = bytes(str(self._csn).zfill(self.csn_digits), 'ascii')

        encoded_msg = b'\x01\r\r\n' + csn + b'\r\r\n' + message + b'\r\r\n\x03'

        length = bytes(str(len(encoded_msg)).zfill(8), 'ascii')
        encoded_msg = length + b'BI' + encoded_msg

        total_sent = 0
        while total_sent < len(encoded_msg):
            sent = self._socket.send(encoded_msg[total_sent:])
            if sent == 0:
                raise ConnectionError('Error writing to socket')
            total_sent = total_sent + sent

        print('sent: {}'.format(encoded_msg))

        self._csn = self._csn + 1 % pow(10, self.csn_digits)

    def _connect(self):
        while True:
            try:
                if self.direction == 'input':
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.bind((self.host, self.port))
                    s.listen(0)
                    sys.stderr.write('Waiting for connection\n')
                    self._socket, address = s.accept()
                    sys.stderr.write('Connection accepted from {}\n'.format(address))
                else:
                    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sys.stderr.write('Connecting to {}:{}\n'.format(self.host, self.port))
                    self._socket.connect((self.host, self.port))
                break
            except (OSError, ConnectionRefusedError) as e:
                    sys.stderr.write('{}. Retrying in 10 seconds\n'.format(e))
                    time.sleep(10)


    def _parse_message(self):
        """
        Attempt to parse a single message from the buffer.

        Raises IndexError if the buffer does not contain a complete message.
        Raises ValueError if unable to parse the message

        Returns a mesage as bytes
        """

        raw_msg = None
        length = None

        pos = 0 # our current position in the buffer

        length = self._buffer[:8]
        pos = 8
        try:
            length = int(length)
        except ValueError:
            raise TuberParseError('Invalid message length {}'.format(length))

        raw_msg = self._buffer[:length + 10] # length and type fields takes 10 bytes
        if len(raw_msg) < length + 10:
            raise TuberIncompleteMessage('Message not complete')

        msg_type = raw_msg[pos:pos + 2]
        if msg_type not in [b'BI', b'AB', b'FX']:
            raise TuberParseError('Ivalid message type {}'.format(msg_type))
        pos = pos + 2

        start_match = self.re_message_start.match(raw_msg[pos:])
        if not start_match:
            raise TuberParseError('Message start not found (found {})'.format(raw_msg[pos:pos + 20]))

        if start_match.group('csn'):
            self._csn = int(start_match.group('csn'))
        pos = pos + start_match.end(0)
        start_pos = pos

        end_match = self.re_message_end.search(raw_msg[pos:])
        if not end_match:
            raise TuberParseError('Message end not found (found {})'.format(raw_msg[-20:]))
        end_pos = pos + end_match.start(0)

        msg = raw_msg[start_pos:end_pos]
        self._buffer = self._buffer[len(raw_msg):]

        return msg

    def __del__(self):
        if self._socket:
            self._socket.close()
