import uuid
from http import HTTPStatus
from typing import Type

from fastapi import APIRouter, Depends, HTTPException, Query

from core.messages import FILMS_NOT_FOUND
from core.auth import auth_route
from models.common import ResponseModel
from models.film import Film, FilmDetails
from services.film import FilmService, SortField, get_film_service
from views.views import BaseView, PaginationParams


class FilmView(BaseView):
    def __init__(self, model_cls: Type[FilmDetails], not_found_msg: str):
        super().__init__(model_cls, not_found_msg)

        self.router = APIRouter()
        self.router.add_api_route(
            "/",
            self.popular_films,
            methods=["GET"],
            response_model=ResponseModel,
            description="Get the most popular film with filtering by genre",
        )
        self.router.add_api_route(
            "/search",
            self.search,
            methods=["GET"],
            response_model=ResponseModel,
            description="Get film from word searching query (in title, description, genre, actors, director",
        )
        self.router.add_api_route(
            "/all_films",
            self.get_all_films,
            methods=["GET"],
            response_model=ResponseModel,
            description="Get all films on resource",
        )
        self.router.add_api_route(
            "/{film_id}",
            self.film_details,
            methods=["GET"],
            response_model=FilmDetails | list[Film],
            dependencies=[Depends(auth_route)],
            description="Get details about film by film_id and films of the same genres",
        )

    async def popular_films(
        self,
        sort_imdb: SortField
        | None = Query(
            default=None,
            alias="sort",
            description="Ascending or descending order sorting",
        ),
        pagination: PaginationParams = Depends(PaginationParams),
        genre_filter: uuid.UUID | None = Query(default=None, alias="filter[genre]", description="Genre id"),
        film_service: FilmService = Depends(get_film_service),
    ) -> ResponseModel:
        films_res = await film_service.sort_by_rating(
            sort_imdb, pagination.page_number, pagination.page_size, genre_filter=genre_filter
        )
        if not films_res:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILMS_NOT_FOUND)

        res = {
            "page_number": pagination.page_number,
            "page_size": pagination.page_size,
            "found_number": films_res["found_number"],
            "result": [Film(**film) for film in films_res["result"]],
        }
        return ResponseModel(**res)

    async def search(
        self,
        query: str,
        pagination: PaginationParams = Depends(PaginationParams),
        film_service: FilmService = Depends(get_film_service),
    ) -> ResponseModel:
        return await super().search(query, pagination.page_number, pagination.page_size, film_service)

    async def film_details(
        self,
        film_id: uuid.UUID,
        genre_filter: bool = Query(
            default=False,
            alias="filter[genre]",
            description="Get films with the same genre",
        ),
        service: FilmService = Depends(get_film_service),
    ) -> FilmDetails | list[Film]:
        film = await super().get_details(film_id, service, self.model_cls)

        if genre_filter:
            film_list = await service.get_films_by_genre(film)
            return film_list

        return film

    async def get_all_films(
        self,
        pagination: PaginationParams = Depends(PaginationParams),
        film_service: FilmService = Depends(get_film_service),
    ) -> int:
        films = await film_service.get_all_films(pagination.page_number, pagination.page_size)
        res = {
            "page_number": pagination.page_number,
            "page_size": pagination.page_size,
            "found_number": films["found_number"],
            "result": [Film(**film) for film in films["result"]],
        }
        return ResponseModel(**res)


view = FilmView(model_cls=FilmDetails, not_found_msg=FILMS_NOT_FOUND)
