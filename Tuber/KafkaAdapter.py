#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tuber.BaseAdapter import BaseAdapter
from Tuber import TuberLogger
from Tuber.Message import Message
from Tuber import TuberIOError, TuberException

from kafka import KafkaProducer, KafkaConsumer #pylint: disable=E0401
from kafka.errors import KafkaError #pylint: disable=E0401

from ssl import SSLError

import time
import sys

class KafkaAdapter(BaseAdapter):
    """
    Adapter for communicating with Kafka brokers
    """

    def __init__(self, direction, bootstrap_servers, topic, **kwargs):
        super().__init__(direction)

        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.extra_opts = kwargs

        if 'sasl_plain_username' in self.extra_opts and 'sasl_plain_password' in self.extra_opts:
            self.extra_opts['sasl_mechanism'] = 'PLAIN'
            self.extra_opts['security_protocol'] = 'SASL_SSL'

        self.url = 'kafka://{}/{}'.format(self.bootstrap_servers[0], self.topic)

        self._connect()

    def _connect(self):
        try:
            if self.direction == 'input':
                self._consumer = KafkaConsumer(self.topic,
                                               bootstrap_servers=self.bootstrap_servers,
                                               **self.extra_opts)
            else:
                self._producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                               retries=6,
                                               **self.extra_opts)
            TuberLogger.info('Connected to {}'.format(self.url))
        except KafkaError as e:
            raise TuberIOError('Unable to connect to {}. Reason: {}'.format(self.url, str(e))) from e
        except SSLError as e:
            raise TuberException('Error creating adapter {}: {}'.format(self.url, str(e))) from e


    def _send(self, message):
        try:
            record = self._producer.send(self.topic, message.serialize())
            record_metadata = record.get(timeout=10)
        except KafkaError as e:
            raise TuberIOError('Unable to send message to {}. Reason: {}'.format(self.url, str(e))) from e


    def receive(self):
        try:
            record = self._consumer.__next__()
            return Message(record.value)
        except KafkaError as e:
            raise TuberIOError('Error receiving from {}. Reson: {}'.format(self.url, str(e))) from e
