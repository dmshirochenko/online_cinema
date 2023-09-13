from abc import ABC, abstractmethod
import logging
from typing import Any, Type

import orjson
import pydantic
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from models.abstract_model import AbstractModel

CACHE_EXPIRE_IN_SECONDS = 60 * 5


class AbstractStorage(ABC):
    """
    Abstract class to manage storages.

    Args:
        storage: object of data storage, which contains methods get, set and search
        index: name of index (index or key)
        validator_cls: data validation class
    """
    def __init__(self, storage: Any, index: str, validator_cls: Type[AbstractModel]):
        self.storage = storage
        self.index = index
        self.validator_cls = validator_cls

    @abstractmethod
    async def get_doc_from_storage(self, _id: str, validator_cls: AbstractModel = None) -> AbstractModel:
        """
        Get data from the storage.

        Args:
            _id: name of index/key to get items
            validator_cls: data model to validate getting items

        Returns:
            data in AbstractModel format
        """
        pass

    @abstractmethod
    async def put_doc_to_storage(self, index: str, doc: Any) -> None:
        """
        Put data into the storage using index name.

        Args:
            index: name of index or key to set data item
            doc: object of data

        Returns:
            None
        """
        pass

    @abstractmethod
    async def search_from_storage(self, **kwargs) -> dict:
        """
        Search data in storage using keywords

        Args:
            **kwargs: attributes which are used to get data from storage;
                      ['index', 'search_body', 'validator_cls'] as possible attrs

        Returns:
            dictionary with results and number of found items
        """
        pass


class ElasticStorage(AbstractStorage):
    def __init__(self, storage: AsyncElasticsearch, index: str, validator_cls: Type[AbstractModel]):
        super().__init__(storage, index, validator_cls)

    async def get_doc_from_storage(self, _id: str, validator_cls: AbstractModel = None) -> AbstractModel | None:
        if not validator_cls:
            validator_cls = self.validator_cls
        try:
            doc = await self.storage.get(self.index, _id)
        except NotFoundError:
            return None

        return validator_cls(**doc['_source']) if doc else None

    async def put_doc_to_storage(self, index: str, doc: Any) -> None:
        pass

    async def search_from_storage(self, **kwargs) -> dict | None:
        """
        Search data in elastic

        Args:
            **kwargs:
            - 'search_body' - dict to set as query body in searching
            - 'validator_cls' - data model to validate getting items

        Returns:
            dictionary with results and number of found items
        """
        if not hasattr(kwargs, 'validator_cls'):
            validator_cls = self.validator_cls
        else:
            validator_cls = kwargs['validator_cls']

        try:
            doc = await self.storage.search(index=self.index, body=kwargs['search_body'],)
        except NotFoundError:
            return None

        results = []
        for hit in doc['hits']['hits']:
            try:
               results.append(validator_cls(**hit["_source"]).dict())
            except pydantic.error_wrappers.ValidationError:
                logging.error(f"Couldn't validate the following data: {hit['_source']}")

        return {
            'found_number': doc["hits"]["total"]["value"],
            'result': results,
        }


class RedisStorage(AbstractStorage):
    def __init__(self, storage: Redis, index: str, validator_cls: Type[AbstractModel]):
        super().__init__(storage, index, validator_cls)

    async def get_doc_from_storage(self, _id, validator_cls: AbstractModel = None):
        if not validator_cls:
            validator_cls = self.validator_cls
        doc = await self.storage.get(_id)
        return validator_cls.parse_raw(doc) if doc else None

    async def put_doc_to_storage(self, index: str | int, doc: dict) -> None:
        """
        Put data in redis storage with expire time of keeping it

        Args:
            index: name of key to set data item
            doc: object of data

        Returns:
            None
        """
        await self.storage.set(index, doc, expire=CACHE_EXPIRE_IN_SECONDS)

    async def search_from_storage(self, **kwargs) -> dict | None:
        """
        Search data in redis

        Args:
            **kwargs:
            - 'index' - name of key to get data from storage
            - 'validator_cls' - data model to validate getting items

        Returns:
            dictionary with results and number of found items
        """

        if not hasattr(kwargs, 'validator_cls'):
            validator_cls = self.validator_cls
        else:
            validator_cls = kwargs['validator_cls']
        data_json = await self.storage.get(kwargs['index'])
        if not data_json:
            return None

        data = orjson.loads(data_json)

        res = {'found_number': data['found_number'], 'result': [validator_cls(**doc).dict() for doc in data['result']]}

        return res
