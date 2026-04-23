from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Automated Threat Hunting with NLP"
    database_url: str = "sqlite:///./threat_hunter.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    spacy_model: str = "en_core_web_sm"
    model_cache_dir: str = "./model_cache"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
