#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tuber.BaseAdapter import BaseAdapter
from Tuber import TuberLogger
from Tuber.Message import Message

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError


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

        self._producer = None
        self._consumer = None
        self._connect()

    def _connect(self):
        if self.direction == 'input':
            self._consumer = KafkaConsumer(self.topic, bootstrap_servers=['{}:{}'.format(self.host, self.port)])
        else:
            self._producer = KafkaProducer(bootstrap_servers=['{}:{}'.format(self.host, self.port)])
        TuberLogger.info('Connected to {}'.format(self.url))


    def _send(self, message):
        record = self._producer.send(self.topic, message.serialize())
        record_metadata = record.get(timeout=10)

    def receive(self):
        record = self._consumer.__next__()
        return Message(record.value)
