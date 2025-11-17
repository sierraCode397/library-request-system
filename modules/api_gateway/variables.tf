variable "name" {
  type    = string
  default = "isaac-http-api"
}

variable "protocol_type" {
  type    = string
  default = "HTTP"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "stage_name" {
  type    = string
  default = "$default"
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "producer_lambda_arn" {
  type        = string
  description = "ARN of the producer Lambda function"
}

variable "consumer_lambda_arn" {
  type        = string
  description = "ARN of the consumer Lambda function"
}
