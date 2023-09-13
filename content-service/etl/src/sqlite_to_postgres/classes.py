import uuid
from dataclasses import dataclass


@dataclass
class Genre:
    name: str
    description: str
    created_at: str
    updated_at: str
    id: uuid.UUID


@dataclass
class Person:
    full_name: str
    created_at: str
    updated_at: str
    id: uuid.UUID


@dataclass
class Filmwork:
    created_at: str
    updated_at: str
    title: str
    description: str
    creation_date: str
    rating: int
    type: str
    file_path: str
    id: uuid.UUID


@dataclass
class GenreFilmwork:
    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: str


@dataclass
class PersonFilmwork:
    id: uuid.UUID
    role: str
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    created_at: str
