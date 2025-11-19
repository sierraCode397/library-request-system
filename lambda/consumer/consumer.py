import os
import json
import boto3

# optional dependency: requests; fallback to urllib
try:
    import requests
except Exception:
    requests = None
    from urllib import request as urllib_request
    import urllib.parse as urllib_parse

TABLE_NAME = os.environ.get("TABLE_NAME")
if not TABLE_NAME:
    raise Exception("TABLE_NAME not set")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

OPENLIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"  # query by title/author
OPENLIBRARY_BOOK_BY_ISBN = "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"

def http_get_json(url, params=None, timeout=5):
    """Use requests if available, otherwise urllib to return parsed JSON."""
    if requests:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    else:
        if params:
            url = url + "?" + urllib_parse.urlencode(params)
        with urllib_request.urlopen(url, timeout=timeout) as resp:
            return json.load(resp)

def normalize_authors_from_openlibrary_obj(obj):
    """Try several shapes where authors may appear in the OpenLibrary response."""
    if not obj:
        return []
    # common shapes:
    # - obj.get('authors') -> list of dicts with 'name'
    # - obj.get('author_name') -> list of strings
    if isinstance(obj, dict):
        if obj.get("authors"):
            authors = []
            for a in obj.get("authors", []):
                if isinstance(a, dict):
                    name = a.get("name")
                    if name:
                        authors.append(name)
                elif isinstance(a, str):
                    authors.append(a)
            return authors
        if obj.get("author_name"):
            # usually already a list of str
            return [a for a in obj.get("author_name") if a]
    return []

def enrich_book(book):
    """Try to enrich book info from OpenLibrary by ISBN first, then by search."""
    isbn = book.get("isbn")
    if isbn:
        url = OPENLIBRARY_BOOK_BY_ISBN.format(isbn=isbn)
        try:
            data = http_get_json(url, timeout=5)
            key = f"ISBN:{isbn}"
            if key in data:
                od = data[key]
                authors = []
                # authors here often list dicts with 'name'
                for a in od.get("authors", []):
                    if isinstance(a, dict):
                        name = a.get("name")
                        if name:
                            authors.append(name)
                    elif isinstance(a, str):
                        authors.append(a)
                return {
                    "title": od.get("title") or book.get("title"),
                    "authors": authors or book.get("author"),
                    "publish_date": od.get("publish_date"),
                    "isbn": isbn,
                    "openlibrary_raw": od
                }
        except Exception:
            # ignore enrichment failures, keep original
            pass

    # Fallback: search by title and/or author
    q = []
    if book.get("title"):
        q.append(book["title"])
    if book.get("author"):
        q.append(book["author"])
    if not q:
        return book

    params = {"q": " ".join(q), "limit": 1}
    try:
        data = http_get_json(OPENLIBRARY_SEARCH_URL, params=params, timeout=5)
        docs = data.get("docs", [])
        if docs:
            d = docs[0]
            authors = d.get("author_name") or d.get("authors") or []
            # ensure list of strings
            if isinstance(authors, list):
                authors = [a for a in authors if a]
            else:
                authors = [authors] if authors else []
            isbn_val = None
            if d.get("isbn"):
                isbn_val = (d.get("isbn") or [None])[0]
            return {
                "title": d.get("title") or book.get("title"),
                "authors": authors or book.get("author"),
                "first_publish_year": d.get("first_publish_year"),
                "isbn": isbn_val,
                "openlibrary_doc": d
            }
    except Exception:
        pass

    return book

def handle_record(record):
    body = json.loads(record.get("body") or "{}")
    enriched = enrich_book(body)

    # normalize authors: try enriched authors, then raw openlibrary doc, then empty list
    authors = enriched.get("authors")
    if authors is None:
        authors = []
        ol = enriched.get("openlibrary_raw") or enriched.get("openlibrary_doc")
        authors = normalize_authors_from_openlibrary_obj(ol) or []
    # ensure authors is a list (not [None])
    if not isinstance(authors, list):
        authors = [authors] if authors else []

    # normalize first_publish_year to int if possible
    first_year = enriched.get("first_publish_year") or enriched.get("publish_date")
    # try convert publish year-like values to int when possible
    parsed_year = None
    if first_year is not None:
        try:
            # sometimes publish_date is "July 2008" — try to extract last 4-digit year
            if isinstance(first_year, str):
                import re
                m = re.search(r"(\d{4})", first_year)
                if m:
                    parsed_year = int(m.group(1))
                else:
                    parsed_year = None
            else:
                parsed_year = int(first_year)
        except Exception:
            parsed_year = None

    isbn = enriched.get("isbn") or None
    msg_id = record.get("messageId") or record.get("messageId", "")
    title_val = (enriched.get("title") or body.get("title") or "unknown").strip()

    pk = isbn if isbn else f"{title_val}#{msg_id}"

    item = {
        "pk": str(pk),
        "title": title_val,
        "authors": authors,
        "first_publish_year": parsed_year,
        "isbn": isbn,
        "raw": enriched
    }

    # write to DynamoDB
    table.put_item(Item=item)
    print(f"Written item pk={item['pk']}")
    return True

def lambda_handler(event, context):
    # event["Records"] contains SQS messages
    records = event.get("Records", [])
    processed = []

    for r in records:
        try:
            handle_record(r)
            processed.append({"id": r.get("messageId"), "status": "OK"})
        except Exception as e:
            # log and re-raise so Lambda/SQS treat the batch as failed (retry / DLQ)
            print(f"ERROR processing message {r.get('messageId')}: {e}")
            raise

    return {"processed": processed}
