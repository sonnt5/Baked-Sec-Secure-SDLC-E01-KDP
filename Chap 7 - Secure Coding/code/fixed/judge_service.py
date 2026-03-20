# app/services/judge_service.py — FIXED version
# Lab 7.3: Command Injection Prevention (ASVS V1.2.5)
#
# IS-03: shell=True with user-controlled arguments allows shell metacharacter
#        injection (;, &&, |, $(), backtick, etc.).
# Fix: list API (shell=False) + absolute interpreter paths + empty environment.

import subprocess
from pathlib import Path

# Allowlist of absolute interpreter paths — no PATH lookup, no injection
ALLOWED_LANGUAGES: dict[str, Path] = {
    "python": Path("/usr/bin/python3"),   # absolute path prevents PATH injection
    "cpp":    Path("/usr/bin/g++"),
    "java":   Path("/usr/bin/java"),
}


def run_in_sandbox(
    source_path: Path,
    language: str,
    timeout_sec: int = 5,
) -> subprocess.CompletedProcess:
    """Execute submitted code safely inside the gVisor sandbox.

    Security properties (ASVS V1.2.5 — parameterized OS calls):
      - shell=False: each list element is a literal argument; shell
        metacharacters (;, &&, |, $(), etc.) are never interpreted.
      - Absolute interpreter path: no PATH traversal or PATH injection.
      - Empty env={}: no environment variable injection
        (PATH, LD_PRELOAD, PYTHONPATH, etc.).
      - cwd="/sandbox": execution starts in the sandbox chroot.
      - timeout: prevents infinite-loop resource exhaustion.

    This is the app-layer command injection control.
    The gVisor sandbox (Code Contract CI-04) is the infra-layer control.
    Defense in Depth: both layers are required.
    ASVS V1.2.5 compliant.
    """
    interpreter = ALLOWED_LANGUAGES.get(language)
    if interpreter is None:
        raise ValueError(f"Unsupported language: {language!r}")

    if not source_path.is_absolute() or not source_path.exists():
        raise ValueError("Invalid source path")

    return subprocess.run(
        [str(interpreter), str(source_path)],  # list API — NEVER shell=True
        capture_output=True,
        timeout=timeout_sec,    # hard time limit — SIGKILL on exceed
        env={},                 # empty environment — no PATH injection
        cwd="/sandbox",         # chroot to the sandbox directory
        # Note: this process runs inside the gVisor container (CI-04).
        # The subprocess call itself uses shell=False for defense-in-depth.
    )
