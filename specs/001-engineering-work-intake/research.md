# Research: TeamPulse Work Intake

## Decision: Explicit lifecycle and role model

**Decision**: TeamPulse will use a constrained workflow lifecycle of `Open -> Assigned -> In Progress -> Resolved -> Closed` with role-based authorization enforced at the API layer.

**Rationale**:
- The clarified specification requires explicit state transitions and auditable change events.
- A limited lifecycle reduces ambiguity and supports deterministic workflow tests.
- Role-based authorization prevents unauthorized mutation of priority and status while still enabling team members to act on assigned work.

**Alternatives considered**:
- Freeform status strings: rejected because it creates inconsistent workflows and weak validation.
- Admin-only status changes: rejected because it slows normal operational work and does not match team-led execution.
- Audit trail as mutable metadata: rejected because it weakens traceability and violates the immutable audit requirement.

## Decision: Split responsibilities by layer

**Decision**: The repository will separate API, application, domain, and persistence layers.

**Rationale**:
- The constitution requires clear boundaries and testable business rules.
- Separation makes workflow and authorization policy easier to validate and review independently.
- It also supports future growth without coupling request logic to database or HTTP concerns.

**Alternatives considered**:
- Single-layer service module: rejected because it mixes validation, database access, and API behavior.
- Frontend-only workflow state: rejected because the request model and authorization rules are business-critical and must be enforced server-side.

## Decision: Immutable audit event storage

**Decision**: Every priority, status, or owner change will create an immutable audit event that records the old value, new value, actor, and timestamp.

**Rationale**:
- The requirement explicitly calls for traceable important changes.
- Immutable event storage is easier to defend in review and supports accountability.
- It is compatible with SQLite and REST API validation.

**Alternatives considered**:
- Overwriting request history: rejected because it destroys provenance.
- Logging only in the application layer: rejected because it is not durable enough for operational and compliance review.

## Decision: SQLite for local delivery

**Decision**: Use SQLite for local persistence, with schema constraints and foreign-key enforcement to preserve integrity.

**Rationale**:
- The project scope explicitly calls for SQLite local storage.
- SQLite is sufficient for local web app validation and supports the needed audit and relationship tables.

**Alternatives considered**:
- PostgreSQL: rejected because the architecture requirement is local and simpler than enterprise deployment.
- In-memory storage: rejected because it does not satisfy auditability or persistence requirements.

## Decision: Contract-first API design

**Decision**: Define request, response, validation, and authorization rules before implementation so the API contract is explicit and test-first.

**Rationale**:
- The constitution requires API contracts before implementation.
- Clear contracts reduce ambiguity for frontend and backend teams.
- The required test coverage for workflow transitions and authorization rules can be written against the contract model.

**Alternatives considered**:
- Let frontend assumptions drive backend behavior: rejected because it creates hidden contracts.
- Implicit field validation: rejected because it makes enforcement inconsistent.
