import uuid
from enum import Enum
from functools import lru_cache
from typing import Type

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, FilmDetails
from services.rebase import BaseService


class SortField(str, Enum):
    asc = "+imdb_rating"
    desc = "-imdb_rating"


class FilmService(BaseService):
    """
    Service to manage films queries.

    Args:
        redis: Redis client
        elastic: ElasticSearch client
        index: name of index for service's queries ('movies')
        validator_cls: data validation class
    """

    def __init__(
        self, redis: Redis, elastic: AsyncElasticsearch, index: str, validator_cls: Type[Film],
    ):
        super().__init__(redis, elastic, index, validator_cls)

    async def sort_by_rating(
        self, sort_val: SortField | None, page_number: int, page_size: int, genre_filter: uuid.UUID | None
    ) -> dict[str, int | list[FilmDetails]] | None:
        """
        Get popular films from elasticsearch sorted by imdb_rating.

        Args:
            sort_val: sort in 'acs' or 'desc' order, None for no sorting
            page_number: number of page to show up
            page_size: number of entries per page
            genre_filter: genre id to filter popular films exact the same genre

        Returns:
            list of films with details in FilmDetails model format or None
        """
        sort_val = 'no_sort' if sort_val is None else sort_val.name
        genre_val = 'no_filter' if genre_filter is None else genre_filter

        redis_key = f'sort={sort_val}?page[number]={page_number}?page[size]={page_size}?genre_id={genre_val}'
        docs = await self.cache.search_from_storage(index=redis_key, validator_cls=FilmDetails)

        if not docs:
            docs = await self._sort_by_rating_elastic(
                sort_val, page_number=page_number, page_size=page_size, genre_id=genre_filter
            )
            if not docs:
                return None
            await self.cache.put_doc_to_storage(redis_key, orjson.dumps(docs))

        return docs

    async def _sort_by_rating_elastic(
        self, sort_val: str, page_size: int, page_number: int, genre_id: uuid.UUID | None
    ) -> dict[str, int | list[FilmDetails]] | None:
        body = {'from': page_size * (page_number - 1), 'size': page_size, 'query': {'match_all': {}}}

        if sort_val in SortField._member_map_.keys():
            body.update({'sort': [{'imdb_rating': sort_val}]})

        if genre_id is not None:
            body['query'] = {
                'bool': {
                    'must': [
                        {'bool': {'must': [{'match_all': {}}]}},
                        {
                            'nested': {
                                'path': 'genres',
                                'query': {'bool': {'should': [{'match': {'genres.id': genre_id}}]}},
                            }
                        },
                    ]
                }
            }

        return await self.elastic.search_from_storage(search_body=body, validator_cls=FilmDetails)

    async def filter_by_genre(
        self, film_list: list[Film], genre_filter: uuid.UUID
    ) -> list[Film]:
        """
        Filter films by genre.

        Args:
            film_list: list of films
            genre_filter: genre_id to filter
        Returns:
            list of films in Film model format
        """
        res_list = []
        if isinstance(genre_filter, uuid.UUID):
            genre_filter = str(genre_filter)
        for film in film_list:
            genres = [genre.id for genre in film.genres]
            if genre_filter not in genres:
                continue
            res_list.append(film)

        return res_list

    @staticmethod
    def get_search_query(query: str) -> dict:
        """
        Search query on films from elastisearch using input query and ranging of fields priority.

        Args:
            query: string with word(s) to search
        Returns:
            dict of search body for elastic query
        """
        return {'multi_match': {'query': query.lower(), 'fields': ['title^3', 'description^1'],}}

    async def get_films_by_genre(self, film: FilmDetails) -> list[Film] | None:
        """
        Get films with the same genres as genres of input film.

        Args:
            film: film information
        Returns:
            list of films in Film model format or None
        """
        redis_key = f'{film.id}_similar_genre'

        docs = await self.cache.search_from_storage(index=redis_key)
        if not docs:
            docs = await self._get_films_by_genre_elastic(film)
            if not docs:
                return None
            await self.cache.put_doc_to_storage(redis_key, orjson.dumps(docs))

        return docs['result']

    async def _get_films_by_genre_elastic(self, film: FilmDetails) -> dict[str, int | Film] | None:
        res_list = []
        try:
            for genre in film.genres:
                docs = await self.elastic.storage.search(
                    index=self.index,
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "must_not": [{"match": {"id": film.id}}]
                                        }
                                    },
                                    {
                                        "nested": {
                                            "path": "genres",
                                            "query": {
                                                "bool": {
                                                    "should": [
                                                        {
                                                            "match": {
                                                                "genres.name": genre.name
                                                            }
                                                        }
                                                    ]
                                                }
                                            },
                                        }
                                    },
                                ]
                            }
                        }
                    },
                )
                ids = [f.id for f in res_list]
                for hit in docs['hits']['hits']:
                    res_film = self.validator_cls(**hit['_source']).dict()
                    if res_film.id not in ids:
                        res_list.append(res_film)
        except NotFoundError:
            return None

        res = {'found_number': len(res_list), 'result': res_list}

        return res

    async def get_all_films(self, page_number: int, page_size: int):
        body = {'from': page_size * (page_number - 1), 'size': page_size, 'query': {'match_all': {}}}
        return await self.elastic.search_from_storage(search_body=body, validator_cls=FilmDetails)

@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis), elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic, 'movies', Film)
