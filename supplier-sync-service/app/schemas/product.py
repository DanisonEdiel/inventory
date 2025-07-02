from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    stock: int = Field(ge=0)
    supplier_id: Optional[UUID] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)
    supplier_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: UUID

    class Config:
        from_attributes = True


class SupplierProductData(BaseModel):
    """Schema for product data received from supplier API"""
    external_id: str
    name: str
    stock: Optional[int] = 0
    price: Optional[float] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None
