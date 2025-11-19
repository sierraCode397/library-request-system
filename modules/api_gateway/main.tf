data "aws_caller_identity" "current" {}

resource "aws_apigatewayv2_api" "this" {
  name          = var.name
  protocol_type = var.protocol_type
  tags          = var.tags
}

# -------------------------------
# Producer Integration
# -------------------------------
resource "aws_apigatewayv2_integration" "producer_integration" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  payload_format_version = "2.0"

  integration_uri = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${var.producer_lambda_arn}/invocations"
}

resource "aws_apigatewayv2_route" "producer_route_post" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "POST /producer"
  target    = "integrations/${aws_apigatewayv2_integration.producer_integration.id}"
}

resource "aws_apigatewayv2_route" "producer_route_get" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "GET /producer"
  target    = "integrations/${aws_apigatewayv2_integration.producer_integration.id}"
}

resource "aws_lambda_permission" "producer_permission" {
  statement_id  = "AllowProducerInvocation"
  action        = "lambda:InvokeFunction"
  function_name = var.producer_lambda_arn
  principal     = "apigateway.amazonaws.com"

  # Use execution_arn with account / api id + wildcard for stages/methods.
  # This is robust for v2 APIs.
  source_arn = "${aws_apigatewayv2_api.this.execution_arn}/*/*"
}
# -------------------------------
# Stage
# -------------------------------
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = var.stage_name
  auto_deploy = true
}