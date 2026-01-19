variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "cvchat"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "groq_api_key" {
  description = "Groq API key for LLM access"
  type        = string
  sensitive   = true
}

variable "content_origin" {
  description = "Content origin URL (e.g., https://msensat.dev)"
  type        = string
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 3008  # Max memory for better CPU performance
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300  # 5 minutes for cold starts and processing
}

variable "lambda_ephemeral_storage" {
  description = "Lambda ephemeral storage in MB"
  type        = number
  default     = 2048  # 2GB for model files
}

variable "allowed_origins" {
  description = "List of allowed CORS origins"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
