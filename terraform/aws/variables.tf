variable "aws_region" {
  description = "AWS region for the deployment."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for AWS resource naming."
  type        = string
  default     = "kira-payments"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "api_image_tag" {
  description = "Image tag for the API container."
  type        = string
  default     = "latest"
}

variable "blockchain_image_tag" {
  description = "Image tag for the blockchain container."
  type        = string
  default     = "latest"
}

variable "vendor_shared_secret" {
  description = "Shared secret used by the API."
  type        = string
  sensitive   = true
  default     = "mocked-secret"
}
