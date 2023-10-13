from datetime import datetime

from pydantic import BaseModel


class KafkaReadOffset(BaseModel):
    partiton: str
    offset: str


class Kafka(BaseModel):
    id: str
    user_id: str
    movie_id: str
    movie_progress: float
    movie_length: int
    time_created: datetime


class Clickhouse(BaseModel):
    id: str
    user_id: str
    movie_id: str
    movie_progress: str
    movie_length: str
    time_created: datetime
