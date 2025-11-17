output "producer_lambda_arn" {
  value = aws_lambda_function.producer.arn
}

output "consumer_lambda_arn" {
  value = aws_lambda_function.consumer.arn
}
