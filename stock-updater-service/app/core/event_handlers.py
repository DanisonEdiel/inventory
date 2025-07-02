import json
import logging
from typing import Callable

import pika
from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine, SessionLocal
from app.services.stock_service import StockService


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
            
            # Create tables
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
        
        # Setup RabbitMQ consumer
        try:
            setup_rabbitmq_consumer()
            logger.info("RabbitMQ consumer setup completed")
        except Exception as e:
            logger.error(f"RabbitMQ consumer setup error: {e}")
    
    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    """
    FastAPI shutdown event handler
    """
    async def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        # Add cleanup tasks here
    
    return shutdown


def setup_rabbitmq_consumer():
    """
    Setup RabbitMQ consumer to listen for product events
    """
    # RabbitMQ connection parameters
    credentials = pika.PlainCredentials(
        username=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD
    )
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host=settings.RABBITMQ_VHOST,
        credentials=credentials
    )
    
    # Create connection and channel
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declare exchanges and queues
    channel.exchange_declare(
        exchange='inventory_events',
        exchange_type='topic',
        durable=True
    )
    
    # Product received queue
    channel.queue_declare(queue='product_received_queue', durable=True)
    channel.queue_bind(
        exchange='inventory_events',
        queue='product_received_queue',
        routing_key=settings.PRODUCT_RECEIVED_TOPIC
    )
    
    # Product sold queue
    channel.queue_declare(queue='product_sold_queue', durable=True)
    channel.queue_bind(
        exchange='inventory_events',
        queue='product_sold_queue',
        routing_key=settings.PRODUCT_SOLD_TOPIC
    )
    
    # Set up consumers
    channel.basic_consume(
        queue='product_received_queue',
        on_message_callback=handle_product_received,
        auto_ack=False
    )
    
    channel.basic_consume(
        queue='product_sold_queue',
        on_message_callback=handle_product_sold,
        auto_ack=False
    )
    
    # Start consuming in a separate thread
    import threading
    thread = threading.Thread(target=channel.start_consuming)
    thread.daemon = True
    thread.start()


def handle_product_received(ch, method, properties, body):
    """
    Handle product received event
    """
    try:
        payload = json.loads(body)
        product_id = payload.get('product_id')
        quantity = payload.get('quantity')
        
        if not product_id or not quantity:
            logger.error("Invalid product received event payload")
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return
        
        # Process the event
        db = SessionLocal()
        try:
            StockService.handle_product_received_event(db, product_id, quantity)
            logger.info(f"Product received event processed: {product_id}, quantity: {quantity}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing product received event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error handling product received event: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)


def handle_product_sold(ch, method, properties, body):
    """
    Handle product sold event
    """
    try:
        payload = json.loads(body)
        product_id = payload.get('product_id')
        quantity = payload.get('quantity')
        
        if not product_id or not quantity:
            logger.error("Invalid product sold event payload")
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return
        
        # Process the event
        db = SessionLocal()
        try:
            StockService.handle_product_sold_event(db, product_id, quantity)
            logger.info(f"Product sold event processed: {product_id}, quantity: {quantity}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing product sold event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error handling product sold event: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)


# Import Base here to avoid circular imports
from app.db.database import Base
