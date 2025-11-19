data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# --- Producer Role ---
resource "aws_iam_role" "producer" {
  name               = "${var.name_prefix}-producer-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = var.tags
}

# Attach AWS managed policy for CloudWatch Logs (basic Lambda execution)
resource "aws_iam_role_policy_attachment" "producer_basic" {
  role       = aws_iam_role.producer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Producer inline policy (least privilege to send messages to SQS)
resource "aws_iam_role_policy" "producer_policy" {
  name = "${var.name_prefix}-producer-inline-policy"
  role = aws_iam_role.producer.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # SQS permissions
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:SendMessageBatch",
          "sqs:GetQueueAttributes"
        ]
        Resource = var.producer_sqs_arn
      },
      # DynamoDB read permissions (GET /producer)
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:GetItem",
          "dynamodb:DescribeTable"
        ]
        Resource = var.dynamodb_table_arn
      },
      # CloudWatch logs
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# --- Consumer Role ---
resource "aws_iam_role" "consumer" {
  name               = "${var.name_prefix}-consumer-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "consumer_basic" {
  role       = aws_iam_role.consumer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "consumer_policy" {
  name = "${var.name_prefix}-consumer-inline-policy"
  role = aws_iam_role.consumer.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # SQS permissions
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ]
        Resource = var.consumer_sqs_arn
      },
      # DynamoDB permissions
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:DescribeTable"
        ]
        Resource = var.dynamodb_table_arn
      },
      # CloudWatch logs
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}
