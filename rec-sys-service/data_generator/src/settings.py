from pydantic import BaseSettings


class AppSettings(BaseSettings):
    auth_url: str = "http://auth:5000"

    n_users: int = 10
    n_likes: int = 500


app_settings = AppSettings()
