from http import HTTPStatus

import pytest
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from models.user import User

pytestmark = pytest.mark.asyncio


def get_access_headers(email: str) -> dict:
    _identity = User.query.filter_by(email=email).first().login
    access_token = create_access_token(identity=_identity)
    return {"Authorization": "Bearer {}".format(access_token)}


def signup_user(client, test_auth_user):
    data = {
        "username": test_auth_user["username"],
        "email": test_auth_user["email"],
        "password": test_auth_user["password"],
        "confirm": test_auth_user["password"],
    }

    client.post("/auth/api/v1/signup", data=data)
    user = User.query.filter_by(email=test_auth_user["email"]).first()

    return user


async def test_genre_access(
    client: FlaskClient,
    make_get_request,
    test_auth_user: dict[str, str],
    resource_service_url: str,
    existing_genre: dict,
):
    signup_user(client, test_auth_user)

    url = f"{resource_service_url}/api/v1/genres/{existing_genre['id']}"
    access_headers = get_access_headers(test_auth_user["email"])

    _, status = await make_get_request(url, params=access_headers)
    assert status == HTTPStatus.OK

    _, status = await make_get_request(url)
    assert status == HTTPStatus.UNAUTHORIZED


async def test_person_access(
    make_get_request,
    test_auth_user: dict[str, str],
    resource_service_url: str,
    existing_person: dict,
):
    url = f"{resource_service_url}/api/v1/persons/{existing_person['id']}"
    access_headers = get_access_headers(test_auth_user["email"])

    _, status = await make_get_request(url, params=access_headers)
    assert status == HTTPStatus.OK

    _, status = await make_get_request(url)
    assert status == HTTPStatus.UNAUTHORIZED


async def test_movie_access(
    make_get_request,
    test_auth_user: dict[str, str],
    resource_service_url: str,
    existing_movie: dict,
):
    url = f"{resource_service_url}/api/v1/films/{existing_movie['id']}"
    access_headers = get_access_headers(test_auth_user["email"])

    _, status = await make_get_request(url, params=access_headers)
    assert status == HTTPStatus.OK

    _, status = await make_get_request(url)
    assert status == HTTPStatus.UNAUTHORIZED
