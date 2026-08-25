from dataclasses import dataclass
from enum import StrEnum

from app.domain.models import Role


class Action(StrEnum):
    CREATE = "create"
    VIEW = "view"
    UPDATE_STATUS = "update_status"
    UPDATE_OWNER = "update_owner"
    UPDATE_PRIORITY = "update_priority"
    UPDATE_CATEGORY = "update_category"


@dataclass(frozen=True)
class UserContext:
    user_id: int
    role: Role


def is_allowed(
    user: UserContext,
    action: Action,
    *,
    created_by_id: int | None = None,
    assigned_to_id: int | None = None,
) -> bool:
    if user.role == Role.ADMIN:
        return True
    if action == Action.CREATE:
        return user.role in {Role.REQUESTER, Role.TEAM_LEAD} and (
            created_by_id is None or created_by_id == user.user_id
        )
    if action == Action.VIEW:
        return user.role in {Role.TEAM_LEAD, Role.APPROVER} or user.user_id in {
            created_by_id,
            assigned_to_id,
        }
    if action == Action.UPDATE_STATUS:
        return user.role == Role.TEAM_LEAD or (
            user.role == Role.ASSIGNEE and assigned_to_id == user.user_id
        )
    if action == Action.UPDATE_OWNER:
        return user.role == Role.TEAM_LEAD
    if action == Action.UPDATE_PRIORITY:
        return user.role in {Role.TEAM_LEAD, Role.APPROVER}
    if action == Action.UPDATE_CATEGORY:
        return user.role == Role.TEAM_LEAD
    return False