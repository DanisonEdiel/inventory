output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.inventory_vpc.id
}

output "rds_endpoint" {
  description = "Endpoint for the RDS PostgreSQL instance"
  value       = aws_db_instance.postgres.endpoint
}

output "stock_updater_public_ip" {
  description = "Public IP address of the stock updater service"
  value       = aws_eip.stock_updater_eip.public_ip
}

output "stock_checker_public_ip" {
  description = "Public IP address of the stock checker service"
  value       = aws_eip.stock_checker_eip.public_ip
}

output "supplier_sync_public_ip" {
  description = "Public IP of the Supplier Sync Service"
  value       = aws_eip.supplier_sync_eip.public_ip
}

output "supplier_order_creator_public_ip" {
  description = "Public IP of the Supplier Order Creator Service"
  value       = aws_instance.supplier_order_creator.public_ip
}

output "rabbitmq_public_ip" {
  description = "Public IP address of the RabbitMQ server"
  value       = aws_eip.rabbitmq_eip.public_ip
}

output "stock_updater_service_url" {
  description = "URL for the stock updater service API"
  value       = "http://${aws_eip.stock_updater_eip.public_ip}:8000"
}

output "stock_checker_service_url" {
  description = "URL for the stock checker service API"
  value       = "http://${aws_eip.stock_checker_eip.public_ip}:8001"
}

output "supplier_sync_service_url" {
  description = "URL for the supplier sync service API"
  value       = "http://${aws_eip.supplier_sync_eip.public_ip}:8002"
}

output "rabbitmq_management_url" {
  description = "URL for the RabbitMQ management interface"
  value       = "http://${aws_eip.rabbitmq_eip.public_ip}:15672"
}
