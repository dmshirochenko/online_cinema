from typing import Type

from fastapi import APIRouter, Depends, Query

from core.messages import FILMS_NOT_FOUND
from models.abstract_model import AbstractModel
from models.common import ResponseModel
from services.common_search import SearchService, get_search_service
from views.views import BaseView


class SearchView(BaseView):
    def __init__(self, model_cls: Type[AbstractModel], not_found_msg: str):
        super().__init__(model_cls, not_found_msg)

        self.router = APIRouter()
        self.router.add_api_route(
            "/",
            self.search,
            methods=["GET"],
            response_model=ResponseModel,
            description="Get films from word searching query (in title, description, actors, director)",
        )

    async def search(
        self,
        query: str,
        page_number: int = Query(
            default=1,
            alias="page[number]",
            description="Page number for pagination",
            ge=1,
        ),
        page_size: int = Query(default=20, alias="page[size]", description="Items amount on page", ge=1),
        search_service: SearchService = Depends(get_search_service),
    ) -> ResponseModel:
        return await super().search(query, page_number=page_number, page_size=page_size, service=search_service)


view = SearchView(model_cls=AbstractModel, not_found_msg=FILMS_NOT_FOUND)
