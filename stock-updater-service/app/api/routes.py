from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.product import StockUpdate, ProductResponse
from app.services.stock_service import StockService

stock_router = APIRouter()


@stock_router.post("/update/{product_id}", response_model=ProductResponse)
def update_stock(
    product_id: UUID,
    stock_update: StockUpdate,
    db: Session = Depends(get_db)
):
    """
    Update product stock by adding or removing quantity
    """
    try:
        updated_product = StockService.update_stock(db, product_id, stock_update)
        return updated_product
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating stock: {str(e)}")
