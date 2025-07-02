from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.product import Product
from app.schemas.product import StockUpdate


class StockService:
    @staticmethod
    def update_stock(db: Session, product_id: UUID, stock_update: StockUpdate) -> Product:
        """
        Update product stock by adding or removing quantity
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Calculate new stock level
        new_stock = product.stock + stock_update.quantity
        
        # Ensure stock doesn't go negative
        if new_stock < 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot reduce stock below zero. Current stock: {product.stock}, Requested reduction: {abs(stock_update.quantity)}"
            )
        
        # Update stock
        product.stock = new_stock
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def handle_product_received_event(db: Session, product_id: UUID, quantity: int) -> Product:
        """
        Handle product received event from Purchasing domain
        """
        stock_update = StockUpdate(quantity=quantity, reason="Product received from supplier")
        return StockService.update_stock(db, product_id, stock_update)
    
    @staticmethod
    def handle_product_sold_event(db: Session, product_id: UUID, quantity: int) -> Product:
        """
        Handle product sold event from Orders domain
        """
        stock_update = StockUpdate(quantity=-quantity, reason="Product sold")
        return StockService.update_stock(db, product_id, stock_update)
