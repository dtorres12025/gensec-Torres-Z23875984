# COT 5930 Homework 4: Model Context Protocol (MCP) Agent & Custom MCP Server

**Student:** Daniel Torres  
**FAU ID:** Z23875984  
**Course:** FAU COT 5930 - Security Engineering Systems with Generative AI  
**Repository:** [gensec-Torres-Z23875984](https://github.com/dtorres12025/gensec-Torres-Z23875984)

## Overview
This homework implements an AI agent that interfaces with two Model Context Protocol (MCP) servers:
1. **Custom FastMCP Server (`mcp-server.py`)**: Exposes security analysis tools (`analyze_vulnerability_risk`, `generate_hardened_patch`, `evaluate_code_diff_security`) and an MCP prompt template.
2. **Published Git MCP Server (`mcp-server-git`)**: Official Model Context Protocol git server providing repository inspection tools (`git_status`, `git_log`, `git_diff`).

## Project Setup
Install dependencies using `uv`:
```bash
uv sync
```
