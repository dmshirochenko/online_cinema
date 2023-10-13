from datetime import datetime

from pydantic import BaseModel


class KafkaEvent(BaseModel):
    id: str
    user_id: str
    movie_id: str
    movie_progress: float
    movie_length: int
    time_created: datetime
