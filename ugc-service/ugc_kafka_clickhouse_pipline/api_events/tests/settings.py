from pydantic import BaseSettings


class TestSettings(BaseSettings):
    # events_service_url = "http://localhost:8000"
    events_service_url = "http://events_api:8000"
    kafka_url = "kafka1:19092"
    kafka_topic_name = "ugc"


test_settings = TestSettings()
