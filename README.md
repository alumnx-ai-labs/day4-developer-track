
# TeamPulse

TeamPulse is an engineering work intake and tracking system. Authorized
users can create work requests (features, bugs, technical debt, or
incidents), assign them to team members, and track status and priority
changes through their lifecycle: `Open → Assigned → In Progress →
Resolved → Closed`. A history of important changes (status, priority,
assignee, category) is kept for each request so work stays visible,
structured, and traceable.

## Project structure

- `backend/` — FastAPI service (Python) exposing the `/api/v1` REST API,
  backed by a SQLite database (`team_pulse.db`).
- `frontend/` — React + TypeScript app (Vite) that consumes the API.
- `specs/` — feature specifications and planning docs.

## Prerequisites

- Python 3.12+
- Node.js 18+

## Running the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is served at `http://localhost:8000/api/v1`.

## Running the frontend

```bash
cd frontend
npm install
npm run dev
```

The app is served at `http://localhost:5173` and proxies `/api` requests
to the backend at `http://localhost:8000`.

## Running tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

