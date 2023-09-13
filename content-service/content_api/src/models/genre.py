from models.abstract_model import AbstractModel


class Genre(AbstractModel):
    name: str
    description: str = ''
