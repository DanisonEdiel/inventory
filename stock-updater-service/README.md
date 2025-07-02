# Stock Updater Service

This microservice is responsible for updating the stock level of products in the inventory system.

## Features

- Real-time stock level updates
- Publishing stock change events to RabbitMQ
- RESTful API for external integrations
- Data validation and error handling
- Audit logging of stock changes

## Technologies

- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- RabbitMQ
- Docker

## Project Structure

```
stock-updater-service/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   └── stock.py
│   │   └── router.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── events.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │       ├── __init__.py
│   │       └── product.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── product.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── stock_service.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_stock_api.py
│   └── main.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Data Models

### Product

```python
class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    sku = Column(String, unique=True, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### StockLog

```python
class StockLog(Base):
    __tablename__ = "stock_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    change_amount = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Optional, if there is authentication
```

## API Endpoints

### Update Stock

**Endpoint:** `POST /stock/update/{product_id}`

**Description:** Updates the stock level of a specific product.

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

**Description:** Checks the status of the service.

**Successful Response (200 OK):**
```json
{
  "status": "ok"
}
```

## Event System

The service publishes events to RabbitMQ when a product's stock is updated.

### Event: stock-updated

```json
{
  "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "previous_stock": 10,
  "new_stock": 20,
  "change_amount": 10,
  "reason": "Restock from supplier",
  "timestamp": 1625097600
}
```

## Configuration

The service configuration is done through environment variables:

```
# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/inventory

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_EXCHANGE=inventory

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True
```

## Local Execution

### With Docker

```bash
# Build the image
docker build -t stock-updater-service .

# Run the container
docker run -p 8000:8000 --env-file .env stock-updater-service
```

### Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

```bash
# Run unit tests
pytest app/tests/

# Run tests with coverage
pytest --cov=app app/tests/
```

## Integration with Other Services

### Stock Checker Service

The Stock Checker Service listens for `stock-updated` events to keep its stock cache updated.

### Supplier Sync Service

The Supplier Sync Service can send requests to this service to update stock when it receives data from suppliers.

## Error Handling

The service implements robust error handling:

1. **Data Validation**: Uses Pydantic to validate all inputs.
2. **HTTP Errors**: Returns appropriate HTTP status codes with descriptive messages.
3. **Error Logging**: Logs detailed errors to facilitate debugging.
4. **Transactions**: Uses database transactions to ensure data integrity.

## Security Considerations

1. **Input Validation**: All inputs are validated to prevent injections.
2. **Access Control**: Authentication and authorization are recommended for production.
3. **Rate Limiting**: Consider implementing rate limiting to prevent abuse.
4. **Sensitive Data**: No sensitive data is stored in this service.
