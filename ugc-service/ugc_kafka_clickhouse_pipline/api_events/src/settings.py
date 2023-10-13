from pydantic import BaseSettings


class AppSettings(BaseSettings):
    kafka_url: str = "kafka1:19092"
    kafka_topic_name: str = "ugc"


app_settings = AppSettings()
