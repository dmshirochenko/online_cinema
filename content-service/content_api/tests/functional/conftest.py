import json
import logging
import os
import time
from typing import Generator

import aiohttp
import elasticsearch
import pytest
from elasticsearch import Elasticsearch
from redis import Redis

from tests.functional.settings import (es_settings, redis_settings,
                                       test_settings)

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))


def load_data() -> dict[str, dict]:
    with open(test_settings.data_path, 'r') as f:
        data = json.load(f)
    logging.info('Data loaded from disk')
    return data


DATA = load_data()


def create_index(client: Elasticsearch, index: str) -> None:
    try:
        with open(es_settings.scheme_path[index], 'r') as f:
            scheme = json.load(f)
        client.indices.create(index='movies', body=scheme)
        logging.info(f'Index {index} created')
    except elasticsearch.exceptions.RequestError as ex:
        if ex.error == 'resource_already_exists_exception':
            pass
        else:
            raise ex


def load_index(client: Elasticsearch, index: str, data: dict[str, dict]) -> None:
    """Load data into given elasticseach index."""

    bulk_data = []
    for _id, _data in data.items():
        index_dict = {'index': {'_index': index, '_id': _id}}
        bulk_data.append(index_dict)
        bulk_data.append({k: v for k, v in _data.items()})

    es_response = client.bulk(index=index, body=bulk_data)
    if es_response['errors']:
        logging.error(f'Error during ES update: {es_response}')


def delete_index(client: Elasticsearch, index: str):
    try:
        client.indices.delete(index=index)
        logging.info(f'Index {index} deleted')
    except elasticsearch.exceptions.RequestError:
        pass


def pytest_sessionstart(session):
    client = Elasticsearch(**es_settings.dict())
    for index in ('movies', 'genre', 'person'):
        create_index(client, index)
        load_index(client, index, DATA[index])
        time.sleep(1)


def pytest_sessionfinish(session, exitstatus):
    client = Elasticsearch(**es_settings.dict())
    for index in ('movies', 'genre', 'person'):
        delete_index(client, index)


@pytest.fixture
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(aiohttp_session):
    async def inner(url: str, params: dict | None = None):
        async with aiohttp_session.get(url, params=params) as response:
            body = await response.json()
            return body, response.status

    return inner


@pytest.fixture
def existing_film() -> dict:
    return list(DATA['movies'].values())[0]


@pytest.fixture
def existing_person() -> dict:
    return list(DATA['person'].values())[0]


@pytest.fixture
def existing_genre() -> dict:
    return list(DATA['genre'].values())[0]


@pytest.fixture
def n_films() -> int:
    return len(DATA['movies'])


@pytest.fixture
def n_genres() -> int:
    return len(DATA['genre'])


@pytest.fixture
def n_persons() -> int:
    return len(DATA['person'])


@pytest.fixture
def all_films() -> list[dict]:
    return list(DATA['movies'].values())


@pytest.fixture
def cache() -> Generator[Redis, None, None]:
    redis = Redis(host=redis_settings.host, port=redis_settings.port)
    yield redis
    redis.flushdb()
