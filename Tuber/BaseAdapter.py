#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dateutil.tz import *
from datetime import datetime
import socket
import os

from Tuber import TuberDuplicateMessage

class BaseAdapter:
    def __init__(self, direction):
        if direction not in ['input' , 'output']:
            raise Exception("Illegal direction {}. Must be either 'input' or 'output'".format(direction))
        self.direction = direction
        self.url = "none"

        self._seen_messages = set()

    def receive(self):
        """
        Receive a single Tuber.Message
        """
        raise NotImplementedError()


    def send(self, message):
        """
        Sends a Tuber.Message.
        """

        # we should avoid sending duplicates
        if message.hash in self._seen_messages:
            raise TuberDuplicateMessage('Duplicate message')
        self._seen_messages.add(message.hash)

        # only check for duplicates for the last 1000 messages
        if len(self._seen_messages) > 1000:
            self._seen_messages = set()

        dt = datetime.now(tzlocal())
        message.set_header('Queue-time', dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))

        hostname = socket.gethostname()
        pid = os.getpid()
        message.set_header('Queued-by', 'Tuber[{}] running on {}'.format(pid, hostname))

        self._send(message)


    def _send(self, message):
        """
        Actually send the message.

        """
        raise NotImplementedError()


    def __str__(self):
        return self.url
