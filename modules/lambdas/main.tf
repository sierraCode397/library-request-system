# --- Producer Lambda ---
resource "aws_lambda_function" "producer" {
  filename         = var.producer_zip_path
  function_name    = var.producer_function_name
  role             = var.producer_role_arn        # ARN proveniente de module.iam
  handler          = var.producer_handler
  runtime          = var.lambda_runtime
  memory_size      = var.lambda_memory_size
  timeout          = var.lambda_timeout
  source_code_hash = filebase64sha256(var.producer_zip_path)
  tags             = var.tags
environment {
  variables = merge(
    {},
    var.sqs_queue_url != "" ? { SQS_URL = var.sqs_queue_url } : {},
    var.dynamodb_table_name != "" ? { DYNAMODB_TABLE = var.dynamodb_table_name } : {}
  )
}
}

# --- Consumer Lambda ---
resource "aws_lambda_function" "consumer" {
  filename         = var.consumer_zip_path
  function_name    = var.consumer_function_name
  role             = var.consumer_role_arn      # ARN proveniente de module.iam
  handler          = var.consumer_handler
  runtime          = var.lambda_runtime
  memory_size      = var.lambda_memory_size
  timeout          = var.lambda_timeout
  source_code_hash = filebase64sha256(var.consumer_zip_path)
  tags             = var.tags
  environment {
    variables = merge(
      {},
      var.dynamodb_table_name != "" ? { TABLE_NAME = var.dynamodb_table_name } : {}
    )
  }
}

# --- Event Source Mapping ---
resource "aws_lambda_event_source_mapping" "consumer_sqs" {
  event_source_arn = var.sqs_queue_arn
  function_name    = aws_lambda_function.consumer.arn
  enabled          = true
  batch_size       = 5
}
