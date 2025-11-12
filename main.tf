provider "aws" {
  region = local.region
}

module "api_gateway" {
  source              = "./modules/api_gateway"
  name                = var.api_name
  lambda_function_arn = "arn:aws:lambda:us-east-1:905418449434:function:Test"
  region              = var.region
  tags = {
    Environment = "dev"
  }
}