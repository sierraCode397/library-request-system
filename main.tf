provider "aws" {
  region = local.region
}

module "simple_lambdas" {
  source = "./modules/lambdas"

  producer_zip_path = "${path.module}/lambda/producer.zip"
  consumer_zip_path = "${path.module}/lambda/consumer.zip"

  tags = {
    project = "simple-lambdas"
    owner   = "isaac"
  }
}


module "api_gateway" {
  source = "./modules/api_gateway"

  name                 = var.api_name
  region               = var.region
  producer_lambda_arn  = module.simple_lambdas.producer_lambda_arn
  consumer_lambda_arn  = module.simple_lambdas.consumer_lambda_arn

  tags = {
    Environment = "dev"
  }
}
