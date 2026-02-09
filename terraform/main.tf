# Terraform Configuration

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Opcional: Backend S3 para state remoto
  # backend "s3" {
  #   bucket         = "my-terraform-state-bucket"
  #   key            = "todo-advogados/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = merge(
      {
        Project     = var.project_name
        Environment = var.environment
        ManagedBy   = "Terraform"
      },
      var.tags
    )
  }
}

# Data Sources

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# Security Group (RDS)

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Security group for RDS PostgreSQL - allows public access"

  # Ingress: PostgreSQL from anywhere
  ingress {
    description = "PostgreSQL from anywhere"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress: Allow all outbound
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  }
}

# RDS PostgreSQL Instance

resource "aws_db_instance" "postgres" {
  # Identifier
  identifier = "${var.project_name}-${var.environment}-db"

  # Engine
  engine         = "postgres"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class

  # Storage
  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true

  # Database
  db_name  = var.db_name
  username = var.db_user
  password = var.db_password
  port     = 5432

  # Network
  publicly_accessible    = var.db_publicly_accessible
  vpc_security_group_ids = [aws_security_group.rds.id]

  # High Availability
  multi_az = var.db_multi_az

  # Backup
  backup_retention_period = var.db_backup_retention_period
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  # Deletion Protection
  deletion_protection       = var.environment == "prod" ? true : false
  skip_final_snapshot       = var.environment == "prod" ? false : true
  final_snapshot_identifier = var.environment == "prod" ? "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.rds_monitoring.arn

  # Performance Insights (desabilitado para custo mínimo)
  performance_insights_enabled = false

  # Auto minor version upgrade
  auto_minor_version_upgrade = true

  # Parameter group (default)
  parameter_group_name = "default.postgres15"

  tags = {
    Name = "${var.project_name}-${var.environment}-db"
  }
}

# ========================================
# IAM Role for RDS Enhanced Monitoring
# ========================================

resource "aws_iam_role" "rds_monitoring" {
  name = "${var.project_name}-${var.environment}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-monitoring-role"
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# SSM Parameters (Secrets)

# Database Host
resource "aws_ssm_parameter" "db_host" {
  name        = "/${var.project_name}/${var.environment}/db-host"
  description = "RDS database host"
  type        = "String"
  value       = aws_db_instance.postgres.address

  tags = {
    Name = "${var.project_name}-${var.environment}-db-host"
  }
}

# Database Port
resource "aws_ssm_parameter" "db_port" {
  name        = "/${var.project_name}/${var.environment}/db-port"
  description = "RDS database port"
  type        = "String"
  value       = tostring(aws_db_instance.postgres.port)

  tags = {
    Name = "${var.project_name}-${var.environment}-db-port"
  }
}

# Database Name
resource "aws_ssm_parameter" "db_name" {
  name        = "/${var.project_name}/${var.environment}/db-name"
  description = "RDS database name"
  type        = "String"
  value       = aws_db_instance.postgres.db_name

  tags = {
    Name = "${var.project_name}-${var.environment}-db-name"
  }
}

# Database User
resource "aws_ssm_parameter" "db_user" {
  name        = "/${var.project_name}/${var.environment}/db-user"
  description = "RDS database username"
  type        = "String"
  value       = aws_db_instance.postgres.username

  tags = {
    Name = "${var.project_name}-${var.environment}-db-user"
  }
}

# Database Password (SecureString)
resource "aws_ssm_parameter" "db_password" {
  name        = "/${var.project_name}/${var.environment}/db-password"
  description = "RDS database password"
  type        = "SecureString"
  value       = var.db_password

  tags = {
    Name = "${var.project_name}-${var.environment}-db-password"
  }
}

# JWT Secret Key (SecureString)
resource "aws_ssm_parameter" "jwt_secret" {
  name        = "/${var.project_name}/${var.environment}/jwt-secret"
  description = "JWT secret key for token signing"
  type        = "SecureString"
  value       = var.jwt_secret_key

  tags = {
    Name = "${var.project_name}-${var.environment}-jwt-secret"
  }
}

# Application Secret Key (SecureString)
resource "aws_ssm_parameter" "secret_key" {
  name        = "/${var.project_name}/${var.environment}/secret-key"
  description = "Application secret key"
  type        = "SecureString"
  value       = var.secret_key

  tags = {
    Name = "${var.project_name}-${var.environment}-secret-key"
  }
}

# CloudWatch Log Group (RDS)

resource "aws_cloudwatch_log_group" "rds_postgresql" {
  name              = "/aws/rds/instance/${aws_db_instance.postgres.identifier}/postgresql"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-postgresql-logs"
  }
}

resource "aws_cloudwatch_log_group" "rds_upgrade" {
  name              = "/aws/rds/instance/${aws_db_instance.postgres.identifier}/upgrade"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-upgrade-logs"
  }
}
