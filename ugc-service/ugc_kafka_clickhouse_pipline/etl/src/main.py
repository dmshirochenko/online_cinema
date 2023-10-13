import logging

from config import Settings
from etl_components.kafka import KafkaConnector
from etl_components.clickhouse import ClickHouseConsumer
from utils import Sleeper

logging.basicConfig(encoding="utf-8", level=logging.INFO)

if __name__ == "__main__":
    settings = Settings()  # create an instance of Settings

    etl_producer = KafkaConnector(settings.kafka_settings)  # use the instance
    etl_consumer = ClickHouseConsumer(settings.click_settings)  # use the instance
    sleeper = Sleeper(sleep_init=5, sleep_increase=None)

    while True:
        data = []
        while not data:
            start_offsets = etl_producer.get_offsets()
            data = etl_producer.load_data()
            etl_consumer.save(data)
            etl_producer.set_offsets(start_offsets)

            sleeper.sleep(sleep_secs=settings.etl_settings.sleep_delay_sec)  # use the instance

        sleeper.sleep("ETL process is exhausted")
