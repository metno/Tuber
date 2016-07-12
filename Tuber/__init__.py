#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

# set up logging
import logging
import logging.handlers
import os

TuberLogger = logging.getLogger('tuber')
TuberLogger.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s[{}]: %(message)s'.format(os.getpid()))
log_handler = logging.handlers.SysLogHandler(address = '/dev/log')
log_handler.setFormatter(formatter)
TuberLogger.addHandler(log_handler)

class TuberException(Exception):
    pass

class TuberParseError(TuberException):
    pass

class TuberIncompleteMessage(TuberException):
    pass

from .BaseAdapter import BaseAdapter
from .TCPAdapter import TCPAdapter
from .KafkaAdapter import KafkaAdapter
from .WMOBulletin import findAHL
