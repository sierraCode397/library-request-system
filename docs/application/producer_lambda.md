# Producer Lambda Documentation

## Overview

The **Producer Lambda** is responsible for receiving input data, validating it, and publishing structured messages to an SQS queue. These messages are later consumed by the **Consumer Lambda** for book enrichment and persistence.

## Key Responsibilities

* Receive book data (via API Gateway or other triggers).
* Validate and normalize the incoming payload.
* Add metadata such as a `request_id`.
* Publish the message to an SQS queue.
* Return a response confirming the publication.

## High-Level Flow

1. **Input received** → The Lambda is triggered with a JSON payload containing book information.
2. **Validation** → The Lambda ensures required fields exist, such as `title`, `author`, or `isbn`.
3. **Message wrapping** → The function wraps the book data alongside extra metadata.
4. **Publish to SQS** → The final payload is sent to a configured SQS queue.
5. **Return** → The Lambda returns an HTTP or event-based success response.

## Example Responsibilities in Code

* Create an SQS client using `boto3`.
* Call `send_message` with a serialized JSON body.
* Use `MessageAttributes` if needed.
* Handle small validation errors before sending.

## Interaction with Consumer Lambda

* The producer sends the message in a structure the consumer expects.
* Key field: `book` → contains title, author, isbn.
* Additional fields like `request_id` help the consumer generate unique primary keys.

## Summary

The Producer Lambda acts as the **entry point** to the book processing workflow. It ensures messages are clean, consistent, and correctly published to the SQS queue, enabling the Consumer Lambda to enrich and store book data reliably.

## API Usage

### Available Methods

* **GET** → Returns all items stored in DynamoDB. You can open the Producer Lambda URL directly in your browser to view the items.
* **POST** → Accepts book requests and sends them to SQS.

## Example Request

```bash
curl -sS -X POST 'https://yorledc60d.execute-api.us-east-1.amazonaws.com/producer' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Atomic Habits",
    "author": "James Clear"
  }'
```
