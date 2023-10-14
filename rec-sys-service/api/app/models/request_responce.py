from fastapi import Query
from pydantic import BaseModel


class MovieOut(BaseModel):
    uuid: str = Query(..., description="movie uuid", examples=["12345678-1234-5678-1234-567812345678"])
    title: str = Query(..., description="movie title", examples=["Star Wars"])
    genres: list[str] = Query(..., description="list of movie's genres", examples=[["action", "drama"]])
    description: str = Query(..., description="movie description", examples=["large text"])
    rating: float = Query(..., description="movie rating", examples=[5.7])
    director: str = Query(..., description="movie director", examples=["James Cameron"])


class UserViewCountIn(BaseModel):
    view_count: str


class MovieIn(BaseModel):
    id: str
    title: str
    imdb_rating: float = 0.0
