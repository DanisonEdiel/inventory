import os
from typing import List, Union, Dict, Any

from pydantic import AnyHttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Supplier Sync Service"
    PROJECT_DESCRIPTION: str = "Service for synchronizing supplier data"
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
    
    # RabbitMQ
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_VHOST: str = os.getenv("RABBITMQ_VHOST", "/")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL", 
        f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
    )
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "rpc://")
    
    # Supplier API endpoints
    SUPPLIER_APIS: Dict[str, Dict[str, Any]] = {
        "supplier1": {
            "name": "ABC Suppliers",
            "base_url": "https://api.abcsuppliers.com/v1",
            "api_key": os.getenv("SUPPLIER1_API_KEY", ""),
            "catalog_endpoint": "/catalog",
            "auth_type": "header",  # header, query, basic
            "auth_header": "X-API-Key",
        },
        "supplier2": {
            "name": "XYZ Distributors",
            "base_url": "https://api.xyzdist.com/v2",
            "api_key": os.getenv("SUPPLIER2_API_KEY", ""),
            "catalog_endpoint": "/products",
            "auth_type": "query",
            "auth_param": "api_key",
        }
    }
    
    # Sync schedule (cron format)
    SYNC_SCHEDULE: str = os.getenv("SYNC_SCHEDULE", "0 0 * * *")  # Default: daily at midnight
    
    # Event topics
    SUPPLIER_DATA_UPDATED_TOPIC: str = "supplier-data-updated"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
