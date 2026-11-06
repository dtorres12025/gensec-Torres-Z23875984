#!/usr/bin/env python3
# ==============================================================================
# Build Script for Homework 6 Submission Document (.docx) and PDF (.pdf)
# ==============================================================================
# Author:    Daniel Torres
# FAU ID:    Z23875984
# Course:    FAU COT 5930 - Security Engineering Systems with Generative AI
# Agent:     Google Antigravity (v2.0)
# Homework:  06 - Code Generation with a Coding Agent
# ==============================================================================

from __future__ import annotations

import html
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

import docx
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Metadata
STUDENT_NAME = "Daniel Torres"
FAU_ID = "Z23875984"
COURSE_NAME = "FAU COT 5930 - Security Engineering Systems with Generative AI"
ASSIGNMENT_NO = "6"
AGENT_NAME = "Google Antigravity (v2.0)"
APP_NAME = "GenSec-Sentinel: Autonomous AI Security Gateway & Adversarial Payload Firewall"
GITHUB_URL = "https://github.com/dtorres12025/gensec-Torres-Z23875984"

BASE_DIR = Path(__file__).resolve().parent.parent
HW6_DIR = Path(__file__).resolve().parent
REPO_DIR = Path("/Users/danieltorres/Documents/FAU Fall 2026/COT5930/gensec-Torres-Z23875984")
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

OUTPUT_DOCX = BASE_DIR / f"hw6-{FAU_ID}.docx"
OUTPUT_PDF = BASE_DIR / f"hw6-{FAU_ID}.pdf"

# Resolve screencast URL
SCREENCAST_URL = "https://youtu.be/PENDING_RECORDING"
screencast_files = [
    HW6_DIR / "screencast_url.txt",
    REPO_DIR / "hw6" / "screencast_url.txt",
    BASE_DIR / "screencast_url.txt",
]
for sc_path in screencast_files:
    if sc_path.exists():
        content = sc_path.read_text(encoding="utf-8").strip()
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("http"):
                SCREENCAST_URL = line
                break
        if "http" in SCREENCAST_URL:
            break

# Palette
COLOR_NAVY = RGBColor(0, 51, 102)
COLOR_STEEL = RGBColor(30, 80, 140)
COLOR_CHARCOAL = RGBColor(40, 44, 52)
COLOR_MUTED = RGBColor(90, 95, 105)


def set_cell_shading(cell, color_hex: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:left w:w="{left}" w:type="dxa"/>'
        f'  <w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def add_callout(doc: Document, title: str, text: str, border_color="003366", bg_color="F0F4F8"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_shading(cell, bg_color)
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)

    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="30" w:space="0" w:color="{border_color}"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(title)
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(9)
    r_title.font.color.rgb = COLOR_STEEL

    p_body = cell.add_paragraph()
    p_body.paragraph_format.space_before = Pt(2)
    p_body.paragraph_format.space_after = Pt(0)
    r_body = p_body.add_run(text)
    r_body.font.name = "Consolas"
    r_body.font.size = Pt(8)
    r_body.font.color.rgb = COLOR_CHARCOAL

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_screenshot_figure(doc: Document, image_path: Optional[Path], figure_label: str):
    if image_path and image_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(str(image_path), width=Inches(6.0))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(8)
        run_cap = p_cap.add_run(figure_label)
        run_cap.font.name = "Arial"
        run_cap.font.size = Pt(8)
        run_cap.font.italic = True
        run_cap.font.color.rgb = COLOR_MUTED


# ==============================================================================
# Build DOCX Document
# ==============================================================================

