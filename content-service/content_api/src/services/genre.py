from functools import lru_cache
from typing import Type

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.rebase import BaseService


class GenreService(BaseService):
    """
    Service to manage genre queries.

    Args:
        redis: Redis client
        elastic: ElasticSearch client
        index: name of index for service's queries ('genre')
        validator_cls: data validation class
    """
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str, validator_cls: Type[Genre]):
        super().__init__(redis, elastic, index, validator_cls)

        self._redis_key = "genres"

    async def get_all(self) -> list[Genre] | None:
        """
        get all genres in storage

        Returns:
            list of data in Genre model format or None
        """
        docs = await self.cache.search_from_storage(index=self._redis_key)
        if not docs:
            search_body = {'query': {'match_all': {}}}
            docs = await self.elastic.search_from_storage(search_body=search_body)
            if not docs:
                return None
            await self.cache.put_doc_to_storage(self._redis_key, orjson.dumps(docs))

        return docs['result']

    async def _search_from_elastic(self, query) -> None | list[Genre]:
        try:
            doc = await self.elastic.search(
                index="genre",
                body={
                    "size": 100,
                    "query": {"match": {"name": {"query": query, "fuzziness": "auto"}}},
                },
            )
        except NotFoundError:
            return None

        return [Genre(**hit["_source"]) for hit in doc["hits"]["hits"]]


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic, "genre", Genre)
