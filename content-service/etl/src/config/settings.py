import os

from pydantic import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SQLiteSettings(BaseSettings):
    db_path: str = os.path.join(BASE_DIR, "data/db.sqlite")


class PostgresSettings(BaseSettings):
    dbname: str
    user: str
    password: str
    host: str
    port: str = "5432"
    options: str = "-c search_path=content"

    class Config:
        fields = {
            "dbname": {"env": "POSTGRES_DB"},
            "user": {"env": "POSTGRES_USER"},
            "password": {"env": "POSTGRES_PASSWORD"},
            "host": {"env": "POSTGRES_HOST"},
            "port": {"env": "POSTGRES_PORT"}
        }


class ElasticSettings(BaseSettings):
    host: str
    port: str
    scheme_path: dict = {
        "movies": os.path.join(BASE_DIR, "data/es_movies.json"),
        "genre": os.path.join(BASE_DIR, "data/es_genre.json"),
        "person": os.path.join(BASE_DIR, "data/es_person.json"),
    }

    class Config:
        env_prefix = "ES_"


class JsonStorageSettings(BaseSettings):
    dir_path: str = ".states"
    path: str = "state.json"
    cnt_path: str = "counter.json"

    def get_path(self):
        return os.path.join(self.dir_path, self.path)
