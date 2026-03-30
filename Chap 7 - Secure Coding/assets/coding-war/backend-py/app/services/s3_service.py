"""
S3 Service
Equivalent to: backend/src/services/s3Service.ts
SDRD Gap Fix: ADR-004/006 — ServerSideEncryption + Object Lock
Pattern from: assets/code/fixed/testcase_storage.py
"""

import boto3
from botocore.config import Config

from app.config import settings
from app.utils.checksum import compute_sha256
from app.utils.logger import get_logger

logger = get_logger("s3_service")

# S3 Client singleton
_s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint,
    region_name=settings.s3_region,
    aws_access_key_id=settings.s3_access_key_id,
    aws_secret_access_key=settings.s3_secret_access_key,
    config=Config(s3={"addressing_style": "path"}),
)

BUCKET = settings.s3_bucket_name


def get_testcase_s3_key(problem_id: str, order_index: int, file_type: str) -> str:
    """
    Generate S3 key for a testcase file.
    Format: testcases/{problemId}/{orderIndex}.{in|out}
    """
    return f"testcases/{problem_id}/{order_index}.{file_type}"


def upload_testcase_file(key: str, content: bytes) -> None:
    """
    Upload a testcase file to S3 with server-side encryption and Object Lock.
    SDRD Gap Fix ADR-006:
      TS-02: SSE-AES256 encrypts at rest
      TS-04: COMPLIANCE Object Lock — immutable after publish, cannot be deleted/overwritten
    """
    # Object Lock retention: lock for 10 years (testcases are immutable reference data)
    from datetime import datetime, timezone, timedelta
    retain_until = (datetime.now(timezone.utc) + timedelta(days=3650)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    _s3_client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=content,
        ContentType="text/plain",
        ServerSideEncryption="AES256",          # TS-02: encrypt at rest
        Metadata={"sha256": compute_sha256(content)},
        ObjectLockMode="COMPLIANCE",             # TS-04: immutable — can't be deleted
        ObjectLockRetainUntilDate=retain_until,
    )
    logger.debug("Uploaded testcase to S3", key=key, size=len(content))


def download_testcase_file(key: str) -> bytes:
    """Download a testcase file from S3."""
    response = _s3_client.get_object(Bucket=BUCKET, Key=key)
    content = response["Body"].read()
    logger.debug("Downloaded testcase from S3", key=key)
    return content


def generate_presigned_url(key: str, expires_in: int | None = None) -> str:
    """
    Generate a presigned GET URL for a testcase file.
    Default TTL: 300 seconds.
    """
    ttl = expires_in or settings.s3_presigned_url_expiry
    url = _s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=ttl,
    )
    logger.debug("Generated presigned URL", key=key, expires_in=ttl)
    return url


def delete_testcase_files(problem_id: str) -> None:
    """Delete all testcase files for a problem from S3."""
    prefix = f"testcases/{problem_id}/"

    response = _s3_client.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
    contents = response.get("Contents", [])

    if not contents:
        logger.debug("No testcase files to delete", problem_id=problem_id)
        return

    objects = [{"Key": obj["Key"]} for obj in contents]
    _s3_client.delete_objects(Bucket=BUCKET, Delete={"Objects": objects})

    logger.info("Deleted testcase files", problem_id=problem_id, count=len(objects))
