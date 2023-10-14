from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    ugc_api_url: str = "ugc"
    usc_api_user_viewed_count: str = "api/v1/user_viewed_count"
    content_api_url: str = "service"
    content_api_popular_movies: str = "/api/v1/films?sort=-imdb_rating"
    min_stored_actions: int = 10

    redis_host: str = "redis-view_count"
    redis_port: int = 6379

    request_timeout_secs: int = 2

    db_general_host: str = "db_ml"
    db_general_port: int = 6380
    db_similar_host: str = "db_recs_similar"
    db_similar_port: int = 6381

    recsys_n_recs: int = 20


app_settings = AppSettings()
