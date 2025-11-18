variable "producer_zip_path" {
  description = "Local path to the producer lambda zip"
  type        = string
}

variable "consumer_zip_path" {
  description = "Local path to the consumer lambda zip"
  type        = string
}

variable "lambda_runtime" {
  type    = string
  default = "python3.9"
}

variable "lambda_memory_size" {
  type    = number
  default = 128
}

variable "lambda_timeout" {
  type    = number
  default = 10
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "sqs_queue_url" {
  type        = string
  description = "SQS queue URL to be injected into the producer lambda (optional)"
  default     = ""
}
