<h1 align="center">Codebase FastAPI</h1>

Backend skeleton built with FastAPI. It applies event-listener driven development, queue processing, realtime WebSocket, scheduled tasks, and caching, with RESTful design, SOLID, dependency injection, the repository pattern, and DTOs.

It shares one REST contract and the same realtime events with Codebase Nest and Codebase Laravel, so Codebase Nuxt and Codebase Next work with any of them.

## Conventions

| Topic | Rule |
|-------|------|
| Brand | Codebase. Primary `#2563eb`, secondary `#84cc16`, tertiary `#1e3a8a` |
| Roles | `superadmin`, `admin`, `user` |
| Format | Indent 4, double quotes, trailing commas, space before `(`. Keep docstrings |
| Layers | Controller, service, repository. Validator DTO in, transformer DTO out. Events and listeners for side effects |
| Validation | HTTP 422 `{ "detail": [{ "type", "loc", "msg", "input", "ctx" }] }` |
| Errors | `{ "detail": "..." }` |
| Locales | `en`, `id`, `ms` |
| GraphQL | Not mounted |
| Mongo | Off when `DATABASE_MONGO_URI` is empty |
| Rate limits | Production only |

Cursor rules live in `.cursor/rules/`.

## Features

| Feature | Technology |
|---------|------------|
| REST API with Swagger | FastAPI |
| JWT access and refresh tokens | python-jose |
| Realtime | python-socketio |
| Queue | RQ + Redis |
| Scheduled tasks | APScheduler |
| Database | SQLModel + Alembic + PostgreSQL |
| Import and export (CSV, XLS, XLSX) | pandas + openpyxl |
| Notifications and Web Push | pywebpush |
| Email | aiosmtplib + Jinja2 |
| Internationalization | `en`, `id`, `ms` |
| Tests | pytest + HTTPX |

## Getting Started

### Requirements

- Python 3.10+
- Poetry 1.8+
- PostgreSQL 14+
- Redis 7+

### Setup

```bash
poetry install
cp .env.example .env
poetry run python3 ./src/cli.py secret
poetry run python3 ./src/cli.py migrate:up
poetry run python3 ./src/cli.py v1:user:seed
```

Put the generated secret in `APP_SECRET`. The seeder creates `superuser@{APP_EMAIL_SERVER}` with password `12345678`.

The `ml` group (scikit-learn, keras, transformers, scrapy) is optional. Install it with `poetry install --with ml`.

### Configuration

| Variable | Description |
|----------|-------------|
| `APP_SECRET` | Encryption and JWT signing key |
| `APP_ENV` | `production` turns on rate limits |
| `FRONTEND_URL` | Base URL for signed links in emails |
| `CORS_ORIGIN` | Allowed origins as a JSON array |
| `DATABASE_POSTGRE_URI` | PostgreSQL connection |
| `DATABASE_MONGO_URI` | Optional MongoDB connection |
| `MEMORY_REDIS_*` | Redis for cache, queue, and Socket.IO |
| `MAIL_URI` | SMTP connection |
| `VAPID_*` | Optional Web Push keys (`npx web-push generate-vapid-keys`) |

### Run

| Command | Description |
|---------|-------------|
| `poetry run fastapi dev` | Development server on `http://localhost:8000` |
| `poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4` | Production server |
| `poetry run python3 ./src/cli.py queue:work` | Queue worker for import and export |

Swagger UI: `http://localhost:8000/api/docs`

## Docker

The image is `python:3.10-alpine` with only the `main` Poetry group.

```bash
cp .env.example .env
docker compose run --rm --no-deps fastapi python ./src/cli.py secret
docker compose up -d --build
```

Put the generated secret in `APP_SECRET` before `docker compose up`. Migrations and seeders run manually:

```bash
docker compose exec fastapi python ./src/cli.py migrate:up
docker compose exec fastapi python ./src/cli.py v1:user:seed
```

