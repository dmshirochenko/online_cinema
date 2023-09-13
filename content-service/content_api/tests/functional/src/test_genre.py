import uuid
from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_get_id_valid(make_get_request, existing_genre: dict):
    _id = existing_genre['id']
    url = test_settings.service_url + f'/api/v1/genres/{_id}'

    body, status = await make_get_request(url)

    assert status == HTTPStatus.OK
    assert body['id'] == _id


async def test_get_id_invalid(make_get_request):
    _id = str(uuid.uuid4())
    url = test_settings.service_url + f'/api/v1/genres/{_id}'

    _, status = await make_get_request(url)

    assert status == HTTPStatus.NOT_FOUND


async def test_cache(make_get_request, existing_genre: dict):
    _id = existing_genre['id']
    url = test_settings.service_url + f'/api/v1/genres/{_id}'

    await make_get_request(url)
    body, status = await make_get_request(url)  # by cache logic

    assert status == HTTPStatus.OK
    assert body['id'] == _id


async def test_get_all_genres(make_get_request, n_genres: int):
    url = test_settings.service_url + '/api/v1/genres'

    body, status = await make_get_request(url)

    assert status == HTTPStatus.OK
    assert len(body) == n_genres
