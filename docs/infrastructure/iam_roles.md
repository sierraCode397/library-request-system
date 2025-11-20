# IAM Roles

## Overview

This document explains the IAM roles used within the infrastructure module. These roles define the permissions and trust relationships required for AWS Lambda functions (Producer and Consumer) to interact with AWS services such as SQS, DynamoDB, and CloudWatch.

---

## Lambda Assume Role Policy

The following IAM policy document defines the trust relationship that allows Lambda services to assume the IAM roles for both Producer and Consumer.

### **Assume Role Policy**

* **Service:** `lambda.amazonaws.com`
* **Purpose:** Grants Lambda permissions to execute using the attached IAM role.

```hcl
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
```

---

# Producer Role

## Purpose

The **Producer Lambda** sends messages to SQS and reads data from DynamoDB. It requires permissions to:

* Send messages to the SQS queue
* Read data from DynamoDB
* Write CloudWatch logs

---

## Role Definition

```hcl
resource "aws_iam_role" "producer" {
  name               = "${var.name_prefix}-producer-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = var.tags
}
```

### Attached Policies

#### 1. **AWSLambdaBasicExecutionRole** (Managed Policy)

Provides CloudWatch logging permissions.

```hcl
resource "aws_iam_role_policy_attachment" "producer_basic" {
  role       = aws_iam_role.producer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
```

#### 2. **Inline Policy: Producer Permissions**

Grants the Lambda function least‑privilege access required for:

* Sending messages to SQS
* Reading items from DynamoDB
* Writing logs to CloudWatch

```hcl
resource "aws_iam_role_policy" "producer_policy" {
  name = "${var.name_prefix}-producer-inline-policy"
  role = aws_iam_role.producer.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:SendMessageBatch",
          "sqs:GetQueueAttributes"
        ]
        Resource = var.producer_sqs_arn
      },
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
```

---

# Consumer Role

## Purpose

The **Consumer Lambda** receives and deletes messages from SQS, and writes new or updated items to DynamoDB. It requires permissions to:

* Receive messages from SQS
* Update or insert data into DynamoDB
* Write CloudWatch logs

---

## Role Definition

```hcl
resource "aws_iam_role" "consumer" {
  name               = "${var.name_prefix}-consumer-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = var.tags
}
```

### Attached Policies

#### 1. **AWSLambdaBasicExecutionRole** (Managed Policy)

Provides CloudWatch logging permissions.

```hcl
resource "aws_iam_role_policy_attachment" "consumer_basic" {
  role       = aws_iam_role.consumer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
```

#### 2. **Inline Policy: Consumer Permissions**

Grants the Lambda function least‑privilege permissions for:

* Receiving and deleting SQS messages
* Reading/writing data to DynamoDB
* Writing logs to CloudWatch

```hcl
resource "aws_iam_role_policy" "consumer_policy" {
  name = "${var.name_prefix}-consumer-inline-policy"
  role = aws_iam_role.consumer.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
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
```

---

# Summary

| Role         | Purpose                                   | Key Permissions                                           |
| ------------ | ----------------------------------------- | --------------------------------------------------------- |
| **Producer** | Sends SQS messages and reads DynamoDB     | `sqs:SendMessage`, `dynamodb:Scan`, CloudWatch Logs       |
| **Consumer** | Reads SQS messages and writes to DynamoDB | `sqs:ReceiveMessage`, `dynamodb:PutItem`, CloudWatch Logs |
