# AGENTS.md

## Project Overview
- **DVDRentalSystem** is a production-grade backend for a DVD rental system, built with FastAPI and async SQLAlchemy 2.x, covering all 15 tables of the PostgreSQL `dvdrental` sample DB.
- The architecture is cleanly layered: API routers → Service layer (business logic) → SQLAlchemy ORM → asyncpg driver → PostgreSQL.
- All API endpoints are versioned under `/api/v1` and require Bearer token authentication (OIDC via Keycloak, PKCE flow).

## Key Directories & Files
- `app/main.py`: App entrypoint, lifespan, middleware, router registration.
- `app/core/`: Core config, async DB engine/session, security.
- `app/models/models.py`: All ORM models (one file, 15 tables).
- `app/schemas/`: Pydantic schemas, organized by domain (e.g., `film.py`, `people.py`).
- `app/services/`: Business logic, each resource has a service class inheriting from `BaseService[T]` for CRUD and custom logic.
- `app/api/v1/`: Route modules per resource, aggregated in `router.py`.
- `app/exceptions/handlers.py`: Centralized exception handling (404, 409, 500).
- `tests/`: End-to-end API tests using `httpx.AsyncClient` (no server needed, real DB required).

## Patterns & Conventions
- **Async everywhere**: All DB and API operations are async.
- **Dependency injection**: Use `Annotated[AsyncSession, Depends(get_db)]` for DB session in routers.
- **Pagination**: All list endpoints accept `page` and `size` query params, return a unified paged response.
- **Service layer**: All business logic (including complex queries, transactions) is in `app/services/`, not routers.
- **Exception handling**: Use custom handlers for 404, 409 (business or DB constraint), and generic 500 errors.
- **Schema organization**: Pydantic schemas are grouped by domain, not by endpoint.
- **API versioning**: All endpoints are under `/api/v1`.
- **Auth**: OIDC (Keycloak) with PKCE, tokens exchanged and refresh handled via `/api/v1/auth/*` endpoints.

## Developer Workflows
- **Install**: `pip install -r requirements.txt`
- **Run (dev)**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- **Run (prod)**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
- **Test**: `pytest tests/ -v` (all 15 API tests must pass)
- **Coverage**: `pytest tests/ --cov=app --cov-report=term-missing`
- **DB migration**: `alembic revision --autogenerate -m "msg"` then `alembic upgrade head`
- **Docker**: `docker compose up -d --build` (full stack, including DB)
- **Keycloak**: See README for local setup; endpoints require valid Bearer token.

## Integration Points
- **PostgreSQL**: All data via asyncpg, schema matches `dvdrental` sample.
- **Keycloak**: OIDC for authentication, PKCE flow, refresh via cookies.
- **Docker**: Compose files for full stack or host-DB only; DB dump auto-imported on first run.

## Project-Specific Advice for AI Agents
- Always use async DB/session patterns and inject dependencies via FastAPI's `Depends`.
- Place all business logic in the service layer, not in routers.
- Use and extend `BaseService[T]` for CRUD and custom resource logic.
- Follow the domain-based schema organization for new models.
- Register new routers in `app/api/v1/router.py`.
- For new DB tables, update `models.py`, create schemas, service, and router modules accordingly.
- Use the provided pagination and error handling patterns for consistency.
- Reference the README for full API, DB, and deployment details.

