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


class StockUpdate(BaseModel):
    quantity: int = Field(description="Quantity to add (positive) or remove (negative)")
    reason: Optional[str] = Field(default=None, description="Reason for stock update")


class ProductResponse(ProductBase):
    id: UUID

    class Config:
        from_attributes = True
