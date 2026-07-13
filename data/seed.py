import argparse
import csv
import json

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
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


def load_csv(file_path):
    with open(file_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(file_path):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS takapay_posts (
        id BIGINT,
        platform VARCHAR(50),
        timestamp TIMESTAMP NOT NULL,
        author VARCHAR(255),
        text TEXT,
        language VARCHAR(20),
        brand_mention BOOLEAN,
        sentiment VARCHAR(20),
        sentiment_score INTEGER,
        topic VARCHAR(100),
        reactions INTEGER,
        comments INTEGER,
        PRIMARY KEY (id, timestamp)
    )
"""


def insert_rows(rows):
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)
                query = f"""
                    INSERT INTO takapay_posts ({", ".join(COLUMNS)})
                    VALUES ({", ".join(["%s"] * len(COLUMNS))})
                    ON CONFLICT (id, timestamp) DO NOTHING
                """
                values = [tuple(row.get(col) or None for col in COLUMNS) for row in rows]
                cur.executemany(query, values)
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Seed takapay_posts table from a CSV or JSON file.")
    parser.add_argument("file_path", help="Path to the data file")
    parser.add_argument("file_type", choices=["csv", "json"], help="Type of the data file")
    args = parser.parse_args()

    if args.file_type == "csv":
        rows = load_csv(args.file_path)
    else:
        rows = load_json(args.file_path)

    insert_rows(rows)
    print(f"Inserted {len(rows)} rows into takapay_posts")


if __name__ == "__main__":
    main()
