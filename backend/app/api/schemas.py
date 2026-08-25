from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.models import Category, Priority, RequestStatus


class RequestCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: Category
    priority: Priority
    status: RequestStatus

    @field_validator("title", "description")
    @classmethod
    def require_meaningful_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class StatusUpdate(BaseModel):
    status: RequestStatus


class PriorityUpdate(BaseModel):
    priority: Priority


class CategoryUpdate(BaseModel):
    category: Category


class OwnerUpdate(BaseModel):
    assigned_to_id: int = Field(gt=0)


class RequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: Category
    priority: Priority
    status: RequestStatus
    created_at: str
    created_by_id: int
    assigned_to_id: int | None = None


class AuditResponse(BaseModel):
    id: int
    request_id: int
    event_type: str
    old_value: str
    new_value: str
    changed_by: int
    changed_at: str
    reason: str | None = None