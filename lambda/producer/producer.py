import os, json, uuid, re
from datetime import datetime, timezone
import boto3

SQS_URL = os.environ.get("SQS_URL")
DDB_TABLE = os.environ.get("DYNAMODB_TABLE")
if not SQS_URL:
    raise Exception("SQS_URL not set in environment")

sqs = boto3.client("sqs")
table = boto3.resource("dynamodb").Table(DDB_TABLE) if DDB_TABLE else None

# --- helpers ---
def iso_now():
    return datetime.now(timezone.utc).isoformat()

def normalize_str(v):
    if v is None: return None
    s = str(v).strip()
    return s or None

def normalize_isbn(isbn):
    if not isbn: return None
    s = re.sub(r"[^0-9Xx]", "", str(isbn))
    s = s.upper()
    return s if len(s) in (10, 13) else s  # keep cleaned value even if invalid length (original behavior)

def is_valid_isbn(isbn):
    if not isbn: return True
    if len(isbn) == 10:
        return all(ch.isdigit() for ch in isbn[:-1]) and (isbn[-1].isdigit() or isbn[-1] == "X")
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

# --- validate & build message ---
def validate_and_transform(payload):
    errors = []
    payload = payload or {}

    title = normalize_str(payload.get("title"))
    author = normalize_str(payload.get("author"))
    isbn_raw = payload.get("isbn")
    isbn = normalize_isbn(isbn_raw)
    requested_by = normalize_str(payload.get("requested_by"))
    priority = payload.get("priority")
    source = normalize_str(payload.get("source"))

    if not title:
        errors.append({"field": "title", "message": "title is required and must be a non-empty string"})
    if not author:
        errors.append({"field": "author", "message": "author is required and must be a non-empty string"})

    if isbn_raw is not None:
        if not isbn:
            errors.append({"field": "isbn", "message": "isbn provided but could not be normalized to 10 or 13 chars"})
        elif not is_valid_isbn(isbn):
            errors.append({"field": "isbn", "message": "isbn looks invalid (expected 10 or 13 digits, last char may be X for ISBN-10)"})

    if priority is not None:
        try:
            priority = int(priority)
            if priority < 0:
                errors.append({"field": "priority", "message": "priority must be >= 0"})
        except Exception:
            errors.append({"field": "priority", "message": "priority must be an integer"})

    if errors:
        return None, errors

    # normalized raw (keep original keys + normalized book)
    normalized_raw = dict(payload)
    normalized_raw["book"] = {"title": title, "author": author, **({"isbn": isbn} if isbn else {})}
    if requested_by: normalized_raw["requested_by"] = requested_by
    if priority is not None: normalized_raw["priority"] = priority
    if source: normalized_raw["source"] = source

    message = {
        "request_id": str(uuid.uuid4()),
        "requested_at": iso_now(),
        "book": {"title": title, "author": author, **({"isbn": isbn} if isbn else {})},
        **({"requested_by": requested_by} if requested_by else {}),
        **({"priority": priority} if priority is not None else {}),
        **({"source": source} if source else {}),
        "raw": normalized_raw
    }
    return message, []

# --- dynamo scan ---
def scan_table(limit=None):
    if table is None:
        raise Exception("DYNAMODB_TABLE not configured")
    resp = table.scan(Limit=int(limit)) if limit else table.scan()
    return resp.get("Items", []), resp.get("LastEvaluatedKey")

# --- lambda handler ---
def lambda_handler(event, context):
    # detect method (support API Gateway v2 and legacy)
    method = (event.get("requestContext", {}) .get("http", {}) .get("method")) or event.get("httpMethod")
    if method == "GET":
        qp = event.get("queryStringParameters") or {}
        limit = qp.get("limit") if qp else None
        try:
            items, last_key = scan_table(limit=limit)
            body = {"items": items}
            if last_key: body["last_evaluated_key"] = last_key
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(body, default=str)}
        except Exception as e:
            return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": str(e)})}

    if method == "POST":
        try:
            payload = parse_json_body(event)
        except ValueError as e:
            return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": str(e)})}

        message, errors = validate_and_transform(payload)
        if errors:
            return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"errors": errors})}

        try:
            resp = sqs.send_message(QueueUrl=SQS_URL, MessageBody=json.dumps(message))
        except Exception as e:
            return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "failed to send message", "detail": str(e)})}

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "request queued", "message_id": resp.get("MessageId"), "request_id": message["request_id"]})
        }

    return {"statusCode": 405, "headers": {"Allow": "GET, POST"}, "body": json.dumps({"error": "Method not allowed"})}