| Service | Purpose | Port |
|---------|---------|------|
| `fastapi` | Uvicorn server (`UVICORN_WORKERS`, default 1) | `APP_PORT` (8000) |
| `worker` | `queue:work` (profile `worker`) | — |
| `postgres`, `redis` | PostgreSQL 16 and Redis 7 | internal |
| `mongo` | MongoDB 7 (profile `mongo`) | internal |

Compose points PostgreSQL and Redis at its own containers. Change their credentials with `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `REDIS_PASSWORD`. Enable MongoDB with `docker compose --profile mongo up -d` and `DATABASE_MONGO_URI=mongodb://mongo:27017/codebase`.

## API

All routes live under `/api/v1`.

| Area | Routes |
|------|--------|
| Auth | `/auth/login`, `/auth/register`, `/auth/refresh`, `/auth/logout`, `/auth/forgot-password`, `/auth/reset-password/{email}`, `/auth/verify-email/{email}` |
| Profile | `/users/me`, `/users/me/accesses`, `/users/me/interests` |
| Notifications | `/notifications/*` |
| Web Push | `/webpush/subscribe`, `/webpush/unsubscribe` |
| Admin | `/admin/users`, `/admin/roles`, `/admin/permissions`, `/admin/activities`, `/admin/notifications`, `/admin/settings`, `/admin/dashboard`, `/admin/search` |

Login body is `{ "identifierKey": "email" | "name", "identifierValue": "...", "password": "..." }` and returns `{ accessToken, refreshToken, accessTokenTtl, refreshTokenTtl }`. `identifierKey` is optional; without it, a value containing `@` is treated as an email, otherwise as a name.

Lists accept `limitPage`, `currentPage`, `orders=field:asc`, and `filters=key:value` and return `{ total, totalPage, perPage, currentPage, nextPage, previousPage, firstPage, lastPage, data }`.

## Realtime

Socket.IO is served at `/socket.io`. Connect with `auth: { token: accessToken }`. Each user joins room `user:{id}`.

| Event | Payload |
|-------|---------|
| `v1.notification.created` | `id`, `unread` |
| `v1.admin.refresh` | `userId`, `scopes` |
| `v1.user.admin.imported` | `userId`, `filename`, `totalImported`, `totalSkipped` |
| `v1.user.admin.imported-failed` | `userId`, `filename`, `error` |
| `v1.user.admin.exported` | `userId`, `filename`, `fileUrl` |
| `v1.user.admin.exported-failed` | `userId`, `error` |
| `v1.acl.role.admin.*`, `v1.acl.permission.admin.*` | Same as the user import and export events |
| `v1.user.admin.activated`, `v1.user.admin.deactivated` | `id`, `name`, `email`, `email_verified_at`, `created_at`, `updated_at`, `deleted_at` |

Import and export events go to the admin who started the job. Activate and deactivate events go to the affected user.

```javascript
import { io } from "socket.io-client";

const socket = io("http://localhost:8000", {
    path: "/socket.io",
    transports: ["websocket"],
    auth: { token: accessToken },
});

socket.on("v1.notification.created", (data) => console.log(data.id, data.unread));
socket.on("v1.user.admin.exported", (data) => console.log(data.fileUrl));
```

## Testing

```bash
poetry run pytest -v
poetry run pytest --cov=src --cov-report=html
```

## CLI

| Command | Description |
|---------|-------------|
| `migrate:up` | Run migrations |
| `migrate:down` | Roll back the last migration |
| `migrate:status` | Show migration status |
| `queue:work` | Start the queue worker |
| `queue:status` | Show queue status |
| `queue:failed` | List failed jobs (`--count`, `--retry`, `--clear`) |
| `cache:clear` | Clear the Redis cache |
| `secret` | Generate `APP_SECRET` |
| `v1:user:seed` | Seed default users |

Run each with `poetry run python3 ./src/cli.py <command>`.

## Author

- Trip Teknologi ([@tripteki](https://linkedin.com/company/tripteki))
- Hasby Maulana ([@hsbmaulana](https://linkedin.com/in/hsbmaulana))
