terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.96"
    }
  }
  required_version = ">= 1.5.0"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "api_name" {
  type    = string
  default = "isaac-http-api"
}