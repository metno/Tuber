#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dateutil.tz import *
from datetime import datetime
import socket
import os

class BaseAdapter:
    def __init__(self, direction):
        if direction not in ['input' , 'output']:
            raise Exception("Illegal direction {}. Must be either 'input' or 'output'".format(direction))
        self.direction = direction
        self.url = "none"

    def receive(self):
        """
        Receive a single Tuber.Message
        """
        raise NotImplementedError()


    def send(self, message):
        """
        Sends a Tuber.Message.
        """

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
