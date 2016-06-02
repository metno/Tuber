#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class BaseAdapter:
    def __init__(self, direction):
        if direction not in ['input' , 'output']:
            raise Exception("Illegal direction {}. Must be either 'input' or 'output'".format(direction))
        self.direction = direction


    def receive(self):
        """
        Receive a single message. Blocks until one is available.

        Returns a message (bytes)
        """
        raise NotImplementedError()


    def send(self, message):
        """
        Sends a message.
        """
        raise NotImplementedError()

    def __iter__(self):
        return self

    def __next__(self):
        return self.receive()
