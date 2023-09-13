import logging
import os
import sqlite3
from datetime import datetime, timezone

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


def dict_factory(cursor, row) -> dict:
    """Converts SQLite row into dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def test_table_sizes(sqlite_conn, pg_conn) -> None:
    """Raise assert in case of table sizes mistmatch."""
    for table in ("genre", "person", "film_work"):
        cur_sqlite = sqlite_conn.cursor()
        cur_sqlite.execute(f"SELECT COUNT(1) FROM {table};")
        n_sqlite = cur_sqlite.fetchone()[0]

        cur_pg = pg_conn.cursor()
        cur_pg.execute(f"SELECT COUNT(1) FROM content.{table};")
        n_pg = cur_pg.fetchone()["count"]

        msg = (
            f"Sizes mistamtch for table {table} between "
            "SQLite and Pg: {n_sqlite} vs. {n_pg}."
        )
        assert n_sqlite == n_pg, msg

    logging.info("Test for tabel sizes - OK.")


def test_table_content(sqlite_conn, pg_conn, n_rows: int = 50) -> None:
    """Raise assert in case of content mismatch.

    Args
        sqlite_conn: SQLite connector.
        pg_conn: Postgres connector.
        n_rows: page size for insertion.
    """

    def _compare_row(row_sqlite, row_pg):
        for k, v_pg in row_pg.items():
            v_sql = row_sqlite[k]
            if v_pg and (k.endswith("at") or k.endswith("date")):
                v_sql = datetime.strptime(v_sql[:-3], "%Y-%m-%d %H:%M:%S.%f")
                v_sql = v_sql.replace(tzinfo=timezone.utc)

            msg = f"Key {k} does not match: {v_sql} with {v_pg}"
            assert v_sql == v_pg, msg

    for table in ["genre", "person", "film_work"]:
        sqlite_conn.row_factory = dict_factory
        cur_sqlite = sqlite_conn.cursor()
        cur_sqlite.execute(f"SELECT * FROM {table} LIMIT {n_rows};")
        data_sqlite = cur_sqlite.fetchall()

        cur_pg = pg_conn.cursor()
        cur_pg.execute(f"SELECT * FROM content.{table} LIMIT {n_rows};")
        data_pg = cur_pg.fetchall()

        for row_sqlite, row_pg in zip(data_sqlite, data_pg):
            _compare_row(row_sqlite, row_pg)

    logging.info("Test for table contents - OK.")


if __name__ == "__main__":
    dsl = {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": "127.0.0.1",
        "port": 5432,
    }
    with sqlite3.connect("db.sqlite") as sqlite_conn, psycopg2.connect(
        **dsl, cursor_factory=RealDictCursor
    ) as pg_conn:
        test_table_sizes(sqlite_conn, pg_conn)
        test_table_content(sqlite_conn, pg_conn)
