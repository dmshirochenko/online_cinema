from typing import Type

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch

from db.storages import ElasticStorage, RedisStorage
from models.abstract_model import AbstractModel


class BaseService:
    """
    Service to manage queries.

    Args:
        redis: Redis client
        elastic: ElasticSearch client
        index: name of index for service's queries
        validator_cls: data validation class
    """

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str, validator_cls: Type[AbstractModel]):
        self.cache = RedisStorage(redis, index, validator_cls)
        self.elastic = ElasticStorage(elastic, index, validator_cls)

        self.index = index
        self.validator_cls = validator_cls

    async def get_by_id(self, _id: str, validator_cls: AbstractModel = None) -> AbstractModel | None:
        """
        Get item from storage by id
        Args:
            _id: index of item in storage
            validator_cls: data model to validate getting item

        Returns:
            data in AbstractModel format or None
        """
        if not validator_cls:
            validator_cls = self.validator_cls
        doc = await self.cache.get_doc_from_storage(_id, validator_cls)
        if not doc:
            doc = await self.elastic.get_doc_from_storage(_id, validator_cls)
            if not doc:
                return None
            await self.cache.put_doc_to_storage(doc.id, doc.json())

        return doc

    async def search(self, query: str, page_number: int, page_size: int) -> dict[str, int | list[AbstractModel]] | None:
        """
        Search items in storage by input query using pagination results

        Args:
            query: keyword(s) to find items in storage
            page_number: number of page to display result
            page_size: amount of result records per page

        Returns:
            dictionary contains number of found items and list of data in AbstractModel format
        """
        redis_key = f"{self.index}:{query}?page[number]={page_number}?page[size]={page_size}"

        docs = await self.cache.search_from_storage(index=hash(redis_key))
        if not docs:
            search_body = {
                "from": page_size * (page_number - 1),
                "size": page_size,
                "query": self.get_search_query(query),
            }
            docs = await self.elastic.search_from_storage(search_body=search_body)
            if not docs:
                return None
            await self.cache.put_doc_to_storage(hash(redis_key), orjson.dumps(docs))

        return docs

    @staticmethod
    def get_search_query(query: str) -> dict:
        """
        Get search body to set into query
        Args:
            query: keyword(s) to find items in storage

        Returns:
            dictionary of query body
        """
        pass
