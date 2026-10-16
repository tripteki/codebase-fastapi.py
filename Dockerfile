ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION}-alpine AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN apk add --no-cache build-base linux-headers postgresql-dev libffi-dev \
    && python -m venv /opt/poetry \
    && /opt/poetry/bin/pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/root/.cache/pypoetry \
    /opt/poetry/bin/poetry install --only main --no-root \
    && find .venv -type d -name "__pycache__" -prune -exec rm -rf {} + \
    && find .venv -type d -name "tests" -path "*/site-packages/*/tests" -prune -exec rm -rf {} +

FROM python:${PYTHON_VERSION}-alpine AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}" \
    APP_ENV=production \
    APP_PORT=8000 \
    UVICORN_WORKERS=1

RUN apk add --no-cache libpq libstdc++ libffi tzdata \
    && addgroup -S app \
    && adduser -S -G app -h /app app

WORKDIR /app

COPY --from=build --chown=app:app /app/.venv ./.venv
COPY --chown=app:app . .

RUN mkdir -p storage/disks/public storage/logs && chown -R app:app storage

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget -qO /dev/null "http://127.0.0.1:${APP_PORT}/api/status" || exit 1

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port \"${APP_PORT}\" --workers \"${UVICORN_WORKERS}\" --proxy-headers --forwarded-allow-ips='*'"]
