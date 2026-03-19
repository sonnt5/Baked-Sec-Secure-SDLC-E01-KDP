# app/services/submission_service.py — FIXED version
# Lab 7.2: TOCTOU fix — atomic temp file creation (ASVS V15.4.2 compliant)
#
# Fix: tempfile.NamedTemporaryFile() creates AND opens the file in one
# atomic OS call (O_CREAT | O_EXCL internally). No window between check
# and create. The path is unpredictable — cannot be guessed by an attacker.

import tempfile
import pathlib

# Controlled directory outside /tmp — prevents cross-user symlink attacks.
# The directory must be on the same filesystem as the sandbox mount point.
SUBMISSION_TEMP_DIR = pathlib.Path("/var/submissions/tmp")
SUBMISSION_TEMP_DIR.mkdir(parents=True, exist_ok=True)


def save_and_verify_submission_safe(source_code: bytes) -> pathlib.Path:
    """Atomically create a temp file and write the submitted source code.

    Key properties (ASVS V15.4.2 — checks performed atomically):
      - NamedTemporaryFile uses O_CREAT | O_EXCL: atomic create-or-fail.
        No window between check and write.
      - Controlled directory: an attacker cannot pre-place a symlink in
        SUBMISSION_TEMP_DIR without write access to that directory.
      - Unpredictable name (NamedTemporaryFile uses secrets.token_hex
        internally on modern Python): cannot be guessed or pre-created.
      - Returns a Path object, not a string: reduces path-traversal bugs.

    The caller is responsible for deleting the file after judging completes.
    """
    with tempfile.NamedTemporaryFile(
        dir=SUBMISSION_TEMP_DIR,
        suffix=".py",
        delete=False,   # keep file after 'with' exits so judge can read it
        mode="wb",
    ) as tmp:
        tmp.write(source_code)
        # Path is only known after atomic creation — no predictable guess
        return pathlib.Path(tmp.name)
