#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

# set up logging
import logging
import logging.handlers
import os
import socket

TuberLogger = logging.getLogger("Tuber")
TuberLogger.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s %(levelname)s: %(message)s'.format(os.getpid()))
try:
    log_handler = logging.handlers.SysLogHandler(address = '/dev/log')
    log_handler.setFormatter(formatter)
    TuberLogger.addHandler(log_handler)
except (OSError, socket.error): # FileNotFoundError on python3.5
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)
    TuberLogger.addHandler(log_handler)
    TuberLogger.error("Could not create a syslog log handler, logging to stderr")


class TuberException(Exception):
    pass


class TuberIOError(TuberException):
    """
    Represents an error in the underlyeing data stream

    E.g. unreachable remote host
    """
    pass


class TuberMessageError(TuberException):
    """
    Represents a problem with a single message.
    """
    pass


class TuberIncompleteMessage(TuberMessageError):
    """
    Represents an error caused by an incomplete message.
    """
    pass


from .BaseAdapter import BaseAdapter
from .TCPAdapter import TCPAdapter
from .KafkaAdapter import KafkaAdapter
from .NullAdapter import NullAdapter
from .Message import Message
