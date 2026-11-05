from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

from app.config import settings


class Entry(BaseModel):
    name: str
    message: str


def connect():
    return psycopg.connect(settings.database_url)


@asynccontextmanager
async def lifespan(_: FastAPI):
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS entries ("
            "id SERIAL PRIMARY KEY, name TEXT NOT NULL, message TEXT NOT NULL)"
        )
    yield


app = FastAPI(title="guestbook", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/entries")
def list_entries():
    with connect() as conn:
        rows = conn.execute("SELECT id, name, message FROM entries ORDER BY id").fetchall()
    return [{"id": r[0], "name": r[1], "message": r[2]} for r in rows]


@app.post("/entries", status_code=201)
def add_entry(entry: Entry):
    with connect() as conn:
        conn.execute(
            "INSERT INTO entries (name, message) VALUES (%s, %s)",
            (entry.name, entry.message),
        )
    return entry
