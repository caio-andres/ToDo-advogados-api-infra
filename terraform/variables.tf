# Environment Variables

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name (used for naming resources)"
  type        = string
  default     = "todo-advogados"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# Database Variables

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "todo_db"
}

variable "db_user" {
  description = "Database master username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Database master password (min 8 chars)"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 8
    error_message = "Database password must be at least 8 characters."
  }
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20 # GB
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.14"
}

variable "db_backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 1 # Day(s)
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "db_publicly_accessible" {
  description = "Make RDS publicly accessible"
  type        = bool
  default     = true
}

# Application Secrets

variable "jwt_secret_key" {
  description = "JWT secret key for token signing"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.jwt_secret_key) >= 32
    error_message = "JWT secret key must be at least 32 characters."
  }
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.secret_key) >= 32
    error_message = "Secret key must be at least 32 characters."
  }
}

# Tags

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}
