"""
Docker Sandbox Service
Manages Docker containers for secure code execution via Python docker SDK.
(No Docker CLI binary required inside the container — uses /var/run/docker.sock)
"""

import asyncio
import uuid
from functools import lru_cache

import docker as docker_sdk
import docker.errors

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("docker_sandbox")

# Language → Docker image mapping
LANGUAGE_IMAGES = {
    "C": "coding-war-judge:latest",
    "CPP": "coding-war-judge:latest",
    "PYTHON": "coding-war-judge:latest",
    "JAVA": "coding-war-judge:latest",
}

# Resource limits (SDRD: REQ-10.1–10.5)
DEFAULT_MEMORY_LIMIT = "256m"
DEFAULT_CPU_PERIOD = 100000
DEFAULT_CPU_QUOTA = 50000  # 50% of one CPU core
DEFAULT_PIDS_LIMIT = 64


@lru_cache(maxsize=1)
def _get_docker_client() -> docker_sdk.DockerClient:
    """Return a cached Docker client connected via /var/run/docker.sock."""
    return docker_sdk.from_env()


def _docker_client() -> docker_sdk.DockerClient:
    return _get_docker_client()


async def create_sandbox(
    language: str,
    source_code: str,
    *,
    memory_limit: str = DEFAULT_MEMORY_LIMIT,
    timeout_ms: int | None = None,
) -> str:
    """
    Create a Docker container sandbox for code execution.
    Returns the container name.
    """
    container_name = f"judge-{uuid.uuid4().hex[:12]}"
    image = LANGUAGE_IMAGES.get(language, LANGUAGE_IMAGES["PYTHON"])
    timeout = timeout_ms or settings.judge_timeout

    def _create():
        client = _docker_client()
        client.containers.create(
            image,
            name=container_name,
            command=["sleep", "infinity"],
            network_disabled=True,
            # Note: read_only removed — Docker's put_archive API writes through the overlay
            # filesystem layer and cannot reach tmpfs mounts on a read-only rootfs.
            # Security is still enforced by: no network, cap_drop ALL, no-new-privileges,
            # pids-limit, mem/cpu limits.
            cap_drop=["ALL"],
            security_opt=["no-new-privileges"],
            mem_limit=memory_limit,
            cpu_period=DEFAULT_CPU_PERIOD,
            cpu_quota=DEFAULT_CPU_QUOTA,
            pids_limit=DEFAULT_PIDS_LIMIT,
            tmpfs={
                "/tmp": "rw,noexec,nosuid,size=64m",
                # /app is NOT tmpfs — put_archive writes via overlay layer and cannot reach tmpfs paths
            },
            environment={
                "TIMEOUT_MS": str(timeout),
            },
            detach=True,
        )
        return container_name

    loop = asyncio.get_event_loop()
    try:
        name = await loop.run_in_executor(None, _create)
        logger.debug("Sandbox created", container=name)
        return name
    except docker.errors.ImageNotFound:
        raise RuntimeError(
            f"Judge image '{image}' not found. Run: docker build -t {image} ./judge"
        )
    except Exception as e:
        logger.error("Failed to create sandbox", error=str(e))
        raise RuntimeError(f"Docker create failed: {e}")


async def start_sandbox(container_name: str) -> None:
    """Start a sandbox container."""
    def _start():
        client = _docker_client()
        container = client.containers.get(container_name)
        container.start()

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _start)


async def exec_in_sandbox(
    container_name: str,
    command: list[str],
    *,
    timeout_seconds: int = 30,
    stdin_data: bytes | None = None,
) -> tuple[int, str, str]:
    """
    Execute a command inside the sandbox.
    Returns (exit_code, stdout, stderr).

    WHY shell-pipe for stdin: exec_run(stdin=True) only opens a stdin channel
    but the docker-py SDK has no API to actually write bytes into it. The process
    then blocks forever on input(), hitting TLE. Instead, we encode stdin as base64
    and pipe it through the shell — the same reliable approach used in write_to_sandbox.
    """
    def _exec():
        import base64
        import shlex

        client = _docker_client()
        container = client.containers.get(container_name)

        if stdin_data is not None:
            # Encode stdin as base64, pipe through shell into the program
            b64 = base64.b64encode(stdin_data).decode()
            prog = " ".join(shlex.quote(c) for c in command)
            actual_command = ["sh", "-c", f"printf '%s' '{b64}' | base64 -d | {prog}"]
        else:
            actual_command = command

        result = container.exec_run(
            actual_command,
            stdin=False,
            stdout=True,
            stderr=True,
            demux=True,  # separate stdout/stderr
        )
        stdout_bytes, stderr_bytes = result.output or (b"", b"")
        return (
            result.exit_code or 0,
            (stdout_bytes or b"").decode(errors="replace"),
            (stderr_bytes or b"").decode(errors="replace"),
        )

    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _exec),
            timeout=timeout_seconds,
        )
    except asyncio.TimeoutError:
        return -1, "", "Time Limit Exceeded"


async def write_to_sandbox(container_name: str, content: str, dst_path: str) -> None:
    """
    Write content to a file inside the sandbox using exec_run + base64.
    exec_run runs inside the container's filesystem namespace, so it correctly
    reaches any path (overlay, tmpfs, etc.) — unlike put_archive which operates
    on the overlay layer from outside and may miss tmpfs/bind mounts.
    """
    def _write():
        import base64
        client = _docker_client()
        container = client.containers.get(container_name)

        # Encode as base64 to safely pass arbitrary content through the shell
        b64 = base64.b64encode(content.encode()).decode()
        # Ensure parent directory exists, then decode and write
        dirpath = "/".join(dst_path.split("/")[:-1]) or "/"
        result = container.exec_run(
            ["sh", "-c", f"mkdir -p {dirpath} && printf '%s' '{b64}' | base64 -d > {dst_path}"],
            stdout=True,
            stderr=True,
        )
        if result.exit_code != 0:
            raise RuntimeError(
                f"Failed to write {dst_path}: {result.output.decode(errors='replace')}"
            )

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _write)


async def copy_to_sandbox(container_name: str, src_path: str, dst_path: str) -> None:
    """Copy a file from host into the sandbox."""
    def _copy():
        import io
        import tarfile

        client = _docker_client()
        container = client.containers.get(container_name)
        with open(src_path, "rb") as f:
            file_data = f.read()

        buf = io.BytesIO()
        filename = dst_path.split("/")[-1]
        dirpath = "/".join(dst_path.split("/")[:-1]) or "/"
        with tarfile.open(fileobj=buf, mode="w") as tar:
            info = tarfile.TarInfo(name=filename)
            info.size = len(file_data)
            tar.addfile(info, io.BytesIO(file_data))
        buf.seek(0)
        container.put_archive(dirpath, buf)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _copy)


async def destroy_sandbox(container_name: str) -> None:
    """Remove the sandbox container."""
    def _remove():
        try:
            client = _docker_client()
            container = client.containers.get(container_name)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass  # Already gone

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _remove)
    logger.debug("Sandbox destroyed", container=container_name)
