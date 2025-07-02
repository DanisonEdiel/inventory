import logging
import httpx
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from app.core.config import settings
from app.schemas.product import SupplierProductData

logger = logging.getLogger(__name__)


class SupplierApiClient:
    """Client for interacting with supplier APIs"""

    def __init__(self, supplier_code: str):
        """
        Initialize supplier API client
        
        Args:
            supplier_code: Code of the supplier in the config
        """
        self.supplier_code = supplier_code
        
        # Get supplier config
        if supplier_code not in settings.SUPPLIER_APIS:
            raise ValueError(f"Supplier code '{supplier_code}' not found in configuration")
        
        self.config = settings.SUPPLIER_APIS[supplier_code]
        self.name = self.config["name"]
        self.base_url = self.config["base_url"]
        self.api_key = self.config["api_key"]
        self.auth_type = self.config["auth_type"]
        
    async def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None) -> Dict[str, Any]:
        """
        Make authenticated request to supplier API
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            method: HTTP method
            params: Query parameters
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        headers = {}
        query_params = params or {}
        
        # Add authentication
        if self.auth_type == "header":
            headers[self.config["auth_header"]] = self.api_key
        elif self.auth_type == "query":
            query_params[self.config["auth_param"]] = self.api_key
        elif self.auth_type == "basic":
            # Basic auth would be handled by the client
            pass
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=query_params,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            raise
    
    async def get_catalog(self, params: Dict = None) -> List[SupplierProductData]:
        """
        Get product catalog from supplier
        
        Args:
            params: Additional query parameters
            
        Returns:
            List of products from supplier
        """
        endpoint = self.config["catalog_endpoint"]
        
        try:
            response = await self._make_request(endpoint, params=params)
            
            # Different suppliers might have different response formats
            # Here we normalize the data to our schema
            products_data = []
            
            # Handle different response formats based on supplier
            if self.supplier_code == "supplier1":
                # ABC Suppliers format
                for item in response.get("products", []):
                    products_data.append(
                        SupplierProductData(
                            external_id=str(item.get("id")),
                            name=item.get("name"),
                            stock=item.get("inventory", 0),
                            price=item.get("price"),
                            description=item.get("description"),
                            metadata={
                                "category": item.get("category"),
                                "sku": item.get("sku"),
                                "last_updated": item.get("updated_at")
                            }
                        )
                    )
            elif self.supplier_code == "supplier2":
                # XYZ Distributors format
                for item in response.get("items", []):
                    products_data.append(
                        SupplierProductData(
                            external_id=str(item.get("product_id")),
                            name=item.get("product_name"),
                            stock=item.get("stock_count", 0),
                            price=item.get("wholesale_price"),
                            description=item.get("product_description"),
                            metadata={
                                "category": item.get("category"),
                                "manufacturer": item.get("manufacturer"),
                                "updated": item.get("last_update")
                            }
                        )
                    )
            else:
                # Generic format - try to map fields
                items = response.get("products", []) or response.get("items", []) or []
                for item in items:
                    products_data.append(
                        SupplierProductData(
                            external_id=str(item.get("id", "")),
                            name=item.get("name", "Unknown Product"),
                            stock=item.get("stock", 0) or item.get("inventory", 0) or 0,
                            price=item.get("price"),
                            description=item.get("description"),
                            metadata=item
                        )
                    )
            
            return products_data
        except Exception as e:
            logger.error(f"Error fetching catalog from {self.name}: {str(e)}")
            raise
