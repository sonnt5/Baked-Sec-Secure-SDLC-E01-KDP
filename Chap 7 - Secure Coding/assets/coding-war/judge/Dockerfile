# Judge Sandbox Image
# This image is used as a sandboxed environment for compiling and running user code.
# It is NOT the Celery judge worker — it is the isolated container created per submission.
#
# Languages supported: C, C++, Python 3, Java
# Security: no network, read-only rootfs (with /tmp and /app tmpfs), dropped capabilities

FROM debian:12-slim

# Install compilers in a single layer, then clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3 \
    python3-pip \
    default-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for code execution
RUN useradd -m -u 1001 -s /bin/sh runner

# Working directory (will be tmpfs-mounted by docker create --tmpfs /app)
WORKDIR /app

# Default: keep container alive so the judge can exec into it
CMD ["sleep", "infinity"]
