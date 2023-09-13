from models.abstract_model import AbstractModel


class Person(AbstractModel):
    full_name: str


class PersonFilms(Person):
    role: list[str] = []
    films: list[dict] = []


class PersonDetail(Person):
    role: list[str] = []
    film_ids: list[str] = []
