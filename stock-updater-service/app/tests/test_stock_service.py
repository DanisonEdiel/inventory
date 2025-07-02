import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.services.stock_service import StockService
from app.schemas.product import StockUpdate


class TestStockService:
    def test_update_stock_success(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock product
        mock_product = MagicMock()
        mock_product.id = uuid.uuid4()
        mock_product.stock = 10
        
        # Mock query result
        mock_db.query().filter().first.return_value = mock_product
        
        # Test data
        product_id = mock_product.id
        stock_update = StockUpdate(quantity=5, reason="Test update")
        
        # Call the service
        result = StockService.update_stock(mock_db, product_id, stock_update)
        
        # Assertions
        assert result == mock_product
        assert mock_product.stock == 15
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_product)
    
    def test_update_stock_negative_quantity(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock product
        mock_product = MagicMock()
        mock_product.id = uuid.uuid4()
        mock_product.stock = 10
        
        # Mock query result
        mock_db.query().filter().first.return_value = mock_product
        
        # Test data
        product_id = mock_product.id
        stock_update = StockUpdate(quantity=-5, reason="Test reduction")
        
        # Call the service
        result = StockService.update_stock(mock_db, product_id, stock_update)
        
        # Assertions
        assert result == mock_product
        assert mock_product.stock == 5
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_product)
    
    def test_update_stock_product_not_found(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock query result - product not found
        mock_db.query().filter().first.return_value = None
        
        # Test data
        product_id = uuid.uuid4()
        stock_update = StockUpdate(quantity=5, reason="Test update")
        
        # Call the service and check exception
        with pytest.raises(HTTPException) as excinfo:
            StockService.update_stock(mock_db, product_id, stock_update)
        
        # Assertions
        assert excinfo.value.status_code == 404
        assert "Product not found" in str(excinfo.value.detail)
        mock_db.commit.assert_not_called()
    
    def test_update_stock_negative_result(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock product
        mock_product = MagicMock()
        mock_product.id = uuid.uuid4()
        mock_product.stock = 10
        
        # Mock query result
        mock_db.query().filter().first.return_value = mock_product
        
        # Test data
        product_id = mock_product.id
        stock_update = StockUpdate(quantity=-15, reason="Test excessive reduction")
        
        # Call the service and check exception
        with pytest.raises(HTTPException) as excinfo:
            StockService.update_stock(mock_db, product_id, stock_update)
        
        # Assertions
        assert excinfo.value.status_code == 400
        assert "Cannot reduce stock below zero" in str(excinfo.value.detail)
        mock_db.commit.assert_not_called()
    
    def test_handle_product_received_event(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock product
        mock_product = MagicMock()
        mock_product.id = uuid.uuid4()
        mock_product.stock = 10
        
        # Mock update_stock method
        with patch.object(StockService, 'update_stock', return_value=mock_product) as mock_update:
            # Test data
            product_id = mock_product.id
            quantity = 5
            
            # Call the service
            result = StockService.handle_product_received_event(mock_db, product_id, quantity)
            
            # Assertions
            assert result == mock_product
            mock_update.assert_called_once()
            # Check that StockUpdate was created with positive quantity
            stock_update = mock_update.call_args[0][2]
            assert stock_update.quantity == 5
            assert "Product received" in stock_update.reason
    
    def test_handle_product_sold_event(self):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock product
        mock_product = MagicMock()
        mock_product.id = uuid.uuid4()
        mock_product.stock = 10
        
        # Mock update_stock method
        with patch.object(StockService, 'update_stock', return_value=mock_product) as mock_update:
            # Test data
            product_id = mock_product.id
            quantity = 5
            
            # Call the service
            result = StockService.handle_product_sold_event(mock_db, product_id, quantity)
            
            # Assertions
            assert result == mock_product
            mock_update.assert_called_once()
            # Check that StockUpdate was created with negative quantity
            stock_update = mock_update.call_args[0][2]
            assert stock_update.quantity == -5
            assert "Product sold" in stock_update.reason