def build_word_document() -> Path:
    print(f"[*] Building Word submission document: {OUTPUT_DOCX}")

    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("Security (System) Engineering with Generative AI")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = COLOR_NAVY

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(4)
    r_sub = p_sub.add_run(f"Homework Assignment no. {ASSIGNMENT_NO} — Code Generation with a Coding Agent")
    r_sub.bold = True
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = COLOR_STEEL

    # Metadata Table
    table_meta = doc.add_table(rows=5, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_meta.autofit = False

    meta_items = [
        ("Student Name:", f"{STUDENT_NAME} (FAU ID: {FAU_ID})"),
        ("Coding Agent Selected:", AGENT_NAME),
        ("Application Engineered:", APP_NAME),
        ("Github Repository URL:", GITHUB_URL),
        ("Screencast Recording URL:", SCREENCAST_URL),
    ]

    for idx, (label, val) in enumerate(meta_items):
        row = table_meta.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width = Inches(2.0)
        cell_val.width = Inches(4.5)
        set_cell_margins(cell_lbl, top=40, bottom=40, left=80, right=80)
        set_cell_margins(cell_val, top=40, bottom=40, left=80, right=80)

        p_l = cell_lbl.paragraphs[0]
        p_l.paragraph_format.space_after = Pt(0)
        r_l = p_l.add_run(label)
        r_l.bold = True
        r_l.font.name = "Arial"
        r_l.font.size = Pt(9)
        r_l.font.color.rgb = COLOR_NAVY

        p_v = cell_val.paragraphs[0]
        p_v.paragraph_format.space_after = Pt(0)
        r_v = p_v.add_run(val)
        r_v.font.name = "Arial"
        r_v.font.size = Pt(9)
        if "http" in val:
            r_v.font.color.rgb = COLOR_STEEL
            r_v.underline = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 1: Executive Summary
    h1 = doc.add_heading("1. Executive Summary & Application Concept", level=1)
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(4)

    p_desc = doc.add_paragraph(
        "For Homework 6, Google Antigravity (v2.0) was utilized as an autonomous coding agent to engineer "
        "GenSec-Sentinel: Autonomous AI Security Gateway & Adversarial Payload Firewall entirely from prompts. "
        "The system acts as a hardened reverse-proxy security barrier deployed in front of Large Language Models "
        "and generative AI application backends. It intercepts, normalizes, inspects, and sanitizes inbound user "
        "prompts and external API queries, protecting the upstream LLM from prompt injection, system exfiltration, "
        "and classical exploitation vectors."
    )
    p_desc.paragraph_format.space_after = Pt(6)

    # Architecture Overview Callout
    add_callout(
        doc,
        "System Architecture & Threat Defense Flow",
        "Inbound Payload -> Layer 1: Unicode NFKC Normalization & Zero-Width Stripping (Token Smuggling Defense)\n"
        "                -> Layer 2: Multi-Layer Threat Inspection (APE Prompt Injection, CWE-78, CWE-918, CWE-79)\n"
        "                -> Layer 3: Risk Scoring (0-100) & Policy Decision (BLOCKED, SANITIZED, ALLOWED)\n"
        "                -> Layer 4: Safe Advisory Engine / Shielded Upstream LLM Dispatcher",
        border_color="003366",
        bg_color="F4F6F9",
    )

    # Section 2: Prompts Used to Create the Application
    h2 = doc.add_heading("2. Prompts Used to Create Application (Prompts Walkthrough)", level=1)
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(4)

    p_prompts_intro = doc.add_paragraph(
        "To maximize efficiency and reproducibility, the entire application was generated in three "
        "meticulously structured prompts recorded in hw6/prompts.txt:"
    )
    p_prompts_intro.paragraph_format.space_after = Pt(4)

    # Discover prompt screenshots
    screenshots = sorted(BASE_DIR.glob("Screenshot*.png")) or sorted((BASE_DIR / "screenshots").glob("Screenshot*.png")) or sorted((BASE_DIR / "screenshots").glob("Screenshot*.png"))
    sc1 = screenshots[0] if len(screenshots) > 0 else None
    sc2 = screenshots[1] if len(screenshots) > 1 else None
    sc3 = screenshots[2] if len(screenshots) > 2 else None

    # Prompt 1
    add_callout(
        doc,
        "Prompt 1: Core System Architecture, FastAPI Engine & Multi-Layer Threat Detection",
        "Act as a senior cybersecurity software engineer. Using Google Antigravity, create a secure, production-grade "
        "Python application in hw6/app.py called 'GenSec-Sentinel: Autonomous AI Security Gateway & Adversarial Payload Firewall'.\n\n"
        "The application must be built using FastAPI and Pydantic, running standalone on port 8000 (uvicorn hw6.app:app or python hw6/app.py).\n"
        "The core mission of the application is to intercept, inspect, sanitize, and evaluate inbound user queries and API requests "
        "before forwarding them to an internal LLM or security advisory engine. It must guard against both Generative AI vulnerabilities "
        "(OWASP Top 10 for LLMs) and traditional web/API exploitation vectors.\n\n"
        "In this first iteration, implement:\n"
        "1. Strongly typed Pydantic models (InspectionRequest, ThreatDetection, InspectionResult, SecurityAuditLog).\n"
        "2. A multi-layer threat detection pipeline that analyzes incoming payloads for:\n"
        "   - Adversarial Prompt Injections mapped to OWASP LLM01 and HiddenLayer APE taxonomy (system instruction overrides, narrative smuggling, jailbreaks).\n"
        "   - System Command Injections (CWE-78: shell metacharacters, forbidden diagnostic binaries like cat /etc/passwd, env, rm -rf, sudo).\n"
        "   - Cross-Site Scripting (CWE-79: script tags, malicious event handlers like onerror).\n"
        "3. Baseline defense rules: reject payloads exceeding 4096 characters (DoS/ReDoS prevention), compute a normalized threat score (0-100), "
        "and assign a policy verdict (ALLOWED, SANITIZED, or BLOCKED).\n"
        "4. FastAPI endpoints: POST /api/inspect and GET /api/health.",
        border_color="003366",
        bg_color="F8FAFC",
    )
    add_screenshot_figure(
        doc,
        sc1,
        f"Figure 2.1: Prompt 1 Execution & Architecture Generation in Google Antigravity (Student: {STUDENT_NAME} | FAU ID: {FAU_ID})",
    )

    # Prompt 2
    add_callout(
        doc,
        "Prompt 2: Adversarial Input Hardening & Threat Defense (Rubric: Defenses Against Adversarial Inputs)",
        "Refactor and harden hw6/app.py to aggressively defend against advanced adversarial inputs, bypass techniques, "
        "and obfuscation attacks that threat actors use against AI gateways.\n\n"
        "Specifically enhance the application with the following defensive security controls:\n"
        "1. Unicode Homoglyph & Smuggling Defense: Implement Unicode NFKC normalization and strip invisible zero-width "
        "characters (\\u200b, \\u200c, \\u200d, \\ufeff) before regex pattern evaluation to defeat homoglyph substitution and token smuggling.\n"
        "2. SSRF & Cloud Metadata Protection (CWE-918): Implement a strict URL/IP validator that performs DNS resolution and "
        "blocks private RFC 1918 subnets (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), loopback/localhost (127.0.0.0/8, ::1), and "
        "cloud metadata IP addresses (169.254.169.254 AWS/GCP/Azure metadata).\n"
        "3. ReDoS Protection & Recursive Delimiter Stripping: Harden all regular expressions against Regular Expression Denial "
        "of Service (ReDoS) using bounded lookaheads and non-backtracking patterns. Recursively sanitize fake LLM role delimiters "
        "(<|im_start|>, [SYSTEM], [/SYSTEM], </context>, [INST]).\n"
        "4. Safe Advisory Query Engine with Context Guard: Implement an internal mock LLM advisory query engine with strict "
        "output escaping (html.escape) and guardrails to prevent indirect prompt injection.\n"
        "5. Defense-in-Depth Audit Logging: Maintain an in-memory rotating audit log recording timestamp, client IP, detected threat "
        "categories, threat score, action taken, and SHA-256 hash of the input (to avoid logging raw adversarial payloads in cleartext).",
        border_color="003366",
        bg_color="F8FAFC",
    )
    add_screenshot_figure(
        doc,
        sc2,
        f"Figure 2.2: Prompt 2 Execution & Adversarial Input Hardening in Google Antigravity (Student: {STUDENT_NAME} | FAU ID: {FAU_ID})",
    )

    # Prompt 3
    add_callout(
        doc,
        "Prompt 3: Embedded SecOps Web Dashboard, 1-Click Presets & Capabilities Benchmark",
        "Complete hw6/app.py by adding an embedded, modern responsive SecOps Web Dashboard and a built-in automated adversarial test suite:\n\n"
        "1. Embedded Web UI at GET /: Serve a sleek, dark-themed HTML5/CSS3/JavaScript dashboard directly from FastAPI featuring:\n"
        "   - Interactive query console allowing real-time prompt analysis.\n"
        "   - 5 One-Click Adversarial Presets matching our course threat model: (1) APE HLT03.02 Narrative Smuggling, "
        "(2) CWE-78 OS Command Injection, (3) CWE-918 SSRF Cloud Metadata, (4) CWE-79 Stored/Reflected XSS, and (5) Benign Security Query.\n"
        "   - Dynamic visual feedback: animated Threat Score meter (0-100%), Verdict badges (BLOCKED/SANITIZED/ALLOWED), and triggered CWE/OWASP classification cards.\n"
        "2. Automated Adversarial Benchmark & Limitations Evaluation: Expose GET /api/benchmark and a CLI flag 'python hw6/app.py --test' "
        "that runs 6 distinct test cases. Explicitly report the application's capabilities and limitations.\n"
        "3. Self-Execution & Standalone Support: Add a main entry point so running 'python hw6/app.py' starts the server on http://127.0.0.1:8000.",
        border_color="003366",
        bg_color="F8FAFC",
    )
    add_screenshot_figure(
        doc,
        sc3,
        f"Figure 2.3: Prompt 3 Execution & SecOps Dashboard Generation in Google Antigravity (Student: {STUDENT_NAME} | FAU ID: {FAU_ID})",
    )

    # Section 3: Security Aspects & Defenses Against Adversarial Inputs
    h3 = doc.add_heading("3. Security Aspects & Adversarial Input Defenses", level=1)
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(4)

    p_sec = doc.add_paragraph(
        "The application specifically implements four defense-in-depth security layers to withstand adversarial inputs:"
    )
    p_sec.paragraph_format.space_after = Pt(4)

    sec_layers = [
        ("Layer 1 — De-obfuscation & Pre-Processing (CWE-400 / Token Smuggling):",
         "Applies unicodedata.normalize('NFKC') to map full-width and lookalike characters back to standard ASCII, "
         "strips zero-width characters (\u200b, \u200c, \u200d, \ufeff), and bounds inputs to 4096 characters to prevent buffer exhaustion and ReDoS."),
        ("Layer 2 — Adversarial Prompt Injection Defense (OWASP LLM01 / HiddenLayer APE):",
         "Inspects inputs against HiddenLayer APE taxonomy patterns, identifying Narrative Smuggling (HLT03.02), "
         "Pretexting Jailbreaks (HLT05.13), and Imperative System Overrides (HLT03.04). Catches attempts to bypass guidelines or exfiltrate system instructions."),
        ("Layer 3 — Command Injection & Metacharacter Defense (CWE-78 / OWASP LLM02):",
         "Detects shell chaining operators (;, &&, ||, |, $(...), backticks) and attempts to probe sensitive system utilities "
         "(cat /etc/passwd, env, id, whoami, rm -rf). Threat scores immediately trigger a BLOCKED verdict."),
        ("Layer 4 — Socket-Level SSRF & Cloud Metadata Protection (CWE-918):",
         "Parses target URLs, performs socket-level DNS resolution via socket.getaddrinfo to defeat DNS rebinding, and strictly blocks "
         "loopback (127.0.0.1, ::1), private RFC 1918 subnets (10/8, 172.16/12, 192.168/16), and cloud metadata endpoints (169.254.169.254)."),
    ]

    for title, desc in sec_layers:
        p_l = doc.add_paragraph()
        p_l.paragraph_format.space_before = Pt(2)
        p_l.paragraph_format.space_after = Pt(2)
        r_lt = p_l.add_run(f"• {title} ")
        r_lt.bold = True
        r_lt.font.name = "Arial"
        r_lt.font.size = Pt(8.5)
        r_ld = p_l.add_run(desc)
        r_ld.font.name = "Arial"
        r_ld.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 4: Automated Adversarial Benchmark Results
    h4 = doc.add_heading("4. Automated Adversarial Benchmark Results (100% Pass Rate)", level=1)
    h4.paragraph_format.space_before = Pt(8)
    h4.paragraph_format.space_after = Pt(4)

    table_bench = doc.add_table(rows=7, cols=6)
    table_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_bench.autofit = False

    bench_headers = ["Test ID", "Scenario Name", "Threat Classification", "Score", "Verdict", "Status"]
    col_widths = [Inches(0.8), Inches(1.8), Inches(1.9), Inches(0.7), Inches(0.8), Inches(0.5)]

    for c_idx, h_text in enumerate(bench_headers):
        cell = table_bench.rows[0].cells[c_idx]
        cell.width = col_widths[c_idx]
        set_cell_shading(cell, "003366")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor(255, 255, 255)

    bench_data = [
        ("TC-01", "Narrative Smuggling Jailbreak", "APE HLT03.02 / OWASP LLM01", "100/100", "BLOCKED", "PASS"),
        ("TC-02", "OS Command Injection & Exfil", "CWE-78 / OWASP LLM02", "100/100", "BLOCKED", "PASS"),
        ("TC-03", "SSRF Cloud Metadata Probe", "CWE-918 / IMDSv1 Probe", "75/100", "BLOCKED", "PASS"),
        ("TC-04", "Stored/Reflected XSS Injection", "CWE-79 / Cross-Site Scripting", "45/100", "SANITIZED", "PASS"),
        ("TC-05", "Unicode Homoglyph Smuggling", "Evasion / NFKC Normalization", "75/100", "BLOCKED", "PASS"),
        ("TC-06", "Benign Security Advisory Query", "Compliant Diagnostic Request", "0/100", "ALLOWED", "PASS"),
    ]

    for r_idx, row_data in enumerate(bench_data, 1):
        row = table_bench.rows[r_idx]
        bg = "F4F6F9" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            set_cell_shading(cell, bg)
            set_cell_margins(cell, top=40, bottom=40, left=60, right=60)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(7.5)
            if c_idx == 4:
                r.bold = True
                if val == "BLOCKED":
                    r.font.color.rgb = RGBColor(180, 40, 40)
                elif val == "SANITIZED":
                    r.font.color.rgb = RGBColor(180, 130, 20)
                else:
                    r.font.color.rgb = RGBColor(20, 140, 60)
            elif c_idx == 5:
                r.bold = True
                r.font.color.rgb = RGBColor(20, 140, 60)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Section 5: Capabilities and Limitations
    h5 = doc.add_heading("5. Capabilities and Limitations Analysis", level=1)
    h5.paragraph_format.space_before = Pt(8)
    h5.paragraph_format.space_after = Pt(4)

    p_cap_intro = doc.add_paragraph(
        "In accordance with the evaluation rubric, the gateway's production capabilities and known academic limitations are summarized below:"
    )
    p_cap_intro.paragraph_format.space_after = Pt(4)

    add_callout(
        doc,
        "System Capabilities (What GenSec-Sentinel Successfully Detects & Blocks)",
        "• Blocks imperative prompt injections, developer-mode triggers, and DAN jailbreak sequences (APE HLT03.04).\n"
        "• Intercepts fictional narrative smuggling and pretexting scenarios designed to bypass safety boundaries (APE HLT03.02).\n"
        "• Identifies and halts OS command injection and sensitive diagnostic command chaining (CWE-78).\n"
        "• Enforces socket-level DNS verification to defeat SSRF and cloud instance metadata theft (CWE-918).\n"
        "• Contextually neutralizes XSS payloads through safe HTML entity escaping (CWE-79).\n"
        "• Strips zero-width token smuggling characters and normalizes Unicode homoglyphs via NFKC.",
        border_color="008844",
        bg_color="F0FDF4",
    )

    add_callout(
        doc,
        "System Limitations (Known Operational Boundaries)",
        "• Heuristic regex engines cannot infer completely novel semantic paraphrases without an auxiliary transformer model (e.g. DeBERTa).\n"
        "• Stateful multi-turn prompt injection where attack tokens are distributed across separated conversational turns.\n"
        "• High-entropy encoded payloads (e.g., nested Base64 or ROT13) require pre-decoding pipeline modules to evaluate.",
        border_color="CC8800",
        bg_color="FFFBEB",
    )

    doc.save(str(OUTPUT_DOCX))
    print(f"[+] Saved Word submission document: {OUTPUT_DOCX}")
    return OUTPUT_DOCX


# ==============================================================================
# Numbered Canvas for PDF
# ==============================================================================

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#5A5F69"))

        # Running header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(
                54,
                755,
                f"COT 5930 HW{ASSIGNMENT_NO} — {STUDENT_NAME} ({FAU_ID}) | {APP_NAME[:45]}...",
            )
            self.drawRightString(612 - 54, 755, "Google Antigravity")
            self.setStrokeColor(colors.HexColor("#D0D5DD"))
            self.setLineWidth(0.5)
            self.line(54, 748, 612 - 54, 748)

        # Running footer
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawString(54, 34, f"FAU COT 5930 Security Engineering with Generative AI | Student: {STUDENT_NAME}")
        self.drawRightString(612 - 54, 34, page_str)
        self.setStrokeColor(colors.HexColor("#D0D5DD"))
        self.setLineWidth(0.5)
        self.line(54, 44, 612 - 54, 44)
        self.restoreState()


