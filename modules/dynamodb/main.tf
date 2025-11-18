resource "aws_dynamodb_table" "this" {
  name         = var.name
  billing_mode = var.billing_mode
  hash_key     = var.hash_key
  range_key    = var.range_key != "" ? var.range_key : null

  # Attributes
  dynamic "attribute" {
    for_each = var.attributes
    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }

  # Throughput (only if PROVISIONED)
  read_capacity  = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
  write_capacity = var.billing_mode == "PROVISIONED" ? var.write_capacity : null

  # Streams
  stream_enabled   = var.stream_enabled
  stream_view_type = var.stream_enabled ? var.stream_view_type : null

  # TTL
  ttl {
    attribute_name = var.ttl_attribute
    enabled        = var.ttl_enabled
  }

  # PITR
  point_in_time_recovery {
    enabled = var.point_in_time_recovery
  }

  # Encryption
  server_side_encryption {
    enabled     = var.sse_enabled
    kms_key_arn = var.sse_kms_key_arn != "" ? var.sse_kms_key_arn : null
  }

  tags = var.tags
}
