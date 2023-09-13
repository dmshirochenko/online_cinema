import os
from logging import config as logging_config

from pydantic import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = os.getenv("PROJECT_NAME", "ContentAPI")


class RedisSettings(BaseSettings):
    host: str
    port: str = "6379"

    class Config:
        env_prefix = "REDIS_"


class ElasticSettings(BaseSettings):
    host: str
    port: str = "9200"

    class Config:
        env_prefix = "ES_"


class AuthSettings(BaseSettings):
    host: str
    port: str
    mode: str = ...
    auth_url: str = "auth/api/v1/role_exists"

    trace: bool = mode == "dev"

    class Config:
        env_prefix = "AUTH_"


auth_settings = AuthSettings()
