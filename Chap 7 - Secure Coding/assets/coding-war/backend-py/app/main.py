"""
Coding War Backend — FastAPI Application Entry Point
Equivalent to: backend/src/index.ts
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.middleware.error_handler import register_exception_handlers
from app.database import engine
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application startup and shutdown events."""
    logger.info("Starting Coding War Backend", environment=settings.environment)

    # Apply schema migrations (idempotent raw SQL — safe to run on every start)
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text(
                "ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS input_content TEXT"
            ))
            await conn.execute(text(
                "ALTER TABLE test_cases ADD COLUMN IF NOT EXISTS output_content TEXT"
            ))
        logger.info("Schema migrations applied")
    except Exception as e:
        logger.warning("Schema migration warning", error=str(e))

    yield
    # Shutdown: dispose database engine
    await engine.dispose()
    logger.info("Coding War Backend shut down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for Coding War - Online Judge Platform",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    redirect_slashes=False,
    lifespan=lifespan,
)

# ─── Middleware (order matters: last added = first executed) ───

# GZip Compression (equivalent to `compression()`)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security Headers (equivalent to `helmet()`) — now BaseHTTPMiddleware subclass
app.add_middleware(SecurityHeadersMiddleware)

# Request ID (equivalent to `requestIdMiddleware`)
app.add_middleware(BaseHTTPMiddleware, dispatch=RequestIdMiddleware())

# Request Logger
app.add_middleware(BaseHTTPMiddleware, dispatch=RequestLoggerMiddleware())

# CORS — must be last added (= first executed) so preflight OPTIONS requests
# are handled before any other middleware touches the request/response.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Exception Handlers ───
register_exception_handlers(app)


# ─── Health Check ───
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    from datetime import datetime, timezone
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ─── Mount API Routers ───
from app.routers import auth, problems, submissions, contests, users, admin  # noqa: E402

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(problems.router, prefix="/api/problems", tags=["Problems"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["Submissions"])
app.include_router(contests.router, prefix="/api/contests", tags=["Contests"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


# ─── Socket.IO — wrap FastAPI as the inner ASGI app ───
# This is the recommended pattern: socket.io is the OUTER ASGI layer.
# /socket.io/* → handled by socket.io (its own CORS)
# everything else → passed through to FastAPI (its own CORSMiddleware)
import socketio as _sio_module  # noqa: E402
from app.services.socket_service import sio  # noqa: E402

top_app = _sio_module.ASGIApp(sio, other_asgi_app=app, socketio_path="socket.io")


# ─── API Info ───
@app.get("/api", tags=["Info"])
async def api_info():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Backend API for Coding War - Online Judge Platform",
        "endpoints": {
            "health": "/health",
            "api": "/api",
            "auth": "/api/auth",
            "problems": "/api/problems",
            "submissions": "/api/submissions",
            "contests": "/api/contests",
            "users": "/api/users",
            "admin": "/api/admin",
        },
    }
