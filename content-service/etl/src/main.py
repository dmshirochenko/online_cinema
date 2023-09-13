import logging
import os
from multiprocessing import Process
from time import sleep

from config.settings import (ElasticSettings, JsonStorageSettings,
                             PostgresSettings)
from etl.base import ETLManager
from etl.processes import etl_filmwork, etl_persons, etl_plain

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


if __name__ == "__main__":
    pg_conf = PostgresSettings().dict()
    es_conf = ElasticSettings().dict()

    # Global ETL Manager
    etl_manager = ETLManager(JsonStorageSettings().cnt_path)
    etl_manager.init()

    comm_params = (pg_conf, es_conf, etl_manager)
    processes = [
            Process(target=etl_plain, args=("genre", ("name",), *comm_params)),
            Process(target=etl_persons, args=("person", "person", True, *comm_params)),
            Process(target=etl_filmwork, args=("person", "movies", True, *comm_params)),
            Process(target=etl_filmwork, args=("genre", "movies", True, *comm_params)),
            Process(target=etl_filmwork, args=("film_work", "movies", False, *comm_params)),
    ]

    for p in processes:
        p.start()
        sleep(3)

    for p in processes:
        p.join()
