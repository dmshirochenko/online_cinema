import uuid
from http import HTTPStatus
from typing import Type

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.messages import GENRE_NOT_FOUND
from core.auth import auth_route
from services.genre import GenreService, get_genre_service
from views.views import BaseView


class Genre(BaseModel):
    id: str
    name: str


class GenreView(BaseView):
    def __init__(self, model_cls: Type[Genre], not_found_msg: str):
        super().__init__(model_cls, not_found_msg)

        self.router = APIRouter()
        self.router.add_api_route(
            "/{genre_id}",
            self.get_details,
            methods=["GET"],
            dependencies=[Depends(auth_route)],
            description="Get genre details",
        )
        self.router.add_api_route("/", self.get_all, methods=["GET"], description="Get list of all genres")

    async def get_details(
        self,
        genre_id: uuid.UUID,
        service: GenreService = Depends(get_genre_service),
        valid_cls: BaseModel | None = None,
    ) -> Genre:
        return await super().get_details(genre_id, service, valid_cls)

    async def get_all(self, service: GenreService = Depends(get_genre_service)) -> list[Genre]:
        genre_list = await service.get_all()
        if not genre_list:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=self.not_found_msg)

        return [Genre(id=g["id"], name=g["name"]) for g in genre_list]


view = GenreView(model_cls=Genre, not_found_msg=GENRE_NOT_FOUND)
