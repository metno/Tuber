#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from .BaseAdapter import BaseAdapter

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

    def __init__(self, direction, host, port):
        super().__init__(direction)
        self.host = host
        self.port = port

        self._socket = None
        self._buffer = b''
        self._csn = 0
        
        self.csn_digits = 3
        
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
                               
    def receive(self):
        while True:
            chunk = self._socket.recv(4096)
            if len(chunk) == 0:
                sys.stderr.write('Remote host closed the connection\n')
            
            self._buffer = self._buffer + chunk
            if len(self._buffer) == 0:
                raise StopIteration('All remaining messages proccessed')

            try:
                msg = self._parse_message()
                return msg
            except IndexError: #rased when we do not have a complete message in the buffer 
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

        self._csn = self._csn + 1 % pow(10, self.csn_digits)

        
    def _parse_message(self):
        """
        Attempt to parse a single message from the buffer.

        Raises IndexError if the buffer does not contain a complete message.
        Raises ValueError if the  

        Returns a mesage as bytes
        """
 
        raw_msg = None
        length = None

        pos = 0 # our current position in the buffer

        try: 
            length = self._buffer[:8]
            pos = 8
            try:
                length = int(length)
            except ValueError:
                raise ValueError('Invalid message length {}'.format(length))
            
            raw_msg = self._buffer[:length + 10] # length and type fields takes 10 bytes
            if len(raw_msg) < length + 10:
                raise IndexError('Message not complete')

            msg_type = raw_msg[pos:pos + 2]
            if msg_type not in [b'BI', b'AB', b'FX']:
                raise ValueError('Ivalid message type {}'.format(msg_type))
            
            pos = pos + 2
            msg_start = raw_msg[pos:pos + 4] # should be SOH (\x01) \r \r \n
            if not msg_start == b'\x01\r\r\n':
                raise ValueError('Message start not found (found {})'.format(msg_start))

            pos = pos + 4
            # This should be {3,5}, but norcom does not seem to use CSNs
            csn_match = re.match(rb'\d{0,5}\r\r\n', raw_msg[pos:pos + 8]) 
            if not csn_match:
                raise ValueError('CSN not found (found {})'.format(raw_msg[pos:pos + 8]))

            start_pos = pos + csn_match.end(0)
            end_pos = len(raw_msg) - 4

            pos = end_pos
            msg_end = raw_msg[pos:pos + 4] # should be \r \r \n ETX (\x03)
            if not msg_end == b'\r\r\n\x03':
                raise ValueError('Message end not found (found {})'.format(msg_end))


        except ValueError as e: # something went wrong when parsing the message, discard it
            sys.stderr.write('Error parsing message: {}\n'.format(e))
            next_message = re.search(br'\d{8}[A-Z]{2}\d{0,5}\x01\r\r\n', buffer[pos:])
            if next_message: # move to the next message if there is one
                self._buffer = self._buffer[next_message.start(0):]
            else: # no more messages, clear the buffer
                self._buffer = b''
            raise
        
        msg = raw_msg[start_pos:end_pos]
        self._buffer = self._buffer[len(raw_msg):]

        return msg
            
    def __del__(self):
        if self._socket:
            self._socket.close()
