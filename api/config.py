from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True


class ApiV1Config(BaseModel):
    prefix: str = "/api/v1"
    users_prefix: str = prefix + "/users"
    coins_prefix: str = prefix + "/coins"


class ApiConfig(BaseModel):
    v1: ApiV1Config = ApiV1Config()


class DatabaseConfig(BaseModel):
    url: str | None = None
    echo: bool | None = None
    echo_pool: bool | None = None
    pool_size: int | None = None
    max_overflow: int | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="APP__",
        env_nested_delimiter="__",
    )
    run: RunConfig = RunConfig()
    api: ApiConfig = ApiConfig()
    db: DatabaseConfig = DatabaseConfig()


settings = Settings()
