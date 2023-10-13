import logging
import pydantic
from pydantic import BaseSettings
import json
from kafka import KafkaConsumer
import kafka.errors

from state import State, JsonFileStorage
from models import Kafka, KafkaReadOffset
from utils import Sleeper


class KafkaConnector:
    """Produces data in batches from Kafka."""

    settings: BaseSettings
    consumer: KafkaConsumer
    state_saver: State
    partitons: set[kafka.TopicPartition]
    offset_state: list[KafkaReadOffset]
    frame_size: int

    def __init__(self, settings: BaseSettings):
        self.settings = settings
        self.consumer = KafkaConsumer(
            settings.topic_name,
            bootstrap_servers=[f"{settings.host}:{settings.port}"],
            auto_offset_reset="earliest",
            group_id=self.settings.group_id,
        )
        self.state_saver = State(JsonFileStorage("states.json"))

        self.partitons = self.consumer.assignment()
        self.offset_state = self.state_saver.get_state("offset_state")
        if self.offset_state:
            self.set_offsets(self.offset_state)
        self.frame_size = settings.frame_size
        self.sleeper = Sleeper()

    def get_offsets(self) -> list[KafkaReadOffset]:
        offsets = []
        for part in self.partitons:
            offset = self.consumer.position(part)
            offsets.append(KafkaReadOffset(partiton=part, offset=offset))
        self.offset_state = offsets
        return offsets

    def set_offsets(self, offsets: list[KafkaReadOffset]):
        self.offset_state = offsets
        for part, offset in offsets:
            self.consumer.seek(part, offset)

    def load_data(self) -> list:
        self.sleeper.reset()

        while True:
            try:
                events = []
                data = self.consumer.poll(max_records=self.frame_size)
            except kafka.errors.NoBrokersAvailable:
                logging.error(f"kafka: {self.settings.host}:{self.settings.port}")
                logging.error("kafka: broker not found")
                self.sleeper.sleep()
            except Exception:
                logging.exception("kafka: new error")
                self.sleeper.sleep()

            for part in data.values():
                for value in part:
                    kafka_event = pydantic.parse_obj_as(Kafka, json.loads(value.value.decode()))
                    events.append(kafka_event)
            self.state_saver.set_state("offset_state", self.get_offsets())
            return events
