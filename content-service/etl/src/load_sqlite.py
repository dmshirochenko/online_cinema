import logging
import os
import sqlite3
from contextlib import contextmanager

import psycopg2
from config.settings import PostgresSettings, SQLiteSettings
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from sqlite_to_postgres.loaders import PostgresSaver, SQLiteExtractor

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


@contextmanager
def sqlite_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection,
        page_size: int=100) -> None:
    """Main method of loading data from SQLite into Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_extractor = SQLiteExtractor(connection)

    for table in ['genre', 'person', 'film_work',
            'genre_film_work', 'person_film_work']:
        for data in sqlite_extractor.extract_data(table, page_size):
            postgres_saver.save_data(table, data)


if __name__ == '__main__':
    pg_conf = PostgresSettings().dict()
    sqlite_conf = SQLiteSettings().dict()

    with sqlite_context(sqlite_conf['db_path']) as sqlite_conn, psycopg2.connect(**pg_conf, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
        
    logging.info("SQLite -> Postgres loading done.")
