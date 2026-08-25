from datetime import datetime, timezone
import sqlite3

from app.application.authorization import UserContext


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_user(connection: sqlite3.Connection, user: UserContext) -> None:
    connection.execute(
        "INSERT INTO users(id, email, display_name, role, created_at) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET role = excluded.role",
        (user.user_id, f"user-{user.user_id}@local", f"User {user.user_id}", user.role.value, now_iso()),
    )


def request_from_row(row: sqlite3.Row) -> dict:
    return dict(row)


def audit_from_row(row: sqlite3.Row) -> dict:
    return dict(row)