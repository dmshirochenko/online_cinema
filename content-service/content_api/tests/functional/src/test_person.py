import uuid
from http import HTTPStatus

import pytest
from aioredis import Redis

from tests.functional.settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_get_id_cache(make_get_request, existing_person: dict, cache: Redis):
    _id = existing_person["id"]
    url = test_settings.service_url + f"/api/v1/persons/{_id}"
    cached_objects_1 = cache.dbsize()

    await make_get_request(url)
    body, status = await make_get_request(url)  # by cache logic
    cached_objects_2 = cache.dbsize()

    assert status == HTTPStatus.OK
    assert body["full_name"] == existing_person["full_name"]
    assert cached_objects_2 - cached_objects_1 == 1


async def test_get_id_valid(make_get_request, existing_person: dict):
    _id = existing_person["id"]
    url = test_settings.service_url + f"/api/v1/persons/{_id}"

    body, status = await make_get_request(url)

    assert status == HTTPStatus.OK
    assert body["full_name"] == existing_person["full_name"]


async def test_get_id_invalid(make_get_request):
    _id = uuid.uuid4()
    url = test_settings.service_url + f"/api/v1/persons/{_id}"

    _, status = await make_get_request(url)

    assert status == HTTPStatus.NOT_FOUND


async def test_films_of_person(make_get_request, existing_person: dict):
    _id = existing_person["id"]
    url = test_settings.service_url + f"/api/v1/persons/{_id}/films"

    body, status = await make_get_request(url)

    assert status == HTTPStatus.OK
    assert len(body) == len(existing_person["films"])


async def test_search_cache(make_get_request, existing_person: dict, cache: Redis):
    url = test_settings.service_url + "/api/v1/persons/search"
    query_data = {"query": existing_person["full_name"]}
    cached_objects_1 = cache.dbsize()

    await make_get_request(url, params=query_data)
    body, status = await make_get_request(url, params=query_data)
    cached_objects_2 = cache.dbsize()

    assert status == HTTPStatus.OK
    assert body["result"][0]["full_name"] == existing_person["full_name"]
    assert cached_objects_2 - cached_objects_1 == 1


async def test_search(make_get_request, existing_person: dict):
    url = test_settings.service_url + "/api/v1/persons/search"
    query_data = {"query": existing_person["full_name"]}

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert body["result"][0]["full_name"] == existing_person["full_name"]


async def test_search_nonexistent(make_get_request):
    url = test_settings.service_url + "/api/v1/persons/search"
    query_data = {"query": str(uuid.uuid4)}

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert len(body["result"]) == 0
