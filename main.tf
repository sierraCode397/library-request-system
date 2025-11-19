provider "aws" {
  region = local.region
}

terraform {
  backend "s3" {
    bucket = "library-epam-cloud-platform"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

module "sqs" {
  source = "./modules/sqs"
  queue_name        = "books-queue"
  dlq_name          = "books-queue-dlq"
  max_receive_count = 5
  tags = {
    project = "library-epam"
    owner   = "isaac"
  }
}

module "dynamodb" {
  source = "./modules/dynamodb"
  name = "books-table"
  tags = {
    project = "library-epam"
    owner   = "isaac"
  }
}

module "iam" {
  source = "./modules/iam"
  name_prefix        = "simple-lib"
  producer_sqs_arn   = module.sqs.queue_arn       
  consumer_sqs_arn   = module.sqs.queue_arn
  dynamodb_table_arn = module.dynamodb.table_arn  
  tags = {
    project = "library-epam"
    owner   = "isaac"
  }
}

module "lambdas" {
  source = "./modules/lambdas"
  producer_zip_path   = "${path.module}/lambda/producer/producer.zip"
  consumer_zip_path   = "${path.module}/lambda/consumer/consumer.zip"
  sqs_queue_url       = module.sqs.queue_url
  sqs_queue_arn       = module.sqs.queue_arn
  dynamodb_table_name = module.dynamodb.table_name
  producer_role_arn = module.iam.producer_role_arn
  consumer_role_arn = module.iam.consumer_role_arn
  tags = {
    project = "library-epam"
    owner   = "isaac"
  }
  depends_on = [module.cloudwatch]
}

module "api_gateway" {
  source = "./modules/api_gateway"
  name                = var.api_name
  region              = var.region
  producer_lambda_arn = module.lambdas.producer_lambda_arn
  consumer_lambda_arn = module.lambdas.consumer_lambda_arn
  tags = {
    Environment = "dev"
  }
}

module "cloudwatch" {
  source = "./modules/cloudwatch"
  lambda_names = ["producer-function", "consumer-function"]
  retention_in_days = 14
  tags = {
    project = "library-epam"
    owner   = "isaac"
  }
}
