# AWS Architecture Components

## Provider Configuration

```hcl
provider "aws" {
  region = local.region
}
```

Defines the AWS provider and sets the deployment region.

---

## Terraform Backend

```hcl
terraform {
  backend "s3" {
    bucket = "library-epam-cloud-platform"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}
```

The Terraform state is stored remotely in an S3 bucket, enabling collaboration and secure state management.

---

## SQS Module

```hcl
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
```

Creates:

* **Main SQS queue** (`books-queue`)
* **Dead Letter Queue (DLQ)** (`books-queue-dlq`)
* Configures retry handling with `max_receive_count`

Purpose: decouples producer and consumer workloads.

---

## DynamoDB Module

```hcl
module "dynamodb" {
  source = "./modules/dynamodb"
  name = "books-table"
  tags = {
    project = "library-epam"
    owner   = "isaac"
  }
}
```

Creates a DynamoDB table called **books-table**, used to store application data.

---

## IAM Module

```hcl
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
```

Creates IAM roles for:

* Producer Lambda
* Consumer Lambda

Grants them the necessary permissions to access:

* SQS queue
* DynamoDB table

---

## Lambda Module

```hcl
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
```

Deploys two Lambda functions:

* **Producer** → sends messages to SQS
* **Consumer** → processes SQS messages and writes to DynamoDB

---

## API Gateway Module

```hcl
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
```

Creates an API Gateway that exposes endpoints that invoke:

* Producer Lambda
* Consumer Lambda

---

## CloudWatch Module

```hcl
module "cloudwatch" {
  source = "./modules/cloudwatch"
  lambda_names = ["producer-function", "consumer-function"]
  retention_in_days = 3
  tags = {
    project = "library-epam"
    owner   = "isaac"
  }
}
```

Configures:

* CloudWatch log groups for both Lambda functions
* 3-day retention policy

---

## Architecture Summary

This infrastructure implements an event-driven architecture using:

* API Gateway for client interaction
* Lambda functions for compute
* SQS for asynchronous message handling
* DynamoDB for data persistence
* IAM for secure access control
* CloudWatch for monitoring

Each Terraform module represents a well-isolated component following best IaC practices.
