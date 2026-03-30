"""
Celery Worker Entry Point
Equivalent to: backend/src/services/submissionQueue.ts (Bull queue)
"""

from celery import Celery
import asyncio

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("celery_worker")

# Create Celery app
celery_app = Celery(
    "coding_war",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=settings.judge_concurrency,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="judge.submission", bind=True, max_retries=1)
def judge_submission_task(self, submission_id: str) -> dict:
    """
    Celery task to judge a submission.
    Wraps the async judge function in an event loop.
    """
    from app.services.judge_service import judge_submission

    try:
        asyncio.run(judge_submission(submission_id))
        return {"status": "completed", "submission_id": submission_id}
    except Exception as e:
        logger.error("Judge task failed", submission_id=submission_id, error=str(e))
        raise self.retry(exc=e, countdown=5)


def enqueue_submission(submission_id: str) -> None:
    """Enqueue a submission for judging."""
    judge_submission_task.delay(submission_id)
    logger.info("Submission enqueued", submission_id=submission_id)
