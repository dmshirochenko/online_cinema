from models.abstract_model import AbstractModel
from models.genre import Genre
from models.person import Person


class Film(AbstractModel):
    title: str
    imdb_rating: float = 0.0


class FilmDetails(Film):
    movie_type: str = "movie"
    description: str = ""
    imdb_rating: float = 0.0
    film_rating: str = ""
    genres: list[Genre] = []
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []
    file_path: str = ""
