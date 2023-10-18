import os

from pydantic import BaseSettings
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TestSettings(BaseSettings):
    data_path: str = os.path.join(BASE_DIR, "data/test_data.json")
    service_url: str = "http://service-content-test:80"


class ElasticSettings(BaseSettings):
    host: Optional[str] = "elastic"
    port: str = "9200"
    scheme_path: dict = {
        "genre": os.path.join(BASE_DIR, "data/indices/es_genre.json"),
        "person": os.path.join(BASE_DIR, "data/indices/es_person.json"),
        "movies": os.path.join(BASE_DIR, "data/indices/es_movies.json"),
    }

    class Config:
        env_prefix = "ES_"


class RedisSettings(BaseSettings):
    host: Optional[str] = "cache"
    port: str = "6379"

    class Config:
        env_prefix = "REDIS_"


test_settings = TestSettings()
es_settings = ElasticSettings()
redis_settings = RedisSettings()
