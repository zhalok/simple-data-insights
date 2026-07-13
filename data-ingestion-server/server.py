import csv
import os
import tempfile
from contextlib import contextmanager

import ijson
import psycopg2
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from psycopg2.extras import execute_values

UPLOAD_PAGE_PATH = os.path.join(os.path.dirname(__file__), "upload.html")

DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": int(os.environ.get("POSTGRES_PORT", 5432)),
    "dbname": os.environ.get("POSTGRES_DB", "postgres"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "postgres"),
}

COLUMNS = [
    "id",
    "platform",
    "timestamp",
    "author",
    "text",
    "language",
    "brand_mention",
    "sentiment",
    "sentiment_score",
    "topic",
    "reactions",
    "comments",
]

CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS takapay_posts (
        id BIGINT PRIMARY KEY,
        platform VARCHAR(50),
        timestamp TIMESTAMP,
        author VARCHAR(255),
        text TEXT,
        language VARCHAR(20),
        brand_mention BOOLEAN,
        sentiment VARCHAR(20),
        sentiment_score INTEGER,
        topic VARCHAR(100),
        reactions INTEGER,
        comments INTEGER
    )
"""

INSERT_SQL = f"""
    INSERT INTO takapay_posts ({", ".join(COLUMNS)})
    VALUES %s
    ON CONFLICT (id, timestamp) DO NOTHING
"""

UPLOAD_CHUNK_BYTES = 1024 * 1024  # 1 MB, bounds memory while streaming the upload to disk
BATCH_SIZE = int(os.environ.get("INGEST_BATCH_SIZE", 1000))  # rows per DB round-trip

app = FastAPI()


@contextmanager
def db_cursor():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        conn.autocommit = False
        with conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)
                yield conn, cur
    finally:
        conn.close()


def row_to_values(row: dict) -> tuple:
    return tuple(row.get(col) or None for col in COLUMNS)


def flush_batch(cur, batch: list) -> None:
    if batch:
        execute_values(cur, INSERT_SQL, batch)
        batch.clear()


async def spool_upload_to_disk(file: UploadFile) -> str:
    """Stream the upload to a temp file in fixed-size chunks so the whole
    payload never has to sit in memory at once."""
    fd, path = tempfile.mkstemp(prefix="ingest_")
    with os.fdopen(fd, "wb") as out:
        while chunk := await file.read(UPLOAD_CHUNK_BYTES):
            out.write(chunk)
    return path


def ingest_csv(path: str) -> int:
    inserted = 0
    with db_cursor() as (conn, cur):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)  # reads and yields one row at a time
            batch = []
            for row in reader:
                batch.append(row_to_values(row))
                inserted += 1
                if len(batch) >= BATCH_SIZE:
                    flush_batch(cur, batch)
                    conn.commit()
            flush_batch(cur, batch)
            conn.commit()
    return inserted


def ingest_json(path: str) -> int:
    inserted = 0
    with db_cursor() as (conn, cur):
        with open(path, "rb") as f:
            items = ijson.items(f, "item")  # streams array elements one at a time
            batch = []
            for row in items:
                batch.append(row_to_values(row))
                inserted += 1
                if len(batch) >= BATCH_SIZE:
                    flush_batch(cur, batch)
                    conn.commit()
            flush_batch(cur, batch)
            conn.commit()
    return inserted


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def upload_page():
    return FileResponse(UPLOAD_PAGE_PATH)


@app.post("/upload")
async def upload(file: UploadFile):
    filename = file.filename or ""
    if filename.lower().endswith(".csv"):
        file_type = "csv"
    elif filename.lower().endswith(".json"):
        file_type = "json"
    else:
        raise HTTPException(status_code=400, detail="File must have a .csv or .json extension")

    path = await spool_upload_to_disk(file)
    try:
        if file_type == "csv":
            inserted = ingest_csv(path)
        else:
            inserted = ingest_json(path)
    except (psycopg2.Error, ijson.JSONError, csv.Error) as exc:
        raise HTTPException(status_code=400, detail=f"Failed to ingest file: {exc}") from exc
    finally:
        os.remove(path)

    return {"filename": filename, "file_type": file_type, "rows_processed": inserted}
