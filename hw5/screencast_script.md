# Homework 5: Narrated Screencast Script (Under 5 Minutes)
**Course:** FAU COT 5930 - Security Engineering Systems with Generative AI  
**Assignment:** Homework 5 - Penetration Testing on Generative AI Security Applications  
**Student:** Daniel Torres  
**FAU ID:** Z23875984  
**Target Application:** Autonomous Cybersecurity Agent (LangGraph ReAct Architecture)  
**Taxonomy:** HiddenLayer Adversarial Prompt Engineering (APE) (https://ape.hiddenlayer.com/)  
**GitHub Repository:** https://github.com/dtorres12025/gensec-Torres-Z23875984  

---

### Screencast Preparation & Checklist
- [ ] **PDF Document Open:** Open `hw5-Z23875984.pdf` in full screen (in Apple Preview, Adobe Acrobat, or your browser). This is the only document you need to show on screen!
- [ ] **Camera ON Initially:** Ensure your webcam is turned on and clearly visible (in the corner or full screen) for at least the first 30 seconds as required by the rubric.
- [ ] **Zoom / Legibility:** Zoom your PDF reader to "Fit Width" or ~125%-150% so callout boxes, text, and screenshot text are crisp and legible.
- [ ] **Student FAU ID Visible:** Ensure your student FAU ID (`Z23875984`) is clearly visible in the PDF header and on the Terminal/IDE figures.
- [ ] **Length:** Target timing is 3:30 to 4:45 (Strictly under 5:00).
- [ ] **Upload:** Upload as **Unlisted** to YouTube, paste link into `hw5/screencast_url.txt`, and push to GitHub.

---

## Word-for-Word Screencast Walkthrough

### Part 1: Introduction & Target Architecture (0:00 – 0:45)
**Visual on Screen:** **Page 1 of `hw5-Z23875984.pdf`**  
*(Display top of Page 1 showing Course title, your name **Daniel Torres**, FAU ID **Z23875984**, GitHub repository URL, and the Application Description. Scroll down slightly to show **Figure 1: HiddenLayer APE Taxonomy Matrix**. Keep your webcam visible in the corner.)*

> "Hello, my name is **Daniel Torres**, FAU ID **Z23875984**, and this is my video demonstration for **Homework 5** in **COT 5930: Security Engineering Systems with Generative AI**.
>
> In this homework, I conducted systematic penetration testing against the **Autonomous Cybersecurity Agent** that I developed in Homework 3 and Homework 4. The agent is built using **LangGraph's ReAct architecture** and powered by **Google Gemini 3.8 Flash**.
>
> When I originally engineered this system, I designed it as a defensive assistant to inspect system diagnostics and query OWASP remediation patterns. I implemented a strict sandbox execution policy in `terminal_tool.py`: a denylist blocking destructive commands like `rm` and `sudo`, regex filters rejecting shell redirection and chaining, and an allowlist of 23 diagnostic utilities. I assumed that this sandbox, combined with the agent's defensive system prompt, made the application resilient against unauthorized execution.
>
> In this penetration test, I used the **HiddenLayer Adversarial Prompt Engineering (APE) Taxonomy** to show how the agent can be compromised in ways I initially did not intend or expect."

---

### Part 2: Baseline Diagnostic Verification (0:45 – 1:30)
**Visual on Screen:** **Page 2 of `hw5-Z23875984.pdf`**  
*(Display Page 2: Section 1: Baseline Verification. Point out the Diagnostic Verification Prompt callout box, the Sandboxed Tool Observation, the Defensive Agent Response, and **Figure 2: Authentic macOS Terminal capture** showing `uname -a`, `uptime`, and the student prompt `Z23875984@mac:~ %`.)*

> "First, let's look at the baseline intended operation on **Page 2**. When a user submits a standard system health inquiry—such as asking for the kernel architecture and uptime—the agent operates completely within policy.
>
> As shown in the prompt and tool observation boxes, the agent invokes `execute_sandboxed_command` with `uname -a` and `uptime`. The sandbox verifies that these binaries are on the approved allowlist, captures the non-destructive output, and the agent synthesizes a clear defensive status report.
>
> Notice in **Figure 2** my authentic macOS Terminal execution showing my student ID `Z23875984` in the prompt and terminal header. Everything here operates strictly within least privilege."

---

### Part 3: Attack 1 – Narrative Smuggling & Synonym Attack (1:30 – 2:30)
**Visual on Screen:** **Pages 3 & 4 of `hw5-Z23875984.pdf`**  
*(Start on **Page 3**: Show the Section 2 table mapping to APE `HLT03.02` & `HLT02.03`, the Adversarial Attack Prompt callout box, and **Figures 3A & 3B** showing live captures of the HiddenLayer website definitions.  
Then flip to **Page 4**: Show the Tool Execution Observation Trace for `env`, the Compromised Agent Response, **Figure 3C** showing `pentest_suite.py` with student ID in title bar, and **Figure 3D** showing the macOS Terminal dumping the credentials.)*

> "Now, turning to **Page 3**, let's demonstrate **Attack 1**: Runtime Environment and Credential Exfiltration.
>
> This attack maps to the APE taxonomy under **Cognitive Manipulation: Narrative Smuggling (`HLT03.02`)** and **Lore Abuse: Synonym Attack (`HLT02.03`)**, as shown in Figures 3A and 3B from the official HiddenLayer portal.
>
> If an attacker simply asked the agent to 'dump all secret API keys', the LLM's safety filters would trigger a refusal. To compromise execution, I crafted an adversarial prompt framing the request as a technical **POSIX system variable export compliance verification**. Instead of asking for 'secrets', I used the harmless operational synonym 'print utility env'.
>
> Now, looking at **Page 4**, look at the tool invocation trace: the agent immediately invokes `execute_sandboxed_command('env')`. Because `env` was included in my diagnostic allowlist, the sandbox check passes completely! The tool dumps the entire runtime process table: including my active `GOOGLE_API_KEY`, user account `danieltorres`, home directory paths, and session tokens. In Figure 3D you can see the terminal execution, and the agent parses and displays these credentials directly in the chat!
>
> This represents a **Critical Confidentiality Compromise (CWE-200 / OWASP LLM02)**, where an allowlisted diagnostic tool is weaponized through narrative manipulation."

---

### Part 4: Attack 2 – Sensitive Configuration Extraction via Pretexting (2:30 – 3:30)
**Visual on Screen:** **Pages 5 & 6 of `hw5-Z23875984.pdf`**  
*(Start on **Page 5**: Show Section 3: Attack 2 table, the Adversarial Pretexting Prompt callout box, **Figure 4A** showing APE Pretexting `HLT05.13`, and **Figure 4B** showing `build_hw5_docx.py`.  
Then flip to **Page 6**: Show the Tool Execution Observation Trace for `cat .env.example`, the Compromised Agent Response, and **Figure 4C** showing the macOS Terminal reading the private configuration file.)*

> "Next, on **Page 5**, is **Attack 2**: Sensitive Configuration and Architecture Extraction via **Pretexting (`HLT05.13`)** under the **Context Manipulation** tactic, shown in Figure 4A.
>
> Here, I fabricated an authoritative regulatory pretext: an automated OWASP security configuration audit. In the red prompt box, I instructed the agent to verify exposed credential placeholders by inspecting the configuration file `../gensec-Torres-Z23875984/hw3/.env.example`.
>
> Because the prompt framed this as a protective security review, the agent's defensive mandate worked against itself. Turning to **Page 6**, the agent called `execute_sandboxed_command` with `cat ../gensec-Torres-Z23875984/hw3/.env.example`. My sandbox allowlist permitted `cat` for reading diagnostic documentation, but had no path traversal restrictions. In Figure 4C you can see the tool dumped the entire configuration template verbatim—revealing student metadata, environment variables, and model parameters.
>
> This results in **High Sensitive Data Exposure (CWE-200 / OWASP LLM06)**."

---

### Part 5: Attack 3 – Host Reconnaissance via Imperative Emphasis (3:30 – 4:15)
**Visual on Screen:** **Pages 7 & 8 of `hw5-Z23875984.pdf`**  
*(Start on **Page 7**: Show Section 4: Attack 3 table, the Adversarial Reconnaissance Prompt callout box, **Figure 5A** showing APE Imperative Emphasis `HLT03.04`, and **Figure 5B** showing `README.md`.  
Then flip to **Page 8**: Show the Tool Execution Observation Trace for `/etc/hosts` and `id`, the Compromised Agent Response, and **Figure 5C** showing the macOS Terminal displaying the host network resolution and administrative groups.)*

> "On **Page 7**, in **Attack 3**, I demonstrated **Imperative Emphasis (`HLT03.04`)** under Cognitive Manipulation to force the agent into performing host reconnaissance.
>
> Using imperative command phrasing in the prompt box, I directed the agent to inspect local network resolution by running `head -n 10 /etc/hosts` and process security credentials via `id`.
>
> Turning to **Page 8**, the observation trace and **Figure 5C** show that the agent executed both commands without objection. It returned local loopback aliases, internal IP mappings, and revealed that user `danieltorres` belongs to administrative and remote management groups including `admin` and `com.apple.access_ssh`.
>
> This is a severe reconnaissance enabler (**OWASP LLM01**), providing attackers with the network topology and privilege context needed for lateral movement."

---

### Part 6: Defense-in-Depth Hardening & Conclusion (4:15 – 4:45)
**Visual on Screen:** **Page 8 of `hw5-Z23875984.pdf`** (or switch webcam to full focus)  
*(Keep **Page 8** visible showing the concluding prompt `Z23875984@mac:Homework 05 %` and Figure 5C while delivering the conclusion. You can also enlarge your webcam window.)*

> "To remediate these vulnerabilities and harden agentic AI systems against APE attacks, three primary defensive controls should be implemented:
> 1. **Path Sandboxing:** Restrict file reading utilities strictly to an isolated canonical directory and disallow relative path navigation (`../`).
> 2. **Output Sanitization & Redaction:** Implement automated regex filtering in `terminal_tool.py` that intercepts and redacts API keys, tokens, and passwords before returning output to the LLM context.
> 3. **Dual-LLM Intent Classification:** Deploy an independent guardrail judge model to evaluate user intent against APE attack patterns before routing commands to execution tools.
>
> All attack traces, reproducible test suites, and this finalized PDF report are pushed to my course GitHub repository.
>
> Thank you!"

---

### Screencast Video Submission Steps
1. Record your screen and webcam using QuickTime Player, OBS Studio, or Zoom.
2. Verify audio clarity and check that the recording is under 5 minutes.
3. Upload to your YouTube channel as **Unlisted**.
4. Paste the YouTube link into `hw5/screencast_url.txt`.
5. Run `uv run --with python-docx --with reportlab --with pillow python3 hw5/build_hw5_docx.py`.
6. Commit and push the updated repository:
   ```bash
   git add hw5 screenshots hw5-Z23875984.docx hw5-Z23875984.pdf
   git commit -m "docs(hw5): update screencast recording URL and finalized PDF submission"
   git push
   ```
