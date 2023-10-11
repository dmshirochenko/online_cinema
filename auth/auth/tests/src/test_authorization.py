import asyncio
import json
import uuid
from http import HTTPStatus

import pytest
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from requests.auth import _basic_auth_str

from db.users import db
from models.user import LoginRecord, User


def get_access_headers(email: str) -> dict:
    _identity = User.query.filter_by(email=email).first().login
    access_token = create_access_token(identity=_identity)
    return {"Authorization": "Bearer {}".format(access_token)}


def test_signup(client: FlaskClient, test_user: dict[str, str]):
    data = {
        "username": test_user["username"],
        "email": test_user["email"],
        "password": test_user["password"],
        "confirm": test_user["password"],
    }

    num_users = User.query.count()
    response = client.post("/auth/api/v1/signup", data=data)
    user = User.query.filter_by(email=test_user["email"]).first()

    assert response.status_code == HTTPStatus.CREATED
    assert User.query.count() - num_users == 1
    assert user.login == test_user["username"]

    # Singup with the same login
    response = client.post("/auth/api/v1/signup", data=data)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    "username, email, password, confirm",
    [
        ("", "sample@gmail.com", "password", "password"),  # Empty login
        ("SomeLogin", "sample1@gmail.com", "", ""),  # Empty password
        ("1", "sample@gmail.com", "SomePassword", "SomePassword"),  # Invalid login
        ("SomeLogin", "sample@gmail.com", "1", "1"),  # Too short password
        ("SomeLogin", "123", "SomePassword", "SomePassword"),  # Invalid email
        (
            "SomeLogin",
            "sample@gmail.com",
            "SomePassword",
            "SomePassword1",
        ),  # Mismatching passwords
    ],
)
def test_signup_invalid(client: FlaskClient, username: str, email: str, password: str, confirm: str):
    data = {
        "username": username,
        "email": email,
        "password": password,
        "confirm": confirm,
    }

    response = client.post("/auth/api/v1/signup", data=data)
    user = User.query.filter_by(email=email).first()

    assert user is None
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    "username,password,status_code",
    [
        ("test_username", "test_password", HTTPStatus.OK),
        ("invalid_username", "test_password", HTTPStatus.UNAUTHORIZED),
        ("test_username", "invalid_password", HTTPStatus.UNAUTHORIZED),
        ("invalid_username", "invalid_password", HTTPStatus.UNAUTHORIZED),
    ],
)
def test_login(client: FlaskClient, username: str, password: str, status_code: str, request: str):
    username = request.getfixturevalue(username)
    password = request.getfixturevalue(password)
    headers = {"Authorization": _basic_auth_str(username, password)}
    num_login_records = LoginRecord.query.count()
    response = client.get("/auth/api/v1/login", headers=headers)

    if status_code == HTTPStatus.OK:
        assert LoginRecord.query.count() - num_login_records == 1
    assert response.status_code == status_code


def test_user_edit(client: FlaskClient, test_user: dict[str, str]):
    access_headers = get_access_headers(test_user["email"])

    _id = User.query.filter_by(email=test_user["email"]).first().id
    new_login = test_user["username"] + "Updated"
    test_user["username"] = new_login
    response = client.put(f"/auth/api/v1/user/{_id}", json=test_user, headers=access_headers)

    user = User.query.filter_by(email=test_user["email"]).first()
    assert response.status_code == HTTPStatus.OK
    assert user.login == new_login


def test_user_edit_nonexistent(client: FlaskClient, test_user: dict[str, str]):
    _id = uuid.uuid4()
    test_user["username"] = test_user["username"] + "Updated"
    access_headers = get_access_headers(test_user["email"])
    response = client.put(f"/auth/api/v1/user/{_id}", json=test_user, headers=access_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_all_users(client: FlaskClient, test_user: dict[str, str]):
    access_headers = get_access_headers(test_user["email"])
    response = client.get("/auth/api/v1/users", headers=access_headers)

    assert response.status_code == HTTPStatus.OK
    assert len(json.loads(response.data)["users"]) > 0


def test_login_history(client: FlaskClient, test_user: dict[str, str]):
    access_headers = get_access_headers(test_user["email"])
    response = client.get("/auth/api/v1/login_history/1", headers=access_headers)

    assert len(json.loads(response.data)) > 0
    assert response.status_code == HTTPStatus.OK


def test_logout(client: FlaskClient, test_user):
    access_headers = get_access_headers(test_user["email"])
    response = client.delete("/auth/api/v1/logout", headers=access_headers)

    assert response.status_code == HTTPStatus.OK
