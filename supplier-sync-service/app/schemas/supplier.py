from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class SupplierBase(BaseModel):
    name: str
    contact_email: EmailStr
    external_id: Optional[str] = None
    api_code: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    external_id: Optional[str] = None
    api_code: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    sync_metadata: Optional[Dict[str, Any]] = None


class SupplierResponse(SupplierBase):
    id: UUID
    last_sync_at: Optional[datetime] = None
    sync_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SyncResult(BaseModel):
    supplier_id: UUID
    status: str = Field(..., description="Status of the sync operation: success, failed, partial")
    products_added: int = 0
    products_updated: int = 0
    products_deactivated: int = 0
    error_message: Optional[str] = None
    sync_log_id: Optional[UUID] = None
    

class SyncRequest(BaseModel):
    supplier_ids: Optional[List[UUID]] = Field(default=None, description="List of supplier IDs to sync. If empty, all suppliers will be synced.")
    force: bool = Field(default=False, description="Force sync even if recently synced")
