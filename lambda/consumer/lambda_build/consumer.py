import os
import json
import boto3
import requests  # si no lo incluyes en ZIP, usa urllib

TABLE_NAME = os.environ.get("TABLE_NAME")
if not TABLE_NAME:
    raise Exception("TABLE_NAME not set")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

OPENLIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"  # query by title/author
OPENLIBRARY_BOOK_BY_ISBN = "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"

def enrich_book(book):
    # Tratar de buscar por ISBN si existe
    isbn = book.get("isbn")
    if isbn:
        url = OPENLIBRARY_BOOK_BY_ISBN.format(isbn=isbn)
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
            key = f"ISBN:{isbn}"
            if key in data:
                od = data[key]
                return {
                    "title": od.get("title", book.get("title")),
                    "authors": [a.get("name')") if isinstance(a, dict) else a for a in od.get("authors", [])],
                    "publish_date": od.get("publish_date"),
                    "isbn": isbn,
                    "openlibrary_raw": od
                }
        except Exception:
            # ignore enrichment failures, keep original
            pass

    # Fallback: search by title
    q = []
    if book.get("title"):
        q.append(book["title"])
    if book.get("author"):
        q.append(book["author"])
    if not q:
        return book

    params = {"q": " ".join(q), "limit": 1}
    try:
        r = requests.get(OPENLIBRARY_SEARCH_URL, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        docs = data.get("docs", [])
        if docs:
            d = docs[0]
            return {
                "title": d.get("title") or book.get("title"),
                "authors": d.get("author_name"),
                "first_publish_year": d.get("first_publish_year"),
                "isbn": (d.get("isbn") or [None])[0],
                "openlibrary_doc": d
            }
    except Exception:
        pass

    return book

def handle_record(record):
    body = json.loads(record.get("body") or "{}")
    enriched = enrich_book(body)
    # prepare item - use pk as book:id (e.g., title#timestamp) or ISBN if available
    pk = enriched.get("isbn") or f"{enriched.get('title')}#{record.get('messageId', '')}"
    item = {
        "pk": str(pk),
        "title": enriched.get("title"),
        "authors": enriched.get("authors"),
        "raw": enriched
    }
    # write to DynamoDB
    table.put_item(Item=item)
    return True

def lambda_handler(event, context):
    # event["Records"] contains SQS messages
    records = event.get("Records", [])
    results = []
    for r in records:
        try:
            handle_record(r)
            results.append({"id": r.get("messageId"), "status": "OK"})
        except Exception as e:
            results.append({"id": r.get("messageId"), "status": "ERROR", "error": str(e)})
    return {"processed": results}
