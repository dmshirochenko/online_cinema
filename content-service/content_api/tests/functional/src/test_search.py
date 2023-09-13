from http import HTTPStatus

import pytest
from aioredis import Redis

from tests.functional.settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_film_search_cache(make_get_request, existing_film: dict,
        cache: Redis):
    url = test_settings.service_url + '/api/v1/search'
    query_data = {'query': existing_film['title']}
    cached_objects_1 = cache.dbsize()

    await make_get_request(url, params=query_data)
    body, status = await make_get_request(url, params=query_data)  # by cache logic
    cached_objects_2 = cache.dbsize()

    assert status == HTTPStatus.OK
    assert body['found_number'] != 0
    assert cached_objects_2 - cached_objects_1 == 1


async def test_common_search(make_get_request, existing_film: dict, existing_person: dict):
    url = test_settings.service_url + '/api/v1/search'
    query_data = {'query': existing_film['title']}

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert body['found_number'] != 0

    query_data = {'query': existing_person['full_name']}

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert body['found_number'] != 0


@pytest.mark.parametrize("test_input,expected", [("0", HTTPStatus.UNPROCESSABLE_ENTITY),
                                                 ("-1", HTTPStatus.UNPROCESSABLE_ENTITY)])
async def test_get_all_invalid_page_size(make_get_request, test_input, expected):
    url = test_settings.service_url + f'/api/v1/search'
    query_data = {'page[size]': test_input}

    _, status = await make_get_request(url, params=query_data)

    assert status == expected


@pytest.mark.parametrize("test_input,expected", [("0", HTTPStatus.UNPROCESSABLE_ENTITY),
                                                 ("-1", HTTPStatus.UNPROCESSABLE_ENTITY)])
async def test_get_all_invalid_page_number(make_get_request, test_input, expected):
    url = test_settings.service_url + f'/api/v1/search'
    query_data = {'page[number]': test_input}

    _, status = await make_get_request(url, params=query_data)

    assert status == expected


async def test_common_search_pagination(make_get_request, existing_film: dict):
    url = test_settings.service_url + '/api/v1/search'
    query_data = {'query': existing_film['title'], 'page[number]': 1, 'page[size]': 5}

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert body['found_number'] != 0

    if body['found_number'] < query_data['page[size]']:
        assert len(body['result']) == body['found_number']
    else:
        assert len(body['result']) == query_data['page[size]']
