import logging
from time import sleep

from .base import ETLManager
from .es_components import ElasticLoader, ElasticTransformer
from .pg_components import PostgresEnricher, PostgresMerger, PostgresPersonMerger, PostgresProducer


def etl_filmwork(
    pg_table: str,
    es_index: str,
    enrich_needed: bool,
    pg_conf: dict,
    es_conf: dict,
    manager: ETLManager,
    batch_size: int = 50,
    idle_sleep: int = 10,
):
    """
    ETL Process that updates filmworks in ES after persons update.

    Args:
        pg_table: name of the source PG table to track changes on.
        es_index: destination index for elastic.
        enrich_needed: convert ids from source table to filmwork ids.
        pg_conf: postgres connection parameters.
        es_conf: elastic connection parameters.
        manager: ETLManager instance for coordinating processes.
        batch_size: size of batches for PG.
        idle_sleep: wating time in seconds if all persons have been updated.
    """
    pg_producer = PostgresProducer(manager=manager, conf=pg_conf, table=pg_table, batch_size=batch_size)
    pg_enricher = PostgresEnricher(manager, pg_conf, pg_table, batch_size=batch_size)
    pg_merger = PostgresMerger(manager, pg_conf, pg_table)
    es_transformer = ElasticTransformer(es_index)
    es_loader = ElasticLoader(manager, es_conf, index=es_index)

    while True:
        for ids in gen_ids(enrich_needed, pg_producer, pg_enricher):
            film_items = pg_merger.run(ids)
            data_es = es_transformer.transform(film_items)
            es_loader.load_batch(data_es)

        if pg_producer.finished():
            logging.info(f"Postgres({pg_table}) -> Elastic({es_index}) up-to-date. " f"Re-checking in {idle_sleep} sec")
            sleep(idle_sleep)


def etl_persons(
    pg_table: str,
    es_index: str,
    enrich_needed: bool,
    pg_conf: dict,
    es_conf: dict,
    manager: ETLManager,
    batch_size: int = 50,
    idle_sleep: int = 10,
):
    """
    ETL Process that updates filmworks in ES after persons update.

    Args:
        pg_table: name of the source PG table to track changes on.
        es_index: destination index for elastic.
        enrich_needed: convert ids from source table to filmwork ids.
        pg_conf: postgres connection parameters.
        es_conf: elastic connection parameters.
        manager: ETLManager instance for coordinating processes.
        batch_size: size of batches for PG.
        idle_sleep: wating time in seconds if all persons have been updated.
    """
    pg_producer = PostgresProducer(manager=manager, conf=pg_conf, table=pg_table, batch_size=batch_size)
    pg_merger = PostgresPersonMerger(manager, pg_conf, pg_table)
    es_transformer = ElasticTransformer(es_index)
    es_loader = ElasticLoader(manager, es_conf, index=es_index)

    while True:
        ids = pg_producer.run()
        film_items = pg_merger.run(ids)
        data_es = es_transformer.transform(film_items)
        es_loader.load_batch(data_es)

        if pg_producer.finished():
            logging.info(f"Postgres({pg_table}) -> Elastic({es_index}) up-to-date. " f"Re-checking in {idle_sleep} sec")
            sleep(idle_sleep)


def etl_plain(
    table: str,
    extract_sql_fields: tuple[str],
    pg_conf: dict,
    es_conf: dict,
    manager: ETLManager,
    batch_size: int = 50,
    idle_sleep: int = 10,
):
    """
    ETL Process that updates filmworks in ES after genres/persons update.

    Args:
        table: name of the source PG table to track changes on.
        es_index: destination index for elastic.
        extract_sql_fields: list of names to extract from PG.
        pg_conf: postgres connection parameters.
        es_conf: elastic connection parameters.
        manager: ETLManager object.
        batch_size: size of batches for PG.
        idle_sleep: wating time in seconds if all persons have been updated.
    """
    pg_producer = PostgresProducer(
        manager, pg_conf, table, extract_sql_fields=extract_sql_fields, batch_size=batch_size
    )
    es_transformer = ElasticTransformer(table)
    es_loader = ElasticLoader(manager, es_conf, index=table)

    while True:
        batch = pg_producer.run()
        batch_es = es_transformer.transform(batch)
        es_loader.load_batch(batch_es)

        if pg_producer.finished():
            logging.info(f"Postgres({table}) -> Elastic({table}) up-to-date. " f"Re-checking in {idle_sleep} sec")
            sleep(idle_sleep)


def gen_ids(enrich_needed: bool, producer: PostgresProducer, enricher: PostgresEnricher) -> list[str]:
    """
    Genereate a batch of filmwork ids from source PG table ids.
    """
    ids = producer.run()
    if enrich_needed:
        for ids in enricher.run(ids):
            yield ids
    else:
        return [ids]
