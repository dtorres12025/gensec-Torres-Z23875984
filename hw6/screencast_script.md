# COT 5930 Homework 6: Concise Screencast Script (~3 Minutes)

**Student:** Daniel Torres | **FAU ID:** Z23875984  
**Agent:** Google Antigravity (v2.0) | **Target Runtime:** 2.5 to 3 minutes (Max 5 mins)  
**App:** GenSec-Sentinel (AI Security Gateway & Adversarial Payload Firewall)  

---

## ⚡ Quick Recording Setup
- **Webcam:** Keep face visible in corner throughout (rubric requirement).
- **Screen:** Terminal on left, Browser on right (`http://127.0.0.1:8000`).
- **Editor:** Have `hw6/prompts.txt` and `hw6/app.py` open in background.

---

### Step 1: Intro & Git Checkout [0:00 – 0:30]
**Show:** Webcam ON + Terminal.  
**Action:** Run:
```bash
git clone https://github.com/dtorres12025/gensec-Torres-Z23875984.git
cd gensec-Torres-Z23875984
ls -la hw6
```
**Say:**
> "Hi, I'm **Daniel Torres**, FAU ID **Z23875984**, presenting Homework 6 for **COT 5930: Security Engineering with Generative AI**.
> Today I'm demonstrating **GenSec-Sentinel**, an autonomous AI Security Gateway and payload firewall built entirely from prompts using **Google Antigravity**.
> Here is my clean git repository clone."

---

### Step 2: 3-Prompt Workflow & Replay [0:30 – 1:10]
**Show:** Switch to editor with `hw6/prompts.txt`, then briefly show the Antigravity chat interface / screenshots with your FAU ID visible.  
**Say:**
> "The entire application was generated in **three sequential prompts**:
> - **Prompt 1:** Built the FastAPI architecture, Pydantic schemas, and baseline threat inspection pipeline.
> - **Prompt 2 (Adversarial Hardening):** Implemented defenses against adversarial inputs: Unicode homoglyphs, zero-width token smuggling, socket-level SSRF against cloud metadata, and ReDoS protection.
> - **Prompt 3:** Generated our embedded SecOps dashboard and automated 6-case benchmark suite.
> Here is the replay in Google Antigravity showing the prompts and generated code with my FAU ID visible."

---

### Step 3: Security Defenses in Code [1:10 – 1:45]
**Show:** Scroll to `GenSecThreatEngine` in `hw6/app.py` (lines 140–300).  
**Say:**
> "Looking at `hw6/app.py`, we implemented multi-layer defenses against adversarial attacks:
> - **Prompt Injection (OWASP LLM01):** Intercepts APE narrative smuggling, system overrides, and jailbreak attempts.
> - **Token Smuggling:** Uses Unicode NFKC normalization and strips invisible zero-width characters before regex evaluation.
> - **SSRF (CWE-918):** Performs socket-level DNS resolution to strictly block cloud metadata at `169.254.169.254` and RFC 1918 private subnets.
> - **Command Injection (CWE-78):** Blocks shell metacharacters and sensitive diagnostic binaries like `cat /etc/passwd`.
> Any threat score of 70 or higher immediately triggers a `BLOCKED` policy verdict."

---

### Step 4: Live Demo (CLI Benchmark + Web Dashboard) [1:45 – 2:40]
**Show:** Terminal on left, Browser on right (`http://127.0.0.1:8000`).  

**Action 1 (Terminal):**
```bash
python hw6/app.py --test
```
**Say:**
> "First, running the automated benchmark CLI: all **6 standardized test cases pass with a 100% success rate**, and it outputs our capabilities and limitations report."

**Action 2 (Browser at `http://127.0.0.1:8000`):** Click the presets in order:
1. Click **Preset 1 (Narrative Smuggling):** Score **100/100**, Verdict **BLOCKED**.
2. Click **Preset 2 (Command Injection):** Score **100/100**, Verdict **BLOCKED** (`cat /etc/passwd`).
3. Click **Preset 3 (SSRF Metadata):** Score **75/100**, Verdict **BLOCKED** (`169.254.169.254`).
4. Click **Preset 4 (Stored XSS):** Score **45/100**, Verdict **SANITIZED** (HTML entities escaped).
5. Click **Preset 5 (Benign Query):** Score **0/100**, Verdict **ALLOWED** (Advisory returned).
6. Click **`▶ Run Automated Benchmark`** button at the bottom to show the interactive results table.

**Say:**
> "On our live dashboard, each 1-click preset instantly evaluates:
> Preset 1 blocks narrative smuggling at score 100.
> Preset 2 blocks command injection.
> Preset 3 stops cloud metadata SSRF.
> Preset 4 sanitizes malicious XSS markup.
> And Preset 5 allows clean diagnostic queries.
> Clicking the benchmark button executes all 6 scenarios directly in the browser."

---

### Step 5: Capabilities, Limitations & Wrap-Up [2:40 – 3:00]
**Show:** Point to the bottom cards on the dashboard, then look at camera.  
**Say:**
> "To summarize our evaluation:
> - **Capabilities:** Real-time, deterministic mitigation of the OWASP LLM Top 10, CWE-78, CWE-918, and evasion attacks with zero external dependencies.
> - **Limitations:** Zero-day semantic paraphrasing without known trigger keywords requires an auxiliary neural embedding model, and multi-turn prompt splitting requires stateful session tracking.
> 
> All code, documentation, and prompt logs are available on GitHub. Thank you!"

---

## 📋 Spoken Word Cheat-Sheet (Under 300 Words Total)
1. *"Hi, I'm Daniel Torres, Z23875984, presenting Homework 6 for COT 5930 with Google Antigravity."*
2. *"Engineered in 3 prompts: Architecture, Adversarial Hardening (homoglyphs, SSRF, prompt injection), and SecOps Dashboard."*
3. *"Code implements Unicode NFKC normalization, socket-level DNS verification for 169.254.169.254, and CWE-78 command filtering."*
4. *"CLI benchmark passes 6 of 6 tests. Dashboard 1-click presets demonstrate real-time blocking, sanitizing, and safe advisory delivery."*
5. *"Capabilities: sub-millisecond OWASP defense. Limitations: novel semantic paraphrases need transformer embeddings. Thank you!"*
