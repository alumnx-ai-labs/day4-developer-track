from collections.abc import Generator

from fastapi import Header, HTTPException

from app.application.authorization import UserContext
from app.domain.models import Role
from app.persistence.database import Database


database = Database()


def get_current_user(
    x_user_id: int | None = Header(None), x_user_role: Role | None = Header(None)
) -> UserContext:
    if x_user_id is None or x_user_role is None:
        raise HTTPException(status_code=403, detail="X-User-Id and X-User-Role are required")
    return UserContext(user_id=x_user_id, role=x_user_role)


def get_connection() -> Generator:
    connection = database.connect()
    try:
        yield connection
    finally:
        connection.close()