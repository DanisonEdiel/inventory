# Terraform Infrastructure for Inventory Microservices

This directory contains the Terraform configuration to deploy the necessary infrastructure for inventory microservices in AWS.

## Infrastructure Components

The deployed infrastructure includes:

- **VPC** with public and private subnets
- **Internet Gateway** for Internet access
- **Route tables** for public and private subnets
- **Security groups** for EC2, RDS, and RabbitMQ
- **RDS PostgreSQL instance** for the shared database
- **EC2 instances** for each microservice:
  - Stock Updater Service
  - Stock Checker Service
  - Supplier Sync Service
- **EC2 instance** for RabbitMQ
- **Elastic IPs** for all EC2 instances

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) v1.0.0+
- [AWS CLI](https://aws.amazon.com/cli/) configured with valid credentials
- SSH key pair in AWS for EC2 instance access

## File Structure

```
terraform/
├── main.tf              # Main Terraform configuration
├── variables.tf         # Variable definitions
├── outputs.tf           # Output definitions
├── terraform.tfvars     # Variable values (not included in version control)
└── scripts/             # Initialization scripts for EC2 instances
    ├── setup_stock_updater.sh
    ├── setup_stock_checker.sh
    ├── setup_supplier_sync.sh
    └── setup_rabbitmq.sh
```

## Variables

| Name | Description | Type | Default Value |
|------|-------------|------|---------------|
| aws_region | AWS region to deploy resources | string | us-east-1 |
| environment | Environment name (dev, staging, prod) | string | dev |
| vpc_cidr | CIDR block for VPC | string | 10.0.0.0/16 |
| public_subnet_cidrs | CIDR blocks for public subnets | list(string) | ["10.0.1.0/24", "10.0.2.0/24"] |
| private_subnet_cidrs | CIDR blocks for private subnets | list(string) | ["10.0.3.0/24", "10.0.4.0/24"] |
| availability_zones | Availability zones for subnets | list(string) | ["us-east-1a", "us-east-1b"] |
| ec2_ami | AMI ID for EC2 instances | string | ami-0c7217cdde317cfec |
| ec2_instance_type | Instance type for EC2 | string | t2.micro |
| db_instance_type | Instance type for RDS | string | db.t3.micro |
| db_username | Username for PostgreSQL database | string | postgres |
| db_password | Password for PostgreSQL database | string | - |
| ssh_key_name | Name of SSH key pair for EC2 | string | - |
| common_tags | Common tags for all resources | map(string) | { Project = "Inventory", Environment = "dev", ManagedBy = "Terraform" } |

## Usage

### Initialization

```bash
terraform init
```

### Variable Configuration

Create a `terraform.tfvars` file with your custom values:

```hcl
aws_region       = "us-east-1"
environment      = "dev"
db_password      = "your-secure-password"
ssh_key_name     = "your-key-pair-name"
```

### Execution Plan

```bash
terraform plan
```

### Apply Changes

```bash
terraform apply
```

Or to apply automatically:

```bash
terraform apply -auto-approve
```

### Destroy Infrastructure

```bash
terraform destroy
```

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | VPC ID |
| rds_endpoint | Endpoint for RDS PostgreSQL instance |
| stock_updater_public_ip | Public IP address of stock updater service |
| stock_checker_public_ip | Public IP address of stock checker service |
| supplier_sync_public_ip | Public IP address of supplier sync service |
| rabbitmq_public_ip | Public IP address of RabbitMQ server |
| stock_updater_service_url | URL for stock updater service API |
| stock_checker_service_url | URL for stock checker service API |
| supplier_sync_service_url | URL for supplier sync service API |
| rabbitmq_management_url | URL for RabbitMQ management interface |

## Initialization Scripts

The initialization scripts in the `scripts/` directory are used to configure EC2 instances when they are launched. These scripts:

1. Update the operating system
2. Install Docker and Docker Compose
3. Clone the source code repository
4. Configure environment variables
5. Create docker-compose.yml files
6. Start the services
7. Configure Nginx as a reverse proxy
8. Configure CloudWatch for logging

## Security

Security groups are configured to allow:

- SSH (port 22) from anywhere (consider restricting this in production)
- HTTP (port 80) from anywhere
- Specific application ports (8000-8002)
- PostgreSQL (port 5432) only from within the VPC
- RabbitMQ (ports 5672, 15672) only from within the VPC

## Best Practices

1. **Secrets Management**: Do not store passwords in code. Use AWS Secrets Manager or environment variables.
2. **High Availability**: For production environments, consider using Auto Scaling Groups and multiple availability zones.
3. **Monitoring**: Configure CloudWatch Alarms to monitor critical resources.
4. **Backup**: Configure automatic backups for RDS.
5. **Security**: Restrict security groups to necessary IPs.

## Troubleshooting

### SSH Connection Error

If you cannot connect to EC2 instances:

1. Verify that the SSH key pair exists in AWS
2. Verify that security groups allow SSH from your IP
3. Wait a few minutes after deployment for initialization scripts to complete

### Database Connection Error

If services cannot connect to the database:

1. Verify that the RDS instance is in "available" state
2. Verify that security groups allow connections on port 5432
3. Verify database credentials in .env files

### RabbitMQ Connection Error

If services cannot connect to RabbitMQ:

1. Verify that the RabbitMQ instance is running
2. Verify that security groups allow connections on ports 5672 and 15672
3. Verify RabbitMQ credentials in .env files
