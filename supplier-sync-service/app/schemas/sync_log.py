from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class SyncLogBase(BaseModel):
    supplier_id: UUID
    sync_type: str  # 'scheduled', 'manual'
    status: str  # 'success', 'failed', 'partial'
    started_at: datetime
    completed_at: Optional[datetime] = None
    products_added: int = 0
    products_updated: int = 0
    products_deactivated: int = 0
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SyncLogCreate(SyncLogBase):
    pass


class SyncLogUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    products_added: Optional[int] = None
    products_updated: Optional[int] = None
    products_deactivated: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SyncLogResponse(SyncLogBase):
    id: UUID
    
    class Config:
        from_attributes = True
