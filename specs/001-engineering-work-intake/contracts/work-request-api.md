# Work Request API Contract

## Overview

The TeamPulse API exposes request lifecycle operations for engineering intake. All endpoint behavior is enforced through role-based authorization and persisted audit history.

## Authentication and Authorization

- Authenticated users are required for all endpoints.
- `requester`: can create requests and view requests they created.
- `assignee`: can update status for assigned requests and view assigned requests.
- `team_lead`: can update status, assign owners, and change priority for team requests.
- `approver`: can change priority and view team requests, but cannot change status or ownership.
- `admin`: can manage all requests and override workflow policy when explicitly permitted.
- Unauthorized changes are rejected with `403 Forbidden`.

## Common Response Format

Successful responses use `{ "data": {}, "error": null, "request_id": "uuid-or-integer" }`; list endpoints place arrays inside `data`.

## Versioning and Compatibility

- The initial contract is exposed under `/api/v1/` and the unversioned `/api/` paths are not part of the public compatibility promise.
- Backward-incompatible changes require a new version prefix, a migration note, compatibility tests for the previous version, and a documented deprecation period.
- Additive response fields and new optional request fields are backward-compatible changes when existing required fields and error semantics remain unchanged.

Errors follow standard HTTP status codes, including `400 Bad Request`, `403 Forbidden`, `404 Not Found`, and `409 Conflict` for invalid transitions.

## Endpoints

### POST /api/v1/requests

Creates a new work request.

**Request body**
```json
{
  "title": "Fix login timeout",
  "description": "Users are timing out while token validation is pending.",
  "category": "bug",
  "priority": "high",
  "status": "open"
}
```

**Validation rules**
- `title`, `description`, `category`, `priority`, and `status` are required.
- `category` must be one of `feature`, `bug`, `technical_debt`, or `incident`.
- `priority` must be one of `low`, `medium`, `high`, or `critical`.
- `status` must be `open` at creation; later status changes use the status endpoint.
- Ownership is assigned through `PATCH /api/v1/requests/{id}/owner` and cannot be set during creation.

**Response**
```json
{
  "id": 101,
  "title": "Fix login timeout",
  "description": "Users are timing out while token validation is pending.",
  "category": "bug",
  "priority": "high",
  "status": "open",
  "created_at": "2026-08-24T10:34:22Z",
  "assigned_to_id": 42,
  "created_by_id": 7
}
```

### GET /api/v1/requests

Returns a list of requests visible to the requesting user. Requesters see requests they created, assignees see requests assigned to them, and team leads, approvers, and admins see all team requests.

**Query parameters**
- `status`
- `priority`
- `assignee_id`
- `category`

**Response**
```json
[
  {
    "id": 101,
    "title": "Fix login timeout",
    "priority": "high",
    "status": "assigned",
    "category": "bug",
    "assigned_to_id": 42
  }
]
```

### GET /api/v1/requests/{id}

Returns the request with current state.

### PATCH /api/v1/requests/{id}/priority

Updates priority for an authorized user.

**Request body**
```json
{
  "priority": "critical"
}
```

**Rules**
- Only `team_lead`, `approver`, or `admin` may change priority.
- A priority change creates an immutable audit event.
- Invalid values return `400 Bad Request`.

### PATCH /api/v1/requests/{id}/status

Updates status for an authorized user.

**Request body**
```json
{
  "status": "in_progress"
}
```

**Rules**
- Allowed transitions are `open -> assigned -> in_progress -> resolved -> closed`; no backward or shortcut transitions are valid.
- Invalid transitions return `409 Conflict`.
- A status change creates an immutable audit event.

### PATCH /api/v1/requests/{id}/owner

Assigns or reassigns the owner.

**Request body**
```json
{
  "assigned_to_id": 21
}
```

**Rules**
- Only `team_lead` or `admin` may change ownership. Assigning an open request transitions it to `assigned`.
- Ownership changes create immutable audit events.

### PATCH /api/v1/requests/{id}/category

Updates the category for an authorized team request.

**Rules**
- Only `team_lead` or `admin` may change category.
- The category must be one of `feature`, `bug`, `technical_debt`, or `incident`.
- A category change creates an immutable audit event.

### GET /api/v1/requests/{id}/history

Returns the immutable audit trail for the request.

**Response**
```json
[
  {
    "id": 331,
    "request_id": 101,
    "event_type": "status_changed",
    "old_value": "assigned",
    "new_value": "in_progress",
    "changed_by": 15,
    "changed_at": "2026-08-24T11:15:02Z"
  }
]
```

## Audit Record Contract

Every immutable audit record must include:
- `request_id`
- `event_type`
- `old_value`
- `new_value`
- `changed_by`
- `changed_at`
- optional `reason` when provided by the actor
- Audit records are append-only. Update and delete operations are not exposed and must be rejected by the persistence layer.
- The request mutation and audit insert must commit atomically; if the audit insert fails, the request mutation must not be committed.

## Error Cases

- Invalid status transition: `409 Conflict`
- Unauthorized actor: `403 Forbidden`
- Unknown request: `404 Not Found`
- Invalid payload: `400 Bad Request`
