from enum import StrEnum


class Role(StrEnum):
    REQUESTER = "requester"
    ASSIGNEE = "assignee"
    TEAM_LEAD = "team_lead"
    APPROVER = "approver"
    ADMIN = "admin"


class Category(StrEnum):
    FEATURE = "feature"
    BUG = "bug"
    TECHNICAL_DEBT = "technical_debt"
    INCIDENT = "incident"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RequestStatus(StrEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AuditEventType(StrEnum):
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    OWNER_CHANGED = "owner_changed"
    CATEGORY_CHANGED = "category_changed"