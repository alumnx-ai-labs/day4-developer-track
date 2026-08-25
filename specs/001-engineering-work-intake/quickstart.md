# TeamPulse Quickstart

## Prerequisites

- Python 3.12+
- Node.js 20+
- npm or pnpm
- SQLite available locally

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## Validation scenarios

1. Create a request with a valid feature request payload.
2. Verify the request appears in the list with required metadata.
3. Update the request status to `assigned` and then to `in_progress`.
4. Attempt an invalid transition such as `open -> resolved` and confirm it fails with `409 Conflict`.
5. Change request priority as a team lead and confirm an immutable audit event is created.
6. Attempt a priority change as a non-authorized user and confirm `403 Forbidden`.
7. Open request history and verify that status, priority, and owner changes are visible with prior values retained.
8. Reassign the owner and confirm the new assignee is reflected and recorded in history.

## Expected outcomes

- Request creation succeeds for authorized users.
- Workflow transitions follow the defined lifecycle.
- Unauthorized updates are rejected.
- Audit history captures all important changes with before/after values.
- The API contract matches the documented endpoints and data model.
