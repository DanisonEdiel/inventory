import logging
from typing import Callable

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine, Base

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
        from app.models.sync_log import SupplierSyncLog
        
        # Check database connection
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            
            # Tables should already exist (shared with other services)
            # We only create the sync_log table which is specific to this service
            SupplierSyncLog.__table__.create(engine, checkfirst=True)
            logger.info("Database tables check completed")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
        
        # Check RabbitMQ connection
        try:
            import pika
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    virtual_host=settings.RABBITMQ_VHOST,
                    credentials=pika.PlainCredentials(
                        settings.RABBITMQ_USER, 
                        settings.RABBITMQ_PASSWORD
                    )
                )
            )
            connection.close()
            logger.info("RabbitMQ connection successful")
        except Exception as e:
            logger.error(f"RabbitMQ connection error: {e}")
    
    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    """
    FastAPI shutdown event handler
    """
    async def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        # Add cleanup tasks here
    
    return shutdown
