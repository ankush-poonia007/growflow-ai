"""
GrowFlow Backend — Typed Centralized Configuration.

Single source of truth for all application settings.
Loaded once at startup; injected throughout via FastAPI Dependency Injection.
Application code must never read os.environ directly.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


_SHARED_ENV_CONFIG = SettingsConfigDict(
    env_file=(".env", "../.env"),
    env_file_encoding="utf-8",
    populate_by_name=True,
    extra="ignore",
)


class AppSettings(BaseSettings):
    """Core application runtime settings."""

    ENV: Environment = Field(default=Environment.DEVELOPMENT, alias="APP_ENV")
    NAME: str = Field(default="GrowFlow", alias="APP_NAME")
    HOST: str = Field(default="127.0.0.1", alias="APP_HOST")
    PORT: int = Field(default=8000, alias="APP_PORT")
    LOG_LEVEL: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    CORS_ORIGINS: list[str] | str = Field(
        default=["http://localhost:3000"],
        alias="APP_CORS_ORIGINS",
    )
    SECRET_KEY: str = Field(alias="APP_SECRET_KEY")
    DEBUG: bool = Field(default=False, alias="DEBUG")
    TESTING: bool = Field(default=False, alias="TESTING")

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = _SHARED_ENV_CONFIG


class DatabaseSettings(BaseSettings):
    """Hosted Supabase / PostgreSQL settings (Gate 03 persistence)."""

    DATABASE_URL: str | None = Field(default=None, alias="DATABASE_URL")
    SUPABASE_URL: str | None = Field(default=None, alias="SUPABASE_URL")
    SUPABASE_PUBLISHABLE_KEY: str | None = Field(default=None, alias="SUPABASE_PUBLISHABLE_KEY")
    SUPABASE_SECRET_KEY: str | None = Field(default=None, alias="SUPABASE_SECRET_KEY")

    POOL_SIZE: int = Field(default=5, alias="DB_POOL_SIZE")
    MAX_OVERFLOW: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    POOL_TIMEOUT_SECONDS: int = Field(default=30, alias="DB_POOL_TIMEOUT_SECONDS")
    POOL_RECYCLE_SECONDS: int = Field(default=1800, alias="DB_POOL_RECYCLE_SECONDS")

    model_config = _SHARED_ENV_CONFIG


class SupabaseAuthSettings(BaseSettings):
    """Supabase Auth & JWT settings (Gate 04 security)."""

    JWT_ISSUER: str | None = Field(default=None, alias="SUPABASE_JWT_ISSUER")
    JWT_AUDIENCE: str = Field(default="authenticated", alias="SUPABASE_JWT_AUDIENCE")
    JWT_SECRET: str | None = Field(default=None, alias="SUPABASE_JWT_SECRET")
    STORAGE_BUCKET: str = Field(default="growflow-documents", alias="SUPABASE_STORAGE_BUCKET")

    model_config = _SHARED_ENV_CONFIG


class AISettings(BaseSettings):
    """
    AI provider and model configuration.

    Supports exactly five OpenRouter provider keys for health-aware rotation (Gate 09+).
    Keys 2-5 are optional; all calls are deferred until Gate 09.
    """

    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        alias="OPENROUTER_BASE_URL",
    )
    OPENROUTER_HTTP_REFERER: str = Field(
        default="https://growflow.app",
        alias="OPENROUTER_HTTP_REFERER",
    )
    OPENROUTER_X_TITLE: str = Field(default="GrowFlow", alias="OPENROUTER_X_TITLE")

    OPENROUTER_API_KEY_1: str | None = Field(default=None, alias="OPENROUTER_API_KEY_1")
    OPENROUTER_API_KEY_2: str | None = Field(default=None, alias="OPENROUTER_API_KEY_2")
    OPENROUTER_API_KEY_3: str | None = Field(default=None, alias="OPENROUTER_API_KEY_3")
    OPENROUTER_API_KEY_4: str | None = Field(default=None, alias="OPENROUTER_API_KEY_4")
    OPENROUTER_API_KEY_5: str | None = Field(default=None, alias="OPENROUTER_API_KEY_5")

    FAST_MODEL: str = Field(default="openai/gpt-4o-mini", alias="AI_FAST_MODEL")
    STANDARD_MODEL: str = Field(default="openai/gpt-4o", alias="AI_STANDARD_MODEL")
    REASONING_MODEL: str = Field(default="openai/o1", alias="AI_REASONING_MODEL")
    EMBEDDING_MODEL: str = Field(
        default="openai/text-embedding-3-small", alias="AI_EMBEDDING_MODEL"
    )
    DEFAULT_MODEL: str = Field(default="openai/gpt-4o", alias="AI_DEFAULT_MODEL")
    FALLBACK_MODEL: str = Field(default="openai/gpt-4o-mini", alias="AI_FALLBACK_MODEL")
    REQUEST_TIMEOUT_SECONDS: int = Field(default=60, alias="AI_REQUEST_TIMEOUT_SECONDS")
    MAX_RETRIES: int = Field(default=3, alias="AI_MAX_RETRIES")
    RETRY_INITIAL_DELAY_SECONDS: int = Field(default=1, alias="AI_RETRY_INITIAL_DELAY_SECONDS")
    RETRY_MAX_DELAY_SECONDS: int = Field(default=8, alias="AI_RETRY_MAX_DELAY_SECONDS")

    @property
    def active_keys(self) -> list[str]:
        """Return non-empty configured provider keys."""
        return [
            k
            for k in [
                self.OPENROUTER_API_KEY_1,
                self.OPENROUTER_API_KEY_2,
                self.OPENROUTER_API_KEY_3,
                self.OPENROUTER_API_KEY_4,
                self.OPENROUTER_API_KEY_5,
            ]
            if k and not k.startswith("your-")
        ]

    model_config = _SHARED_ENV_CONFIG


class TavilySettings(BaseSettings):
    """Tavily web research settings (deferred integration)."""

    API_KEY: str | None = Field(default=None, alias="TAVILY_API_KEY")
    MAX_RESULTS: int = Field(default=5, alias="TAVILY_MAX_RESULTS")
    SEARCH_DEPTH: str = Field(default="basic", alias="TAVILY_SEARCH_DEPTH")

    model_config = _SHARED_ENV_CONFIG


class LangSmithSettings(BaseSettings):
    """LangSmith AI tracing/evaluation settings (deferred integration)."""

    TRACING_V2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    API_KEY: str | None = Field(default=None, alias="LANGCHAIN_API_KEY")
    PROJECT: str = Field(default="growflow-local", alias="LANGCHAIN_PROJECT")
    ENDPOINT: str = Field(default="https://api.smith.langchain.com", alias="LANGCHAIN_ENDPOINT")

    model_config = _SHARED_ENV_CONFIG


class GitHubSettings(BaseSettings):
    """GitHub OAuth and repository activity settings (deferred integration)."""

    CLIENT_ID: str | None = Field(default=None, alias="GITHUB_CLIENT_ID")
    CLIENT_SECRET: str | None = Field(default=None, alias="GITHUB_CLIENT_SECRET")
    REDIRECT_URI: str | None = Field(default=None, alias="GITHUB_OAUTH_REDIRECT_URI")
    WEBHOOK_SECRET: str | None = Field(default=None, alias="GITHUB_WEBHOOK_SECRET")

    model_config = _SHARED_ENV_CONFIG


class EmailSettings(BaseSettings):
    """Email provider settings (deferred integration)."""

    PROVIDER: str | None = Field(default=None, alias="EMAIL_PROVIDER")
    FROM_ADDRESS: str = Field(default="noreply@example.com", alias="EMAIL_FROM")
    API_KEY: str | None = Field(default=None, alias="EMAIL_API_KEY")

    model_config = _SHARED_ENV_CONFIG


class RAGSettings(BaseSettings):
    """RAG & document intelligence settings (deferred integration)."""

    ENABLED: bool = Field(default=True, alias="RAG_ENABLED")
    TOP_K: int = Field(default=8, alias="RAG_TOP_K")
    CHUNK_SIZE: int = Field(default=1000, alias="RAG_CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=150, alias="RAG_CHUNK_OVERLAP")
    INDEX_GENERATED_DOCUMENTS: bool = Field(default=True, alias="RAG_INDEX_GENERATED_DOCUMENTS")

    model_config = _SHARED_ENV_CONFIG


class FileSettings(BaseSettings):
    """Document upload & storage limit settings."""

    MAX_UPLOAD_SIZE_MB: int = Field(default=25, alias="MAX_UPLOAD_SIZE_MB")
    MAX_ARCHIVE_SIZE_MB: int = Field(default=50, alias="MAX_ARCHIVE_SIZE_MB")

    model_config = _SHARED_ENV_CONFIG


class ObservabilitySettings(BaseSettings):
    """OpenTelemetry observability settings."""

    SERVICE_NAME: str = Field(default="growflow-api", alias="OTEL_SERVICE_NAME")
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = Field(
        default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    OTEL_ENABLED: bool = Field(default=False, alias="OTEL_ENABLED")

    model_config = _SHARED_ENV_CONFIG


class WorkerSettings(BaseSettings):
    """Background worker settings."""

    ENABLED: bool = Field(default=False, alias="WORKER_ENABLED")
    CONCURRENCY: int = Field(default=1, alias="WORKER_CONCURRENCY")
    MAX_RETRIES: int = Field(default=3, alias="WORKER_MAX_RETRIES")

    model_config = _SHARED_ENV_CONFIG


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration."""

    ENABLED: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    REQUESTS_PER_MINUTE: int = Field(default=60, alias="RATE_LIMIT_REQUESTS_PER_MINUTE")

    model_config = _SHARED_ENV_CONFIG


