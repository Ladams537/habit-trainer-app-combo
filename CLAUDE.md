# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A unified personal training and habit tracking web application. Combines fitness workout logging, habit tracking (with Loop-style strength scores), and planned skills/practice modules in a single adaptive interface. See `training_app.md` for the full design document.

## Tech Stack

- **Frontend**: SvelteKit (Svelte 5 with runes) + Tailwind CSS v4 + shadcn-svelte (bits-ui) + ECharts
- **Backend**: FastAPI (Python 3.12+) + SQLAlchemy 2.0 async + Alembic
- **Database**: PostgreSQL 16 (via Docker, exposed on port 5433)
- **Package management**: uv (backend), npm (frontend)

## Common Commands

### Full stack (Docker)
```bash
docker compose up              # Start all services (postgres, backend, frontend)
docker compose up -d postgres  # Start just the database
```

### Backend (from `backend/`)
```bash
uv run uvicorn src.main:app --reload              # Dev server on :8000
uv run alembic upgrade head                        # Run migrations
uv run alembic revision --autogenerate -m "msg"    # Create migration
uv run pytest                                      # Run all tests
uv run pytest tests/test_habits_logic.py           # Run single test file
uv run pytest tests/test_habits_logic.py::TestComputeStreaks::test_gap_in_middle  # Single test
uv run ruff check src/                             # Lint
uv run ruff format src/                            # Format
```

### Frontend (from `frontend/`)
```bash
npm run dev          # Dev server on :5173
npm run build        # Production build
npm run check        # Svelte type checking
```

## Architecture

### Backend: Modular monolith

```
backend/src/
├── main.py              # FastAPI app factory, seeds exercises on startup
├── config.py            # Pydantic Settings (reads env vars / .env)
├── api/
│   ├── router.py        # Mounts all module routers
│   ├── dependencies.py  # DB (async session) and CurrentUser (JWT auth) deps
│   └── middleware.py     # CORS setup
├── modules/
│   ├── auth/            # JWT auth (register, login, refresh, me)
│   ├── habits/          # Habit CRUD, completions, streak/strength algorithms
│   ├── fitness/         # Exercises, templates, sessions, sets, progression stats
│   └── analytics/       # (Placeholder, not yet implemented)
└── shared/
    ├── database.py      # Async engine + session factory (auto-commit/rollback)
    ├── base_models.py   # Base, UUIDMixin, TimestampMixin
    ├── auth.py          # JWT encode/decode helpers
    └── utils.py
```

Each module follows the pattern: `models.py` (SQLAlchemy) → `schemas.py` (Pydantic) → `service.py` (business logic) → `routes.py` (FastAPI endpoints). Services are instantiated per-request with the DB session: `service = FitnessService(db)`.

**Key dependency injection**: `DB` = async SQLAlchemy session, `CurrentUser` = authenticated user via JWT. Import from `src.api.dependencies`.

**API prefixes**: `/api/auth/`, `/api/habits/`, `/api/fitness/`

### Frontend: SvelteKit with server-side API proxying

All API calls go through SvelteKit's server-side `+page.server.ts` load functions and form actions, not directly from the browser. The `$lib/api/client.ts` module (`apiFetch`) handles requests from server to backend using the `API_URL` env var (defaults to `http://localhost:8000`).

**Auth flow**: JWT tokens stored in httpOnly cookies. `hooks.server.ts` validates/refreshes tokens on every request, populating `event.locals.user` and `event.locals.token`. The `(app)` route group requires authentication via its `+layout.server.ts`.

**Route structure**:
- `/login`, `/register` — public auth pages
- `/(app)/today` — daily dashboard (habits checklist + workout start/resume)
- `/(app)/habits/` — habit management (list, create, detail)
- `/(app)/plan/` — workout templates (list, create, edit)
- `/(app)/workout` — active workout session logging
- `/(app)/analytics/` — fitness stats, exercise progression charts

**UI components**: shadcn-svelte components in `$lib/components/ui/`, custom layout components in `$lib/components/layout/` (AppShell, BottomNav, Sidebar). Domain components in `$lib/components/habits/` and `$lib/components/fitness/`.

### Database

PostgreSQL on Docker port 5433 (maps to internal 5432). Credentials: `trainer/trainer`, database `trainer_db`.

Alembic migrations are in `backend/alembic/versions/`. The `env.py` imports all models to register them with Base.metadata — **new models must be imported there** for autogenerate to detect them.

### Environment Variables

Backend reads from env or `.env` file: `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_ORIGINS`, `ENVIRONMENT`.
Frontend reads: `PUBLIC_API_URL` (browser-visible), `API_URL` (server-side, for SSR requests to backend).

## Known Gotcha: PostgreSQL DISTINCT/ORDER BY

When using `DISTINCT` with `ORDER BY` in PostgreSQL queries via SQLAlchemy, the ORDER BY columns must appear in the SELECT list. This has caused bugs before (commit c098097). Use subqueries or `DISTINCT ON` instead.
