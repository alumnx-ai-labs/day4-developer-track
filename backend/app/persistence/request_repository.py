from __future__ import annotations

import sqlite3

from .repositories import audit_from_row, now_iso, request_from_row


class RequestRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create(self, values: dict) -> dict:
        cursor = self.connection.execute(
            "INSERT INTO work_requests(title, description, category, priority, status, created_at, created_by_id) "
            "VALUES (:title, :description, :category, :priority, :status, :created_at, :created_by_id)",
            values | {"created_at": now_iso()},
        )
        return self.get(cursor.lastrowid)

    def get(self, request_id: int) -> dict | None:
        row = self.connection.execute("SELECT * FROM work_requests WHERE id = ?", (request_id,)).fetchone()
        return request_from_row(row) if row else None

    def list(self, visibility_sql: str, params: tuple, filters: dict) -> list[dict]:
        clauses = [visibility_sql]
        values = list(params)
        for field in ("status", "priority", "category"):
            if filters.get(field) is not None:
                clauses.append(f"{field} = ?")
                values.append(filters[field])
        if filters.get("assignee_id") is not None:
            clauses.append("assigned_to_id = ?")
            values.append(filters["assignee_id"])
        rows = self.connection.execute(
            f"SELECT * FROM work_requests WHERE {' AND '.join(clauses)} ORDER BY id DESC", values
        ).fetchall()
        return [request_from_row(row) for row in rows]

    def update_field(self, request_id: int, field: str, value: str | int | None) -> dict:
        self.connection.execute(f"UPDATE work_requests SET {field} = ? WHERE id = ?", (value, request_id))
        return self.get(request_id)

    def history(self, request_id: int) -> list[dict]:
        rows = self.connection.execute(
            "SELECT * FROM request_audit_events WHERE request_id = ? ORDER BY id ASC", (request_id,)
        ).fetchall()
        return [audit_from_row(row) for row in rows]