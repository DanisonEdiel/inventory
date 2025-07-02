from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    stock: int = Field(ge=0)
    supplier_id: Optional[UUID] = None
    is_active: bool = True


class ProductResponse(ProductBase):
    id: UUID

    class Config:
        from_attributes = True


class StockResponse(BaseModel):
    product_id: UUID
    name: str
    stock: int
    is_available: bool = Field(description="True if stock > 0")
    
    class Config:
        from_attributes = True


class StockStatusResponse(BaseModel):
    product_id: UUID
    name: str
    stock: int
    status: str = Field(description="Status of stock level: 'low', 'ok', 'out_of_stock'")
    
    class Config:
        from_attributes = True
