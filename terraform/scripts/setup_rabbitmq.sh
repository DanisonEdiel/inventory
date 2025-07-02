#!/bin/bash

# Update system packages
yum update -y
yum install -y docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start Docker service
systemctl enable docker
systemctl start docker

# Create app directory
mkdir -p /opt/rabbitmq

# Create Docker Compose file for RabbitMQ
cat > /opt/rabbitmq/docker-compose.yml << EOF
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    restart: always

volumes:
  rabbitmq_data:
EOF

# Start RabbitMQ
cd /opt/rabbitmq
docker-compose up -d

# Add a cron job to ensure RabbitMQ is always running
echo "*/5 * * * * root cd /opt/rabbitmq && docker-compose ps | grep -q 'rabbitmq' || docker-compose up -d" > /etc/cron.d/rabbitmq

# Set up Nginx as a reverse proxy for RabbitMQ management
yum install -y nginx
cat > /etc/nginx/conf.d/rabbitmq.conf << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:15672;
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
            "log_group_name": "inventory-rabbitmq",
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
