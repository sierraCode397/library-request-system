locals {
  lambda_assume_role = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Role for lambdas (basic logging)
resource "aws_iam_role" "lambda_role" {
  name               = "simple-lambda-role"
  assume_role_policy = local.lambda_assume_role
}

resource "aws_iam_role_policy" "lambda_logging" {
  name = "simple-lambda-logging"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Producer
resource "aws_lambda_function" "producer" {
  filename         = var.producer_zip_path
  function_name    = "producer-simple"
  role             = aws_iam_role.lambda_role.arn
  handler          = "producer.lambda_handler"
  runtime          = var.lambda_runtime
  memory_size      = var.lambda_memory_size
  timeout          = var.lambda_timeout
  source_code_hash = filebase64sha256(var.producer_zip_path)
  tags             = var.tags
}

# Consumer
resource "aws_lambda_function" "consumer" {
  filename         = var.consumer_zip_path
  function_name    = "consumer-simple"
  role             = aws_iam_role.lambda_role.arn
  handler          = "consumer.lambda_handler"
  runtime          = var.lambda_runtime
  memory_size      = var.lambda_memory_size
  timeout          = var.lambda_timeout
  source_code_hash = filebase64sha256(var.consumer_zip_path)
  tags             = var.tags
}
