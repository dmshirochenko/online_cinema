import logging
import sqlite3
from typing import Callable, Generator

from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_values

from .classes import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


class SQLiteExtractor:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

        self.table2dataclass = {
            "genre": Genre,
            "person": Person,
            "film_work": Filmwork,
            "genre_film_work": GenreFilmwork,
            "person_film_work": PersonFilmwork,
        }

    def extract_data(self, table: str, page_size: int = 100) -> Generator[list, None, None]:
        """Returns content of QSLite database as dictionary.

        Args:
            table: name of the SQLite table to extract data from.
            page_size: number of rows to yield.

        """
        curs = self.connection.cursor()
        dataclass = self.table2dataclass[table]
        curs.execute(f"SELECT * FROM {table};")

        while len(data := curs.fetchmany(page_size)):
            yield [dataclass(**row) for row in data]
        else:
            logging.info(f"Table {table} loaded.")


class PostgresSaver:
    def __init__(self, pg_conn: _connection):
        self.connection = pg_conn

        self.savers = {
            "genre": self._save_genre,
            "person": self._save_person,
            "film_work": self._save_film_work,
            "genre_film_work": self._save_genre_film_work,
            "person_film_work": self._save_person_film_work,
        }

    def get_saver(self, table: str) -> Callable[[list], None]:
        return self.savers.get(table)

    def save_data(self, table: str, data: list):
        """
        Save batch of data to a given table.
        """
        save_func = self.get_saver(table)
        if save_func is None:
            raise ValueError(f"No {table} table supported.")

        save_func(data)

    def _save_genre(self, data: list) -> None:
        cur = self.connection.cursor()
        batch = [[row.id, row.name, row.description, row.created_at, row.updated_at] for row in data]
        query = (
            "INSERT INTO content.genre (id, name, description, created_at, updated_at) VALUES %s ON CONFLICT DO NOTHING"
        )
        execute_values(cur, query, batch)

    def _save_person(self, data: list) -> None:
        cur = self.connection.cursor()
        batch = [[row.id, row.full_name, row.created_at, row.updated_at] for row in data]
        query = "INSERT INTO content.person (id, full_name,  created_at, updated_at) VALUES %s ON CONFLICT DO NOTHING"
        execute_values(cur, query, batch, template=None)

    def _save_film_work(self, data: list) -> None:
        cur = self.connection.cursor()
        batch = [
            [
                row.id,
                row.title,
                row.description,
                row.creation_date,
                row.rating,
                row.type,
                row.file_path,
                row.created_at,
                row.updated_at,
            ]
            for row in data
        ]
        query = (
            "INSERT INTO content.film_work "
            "(id, title, description, creation_date, rating, type, file_path, created_at, updated_at) "
            "VALUES %s ON CONFLICT DO NOTHING"
        )
        execute_values(cur, query, batch, template=None)

    def _save_genre_film_work(self, data: list) -> None:
        cur = self.connection.cursor()
        batch = [[row.id, row.film_work_id, row.genre_id, row.created_at] for row in data]
        query = (
            "INSERT INTO content.genre_film_work (id, film_work_id, genre_id, created_at) "
            "VALUES %s ON CONFLICT DO NOTHING"
        )
        execute_values(cur, query, batch, template=None)

    def _save_person_film_work(self, data: list) -> None:
        cur = self.connection.cursor()
        batch = [[row.id, row.role, row.film_work_id, row.person_id, row.created_at] for row in data]
        query = (
            "INSERT INTO content.person_film_work (id, role, film_work_id, person_id, created_at) "
            "VALUES %s ON CONFLICT DO NOTHING"
        )
        execute_values(cur, query, batch, template=None)
