from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    es_host: str = Field("http://localhost:9200", validation_alias="ES_HOST")
    es_username: str | None = Field(None, validation_alias="ES_USERNAME")
    es_password: str | None = Field(None, validation_alias="ES_PASSWORD")
    es_index: str = Field("products", validation_alias="ES_INDEX")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

