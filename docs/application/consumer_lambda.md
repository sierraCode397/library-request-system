# Consumer_lambda

## 1. Summary

`consumer_lambda` is an AWS Lambda function that consumes messages (typically from SQS), enriches book metadata using the Open Library API, and persists the final processed record into a DynamoDB table. It expects an event containing records where each `body` holds the book payload.

---

## 2. Purpose

* Enrich book metadata such as title, authors, publication year, and ISBN by calling Open Library.
* Store the enriched output in DynamoDB with a predictable primary key.
* Tolerate partial or missing data without failing.

---

## 3. Requirements & Dependencies

* Python 3.9+ (or the AWS Lambda runtime version you choose).
* Libraries: `boto3`, `requests` (must be packaged in the deployment artifact or provided via Lambda Layers).

---

## 4. Environment Variables

* **`TABLE_NAME`** (required): Name of the DynamoDB table where records will be written.

An exception is thrown at startup if this variable is missing.

---

## 5. Required AWS Resources & IAM

### Resources

* AWS Lambda function `consumer_lambda`.
* DynamoDB table (referenced by `TABLE_NAME`).
* SQS queue or other producer invoking this Lambda.

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

## 6. Expected Input (Event Payload)

The Lambda expects an event with `Records`, each similar to SQS format:

```json
{
  "Records": [
    {
      "messageId": "...",
      "body": "{ \"book\": { \"title\": \"...\", \"author\": \"...\" } }"
    }
  ]
}
```

`body` may contain:

* A JSON object with a `book` key, or
* A book object directly.

---

## 8. Key Functions

* **`http_get_json(url, ...)`**: Wrapper around `requests.get()` + `.raise_for_status()` + `.json()`.
* **`_authors_from_obj(o)`**: Extracts author names from varying Open Library structures.
* **`enrich_book(book)`**: Performs metadata enrichment via Open Library (ISBN first, fallback to search).
* **`handle_record(record)`**: Orchestrates parsing, enrichment, normalization, and persistence.
* **`lambda_handler(event, context)`**: Main entry point that processes all incoming records.

---

