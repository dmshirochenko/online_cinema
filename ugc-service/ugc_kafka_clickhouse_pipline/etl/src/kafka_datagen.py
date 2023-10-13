from time import sleep
from random import randint, random
from uuid import uuid4
from models import Kafka
from datetime import datetime

from kafka import KafkaProducer
from config import Settings

settings = Settings()
producer = KafkaProducer(bootstrap_servers=[f"{settings.kafka_settings.host}:{settings.kafka_settings.port}"])

for i in range(100):
    data = Kafka(
        id=str(uuid4()),
        user_id=str(uuid4()),
        movie_id=str(uuid4()),
        movie_progress=random(),
        movie_length=randint(0, 7200),
        time_created=datetime.now(),
    ).json()
    rez = producer.send(topic=settings.kafka_settings.topic_name, value=str.encode(data), key=str(uuid4()).encode())
    sleep(0.01)
print("Data generated successfully.")
