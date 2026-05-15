# Local Development

This guide covers a fresh local clone of `ops-platform`.

## Fresh Clone Setup

From the repository root:

```powershell
cd C:\dev\web_dev\project05_ops_platform
```

Create local environment files from the checked-in examples:

```powershell
Copy-Item frontend\.env.example frontend\.env.local
Copy-Item backend\.env.example backend\.env
```

The `.env` files are intentionally ignored by git. They hold local-only settings and secrets, so new clones need to create them from the examples.

## Docker Startup

Start the local stack:

```powershell
docker compose up --build
```

Run migrations:

```powershell
docker compose exec backend alembic upgrade head
```

Seed local demo/login data:

```powershell
docker compose exec backend python scripts/seed_dev_data.py
```

## Local URLs

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Backend Swagger: `http://localhost:8000/docs`

## Demo Mode

The demo workspace route is only registered when demo mode is enabled.

For Docker Compose, demo mode defaults to enabled through:

```yaml
DEMO_MODE_ENABLED: ${DEMO_MODE_ENABLED:-true}
DEMO_SESSION_TTL_HOURS: ${DEMO_SESSION_TTL_HOURS:-24}
```

For non-Docker backend development, set this in `backend\.env` when you need demo sessions:

```text
DEMO_MODE_ENABLED=true
DEMO_SESSION_TTL_HOURS=24
```

## Troubleshooting

If `POST /demo/sessions` returns `404`, demo mode is probably disabled for the running backend process. Set `DEMO_MODE_ENABLED=true`, restart the backend, and try again.
