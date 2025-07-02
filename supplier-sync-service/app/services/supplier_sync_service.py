import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
import pika

from app.models.supplier import Supplier
from app.models.product import Product
from app.models.sync_log import SupplierSyncLog
from app.schemas.supplier import SyncResult
from app.schemas.sync_log import SyncLogCreate, SyncLogUpdate
from app.schemas.product import SupplierProductData
from app.services.supplier_api_client import SupplierApiClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class SupplierSyncService:
    @staticmethod
    async def sync_supplier(db: Session, supplier_id: UUID, force: bool = False) -> SyncResult:
        """
        Synchronize products from a specific supplier
        
        Args:
            db: Database session
            supplier_id: ID of the supplier to sync
            force: Force sync even if recently synced
            
        Returns:
            SyncResult with sync status and statistics
        """
        # Get supplier
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return SyncResult(
                supplier_id=supplier_id,
                status="failed",
                error_message="Supplier not found"
            )
        
        # Check if supplier has API code
        if not supplier.api_code or supplier.api_code not in settings.SUPPLIER_APIS:
            return SyncResult(
                supplier_id=supplier_id,
                status="failed",
                error_message=f"Supplier has no valid API code configured"
            )
        
        # Create sync log entry
        sync_log = SupplierSyncLog(
            supplier_id=supplier_id,
            sync_type="manual",
            status="in_progress",
            started_at=datetime.utcnow()
        )
        db.add(sync_log)
        db.commit()
        db.refresh(sync_log)
        
        try:
            # Initialize API client
            api_client = SupplierApiClient(supplier.api_code)
            
            # Fetch products from supplier API
            supplier_products = await api_client.get_catalog()
            
            # Process products
            products_added = 0
            products_updated = 0
            products_deactivated = 0
            
            # Get existing products for this supplier
            existing_products = {
                p.external_id: p for p in 
                db.query(Product).filter(Product.supplier_id == supplier_id).all()
                if p.external_id  # Only include products with external_id
            }
            
            # Track processed external IDs
            processed_external_ids = set()
            
            # Process each product from supplier
            for product_data in supplier_products:
                external_id = product_data.external_id
                processed_external_ids.add(external_id)
                
                if external_id in existing_products:
                    # Update existing product
                    product = existing_products[external_id]
                    product.name = product_data.name
                    product.stock = product_data.stock
                    product.is_active = True
                    products_updated += 1
                else:
                    # Create new product
                    product = Product(
                        name=product_data.name,
                        stock=product_data.stock,
                        supplier_id=supplier_id,
                        external_id=external_id,
                        is_active=True
                    )
                    db.add(product)
                    products_added += 1
            
            # Deactivate products not in supplier data
            for external_id, product in existing_products.items():
                if external_id not in processed_external_ids and product.is_active:
                    product.is_active = False
                    products_deactivated += 1
            
            # Update supplier sync info
            supplier.last_sync_at = datetime.utcnow().isoformat()
            supplier.sync_metadata = {
                "products_count": len(supplier_products),
                "last_sync_status": "success"
            }
            
            # Update sync log
            sync_log.status = "success"
            sync_log.completed_at = datetime.utcnow()
            sync_log.products_added = products_added
            sync_log.products_updated = products_updated
            sync_log.products_deactivated = products_deactivated
            
            # Commit changes
            db.commit()
            
            # Publish event
            SupplierSyncService._publish_supplier_updated_event(supplier_id)
            
            return SyncResult(
                supplier_id=supplier_id,
                status="success",
                products_added=products_added,
                products_updated=products_updated,
                products_deactivated=products_deactivated,
                sync_log_id=sync_log.id
            )
            
        except Exception as e:
            logger.error(f"Error syncing supplier {supplier_id}: {str(e)}")
            
            # Update sync log with error
            sync_log.status = "failed"
            sync_log.completed_at = datetime.utcnow()
            sync_log.error_message = str(e)
            
            # Update supplier sync info
            supplier.sync_metadata = {
                "last_sync_status": "failed",
                "last_error": str(e)
            }
            
            # Commit changes
            db.commit()
            
            return SyncResult(
                supplier_id=supplier_id,
                status="failed",
                error_message=str(e),
                sync_log_id=sync_log.id
            )
    
    @staticmethod
    async def sync_all_suppliers(db: Session, force: bool = False) -> List[SyncResult]:
        """
        Synchronize products from all suppliers
        
        Args:
            db: Database session
            force: Force sync even if recently synced
            
        Returns:
            List of SyncResults for each supplier
        """
        suppliers = db.query(Supplier).all()
        results = []
        
        for supplier in suppliers:
            result = await SupplierSyncService.sync_supplier(db, supplier.id, force)
            results.append(result)
        
        return results
    
    @staticmethod
    def _publish_supplier_updated_event(supplier_id: UUID) -> None:
        """
        Publish supplier data updated event to RabbitMQ
        
        Args:
            supplier_id: ID of the updated supplier
        """
        try:
            # Connect to RabbitMQ
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
            channel = connection.channel()
            
            # Declare exchange
            channel.exchange_declare(
                exchange="inventory",
                exchange_type="topic",
                durable=True
            )
            
            # Create message
            message = {
                "supplier_id": str(supplier_id),
                "event_type": "supplier_data_updated",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish message
            channel.basic_publish(
                exchange="inventory",
                routing_key=settings.SUPPLIER_DATA_UPDATED_TOPIC,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type="application/json"
                )
            )
            
            # Close connection
            connection.close()
            
        except Exception as e:
            logger.error(f"Error publishing supplier updated event: {str(e)}")
            # Don't raise exception, as this is a non-critical operation
