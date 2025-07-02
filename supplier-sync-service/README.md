# Supplier Sync Service

This microservice is responsible for synchronizing product data with external supplier systems. It manages communication with multiple supplier APIs, maintains a record of synchronizations, and publishes events when product data changes.

## Features

- Synchronization with multiple supplier APIs
- Scheduling of periodic synchronizations with Celery
- Detailed logging of synchronization activities
- Publishing events when product data changes
- RESTful API for managing suppliers and synchronizations

## Technologies

- Python 3.11
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- Pydantic
- Celery (for asynchronous and scheduled tasks)
- RabbitMQ (for messaging)
- HTTPX (for asynchronous HTTP communication)
- Docker

## Project Structure

```
supplier-sync-service/
├── app/
│   ├── api/                # API Endpoints
│   ├── celery_app.py       # Celery configuration
│   ├── clients/            # Clients for external APIs
│   ├── core/               # Configuration and utilities
│   ├── db/                 # Database configuration
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── tasks/              # Celery tasks
│   └── tests/              # Unit tests
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Dependencies
└── .env                    # Environment variables (not in version control)
```

## Data Models

### Supplier

- `id`: UUID - Unique supplier identifier
- `name`: String - Supplier name
- `contact_email`: String - Contact email
- `api_key`: String - API key for authentication
- `api_url`: String - Base URL of the supplier's API
- `api_type`: String - API type (REST, SOAP, etc.)
- `active`: Boolean - Supplier status
- `products`: Relationship - Relationship with products

### Product

- `id`: UUID - Unique product identifier
- `name`: String - Product name
- `stock`: Integer - Current inventory quantity
- `supplier_id`: UUID - Reference to supplier
- `external_id`: String - Product ID in the supplier's system
- `active`: Boolean - Product status

### SupplierSyncLog

- `id`: UUID - Unique log identifier
- `supplier_id`: UUID - Reference to supplier
- `start_time`: DateTime - Synchronization start time
- `end_time`: DateTime - Synchronization end time
- `status`: String - Synchronization status (success, error)
- `products_added`: Integer - Number of products added
- `products_updated`: Integer - Number of products updated
- `products_deactivated`: Integer - Number of products deactivated
- `error_message`: String - Error message (if any)

## API Endpoints

### List Suppliers

```
GET /suppliers/
```

Gets a list of all suppliers.

**Response:**
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

### Get Supplier Details

```
GET /suppliers/{supplier_id}
```

Gets details of a specific supplier.

**Path Parameters:**
- `supplier_id`: Supplier UUID

**Response:**
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

### Start Supplier Synchronization

```
POST /suppliers/{supplier_id}/sync
```

Starts an asynchronous synchronization with a specific supplier.

**Path Parameters:**
- `supplier_id`: Supplier UUID

**Response:**
```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "started",
  "message": "Sync task started for supplier Supplier Name"
}
```

### Start Synchronization of All Suppliers

```
POST /suppliers/sync/all
```

Starts an asynchronous synchronization with all active suppliers.

**Response:**
```json
{
  "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "started",
  "message": "Sync task started for all active suppliers"
}
```

### Get Synchronization Logs

```
GET /suppliers/{supplier_id}/sync-logs
```

Gets the synchronization history for a specific supplier.

**Path Parameters:**
- `supplier_id`: Supplier UUID

**Query Parameters:**
- `limit`: Maximum number of records (default: 10)
- `offset`: Offset for pagination (default: 0)

**Response:**
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

## Celery Tasks

The service uses Celery to execute synchronization tasks asynchronously and on schedule:

### Asynchronous Tasks

- `sync_supplier`: Synchronizes data from a specific supplier
- `sync_all_suppliers`: Synchronizes data from all active suppliers

### Scheduled Tasks (Celery Beat)

- Daily synchronization of all active suppliers (configurable via `SYNC_SCHEDULE`)

## Published Events

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

## Configuration

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| POSTGRES_SERVER | PostgreSQL host | localhost |
| POSTGRES_USER | PostgreSQL user | postgres |
| POSTGRES_PASSWORD | PostgreSQL password | postgres |
| POSTGRES_DB | PostgreSQL database | inventory |
| POSTGRES_PORT | PostgreSQL port | 5432 |
| RABBITMQ_HOST | RabbitMQ host | localhost |
| RABBITMQ_PORT | RabbitMQ port | 5672 |
| RABBITMQ_USER | RabbitMQ user | guest |
| RABBITMQ_PASSWORD | RabbitMQ password | guest |
| RABBITMQ_VHOST | RabbitMQ VHost | / |
| CELERY_BROKER_URL | Celery broker URL | amqp://guest:guest@localhost:5672/ |
| CELERY_RESULT_BACKEND | Celery results backend | rpc:// |
| SYNC_SCHEDULE | Synchronization schedule (cron format) | 0 0 * * * |
| PROJECT_NAME | Project name | Supplier Sync Service |
| ALLOWED_ORIGINS | Allowed origins for CORS | * |

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

3. Run the application, Celery worker, and Celery Beat:

```bash
# Terminal 1: FastAPI app
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 2: Celery worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Celery beat
celery -A app.celery_app beat --loglevel=info
```

## Testing

```bash
pytest app/tests/
```

## Integration with Other Services

- **Stock Updater Service**: Receives product update events.
- **Stock Checker Service**: Uses product data updated by this service.

## Error Handling

- 404: Supplier not found
- 400: Invalid request
- 500: Internal server error
- 503: Communication error with supplier API
