# Data Model: TeamPulse Work Intake

## Core Entities

### User

Represents an authenticated project participant with role-based access.

| Field | Type | Notes |
|---|---|---|
| id | integer | Primary key |
| email | string | Unique login identifier |
| display_name | string | Human-readable name |
| role | enum | `requester`, `assignee`, `team_lead`, `approver`, `admin` |
| created_at | datetime | Creation timestamp |

### WorkRequest

Represents an engineering work item.

| Field | Type | Notes |
|---|---|---|
| id | integer | Primary key |
| title | string | Short, descriptive request title |
| description | text | Detailed description of the work |
| category | enum | `feature`, `bug`, `technical_debt`, `incident` |
| priority | enum | `low`, `medium`, `high`, `critical` |
| status | enum | `open`, `assigned`, `in_progress`, `resolved`, `closed` |
| created_at | datetime | Immutable creation timestamp |
| created_by_id | integer | Foreign key to User |
| assigned_to_id | integer | Optional foreign key to User |

### RequestAuditEvent

Immutable audit record for important changes.

| Field | Type | Notes |
|---|---|---|
| id | integer | Primary key |
| request_id | integer | Foreign key to WorkRequest |
| event_type | string | e.g. `status_changed`, `priority_changed`, `owner_changed` |
| old_value | string | Previous value |
| new_value | string | New value |
| changed_by | integer | Foreign key to User |
| changed_at | datetime | Immutable time of change |
| reason | text | Optional justification |

## Relationships

- One `User` can create many `WorkRequest` entries.
- One `User` can be assigned many `WorkRequest` entries.
- One `WorkRequest` can have many `RequestAuditEvent` rows.
- `RequestAuditEvent` entries are append-only and cannot be updated or deleted in normal workflows.

## Validation Rules

- `WorkRequest.title` must be non-empty and trimmed.
- `WorkRequest.description` must be non-empty and meaningful.
- `WorkRequest.category` must use the approved enum values.
- `WorkRequest.priority` must use the approved enum values.
- `WorkRequest.status` must be `open` when a request is created and must follow the explicit state machine thereafter.
- `RequestAuditEvent` preserves both old and new values for every important change.

## State Transition Rules

| Current State | Allowed Next States |
|---|---|
| open | assigned |
| assigned | in_progress |
| in_progress | resolved |
| resolved | closed |
| closed | none |

Rules:
- `open` may progress to `assigned` only when a team lead or admin assigns an owner.
- `assigned` implies a designated owner has accepted or been assigned the request.
- `in_progress` indicates active engineering work is underway and cannot transition backward.
- `resolved` means the work is complete and ready for closure review.
- `closed` is terminal.
- Any undefined transition is rejected.

## Authorization Rules

- `requester`: can create new requests and view requests they created.
- `assignee`: can update status for assigned work only.
- `team_lead`: can update status, assign or reassign ownership, and update priority for team work.
- `approver`: can update priority for team work and view team requests; cannot update status or ownership.
- `admin`: can manage all requests and override standard policy where needed.
- Priority change is restricted to `team_lead`, `approver`, and `admin` roles.
- Status change is restricted to `assignee`, `team_lead`, and `admin` roles within the defined transition model.
- Ownership change is restricted to `team_lead` and `admin` roles; an ownership change from `open` to a valid assignee also performs the `open -> assigned` transition.
- Category change is restricted to `team_lead` and `admin` roles.
- Visibility is request-scoped: requesters see their own requests, assignees see assigned requests, and team leads, approvers, and admins see all team requests.

## Audit Semantics

The system records an immutable event whenever any of the following change:
- `priority`
- `status`
- `assigned_to_id`
- `category`

These events must be retained in the request history and exposed by the API history endpoint.

Audit events cannot be updated or deleted through normal persistence or API operations. A failed audit write MUST prevent the corresponding request mutation from being committed.
