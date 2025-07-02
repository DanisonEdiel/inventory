# Inventory Microservices System Architecture

## Overview

The inventory microservices system is designed following the principles of microservices architecture and event-based communication. Each service has a single, well-defined responsibility and communicates with other services primarily through asynchronous events.

## Architecture Diagram

```
                                 ┌─────────────────┐
                                 │                 │
                                 │  API Gateway    │
                                 │                 │
                                 └────────┬────────┘
                                          │
                                          ▼
┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
│                 │           │                 │           │                 │
│  Stock Updater  │◄────────►│   RabbitMQ      │◄────────►│  Supplier Sync  │
│    Service      │           │   (Events)      │           │    Service      │
│                 │           │                 │           │                 │
```

## Components

### Stock Updater Service

**Responsibility**: Manage product stock level updates.

**Main Technologies**:
- Python 3.11
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- RabbitMQ (for event publishing)

**Key Features**:
- Stock level updates
- Inventory transaction logging
- Stock change event publishing
- Input data validation

### Stock Checker Service

**Responsibility**: Provide information about the current inventory status.

**Main Technologies**:
- Python 3.11
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- Redis (for caching)

**Key Features**:
- Query product stock levels
- Identify low stock products
- General inventory status overview
- Caching of frequent queries

### Supplier Sync Service

**Responsibility**: Manage synchronization with supplier systems.

**Main Technologies**:
- Python 3.11
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- RabbitMQ (for event consumption)
- Celery (for asynchronous tasks)

**Key Features**:
- Synchronization with supplier systems
- Product catalog management
- Restock order processing
- Synchronization task scheduling

## Design Patterns

### Event-Based Communication

Microservices communicate with each other primarily through events, using RabbitMQ as a message broker. This approach allows for loose coupling between services and better scalability.

**Event Flow Example**:
1. Stock Updater Service updates a product's stock level
2. Publishes a "stock_updated" event to RabbitMQ
3. Supplier Sync Service consumes the event and checks if reordering is needed

### Redis Caching

The Stock Checker Service uses Redis to cache responses from frequent queries, which significantly improves performance.

**Caching Strategy**:
- Configurable expiration time
- Automatic invalidation when data changes
- JSON serialization/deserialization for complex objects

### Asynchronous Processing with Celery

The Supplier Sync Service uses Celery for asynchronous task processing, such as synchronizing with external supplier systems.

**Benefits**:
- Background processing
- Automatic retries
- Task scheduling
- Horizontal scalability

## Data Flows

### Stock Update

1. Client sends stock update request to Stock Updater Service
2. Stock Updater Service validates the request
3. Updates the PostgreSQL database
4. Publishes "stock_updated" event to RabbitMQ
5. Stock Checker Service invalidates related cache
6. Supplier Sync Service evaluates if reordering is needed

### Stock Query

1. Client sends query request to Stock Checker Service
2. Stock Checker Service checks if the response is in cache
3. If not in cache, queries the PostgreSQL database
4. Stores the result in cache for future queries
5. Returns the response to the client

### Supplier Synchronization

1. Supplier Sync Service schedules synchronization task
2. Celery worker executes the task in the background
3. Connects to the supplier system via API
4. Updates the product catalog in the database
5. Publishes "supplier_catalog_updated" event to RabbitMQ

## Scalability

The architecture is designed to scale horizontally:

- **Microservices**: Each service can scale independently based on its load
- **Database**: PostgreSQL can be configured with read replicas
- **Cache**: Redis can be configured in cluster mode
- **Messaging**: RabbitMQ supports clustering for high availability
- **Asynchronous processing**: Celery workers can be added as needed

## Security

- **Authentication**: JWT for APIs
- **Authorization**: Role-based access control
- **Communication**: TLS for all external communications
- **Sensitive data**: Stored encrypted in the database
- **Secrets**: Managed through environment variables or AWS Secrets Manager

## Monitoring and Logging

- **Centralized logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics**: Prometheus and Grafana
- **Traceability**: OpenTelemetry for distributed tracing
- **Alerts**: Configured for critical events

## Deployment Considerations

- **Containers**: All services are dockerized
- **Orchestration**: Kubernetes or AWS ECS
- **Infrastructure as code**: Terraform
- **CI/CD**: GitHub Actions
- **Environments**: Development, Staging, Production

## Future Evolution

- Implementation of API Gateway
- Centralized authentication service
- Implementation of Circuit Breaker for greater resilience
- Expansion of inventory data analysis capabilities
- Redis can be configured in cluster mode or with replicas
- PostgreSQL database can be scaled vertically or configured with read replicas

## Security Considerations

- Authentication and authorization for APIs (not implemented in this version)
- Secure communication with external APIs
- Secure storage of credentials in environment variables
- AWS security groups to restrict access to resources

## Monitoring and Observability

- Application logs
- CloudWatch for monitoring in AWS
- Health endpoints to verify service status
- Detailed synchronization logs for auditing
