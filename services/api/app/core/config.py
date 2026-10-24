"""Application Configuration for ScamGraph AI API."""

import os
from typing import Any, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "t", "yes", "development", "dev")
        return bool(v)
    PORT: int = 8000
    SECRET_KEY: str = "dev-secret-key-scamgraph-ai"
    DEMO_MODE: bool = False  # Set to True for demonstration/testing without live services

    # PostgreSQL + pgvector
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "scamgraph"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/scamgraph"

    # Neo4j Graph DB
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "scamgraph_password"

    # TinyFish API
    TINYFISH_API_KEY: str = ""
    TINYFISH_BASE_URL: str = "https://api.tinyfish.io/v1"

    # AI / Embeddings
    SCAMGRAPH_EMBEDDING_MODEL: str = os.getenv("SCAMGRAPH_EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    EMBEDDING_MODEL_NAME: str = os.getenv("SCAMGRAPH_EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    DEVICE: str = "cpu"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
