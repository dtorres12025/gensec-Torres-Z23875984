# COT 5930 Homework 6: Code Generation with a Coding Agent

**Student:** Daniel Torres  
**FAU ID:** Z23875984  
**Course:** COT 5930 - Security Engineering Systems with Generative AI (Florida Atlantic University)  
**Coding Agent:** Google Antigravity (v2.0)  
**Target Application:** GenSec-Sentinel (Autonomous AI Security Gateway & Adversarial Payload Firewall)  
**Repository URL:** [https://github.com/dtorres12025/gensec-Torres-Z23875984](https://github.com/dtorres12025/gensec-Torres-Z23875984)  
**Screencast Recording:** See `hw6/screencast_url.txt` and `hw6/screencast_script.md`  

---

## Executive Summary

In Homework 6, **Google Antigravity** was utilized as an autonomous coding agent to engineer **GenSec-Sentinel: Autonomous AI Security Gateway & Adversarial Payload Firewall** entirely from prompts. Built to defend modern LLM architectures from the exploitation vectors analyzed during Homework 5, GenSec-Sentinel acts as a hardened reverse-proxy gateway that intercepts, normalizes, inspects, and sanitizes inbound user queries and API requests before they reach upstream generative language models.

The application addresses critical threats across both the **OWASP Top 10 for Large Language Models** and classical API security vulnerabilities:
1. **OWASP LLM01: Prompt Injection & System Prompt Overrides** (e.g., HiddenLayer APE HLT03.04 Imperative Emphasis).
2. **HiddenLayer APE HLT03.02 / HLT05.13: Narrative Smuggling & Pretexting Jailbreaks**.
3. **CWE-78: OS Command Injection & Sensitive Environment Exfiltration** (`cat /etc/passwd`, `env`, shell chaining).
4. **CWE-918: Server-Side Request Forgery (SSRF) & Cloud Instance Metadata Harvesting** (`http://169.254.169.254/`).
5. **CWE-79: Cross-Site Scripting (XSS)** via contextual HTML entity escaping (`html.escape`).
6. **Evasion Defenses:** Unicode NFKC normalization and invisible zero-width character stripping (`\u200B-\u200D\uFEFF`) to prevent token smuggling.

---

## Architecture & Threat Detection Pipeline

```
  Inbound Request (Prompt / Target URL)
                    │
                    ▼
  [Layer 1: Input Pre-Processor & Normalization]
    ├── Payload Size Guard (CWE-400 / ReDoS Buffer <= 4096 chars)
    ├── Invisible Zero-Width Token Stripping (\u200b, \u200c, \ufeff)
    └── Unicode NFKC Normalization (Homoglyph De-obfuscation)
                    │
                    ▼
  [Layer 2: Multi-Layer Adversarial Inspection Engine]
    ├── APE Prompt Injection & System Override Scanner (HLT03.04 / HLT03.02)
    ├── OS Command Injection & Shell Metacharacter Scanner (CWE-78)
    ├── Socket-Level DNS SSRF & Cloud Metadata Validator (CWE-918)
    ├── Contextual Cross-Site Scripting (XSS) Sanitizer (CWE-79)
    └── Recursive LLM Context Delimiter Stripper (<|im_start|>, [SYSTEM])
                    │
                    ▼
  [Layer 3: Policy Decision & Scoring Engine]
    ├── Normalized Threat Score (0 - 100)
    └── Policy Verdict:
          ├── BLOCKED   (Threat Score >= 70 or CRITICAL severity)
          ├── SANITIZED (Threat Score 20-69, dangerous markup escaped)
          └── ALLOWED   (Threat Score < 20, clean diagnostic request)
                    │
                    ▼
  [Layer 4: Shielded Upstream Dispatcher & Embedded SecOps Web GUI]
```

---

## 3-Prompt Orchestration Sequence

The entire application was generated in **three concise, sequential prompts** recorded in `hw6/prompts.txt`:

| Prompt | Focus Area | Deliverable & Security Capabilities Implemented |
| :--- | :--- | :--- |
| **Prompt 1** | **Architecture & Foundation** | Defined FastAPI backend, Pydantic data schemas, baseline threat detection rules (APE prompt injection, CWE-78 command injection, CWE-79 XSS), and normalized risk scoring (0-100). |
| **Prompt 2** | **Adversarial Hardening** | Added Unicode NFKC normalization, zero-width token de-obfuscation, socket-level DNS resolution to defeat SSRF/cloud metadata probes (169.254.169.254), ReDoS-safe patterns, and recursive delimiter stripping. |
| **Prompt 3** | **SecOps Dashboard & Benchmark** | Built embedded dark-mode HTML5/JS dashboard at `GET /`, 5 one-click attack presets, automated 6-case adversarial benchmark suite (`--test`), and capabilities vs. limitations reporting. |

---

## Quickstart & Verification

### 1. Execute Automated Adversarial Benchmark (`--test`)
Verify all 6 test scenarios directly from the command line:
```bash
python hw6/app.py --test
# Or via uv:
uv run python hw6/app.py --test
```

### 2. Launch Interactive SecOps Web Dashboard
Start the local server on port 8000:
```bash
python hw6/app.py
# Or via uvicorn:
uvicorn hw6.app:app --host 127.0.0.1 --port 8000
```
Open your browser to: **`http://127.0.0.1:8000`**

---

## Adversarial Benchmark Results

| Test ID | Test Scenario | Threat Category | Threat Score | Policy Verdict | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **TC-01** | Narrative Smuggling Jailbreak | APE HLT03.02 / OWASP LLM01 | **100/100** | `BLOCKED` | **PASS** |
| **TC-02** | OS Command Injection & Exfiltration | CWE-78 / OWASP LLM02 | **100/100** | `BLOCKED` | **PASS** |
| **TC-03** | SSRF Cloud Metadata IMDSv1 Probe | CWE-918 / Cloud Metadata | **75/100** | `BLOCKED` | **PASS** |
| **TC-04** | Stored/Reflected XSS Injection | CWE-79 / Cross-Site Scripting | **45/100** | `SANITIZED` | **PASS** |
| **TC-05** | Unicode Homoglyph Token Smuggling | Evasion / NFKC Normalization | **75/100** | `BLOCKED` | **PASS** |
| **TC-06** | Benign Security Advisory Query | Compliant Diagnostic Request | **0/100** | `ALLOWED` | **PASS** |

---

## Capabilities & Limitations (Rubric Fulfillment)

### System Capabilities:
- **Imperative Prompt Injection Defense:** Catches direct system prompt overrides, developer-mode activations, and DAN jailbreak sequences.
- **Cognitive Narrative Smuggling:** Intercepts fictional roleplay and hypothetical pretexting attacks that attempt to bypass safety guidelines.
- **System Command Injection & Shell Metacharacters:** Flags chaining operators (`;`, `&&`, `||`, `|`, `$(...)`, backticks) and sensitive binaries (`cat /etc/passwd`, `env`, `id`, `whoami`).
- **Socket-Level SSRF Prevention:** Resolves hostnames via DNS before evaluation, strictly blocking private RFC 1918 subnets, loopback interfaces (`127.0.0.1`, `::1`), and cloud metadata (`169.254.169.254`).
- **Contextual XSS Sanitization:** Replaces raw HTML tags with safe entity encodings to prevent reflected and stored script execution.
- **Unicode Homoglyph & Invisible Character Stripping:** Normalizes full-width and lookalike unicode characters to ASCII equivalents and removes zero-width spaces.

### Academic Limitations:
- **Zero-Day Semantic Paraphrasing:** Pure lexical/heuristic regular expressions cannot detect deeply camouflaged semantic jailbreaks without a secondary neural embedding model (e.g., DeBERTa-v3 or Llama-Guard).
- **Multi-Turn Stateful Prompt Injection:** Attacks split across multiple conversational dialogue turns require a stateful conversational memory graph to reconstruct the unified adversarial context.
- **High-Entropy Encoded Payloads:** Obfuscated payloads encoded in nested base64, rot13, or custom ciphers require automated decoding pipelines before rule matching can occur.
