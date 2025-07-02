from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class SupplierBase(BaseModel):
    name: str
    contact_email: EmailStr


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class SupplierResponse(SupplierBase):
    id: UUID

    class Config:
        from_attributes = True
