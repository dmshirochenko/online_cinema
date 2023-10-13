import os
import logging
import aiohttp
import pytest
import pytest_asyncio

from settings import test_settings


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


@pytest_asyncio.fixture
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
def make_post_request(aiohttp_session):
    async def inner(url: str, json: dict | None = None):
        async with aiohttp_session.post(url, json=json) as response:
            body = await response.json()
            return body, response.status

    return inner


@pytest.fixture
def resource_url() -> str:
    return test_settings.events_service_url
