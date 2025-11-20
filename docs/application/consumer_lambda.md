# Consumer_Lambda Documentation

## Overview

The **consumer Lambda** processes incoming messages from an SQS queue and executes business logic based on the content of each message.

---

## Purpose

This Lambda is responsible for consuming queued events and transforming, validating, or forwarding the processed data to internal application services.

---

## Architecture

* **Trigger:** SQS Queue.
* **Execution:** Each message triggers the Lambda.
* **Downstream Services:** May call internal APIs or store data in a database.
* **Dependencies:** AWS SDK, internal helper modules.

---

## Flow

1. Lambda receives an event from SQS.
2. Parses the message body.
3. Executes validation and business rules.
4. Sends processed results to the next service.
5. Deletes the message if processed successfully.

---

## IAM Permissions

* Read messages from SQS.
* Write logs to CloudWatch.
* Call internal services via API Gateway.

---

## Error Handling

* Automatic retries handled by SQS.
* Failed messages are redirected to a DLQ.

---

## Logging & Monitoring

* Logs written to CloudWatch.
* Metrics for invocation count and failures.

---

### Minimum IAM Permissions

```json
    Statement = [
      # SQS permissions
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
      # DynamoDB permissions
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
      # CloudWatch logs
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
```

tiny chnage