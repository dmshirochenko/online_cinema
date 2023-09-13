import uuid
from http import HTTPStatus
from typing import Type

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.messages import PERSON_FILMS_NOT_FOUND, PERSONS_NOT_FOUND
from core.auth import auth_route
from models.common import ResponseModel
from models.film import Film
from models.person import PersonDetail as Person
from services.person import PersonService, get_person_service
from views.views import BaseView, PaginationParams


class PersonView(BaseView):
    def __init__(self, model_cls: Type[Person], not_found_msg: str):
        super().__init__(model_cls, not_found_msg)

        self.router = APIRouter()
        self.router.add_api_route(
            "/search",
            self.search,
            methods=["GET"],
            response_model=ResponseModel,
            description="Search person by their names",
        )
        self.router.add_api_route(
            "/{person_id}",
            self.get_details,
            methods=["GET"],
            response_model=Person,
            dependencies=[Depends(auth_route)],
            description="Get person details",
        )
        self.router.add_api_route(
            "/{person_id}/films",
            self.get_films,
            methods=["GET"],
            response_model=list[Film],
            description="Get list of films that include given person",
        )

    async def search(
        self,
        query: str,
        pagination: PaginationParams = Depends(PaginationParams),
        person_service: PersonService = Depends(get_person_service),
    ) -> ResponseModel:
        return await super().search(query, pagination.page_number, pagination.page_size, person_service)

    async def get_details(
        self,
        person_id: uuid.UUID,
        service: PersonService = Depends(get_person_service),
        valid_cls: BaseModel | None = None,
    ) -> Person:
        return await super().get_details(person_id, service, valid_cls)

    async def get_films(
        self,
        person_id: uuid.UUID,
        person_service: PersonService = Depends(get_person_service),
    ):
        films = await person_service.get_films(str(person_id))
        if not films:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PERSON_FILMS_NOT_FOUND)

        return [Film(**f) for f in films]


view = PersonView(model_cls=Person, not_found_msg=PERSONS_NOT_FOUND)
