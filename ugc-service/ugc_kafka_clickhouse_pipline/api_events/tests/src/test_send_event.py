from http import HTTPStatus
import asyncio
import pytest


@pytest.mark.asyncio
async def test_send_event(make_post_request, resource_url):
    test_data = {
        "id": "8b22c4d6-6f66-4e8f-87ab-5c4924b06c92",
        "user_id": "3ce2a79f-9b94-4d8a-a79f-f31608c0a3f0",
        "movie_id": "f4b334ba-976f-4ad9-a718-81c492a60c8f",
        "movie_progress": 5,
        "movie_length": 10,
        "time_created": "2023-07-14T09:37:20.159Z",
    }

    _, status = await make_post_request(f"{resource_url}/api/v1/send_event", json=test_data)
    assert status == HTTPStatus.OK
