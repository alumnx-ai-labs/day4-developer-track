import sqlite3


class AuditRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def append(self, values: dict) -> None:
        self.connection.execute(
            "INSERT INTO request_audit_events(request_id, event_type, old_value, new_value, changed_by, changed_at, reason) "
            "VALUES (:request_id, :event_type, :old_value, :new_value, :changed_by, :changed_at, :reason)",
            values,
        )