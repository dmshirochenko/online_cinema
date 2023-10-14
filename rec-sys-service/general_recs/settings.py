from pydantic import BaseSettings


class AppSettings(BaseSettings):
    ugc_api_url: str = "http://ugc_api:8000"
    recsys_db_host: str = "db_ml"
    recsys_db_port: int = 6380
    recsys_db_name: str = "usg_ml"
    recsys_coll_name: str = "users_likes"


app_settings = AppSettings()
