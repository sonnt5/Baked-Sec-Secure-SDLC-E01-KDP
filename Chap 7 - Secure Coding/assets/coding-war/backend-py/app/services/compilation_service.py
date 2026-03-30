"""
Compilation Service
Equivalent to: backend/src/services/compilationService.ts
Multi-language code compilation inside Docker sandbox.
"""

from app.services.docker_sandbox import exec_in_sandbox, write_to_sandbox
from app.utils.logger import get_logger

logger = get_logger("compilation_service")

# Language → compile commands
COMPILE_COMMANDS: dict[str, dict] = {
    "C": {
        "source_file": "/app/solution.c",
        "output_file": "/app/solution",
        "compile_cmd": ["gcc", "-o", "/app/solution", "/app/solution.c", "-O2", "-lm", "-std=c17"],
    },
    "CPP": {
        "source_file": "/app/solution.cpp",
        "output_file": "/app/solution",
        "compile_cmd": ["g++", "-o", "/app/solution", "/app/solution.cpp", "-O2", "-std=c++20"],
    },
    "PYTHON": {
        "source_file": "/app/solution.py",
        "output_file": None,  # Interpreted
        "compile_cmd": ["python3", "-m", "py_compile", "/app/solution.py"],
    },
    "JAVA": {
        "source_file": "/app/Solution.java",
        "output_file": "/app/Solution.class",
        "compile_cmd": ["javac", "/app/Solution.java"],
    },
}

# Language → run commands
RUN_COMMANDS: dict[str, list[str]] = {
    "C": ["/app/solution"],
    "CPP": ["/app/solution"],
    "PYTHON": ["python3", "/app/solution.py"],
    "JAVA": ["java", "-cp", "/app", "Solution"],
}


async def compile_code(
    container_name: str,
    language: str,
    source_code: str,
) -> tuple[bool, str]:
    """
    Write source code and compile it inside the sandbox.
    Returns (success, error_message).
    """
    lang_config = COMPILE_COMMANDS.get(language)
    if not lang_config:
        return False, f"Unsupported language: {language}"

    # Write source code
    await write_to_sandbox(container_name, source_code, lang_config["source_file"])

    # Compile
    exit_code, stdout, stderr = await exec_in_sandbox(
        container_name,
        lang_config["compile_cmd"],
        timeout_seconds=30,
    )

    if exit_code != 0:
        error = stderr.strip() or stdout.strip()
        logger.info("Compilation failed", language=language, error=error[:500])
        return False, error[:2000]  # Truncate long errors

    logger.debug("Compilation succeeded", language=language)
    return True, ""


def get_run_command(language: str) -> list[str]:
    """Get the run command for a language."""
    return RUN_COMMANDS.get(language, ["echo", "unsupported"])
