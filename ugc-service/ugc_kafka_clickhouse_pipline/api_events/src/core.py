import logging
import time
from typing import Optional

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable


class KafkaConnector:
    """Connects to Kafka lazily on the first call."""

    def __init__(self, kafka_url: str, sleep_secs: int = 5) -> None:
        self._producer: Optional[KafkaProducer] = None
        self._kafka_url: str = kafka_url
        self._sleep_secs: int = sleep_secs

    def send(self, topic: str, value: bytes, key: str) -> None:
        if self._producer is None:
            while True:
                try:
                    self._producer = KafkaProducer(bootstrap_servers=[self._kafka_url])
                except NoBrokersAvailable:
                    logging.info(f"Error: No Kafka Borkers Found. Sleeping for {self._sleep_secs}")
                    time.sleep(self._sleep_secs)
                    continue
                break

        self._producer.send(topic=topic, value=value, key=key)
