variable "producer_zip_path" {
  description = "Local path to the producer lambda zip"
  type        = string
}

variable "consumer_zip_path" {
  description = "Local path to the consumer lambda zip"
  type        = string
}

variable "producer_function_name" {
  description = "Name for the producer lambda function"
  type        = string
  default     = "producer-function"
}

variable "consumer_function_name" {
  description = "Name for the consumer lambda function"
  type        = string
  default     = "consumer-function"
}

variable "producer_handler" {
  description = "Handler for the producer lambda (module-level default)"
  type        = string
  default     = "producer.lambda_handler"
}

variable "consumer_handler" {
  description = "Handler for the consumer lambda (module-level default)"
  type        = string
  default     = "consumer.lambda_handler"
}

variable "producer_role_arn" {
  description = "ARN of the IAM role to be used by the producer lambda (from modules/iam)"
  type        = string
}

variable "consumer_role_arn" {
  description = "ARN of the IAM role to be used by the consumer lambda (from modules/iam)"
  type        = string
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.9"
}

variable "lambda_memory_size" {
  description = "Memory (MB) for the lambdas"
  type        = number
  default     = 128
}

variable "lambda_timeout" {
  description = "Timeout (seconds) for the lambdas"
  type        = number
  default     = 10
}

variable "sqs_queue_url" {
  description = "SQS queue URL to be injected into the producer lambda (optional)"
  type        = string
  default     = ""
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name to be injected into the consumer lambda (optional)"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to lambda resources"
  type        = map(string)
  default     = {}
}

variable "sqs_queue_arn" {
  type        = string
  description = "ARN of the SQS queue for consumer"
}

variable "consumer_lambda_arn" {
  type        = string
  description = "Optional: ARN of consumer Lambda if needed externally"
  default     = null
}