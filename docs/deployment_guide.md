# Guía de Despliegue y Operaciones

Esta guía proporciona instrucciones detalladas para desplegar y operar el sistema de microservicios de inventario en diferentes entornos.

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Despliegue Local con Docker Compose](#despliegue-local-con-docker-compose)
3. [Despliegue en AWS con Terraform](#despliegue-en-aws-con-terraform)
4. [Configuración de CI/CD con GitHub Actions](#configuración-de-cicd-con-github-actions)
5. [Monitoreo y Logging](#monitoreo-y-logging)
6. [Backup y Recuperación](#backup-y-recuperación)
7. [Solución de Problemas Comunes](#solución-de-problemas-comunes)

## Requisitos Previos

### Tools

- Docker and Docker Compose
- AWS CLI configured with valid credentials
- Terraform v1.0.0+
- Git
- Python 3.11+

### Credentials

- AWS account with appropriate permissions
- PostgreSQL credentials
- RabbitMQ credentials

## Local Deployment with Docker Compose

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-organization/inventory-microservices.git
cd inventory-microservices
```

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=inventory
POSTGRES_PORT=5432

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672

# Redis
REDIS_PORT=6379

# Services
STOCK_UPDATER_PORT=8000
STOCK_CHECKER_PORT=8001
SUPPLIER_SYNC_PORT=8002
```

### Step 3: Start the Services

```bash
docker-compose up -d
```

This will start all the necessary services:

- PostgreSQL
- RabbitMQ
- Redis
- Stock Updater Service
- Stock Checker Service
- Supplier Sync Service

### Step 4: Verify the Deployment

Verify that all services are running:

```bash
docker-compose ps
```

Check the logs of each service:

```bash
docker-compose logs -f stock-updater-service
docker-compose logs -f stock-checker-service
docker-compose logs -f supplier-sync-service
```

Verify that the services are responding:

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## AWS Deployment with Terraform

### Step 1: Configure Terraform

Navigate to the Terraform directory:

```bash
cd terraform
```

Create a `terraform.tfvars` file with your custom values:

```hcl
aws_region       = "us-east-1"
environment      = "dev"
db_password      = "your-secure-password"
ssh_key_name     = "your-key-pair-name"
```

### Step 2: Initialize Terraform

```bash
terraform init
```

### Step 3: Review the Terraform Plan

```bash
terraform plan
```

### Step 4: Apply the Configuration

```bash
terraform apply
```

Confirm the operation when prompted.

### Step 5: Get Output Information

After Terraform completes the deployment, you will get important information such as URLs and IP addresses:

```bash
terraform output
```

Save this information for future reference.

## CI/CD Configuration with GitHub Actions

### Step 1: Configure Secrets in GitHub

In your GitHub repository, go to Settings > Secrets and add the following secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `POSTGRES_PASSWORD`
- `RABBITMQ_PASSWORD`

### Step 2: Configure Workflows

Create the following workflow files in the `.github/workflows/` directory:

#### CI Workflow (ci.yml)

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov
          pip install -r stock-updater-service/requirements.txt
          pip install -r stock-checker-service/requirements.txt
          pip install -r supplier-sync-service/requirements.txt
      - name: Run tests
        run: |
          pytest stock-updater-service/app/tests/
          pytest stock-checker-service/app/tests/
          pytest supplier-sync-service/app/tests/
```

#### CD Workflow (cd.yml)

```yaml
name: CD

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v1
        with:
          terraform_version: 1.0.0
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
      - name: Terraform Init
        run: cd terraform && terraform init
      - name: Terraform Apply
        run: |
          cd terraform
          terraform apply -auto-approve -var="db_password=${{ secrets.POSTGRES_PASSWORD }}" -var="rabbitmq_password=${{ secrets.RABBITMQ_PASSWORD }}"
```

## Monitoring and Logging

### CloudWatch

Services deployed on AWS are configured to send logs to CloudWatch. To view the logs:

1. Log in to the AWS console
2. Navigate to CloudWatch > Logs > Log Groups
3. Look for log groups with the environment prefix (e.g., `dev-stock-updater`)

### Prometheus and Grafana

For advanced monitoring, you can configure Prometheus and Grafana:

1. Deploy Prometheus and Grafana using the `monitoring/docker-compose.yml` file:

```bash
cd monitoring
docker-compose up -d
```

2. Access Grafana at `http://localhost:3000` (default credentials: admin/admin)
3. Import the predefined dashboards from `monitoring/dashboards/`

## Backup and Recovery

### Database Backup

#### Manual Backup

```bash
pg_dump -h <db_host> -U postgres -d inventory -f backup.sql
```

#### Automated Backup in AWS

RDS instances have daily automated backups configured with a 7-day retention period.

### Database Recovery

#### Manual Recovery

```bash
psql -h <db_host> -U postgres -d inventory -f backup.sql
```

#### Recovery in AWS

1. In the AWS console, navigate to RDS > Instances
2. Select the database instance
3. In Actions, select "Restore to point in time"

## Troubleshooting

### Common Issues

#### Services Not Starting

1. Check Docker logs:
   ```bash
   docker-compose logs -f <service-name>
   ```

2. Check database connectivity:
   ```bash
   docker-compose exec stock-updater-service python -c "import psycopg2; conn = psycopg2.connect(host='postgres', dbname='inventory', user='postgres', password='postgres')"
   ```

3. Check RabbitMQ connectivity:
   ```bash
   docker-compose exec stock-updater-service python -c "import pika; connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))"
   ```

#### Supplier Synchronization Error

1. Check service logs:
   ```bash
   docker-compose logs -f supplier-sync-service
   ```

2. Check Celery task status:
   ```bash
   docker-compose exec supplier-sync-service celery -A app.worker.celery inspect active
   ```

3. Restart the Celery worker:
   ```bash
   docker-compose restart supplier-sync-service-celery
   ```

#### Performance Issues

1. Check resource usage:
   ```bash
   docker stats
   ```

2. Check database performance:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM products WHERE stock < 10;
   ```

3. Check Redis cache status:
   ```bash
   docker-compose exec redis redis-cli info stats
   ```

### Support Contacts

- **Infrastructure Issues**: infrastructure-team@example.com
- **Application Issues**: app-support@example.com
- **Emergencies**: On-call engineer: +1-123-456-7890

### Troubleshooting AWS Deployment Issues

#### Symptoms: Terraform deployment fails.

#### Solutions:

1. Verify AWS permissions
2. Verify that the SSH key pair exists
3. Run `terraform destroy` and then try again
4. Check AWS service limits

### Troubleshooting Docker Compose Issues

#### Symptoms: Services do not start correctly with Docker Compose.

#### Solutions:

1. Check Docker logs:
   ```bash
   docker-compose logs -f <service-name>
   ```

2. Check environment variables in the `.env` file
3. Ensure ports are not in use
4. Rebuild images with `docker-compose build --no-cache`
**Soluciones**:
1. Verifique los logs con `docker-compose logs -f [service]`
2. Verifique las variables de entorno en el archivo `.env`
3. Asegúrese de que los puertos no estén en uso
4. Reconstruya las imágenes con `docker-compose build --no-cache`
