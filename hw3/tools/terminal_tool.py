# Author: Daniel Torres
# FAU ID: Z12345678
# Course: COT 5930 - Security Engineering Systems with Generative AI
"""Guarded terminal execution tool for non-destructive system diagnostics.

This module provides a LangChain tool enabling agents to execute safe diagnostic
commands within an isolated environment. Strict guardrails prohibit destructive,
privilege-escalating, arbitrary-write, or shell-piping commands.
"""

import os
import re
import shlex
import subprocess
from typing import List, Optional, Pattern, Set
from langchain_core.tools import tool

SECURITY_ERROR_MESSAGE: str = (
    "SECURITY ERROR: Command execution denied by sandbox policy. Prohibited operation detected."
)

# Denylist of prohibited commands, destructive utilities, and privilege escalation tools
PROHIBITED_COMMANDS: Set[str] = {
    "rm",
    "rmdir",
    "sudo",
    "dd",
    "chmod",
    "chown",
    "mv",
    "mkfs",
    "cp",
    "kill",
    "pkill",
    "killall",
    "reboot",
    "shutdown",
    "poweroff",
    "init",
    "su",
    "useradd",
    "userdel",
    "usermod",
    "passwd",
    "fdisk",
    "gdisk",
    "parted",
    "format",
    "wget",
    "curl",
    "nc",
    "netcat",
    "ncat",
    "socat",
    "sh",
    "bash",
    "zsh",
    "dash",
    "ksh",
    "csh",
    "tcsh",
    "touch",
    "truncate",
    "tee",
}

# Regex patterns matching prohibited operations (redirection, pipe-to-sh, chaining, substitution)
PROHIBITED_PATTERNS: List[Pattern[str]] = [
    re.compile(r">"),                                                            # Output redirection (> and >>)
    re.compile(r"<"),                                                            # Input redirection
    re.compile(r"\|\s*(?:/bin/|/usr/bin/)?(?:sh|bash|zsh|dash|ksh|python\d*|perl|ruby)\b", re.IGNORECASE),  # Pipe-to-shell
    re.compile(r";"),                                                            # Semicolon command chaining
    re.compile(r"&&"),                                                           # Logical AND chaining
    re.compile(r"\|\|"),                                                         # Logical OR chaining
    re.compile(r"&"),                                                            # Background operator
    re.compile(r"`"),                                                            # Backtick command substitution
    re.compile(r"\$\("),                                                         # Subshell command substitution
    re.compile(r"\${"),                                                          # Shell variable expansion
    re.compile(r"\bmkfs(?:\.\w+)?\b", re.IGNORECASE),                            # mkfs filesystem formatting
]

# Explicit allowlist of permissible non-destructive diagnostic binaries
ALLOWED_DIAGNOSTIC_COMMANDS: Set[str] = {
    "whoami",
    "uname",
    "pwd",
    "uptime",
    "python3",
    "python",
    "df",
    "id",
    "date",
    "hostname",
    "echo",
    "cat",
    "head",
    "tail",
    "ls",
    "ps",
    "grep",
    "wc",
    "env",
    "printenv",
    "which",
    "free",
    "sw_vers",
    "du",
}


def _validate_command_safety(command: str) -> Optional[str]:
    """Validate a terminal command string against security sandbox policies.

    Inspects the command string for forbidden characters, metacharacters,
    pipe-to-shell patterns, and destructive binaries. Also parses tokens
    to verify that the primary command is an approved diagnostic tool.

    Args:
        command: The terminal command string to inspect.

    Returns:
        None if the command passes all sandbox checks; otherwise, returns the
        standardized security error message.
    """
    clean_command: str = command.strip()
    if not clean_command:
        return SECURITY_ERROR_MESSAGE

    # 1. Check against prohibited regex patterns (redirections, pipe-to-sh, chaining, substitutions)
    for pattern in PROHIBITED_PATTERNS:
        if pattern.search(clean_command):
            return SECURITY_ERROR_MESSAGE

    # 2. Parse command arguments safely using POSIX shell syntax
    try:
        tokens: List[str] = shlex.split(clean_command)
    except ValueError:
        # Malformed quotes or invalid shell syntax
        return SECURITY_ERROR_MESSAGE

    if not tokens:
        return SECURITY_ERROR_MESSAGE

    # 3. Check base binary against allowlist
    base_command: str = os.path.basename(tokens[0]).lower()
    if base_command not in ALLOWED_DIAGNOSTIC_COMMANDS:
        return SECURITY_ERROR_MESSAGE

    # 4. Check all tokens against prohibited commands/utilities
    for token in tokens:
        normalized_token: str = os.path.basename(token).lower()
        if normalized_token in PROHIBITED_COMMANDS or normalized_token.startswith("mkfs"):
            return SECURITY_ERROR_MESSAGE

    return None


@tool
def execute_sandboxed_command(command: str) -> str:
    """Execute a guarded, non-destructive diagnostic terminal command in a sandbox.

    Executes approved diagnostic commands (such as 'whoami', 'uname -a', 'pwd',
    'uptime', 'python3 --version', 'df -h') with capture_output=True, text=True,
    and a strict 5-second timeout. Prohibits destructive operations (rm, dd, mkfs),
    privilege escalation (sudo, su), arbitrary write operations (chmod, chown, mv),
    output redirection (>), and pipe-to-shell patterns.

    Args:
        command: Non-destructive terminal command to execute.

    Returns:
        The command output string upon success, or a security error message if the
        command violates the sandbox policy.
    """
    # Validate command with sandbox guardrails
    security_error: Optional[str] = _validate_command_safety(command)
    if security_error is not None:
        return security_error

    try:
        parsed_args: List[str] = shlex.split(command.strip())
        result: subprocess.CompletedProcess[str] = subprocess.run(
            parsed_args,
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
            check=False,
        )

        stdout_clean: str = result.stdout.strip()
        stderr_clean: str = result.stderr.strip()

        if result.returncode == 0:
            if stdout_clean:
                return stdout_clean
            if stderr_clean:
                return stderr_clean
            return "[Command executed successfully with no output]"

        # Non-zero return code
        error_output: str = stderr_clean or stdout_clean or f"Command failed with exit code {result.returncode}"
        return f"Execution Error (Exit Code {result.returncode}):\n{error_output}"

    except subprocess.TimeoutExpired:
        return "ERROR: Command execution timed out after 5 seconds."
    except FileNotFoundError:
        return f"ERROR: Command executable not found: {command}"
    except subprocess.SubprocessError as err:
        return f"ERROR: Subprocess execution failed: {str(err)}"
    except Exception as err:
        return f"ERROR: Unexpected error occurred during execution: {str(err)}"
