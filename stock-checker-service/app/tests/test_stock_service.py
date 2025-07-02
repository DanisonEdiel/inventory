import pytest
import uuid
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from app.services.stock_service import StockService
from app.schemas.product import StockResponse, StockStatusResponse


class TestStockService:
    def test_get_product_stock_success(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock product
        mock_product = MagicMock()
        mock_product.id = uuid.uuid4()
        mock_product.name = "Test Product"
        mock_product.stock = 10
        mock_product.is_active = True
        
        # Mock query result
        mock_db.query().filter().first.return_value = mock_product
        
        # Mock cache
        with patch('app.services.stock_service.JsonCache') as mock_cache_class:
            mock_cache = MagicMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            
            # Call the service
            result = StockService.get_product_stock(mock_db, mock_product.id)
            
            # Assertions
            assert result.product_id == mock_product.id
            assert result.name == mock_product.name
            assert result.stock == mock_product.stock
            assert result.is_available == True
            mock_cache.set.assert_called_once()
    
    def test_get_product_stock_from_cache(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock cached response
        cached_response = StockResponse(
            product_id=uuid.uuid4(),
            name="Cached Product",
            stock=5,
            is_available=True
        )
        
        # Mock cache
        with patch('app.services.stock_service.JsonCache') as mock_cache_class:
            mock_cache = MagicMock()
            mock_cache.get.return_value = cached_response
            mock_cache_class.return_value = mock_cache
            
            # Call the service
            result = StockService.get_product_stock(mock_db, cached_response.product_id)
            
            # Assertions
            assert result == cached_response
            mock_db.query.assert_not_called()  # Database should not be queried
            mock_cache.set.assert_not_called()  # Cache should not be updated
    
    def test_get_product_stock_not_found(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock query result - product not found
        mock_db.query().filter().first.return_value = None
        
        # Mock cache
        with patch('app.services.stock_service.JsonCache') as mock_cache_class:
            mock_cache = MagicMock()
            mock_cache.get.return_value = None
            mock_cache_class.return_value = mock_cache
            
            # Call the service and check exception
            with pytest.raises(HTTPException) as excinfo:
                StockService.get_product_stock(mock_db, uuid.uuid4())
            
            # Assertions
            assert excinfo.value.status_code == 404
            assert "Product not found" in str(excinfo.value.detail)
            mock_cache.set.assert_not_called()
    
    def test_get_low_stock_products(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock products
        mock_product1 = MagicMock()
        mock_product1.id = uuid.uuid4()
        mock_product1.name = "Low Stock Product"
        mock_product1.stock = 5
        mock_product1.is_active = True
        
        mock_product2 = MagicMock()
        mock_product2.id = uuid.uuid4()
        mock_product2.name = "Out of Stock Product"
        mock_product2.stock = 0
        mock_product2.is_active = True
        
        mock_product3 = MagicMock()
        mock_product3.id = uuid.uuid4()
        mock_product3.name = "Normal Stock Product"
        mock_product3.stock = 20
        mock_product3.is_active = True
        
        # Mock query result
        mock_db.query().filter().all.return_value = [mock_product1, mock_product2, mock_product3]
        
        # Call the service
        result = StockService.get_low_stock_products(mock_db, min_stock=10)
        
        # Assertions
        assert len(result) == 2  # Only low and out of stock products
        assert any(p.product_id == mock_product1.id and p.status == "low" for p in result)
        assert any(p.product_id == mock_product2.id and p.status == "out_of_stock" for p in result)
        assert not any(p.product_id == mock_product3.id for p in result)
    
    def test_get_all_stock_status(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock products
        mock_product1 = MagicMock()
        mock_product1.id = uuid.uuid4()
        mock_product1.name = "Low Stock Product"
        mock_product1.stock = 5
        mock_product1.is_active = True
        
        mock_product2 = MagicMock()
        mock_product2.id = uuid.uuid4()
        mock_product2.name = "Normal Stock Product"
        mock_product2.stock = 20
        mock_product2.is_active = True
        
        # Mock query result
        mock_db.query().filter().all.return_value = [mock_product1, mock_product2]
        
        # Call the service
        result = StockService.get_all_stock_status(mock_db)
        
        # Assertions
        assert len(result) == 2
        assert any(p.product_id == mock_product1.id and p.status == "low" for p in result)
        assert any(p.product_id == mock_product2.id and p.status == "ok" for p in result)
    
    def test_get_all_stock_status_with_min(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock products
        mock_product1 = MagicMock()
        mock_product1.id = uuid.uuid4()
        mock_product1.name = "Low Stock Product"
        mock_product1.stock = 5
        mock_product1.is_active = True
        
        # Mock query result with filter
        mock_db.query().filter().filter().all.return_value = [mock_product1]
        
        # Call the service
        result = StockService.get_all_stock_status(mock_db, min_stock=10)
        
        # Assertions
        assert len(result) == 1
        assert result[0].product_id == mock_product1.id
        assert result[0].status == "low"
