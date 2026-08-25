# Tasks: TeamPulse Work Intake and Tracking

**Input**: Design documents from `/specs/001-engineering-work-intake/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Automated tests are explicitly requested for workflow transitions and authorization rules.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: can run in parallel with other tasks in the same phase
- **[Story]**: maps to US1, US2, or US3 for user-story phases
- Exact file paths are included in each task description

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the project structure and shared tooling needed by the backend and frontend.

- [X] T001 Create repository structure for backend and frontend projects per implementation plan in `backend/` and `frontend/`
- [X] T002 Initialize FastAPI backend dependencies and app skeleton in `backend/requirements.txt` and `backend/app/main.py`
- [X] T003 Initialize React + TypeScript frontend project and Vite configuration in `frontend/package.json` and `frontend/vite.config.ts`
- [ ] T004 [P] Configure backend test tooling and linting in `backend/pytest.ini`, `backend/requirements.txt`, and `backend/tests/`
- [ ] T005 [P] Configure frontend test tooling and linting in `frontend/package.json` and `frontend/tests/`
- [ ] T006 [P] Configure SQLite connection settings and environment defaults in `backend/app/config.py` and `backend/app/persistence/database.py`
- [X] T007 [P] Establish the initial API versioning, compatibility, and migration policy in `specs/001-engineering-work-intake/contracts/work-request-api.md` and `specs/001-engineering-work-intake/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared domain, persistence, authorization, and API building blocks before any user story work begins.

**Critical checkpoint**: No user story work can start until the foundational layer is complete.

- [X] T008 Define domain entities and enums for users, requests, and audit events in `backend/app/domain/`
- [X] T009 Implement the workflow state machine and transition validation in `backend/app/domain/workflow.py`
- [X] T010 Implement authorization policy, authenticated-user context, request-scoped visibility, and role checks for requester, assignee, team_lead, approver, and admin in `backend/app/application/authorization.py`
- [X] T011 [P] Create API schemas and validation models in `backend/app/api/schemas.py`
- [X] T012 [P] Implement persistence layer setup and SQLite migrations/schema creation in `backend/app/persistence/database.py` and `backend/app/persistence/repositories.py`
- [X] T013 [P] Build shared API app bootstrap and router registration in `backend/app/main.py` and `backend/app/api/router.py`
- [X] T014 Create request service foundation and repository interfaces in `backend/app/application/request_service.py` and `backend/app/persistence/request_repository.py`

---

## Phase 3: User Story 1 - Submit a new engineering work request (Priority: P1) 🎯 MVP

**Goal**: Enable authorized users to create requests, persist the initial request metadata, and display them in the intake queue.

**Independent Test**: An authorized user can create a valid request and verify it appears in the active work queue with the correct metadata and defaults.

### Tests for User Story 1

- [ ] T015 [P] [US1] Add failing contract test for `POST /api/v1/requests` and `GET /api/v1/requests` in `backend/tests/contract/test_request_contract.py`
- [ ] T016 [P] [US1] Add failing integration tests for valid creation, required-field validation, forced `open` status, and unauthorized creation in `backend/tests/integration/test_request_creation.py`

### Implementation for User Story 1

- [X] T017 [US1] Implement `WorkRequest` entity and request creation validation in `backend/app/domain/work_request.py`
- [X] T018 [US1] Implement create-request application logic and persistence flow in `backend/app/application/request_service.py`
- [X] T019 [US1] Implement `POST /api/v1/requests` and `GET /api/v1/requests` endpoints with authenticated request-scoped visibility in `backend/app/api/requests.py`
- [X] T020 [US1] Persist request records and created timestamp metadata in `backend/app/persistence/request_repository.py`
- [X] T021 [US1] Add request form component and backlog list view in `frontend/src/components/RequestForm.tsx` and `frontend/src/pages/RequestQueuePage.tsx`
- [X] T022 [US1] Add request API client and POST/GET wiring in `frontend/src/services/requestApi.ts`
- [ ] T023 [US1] Validate the request submission workflow end-to-end against the defined intake requirements in `backend/tests/integration/test_request_creation.py` and `frontend/tests/unit/RequestForm.test.tsx`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Update a request as work changes (Priority: P1)

**Goal**: Allow authorized status and priority updates while enforcing explicit transitions and recording immutable audit entries.

**Independent Test**: An authorized user can change status or priority on an existing request and an unauthorized user cannot, while invalid transitions are rejected.

### Tests for User Story 2

- [ ] T024 [P] [US2] Add failing workflow tests for only the linear transitions `open -> assigned -> in_progress -> resolved -> closed` and rejection of shortcuts/backward moves in `backend/tests/unit/test_workflow_transitions.py`
- [ ] T025 [P] [US2] Add failing authorization tests for status, priority, ownership, category, create, and request-scoped visibility across all roles in `backend/tests/unit/test_authorization_rules.py`
- [ ] T026 [P] [US2] Add failing integration tests for status, priority, and category mutation behavior, invalid transitions, and denied mutations in `backend/tests/integration/test_status_priority_updates.py`

### Implementation for User Story 2

