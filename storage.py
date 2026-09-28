import os
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(os.getenv("DB_PATH", Path(__file__).parent / "data" / "tasks.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      TEXT NOT NULL,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    status       TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'done')),
    created_at   TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS learnings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    TEXT NOT NULL,
    topic      TEXT NOT NULL,
    notes      TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _since(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            yield conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.executescript(SCHEMA)


# ---------- Tasks ----------

def add_task(user_id: str, title: str, description: str = "") -> dict:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (user_id, title, description, created_at) VALUES (?, ?, ?, ?)",
            (user_id, title, description, _now()),
        )
    return get_task(user_id, cur.lastrowid)


def get_task(user_id: str, task_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)
        ).fetchone()
    return dict(row) if row else None


def list_tasks(user_id: str, status: str | None = None) -> list[dict]:
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params: list = [user_id]
    if status:
        query += " AND status = ?"
        params.append(status)
    with _connect() as conn:
        rows = conn.execute(query + " ORDER BY created_at", params).fetchall()
    return [dict(r) for r in rows]


def complete_task(user_id: str, task_id: int) -> dict | None:
    with _connect() as conn:
        conn.execute(
            "UPDATE tasks SET status = 'done', completed_at = ? "
            "WHERE id = ? AND user_id = ? AND status = 'open'",
            (_now(), task_id, user_id),
        )
    return get_task(user_id, task_id)


def delete_task(user_id: str, task_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    return cur.rowcount > 0


def list_completed_since(user_id: str, days: int) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND status = 'done' AND completed_at >= ? "
            "ORDER BY completed_at",
            (user_id, _since(days)),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------- Learnings ----------

def add_learning(user_id: str, topic: str, notes: str) -> dict:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO learnings (user_id, topic, notes, created_at) VALUES (?, ?, ?, ?)",
            (user_id, topic, notes, _now()),
        )
        row = conn.execute("SELECT * FROM learnings WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


def list_learnings(user_id: str, days: int = 7) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM learnings WHERE user_id = ? AND created_at >= ? ORDER BY created_at DESC",
            (user_id, _since(days)),
        ).fetchall()
    return [dict(r) for r in rows]
