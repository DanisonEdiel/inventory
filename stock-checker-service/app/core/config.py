import os
from typing import List, Union, Optional

from pydantic import AnyHttpUrl, PostgresDsn, validator, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Stock Checker Service"
    PROJECT_DESCRIPTION: str = "Service for checking product stock levels"
    PROJECT_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # PostgreSQL
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "inventory")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URI: Union[PostgresDsn, str] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Union[str, None], values: dict) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Redis (optional)
    USE_REDIS_CACHE: bool = os.getenv("USE_REDIS_CACHE", "False").lower() == "true"
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_URI: Optional[RedisDsn] = None
    REDIS_CACHE_EXPIRY: int = int(os.getenv("REDIS_CACHE_EXPIRY", "3600"))  # 1 hour default
    
    @validator("REDIS_URI", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: dict) -> Optional[str]:
        if isinstance(v, str):
            return v
        if not values.get("USE_REDIS_CACHE"):
            return None
        
        password_part = f":{values.get('REDIS_PASSWORD')}@" if values.get("REDIS_PASSWORD") else ""
        return f"redis://{password_part}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
