from functools import lru_cache
from typing import Type

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.abstract_model import AbstractModel
from models.film import Film
from models.person import Person
from services.rebase import BaseService


class SearchService(BaseService):
    """
    Service to manage common search queries.

    Args:
        redis: Redis client
        elastic: ElasticSearch client
        index: name of index ('movies' and 'person')
        validator_cls: data validation class
    """

    def __init__(
        self, redis: Redis, elastic: AsyncElasticsearch, index: str, validator_cls: Type[AbstractModel],
    ):
        super().__init__(redis, elastic, index, validator_cls)

    async def search(
        self, query: str, page_number: int, page_size: int
    ) -> dict[str, int | list[AbstractModel]] | None:
        """
        Search on films using input query and ranging of fields by priority.

        Args:
            query: string of input query
            page_number: number of page to display searching results
            page_size: amount of displayed searching results per page
        Returns:
            list of films and/or persons or None
        """
        redis_key = f'{self.index}:{query}?page[number]={page_number}?page[size]={page_size}'

        docs = await self._search_from_cache(redis_key)
        if not docs:
            search_body = {
                'from': page_size * (page_number - 1),
                'size': page_size,
                'query': self.get_search_query(query),
            }
            docs = await self._search_from_storage(search_body=search_body)
            if not docs:
                return None
            await self.cache.put_doc_to_storage(hash(redis_key), orjson.dumps(docs))

        return docs

    def get_search_query(self, query: str) -> dict:
        return {
            'multi_match': {
                'query': query.lower(),
                'fields': ['title^5', 'description^2', 'actors_names^1', 'full_name^3'],
            }
        }

    async def _search_from_cache(self, query: str) -> dict[str, int | list[Film | Person]] | None:
        data_json = await self.cache.storage.get(hash(query))
        if not data_json:
            return None

        data = orjson.loads(data_json)

        res = []
        for doc in data['result']:
            if 'full_name' in doc.keys():
                res.append(Person(**doc).dict())
            else:
                res.append(Film(**doc).dict())

        res = {'found_number': data['found_number'], 'result': res}

        return res

    async def _search_from_storage(self, search_body: dict) -> dict[str, int | list[Film | Person]] | None:
        try:
            docs = await self.elastic.storage.search(index=self.index.split(', '), body=search_body)
        except NotFoundError:
            return None

        res = {
            'found_number': docs['hits']['total']['value'],
            'result': [
                Film(**hit['_source']).dict() if hit['_index'] == 'movies' else Person(**hit['_source']).dict()
                for hit in docs['hits']['hits']
            ],
        }

        return res


@lru_cache()
def get_search_service(
    redis: Redis = Depends(get_redis), elastic: AsyncElasticsearch = Depends(get_elastic),
) -> SearchService:
    return SearchService(redis, elastic, 'movies, person', AbstractModel)
