import logging
import os
import pathlib
from functools import lru_cache

from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")
BASE_DIR = pathlib.Path(__file__).parent.parent


class Settings(BaseSettings):
    env: str = os.environ.get("ENV", "production")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")

    ####################
    # Database info
    ####################
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str


class LocalSettings(Settings):
    class Config:
        env_file = f"{BASE_DIR}/.env.local"


class DevelopmentSettings(Settings):
    class Config:
        env_file = f"{BASE_DIR}/.env.dev"


class ProductionSettings(Settings):
    class Config:
        env_file = f"{BASE_DIR}/.env"


class TestingSettings(Settings):
    class Config:
        env_file = f"{BASE_DIR}/.env.test"


@lru_cache
def get_settings() -> BaseSettings:
    settings_cls_dict = {
        "local": LocalSettings,
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestingSettings,
    }

    env = os.environ.get("ENV", "production")
    settings_cls = settings_cls_dict[env]

    return settings_cls()


settings = get_settings()
