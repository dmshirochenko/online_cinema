import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from .base import ETLComponent, ETLManager
from .utils import backoff


@contextmanager
def pg_context(dsl_params: dict):
    conn = None
    try:
        conn = psycopg2.connect(**dsl_params, cursor_factory=DictCursor)
        yield conn
    except psycopg2.OperationalError:
        logging.exception("Error during connection to database")
    finally:
        if conn:
            conn.close()


class PostgresProducer(ETLComponent):
    """Produce batch of ids from the specified table."""

    def __init__(
        self, manager: ETLManager, conf: dict, table: str, extract_sql_fields: tuple[str] = (), batch_size: int = 100
    ):
        """
        Args:
            manager: ETLManager instance.
            table: name of the table in `content.` sceme.
            extract_sql_fields: list of field names for extracting from DB.
            batch_size: size of the batch that produces returns.
        """
        super().__init__(manager, conf, table, batch_size)

        self._extract_sql_fields = list(extract_sql_fields)
        self._finihsed = False

    def _get_earliest_modified(self, conn: _connection) -> datetime:
        """
        Returns earliest date time.
        """
        cur = conn.cursor()
        query = f"""
        SELECT updated_at
        FROM content.{self.table}
        ORDER BY updated_at
        LIMIT 1;
        """
        cur.execute(query)
        return cur.fetchone()[0]

    @backoff(logging)
    def run(self) -> list:
        """
        Args:
            pg_conn: Postgres connection object.

        Returns: batch of ids of specified table.
        """
        with pg_context(self.conf) as conn:
            cur = conn.cursor()

            modified_from = self._restore_state(conn)
            fields = ",".join(["id"] + self._extract_sql_fields + ["updated_at"])

            cur.execute(
                f"""
            SELECT {fields}
            FROM content.{self.table}
            WHERE updated_at >= %s
            ORDER BY updated_at
            LIMIT {self.batch_size};
            """,
                (modified_from,),
            )
            data = cur.fetchall()

        self._finished = len(data) != self.batch_size

        # State is updated to the latest retrieved datetime
        latest_dt = data[-1][-1]
        if len(data):
            self.state.set_state("modified", latest_dt.isoformat())

        logging.info("Modifed from %s to %s", modified_from, latest_dt)

        return data

    def _restore_state(self, pg_conn: _connection) -> datetime:
        modified_from = self.state.get_state("modified")
        if modified_from is None:
            modified_from = self._get_earliest_modified(pg_conn)
        else:
            modified_from = datetime.fromisoformat(modified_from)
        return modified_from

    def finished(self):
        return self._finished


class PostgresEnricher(ETLComponent):
    """
    Enriches given list of ids selecting corresponding filmwork items.
    """

    def __init__(self, manager: ETLManager, conf, table: str, batch_size: int = 100):
        super().__init__(manager, conf, table, batch_size)

    @backoff(logging)
    def run(self, data: list[str]) -> Generator[list[str], None, None]:
        """
        Args:
            pg_conn: Postgres connecton.
            ids: ids from specified table to enrich with filmwork.
        Return
        """
        ids = [row[0] for row in data]
        ids = self._restore_state(ids)

        with pg_context(self.conf) as conn:
            cur = conn.cursor()
            query = f"""
            SELECT fw.id, fw.updated_at
            FROM content.film_work fw
            LEFT JOIN content.{self.table}_film_work pfw ON pfw.film_work_id = fw.id
            WHERE pfw.{self.table}_id IN %s;
            """
            cur.execute(query, (tuple(ids),))

            while batch := cur.fetchmany(self.batch_size):
                state_ids = ids[self.batch_size:]
                self.state.set_state("state", state_ids)
                yield [row[0] for row in batch]


class PostgresMerger(ETLComponent):
    """
    Collects information from filmwork, persons, and genres.
    """

    def __init__(self, manager: ETLManager, conf: dict, table: str):
        super().__init__(manager, conf, table)

    @backoff(logging)
    def run(self, filmwork_ids: list[str]) -> list[dict]:
        """
        Args:
            pg_conn: Postgres connection.
            filmwork_ids: List of filmwork ids.
        Returns: list of filmwork items.
        """
        with pg_context(self.conf) as conn:
            cur = conn.cursor()
            state_film_ids = self._restore_state(filmwork_ids)
            query = """
            SELECT
                fw.id as fw_id,
                fw.title,
                fw.description,
                fw.rating,
                fw.type,
                fw.created_at,
                fw.updated_at ,
                pfw.role,
                p.id,
                p.full_name,
                g.id,
                g.name,
                fw.file_path
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN %s;
            """

            cur.execute(query, (tuple(state_film_ids),))
            raw_data = cur.fetchall()

        fw_data = [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "rating": row[3],
                "type": row[4],
                "created_at": row[5],
                "updated_at": row[6],
                "role": row[7],
                "person_id": row[8],
                "person_full_name": row[9],
                "genre_id": row[10],
                "genre": row[11],
                "file_path": row[12],
            }
            for row in raw_data
        ]

        self.state.set_state("state", [])

        return fw_data


class PostgresPersonMerger(ETLComponent):
    """
    Collects information from filmwork, persons. Works directly with
    producer.
    """

    def __init__(self, manager: ETLManager, conf: dict, table: str):
        super().__init__(manager, conf, table)

    @backoff(logging)
    def run(self, person_ids: list[list]) -> list[dict]:
        """
        Args:
            pg_conn: Postgres connection.
            person_ids: List of person ids.
        Returns: list of filmwork items.
        """
        # Extract ids only
        person_ids = [item[0] for item in person_ids]

        with pg_context(self.conf) as conn:
            cur = conn.cursor()
            state_person_ids = self._restore_state(person_ids)
            query = """
            SELECT
                p.id,
                p.full_name,
                pfw.role,
                fw.id,
                fw.title,
                fw.rating,
                fw.type
            FROM content.person p 
            LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
            LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
            WHERE p.id IN %s;
            """
            cur.execute(query, (tuple(state_person_ids),))
            raw_data = cur.fetchall()

        person_data = [
            {
                "person_id": row[0],
                "person_full_name": row[1],
                "role": row[2],
                "id": row[3],
                "title": row[4],
                "rating": row[5],
                "type": row[6],
            }
            for row in raw_data
        ]

        self.state.set_state("state", [])

        return person_data
