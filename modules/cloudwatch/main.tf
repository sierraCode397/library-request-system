resource "aws_cloudwatch_log_group" "this" {
  for_each = toset(var.lambda_names)

  name              = "/aws/lambda/${each.value}"
  retention_in_days = var.retention_in_days
  tags              = var.tags
}
