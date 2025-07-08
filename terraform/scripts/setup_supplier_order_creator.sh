#!/bin/bash
set -e

# Update and install dependencies
apt-get update
apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create app directory
mkdir -p /opt/inventory/supplier-order-creator

# Create docker-compose.yml
cat > /opt/inventory/supplier-order-creator/docker-compose.yml << 'EOL'
version: '3'

services:
  supplier-order-creator:
    build: .
    ports:
      - "8003:8003"
    environment:
      - DB_HOST=${db_host}
      - DB_PORT=${db_port}
      - DB_NAME=${db_name}
      - DB_USER=${db_user}
      - DB_PASSWORD=${db_password}
      - RABBITMQ_HOST=${RABBITMQ_HOST}
      - RABBITMQ_PORT=${RABBITMQ_PORT}
      - RABBITMQ_USER=${RABBITMQ_USER}
      - RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
      - RABBITMQ_VHOST=${RABBITMQ_VHOST}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
      - ORDER_SCHEDULE=${ORDER_SCHEDULE}
    restart: always
    volumes:
      - ./app:/app
EOL

# Clone the repository
cd /opt/inventory
git clone https://github.com/DanisonEdiel/inventory.git temp
cp -r temp/supplier-order-creator/* supplier-order-creator/
rm -rf temp

# Set permissions
chown -R ubuntu:ubuntu /opt/inventory

# Start the service
cd /opt/inventory/supplier-order-creator
docker-compose up -d
