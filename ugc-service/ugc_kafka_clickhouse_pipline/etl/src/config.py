from pydantic import BaseSettings


class KafkaSettings(BaseSettings):
    host: str = "kafka1"
    port: str = "19092"
    group_id: str = "etl"
    topic_name: str = "ugc"
    frame_size: int = 50


class ClickSettings(BaseSettings):
    host: str = "clickhouse-node1"
    port: int = 8123
    clickhouse_user: str = "default"
    clickhouse_password: str = "test"


class ETLSettings(BaseSettings):
    sleep_delay_sec: float = 3


class Settings(BaseSettings):
    kafka_settings: KafkaSettings = KafkaSettings()
    click_settings: ClickSettings = ClickSettings()
    etl_settings: ETLSettings = ETLSettings()
