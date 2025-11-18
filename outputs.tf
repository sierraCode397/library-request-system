output "api_endpoint" {
  value = module.api_gateway.api_endpoint
}

output "sqs_queue_url" {
  value = module.sqs.queue_url
}

output "dynamodb_table_id" {
  value = module.dynamodb.table_id
}

output "consumer_policy_arn" {
  value = module.iam.consumer_policy_arn
}

output "producer_policy_arn" {
  value = module.iam.producer_policy_arn
}