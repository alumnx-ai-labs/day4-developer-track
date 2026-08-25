from app.application.authorization import Action, UserContext, is_allowed
from app.domain.models import AuditEventType, RequestStatus
from app.domain.workflow import can_transition
from app.persistence.repositories import ensure_user, now_iso
from app.persistence.unit_of_work import UnitOfWork


class ServiceError(Exception):
    def __init__(self, detail: str, status_code: int) -> None:
        self.detail = detail
        self.status_code = status_code


def _require_request(request: dict | None) -> dict:
    if request is None:
        raise ServiceError("Request not found", 404)
    return request


def _audit(request_id: int, event_type: AuditEventType, old: object, new: object, user_id: int) -> dict:
    return {
        "request_id": request_id,
        "event_type": event_type.value,
        "old_value": str(old),
        "new_value": str(new),
        "changed_by": user_id,
        "changed_at": now_iso(),
        "reason": None,
    }


def create_request(connection, user: UserContext, values: dict) -> dict:
    if not is_allowed(user, Action.CREATE, created_by_id=user.user_id):
        raise ServiceError("User is not allowed to create requests", 403)
    with UnitOfWork(connection) as unit:
        ensure_user(connection, user)
        values = values | {"status": RequestStatus.OPEN.value, "created_by_id": user.user_id}
        return unit.requests.create(values)


def mutate_request(connection, user: UserContext, request_id: int, field: str, value: object, event: AuditEventType) -> dict:
    with UnitOfWork(connection) as unit:
        ensure_user(connection, user)
        request = _require_request(unit.requests.get(request_id))
        action = {
            "status": Action.UPDATE_STATUS,
            "priority": Action.UPDATE_PRIORITY,
            "category": Action.UPDATE_CATEGORY,
            "assigned_to_id": Action.UPDATE_OWNER,
        }[field]
        if not is_allowed(user, action, created_by_id=request["created_by_id"], assigned_to_id=request["assigned_to_id"]):
            raise ServiceError("User is not allowed to update this request", 403)
        if field == "status":
            current = RequestStatus(request["status"])
            requested = RequestStatus(value)
            if not can_transition(current, requested):
                raise ServiceError("Invalid status transition", 409)
            if requested == RequestStatus.ASSIGNED and request["assigned_to_id"] is None:
                raise ServiceError("An owner is required before assignment", 409)
        if field == "assigned_to_id":
            connection.execute(
                "INSERT INTO users(id, email, display_name, role, created_at) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO NOTHING",
                (value, f"user-{value}@local", f"User {value}", "assignee", now_iso()),
            )
            if request["status"] == RequestStatus.CLOSED.value:
                raise ServiceError("Closed requests cannot be reassigned", 409)
            if request["status"] == RequestStatus.OPEN.value:
                unit.requests.update_field(request_id, "status", RequestStatus.ASSIGNED.value)
                unit.audit.append(_audit(request_id, AuditEventType.STATUS_CHANGED, RequestStatus.OPEN.value, RequestStatus.ASSIGNED.value, user.user_id))
        old_value = request[field]
        unit.requests.update_field(request_id, field, value)
        unit.audit.append(_audit(request_id, event, old_value, value, user.user_id))
        return unit.requests.get(request_id)


def get_visible(connection, user: UserContext, request_id: int) -> dict:
    request = _require_request(connection.execute("SELECT * FROM work_requests WHERE id = ?", (request_id,)).fetchone())
    request = dict(request)
    if not is_allowed(user, Action.VIEW, created_by_id=request["created_by_id"], assigned_to_id=request["assigned_to_id"]):
        raise ServiceError("User cannot view this request", 403)
    return request