#!/bin/bash

# Update system packages
yum update -y
yum install -y git docker python3 python3-pip

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start Docker service
systemctl enable docker
systemctl start docker

# Create app directory
mkdir -p /opt/inventory/stock-updater-service

# Clone repository (in a real scenario, you would use a private repository)
cd /opt/inventory
git clone https://github.com/your-org/inventory.git .

# Create environment file with database connection details
cat > /opt/inventory/stock-updater-service/.env << EOF
POSTGRES_SERVER=${db_host}
POSTGRES_USER=${db_user}
POSTGRES_PASSWORD=${db_password}
POSTGRES_DB=${db_name}
POSTGRES_PORT=${db_port}
RABBITMQ_HOST=rabbitmq.internal
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
PROJECT_NAME="Stock Updater Service"
PROJECT_DESCRIPTION="Service for updating product stock levels"
PROJECT_VERSION="0.1.0"
API_PREFIX="/api"
ALLOWED_ORIGINS=*
EOF

# Create Docker Compose file
cat > /opt/inventory/stock-updater-service/docker-compose.yml << EOF
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_SERVER=${db_host}
      - POSTGRES_USER=${db_user}
      - POSTGRES_PASSWORD=${db_password}
      - POSTGRES_DB=${db_name}
      - POSTGRES_PORT=${db_port}
      - RABBITMQ_HOST=\${RABBITMQ_HOST}
      - RABBITMQ_PORT=\${RABBITMQ_PORT}
      - RABBITMQ_USER=\${RABBITMQ_USER}
      - RABBITMQ_PASSWORD=\${RABBITMQ_PASSWORD}
      - RABBITMQ_VHOST=\${RABBITMQ_VHOST}
    restart: always
EOF

# Build and start the service
cd /opt/inventory/stock-updater-service
docker-compose up -d

# Add a cron job to ensure the service is always running
echo "*/5 * * * * root cd /opt/inventory/stock-updater-service && docker-compose ps | grep -q 'app' || docker-compose up -d" > /etc/cron.d/stock-updater-service

# Set up Nginx as a reverse proxy
yum install -y nginx
cat > /etc/nginx/conf.d/stock-updater.conf << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Start Nginx
systemctl enable nginx
systemctl start nginx

# Set up CloudWatch for logging (optional, requires IAM role)
yum install -y amazon-cloudwatch-agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/docker",
            "log_group_name": "inventory-stock-updater",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

# Start CloudWatch agent
systemctl enable amazon-cloudwatch-agent
systemctl start amazon-cloudwatch-agent
