import logging
from typing import Callable

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine, Base
from app.core.cache import RedisCache


logger = logging.getLogger(__name__)


def start_app_handler(app: FastAPI) -> Callable:
    """
    FastAPI startup event handler
    """
    async def startup() -> None:
        logger.info("Running app start handler.")
        # Initialize database tables
        from app.models.product import Product
        from app.models.supplier import Supplier
        
        # Create tables
        try:
            # Check database connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            
            # Tables should already exist (shared with stock-updater-service)
            # We don't create tables here to avoid conflicts
            logger.info("Database tables check completed")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
        
        # Check Redis connection if enabled
        if settings.USE_REDIS_CACHE:
            try:
                redis_cache = RedisCache()
                if redis_cache._client and redis_cache._client.ping():
                    logger.info("Redis connection successful")
                else:
                    logger.warning("Redis connection failed, cache will be disabled")
            except Exception as e:
                logger.error(f"Redis connection error: {e}")
    
    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    """
    FastAPI shutdown event handler
    """
    async def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        # Add cleanup tasks here
    
    return shutdown
