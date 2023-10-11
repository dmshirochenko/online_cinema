import json
import logging
import time

import aiohttp
import elasticsearch
import pytest
from conf import es_settings, test_settings
from elasticsearch import Elasticsearch
from faker import Faker
from flask_jwt_extended import create_access_token

from models.user import LoginRecord, User
from src.db.users import db, init_db
from src.main import create_app

fake = Faker()
username = fake.first_name() + fake.last_name()
email = fake.email()
password = fake.password()


@pytest.fixture
def app():
    app = create_app()
    init_db(app)
    app.config.update({"TESTING": True, "WTF_CSRF_ENABLED": False})

    yield app

    db.drop_all()


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def test_username() -> str:
    return username


@pytest.fixture
def test_password() -> str:
    return password


@pytest.fixture
def invalid_username() -> str:
    return username + "?"


@pytest.fixture
def invalid_password() -> str:
    return password + "?"


@pytest.fixture
def test_user() -> dict[str, str]:
    return {
        "username": username,
        "email": email,
        "password": password,
    }


test_auth_user_name = fake.first_name()
test_auth_user_email = fake.email()
test_auth_user_password = fake.password()


@pytest.fixture
def test_auth_user() -> dict[str, str]:
    return {
        "username": test_auth_user_name,
        "email": test_auth_user_email,
        "password": test_auth_user_password,
    }


# --- Authentication section ---


@pytest.fixture
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(aiohttp_session):
    async def inner(url: str, params: dict | None = None):
        print("INSIDE MAKE_GET_REQUEST: ", url, params)
        async with aiohttp_session.get(url, params=params) as response:
            body = await response.json()
            print("GOT BODY: ", body)
            print("RESPONSE STATUS: ", response.status)
            return body, response.status

    return inner


def load_data() -> dict[str, dict]:
    with open(test_settings.data_path, "r") as f:
        data = json.load(f)
    logging.info("Data loaded from disk")
    return data


DATA = load_data()


def create_index(client: Elasticsearch, index: str) -> None:
    try:
        with open(es_settings.scheme_path[index], "r") as f:
            scheme = json.load(f)
        client.indices.create(index=index, body=scheme)
        logging.info(f"Index {index} created")
    except elasticsearch.exceptions.RequestError as ex:
        if ex.error == "resource_already_exists_exception":
            pass
        else:
            raise ex


def delete_index(client: Elasticsearch, index: str):
    try:
        client.indices.delete(index=index)
        logging.info(f"Index {index} deleted")
    except elasticsearch.exceptions.RequestError:
        pass


def load_index(client: Elasticsearch, index: str, data: dict[str, dict]) -> None:
    """Load data into given elasticseach index."""

    bulk_data = []
    for _id, _data in data.items():
        index_dict = {"index": {"_index": index, "_id": _id}}
        bulk_data.append(index_dict)
        bulk_data.append({k: v for k, v in _data.items()})

    es_response = client.bulk(index=index, body=bulk_data)
    if es_response["errors"]:
        logging.error(f"Error during ES update: {es_response}")


def pytest_sessionstart(session):
    client = Elasticsearch(**es_settings.dict())
    for index in ("genre", "person", "movies"):
        create_index(client, index)
        load_index(client, index, DATA[index])
        time.sleep(1)


def pytest_sessionfinish(session, exitstatus):
    client = Elasticsearch(**es_settings.dict())
    for index in ("genre", "person", "movies"):
        delete_index(client, index)


def teardown_module():
    LoginRecord.query.delete()
    User.query.delete()


@pytest.fixture
def existing_genre() -> dict:
    return list(DATA["genre"].values())[0]


@pytest.fixture
def existing_person() -> dict:
    return list(DATA["person"].values())[0]


@pytest.fixture
def existing_movie() -> dict:
    return list(DATA["movies"].values())[0]


@pytest.fixture
def resource_service_url() -> str:
    return test_settings.service_url


test_admin_user_name = fake.first_name()
test_admin_user_email = fake.email()
test_admin_user_password = fake.password()


@pytest.fixture
def test_admin_user() -> dict[str, str]:
    return {
        "username": test_admin_user_name,
        "email": test_admin_user_email,
        "password": test_admin_user_password,
    }
