import logging
from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.services.supplier_sync_service import SupplierSyncService
from app.schemas.supplier import SyncResult

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.sync_supplier")
def sync_supplier(supplier_id: str, force: bool = False) -> dict:
    """
    Celery task to sync a specific supplier
    
    Args:
        supplier_id: UUID of supplier to sync
        force: Force sync even if recently synced
        
    Returns:
        Dictionary with sync result
    """
    logger.info(f"Starting sync for supplier {supplier_id}")
    
    try:
        # Create DB session
        db = SessionLocal()
        
        # Run sync
        result = sync_supplier_sync(db, UUID(supplier_id), force)
        
        # Close session
        db.close()
        
        return result.dict()
    except Exception as e:
        logger.error(f"Error in sync_supplier task: {str(e)}")
        return {
            "supplier_id": supplier_id,
            "status": "failed",
            "error_message": str(e)
        }


@celery_app.task(name="app.tasks.sync_all_suppliers")
def sync_all_suppliers(force: bool = False) -> List[dict]:
    """
    Celery task to sync all suppliers
    
    Args:
        force: Force sync even if recently synced
        
    Returns:
        List of dictionaries with sync results
    """
    logger.info("Starting sync for all suppliers")
    
    try:
        # Create DB session
        db = SessionLocal()
        
        # Run sync
        results = sync_all_suppliers_sync(db, force)
        
        # Close session
        db.close()
        
        return [result.dict() for result in results]
    except Exception as e:
        logger.error(f"Error in sync_all_suppliers task: {str(e)}")
        return [{
            "status": "failed",
            "error_message": str(e)
        }]


# Synchronous versions of the sync functions to be used by Celery tasks
def sync_supplier_sync(db: Session, supplier_id: UUID, force: bool = False) -> SyncResult:
    """
    Synchronous version of supplier sync for Celery task
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(SupplierSyncService.sync_supplier(db, supplier_id, force))
    finally:
        loop.close()


def sync_all_suppliers_sync(db: Session, force: bool = False) -> List[SyncResult]:
    """
    Synchronous version of all suppliers sync for Celery task
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(SupplierSyncService.sync_all_suppliers(db, force))
    finally:
        loop.close()
