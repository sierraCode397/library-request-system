variable "name" {
  type        = string
}

variable "billing_mode" {
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "hash_key" {
  type        = string
}

variable "range_key" {
  type        = string
  default     = ""
}

variable "attributes" {
  type = list(object({
    name = string
    type = string
  }))
}

variable "read_capacity" {
  type        = number
  default     = 5
}

variable "write_capacity" {
  type        = number
  default     = 5
}

variable "stream_enabled" {
  type    = bool
  default = false
}

variable "stream_view_type" {
  type    = string
  default = "NEW_IMAGE"
}

variable "ttl_enabled" {
  type    = bool
  default = false
}

variable "ttl_attribute" {
  type    = string
  default = "ttl"
}

variable "point_in_time_recovery" {
  type    = bool
  default = true
}

variable "sse_enabled" {
  type    = bool
  default = true
}

variable "sse_kms_key_arn" {
  type    = string
  default = ""
}

variable "tags" {
  type        = map(string)
  default     = {}
}
