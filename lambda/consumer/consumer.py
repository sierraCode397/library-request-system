import os, json, re
import boto3
import requests

TABLE_NAME = os.environ.get("TABLE_NAME")
if not TABLE_NAME:
    raise Exception("TABLE_NAME not set")

table = boto3.resource("dynamodb").Table(TABLE_NAME)
OPEN_SEARCH = "https://openlibrary.org/search.json"
OPEN_ISBN = "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"

def http_get_json(url, params=None, timeout=5):
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()

def _authors_from_obj(o):
    if not o: return []
    if isinstance(o, dict):
        if a := o.get("authors"):
            return [x.get("name") if isinstance(x, dict) else x for x in a if x]
        if a := o.get("author_name"):
            return [x for x in a if x]
    return []

def enrich_book(book):
    isbn = (book or {}).get("isbn")
    if isbn:
        try:
            data = http_get_json(OPEN_ISBN.format(isbn=isbn))
            key = f"ISBN:{isbn}"
            if key in data:
                od = data[key]
                authors = [a.get("name") if isinstance(a, dict) else a for a in od.get("authors", []) if a]
                return {
                    "title": od.get("title") or book.get("title"),
                    "authors": authors or book.get("author"),
                    "publish_date": od.get("publish_date"),
                    "isbn": isbn,
                    "openlibrary_raw": od
                }
        except Exception:
            pass

    q = " ".join(x for x in ((book or {}).get("title"), (book or {}).get("author")) if x)
    if not q:
        return book

    try:
        data = http_get_json(OPEN_SEARCH, params={"q": q, "limit": 1})
        docs = data.get("docs", [])
        if docs:
            d = docs[0]
            authors = d.get("author_name") or d.get("authors") or []
            authors = [a for a in (authors if isinstance(authors, list) else [authors]) if a]
            isbn_val = (d.get("isbn") or [None])[0] if d.get("isbn") else None
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
    book_payload = body.get("book") if isinstance(body, dict) and body.get("book") else body

    enriched = enrich_book(book_payload or {})

    authors = enriched.get("authors")
    if authors is None:
        ol = enriched.get("openlibrary_raw") or enriched.get("openlibrary_doc")
        authors = _authors_from_obj(ol) or []
    if not isinstance(authors, list):
        authors = [authors] if authors else []

    first_year = enriched.get("first_publish_year") or enriched.get("publish_date")
    parsed_year = None
    if first_year is not None:
        try:
            if isinstance(first_year, str):
                m = re.search(r"(\d{4})", first_year)
                parsed_year = int(m.group(1)) if m else None
            else:
                parsed_year = int(first_year)
        except Exception:
            parsed_year = None

    isbn = enriched.get("isbn") or (book_payload.get("isbn") if isinstance(book_payload, dict) else None)
    title_val = (enriched.get("title") or (book_payload.get("title") if isinstance(book_payload, dict) else None)
                 or body.get("title") or "unknown").strip()
    request_id = body.get("request_id") or record.get("messageId", "")
    pk = isbn if isbn else f"{title_val}#{request_id}"

    item = {
        "pk": str(pk),
        "title": title_val,
        "authors": authors,
        "first_publish_year": parsed_year,
        "isbn": isbn,
        "raw": body
    }

    table.put_item(Item=item)
    print(f"Written item pk={item['pk']}")
    return True

def lambda_handler(event, context):
    records = event.get("Records", [])
    processed = []
    for r in records:
        try:
            handle_record(r)
            processed.append({"id": r.get("messageId"), "status": "OK"})
        except Exception as e:
            print(f"ERROR processing message {r.get('messageId')}: {e}")
            raise
    return {"processed": processed}
