import os
import time
import psycopg2
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg2.connect(DATABASE_URL)


# Create the table when the server starts
def setup_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_data (
            id INTEGER PRIMARY KEY,
            button_count INTEGER NOT NULL
        )
    """)

    cur.execute("""
        INSERT INTO game_data (id, button_count)
        VALUES (1, 0)
        ON CONFLICT (id) DO NOTHING
    """)

    conn.commit()
    cur.close()
    conn.close()


setup_database()


last_requests = {}
last_ct_requests = {}


@app.post("/increment")
def increment(request: Request):
    ip = request.client.host
    now = time.time()

    if ip in last_requests and now - last_requests[ip] < 0.1:
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

    last_requests[ip] = now

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE game_data
        SET button_count = button_count + 1
        WHERE id = 1
        RETURNING button_count
    """)

    count = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return {"count": count}


@app.post("/decrement")
def decrement():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE game_data
        SET button_count = button_count - 1
        WHERE id = 1
        RETURNING button_count
    """)

    count = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return {"count": count}


@app.get("/count")
def count(request: Request):
    ip = request.client.host
    now = time.time()

    if ip in last_ct_requests and now - last_ct_requests[ip] < 0.1:
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

    last_ct_requests[ip] = now

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT button_count
        FROM game_data
        WHERE id = 1
    """)

    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {"count": count}
