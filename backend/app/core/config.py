"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "secure-open-source-devops"
    app_env: str = "development"
    app_debug: bool = True

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    postgres_user: str = "devops_user"
    postgres_password: str = "changeme_in_production"
    postgres_db: str = "secure_devops"
    database_url: str = (
        "postgresql+psycopg://devops_user:changeme_in_production@localhost:5432/secure_devops"
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10

    log_level: str = "INFO"
    json_logs: bool = False

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = "changeme_in_production"

    github_token: str = ""
    github_webhook_secret: str = ""

    trivy_timeout: int = 300
    semgrep_timeout: int = 300
    gitleaks_timeout: int = 300

    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
