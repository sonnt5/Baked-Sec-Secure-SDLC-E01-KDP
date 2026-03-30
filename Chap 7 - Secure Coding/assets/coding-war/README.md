# Coding War

An online judge platform for competitive programming — built with React + Python/FastAPI.

## Overview

Coding War lets users:
- Practice algorithm problems with a live judge
- Participate in ACM/IOI-style contests
- Get real-time verdict feedback via WebSocket
- Track rankings on a live scoreboard

## Project Structure

```
coding-war/
├── frontend/           # React 19 + TypeScript (Vite)
├── backend-py/         # Python 3.12 + FastAPI + SQLAlchemy
├── docker-compose.yml  # Full-stack local environment
└── Makefile            # Convenience aliases
```

## Quick Start

### Prerequisites
- Docker & Docker Compose (v2)

### 1. Start everything

```bash
docker compose up --build -d
```

This starts:
| Service | Port | Description |
|---|---|---|
| `frontend` | 5173 | React dev server (Vite HMR) |
| `backend` | 3000 | FastAPI + Uvicorn |
| `postgres` | 5432 | PostgreSQL 15 |
| `redis` | 6379 | Redis 7 (cache + job queue) |
| `minio` | 9000 | S3-compatible object storage |
| `judge` | — | Celery worker (code execution) |

Schema migrations run automatically on backend startup (idempotent).

### 2. Open the app

- **Frontend**: http://localhost:5173
- **API docs**: http://localhost:3000/docs

### 3. Useful commands

```bash
# View logs
docker compose logs -f backend

# Rebuild backend only (after code changes)
docker compose up --build -d backend

# Access PostgreSQL
docker compose exec postgres psql -U postgres -d codingwar

# Restart everything cleanly
docker compose down && docker compose up --build -d
```

## Tech Stack

### Frontend
| | |
|---|---|
| Framework | React 19 + TypeScript |
| Build | Vite |
| State | Zustand + TanStack Query |
| Routing | React Router v7 |
| Real-time | Socket.io Client |
| HTTP | Axios |

### Backend
| | |
|---|---|
| Framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 async |
| Database | PostgreSQL 15 |
| Cache/Queue | Redis 7 + Celery |
| WebSocket | python-socketio (ASGI outer wrapper) |
| Auth | Argon2id + JWT |
| Storage | S3 / MinIO |
| Validation | Pydantic v2 |

## Features

### ✅ Authentication & Authorization
- Register / login / email verification / password reset
- JWT (access + refresh tokens)
- Role-based access: Admin, User, Guest

### ✅ Problem Management
- CRUD with Markdown + LaTeX descriptions
- Difficulty levels: Easy / Medium / Hard
- Public / Private / Contest-only visibility
- **Inline test case manager**: add, visualize, and delete test cases as plain text
- Legacy ZIP upload → S3 (COMPLIANCE ObjectLock, immutable)

### ✅ Judge System
- Languages: C, C++17, Python 3, Java
- Docker sandbox: `network=none`, read-only rootfs, cap-drop ALL
- Time and memory limit enforcement
- Verdicts: AC, WA, TLE, MLE, RE, CE
- Real-time status updates (Queued → Compiling → Running → Verdict)

### ✅ Contest System
- ACM/ICPC and IOI scoring modes
- Problem assignment during create or via `PUT /{id}/problems`
- Contest registration with time-based access control
- Freeze time support
- Live scoreboard via Socket.io

### ✅ User Features
- Profile with submission statistics
- Submission history
- **Resubmit** — from any failed submission, pre-fills the editor with previous code

### ✅ Admin Panel
- User management (search, role assignment)
- Problem CRUD with test case manager
- Contest creation and management
- System statistics dashboard

## Architecture

```
Browser
  │
  ├─ HTTP /api/*  ──────────────────▶ FastAPI (CORSMiddleware)
  │                                       │
  └─ WS  /socket.io/*  ──────────▶ python-socketio (outer ASGI)
                                          │
                          ┌───────────────┴───────────────┐
                      PostgreSQL                         Redis
                      (SQLAlchemy)                 (cache + Celery)
                                                          │
                                                    Celery Worker
                                                   (Docker sandbox)
                                                          │
                                                       MinIO / S3
                                                     (test cases)
```

**Socket.IO as the outer ASGI layer** — prevents duplicate CORS headers that occur when Socket.IO is mounted as a FastAPI sub-app.

## Documentation

- [Frontend README](./frontend/README.md)
- [Backend README](./backend-py/README.md)

## License

MIT
