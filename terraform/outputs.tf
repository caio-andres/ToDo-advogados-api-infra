# SSM Parameter Names

output "rds_endpoint" {
  description = "RDS instance endpoint (host:port)"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_address" {
  description = "RDS instance address (host only)"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.postgres.db_name
}

output "rds_username" {
  description = "RDS master username"
  value       = aws_db_instance.postgres.username
  sensitive   = true
}

output "rds_security_group_id" {
  description = "Security Group ID for RDS"
  value       = aws_security_group.rds.id
}

output "rds_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.postgres.arn
}

# SSM Parameter Names

output "ssm_parameters" {
  description = "SSM Parameter Store parameter names"
  value = {
    db_host     = aws_ssm_parameter.db_host.name
    db_port     = aws_ssm_parameter.db_port.name
    db_name     = aws_ssm_parameter.db_name.name
    db_user     = aws_ssm_parameter.db_user.name
    db_password = aws_ssm_parameter.db_password.name
    jwt_secret  = aws_ssm_parameter.jwt_secret.name
    secret_key  = aws_ssm_parameter.secret_key.name
  }
}

# Connection String (for local testing)

output "database_url" {
  description = "PostgreSQL connection string (for local use only)"
  value       = "postgresql://${aws_db_instance.postgres.username}:${var.db_password}@${aws_db_instance.postgres.address}:${aws_db_instance.postgres.port}/${aws_db_instance.postgres.db_name}"
  sensitive   = true
}

# Deployment

output "deployment_summary" {
  description = "Deployment summary"
  value = {
    project                 = var.project_name
    environment             = var.environment
    region                  = var.aws_region
    rds_endpoint            = aws_db_instance.postgres.endpoint
    rds_instance_class      = var.db_instance_class
    rds_storage             = "${var.db_allocated_storage}GB"
    rds_multi_az            = var.db_multi_az
    rds_publicly_accessible = var.db_publicly_accessible
  }
}
