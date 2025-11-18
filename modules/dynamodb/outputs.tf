output "table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.this.name
}

output "table_arn" {
  description = "DynamoDB table ARN"
  value       = aws_dynamodb_table.this.arn
}

output "stream_arn" {
  description = "DynamoDB stream ARN (if enabled)"
  value       = aws_dynamodb_table.this.stream_enabled ? aws_dynamodb_table.this.stream_arn : null
}

output "table_id" {
  description = "DynamoDB table ID"
  value       = aws_dynamodb_table.this.id
}
