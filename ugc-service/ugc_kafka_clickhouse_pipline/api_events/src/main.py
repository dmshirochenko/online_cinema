from http import HTTPStatus
from fastapi import FastAPI, status
from typing import Dict, Tuple, Any
import logging
import uuid

from settings import app_settings as conf
from models import KafkaEvent
from core import KafkaConnector

app: FastAPI = FastAPI()
kafka_connector: KafkaConnector = KafkaConnector(conf.kafka_url)


@app.post("/api/v1/send_event", status_code=status.HTTP_200_OK)
async def send_event(event: KafkaEvent) -> Tuple[Dict[str, Any], HTTPStatus]:
    logging.info(f"Event sent to kafka: {event.dict()}")

    kafka_connector.send(
        topic=conf.kafka_topic_name,
        value=str.encode(event.json()),
        key=str(uuid.uuid4()).encode(),
    )

    return {}, HTTPStatus.OK