class SecuritySettings(BaseSettings):
    """Security and cookie policies."""

    SECURE_COOKIES: bool = Field(default=False, alias="SECURE_COOKIES")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    CSRF_PROTECTION_ENABLED: bool = Field(default=True, alias="CSRF_PROTECTION_ENABLED")

    model_config = _SHARED_ENV_CONFIG


class Settings(BaseSettings):
    """
    Root settings container composing all configuration groups.

    Inject via FastAPI DI:
        def my_route(settings: Annotated[Settings, Depends(get_settings)]):
            ...

    Never read os.environ directly in application logic.
    """

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    auth: SupabaseAuthSettings = Field(default_factory=SupabaseAuthSettings)
    ai: AISettings = Field(default_factory=AISettings)
    tavily: TavilySettings = Field(default_factory=TavilySettings)
    langsmith: LangSmithSettings = Field(default_factory=LangSmithSettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    files: FileSettings = Field(default_factory=FileSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    workers: WorkerSettings = Field(default_factory=WorkerSettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    model_config = _SHARED_ENV_CONFIG

    def __repr__(self) -> str:
        return f"<Settings env={self.app.ENV.value} app_name={self.app.NAME}>"

    def safe_dict(self) -> dict[str, Any]:
        """Return configuration dictionary with all secrets and credentials redacted."""
        return {
            "app": {
                "env": self.app.ENV.value,
                "name": self.app.NAME,
                "host": self.app.HOST,
                "port": self.app.PORT,
                "log_level": self.app.LOG_LEVEL,
                "cors_origins": self.app.CORS_ORIGINS,
                "debug": self.app.DEBUG,
                "testing": self.app.TESTING,
            },
            "database": {
                "pool_size": self.database.POOL_SIZE,
                "max_overflow": self.database.MAX_OVERFLOW,
                "configured": bool(self.database.DATABASE_URL),
            },
            "auth": {
                "jwt_audience": self.auth.JWT_AUDIENCE,
                "storage_bucket": self.auth.STORAGE_BUCKET,
                "configured": bool(self.auth.JWT_SECRET),
            },
            "ai": {
                "base_url": self.ai.OPENROUTER_BASE_URL,
                "fast_model": self.ai.FAST_MODEL,
                "standard_model": self.ai.STANDARD_MODEL,
                "configured_keys_count": len(self.ai.active_keys),
            },
            "observability": {
                "service_name": self.observability.SERVICE_NAME,
                "otel_enabled": self.observability.OTEL_ENABLED,
            },
            "workers": {
                "enabled": self.workers.ENABLED,
                "concurrency": self.workers.CONCURRENCY,
            },
            "rate_limit": {
                "enabled": self.rate_limit.ENABLED,
                "requests_per_minute": self.rate_limit.REQUESTS_PER_MINUTE,
            },
            "security": {
                "secure_cookies": self.security.SECURE_COOKIES,
                "cors_allow_credentials": self.security.CORS_ALLOW_CREDENTIALS,
                "csrf_protection_enabled": self.security.CSRF_PROTECTION_ENABLED,
            },
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached application settings singleton.

    Fails closed on missing or invalid configuration.
    Can be cleared in tests via `get_settings.cache_clear()`.
    """
    return Settings()