# ==============================================================================
# Build PDF Document
# ==============================================================================

def build_pdf_document() -> Path:
    print(f"[*] Building publication-grade PDF: {OUTPUT_PDF}")

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    h1_style = ParagraphStyle(
        "H1Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#003366"),
        spaceBefore=8,
        spaceAfter=4,
    )

    h2_style = ParagraphStyle(
        "H2Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#1E508C"),
        spaceBefore=6,
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#282C34"),
        spaceAfter=4,
    )

    code_style = ParagraphStyle(
        "CodeCustom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#1A1A1A"),
    )

    table_header_style = ParagraphStyle(
        "THStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TDStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#282C34"),
    )

    def make_callout_table(title: str, content: str, box_color: str, bg_color: str) -> Table:
        clean_content = content.replace("\n", "<br/>")
        p = Paragraph(f"<b><font color='{box_color}'>[{title}]</font></b><br/>{clean_content}", code_style)
        t = Table([[p]], colWidths=[504])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
                    ("LINEBEFORE", (0, 0), (0, -1), 3.0, colors.HexColor(box_color)),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return t

    story = []

    # Title block
    story.append(Paragraph("Security (System) Engineering with Generative AI", h1_style))
    story.append(Paragraph(f"Homework Assignment no. {ASSIGNMENT_NO} — Code Generation with a Coding Agent", h2_style))
    story.append(Spacer(1, 4))

    # Metadata table
    meta_data = [
        [Paragraph("<b>Student Name:</b>", body_style), Paragraph(f"{STUDENT_NAME} (FAU ID: {FAU_ID})", body_style)],
        [Paragraph("<b>Coding Agent Selected:</b>", body_style), Paragraph(AGENT_NAME, body_style)],
        [Paragraph("<b>Application Engineered:</b>", body_style), Paragraph(APP_NAME, body_style)],
        [Paragraph("<b>Github Repository:</b>", body_style), Paragraph(f"<a href='{GITHUB_URL}'>{GITHUB_URL}</a>", body_style)],
        [Paragraph("<b>Screencast Recording:</b>", body_style), Paragraph(f"<a href='{SCREENCAST_URL}'>{SCREENCAST_URL}</a>", body_style)],
    ]
    t_meta = Table(meta_data, colWidths=[130, 374])
    t_meta.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # Section 1
    story.append(Paragraph("1. Executive Summary & Application Concept", h1_style))
    story.append(
        Paragraph(
            "For Homework 6, Google Antigravity (v2.0) was utilized as an autonomous coding agent to engineer "
            "GenSec-Sentinel: Autonomous AI Security Gateway & Adversarial Payload Firewall entirely from prompts. "
            "The system acts as a hardened reverse-proxy security barrier deployed in front of Large Language Models "
            "and generative AI application backends. It intercepts, normalizes, inspects, and sanitizes inbound user "
            "prompts and external API queries, protecting the upstream LLM from prompt injection, system exfiltration, "
            "and classical exploitation vectors.",
            body_style,
        )
    )

    story.append(
        make_callout_table(
            "System Architecture & Threat Defense Flow",
            "Inbound Payload -> Layer 1: Unicode NFKC Normalization & Zero-Width Stripping (Token Smuggling Defense)\n"
            "                -> Layer 2: Multi-Layer Threat Inspection (APE Prompt Injection, CWE-78, CWE-918, CWE-79)\n"
            "                -> Layer 3: Risk Scoring (0-100) & Policy Decision (BLOCKED, SANITIZED, ALLOWED)\n"
            "                -> Layer 4: Safe Advisory Engine / Shielded Upstream LLM Dispatcher",
            "#003366",
            "#F4F6F9",
        )
    )
    story.append(Spacer(1, 6))

    # Section 2
    story.append(Paragraph("2. Prompts Used to Create Application (Prompts Walkthrough)", h1_style))
    story.append(
        Paragraph(
            "To maximize efficiency and reproducibility, the entire application was generated in three "
            "meticulously structured prompts recorded in hw6/prompts.txt:",
            body_style,
        )
    )

    screenshots = sorted(BASE_DIR.glob("Screenshot*.png")) or sorted((BASE_DIR / "screenshots").glob("Screenshot*.png"))
    sc1 = screenshots[0] if len(screenshots) > 0 else None
    sc2 = screenshots[1] if len(screenshots) > 1 else None
    sc3 = screenshots[2] if len(screenshots) > 2 else None

    cap_style = ParagraphStyle(
        "FigCap",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        alignment=1,
        textColor=colors.HexColor("#5A5F69"),
        spaceAfter=6,
    )

    story.append(
        make_callout_table(
            "Prompt 1: Core System Architecture, FastAPI Engine & Multi-Layer Threat Detection",
            "Act as a senior cybersecurity software engineer. Using Google Antigravity, create a secure, production-grade "
            "Python application in hw6/app.py called 'GenSec-Sentinel: Autonomous AI Security Gateway & Adversarial Payload Firewall'.\n"
            "Implement FastAPI and Pydantic schemas (InspectionRequest, ThreatDetection, InspectionResult), multi-layer threat detection "
            "(OWASP LLM01, CWE-78, CWE-79), payload size limit (4096 chars), threat scoring (0-100), and policy verdicts (ALLOWED, SANITIZED, BLOCKED).",
            "#003366",
            "#F8FAFC",
        )
    )
    if sc1 and sc1.exists():
        story.append(Spacer(1, 3))
        story.append(RLImage(str(sc1), width=490, height=278))
        story.append(Spacer(1, 2))
        story.append(
            Paragraph(
                f"Figure 2.1: Prompt 1 Execution in Google Antigravity (Student: {STUDENT_NAME} | FAU ID: {FAU_ID})",
                cap_style,
            )
        )
    story.append(Spacer(1, 4))

    story.append(
        make_callout_table(
            "Prompt 2: Adversarial Input Hardening & Threat Defense (Rubric Requirement)",
            "Refactor and harden hw6/app.py to aggressively defend against advanced adversarial inputs and bypass techniques.\n"
            "1. Unicode Homoglyph & Smuggling Defense: Unicode NFKC normalization and zero-width stripping (\\u200b-\\u200d\\ufeff).\n"
            "2. SSRF & Cloud Metadata Protection (CWE-918): Socket-level DNS resolution blocking private RFC 1918 subnets and cloud metadata (169.254.169.254).\n"
            "3. ReDoS Protection & Delimiter Stripping: Bounded regex patterns and recursive fake delimiter sanitization.\n"
            "4. Safe Advisory Query Engine: Strict HTML entity escaping to prevent indirect prompt injection.\n"
            "5. Rotating In-Memory Audit Telemetry with SHA-256 payload hashing.",
            "#003366",
            "#F8FAFC",
        )
    )
    if sc2 and sc2.exists():
        story.append(Spacer(1, 3))
        story.append(RLImage(str(sc2), width=490, height=278))
        story.append(Spacer(1, 2))
        story.append(
            Paragraph(
                f"Figure 2.2: Prompt 2 Execution in Google Antigravity (Student: {STUDENT_NAME} | FAU ID: {FAU_ID})",
                cap_style,
            )
        )
    story.append(Spacer(1, 4))

    story.append(
        make_callout_table(
            "Prompt 3: Embedded SecOps Dashboard, 1-Click Presets & Capabilities Benchmark",
            "Complete hw6/app.py by adding an embedded, modern responsive SecOps Web Dashboard and a built-in automated adversarial test suite:\n"
            "1. Embedded Web UI at GET /: Dark-themed HTML5/JS dashboard with 5 One-Click Presets (Narrative Smuggling, Command Injection, SSRF, XSS, Benign).\n"
            "2. Automated Adversarial Benchmark: Expose GET /api/benchmark and CLI flag 'python hw6/app.py --test' running 6 test cases.\n"
            "3. Explicitly report the application's capabilities and limitations.\n"
            "4. Standalone support: Running 'python hw6/app.py' starts uvicorn on http://127.0.0.1:8000.",
            "#003366",
            "#F8FAFC",
        )
    )
    if sc3 and sc3.exists():
        story.append(Spacer(1, 3))
        story.append(RLImage(str(sc3), width=490, height=278))
        story.append(Spacer(1, 2))
        story.append(
            Paragraph(
                f"Figure 2.3: Prompt 3 Execution in Google Antigravity (Student: {STUDENT_NAME} | FAU ID: {FAU_ID})",
                cap_style,
            )
        )
    story.append(Spacer(1, 6))

    # Section 3
    story.append(Paragraph("3. Security Aspects & Adversarial Input Defenses", h1_style))
    story.append(
        Paragraph(
            "The application specifically implements four defense-in-depth security layers to withstand adversarial inputs:\n"
            "• <b>Layer 1 — De-obfuscation & Pre-Processing (CWE-400):</b> Unicode NFKC normalization maps lookalikes to ASCII; invisible zero-width characters are stripped; max length is capped at 4096 bytes.\n"
            "• <b>Layer 2 — Adversarial Prompt Injection Defense (OWASP LLM01 / APE):</b> Identifies Narrative Smuggling (HLT03.02), Pretexting Jailbreaks (HLT05.13), and Imperative System Overrides (HLT03.04).\n"
            "• <b>Layer 3 — Command Injection Defense (CWE-78):</b> Halts shell chaining operators (;, &&, ||, |, `) and probes for diagnostic binaries (cat /etc/passwd, env, id, whoami).\n"
            "• <b>Layer 4 — Socket-Level SSRF Protection (CWE-918):</b> Performs DNS resolution via socket.getaddrinfo to defeat DNS rebinding, blocking RFC 1918 subnets and cloud metadata (169.254.169.254).",
            body_style,
        )
    )
    story.append(Spacer(1, 6))

    # Section 4: Benchmark Table
    story.append(Paragraph("4. Automated Adversarial Benchmark Results (100% Pass Rate)", h1_style))

    bench_table_data = [
        [
            Paragraph("<b>ID</b>", table_header_style),
            Paragraph("<b>Scenario Name</b>", table_header_style),
            Paragraph("<b>Threat Classification</b>", table_header_style),
            Paragraph("<b>Score</b>", table_header_style),
            Paragraph("<b>Verdict</b>", table_header_style),
            Paragraph("<b>Status</b>", table_header_style),
        ]
    ]

    for tc_id, name, cat, score, verd, status in [
        ("TC-01", "Narrative Smuggling Jailbreak", "APE HLT03.02 / OWASP LLM01", "100/100", "BLOCKED", "PASS"),
        ("TC-02", "OS Command Injection & Exfil", "CWE-78 / OWASP LLM02", "100/100", "BLOCKED", "PASS"),
        ("TC-03", "SSRF Cloud Metadata Probe", "CWE-918 / IMDSv1 Probe", "75/100", "BLOCKED", "PASS"),
        ("TC-04", "Stored/Reflected XSS Injection", "CWE-79 / Cross-Site Scripting", "45/100", "SANITIZED", "PASS"),
        ("TC-05", "Unicode Homoglyph Smuggling", "Evasion / NFKC Normalization", "75/100", "BLOCKED", "PASS"),
        ("TC-06", "Benign Security Advisory Query", "Compliant Diagnostic Request", "0/100", "ALLOWED", "PASS"),
    ]:
        bench_table_data.append(
            [
                Paragraph(tc_id, table_cell_style),
                Paragraph(f"<b>{name}</b>", table_cell_style),
                Paragraph(cat, table_cell_style),
                Paragraph(score, table_cell_style),
                Paragraph(f"<b>{verd}</b>", table_cell_style),
                Paragraph(f"<b><font color='#10B981'>{status}</font></b>", table_cell_style),
            ]
        )

    t_bench = Table(bench_table_data, colWidths=[45, 140, 155, 54, 65, 45])
    t_bench.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t_bench)
    story.append(Spacer(1, 6))

    # Section 5: Capabilities vs Limitations
    story.append(Paragraph("5. Capabilities and Limitations Analysis", h1_style))
    story.append(
        make_callout_table(
            "System Capabilities (What GenSec-Sentinel Successfully Detects & Blocks)",
            "• Blocks imperative prompt injections, developer-mode triggers, and DAN jailbreak sequences (APE HLT03.04).\n"
            "• Intercepts fictional narrative smuggling and pretexting scenarios designed to bypass safety boundaries (APE HLT03.02).\n"
            "• Identifies and halts OS command injection and sensitive diagnostic command chaining (CWE-78).\n"
            "• Enforces socket-level DNS verification to defeat SSRF and cloud instance metadata theft (CWE-918).\n"
            "• Contextually neutralizes XSS payloads through safe HTML entity escaping (CWE-79).\n"
            "• Strips zero-width token smuggling characters and normalizes Unicode homoglyphs via NFKC.",
            "#10B981",
            "#F0FDF4",
        )
    )
    story.append(Spacer(1, 4))

    story.append(
        make_callout_table(
            "System Limitations (Known Operational Boundaries)",
            "• Heuristic regex engines cannot infer completely novel semantic paraphrases without an auxiliary transformer model (e.g. DeBERTa).\n"
            "• Stateful multi-turn prompt injection where attack tokens are distributed across separated conversational turns.\n"
            "• High-entropy encoded payloads (e.g., nested Base64 or ROT13) require pre-decoding pipeline modules to evaluate.",
            "#F59E0B",
            "#FFFBEB",
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Saved publication-grade PDF: {OUTPUT_PDF}")
    return OUTPUT_PDF


def main():
    build_word_document()
    build_pdf_document()
    print("[*] Document build complete!")


if __name__ == "__main__":
    main()

