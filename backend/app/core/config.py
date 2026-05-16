from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@db:5432/coderunner"
    redis_url: str = "redis://redis:6379"
    secret_key: str = "dev-secret-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    max_execution_time_seconds: int = 10
    max_memory_mb: int = 128
    max_output_bytes: int = 65536

    class Config:
        env_file = ".env"


settings = Settings()