from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.product import StockResponse, StockStatusResponse
from app.services.stock_service import StockService

stock_router = APIRouter()


@stock_router.get("/{product_id}", response_model=StockResponse)
def get_product_stock(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get stock information for a specific product
    """
    try:
        return StockService.get_product_stock(db, product_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stock: {str(e)}")


@stock_router.get("", response_model=List[StockStatusResponse])
def get_stock_status(
    min: Optional[int] = Query(None, description="Minimum stock level to filter by"),
    db: Session = Depends(get_db)
):
    """
    Get stock status for all products, optionally filtering by minimum stock level
    """
    try:
        return StockService.get_all_stock_status(db, min)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stock status: {str(e)}")


@stock_router.get("/low", response_model=List[StockStatusResponse])
def get_low_stock_products(
    min: int = Query(10, description="Minimum stock threshold"),
    db: Session = Depends(get_db)
):
    """
    Get all products with stock below the specified minimum
    """
    try:
        return StockService.get_low_stock_products(db, min)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving low stock products: {str(e)}")
