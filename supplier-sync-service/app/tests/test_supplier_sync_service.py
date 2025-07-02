import pytest
import uuid
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from fastapi import HTTPException
from app.services.supplier_sync_service import SupplierSyncService
from app.schemas.supplier import SyncResult
from app.schemas.product import SupplierProductData


class TestSupplierSyncService:
    def test_sync_supplier_not_found(self):
        # Mock DB session
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None
        
        # Create test supplier ID
        supplier_id = uuid.uuid4()
        
        # Run test with async handling
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(SupplierSyncService.sync_supplier(mock_db, supplier_id))
        finally:
            loop.close()
        
        # Assertions
        assert result.supplier_id == supplier_id
        assert result.status == "failed"
        assert "Supplier not found" in result.error_message
    
    def test_sync_supplier_no_api_code(self):
        # Mock supplier
        mock_supplier = MagicMock()
        mock_supplier.id = uuid.uuid4()
        mock_supplier.api_code = None
        
        # Mock DB session
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = mock_supplier
        
        # Run test with async handling
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(SupplierSyncService.sync_supplier(mock_db, mock_supplier.id))
        finally:
            loop.close()
        
        # Assertions
        assert result.supplier_id == mock_supplier.id
        assert result.status == "failed"
        assert "no valid API code" in result.error_message
    
    @patch('app.services.supplier_sync_service.SupplierApiClient')
    def test_sync_supplier_success(self, mock_api_client_class):
        # Mock supplier
        supplier_id = uuid.uuid4()
        mock_supplier = MagicMock()
        mock_supplier.id = supplier_id
        mock_supplier.api_code = "supplier1"
        
        # Mock DB session
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = mock_supplier
        
        # Mock existing products
        mock_product1 = MagicMock()
        mock_product1.external_id = "ext1"
        mock_product1.is_active = True
        
        mock_product2 = MagicMock()
        mock_product2.external_id = "ext2"
        mock_product2.is_active = True
        
        mock_db.query().filter().all.return_value = [mock_product1, mock_product2]
        
        # Mock API client
        mock_api_client = AsyncMock()
        mock_api_client_class.return_value = mock_api_client
        
        # Mock supplier products from API
        mock_api_client.get_catalog.return_value = [
            SupplierProductData(external_id="ext1", name="Updated Product", stock=10),
            SupplierProductData(external_id="ext3", name="New Product", stock=5)
        ]
        
        # Mock sync log
        mock_sync_log = MagicMock()
        mock_sync_log.id = uuid.uuid4()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Mock RabbitMQ
        with patch('app.services.supplier_sync_service.pika') as mock_pika:
            # Mock connection and channel
            mock_connection = MagicMock()
            mock_channel = MagicMock()
            mock_pika.BlockingConnection.return_value = mock_connection
            mock_connection.channel.return_value = mock_channel
            
            # Run test with async handling
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(SupplierSyncService.sync_supplier(mock_db, supplier_id))
            finally:
                loop.close()
            
            # Assertions
            assert result.supplier_id == supplier_id
            assert result.status == "success"
            assert result.products_added == 1  # ext3
            assert result.products_updated == 1  # ext1
            assert result.products_deactivated == 1  # ext2
            
            # Verify DB operations
            mock_db.add.assert_called()
            assert mock_db.commit.call_count >= 1
            
            # Verify RabbitMQ publish
            mock_channel.exchange_declare.assert_called_once()
            mock_channel.basic_publish.assert_called_once()
            mock_connection.close.assert_called_once()
    
    @patch('app.services.supplier_sync_service.SupplierApiClient')
    def test_sync_supplier_api_error(self, mock_api_client_class):
        # Mock supplier
        supplier_id = uuid.uuid4()
        mock_supplier = MagicMock()
        mock_supplier.id = supplier_id
        mock_supplier.api_code = "supplier1"
        
        # Mock DB session
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = mock_supplier
        
        # Mock API client with error
        mock_api_client = AsyncMock()
        mock_api_client_class.return_value = mock_api_client
        mock_api_client.get_catalog.side_effect = Exception("API connection error")
        
        # Mock sync log
        mock_sync_log = MagicMock()
        mock_sync_log.id = uuid.uuid4()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Run test with async handling
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(SupplierSyncService.sync_supplier(mock_db, supplier_id))
        finally:
            loop.close()
        
        # Assertions
        assert result.supplier_id == supplier_id
        assert result.status == "failed"
        assert "API connection error" in result.error_message
        
        # Verify DB operations
        mock_db.add.assert_called()
        assert mock_db.commit.call_count >= 1
