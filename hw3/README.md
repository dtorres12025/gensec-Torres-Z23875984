# COT 5930 - Homework 3: Security Engineering Systems with Generative AI

**Student:** Daniel Torres  
**FAU ID:** Z12345678  

## Setup & Dependency Management

This project uses [`uv`](https://docs.astral.sh/uv/) for Python packaging and environment management.

### Prerequisites
- Python >= 3.11
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Environment Setup
1. Copy `.env.example` to `.env` and fill in your API credentials:
   ```bash
   cp .env.example .env
   ```
2. Create virtual environment and install dependencies:
   ```bash
   uv sync
   ```
