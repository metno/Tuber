#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tuber.BaseAdapter import BaseAdapter
from Tuber import TuberLogger

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

        self.url = 'kafka://{}:{}/{}'.format(self.host, self.port, self.topic)

        self._connect()

    def _connect(self):
        if self.direction == 'input':
            pass
        else:
            self.producer = KafkaProducer(bootstrap_servers=['{}:{}'.format(self.host, self.port)])
            TuberLogger.info('Connected to {}'.format(self.url))


    def _send(self, message):
        record = self.producer.send(self.topic, message.serialize())
        record_metadata = record.get(timeout=10)
