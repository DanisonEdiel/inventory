provider "aws" {
  region = var.aws_region
}

# VPC and Networking
resource "aws_vpc" "inventory_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-vpc"
    }
  )
}

resource "aws_subnet" "public_subnet" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.inventory_vpc.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-public-subnet-${count.index + 1}"
    }
  )
}

resource "aws_subnet" "private_subnet" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.inventory_vpc.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-private-subnet-${count.index + 1}"
    }
  )
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.inventory_vpc.id

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-igw"
    }
  )
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.inventory_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-public-rt"
    }
  )
}

resource "aws_route_table_association" "public_rta" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = aws_subnet.public_subnet[count.index].id
  route_table_id = aws_route_table.public_rt.id
}

# Security Groups
resource "aws_security_group" "ec2_sg" {
  name        = "inventory-ec2-sg"
  description = "Security group for EC2 instances running inventory microservices"
  vpc_id      = aws_vpc.inventory_vpc.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Application ports
  ingress {
    from_port   = 8000
    to_port     = 8002
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # RabbitMQ ports
  ingress {
    from_port   = 5672
    to_port     = 5672
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 15672
    to_port     = 15672
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-ec2-sg"
    }
  )
}

resource "aws_security_group" "rds_sg" {
  name        = "inventory-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.inventory_vpc.id

  # PostgreSQL access from EC2 instances
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-rds-sg"
    }
  )
}

# RDS PostgreSQL
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "inventory-rds-subnet-group"
  subnet_ids = aws_subnet.private_subnet[*].id

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-rds-subnet-group"
    }
  )
}

resource "aws_db_instance" "postgres" {
  identifier             = "inventory-postgres"
  allocated_storage      = 20
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = var.db_instance_type
  db_name                = "inventory"
  username               = var.db_username
  password               = var.db_password
  parameter_group_name   = "default.postgres16"
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true
  publicly_accessible    = false
  multi_az               = var.environment == "prod"

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-postgres"
    }
  )
}

# EC2 Instances for Microservices
resource "aws_instance" "stock_updater" {
  ami                    = var.ec2_ami
  instance_type          = var.ec2_instance_type
  key_name               = var.ssh_key_name
  subnet_id              = aws_subnet.public_subnet[0].id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  user_data              = templatefile("${path.module}/scripts/setup_stock_updater.sh", {
    db_host     = aws_db_instance.postgres.address
    db_port     = aws_db_instance.postgres.port
    db_name     = aws_db_instance.postgres.db_name
    db_user     = aws_db_instance.postgres.username
    db_password = aws_db_instance.postgres.password
    RABBITMQ_HOST = aws_instance.rabbitmq.private_ip
    RABBITMQ_PORT = "5672"
    RABBITMQ_USER = "guest"
    RABBITMQ_PASSWORD = "guest"
    RABBITMQ_VHOST = "/"
  })

  root_block_device {
    volume_size = 20
    volume_type = "gp2"
  }

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-stock-updater"
    }
  )
}

resource "aws_instance" "stock_checker" {
  ami                    = var.ec2_ami
  instance_type          = var.ec2_instance_type
  key_name               = var.ssh_key_name
  subnet_id              = aws_subnet.public_subnet[0].id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  user_data              = templatefile("${path.module}/scripts/setup_stock_checker.sh", {
    db_host     = aws_db_instance.postgres.address
    db_port     = aws_db_instance.postgres.port
    db_name     = aws_db_instance.postgres.db_name
    db_user     = aws_db_instance.postgres.username
    db_password = aws_db_instance.postgres.password
  })

  root_block_device {
    volume_size = 20
    volume_type = "gp2"
  }

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-stock-checker"
    }
  )
}

resource "aws_instance" "supplier_sync" {
  ami                    = var.ec2_ami
  instance_type          = var.ec2_instance_type
  key_name               = var.ssh_key_name
  subnet_id              = aws_subnet.public_subnet[0].id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  user_data              = templatefile("${path.module}/scripts/setup_supplier_sync.sh", {
    db_host     = aws_db_instance.postgres.address
    db_port     = aws_db_instance.postgres.port
    db_name     = aws_db_instance.postgres.db_name
    db_user     = aws_db_instance.postgres.username
    db_password = aws_db_instance.postgres.password
    RABBITMQ_HOST = aws_instance.rabbitmq.private_ip
    RABBITMQ_PORT = "5672"
    RABBITMQ_USER = "guest"
    RABBITMQ_PASSWORD = "guest"
    RABBITMQ_VHOST = "/"
    CELERY_BROKER_URL = "amqp://guest:guest@${aws_instance.rabbitmq.private_ip}:5672/"
    CELERY_RESULT_BACKEND = "db+postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.address}:${aws_db_instance.postgres.port}/${aws_db_instance.postgres.db_name}"
    SYNC_SCHEDULE = "*/30 * * * *"
  })

  root_block_device {
    volume_size = 20
    volume_type = "gp2"
  }

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-supplier-sync"
    }
  )
}

# RabbitMQ EC2 Instance
resource "aws_instance" "rabbitmq" {
  ami                    = var.ec2_ami
  instance_type          = var.ec2_instance_type
  key_name               = var.ssh_key_name
  subnet_id              = aws_subnet.public_subnet[0].id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  user_data              = file("${path.module}/scripts/setup_rabbitmq.sh")

  root_block_device {
    volume_size = 20
    volume_type = "gp2"
  }

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-rabbitmq"
    }
  )
}

# Elastic IPs
resource "aws_eip" "stock_updater_eip" {
  instance = aws_instance.stock_updater.id
  domain   = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-stock-updater-eip"
    }
  )
}

resource "aws_eip" "stock_checker_eip" {
  instance = aws_instance.stock_checker.id
  domain   = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-stock-checker-eip"
    }
  )
}

resource "aws_eip" "supplier_sync_eip" {
  instance = aws_instance.supplier_sync.id
  domain   = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-supplier-sync-eip"
    }
  )
}

resource "aws_eip" "rabbitmq_eip" {
  instance = aws_instance.rabbitmq.id
  domain   = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name = "inventory-rabbitmq-eip"
    }
  )
}
