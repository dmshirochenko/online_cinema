from typing import Annotated
from http import HTTPStatus

import aiohttp
from fastapi import Header, HTTPException

from settings import auth_settings as conf


async def auth_route(Authorization: Annotated[str, Header()] = ""):
    url = f"http://{conf.host}:{conf.port}/{conf.auth_url}"
    # Skip authorizqtion in dev mode
    if conf.mode == "dev":
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Authorization": Authorization}) as resp:
            if resp.status != HTTPStatus.OK:
                raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
