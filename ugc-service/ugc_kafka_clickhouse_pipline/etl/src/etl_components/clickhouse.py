import logging
from pydantic import BaseSettings
from clickhouse_driver import Client as ClickhouseClient
from clickhouse_driver.errors import Error as ClickError
from utils import Sleeper


class ClickHouseConsumer:
    """Receives data in batches and saves it in ClickHouse."""

    def __init__(self, conf: BaseSettings):  # Accept an instance of BaseSettings
        self.client = ClickhouseClient(host=conf.host, user=conf.clickhouse_user, password=conf.clickhouse_password)

        self.cnt_records = 0
        self.sleeper = Sleeper()

    def save(self, data: list):
        self.sleeper.reset()
        if len(data) == 0:
            return

        while True:
            try:
                data_dict = [d.dict() for d in data]
                batch_size = len(data_dict)

                self.client.execute(
                    "INSERT INTO ugc.views (id, user_id, movie_id, movie_progress, movie_length) VALUES", data_dict
                )

                logging.info(f"ClickHouse saved records {self.cnt_records}...{self.cnt_records + batch_size}...")
                self.cnt_records += batch_size
                return
            except ClickError as e:
                logging.error(f"ClickHouse save failed: {e}")
                self.sleeper.sleep()
