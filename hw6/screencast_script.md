# COT 5930 Homework 6: Narrated Screencast Script (Max 5 Minutes)

**Student:** Daniel Torres  
**FAU ID:** Z23875984  
**Course:** COT 5930 - Security Engineering Systems with Generative AI (Florida Atlantic University)  
**Agent Selected:** Google Antigravity (v2.0)  
**Application:** GenSec-Sentinel (AI Security Gateway & Adversarial Payload Firewall)  
**Target Duration:** 4 minutes 45 seconds (Strictly under the 5-minute rubric limit)  

---

## Pre-Recording Checklist
- [ ] Webcam ON and positioned showing your face clearly.
- [ ] Terminal window open on the left.
- [ ] Browser window open on the right (or ready to open `http://127.0.0.1:8000`).
- [ ] VS Code / Antigravity IDE open showing the workspace and `prompts.txt`.

---

## Minute-by-Minute Script

### Part 1: Introduction & Git Checkout [0:00 – 0:30]
**Camera Cue:** Webcam ON, looking at the camera.  
**Screen Display:** Terminal showing clean directory.

> "Hello everyone. My name is Daniel Torres, FAU ID Z23875984. This is my submission screencast for Homework 6 in COT 5930: Security Engineering Systems with Generative AI.
> 
> In this assignment, our objective is to engineer a secure, functional Python application using a coding agent entirely from prompts, address adversarial input vulnerabilities, and demonstrate both its capabilities and limitations.
> 
> For my coding agent, I selected **Google Antigravity**. To begin, let's clone the homework repository directly from GitHub."

**Action on Screen:**  
Run in terminal:
```bash
git clone https://github.com/dtorres12025/gensec-Torres-Z23875984.git
cd gensec-Torres-Z23875984
ls -la hw6
```

---

### Part 2: Overview Walk-Through of `prompts.txt` [0:30 – 1:15]
**Screen Display:** Open `hw6/prompts.txt` in the editor.

> "Now let's review the main prompts in `hw6/prompts.txt` used to build **GenSec-Sentinel: Autonomous AI Security Gateway & Adversarial Payload Firewall**.
> 
> To minimize effort and maintain strict reproducibility, the application was engineered using **three sequential prompts**:
> 
> 1. **Prompt 1 establishes the Architecture & Foundation:** It instructs Antigravity to build a FastAPI service in `app.py` with strongly typed Pydantic schemas, baseline threat detection rules (OWASP LLM01, CWE-78, CWE-79), and a normalized risk score from 0 to 100.
> 
> 2. **Prompt 2 enforces Adversarial Input Hardening:** This addresses the core rubric criterion by specifically instructing the agent to defend against adversarial input attacks: Unicode homoglyphs, zero-width token smuggling, socket-level SSRF against cloud metadata, ReDoS protection, and recursive delimiter stripping.
> 
> 3. **Prompt 3 builds the SecOps Dashboard & Capabilities Benchmark:** It generates an embedded dark-mode HTML5 web console with 5 one-click attack presets and a built-in automated test suite exposed via `python hw6/app.py --test`."

---

### Part 3: Replay of Prompts in Google Antigravity [1:15 – 2:30]
**Screen Display:** Antigravity IDE / Chat interface showing the prompts and the agent's code generation responses.

> "Now, let's perform a replay of these prompts.
> 
> When Prompt 1 was executed in Google Antigravity, the agent initialized `hw6/app.py`, created the Pydantic data models for `InspectionRequest`, `ThreatDetection`, and `InspectionResult`, and structured the multi-layered inspection pipeline.
> 
> In Prompt 2, we commanded Antigravity to address adversarial bypasses. Notice how Antigravity integrated `unicodedata.normalize('NFKC')` to strip zero-width characters, implemented `socket.getaddrinfo` to resolve hostnames before socket connection to prevent DNS rebinding, and applied contextual HTML escaping to stop XSS.
> 
> Finally, in Prompt 3, Antigravity embedded the complete HTML5 and JavaScript SecOps console directly into FastAPI and built the automated benchmark suite. The entire application is self-contained in a single, robust `hw6/app.py` file with zero configuration overhead."

---

### Part 4: Security Aspects & Adversarial Input Defenses [2:30 – 3:45]
**Screen Display:** Scroll to the security logic in `hw6/app.py` (lines 140–280).

> "Let's examine how the prompts specifically address adversarial input attacks:
> 
> First, **Prompt Injection & APE Tactics (OWASP LLM01):** The engine inspects for HiddenLayer APE techniques like Narrative Smuggling (HLT03.02) and Imperative System Overrides (HLT03.04), blocking attempts like *'ignore all previous instructions'* or roleplaying unfiltered personas.
> 
> Second, **Evasion & Token Smuggling:** Attackers often use Unicode homoglyphs or invisible zero-width spaces (`\u200b`) to bypass lexical filters. Our Layer 1 pre-processor strips these invisible characters and normalizes the text to standard ASCII before regex evaluation.
> 
> Third, **SSRF & Cloud Metadata Protection (CWE-918):** If an attacker attempts to exfiltrate AWS or GCP instance credentials by supplying `http://169.254.169.254/`, the engine resolves the hostname via DNS and strictly blocks loopback, private RFC 1918 subnets, and link-local metadata ranges.
> 
> Fourth, **OS Command Injection (CWE-78):** It blocks shell metacharacters and sensitive binary probes like `cat /etc/passwd` or `env`.
> 
> Any request exceeding a threat score of 70 is immediately assigned a `BLOCKED` verdict, shielding the upstream AI model."

---

### Part 5: Live Demonstration, Capabilities & Limitations [3:45 – 5:00]
**Screen Display:** Terminal running test suite, then browser at `http://127.0.0.1:8000`.

> "Let's demonstrate the application live. First, we will run the automated adversarial benchmark from the command line:"

**Action on Screen:**  
Run in terminal:
```bash
python hw6/app.py --test
```
*(Show all 6 tests passing with 100% success rate)*

> "As you can see, all 6 automated test scenarios passed with 100% accuracy.
> 
> Now, let's launch the interactive web dashboard:"

**Action on Screen:**  
Run in terminal:
```bash
python hw6/app.py
```
Open browser to `http://127.0.0.1:8000`.

> "Here is the embedded SecOps dashboard. Let's test our presets:
> 
> 1. Click **Preset 1 (Narrative Smuggling):** Click *Execute Security Inspection*. Threat score is 100/100, verdict is **BLOCKED**, triggering APE HLT03.02 and HLT03.04 rules.
> 2. Click **Preset 2 (Command Injection):** Threat score 100/100, verdict **BLOCKED**, flagging `cat /etc/passwd` and shell chaining.
> 3. Click **Preset 3 (SSRF Cloud Metadata):** Threat score 75/100, verdict **BLOCKED**, stopping metadata exfiltration.
> 4. Click **Preset 4 (Stored XSS):** Threat score 45/100, verdict is **SANITIZED**, escaping the script tag safely.
> 5. Click **Preset 5 (Benign Query):** Threat score is 0/100, verdict is **ALLOWED**, returning safe remediation guidance.
> 
> **Capabilities vs. Limitations:**
> - **Capabilities:** As demonstrated, GenSec-Sentinel effectively intercepts prompt injections, command injections, cloud SSRF, XSS, and Unicode homoglyphs with sub-millisecond latency.
> - **Limitations:** Because it uses heuristic pattern matching, novel semantic paraphrasing without known trigger keywords requires a secondary neural model like DeBERTa. Additionally, multi-turn stateful prompt injections split across separate turns require persistent session memory to detect.
> 
> Thank you very much for watching!"
