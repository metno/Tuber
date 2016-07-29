#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tuber.BaseAdapter import BaseAdapter
from Tuber import TuberLogger
from Tuber.Message import Message
from Tuber import TuberIOError

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

import time
import sys

class KafkaAdapter(BaseAdapter):
    """
    Adapter for communicating with Kafka brokers
    """

    def __init__(self, direction, bootstrap_servers, topic, **kwargs): #pylint: disable=E1003
        if sys.version_info.major == 3:
            super().__init__(direction)
        else:
            super(KafkaAdapter, self).__init__(direction)

        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.extra_opts = kwargs

        scheme = 'kafka'

        if 'sasl_plain_username' in self.extra_opts and 'sasl_plain_password' in self.extra_opts:
            self.extra_opts['sasl_mechanism'] = 'PLAIN'
            scheme = 'kafkassl'

        self.url = '{}://{}/{}'.format(scheme, self.bootstrap_servers[0], self.topic)

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
            raise TuberIOError('Kafka error: {}'.format(e.__class__.__name__))


    def _send(self, message):
        try:
            record = self._producer.send(self.topic, message.serialize())
        except KafkaError as e:
            raise TuberIOError('Kafka error: {}'.format(e.__class__.__name__))


    def receive(self):
        try:
            record = self._consumer.__next__()
            return Message(record.value)
        except KafkaError as e:
            raise TuberIOError('Kafka error: {}'.format(e.__class__.__name__))
