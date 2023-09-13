from functools import lru_cache
from typing import Type

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import PersonDetail, PersonFilms
from services.rebase import BaseService


def person2persondetail(data: dict) -> dict:
    """Add a list of film ids."""
    data["film_ids"] = [film["id"] for film in data["films"]]
    return data


class PersonService(BaseService):
    """
    Service to manage person queries.

    Args:
        redis: Redis client
        elastic: ElasticSearch client
        index: name of index for service's queries ('person')
        validator_cls: data validation class
    """
    def __init__(
        self, redis: Redis, elastic: AsyncElasticsearch, index: str, validator_cls: Type[PersonFilms],
    ):
        super().__init__(redis, elastic, index, validator_cls)

    async def get_by_id(self, _id: str, **kwargs) -> PersonDetail | None:
        doc = await super().get_by_id(_id)
        if not doc:
            return None

        doc = person2persondetail(doc.dict())
        return PersonDetail(**doc)

    async def search(self, query: str, page_number: int, page_size: int) -> None | dict[str, int | list[PersonDetail]]:
        docs = await super().search(query, page_number, page_size)
        if not docs:
            return None

        res = {
            'found_number': docs['found_number'],
            # Convert to PersonDetail view
            'result': [PersonDetail(**person2persondetail(film)) for film in docs['result']],
        }

        return res

    @staticmethod
    def get_search_query(query: str):
        return {'match': {'full_name': {'query': query, 'fuzziness': 'auto'}}}

    async def get_films(self, _id: str) -> None | list[PersonFilms]:
        """
        Get person and films in which they took part
        Args:
            _id: id of person

        Returns:
            list of data in PersonFilms model format or None
        """
        doc = await super().get_by_id(_id)
        if not doc:
            return None

        return [film for film in doc.dict()["films"]]


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis), elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic, "person", PersonFilms)
