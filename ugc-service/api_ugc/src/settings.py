import logging
from pydantic import BaseSettings, Field, validator
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class AppSettings(BaseSettings):
    """Base settings for api events service."""

    debug: Optional[bool] = Field(default=True, env="DEBUG_UGC")
    sentry_dsn: str = ""

    # logstash_url = "logstash"
    # logstash_port = 5044

    mongo_url: str = "mongodb://mongo:27017"
    db_name: str = "movies"
    db_rating_collection: str = "ratings"
    db_bookmark_collection: str = "bookmarks"
    db_review_collection: str = "review"
    db_watched_movies_collection: str = "watched_movies"

    auth_url: str = "http://auth_api:5000/auth_api/api/v1/auth/user"

    logging_level: str

    @validator("logging_level", pre=True, always=True)
    def set_logging_level(cls, value):
        valid_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
        if value.upper() not in valid_levels:
            raise ValueError("Invalid logging level")
        return value.upper()


class AuthSettings(BaseSettings):
    host: str = "auth"
    port: str = "5000"
    mode: str = "dev"
    auth_url: str = "auth/api/v1/role_exists"


auth_settings = AuthSettings()
app_settings = AppSettings()
logging_level = getattr(logging, app_settings.logging_level)
