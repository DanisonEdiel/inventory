# Inventory Microservices System

This project implements an inventory management system based on microservices using Python FastAPI, PostgreSQL, RabbitMQ, Redis, and Docker.

## Architecture

The system is composed of three main microservices:

1. **Stock Updater Service**: Manages inventory updates and processes events related to stock changes.
2. **Stock Checker Service**: Provides endpoints to query the current inventory status with Redis caching.
3. **Supplier Sync Service**: Synchronizes data with external suppliers and keeps product information updated.

![Architecture](docs/architecture.png)

## Technologies

- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL
- **Messaging**: RabbitMQ
- **Cache**: Redis
- **Asynchronous tasks**: Celery
- **Containers**: Docker, Docker Compose
- **Infrastructure**: Terraform, AWS (EC2, RDS)
- **CI/CD**: GitHub Actions

## Project Structure

```
inventory/
├── stock-updater-service/    # Stock update service
├── stock-checker-service/    # Stock query service
├── supplier-sync-service/    # Supplier synchronization service
├── terraform/                # Infrastructure configuration
├── .github/                  # CI/CD workflows
├── docs/                     # Documentation
└── integration_test.py       # Integration tests
```

## Requirements

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 14+
- RabbitMQ 3.9+
- Redis 7+
- Terraform 1.0+ (for deployment)
- AWS CLI (for deployment)

## Local Configuration

### 1. Clone the repository

```bash
git clone https://github.com/your-org/inventory.git
cd inventory
```

### 2. Configure environment variables

Each service has its own `.env` file. Copy the example files and adjust as needed:

```bash
cp stock-updater-service/.env.example stock-updater-service/.env
cp stock-checker-service/.env.example stock-checker-service/.env
cp supplier-sync-service/.env.example supplier-sync-service/.env
```

### 3. Start services with Docker Compose

Each service can be run independently:

```bash
# Stock Updater Service
cd stock-updater-service
docker-compose up -d

# Stock Checker Service
cd stock-checker-service
docker-compose up -d

# Supplier Sync Service
cd supplier-sync-service
docker-compose up -d
```

Or you can start all services together with the main docker-compose:

```bash
docker-compose up -d
```

### 4. Verify services

- Stock Updater Service: http://localhost:8000/docs
- Stock Checker Service: http://localhost:8001/docs
- Supplier Sync Service: http://localhost:8002/docs
- RabbitMQ Management: http://localhost:15672 (guest/guest)
- Redis Commander: http://localhost:8081

## AWS Deployment

### Prerequisites

- AWS account with appropriate permissions
- AWS CLI configured
- Terraform installed
- SSH key pair in AWS

### Deployment Steps

1. Configure Terraform variables:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

2. Initialize and apply the Terraform configuration:

```bash
terraform init
terraform plan
terraform apply
```

3. Verify the deployment:

```bash
terraform output
```

## Testing

### Unit Tests

Each service has its own unit tests:

```bash
cd stock-updater-service
pytest app/tests/

cd stock-checker-service
pytest app/tests/

cd supplier-sync-service
pytest app/tests/
```

### Integration Tests

```bash
python integration_test.py
```

## API Documentation

Each service provides Swagger UI documentation:

- Stock Updater Service: http://localhost:8000/docs
- Stock Checker Service: http://localhost:8001/docs
- Supplier Sync Service: http://localhost:8002/docs

## Event Flow

1. **Product Reception**:
   - A `product-received` event is published to RabbitMQ
   - Stock Updater Service processes the event and updates the inventory

2. **Product Sales**:
   - A `product-sold` event is published to RabbitMQ
   - Stock Updater Service reduces the inventory

3. **Supplier Synchronization**:
   - Supplier Sync Service communicates with external APIs
   - Product data is updated
   - Update events are published

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Your Name - your.email@example.com

Project Link: [https://github.com/your-org/inventory](https://github.com/your-org/inventory)
