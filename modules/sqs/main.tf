# Cola DLQ
resource "aws_sqs_queue" "dlq" {
  name = "${var.queue_name}-dlq"
  message_retention_seconds = 1209600 # 14 días
  tags = var.tags
}

# Cola principal
resource "aws_sqs_queue" "this" {
  name = var.queue_name

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 5
  })

  tags = var.tags
}
