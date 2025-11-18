variable "name_prefix" {
  description = "Prefix for IAM role names"
  type        = string
  default     = "simple-lib"
}

variable "producer_sqs_arn" {
  description = "ARN of the SQS queue used by the producer (SendMessage)"
  type        = string
}

variable "consumer_sqs_arn" {
  description = "ARN of the SQS queue used by the consumer (Receive/Delete)"
  type        = string
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table where consumer writes records"
  type        = string
}

variable "kms_key_arn" {
  description = "Optional KMS key ARN if DynamoDB uses KMS-managed encryption"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to add to the IAM roles"
  type        = map(string)
  default     = {}
}
