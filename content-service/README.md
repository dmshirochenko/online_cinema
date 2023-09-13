# Content App

## Async API service for online cinema

____
### Description

#### Technologies
* Backbone: Python + FastAPI
* Application is run via ASGI(uvicorn)
* Elasticsearch is used a search engine
* Redis Cluster is used for data caching
* Docker connects and launches all the components

___
### Endpoints

#### Documentary
* Open API docs
```/api/docs```


#### Main page
* Popular movies
```/api/v1/films?sort=-imdb_rating```
* Genre and corresponding popular films
```/api/v1/films?sort=-imdb_rating&filter[genre]=<genre-uuid>```
* List of genres
```/api/v1/genres/```

#### Search
* Search for movies
```/api/v1/films/search/```
* Search for persons
```/api/v1/persons/search/```

#### Movie page
* Movie full info
```/api/v1/films/<uuid:UUID>/```
* Similar movies
```/api/v1/films/<uuid:UUID>?filter[genre]=True```

#### Genre page
* Genre info
```/api/v1/genres/<uuid:UUID>/```
* Popular films in genre
```/api/v1/genres/<uuid:UUID>/films?sort=-imdb_rating&filter[genre]=```


#### Person page
* Person info
```/api/v1/persons/<uuid:UUID>/```
* Movies of a person
```/api/v1/persons/<uuid:UUID>/films```

----
## Tests
### Description

- Films API (/films):
  - edge cases for data validation;
  - search for a given film;
  - list all films;
  - cached search;
- Genres API (/genres):
  - edge cases for data validation;
  - search for a given genre;
  - list all genres;
  - cached search;
- Persons API (/persons):
  - edge cases for data validation;
  - search for a given person;
  - list all movies for a given person;
  - list all persons;
  - cached search;
- Search API:
  - edge cases for data validation;
  - display only N found items;
  - search for item(s) given a phrase;
  - cached search;

----

## How to run

### Service

Configure `docker-compose.override.yaml` file for either developer or pruduction settings.

- ```docker-compose up -d --build```


### Tests

- ```cd content_api/tests/functional```
- ```docker-compose up -d --build```
- ```docker-compose logs -f --tail=200 tests```

----
