from pydantic_settings import BaseSettings, SettingsConfigDict


class DBEmbeddingsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_EMBEDDED_")
    host: str = "db_embeddings"
    port: int = 6382


class DBSimilarSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_SIMILAR_")
    host: str = "db_recs_similar"
    port: int = 6381


class DBContentSettings(BaseSettings):
    host: str = "http://service:8000"


class Settings(BaseSettings):
    Embeddings: DBEmbeddingsSettings = DBEmbeddingsSettings()
    Similar: DBSimilarSettings = DBSimilarSettings()
    Content: DBContentSettings = DBContentSettings()

    model_path: str = "/opt/app/models/encoder_epoch_499.pt"
    feature_extractor_path: str = "/opt/app/models/feature_extractor.pickle"


settings = Settings()
