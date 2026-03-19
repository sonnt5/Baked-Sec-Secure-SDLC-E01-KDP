# app/services/submission_service.py — VULNERABLE version
# Lab 7.2: TOCTOU vulnerability (ASVS V15.4.2 violation)
# DO NOT USE IN PRODUCTION — educational purposes only
#
# Bug: check-then-use on a filesystem path is not atomic.
# Attacker can replace the path with a symlink between T1 (check) and T2 (open),
# causing the write to target an attacker-controlled file.

import os


def save_and_verify_submission(source_code: bytes, submission_id: str) -> str:
    """Save submitted source code to a temporary file for the judge.

    BUG (TOCTOU — ASVS V15.4.2):
      T1: os.path.exists() check
      GAP: attacker replaces path with symlink → /etc/passwd or /judge/test_cases/*.txt
      T2: open() writes to the attacker's symlink target

    If the judge process has write access to sensitive files, this can:
      - Overwrite test cases → contest integrity failure
      - Overwrite application config → potential RCE
    """
    temp_path = f"/tmp/submission_{submission_id}.py"

    # T1: Check if path is "safe"
    if os.path.exists(temp_path):
        raise FileExistsError(f"Temp file already exists: {temp_path}")

    # ← TOCTOU gap: attacker can create a symlink here ←

    # T2: Write to path (now potentially an attacker-controlled symlink target)
    with open(temp_path, "wb") as f:  # Could write to attacker-controlled file
        f.write(source_code)

    return temp_path  # Predictable path → enumerable by attacker
