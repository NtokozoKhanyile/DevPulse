from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    # Database
    database_url: str
    database_url_sync: str
    test_database_url: str = ""  # For pytest — defaults to empty, override in .env

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    secret_key: str  
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: List[str] = ["http://localhost:5173"]

    # S3 / Storage
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = "devpulse-assets"
    aws_region: str = "us-east-1"

    # Environment
    environment: str = "development"
    debug: bool = False

    model_config = {
    "env_file": str(Path(__file__).resolve().parent.parent.parent.parent / ".env"),
    "env_file_encoding": "utf-8",
    "extra": "ignore"
    }


# Debug: Check if .env file exists
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")
if env_path.exists():
    print(f"File size: {env_path.stat().st_size} bytes")

settings = Settings()