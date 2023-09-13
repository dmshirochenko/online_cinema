import uuid
from http import HTTPStatus

import pytest
from aioredis import Redis

from tests.functional.settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_get_id_cache(make_get_request, existing_film: dict, cache: Redis):
    _id = existing_film["id"]
    url = test_settings.service_url + f"/api/v1/films/{_id}"
    cached_objects_1 = cache.dbsize()

    await make_get_request(url)
    body, status = await make_get_request(url)  # by cache logic
    cached_objects_2 = cache.dbsize()

    assert status == HTTPStatus.OK
    assert body["id"] == _id
    assert cached_objects_2 - cached_objects_1 == 1


async def test_get_id_valid(make_get_request, existing_film: dict):
    _id = existing_film["id"]
    url = test_settings.service_url + f"/api/v1/films/{_id}"

    body, status = await make_get_request(url)

    assert status == HTTPStatus.OK
    assert body["id"] == _id


async def test_get_id_invalid(make_get_request):
    _id = str(uuid.uuid4())
    url = test_settings.service_url + f"/api/v1/films/{_id}"

    _, status = await make_get_request(url)

    assert status == HTTPStatus.NOT_FOUND


async def test_get_films_by_search_exist(make_get_request, existing_film: dict):
    url = test_settings.service_url + "/api/v1/films/search"
    query_data = {"query": existing_film["title"]}

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert body["result"][0]["title"] == query_data["query"]


async def test_get_films_by_search_absence(make_get_request):
    url = test_settings.service_url + "/api/v1/films/search"
    query_data = {"query": "+++"}

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert body["found_number"] == 0
    assert body["result"] == []


async def test_get_all_no_sort(make_get_request, n_films: int):
    url = test_settings.service_url + "/api/v1/films"

    body, status = await make_get_request(url)

    assert status == HTTPStatus.OK
    assert body["found_number"] == n_films


async def test_get_all_asc(make_get_request, n_films: int):
    url = test_settings.service_url + "/api/v1/films"
    query_data = {"sort": "+imdb_rating"}

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert body["found_number"] == n_films
    assert all(
        body["result"][i]["imdb_rating"] <= body["result"][i + 1]["imdb_rating"] for i in range(len(body["result"]) - 1)
    )


async def test_get_all_desc(make_get_request, n_films: int):
    url = test_settings.service_url + "/api/v1/films"
    query_data = {"sort": "-imdb_rating"}

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert body["found_number"] == n_films
    assert all(
        body["result"][i]["imdb_rating"] >= body["result"][i + 1]["imdb_rating"] for i in range(len(body["result"]) - 1)
    )


@pytest.mark.parametrize(
    "test_input,expected",
    [("5", HTTPStatus.OK), ("0", HTTPStatus.UNPROCESSABLE_ENTITY), ("-1", HTTPStatus.UNPROCESSABLE_ENTITY)],
)
async def test_get_all_invalid_page_size(make_get_request, test_input, expected):
    url = test_settings.service_url + "/api/v1/films"
    query_data = {"page[size]": test_input}

    body, status = await make_get_request(url, params=query_data)

    assert status == expected

    if status == HTTPStatus.OK:
        assert len(body["result"]) == int(test_input)


@pytest.mark.parametrize(
    "test_input,expected", [("0", HTTPStatus.UNPROCESSABLE_ENTITY), ("-1", HTTPStatus.UNPROCESSABLE_ENTITY)]
)
async def test_get_all_invalid_page_number(make_get_request, test_input, expected):
    url = test_settings.service_url + "/api/v1/films"
    query_data = {"page[number]": test_input}

    _, status = await make_get_request(url, params=query_data)

    assert status == expected


@pytest.mark.parametrize("test_input,expected", [("1", HTTPStatus.OK)])
async def test_get_all_valid_page_number(make_get_request, test_input, expected):
    url = test_settings.service_url + "/api/v1/films"

    query_data_2 = {"page[number]": test_input}
    body_2, status = await make_get_request(url, params=query_data_2)
    assert status == expected

    query_data_1 = {"page[number]": str(int(test_input) + 1)}
    body_1, status = await make_get_request(url, params=query_data_1)
    assert status == expected

    assert body_1["result"] != body_2["result"]


async def test_get_all_filter_genre(make_get_request, all_films: list):
    url = test_settings.service_url + "/api/v1/films"
    genre_id = all_films[0]["genres"][0]["id"]
    query_data = {"filter[genre]": genre_id}

    films_amount = 0
    for film in all_films:
        genres = [genre["id"] for genre in film["genres"]]
        if genre_id in genres:
            films_amount += 1

    body, status = await make_get_request(url, params=query_data)

    assert status == HTTPStatus.OK
    assert body["found_number"] == films_amount
