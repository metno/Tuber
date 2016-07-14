#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from Tuber import BaseAdapter
from Tuber import TuberParseError, TuberIncompleteMessage
from Tuber import TuberLogger
from Tuber import Message

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
            # first, check if we already have an unprocessed message waiting in our buffer
            try:
                msg = self._parse_message()
                return msg
            except TuberIncompleteMessage:
                pass # try again when we have received more data from the socket
            except Exception as e:
                TuberLogger.error('Error parsing message: {}'.format(e))

            # receive data from our socket and add it to our buffer
            chunk = self._socket.recv(4096)
            if len(chunk) == 0:
                raise ConnectionResetError()
            self._buffer = self._buffer + chunk


    def send(self, message):
        csn = bytes(str(self._csn).zfill(self.csn_digits), 'ascii')

        encoded_msg = b'\x01\r\r\n' + csn + b'\r\r\n' + message.wmobulletin + b'\r\r\n\x03'

        length = bytes(str(len(encoded_msg)).zfill(8), 'ascii')
        encoded_msg = length + b'BI' + encoded_msg

        total_sent = 0
        while total_sent < len(encoded_msg):
            sent = self._socket.send(encoded_msg[total_sent:])
            if sent == 0:
                raise ConnectionError('Error writing to socket')
            total_sent = total_sent + sent

        self._csn = self._csn + 1 % pow(10, self.csn_digits)

    def _connect(self):
        while True:
            try:
                if self.direction == 'input':
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.bind((self.host, self.port))
                    s.listen(0)
                    TuberLogger.info('Listening on {}:{}'.format(self.host, self.port))
                    self._socket, address = s.accept()
                    TuberLogger.info('Connection accepted from {}:{}\n'.format(address[0], address[1]))
                    # update the url now that we know who we're talking to
                    self.url = 'gts://{}:{}'.format(address[0], address[1])
                else:
                    self.url = 'gts://{}:{}'.format(self.host, self.port)

                    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    TuberLogger.info('Connecting to {}'.format(self.url))
                    self._socket.connect((self.host, self.port))
                    TuberLogger.info('Connected to {}'.format(self.url))

                break
            except (OSError, ConnectionRefusedError) as e:
                    TuberLogger.error('{}. Retrying in 10 seconds'.format(e))
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

        # check if there is something to work on in the buffer
        if len(self._buffer) <= 10:
            raise TuberIncompleteMessage('Message not complete')

        length = self._buffer[:8]
        pos = 8
        try:
            length = int(length)
        except ValueError:
            self._buffer = self._buffer[:8]
            raise TuberParseError('Invalid message length {}'.format(length))

        raw_msg = self._buffer[:length + 10] # length and type fields takes 10 bytes
        if len(raw_msg) < length + 10:
            raise TuberIncompleteMessage('Message not complete')

        # remove the chunk we're working on from the buffer so we do not attempt to
        # reprocess it we must throw an exception
        self._buffer = self._buffer[len(raw_msg):]

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

        return Message(raw_msg[start_pos:end_pos])

    def __del__(self):
        if self._socket:
            TuberLogger.info('Closing connection to {}'.format(self.url))
            self._socket.close()
            self._socket = None