- [ ] T027 [US2] Implement permission checks for assignee, team lead, approver, and admin action scope in `backend/app/application/authorization.py`
- [ ] T028 [US2] Enforce the linear lifecycle and reject undefined, shortcut, and backward transitions in `backend/app/domain/workflow.py`
- [ ] T029 [US2] Implement PATCH endpoints for status, priority, and category with explicit `403`, `400`, and `409` error behavior in `backend/app/api/requests.py`
- [ ] T030 [US2] Record immutable audit events for status, priority, owner, and category changes with atomic request/audit persistence in `backend/app/persistence/audit_repository.py` and `backend/app/persistence/unit_of_work.py`
- [ ] T031 [US2] Add status and priority update controls to the request detail UI in `frontend/src/components/RequestDetail.tsx` and `frontend/src/pages/RequestDetailPage.tsx`
- [ ] T032 [US2] Wire frontend mutation requests to the API in `frontend/src/services/requestApi.ts`
- [ ] T033 [US2] Validate workflow, authorization, atomic audit writes, and unchanged state after denied or failed mutations in `backend/tests/unit/test_workflow_transitions.py`, `backend/tests/unit/test_authorization_rules.py`, and `backend/tests/integration/test_status_priority_updates.py`

**Checkpoint**: User Story 2 is independently functional and protected by workflow validation.

---

## Phase 5: User Story 3 - Review request history and assignment information (Priority: P2)

**Goal**: Make important request changes traceable, ownership visible, and history reviewable without exposing unrelated internal details.

**Independent Test**: A user can open a request and review the chronological audit trail and current assignee for the request.

### Tests for User Story 3

- [ ] T034 [P] [US3] Add failing history endpoint tests for chronological request-scoped results and forbidden unrelated history in `backend/tests/integration/test_request_history.py`
- [ ] T035 [P] [US3] Add frontend unit tests for rendering history and assignment details in `frontend/tests/unit/RequestHistory.test.tsx`

### Implementation for User Story 3

- [ ] T036 [US3] Implement request history retrieval and owner reassignment endpoint logic in `backend/app/api/requests.py`
- [ ] T037 [US3] Persist and retrieve immutable audit events for status, priority, owner, and category changes in `backend/app/persistence/request_repository.py` and `backend/app/persistence/audit_repository.py`
- [ ] T038 [US3] Add request detail history timeline and assignee display in `frontend/src/components/RequestHistory.tsx` and `frontend/src/components/RequestDetail.tsx`
- [ ] T039 [US3] Extend the API client and state model for history data in `frontend/src/services/requestApi.ts` and `frontend/src/types/request.ts`
- [ ] T040 [US3] Verify audit chronology, ownership visibility, category history, append-only enforcement, and related history semantics in `backend/tests/integration/test_request_history.py` and `backend/tests/integration/test_audit_immutability.py`

**Checkpoint**: User Stories 1-3 are independently functional and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final project hardening, validation, and documentation for the end-to-end TeamPulse workflow.

- [ ] T041 [P] Review and refine API error handling and consistent HTTP status codes in `backend/app/api/`
- [ ] T042 [P] Add endpoint performance measurement and verify the 500 ms p95 target for request list and history responses in `backend/tests/integration/test_performance.py`
- [ ] T043 [P] Add or update quickstart validation steps in `specs/001-engineering-work-intake/quickstart.md`
- [ ] T044 [P] Run the backend test suite covering workflow transitions, authorization, visibility, performance, and audit history in `backend/tests/`
- [ ] T045 [P] Run frontend unit and integration checks for request creation, status updates, category updates, and history rendering in `frontend/tests/`
- [ ] T046 Validate the requested MVP flow from intake through assignment, status change, priority/category update, and history review against the spec in `specs/001-engineering-work-intake/spec.md`
- [ ] T047 Perform final cleanup, code review pass, and release-readiness check for TeamPulse in `backend/app/` and `frontend/src/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; starts immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user story work.
- **User Story 1 (Phase 3)**: Depends on Phase 2; delivers the MVP intake flow.
- **User Story 2 (Phase 4)**: Depends on Phase 2 and can begin after Phase 3 starts, but should be independently testable.
- **User Story 3 (Phase 5)**: Depends on Phase 2 and can proceed once request lifecycle and audit capability are in place.
- **Polish (Phase 6)**: Depends on all desired story tasks being complete.

### User Story Dependencies

- **US1**: No dependency on the other user stories; it is the entry point for intake and visibility.
- **US2**: Builds on the request model, status workflow, and authorization checks from US1.
- **US3**: Depends on the request lifecycle and audit event framework from US1 and US2.

### Parallel Opportunities

- Setup tasks T004-T006 can run in parallel.
- Foundational tasks T010-T013 can proceed in parallel where file ownership is distinct.
- Workflow, authorization, and contract tests T023-T025 can run in parallel before implementation.
- Story tests within a single phase are parallelizable when they target different files.
- UI and API work for a story can be split across developers once the contract is stable.

---

## Parallel Example: Story Delivery

```bash
# Work on User Story 1 in parallel once foundational tasks are complete
# Backend contract tests for `/api/v1/requests`: T015
# Backend integration tests: T015
# Frontend form + queue integration: T020-T021
```

---

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational tasks.
2. Deliver User Story 1 only and validate create-request flow.
3. Stop and confirm that the intake queue, API, and data model work correctly.
4. Add User Story 2 and validate state machine and authorization enforcement.
5. Add User Story 3 and confirm request history and assignment views are correct.

### Incremental Delivery

1. Setup + Foundational -> stable platform foundation.
2. US1 -> request intake and visibility.
3. US2 -> controlled updates and audit trail.
4. US3 -> traceability and reviewability.
5. Polish -> final hardening and documentation.

---

## Notes

- All tasks follow the required checklist format: checkbox, ID, optional [P], and required story label for story phases.
- Test tasks are written before implementation for each story to satisfy the TDD requirement.
- File paths are explicit and scoped to the TeamPulse backend/frontend structure from the plan.
- Invalid transitions, unauthorized mutations, and immutable history requirements are treated as first-class acceptance criteria.
