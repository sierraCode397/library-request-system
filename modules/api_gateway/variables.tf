variable "name" {
  type    = string
  default = "isaac-http-api"
}

variable "protocol_type" {
  type    = string
  default = "HTTP"
}

# full lambda function ARN, e.g. arn:aws:lambda:us-east-1:123456789012:function:my-fn
variable "lambda_function_arn" {
  type        = string
  description = "ARN of the Lambda function to integrate with the API (required)"
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
