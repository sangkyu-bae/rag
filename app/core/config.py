"""Application settings and configuration."""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings   # ✅ 최신 버전용
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    PROJECT_NAME: str = Field(default="FastAPI Boilerplate")
    VERSION: str = Field(default="0.1.0")             # ✅ 따옴표 닫힘 확인!
    API_V1_STR: str = Field(default="/api/v1")
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    
    # LlamaParse 설정
    LLAMA_PARSE_API_KEY: str = Field(default="", description="LlamaParse API 키")
    
    # OpenAI 설정
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API 키")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="OpenAI 모델명")

    model_config = {                                  # ✅ Pydantic v2 문법
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()
