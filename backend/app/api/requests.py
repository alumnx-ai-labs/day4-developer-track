from fastapi import APIRouter, Depends, Query

from app.application.authorization import Action, Role, UserContext, is_allowed
from app.application.request_service import ServiceError, create_request, get_visible, mutate_request
from app.domain.models import AuditEventType, Category, Priority, RequestStatus
from app.persistence.repositories import ensure_user
from app.persistence.request_repository import RequestRepository
from app.persistence.unit_of_work import UnitOfWork

from .dependencies import get_connection, get_current_user
from .schemas import AuditResponse, CategoryUpdate, OwnerUpdate, PriorityUpdate, RequestCreate, RequestResponse, StatusUpdate

router = APIRouter(prefix="/requests", tags=["requests"])


def _envelope(data):
    return {"data": data, "error": None, "request_id": None}


def _handle(error: ServiceError):
    from fastapi import HTTPException
    raise HTTPException(status_code=error.status_code, detail=error.detail)


@router.post("", response_model=dict, status_code=201)
def create(payload: RequestCreate, user: UserContext = Depends(get_current_user), connection=Depends(get_connection)):
    try:
        return _envelope(create_request(connection, user, payload.model_dump(mode="json")))
    except ServiceError as error:
        _handle(error)


def _list_visible(connection, user, filters):
    ensure_user(connection, user)
    if user.role in {Role.TEAM_LEAD, Role.APPROVER, Role.ADMIN}:
        sql, params = "1 = 1", ()
    elif user.role == Role.REQUESTER:
        sql, params = "created_by_id = ?", (user.user_id,)
    else:
        sql, params = "assigned_to_id = ?", (user.user_id,)
    return RequestRepository(connection).list(sql, params, filters)


@router.get("", response_model=dict)
def list_requests(
    status: RequestStatus | None = Query(None), priority: Priority | None = Query(None),
    assignee_id: int | None = Query(None), category: Category | None = Query(None),
    user: UserContext = Depends(get_current_user), connection=Depends(get_connection),
):
    values = {"status": status.value if status else None, "priority": priority.value if priority else None,
              "assignee_id": assignee_id, "category": category.value if category else None}
    return _envelope(_list_visible(connection, user, values))


@router.get("/{request_id}", response_model=dict)
def get_request(request_id: int, user: UserContext = Depends(get_current_user), connection=Depends(get_connection)):
    try:
        return _envelope(get_visible(connection, user, request_id))
    except ServiceError as error:
        _handle(error)


def _mutation(request_id, user, connection, field, value, event):
    try:
        return _envelope(mutate_request(connection, user, request_id, field, value, event))
    except ServiceError as error:
        _handle(error)


@router.patch("/{request_id}/owner", response_model=dict)
def owner(request_id: int, payload: OwnerUpdate, user: UserContext = Depends(get_current_user), connection=Depends(get_connection)):
    return _mutation(request_id, user, connection, "assigned_to_id", payload.assigned_to_id, AuditEventType.OWNER_CHANGED)


@router.patch("/{request_id}/status", response_model=dict)
def status(request_id: int, payload: StatusUpdate, user: UserContext = Depends(get_current_user), connection=Depends(get_connection)):
    return _mutation(request_id, user, connection, "status", payload.status.value, AuditEventType.STATUS_CHANGED)


@router.patch("/{request_id}/priority", response_model=dict)
def priority(request_id: int, payload: PriorityUpdate, user: UserContext = Depends(get_current_user), connection=Depends(get_connection)):
    return _mutation(request_id, user, connection, "priority", payload.priority.value, AuditEventType.PRIORITY_CHANGED)


@router.patch("/{request_id}/category", response_model=dict)
def category(request_id: int, payload: CategoryUpdate, user: UserContext = Depends(get_current_user), connection=Depends(get_connection)):
    return _mutation(request_id, user, connection, "category", payload.category.value, AuditEventType.CATEGORY_CHANGED)


@router.get("/{request_id}/history", response_model=dict)
def history(request_id: int, user: UserContext = Depends(get_current_user), connection=Depends(get_connection)):
    try:
        get_visible(connection, user, request_id)
        return _envelope(RequestRepository(connection).history(request_id))
    except ServiceError as error:
        _handle(error)