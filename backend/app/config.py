"""Application settings loaded from environment / .env file."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI
    openai_api_key: str
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Crawler
    site_base_url: str = "https://compileit.com"
    crawl_max_pages: int = 100
    crawl_max_depth: int = 2

    # Vector store
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection: str = "compileit"

    # Retrieval
    retrieval_k: int = 5
    retrieval_fetch_k: int = 20

    # CORS
    allowed_origins: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()  # type: ignore[call-arg]
