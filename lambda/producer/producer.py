import os
import json
import boto3

sqs_url = os.environ.get("SQS_URL")
if not sqs_url:
    raise Exception("SQS_URL not set in environment")

sqs = boto3.client("sqs")

def validate_and_transform(payload):
    # Esperamos: { "title": "...", "author": "...", "isbn": "..." (optional) }
    title = payload.get("title")
    author = payload.get("author")
    if not title or not author:
        raise ValueError("Missing required 'title' or 'author' in payload")
    # normalizar estructura
    book = {
        "title": str(title).strip(),
        "author": str(author).strip(),
    }
    if payload.get("isbn"):
        book["isbn"] = str(payload.get("isbn")).strip()
    if payload.get("requested_by"):
        book["requested_by"] = str(payload.get("requested_by")).strip()
    return book

def lambda_handler(event, context):
    # API Gateway proxy integration: body en event["body"]
    try:
        body = event.get("body")
        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body or {}
        book = validate_and_transform(payload)
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }

    # enviar a SQS
    try:
        resp = sqs.send_message(
            QueueUrl=sqs_url,
            MessageBody=json.dumps(book)
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "failed to send message", "detail": str(e)})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "request queued", "message_id": resp.get("MessageId")})
    }
