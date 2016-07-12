#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tuber.BaseAdapter import BaseAdapter

from kafka import KafkaProducer
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

        self._connect()

    def _connect(self):
        if self.direction == 'input':
            pass
        else:
            self.producer = KafkaProducer(bootstrap_servers=['{}:{}'.format(self.host, self.port)])

    def send(self, message):
        message = bytes(message)
        record = self.producer.send(self.topic, message)
        record_metadata = record.get(timeout=10)
