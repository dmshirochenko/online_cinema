import os
from datetime import timedelta
from enum import Enum

from pydantic import BaseSettings


class BaseAppSettings(BaseSettings):
    FLASK_ENV = "development"
    TESTING = True
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")
    AUTH_SECRET: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "client_secret.json",
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=30)


# Supported types of social-based authentication
AuthType = Enum("AuthType", ["GOOGLE"])


class GoogleAuthSettings(BaseSettings):
    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ]


class DevSettings(BaseAppSettings):
    FLASK_ENV = "development"
    TESTING = True
    TRACING = False


class ProdSettings(BaseAppSettings):
    FLASK_ENV = "production"
    TESTING = False
    TRACING = True


class PostgresSettings(BaseSettings):
    db: str
    user: str
    password: str
    host: str
    port: str = "5433"

    class Config:
        env_prefix = "POSTGRES_AUTH_"


class RedisSettings(BaseSettings):
    host: str = "cache_auth"
    port: int = 6379
    db: int = 1


class FlaskSettings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 5000


AppSettings = None
if (app_mode := os.environ.get("AUTH_MODE")) in ("dev", "test"):
    AppSettings = DevSettings
elif app_mode == "prod":
    AppSettings = ProdSettings
else:
    raise ValueError(f"Unknown auth app mode: {app_mode}")


app_settings = AppSettings()
pg_settings = PostgresSettings()
redis_setttings = RedisSettings()
flask_settings = FlaskSettings()
google_auth_settings = GoogleAuthSettings()
