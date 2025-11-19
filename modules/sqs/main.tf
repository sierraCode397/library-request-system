# Dead-Letter Queue (DLQ)
resource "aws_sqs_queue" "dlq" {
  name = "${var.queue_name}-dlq"
  message_retention_seconds = 259200
  tags = var.tags
}

# Main SQS Queue
resource "aws_sqs_queue" "this" {
  name = var.queue_name

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 5
  })
  tags = var.tags
}
