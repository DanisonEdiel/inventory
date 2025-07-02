# Stock Checker Service

This microservice is responsible for providing information about the current inventory status. It offers endpoints to query individual product stock levels, identify low stock products, and get a general overview of the inventory status.

## Features

- Query individual product stock levels
- Identification of low stock products
- General overview of inventory status
- Redis cache to improve performance
- RESTful API for inventory queries

## Technologies

- Python 3.11
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- Pydantic
- Redis (for caching)
- Docker

## Project Structure

```
stock-checker-service/
├── app/
│   ├── api/                # API Endpoints
│   ├── core/               # Configuration and utilities
│   │   └── cache.py        # Redis cache implementation
│   ├── db/                 # Database configuration
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   └── tests/              # Unit tests
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Dependencies
└── .env                    # Environment variables (not in version control)
```

## Data Models

### Product

- `id`: UUID - Unique product identifier
- `name`: String - Product name
- `stock`: Integer - Current inventory quantity
- `supplier_id`: UUID - Reference to supplier
- `active`: Boolean - Product status

### Supplier

- `id`: UUID - Unique supplier identifier
- `name`: String - Supplier name
- `contact_email`: String - Contact email
- `products`: Relationship - Relationship with products

## API Endpoints

### Get Product Stock

```
GET /stock/product/{product_id}
```

Gets the current stock level of a specific product.

**Path Parameters:**
- `product_id`: Product UUID

**Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Product Name",
  "stock": 20,
  "supplier_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "supplier_name": "Supplier Name"
}
```

### Get Low Stock Products

```
GET /stock/low?threshold={threshold}
```

Gets a list of products whose stock level is below the specified threshold.

**Query Parameters:**
- `threshold`: Stock threshold (default: 10)

**Response:**
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

### Get General Stock Status

```
GET /stock/status?active_only={active_only}
```

Gets a summary of the stock status of all products.

**Query Parameters:**
- `active_only`: Filter only active products (default: true)

**Response:**
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

## Cache System

The service uses Redis to cache responses from frequent queries, which significantly improves performance. The cache implementation includes:

- JSON serialization/deserialization for complex objects
- Configurable expiration time
- Automatic cache invalidation when data changes
- Option to disable caching through configuration

## Configuration

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| POSTGRES_SERVER | PostgreSQL host | localhost |
| POSTGRES_USER | PostgreSQL user | postgres |
| POSTGRES_PASSWORD | PostgreSQL password | postgres |
| POSTGRES_DB | PostgreSQL database | inventory |
| POSTGRES_PORT | PostgreSQL port | 5432 |
| USE_REDIS_CACHE | Enable Redis cache | true |
| REDIS_HOST | Redis host | localhost |
| REDIS_PORT | Redis port | 6379 |
| PROJECT_NAME | Project name | Stock Checker Service |
| ALLOWED_ORIGINS | CORS allowed origins | * |

## Local Execution

### With Docker Compose

```bash
docker-compose up -d
```

### Without Docker

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables or `.env` file

3. Run the application:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Testing

```bash
pytest app/tests/
```

## Integration with Other Services

- **Stock Updater Service**: Updates the stock levels that this service queries.
- **Supplier Sync Service**: Provides updated supplier information.

## Error Handling

- 404: Product not found
- 500: Internal server error
- 503: Cache service unavailable
