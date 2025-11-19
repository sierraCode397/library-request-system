# producer.py
import os
import json
import uuid
from datetime import datetime, timezone

import boto3

sqs_url = os.environ.get("SQS_URL")
dynamodb_table = os.environ.get("DYNAMODB_TABLE")  # opcional, para GET
if not sqs_url:
    raise Exception("SQS_URL not set in environment")

sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")
table = None
if dynamodb_table:
    table = dynamodb.Table(dynamodb_table)

# ---------- Helpers ----------
def iso_now():
    return datetime.now(timezone.utc).isoformat()

def normalize_str(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s != "" else None

def normalize_isbn(isbn):
    if not isbn:
        return None
    s = str(isbn).strip().replace("-", "").replace(" ", "")
    # keep only digits/X (for ISBN-10 sometimes ends with X)
    s = "".join(ch for ch in s if ch.isdigit() or ch.upper() == "X")
    if len(s) in (10, 13):
        return s
    # invalid length -> return as-is (we'll treat invalid later if needed)
    return s

def is_valid_isbn(isbn):
    if not isbn:
        return True  # optional
    if len(isbn) == 10:
        return all(ch.isdigit() for ch in isbn[:-1]) and (isbn[-1].isdigit() or isbn[-1].upper() == "X")
    if len(isbn) == 13:
        return isbn.isdigit()
    return False

def parse_json_body(event):
    body = event.get("body")
    if body is None:
        return {}
    if isinstance(body, str):
        try:
            return json.loads(body)
        except Exception:
            raise ValueError("Request body is not valid JSON")
    if isinstance(body, dict):
        return body
    raise ValueError("Unsupported request body type")

# ---------- Validation & Transform ----------
def validate_and_transform(payload):
    """
    Validate payload and return (message, errors).
    message includes:
      - request_id
      - requested_at
      - book: { title, author, (isbn) }
      - requested_by (optional)
      - raw: normalized original payload (keeps optional/extra fields)
    """
    errors = []

    # preserve original payload minimally normalized for `raw`
    raw_payload = {}
    for k, v in (payload or {}).items():
        raw_payload[k] = v

    # normalize required fields
    title = normalize_str(payload.get("title"))
    author = normalize_str(payload.get("author"))
    isbn_raw = payload.get("isbn")
    isbn = normalize_isbn(isbn_raw)
    requested_by = normalize_str(payload.get("requested_by"))
    priority = payload.get("priority")
    source = normalize_str(payload.get("source"))

    # required checks
    if not title:
        errors.append({"field": "title", "message": "title is required and must be a non-empty string"})
    if not author:
        errors.append({"field": "author", "message": "author is required and must be a non-empty string"})

    # isbn basic validation
    if isbn_raw is not None:
        if not isbn:
            errors.append({"field": "isbn", "message": "isbn provided but could not be normalized to 10 or 13 chars"})
        elif not is_valid_isbn(isbn):
            errors.append({"field": "isbn", "message": "isbn looks invalid (expected 10 or 13 digits, last char may be X for ISBN-10)"})

    # priority as integer (optional)
    if priority is not None:
        try:
            priority = int(priority)
            if priority < 0:
                errors.append({"field": "priority", "message": "priority must be >= 0"})
        except Exception:
            errors.append({"field": "priority", "message": "priority must be an integer"})

    if errors:
        return None, errors

    # Rebuild a normalized raw payload to include into message
    normalized_raw = dict(raw_payload)  # start with original values
    # overwrite normalized key forms for convenience (do not remove other keys)
    normalized_raw["book"] = {
        "title": title,
        "author": author,
        **({"isbn": isbn} if isbn else {})
    }
    # include requested_by if present (so consumer sees it in raw too)
    if requested_by:
        normalized_raw["requested_by"] = requested_by
    if priority is not None:
        normalized_raw["priority"] = priority
    if source:
        normalized_raw["source"] = source

    # final message payload
    message = {
        "request_id": str(uuid.uuid4()),
        "requested_at": iso_now(),
        "book": {
            "title": title,
            "author": author,
            **({"isbn": isbn} if isbn else {})
        },
        # metadata top-level (optional)
        **({"requested_by": requested_by} if requested_by else {}),
        **({"priority": priority} if priority is not None else {}),
        **({"source": source} if source else {}),
        # include normalized original payload for consumer/debugging
        "raw": normalized_raw
    }

    return message, []

# ---------- DynamoDB read (GET) ----------
def scan_table(limit=None):
    if table is None:
        raise Exception("DYNAMODB_TABLE not configured")
    if limit:
        resp = table.scan(Limit=int(limit))
    else:
        resp = table.scan()
    items = resp.get("Items", [])
    return items, resp.get("LastEvaluatedKey")

# ---------- Lambda handler ----------
def lambda_handler(event, context):
    # determine method (HTTP API v2 or fallback)
    method = None
    try:
        method = event["requestContext"]["http"]["method"]
    except Exception:
        method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")

    # GET: read from DynamoDB if configured
    if method == "GET":
        limit = None
        try:
            qp = event.get("queryStringParameters") or {}
            if qp and qp.get("limit"):
                limit = qp.get("limit")
        except Exception:
            limit = None
        try:
            items, last_key = scan_table(limit=limit)
            body = {"items": items}
            if last_key:
                body["last_evaluated_key"] = last_key
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(body, default=str)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)})
            }

    # POST: validate, restructure and send to SQS
    if method == "POST":
        try:
            payload = parse_json_body(event)
        except ValueError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)})
            }

        message, errors = validate_and_transform(payload)
        if errors:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"errors": errors})
            }

        try:
            resp = sqs.send_message(QueueUrl=sqs_url, MessageBody=json.dumps(message))
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "failed to send message", "detail": str(e)})
            }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "request queued",
                "message_id": resp.get("MessageId"),
                "request_id": message["request_id"]
            })
        }

    # default
    return {
        "statusCode": 405,
        "headers": {"Allow": "GET, POST"},
        "body": json.dumps({"error": "Method not allowed"})
    }
