"""Service request routes."""

import logging

# import logstash
import sentry_sdk
import requests_async as requests
from sentry_sdk.integrations import fastapi
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from settings import app_settings as conf
from api.v1.ratings import router as ratings_router
from api.v1.reviews import router as reviews_router
from api.v1.bookmarks import router as bookmarks_router
from api.v1.watched import router as watched_router

if conf.sentry_dsn:
    sentry_sdk.init(integrations=[fastapi.FastApiIntegration()])

app = FastAPI()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# logstash_handler = logstash.LogstashHandler(conf.logstash_url, conf.logstash_port, version=1)

# logger.addHandler(logstash_handler)

app.include_router(ratings_router)
app.include_router(reviews_router)
app.include_router(bookmarks_router)
app.include_router(watched_router)


@app.get("/ugc/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint. Returns 200 status with a simple JSON payload if the service is healthy.
    """
    return JSONResponse(content={"status": "ok"}, status_code=200)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Do checking X-Request-Id.

    Raises:
        RuntimeError: X-Request-Id check fail

    Args:
        request (Request): request data to
        call_next: next action function

    Returns:
        data: data from next action
    """
    request_id = request.headers.get("X-Request-Id")
    if not request_id and not conf.debug:
        raise RuntimeError("X-Request-id is required")
    return await call_next(request)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Do checking X-Request-Id.

    Raises:
        HTTPException: Invalid token

    Args:
        request (Request): request data to
        call_next: next action function

    Returns:
        data: data from next action
    """
    if not conf.debug:
        response = await requests.post(url=conf.auth_url, headers=request.headers)
        if response.status_code != 200:
            raise HTTPException(401, "Invalid token")
    return await call_next(request)
