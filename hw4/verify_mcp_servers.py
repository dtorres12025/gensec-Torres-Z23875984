# Author: Daniel Torres
# FAU ID: Z23875984
# Course: COT 5930 - Security Engineering Systems with Generative AI

"""MCP Multi-Server Verification Script.

This module validates concurrent stdio client connections to:
1. Custom FastMCP Server: SecurityAuditServer (hw4/mcp-server.py)
2. Published MCP Server: Git Server (mcp-server-git via python -m mcp_server_git)

It uses contextlib.AsyncExitStack to establish asynchronous client sessions,
adapts the tools into unified LangChain tool interfaces via langchain_mcp_adapters,
and executes live validation tool calls against both servers.
"""

from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment configuration
load_dotenv()

# Determine default target repository path
DEFAULT_REPO_PATH = Path(
    os.getenv(
        "TARGET_REPO_PATH",
        "/Users/danieltorres/Documents/FAU Fall 2026/COT5930/gensec-Torres-Z23875984",
    )
).resolve()


def _resolve_server_script_path() -> Path:
    """Resolve the absolute path to hw4/mcp-server.py.

    Returns:
        Path to mcp-server.py.

    Raises:
        FileNotFoundError: If the script cannot be located.
    """
    candidates = [
        Path(__file__).parent / "mcp-server.py",
        Path.cwd() / "hw4" / "mcp-server.py",
        Path.cwd() / "mcp-server.py",
        Path("/Users/danieltorres/Documents/FAU Fall 2026/COT5930/gensec-Torres-Z23875984/hw4/mcp-server.py"),
        Path("/Users/danieltorres/Documents/FAU Fall 2026/COT5930/Homework 04 - MCP/hw4/mcp-server.py"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    raise FileNotFoundError("Could not locate hw4/mcp-server.py in search paths.")


async def verify_mcp_connectivity(repo_path: Path) -> Dict[str, Any]:
    """Connect concurrently to custom and git MCP servers, load tools, and execute tests.

    Args:
        repo_path: Path to the target Git repository for git operations.

    Returns:
        A dictionary containing verification metrics, tools list, and test results.
    """
    server_script = _resolve_server_script_path()
    python_exe = sys.executable

    print("\n" + "=" * 80)
    print("COT 5930: MCP Multi-Server Concurrent Client Verification")
    print("Student: Daniel Torres | FAU ID: Z23875984")
    print("=" * 80)
    print(f"[*] Python Interpreter : {python_exe}")
    print(f"[*] Custom MCP Server  : {server_script}")
    print(f"[*] Target Git Repo    : {repo_path}")
    print("=" * 80 + "\n")

    # Inherit system environment for child server processes
    server_env = os.environ.copy()
    server_env["PYTHONUNBUFFERED"] = "1"
    server_env["FASTMCP_SHOW_SERVER_BANNER"] = "False"

    # Configure stdio server parameters for Custom Security Server
    custom_server_params = StdioServerParameters(
        command=python_exe,
        args=[str(server_script), "stdio"],
        env=server_env,
    )

    # Configure stdio server parameters for published Git MCP Server
    git_server_params = StdioServerParameters(
        command=python_exe,
        args=["-m", "mcp_server_git", "--repository", str(repo_path)],
        env=server_env,
    )

    results: Dict[str, Any] = {
        "custom_tools": [],
        "git_tools": [],
        "total_tools": 0,
        "custom_test_status": "FAILED",
        "git_test_status": "FAILED",
        "custom_test_output": None,
        "git_test_output": None,
    }

    async with AsyncExitStack() as stack:
        print("[+] Connecting to Custom SecurityAuditServer via stdio...")
        custom_read, custom_write = await stack.enter_async_context(
            stdio_client(custom_server_params)
        )
        custom_session = await stack.enter_async_context(
            ClientSession(custom_read, custom_write)
        )
        await custom_session.initialize()
        print("[✓] Custom SecurityAuditServer initialized successfully.")

        print("[+] Connecting to published Git MCP Server via stdio...")
        git_read, git_write = await stack.enter_async_context(
            stdio_client(git_server_params)
        )
        git_session = await stack.enter_async_context(
            ClientSession(git_read, git_write)
        )
        await git_session.initialize()
        print("[✓] Published Git MCP Server initialized successfully.")

        # Adapt MCP sessions into unified LangChain tools
        print("\n[+] Dynamically adapting MCP server capabilities via langchain_mcp_adapters...")
        custom_tools = await load_mcp_tools(custom_session)
        git_tools = await load_mcp_tools(git_session)

        custom_tool_names = [t.name for t in custom_tools]
        git_tool_names = [t.name for t in git_tools]
        all_tools = custom_tools + git_tools

        results["custom_tools"] = custom_tool_names
        results["git_tools"] = git_tool_names
        results["total_tools"] = len(all_tools)

        print(f"[✓] Custom Tools ({len(custom_tools)}): {custom_tool_names}")
        print(f"[✓] Git Tools    ({len(git_tools)}): {git_tool_names}")
        print(f"[✓] Total Unified LangChain Tools Loaded: {len(all_tools)}")

        # Verification 1: Verify Custom Security Server Tool Schema
        EXPECTED_CUSTOM = {
            "analyze_vulnerability_risk",
            "generate_hardened_patch",
            "evaluate_code_diff_security",
        }
        missing_custom = EXPECTED_CUSTOM - set(custom_tool_names)
        if missing_custom:
            raise AssertionError(f"Custom server missing expected tools: {missing_custom}")

        # Verification 2: Verify Published Git Server Core Tools
        EXPECTED_GIT = {"git_status", "git_log", "git_diff"}
        missing_git = EXPECTED_GIT - set(git_tool_names)
        if missing_git:
            raise AssertionError(f"Git server missing expected tools: {missing_git}")

        # Live Test Invocation 1: Custom Server analyze_vulnerability_risk
        print("\n" + "-" * 80)
        print("[*] LIVE TEST 1: Invoking 'analyze_vulnerability_risk' on Custom MCP Server...")
        risk_tool = next(t for t in custom_tools if t.name == "analyze_vulnerability_risk")
        risk_output = await risk_tool.ainvoke({"vulnerability_type": "sql_injection"})

        # Extract text content if wrapped
        raw_text = risk_output
        if isinstance(risk_output, list) and risk_output:
            raw_text = getattr(risk_output[0], "text", str(risk_output[0]))
        elif hasattr(risk_output, "content"):
            raw_text = risk_output.content

        results["custom_test_output"] = raw_text
        results["custom_test_status"] = "PASSED"
        print("[✓] Custom Tool Response:")
        try:
            parsed_json = json.loads(raw_text)
            print(json.dumps(parsed_json, indent=2))
        except Exception:
            print(raw_text)

        # Live Test Invocation 2: Git Server git_status
        print("\n" + "-" * 80)
        print("[*] LIVE TEST 2: Invoking 'git_status' on Published Git MCP Server...")
        status_tool = next(t for t in git_tools if t.name == "git_status")
        # git_status accepts repo_path if defined in tool schema
        call_args = {"repo_path": str(repo_path)} if "repo_path" in status_tool.args else {}
        status_output = await status_tool.ainvoke(call_args)

        git_raw_text = status_output
        if isinstance(status_output, list) and status_output:
            git_raw_text = getattr(status_output[0], "text", str(status_output[0]))
        elif hasattr(status_output, "content"):
            git_raw_text = status_output.content

        results["git_test_output"] = git_raw_text
        results["git_test_status"] = "PASSED"
        print("[✓] Git Tool Response:")
        print(git_raw_text)

    # Print Final Formatted Summary Report
    print("\n" + "=" * 80)
    print("CONCURRENT MCP SERVERS VERIFICATION REPORT")
    print("=" * 80)
    print(f"Lead Student Auditor : Daniel Torres (FAU ID: Z23875984)")
    print(f"Custom Server Tools  : {len(results['custom_tools'])} tools loaded -> {results['custom_test_status']}")
    print(f"Git Server Tools     : {len(results['git_tools'])} tools loaded -> {results['git_test_status']}")
    print(f"Total Unified Tools  : {results['total_tools']} tools verified")
    print("Integration Status   : ALL CONCURRENT MCP CLIENT TESTS PASSED")
    print("=" * 80 + "\n")

    return results


def main() -> None:
    """Entry point for command line execution."""
    target_repo = DEFAULT_REPO_PATH
    if len(sys.argv) > 1:
        target_repo = Path(sys.argv[1]).resolve()

    if not target_repo.exists():
        print(f"Error: Target repository directory does not exist: {target_repo}")
        sys.exit(1)

    try:
        asyncio.run(verify_mcp_connectivity(target_repo))
    except Exception as exc:
        print(f"\n[!] Verification failed with error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
