import uuid
from http import HTTPStatus
from typing import Type

from fastapi import HTTPException, Query
from pydantic import BaseModel

from models.common import ResponseModel
from services.rebase import BaseService


class PaginationParams:

    def __init__(self, 
        page_number: int = Query(default=1, alias='page[number]', description='Page number for pagination', ge=1,),
        page_size: int = Query(default=20, alias='page[size]', description='Items amount on page', ge=1)):
        self.page_number = page_number
        self.page_size = page_size


class BaseView:
    def __init__(self, model_cls: Type[BaseModel], not_found_msg: str):
        self.model_cls = model_cls
        self.not_found_msg = not_found_msg

    async def get_details(self, _id: uuid.UUID, service: BaseService,
                          valid_cls: Type[BaseModel] | None = None) -> BaseModel:
        doc = await service.get_by_id(str(_id), validator_cls=valid_cls)
        if not doc:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=self.not_found_msg)
        return self.model_cls(**doc.dict())

    async def search(
        self,
        query: str,
        page_number: int | None = Query(1, alias='page[number]', ge=1),
        page_size: int | None = Query(50, alias='page[size]', ge=1),
        service: BaseService = None,
    ) -> ResponseModel:
        res = await service.search(query, page_number, page_size)
        if not res:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=self.not_found_msg)

        res = {
            'page_number': page_number,
            'page_size': page_size,
            'found_number': res['found_number'],
            'result': res['result'],
        }

        return ResponseModel(**res)
