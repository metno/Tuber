#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tuber.BaseAdapter import BaseAdapter
from Tuber import TuberLogger
from Tuber.Message import Message
from Tuber import TuberIOError

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

import time

class KafkaAdapter(BaseAdapter):
    """
    Adapter for communicating with Kafka brokers
    """

    def __init__(self, direction, host, port, topic):
        super().__init__(direction)
        self.host = host
        self.port = port
        self.topic = topic

        self.url = 'kafka://{}:{}/{}'.format(self.host, self.port, self.topic)

        self._connect()

    def _connect(self):
        try:
            if self.direction == 'input':
                self._consumer = KafkaConsumer(self.topic,
                                                   bootstrap_servers=['{}:{}'.format(self.host, self.port)])
            else:
                self._producer = KafkaProducer(bootstrap_servers=['{}:{}'.format(self.host, self.port)],
                                               retries=6,
                                               max_block_ms = 1000 * 60 * 10)
            TuberLogger.info('Connected to {}'.format(self.url))
        except KafkaError as e:
            raise TuberIOError('Kafka error: {}'.format(e.__class__.__name__)) from e


    def _send(self, message):
        try:
            record = self._producer.send(self.topic, message.serialize())
            metadata = record.get(timeout=10)
        except KafkaError as e:
            raise TuberIOError('Kafka error: {}'.format(e.__class__.__name__)) from e


    def receive(self):
        try:
            record = self._consumer.__next__()
            return Message(record.value)
        except KafkaError as e:
            raise TuberIOError('Kafka error: {}'.format(e.__class__.__name__)) from e
