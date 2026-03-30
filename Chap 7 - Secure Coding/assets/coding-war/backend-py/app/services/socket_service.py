"""
WebSocket / Socket.io Service
Equivalent to: backend/src/services/socketService.ts + submissionSocketService.ts + scoreboardSocketService.ts
"""

import socketio

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("socket_service")

# Create Socket.IO async server with explicit allowed origins.
# This is used as the OUTER ASGI wrapper in main.py (not a mounted sub-app),
# so FastAPI's CORSMiddleware won't interfere with socket.io paths.
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origins,
    logger=False,
)


# ──────────────────────────── Events ────────────────────────────

@sio.event
async def connect(sid, environ):
    """Client connected."""
    logger.debug("Client connected", sid=sid)


@sio.event
async def disconnect(sid):
    """Client disconnected."""
    logger.debug("Client disconnected", sid=sid)


@sio.event
async def subscribe_submission(sid, data):
    """
    Subscribe to submission status updates.
    Client sends: { submissionId: string }
    """
    submission_id = data.get("submissionId")
    if submission_id:
        room = f"submission:{submission_id}"
        await sio.enter_room(sid, room)
        logger.debug("Subscribed to submission", sid=sid, submission_id=submission_id)


@sio.event
async def subscribe_scoreboard(sid, data):
    """
    Subscribe to scoreboard updates.
    Client sends: { contestId: string }
    """
    contest_id = data.get("contestId")
    if contest_id:
        room = f"scoreboard:{contest_id}"
        await sio.enter_room(sid, room)
        logger.debug("Subscribed to scoreboard", sid=sid, contest_id=contest_id)


# ──────────────────────────── Emit Helpers ────────────────────────────

async def emit_submission_update(submission_id: str, status: str, data: dict | None = None) -> None:
    """
    Emit submission status update to subscribers.
    Server → Client: submission:update
    """
    room = f"submission:{submission_id}"
    payload = {"submissionId": submission_id, "status": status}
    if data:
        payload.update(data)

    await sio.emit("submission:update", payload, room=room)
    logger.debug("Emitted submission update", submission_id=submission_id, status=status)


async def emit_submission_complete(submission_id: str, result: dict) -> None:
    """
    Emit submission complete event to subscribers.
    Server → Client: submission:complete
    """
    room = f"submission:{submission_id}"
    await sio.emit("submission:complete", {
        "submissionId": submission_id,
        **result,
    }, room=room)
    logger.debug("Emitted submission complete", submission_id=submission_id)


async def emit_scoreboard_update(contest_id: str, scoreboard: dict) -> None:
    """
    Emit scoreboard update to subscribers.
    Server → Client: scoreboard:update
    """
    room = f"scoreboard:{contest_id}"
    await sio.emit("scoreboard:update", scoreboard, room=room)
    logger.debug("Emitted scoreboard update", contest_id=contest_id)
