#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dateutil.tz import tzlocal #pylint: disable=E0401
from datetime import datetime
import socket
import os

from Tuber import TuberMessageError, TuberDuplicateMessage

class BaseAdapter(object):
    def __init__(self, direction):
        if direction not in ['input' , 'output']:
            raise Exception("Illegal direction {}. Must be either 'input' or 'output'".format(direction))
        self.direction = direction
        self.url = "none"

        self._seen_messages = set()

    def receive(self):
        """
        Receive a single Tuber.Message

        Returns a Tuber.Message
        Raises TuberMessageError and TuberIOError
        """
        raise NotImplementedError()


    def send(self, message):
        """
        Sends a Tuber.Message.
        """

        # we should avoid sending duplicates
        if message.hash in self._seen_messages:
            raise TuberDuplicateMessage('Duplicate message {}'.format(message.ahl))

        dt = datetime.now(tzlocal())
        message.add_header(dt.strftime('Queue-time: %Y-%m-%dT%H:%M:%S.%f%z'))

        hostname = socket.gethostname()
        pid = os.getpid()
        message.add_header('Queued-by: Tuber[{}] running on {}'.format(pid, hostname))

        self._send(message)

        # presumable the message was successfully sent, add it to the list of seen messages
        self._seen_messages.add(message.hash)
        # only check for duplicates for the last 1000 messages
        if len(self._seen_messages) > 1000:
            self._seen_messages = set()


    def _send(self, message):
        """
        Actually send the message.

        """
        raise NotImplementedError()


    def __str__(self):
        return self.url
