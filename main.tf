provider "aws" {
  region = local.region
}

# -----------------------
# 1) SQS (prerequisito)
# -----------------------
module "sqs" {
  source     = "./modules/sqs"
  queue_name = "books-queue"

  tags = {
    project = "simple-lambdas"
    owner   = "isaac"
  }
}

# -----------------------
# 2) DynamoDB (prerequisito)
# -----------------------
module "dynamodb" {
  source = "./modules/dynamodb"

  name         = "books-table"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "pk"
  range_key = "" # no sort key

  attributes = [
    { name = "pk", type = "S" }
  ]

  stream_enabled         = false
  ttl_enabled            = false
  point_in_time_recovery = true

  tags = {
    project = "simple-lambdas"
    owner   = "isaac"
  }
}

# -----------------------
# 3) IAM roles (usa ARNs de SQS y Dynamo)
# -----------------------
module "iam" {
  source = "./modules/iam"

  name_prefix        = "simple-lib"
  producer_sqs_arn   = module.sqs.queue_arn        # <-- asegurate que module.sqs exporte queue_arn
  consumer_sqs_arn   = module.sqs.queue_arn
  dynamodb_table_arn = module.dynamodb.table_arn   # <-- asegurate que module.dynamodb exporte table_arn

  tags = {
    project = "simple-lambdas"
    owner   = "isaac"
  }
}

# -----------------------
# 4) Lambdas (usa role ARNs y queue URL)
# -----------------------
module "simple_lambdas" {
  source = "./modules/lambdas"

  producer_zip_path = "${path.module}/lambda/producer.zip"
  consumer_zip_path = "${path.module}/lambda/consumer.zip"

  sqs_queue_url     = module.sqs.queue_url
  dynamodb_table_name = module.dynamodb.table_name

  producer_role_arn = module.iam.producer_role_arn
  consumer_role_arn = module.iam.consumer_role_arn

  tags = {
    project = "simple-lambdas"
    owner   = "isaac"
  }
}


# -----------------------
# 5) API Gateway (invoca producer lambda)
# -----------------------
module "api_gateway" {
  source = "./modules/api_gateway"

  name                 = var.api_name
  region               = var.region

  # el API invoca la lambda producer: se necesita el ARN de la lambda
  producer_lambda_arn  = module.simple_lambdas.producer_lambda_arn
  consumer_lambda_arn  = module.simple_lambdas.consumer_lambda_arn

  tags = {
    Environment = "dev"
  }
}
