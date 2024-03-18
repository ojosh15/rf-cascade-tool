from functools import cached_property

from pydantic import PostgresDsn, computed_field, Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    API_PREFIX: str = "/api/v1"

    # Postgres Params
    POSTGRES_HOST: str = Field(default=...)
    POSTGRES_USER: str = Field(default=...)
    POSTGRES_PASSWORD: str = Field(default=...)
    POSTGRES_DB: str = Field(default=...)

    @computed_field
    @cached_property
    def POSTGRES_URL(self) -> str:
        return str(PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            path=self.POSTGRES_DB,
        ))

    # WARNING! Used to clear the database when running the API
    # Used for development
    CLEAR_DB: bool = Field(default=...)


config = Config()