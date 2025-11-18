output "producer_role_arn" {
  value       = aws_iam_role.producer.arn
  description = "ARN of the Lambda role for producer"
}

output "producer_role_name" {
  value       = aws_iam_role.producer.name
  description = "Name of the Lambda role for producer"
}

output "producer_policy_arn" {
  value       = aws_iam_role_policy.producer_policy.id
  description = "Inline policy ID for the producer role"
}

output "consumer_role_arn" {
  value       = aws_iam_role.consumer.arn
  description = "ARN of the Lambda role for consumer"
}

output "consumer_role_name" {
  value       = aws_iam_role.consumer.name
  description = "Name of the Lambda role for consumer"
}

output "consumer_policy_arn" {
  value       = aws_iam_role_policy.consumer_policy.id
  description = "Inline policy ID for the consumer role"
}
