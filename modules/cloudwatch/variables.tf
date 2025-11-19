variable "lambda_names" {
  description = "List of lambda function names (strings) to create log groups for"
  type        = list(string)
}

variable "retention_in_days" {
  type    = number
  default = 14
}

variable "tags" {
  type    = map(string)
  default = {}
}
