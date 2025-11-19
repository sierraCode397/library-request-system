variable "queue_name" {
  type = string
}

variable "dlq_name" {
  type        = string
  description = "Name of the dead-letter queue"
}

variable "max_receive_count" {
  type        = number
  default     = 5
  description = "How many times a message can be received before going to DLQ"
}

variable "tags" {
  type = map(string)
}
