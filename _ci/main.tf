terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    # Configure this with your S3 bucket for state storage
    # bucket = "your-terraform-state-bucket"
    # key    = "cvchat/terraform.tfstate"
    # region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
