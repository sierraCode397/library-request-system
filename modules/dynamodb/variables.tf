variable "name" {
  type        = string
  description = "DynamoDB table name"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Tags to apply to the table"
}