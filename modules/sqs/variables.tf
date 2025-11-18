variable "queue_name" {
  type        = string
  description = "Name of the SQS Queue"
}

variable "tags" {
  type        = map(string)
  description = "Tags for SQS"
  default     = {}
}
