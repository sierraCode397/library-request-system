output "producer_lambda_arn" {
  value = aws_lambda_function.producer.arn
}

output "consumer_lambda_arn" {
  value = aws_lambda_function.consumer.arn
} 

output "producer_lambda_name" {
  value       = aws_lambda_function.producer.function_name
  description = "Name of the producer lambda"
}

output "consumer_lambda_name" {
  value       = aws_lambda_function.consumer.function_name
  description = "Name of the consumer lambda"
}
