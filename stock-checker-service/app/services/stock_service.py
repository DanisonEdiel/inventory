from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.product import Product
from app.schemas.product import StockResponse, StockStatusResponse
from app.core.cache import JsonCache


class StockService:
    @staticmethod
    def get_product_stock(db: Session, product_id: UUID) -> StockResponse:
        """
        Get stock information for a specific product
        """
        # Try to get from cache first if Redis is enabled
        cache = JsonCache[StockResponse](StockResponse, prefix="product_stock")
        cached_stock = cache.get(product_id)
        
        if cached_stock:
            return cached_stock
        
        # If not in cache or cache disabled, get from database
        product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or inactive")
        
        # Create response
        stock_response = StockResponse(
            product_id=product.id,
            name=product.name,
            stock=product.stock,
            is_available=product.stock > 0
        )
        
        # Cache the result
        cache.set(product_id, stock_response)
        
        return stock_response
    
    @staticmethod
    def get_low_stock_products(db: Session, min_stock: int = 10) -> List[StockStatusResponse]:
        """
        Get all products with stock below the specified minimum
        """
        products = db.query(Product).filter(Product.is_active == True).all()
        
        result = []
        for product in products:
            status = "out_of_stock" if product.stock == 0 else "low" if product.stock < min_stock else "ok"
            
            # Only include products that are out of stock or have low stock
            if status != "ok":
                result.append(StockStatusResponse(
                    product_id=product.id,
                    name=product.name,
                    stock=product.stock,
                    status=status
                ))
        
        return result
    
    @staticmethod
    def get_all_stock_status(db: Session, min_stock: Optional[int] = None) -> List[StockStatusResponse]:
        """
        Get stock status for all products, optionally filtering by minimum stock level
        """
        query = db.query(Product).filter(Product.is_active == True)
        
        if min_stock is not None:
            query = query.filter(Product.stock < min_stock)
            
        products = query.all()
        
        result = []
        for product in products:
            status = "out_of_stock" if product.stock == 0 else "low" if product.stock < 10 else "ok"
            result.append(StockStatusResponse(
                product_id=product.id,
                name=product.name,
                stock=product.stock,
                status=status
            ))
        
        return result
