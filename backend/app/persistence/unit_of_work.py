import sqlite3

from .audit_repository import AuditRepository
from .request_repository import RequestRepository


class UnitOfWork:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.requests = RequestRepository(connection)
        self.audit = AuditRepository(connection)

    def __enter__(self) -> "UnitOfWork":
        self.connection.execute("BEGIN")
        return self

    def __exit__(self, exception_type, exception, traceback) -> None:
        if exception_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()