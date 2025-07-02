# API Documentation for Inventory Microservices

This document provides a complete reference of all APIs exposed by the inventory microservices.

## Stock Updater Service

Base URL: `http://{host}:8000`

### Update Product Stock

**Endpoint:** `POST /stock/update/{product_id}`

Updates the stock level of a specific product.

**Path Parameters:**
- `product_id` (UUID): Unique product identifier

**Request Body:**
```json
{
  "quantity": 10,        // Quantity to add (positive) or subtract (negative)
  "reason": "string"     // Reason for the update
}
```

**Successful Response (200 OK):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Product Name",
  "stock": 20,
  "supplier_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "active": true
}
```

**Error Responses:**
- `404 Not Found`: Product not found
- `400 Bad Request`: Cannot reduce stock below zero
- `500 Internal Server Error`: Server error

### Check Service Status

**Endpoint:** `GET /health`

Checks the status of the service.

**Successful Response (200 OK):**
```json
{
  "status": "ok"
}
```

## Stock Checker Service

Base URL: `http://{host}:8001`

### Get Product Stock

**Endpoint:** `GET /stock/product/{product_id}`

Gets the current stock level of a specific product.

**Path Parameters:**
- `product_id` (UUID): Unique product identifier

**Successful Response (200 OK):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Product Name",
  "stock": 20,
  "supplier_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "supplier_name": "Supplier Name"
}
```

**Error Responses:**
- `404 Not Found`: Product not found
- `500 Internal Server Error`: Server error

### Get Low Stock Products

**Endpoint:** `GET /stock/low`

Gets a list of products whose stock level is below the specified threshold.

**Query Parameters:**
- `threshold` (integer, optional): Stock threshold (default: 10)

**Successful Response (200 OK):**
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Product Name",
    "stock": 5,
    "supplier_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "supplier_name": "Supplier Name"
  }
]
```

**Error Responses:**
- `500 Internal Server Error`: Server error

### Get General Stock Status

**Endpoint:** `GET /stock/status`

Gets a summary of the stock status of all products.

**Query Parameters:**
- `active_only` (boolean, optional): Filter only active products (default: true)

**Successful Response (200 OK):**
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Product Name",
    "stock": 20,
    "status": "OK",
    "supplier_name": "Supplier Name"
  },
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Another Product",
    "stock": 5,
    "status": "LOW",
    "supplier_name": "Supplier Name"
  }
]
```

**Error Responses:**
- `500 Internal Server Error`: Server error

### Check Service Status

**Endpoint:** `GET /health`

Checks the status of the service.

**Successful Response (200 OK):**
```json
{
  "status": "ok"
}
```

## Supplier Sync Service

Base URL: `http://{host}:8002`

### List Suppliers

**Endpoint:** `GET /suppliers/`

Gets a list of all suppliers.

**Query Parameters:**
- `active_only` (boolean, optional): Filter only active suppliers (default: true)

**Successful Response (200 OK):**
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Supplier Name",
    "contact_email": "contact@supplier.com",
    "api_url": "https://api.supplier.com",
    "api_type": "REST",
    "active": true
  }
]
```

**Error Responses:**
- `500 Internal Server Error`: Server error

### Get Supplier Details

**Endpoint:** `GET /suppliers/{supplier_id}`

Gets details of a specific supplier.

**Path Parameters:**
- `supplier_id` (UUID): Unique supplier identifier

**Successful Response (200 OK):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Supplier Name",
  "contact_email": "contact@supplier.com",
  "api_url": "https://api.supplier.com",
  "api_type": "REST",
  "active": true,
  "products_count": 42,
  "last_sync": "2023-07-01T12:00:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Supplier not found
- `500 Internal Server Error`: Server error

### Start Supplier Synchronization

**Endpoint:** `POST /suppliers/{supplier_id}/sync`

Starts an asynchronous synchronization with a specific supplier.

**Path Parameters:**
- `supplier_id` (UUID): Unique supplier identifier

**Successful Response (202 Accepted):**
```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "started",
  "message": "Sync task started for supplier Supplier Name"
}
```

**Error Responses:**
- `404 Not Found`: Supplier not found
- `400 Bad Request`: Supplier inactive or request error
- `500 Internal Server Error`: Server error

### Start Synchronization of All Suppliers

**Endpoint:** `POST /suppliers/sync/all`

Starts an asynchronous synchronization with all active suppliers.

**Successful Response (202 Accepted):**
```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "started",
  "message": "Sync task started for all active suppliers"
}
```

**Error Responses:**
- `500 Internal Server Error`: Server error

### Get Synchronization Logs

**Endpoint:** `GET /suppliers/{supplier_id}/sync-logs`

Gets the synchronization history for a specific supplier.

**Path Parameters:**
- `supplier_id` (UUID): Unique supplier identifier

**Query Parameters:**
- `limit` (integer, optional): Maximum number of records (default: 10)
- `offset` (integer, optional): Offset for pagination (default: 0)

**Successful Response (200 OK):**
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "supplier_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "start_time": "2023-07-01T12:00:00Z",
    "end_time": "2023-07-01T12:05:30Z",
    "status": "success",
    "products_added": 5,
    "products_updated": 10,
    "products_deactivated": 2,
    "error_message": null
  }
]
```

**Error Responses:**
- `404 Not Found`: Supplier not found
- `500 Internal Server Error`: Server error

### Check Service Status

**Endpoint:** `GET /health`

Checks the status of the service.

**Successful Response (200 OK):**
```json
{
  "status": "ok"
}
```

## Event Formats

### product-received

```json
{
  "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "quantity": 10,
  "supplier_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": 1625097600
}
```

### product-sold

```json
{
  "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "quantity": 5,
  "order_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "timestamp": 1625097600
}
```

### supplier-data-updated

```json
{
  "supplier_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "products_updated": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "3fa85f64-5717-4562-b3fc-2c963f66afa7"
  ],
  "timestamp": 1625097600
}
```
