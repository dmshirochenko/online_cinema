from pydantic import BaseModel


class ResponseModel(BaseModel):
    page_number: int
    page_size: int
    found_number: int
    result: list
