# Coding War — Backend (Python / FastAPI)

FastAPI backend for the Coding War online judge platform.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI + Uvicorn |
| Database | PostgreSQL 15 + SQLAlchemy 2.0 (async) |
| Migrations | Idempotent raw SQL via `lifespan` startup event |
| Cache / Queue | Redis 7 + Celery |
| WebSocket | python-socketio (ASGI outer wrapper) |
| Auth | Argon2id + JWT (python-jose) |
| Storage | S3 / MinIO (boto3) |
| Validation | Pydantic v2 |
| Logging | structlog |

## Quick Start (Docker)

All services are managed by Docker Compose at the repo root:

```bash
docker compose up --build -d
```

The backend container runs `entrypoint.sh` which:
1. Applies schema migrations (idempotent, safe to re-run)
2. Starts Uvicorn pointing at `app.main:top_app` (Socket.IO ASGI wrapper)

## API Documentation

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc
- **Health**: http://localhost:3000/health

## API Endpoints

### Authentication (`/api/auth`) — 6 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/register` | — | Register + send verification email |
| POST | `/verify-email` | — | Verify email token |
| POST | `/login` | — | Login → access + refresh JWT |
| POST | `/refresh` | — | Refresh access token |
| POST | `/forgot-password` | — | Send reset email |
| POST | `/reset-password` | — | Reset with token |

### Problems (`/api/problems`) — 9 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | Optional | List problems (paginate, filter, search) |
| GET | `/{id}` | Optional | Get problem details |
| POST | `/` | Admin | Create problem |
| PUT | `/{id}` | Admin | Update problem |
| DELETE | `/{id}` | Admin | Delete problem |
| GET | `/{id}/test-cases` | Admin | List test cases (DB inline + S3 fallback) |
| POST | `/{id}/test-cases/single` | Admin | Add inline text test case |
| DELETE | `/{id}/test-cases/{tc_id}` | Admin | Delete test case |
| POST | `/{id}/test-cases` | Admin | Upload test cases (zip → S3) |

### Submissions (`/api/submissions`) — 4 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/` | User | Submit solution |
| GET | `/{id}` | User | Get submission (ownership check) |
| GET | `/` | User | List user's submissions |
| POST | `/{id}/rejudge` | Admin | Rejudge a submission |

### Contests (`/api/contests`) — 8 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | — | List contests (filter by status) |
| GET | `/{id}` | Optional | Get contest + problems (with title & difficulty) |
| POST | `/` | Admin | Create contest (accepts `problems` array) |
| PUT | `/{id}` | Admin | Update contest metadata |
| PUT | `/{id}/problems` | Admin | Replace contest problem list |
| DELETE | `/{id}` | Admin | Delete contest |
| POST | `/{id}/register` | User | Register for contest |
| GET | `/{id}/scoreboard` | Optional | Live scoreboard |

### Users (`/api/users`) — 3 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/{id}` | Optional | Profile + statistics |
| PUT | `/{id}` | User | Update own profile |
| GET | `/{id}/submissions` | User | Submission history |

### Admin (`/api/admin`) — 3 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/users` | Admin | List users (search, paginate) |
| PUT | `/users/{id}/role` | Admin | Change user role |
| GET | `/statistics` | Admin | System statistics |

## Project Structure

```
app/
├── main.py              # FastAPI app + lifespan startup migration
│                        # Exports top_app = socketio.ASGIApp(sio, app)
├── config.py            # Pydantic Settings
├── database.py          # Async SQLAlchemy engine + session factory
├── worker.py            # Celery judge worker
├── models/              # SQLAlchemy models (User, Problem, TestCase,
│                        #   Submission, TestCaseResult, Contest,
│                        #   ContestProblem, ContestParticipant)
├── schemas/             # Pydantic request/response schemas
├── routers/             # auth, problems, submissions, contests, users, admin
├── services/            # Business logic (14 services)
│   ├── socket_service.py   # python-socketio sio instance + event handlers
│   └── ...
├── middleware/          # Security headers, error handler, logging, rate limit
├── dependencies/        # get_db (auto-commit session), JWT auth, RBAC
└── utils/               # Logger, SHA-256 checksum
```

## Architecture: Socket.IO Integration

Socket.IO is the **outer ASGI layer**:

```
Uvicorn → top_app (socketio.ASGIApp)
            ├── /socket.io/*  →  socket.io  (own CORS)
            └── everything else → FastAPI app (CORSMiddleware)
```

This avoids duplicate CORS headers that occurred when Socket.IO was mounted as a sub-app inside FastAPI.

## Database Schema — Key Models

| Model | Table | Notes |
|---|---|---|
| `User` | `users` | Argon2id password, RBAC role |
| `Problem` | `problems` | Markdown description, S3 test case keys |
| `TestCase` | `test_cases` | `input_content` / `output_content` for inline storage |
| `Submission` | `submissions` | Language, verdict, execution stats |
| `Contest` | `contests` | IOI/ACM scoring, freeze time |
| `ContestProblem` | `contest_problems` | `order_index`, `points`; eager-loaded with `lazy="selectin"` |

## Security

| Control | Implementation |
|---|---|
| Password Hashing | Argon2id (64 MB, 3 iterations, parallelism 4) |
| Authentication | JWT Bearer (7-day access, 30-day refresh) |
| Authorization | RBAC: Admin > User > Guest |
| Rate Limiting | 3-tier: 100/min general, 10/min submit, 5/min login |
| Input Validation | Pydantic v2 on all endpoints |
| Security Headers | HSTS, CSP, X-Frame-Options, X-Content-Type-Options |
| S3 Test Cases | SSE-AES256, COMPLIANCE ObjectLock (immutable) |
| Integrity | SHA-256 checksums + timing-safe compare |
| Sandbox | Docker: `network=none`, read-only rootfs, cap-drop ALL |
| Server Time | `_utc_now()` — centralised UTC clock (ADR-008) |

## Environment Variables

See `.env.example` for the full list.

| Variable | Description |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` |
| `REDIS_HOST` | Redis hostname |
| `JWT_SECRET` | **Required** — random 32+ byte secret |
| `S3_ENDPOINT` | S3/MinIO endpoint URL |
| `JUDGE_CONCURRENCY` | Parallel judge processes (default: 3) |

## WebSocket Events

| Direction | Event | Payload |
|---|---|---|
| Client → Server | `subscribe:submission` | `{ submissionId }` |
| Server → Client | `submission:update` | `{ id, status, … }` |
| Server → Client | `submission:complete` | Full submission with test results |
| Client → Server | `subscribe:scoreboard` | `{ contestId }` |
| Server → Client | `scoreboard:update` | Updated scoreboard row |
