from pydantic import BaseModel

# Models for validation puproses

class FilmworkElastic(BaseModel):
    id: str
    imdb_rating: float | None
    movie_type: str
    genre: list[str]
    genres: list[dict[str, str]]
    title: str
    description: str
    director: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: list[dict[str, str]]
    writers: list[dict[str, str]]
    directors: list[dict[str, str]]
    file_path: str


class GenreElastic(BaseModel):
    id: str
    name: str


class FilmPersonElastic(BaseModel):
    id: str
    title: str
    imdb_rating: float | None


class PersonElastic(BaseModel):
    id: str
    full_name: str
    role: list[str] = []
    films: list[FilmPersonElastic] = []


def normalize_filmwork(data: list[dict]) -> dict[str, dict]:
    """
    Normalise given list of dicts to the elastic-compatible format.
    """
    filmworks = {}

    for row in data:
        fw_id = row["id"]
        if fw_id not in filmworks:
            filmworks[fw_id] = {
                "id": fw_id,
                "imdb_rating": row["rating"],
                "genre": set(),
                "genres": {},
                "title": row["title"],
                "description": row["description"],
                "director": set(),
                "actors_names": set(),
                "writers_names": set(),
                "actors": {},
                "writers": {},
                "directors": {},
                "file_path": row["file_path"] if row["file_path"] is not None else '',
                "movie_type": row["type"] if row["type"] is not None else ''
            }

        fw = filmworks[fw_id]

        fw['genre'].add(row["genre"])
        fw['genres'][row["genre_id"]] = row["genre"]

        if row["role"] == "director":
            fw["director"].add(row["person_full_name"])
            fw["directors"][row["person_id"]] = row["person_full_name"]
        elif row["role"] == "actor":
            fw["actors_names"].add(row["person_full_name"])
            fw["actors"][row["person_id"]] = row["person_full_name"]
        elif row["role"] == "writer":
            fw["writers_names"].add(row["person_full_name"])
            fw["writers"][row["person_id"]] = row["person_full_name"]

    # Casting structure for Elasticsearch
    for fw_id in filmworks:
        filmworks[fw_id]["genre"] = list(filmworks[fw_id]["genre"])
        filmworks[fw_id]["director"] = list(filmworks[fw_id]["director"])
        filmworks[fw_id]["actors_names"] = list(filmworks[fw_id]["actors_names"])
        filmworks[fw_id]["writers_names"] = list(filmworks[fw_id]["writers_names"])

        genres_list = [{"id": _id, "name": name} for _id, name in filmworks[fw_id]["genres"].items()]
        filmworks[fw_id]["genres"] = genres_list

        actors_list = [{"id": _id, "full_name": name} for _id, name in filmworks[fw_id]["actors"].items()]
        filmworks[fw_id]["actors"] = actors_list

        writers_list = [{"id": _id, "full_name": name} for _id, name in filmworks[fw_id]["writers"].items()]
        filmworks[fw_id]["writers"] = writers_list

        directors_list = [{"id": _id, "full_name": name} for _id, name in filmworks[fw_id]["directors"].items()]
        filmworks[fw_id]["directors"] = directors_list

        # If description is null make it empty string
        if filmworks[fw_id]["description"] is None:
            filmworks[fw_id]["description"] = ""

    return filmworks


def validate_filmwork(data: dict[str, dict]) -> dict[str, dict]:
    for fw_id, fw_data in data.items():
        data[fw_id] = FilmworkElastic(**fw_data).dict()
    return data


def normalize_genre(data: list):
    genres = {}
    for row in data:
        genres[row[0]] = {
            "id": row[0],
            "name": row[1]
        }
    return genres


def normalize_person(data: list[dict]):
    persons = {}
    for row in data:
        p_id = row["person_id"]

        film = {
            "id": row["id"],
            "title": row["title"],
            "imdb_rating": row["rating"]
        }

        if p_id not in persons:
            persons[p_id] = {
                "id": p_id,
                "full_name": row["person_full_name"],
                "role": set([row["role"]]),
                "title_names": set([row["title"]]),
                "films": [film]
            }
        else:
            persons[p_id]["role"].add(row["role"])
            if row["title"] not in persons[p_id]["title_names"]:
                persons[p_id]["title_names"].add(row["title"])
                persons[p_id]["films"].append(film)

    return persons


def validate_genre(data: dict[str, dict]) -> dict[str, dict]:
    for _id, genre_data in data.items():
        data[_id] = GenreElastic(**genre_data).dict()
    return data


def validate_person(data: dict[str, dict]) -> dict[str, dict]:
    for _id, person_data in data.items():
        data[_id] = PersonElastic(**person_data).dict()

    return data


def make_normalizer(table):
    if table == "movies":
        return normalize_filmwork
    elif table == "genre":
        return normalize_genre
    elif table == "person":
        return normalize_person


def make_validator(table):
    if table == "movies":
        return validate_filmwork
    elif table == "genre":
        return validate_genre
    elif table == "person":
        return validate_person
