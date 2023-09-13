import aioredis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films, genre, person, search
from core.config import PROJECT_NAME, ElasticSettings, RedisSettings
from db import elastic, redis

elastic_cfg = ElasticSettings()
redis_cfg = RedisSettings()


tags_metadata = [
    {
        "name": "films",
        "description": "Manage Main page and page with information about specific film by id. Search.",
    },
    {
        "name": "genres",
        "description": "Manage Genres page. Search.",
    },
    {
        "name": "persons",
        "description": "Manage Persons page and information about specific person by id. Search.",
    },
    {
        "name": "search",
        "description": "Common search to find the most similar items in elastic",
    }
]


app = FastAPI(
    title=PROJECT_NAME,
    docs_url="/api/docs",
    openapi_url="/api/docs.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = await aioredis.create_redis_pool(
        (redis_cfg.host, redis_cfg.port), minsize=10, maxsize=20
    )
    elastic.es = AsyncElasticsearch(**elastic_cfg.dict())


@app.on_event("shutdown")
async def shutdown():
    redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()


app.include_router(films.view.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genre.view.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(person.view.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(search.view.router, prefix="/api/v1/search", tags=["search"])
