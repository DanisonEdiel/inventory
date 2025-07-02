from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.supplier_sync_service import SupplierSyncService
from app.schemas.supplier import SupplierResponse, SyncResult, SyncRequest
from app.schemas.sync_log import SyncLogResponse
from app.models.supplier import Supplier
from app.models.sync_log import SupplierSyncLog
from app.tasks import sync_supplier as celery_sync_supplier

supplier_router = APIRouter()


@supplier_router.get("", response_model=List[SupplierResponse])
async def get_suppliers(db: Session = Depends(get_db)):
    """
    Get all suppliers
    """
    suppliers = db.query(Supplier).all()
    return suppliers


@supplier_router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific supplier by ID
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@supplier_router.post("/sync", response_model=List[SyncResult])
async def sync_suppliers(
    sync_request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger synchronization of supplier data
    """
    if sync_request.supplier_ids:
        # Verify all supplier IDs exist
        for supplier_id in sync_request.supplier_ids:
            supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if not supplier:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Supplier with ID {supplier_id} not found"
                )
        
        # Queue sync tasks for each supplier
        results = []
        for supplier_id in sync_request.supplier_ids:
            # Queue task in Celery
            celery_sync_supplier.delay(str(supplier_id), sync_request.force)
            
            # Return immediate response
            results.append(SyncResult(
                supplier_id=supplier_id,
                status="queued"
            ))
        
        return results
    else:
        # Queue sync task for all suppliers
        celery_sync_supplier.delay("all", sync_request.force)
        
        # Return immediate response
        suppliers = db.query(Supplier).all()
        return [
            SyncResult(supplier_id=supplier.id, status="queued")
            for supplier in suppliers
        ]


@supplier_router.post("/{supplier_id}/sync", response_model=SyncResult)
async def sync_supplier(
    supplier_id: UUID,
    force: bool = False,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger synchronization for a specific supplier
    """
    # Verify supplier exists
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Queue sync task in Celery
    celery_sync_supplier.delay(str(supplier_id), force)
    
    # Return immediate response
    return SyncResult(
        supplier_id=supplier_id,
        status="queued"
    )


@supplier_router.get("/{supplier_id}/sync-logs", response_model=List[SyncLogResponse])
async def get_supplier_sync_logs(
    supplier_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get sync logs for a specific supplier
    """
    # Verify supplier exists
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Get sync logs
    logs = db.query(SupplierSyncLog)\
        .filter(SupplierSyncLog.supplier_id == supplier_id)\
        .order_by(SupplierSyncLog.started_at.desc())\
        .limit(limit)\
        .all()
    
    return logs
