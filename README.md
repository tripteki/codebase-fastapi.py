<h1 align="center">Codebase FastAPI</h1>

This skeleton provides comprehensive backend implementation built with FastAPI framework, applying concepts like `Test Driven Development` `Event-Listener Driven Development` `Queue Processing` `WebSocket Real-time` `Scheduled Tasks` `Cached`, implementing design principles like `RESTful API` `GraphQL` `Tight Cohesion & Loose Coupling` `SOLID` `Dependency Injection`, and design patterns like `Gangs of Four (GoF) Repository Pattern` `Data Transfer Object (DTO)` `Middleware Pattern` `Observer Pattern`.

### Features

<table style="width: 100%; border: none;">
  <tr>
    <th>No</th>
    <th>Feature</th>
    <th>Description</th>
    <th>Technology</th>
  </tr>
  <tr>
    <td>1</td>
    <td>REST API</td>
    <td>Comprehensive RESTful API with OpenAPI/Swagger documentation</td>
    <td>FastAPI + Swagger UI</td>
  </tr>
  <tr>
    <td>2</td>
    <td>GraphQL API</td>
    <td>Modern GraphQL API with Strawberry integration</td>
    <td>Strawberry GraphQL</td>
  </tr>
  <tr>
    <td>3</td>
    <td>Authentication</td>
    <td>JWT-based authentication with access/refresh token mechanism</td>
    <td>JWT + Python-Jose</td>
  </tr>
  <tr>
    <td>4</td>
    <td>WebSocket</td>
    <td>Real-time bidirectional event-based communication</td>
    <td>Socket.IO + Python-SocketIO</td>
  </tr>
  <tr>
    <td>5</td>
    <td>Queue Processing</td>
    <td>Asynchronous job processing with Redis-backed queue system</td>
    <td>RQ (Redis Queue) + Redis</td>
  </tr>
  <tr>
    <td>6</td>
    <td>Scheduled Tasks</td>
    <td>Cron-based task scheduling for periodic operations</td>
    <td>APScheduler</td>
  </tr>
  <tr>
    <td>7</td>
    <td>Database</td>
    <td>Multi-database support with async ORM</td>
    <td>SQLModel + Alembic + PostgreSQL + MongoDB</td>
  </tr>
  <tr>
    <td>8</td>
    <td>Caching</td>
    <td>Redis-based caching for improved performance</td>
    <td>Redis + FastAPI-Limiter</td>
  </tr>
  <tr>
    <td>9</td>
    <td>Import/Export</td>
    <td>Bulk user data import/export with CSV/Excel support</td>
    <td>Pandas + openpyxl + Queue</td>
  </tr>
  <tr>
    <td>10</td>
    <td>Email Service</td>
    <td>Transactional email notifications with template support</td>
    <td>aiosmtplib + Jinja2</td>
  </tr>
  <tr>
    <td>11</td>
    <td>Internationalization</td>
    <td>Multi-language support with i18n (English + Indonesian)</td>
    <td>Custom i18n implementation</td>
  </tr>
  <tr>
    <td>12</td>
    <td>Rate Limiting</td>
    <td>API rate limiting and throttling for security</td>
    <td>FastAPI-Limiter + Redis</td>
  </tr>
  <tr>
    <td>13</td>
    <td>Testing</td>
    <td>End-to-end testing with comprehensive test coverage</td>
    <td>Pytest + HTTPX</td>
  </tr>
</table>

Getting Started
---

### Requirements

Ensure you have the following installed:

- Python >= 3.10
- Poetry >= 1.8.0
- PostgreSQL >= 14.x
- MongoDB >= 6.x
- Redis >= 7.x

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd codebase-fastapi.py

# Install dependencies with Poetry
poetry install
```

### Configuration

Copy the environment configuration file and update with your credentials:

```bash
cp .env.example .env
```

Run database migrations:

```bash
# PostgreSQL migration
poetry run python3 ./src/cli.py migrate:up
```

### Running the Application

#### Development Mode

```bash
poetry run fastapi dev
```

The server will start at `http://localhost:8000` with the following features enabled:

- Hot-reload on file changes
- Debug mode enabled
- Detailed logging

#### Production Mode

```bash
# Start production server
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Background Workers

Start Redis Queue workers to process background jobs:

```bash
# Start queue worker
poetry run python3 ./src/cli.py queue:work

# Start with specific queue
poetry run python3 ./src/cli.py queue:work --queue default
```

### API Documentation

#### Swagger UI (REST API)

Access the interactive API documentation at:

```
http://localhost:8000/api/docs
```

Features:
- Interactive API testing
- Request/response examples
- Schema definitions
- Authentication support

#### GraphQL Playground

Access the GraphQL API interface at:

```
http://localhost:8000/graphql
```

Example query:

```graphql
query {
  me {
    id
    email
    name
  }
}

query {
  version
}
```

Example mutation:

```graphql
mutation {
  login(email: "user@example.com", password: "password") {
    accessToken
    refreshToken
  }
}
```

### WebSocket Setup

This application provides real-time notifications for import/export operations using Socket.IO.

#### Available Events

- `v1.user.admin.imported` - User import completed successfully
- `v1.user.admin.imported-failed` - User import failed
- `v1.user.admin.exported` - User export completed successfully
- `v1.user.admin.exported-failed` - User export failed

#### Client Connection Example

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:8000', {
    transports: ['websocket', 'polling'],
    extraHeaders: {
        'Authorization': 'Bearer YOUR_JWT_TOKEN'
    }
});

socket.on('v1.user.admin.imported', (data) => {
    console.log('Import completed:', data.totalImported, 'users');
});

socket.on('v1.user.admin.exported', (data) => {
    console.log('Export ready:', data.fileUrl);
});
```

#### Testing WebSocket

Use the provided HTML client for testing:

```bash
open examples/websocket-import-export-client.html
```

### Testing

Run the end-to-end test suite:

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=src --cov-report=html
```

### Available Scripts

<table style="width: 100%; border: none;">
  <tr>
    <th>Script</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>poetry run fastapi dev</code></td>
    <td>Start development server with hot-reload</td>
  </tr>
  <tr>
    <td><code>poetry run fastapi run</code></td>
    <td>Start production server</td>
  </tr>
  <tr>
    <td><code>poetry run pytest</code></td>
    <td>Run end-to-end tests</td>
  </tr>
  <tr>
    <td><code>poetry run pytest --cov</code></td>
    <td>Run tests with coverage report</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py migrate:up</code></td>
    <td>Run PostgreSQL database migrations</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py migrate:down</code></td>
    <td>Rollback last migration</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py migrate:status</code></td>
    <td>Show migration status</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py queue:work</code></td>
    <td>Start background queue worker</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py queue:failed</code></td>
    <td>List all failed jobs</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py queue:failed --count</code></td>
    <td>Show count of failed jobs</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py queue:failed --retry</code></td>
    <td>Retry all failed jobs</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py queue:failed --clear</code></td>
    <td>Clear all failed jobs</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py cache:clear</code></td>
    <td>Clear all Redis cache</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py secret</code></td>
    <td>Generate random secret key for JWT</td>
  </tr>
  <tr>
    <td><code>poetry run python3 ./src/cli.py v1:user:seed</code></td>
    <td>Seed default users into database</td>
  </tr>
</table>

Author
---

- Trip Teknologi ([@tripteki](https://linkedin.com/company/tripteki))
- Hasby Maulana ([@hsbmaulana](https://linkedin.com/in/hsbmaulana))
