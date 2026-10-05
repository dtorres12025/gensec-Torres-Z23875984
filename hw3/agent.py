# Author: Daniel Torres
# FAU ID: Z12345678
# Course: COT 5930 - Security Engineering Systems with Generative AI
"""Autonomous cybersecurity agent for system diagnostics and vulnerability remediation.

This module assembles a LangGraph ReAct agent powered by either Google Gemini
(via ChatGoogleGenerativeAI) or OpenAI (via ChatOpenAI), bound with system
diagnostic inspection and security advisory tools. The agent adheres strictly
to defensive operating policies and sandboxed execution boundaries.
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

# Support relative and package execution contexts
try:
    from hw3.tools.security_advisory import query_security_advisory
    from hw3.tools.terminal_tool import execute_sandboxed_command
except ImportError:
    from tools.security_advisory import query_security_advisory
    from tools.terminal_tool import execute_sandboxed_command

# Load environment configuration (.env)
_ENV_FILE_DIR: Path = Path(__file__).resolve().parent
if (_ENV_FILE_DIR / ".env").exists():
    load_dotenv(dotenv_path=_ENV_FILE_DIR / ".env")
elif (_ENV_FILE_DIR.parent / ".env").exists():
    load_dotenv(dotenv_path=_ENV_FILE_DIR.parent / ".env")
else:
    load_dotenv()

SYSTEM_PROMPT: str = (
    "You are the COT 5930 Security Engineering Assistant (Daniel Torres / Z12345678).\n\n"
    "Mandate:\n"
    "Aid operators in system diagnostics, security hardening, and vulnerability remediation.\n\n"
    "Operating Policy:\n"
    "1. Always verify system state with 'execute_sandboxed_command' when diagnostic questions "
    "or environment inspection requests arise (e.g., system identity, OS versions, uptime, disk usage).\n"
    "2. Consult 'query_security_advisory' for defensive mitigations, risk severities, "
    "and NIST SP 800-53 control mappings for any identified or discussed vulnerabilities.\n"
    "3. Respect sandbox boundaries and never attempt to bypass command policy. Prohibited operations "
    "(such as destructive deletion, privilege escalation, output redirection, or shell piping) must "
    "never be attempted or recommended.\n"
    "4. Deliver structured, professional, and actionable defensive engineering guidance."
)


def get_security_agent(
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
    temperature: float = 0.0,
) -> CompiledStateGraph:
    """Initialize and compile the autonomous cybersecurity ReAct agent.

    Configures a chat model using Google Gemini (via ChatGoogleGenerativeAI) or
    OpenAI (via ChatOpenAI) depending on available environment keys (GOOGLE_API_KEY
    or OPENAI_API_KEY), binds the defensive advisory and terminal tools, and
    compiles the LangGraph ReAct execution graph.

    Args:
        model_name: Optional override for the language model name. Defaults to the
            AGENT_MODEL environment variable, 'gemini-3.8-flash' (Google), or
            'gpt-4o-mini' (OpenAI).
        api_key: Optional override for the API key. Defaults to GOOGLE_API_KEY or
            OPENAI_API_KEY from the environment.
        provider: Optional explicit provider selection ('google' or 'openai').
            Auto-detected based on available environment variables if not specified.
        temperature: Sampling temperature for model responses. Defaults to 0.0.

    Returns:
        CompiledStateGraph: The compiled executable LangGraph ReAct agent.

    Raises:
        ValueError: If neither GOOGLE_API_KEY nor OPENAI_API_KEY is configured.
    """
    google_key: Optional[str] = (
        api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    )
    openai_key: Optional[str] = (
        api_key or os.getenv("OPENAI_API_KEY")
    )

    # Determine LLM Provider
    selected_provider: str = provider or ("google" if google_key else ("openai" if openai_key else "google"))

    llm: BaseChatModel
    if selected_provider == "google":
        resolved_key: Optional[str] = api_key or google_key
        if not resolved_key or resolved_key.strip() == "your_google_api_key_here":
            raise ValueError(
                "GOOGLE_API_KEY is not set. Please add your Google API key to hw3/.env:\n"
                "    GOOGLE_API_KEY=AIzaSy..."
            )
        resolved_model: str = model_name or os.getenv("AGENT_MODEL", "gemini-3.8-flash")
        llm = ChatGoogleGenerativeAI(
            model=resolved_model,
            google_api_key=resolved_key,
            temperature=temperature,
        )
    elif selected_provider == "openai":
        resolved_key: Optional[str] = api_key or openai_key
        if not resolved_key or resolved_key.strip() == "your_openai_api_key_here":
            raise ValueError(
                "OPENAI_API_KEY is not set. Please add your OpenAI API key to hw3/.env:\n"
                "    OPENAI_API_KEY=sk-..."
            )
        resolved_model: str = model_name or os.getenv("AGENT_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(
            model=resolved_model,
            api_key=resolved_key,
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unsupported provider '{selected_provider}'. Must be 'google' or 'openai'.")

    # Bind defensive security tools
    tools: List[BaseTool] = [
        query_security_advisory,
        execute_sandboxed_command,
    ]

    # Assemble ReAct agent workflow graph
    agent: CompiledStateGraph = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )

    return agent


if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("COT 5930 Security Engineering Agent Initialization Test")
    print("Student: Daniel Torres | FAU ID: Z12345678")
    print("=" * 70)

    try:
        # Check available key or fallback to mock key for compilation test
        mock_key: str = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or "mock-api-key-for-initialization"
        )
        test_agent: CompiledStateGraph = get_security_agent(api_key=mock_key, provider="google")
        print("Status: Google GenAI Agent graph compiled successfully.")
        print(f"Graph Nodes: {list(test_agent.nodes.keys())}")
        print("Available Tools: query_security_advisory, execute_sandboxed_command")
    except Exception as exc:
        print(f"Agent initialization failed: {exc}", file=sys.stderr)
        sys.exit(1)
