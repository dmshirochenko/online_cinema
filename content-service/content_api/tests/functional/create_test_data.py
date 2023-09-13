"""
Generate test data in json format.
"""
import argparse
import json
import os
import uuid
from random import choice, randint, uniform

from faker import Faker
from settings import test_settings as settings

parser = argparse.ArgumentParser(description='Test database data generator.')
parser.add_argument(
    '-f',
    '--filename',
    type=str,
    default='test_data.json',
    help='file name to store test data (test_data.json by default)',
)

fake = Faker()


def make_enum_generator(enum):
    def gen():
        return choice(enum)

    return gen


def generate_persons(total: int) -> dict[str, dict]:
    gen_role = make_enum_generator(['Actor', 'Director', 'Writer'])

    data = {}
    for _ in range(total):
        p_id = str(uuid.uuid4())

        films = [
            {'id': str(uuid.uuid4()), 'title': fake.name(), 'imdb_rating': round(uniform(0.0, 10.0), 2),}
            for _ in range(randint(1, 5))
        ]

        data[p_id] = {
            'id': p_id,
            'full_name': fake.name(),
            'role': list(set([gen_role() for _ in range(randint(1, 3))])),
            'films': films,
        }

    return data


def generate_movies(total: int) -> dict[str, dict]:
    gen_type = make_enum_generator(['film', 'tv-show', ""])
    gen_genre = make_enum_generator(['Action', 'Sci-Fi', 'Drama', 'Comedy', 'Thriller'])

    def gen_persons():
        return [{'id': str(uuid.uuid4()), 'full_name': fake.name()} for _ in range(randint(0, 3))]

    def gen_genres():
        return [{'id': str(uuid.uuid4()), 'name': gen_genre()} for _ in range(randint(0, 3))]

    data = {}
    for _ in range(total):
        _id = str(uuid.uuid4())
        data[_id] = {
            'id': _id,
            'genre': gen_genre(),
            'imdb_rating': round(uniform(0.0, 10.0), 2),
            'genres': gen_genres(),
            'title': fake.name(),
            'description': fake.sentence(nb_words=10),
            'director': [fake.name() for _ in range(randint(0, 2))],
            'actors_names': [fake.name() for _ in range(randint(0, 4))],
            'writers_names': [fake.name() for _ in range(randint(0, 4))],
            'actors': gen_persons(),
            'writers': gen_persons(),
            'directors': gen_persons(),
            'file_path': fake.sentence(nb_words=3),
            'movie_type': gen_type(),
        }
    return data


def generate_genres(total: int) -> dict[str, dict]:
    data = {}
    for _ in range(total):
        _id = str(uuid.uuid4())
        data[_id] = {'id': _id, 'name': fake.name()}
    return data


def generate_data(n_genres: int, n_movies: int, n_persons: int) -> dict[str, dict]:
    data = {
        'genre': generate_genres(n_genres),
        'person': generate_persons(n_persons),
        'movies': generate_movies(n_movies),
    }
    return data


def save_data(data: dict[str, dict], filename: str,) -> None:
    path = os.path.join('data', filename)
    with open(path, 'w') as f:
        json.dump(data, f)
    print(f'Test data saved to {path}.')


if __name__ == '__main__':
    args = parser.parse_args()

    data = generate_data(n_genres=settings.n_genres, n_movies=settings.n_movies, n_persons=settings.n_persons,)
    save_data(data, args.filename)
