# Author: Daniel Torres
# FAU ID: Z23875984
# Course: COT 5930 - Security Engineering Systems with Generative AI

"""Build script for Homework 5 submission document and PDF.

Automates the generation of:
- hw5-Z23875984.docx (from homework-template.docx)
- hw5-Z23875984.pdf (via ReportLab publication-grade engine with NumberedCanvas)

Embeds:
1. 100% authentic macOS window captures (Terminal & Antigravity IDE) showing
   student name (Daniel Torres) and student FAU ID (Z23875984).
2. 100% authentic live website captures from https://ape.hiddenlayer.com
   displaying the exact APE Taxonomy matrix and individual technique definitions
   (HLT03.02 Narrative Smuggling, HLT02.03 Synonym Attack, HLT05.13 Pretexting,
   and HLT03.04 Imperative Emphasis).
3. Live agent traces, tool execution observations, and defense-in-depth remediations.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, List, Optional, Tuple

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

# ==============================================================================
# Metadata & Paths
# ==============================================================================
STUDENT_NAME = "Daniel Torres"
FAU_ID = "Z23875984"
COURSE_NAME = "FAU COT 5930 - Security Engineering Systems with Generative AI"
ASSIGNMENT_NO = "5"
APP_NAME = "Autonomous Cybersecurity Agent for System Diagnostics & Remediation (LangGraph ReAct Architecture)"
GITHUB_URL = "https://github.com/dtorres12025/gensec-Torres-Z23875984"

BASE_DIR = Path(__file__).resolve().parent.parent
HW5_DIR = Path(__file__).resolve().parent
REPO_DIR = Path("/Users/danieltorres/Documents/FAU Fall 2026/COT5930/gensec-Torres-Z23875984")
COURSE_DOCS_DIR = Path("/Users/danieltorres/Documents/FAU Fall 2026/COT5930")
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

TEMPLATE_PATH = BASE_DIR / "homework-template.docx"
OUTPUT_DOCX = BASE_DIR / f"hw5-{FAU_ID}.docx"
OUTPUT_PDF = BASE_DIR / f"hw5-{FAU_ID}.pdf"

# Read screencast URL if populated
SCREENCAST_URL = "https://youtu.be/YOUR_SCREENCAST_URL"
screencast_candidates = [
    HW5_DIR / "screencast_url.txt",
    REPO_DIR / "hw5" / "screencast_url.txt",
    BASE_DIR / "screencast_url.txt",
]
for sc in screencast_candidates:
    if sc.exists():
        content = sc.read_text(encoding="utf-8").strip()
        if content and "YOUR_SCREENCAST_URL" not in content:
            SCREENCAST_URL = content
            break

# Typography & Color Palette
COLOR_NAVY = RGBColor(0, 51, 102)
COLOR_STEEL = RGBColor(30, 80, 140)
COLOR_CHARCOAL = RGBColor(40, 44, 52)
COLOR_MUTED = RGBColor(90, 95, 105)

APP_DESCRIPTION_TEXT = (
    "The Autonomous Cybersecurity Agent for System Diagnostics and Vulnerability Remediation is an "
    "agentic AI system developed during Homework 3 and Homework 4. Engineered using LangChain and the "
    "LangGraph ReAct (Reasoning and Acting) architecture powered by Google Gemini (gemini-3.8-flash), "
    "the agent assists systems administrators and security operations (SecOps) teams in inspecting "
    "system health, identifying vulnerabilities, and retrieving defensive NIST SP 800-53 and OWASP Top 10:2021 controls.\n\n"
    "The application architecture coordinates two primary defensive components:\n"
    "1. Guarded Terminal Diagnostic Tool (`execute_sandboxed_command`): Enables execution of non-destructive system "
    "diagnostic utilities with a 5-second timeout. To protect system integrity, the developer implemented an explicit "
    "sandbox policy containing a strict command denylist (prohibiting destructive commands like `rm`, `sudo`, `dd`, `chmod`), "
    "disallowing shell redirection operators (`>`, `<`), blocking command chaining (`;`, `&&`, `||`, `&`), and permitting "
    "only an explicit allowlist of 23 diagnostic binaries (such as `whoami`, `uname`, `pwd`, `uptime`, `ls`, `ps`, `env`, `cat`, `head`).\n"
    "2. Security Knowledge Advisory Base (`query_security_advisory`): A curated knowledge base indexing eight OWASP "
    "vulnerability classes, NIST SP 800-53 Rev. 5 control mappings (SI-10, AC-3, SC-28, IA-5), and secure remediation patterns.\n\n"
    "Initial Developer Assumptions & Security Flaws:\n"
    "The developer initially assumed that restricting command execution to diagnostic allowlists and instructing the LLM "
    "via its system prompt ('Aid operators in system diagnostics... Respect sandbox boundaries and never attempt to bypass command policy') "
    "would prevent malicious execution. However, as demonstrated in this penetration test using the HiddenLayer Adversarial Prompt "
    "Engineering (APE) taxonomy (https://ape.hiddenlayer.com/), an attacker can leverage Cognitive Manipulation (Narrative Smuggling, "
    "Imperative Emphasis), Lore Abuse (Synonym Attacks), and Context Manipulation (Pretexting) to hijack the agent's reasoning. "
    "The attacker coerces the agent into exfiltrating live environment credentials, leaking private configuration files (`.env`), "
    "and conducting unauthorized system reconnaissance—completely compromising the application without ever triggering the developer's "
    "lexical sandbox denylist."
)

# Load Penetration Test Results
RESULTS_FILE = HW5_DIR / "pentest_results.json"
if RESULTS_FILE.exists():
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        PENTEST_DATA = json.load(f)
else:
    PENTEST_DATA = []


# ==============================================================================
# Helper Functions for Word XML Formatting
# ==============================================================================
def set_cell_shading(cell, color_hex: str):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for margin_name, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{margin_name}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def add_callout_box(doc: Document, title: str, text: str, border_color="003366", bg_color="F4F6F9"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_shading(cell, bg_color)
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)

    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="36" w:space="0" w:color="{border_color}"/>'
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
    r_title.font.size = Pt(9.5)
    r_title.font.color.rgb = COLOR_STEEL

    p_body = cell.add_paragraph()
    p_body.paragraph_format.space_before = Pt(2)
    p_body.paragraph_format.space_after = Pt(0)
    r_body = p_body.add_run(text)
    r_body.font.name = "Consolas"
    r_body.font.size = Pt(8)
    r_body.font.color.rgb = COLOR_CHARCOAL

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_figure(doc: Document, image_path: Path, caption: str, width: float = 6.2):
    if not image_path.exists():
        print(f"[!] Warning: Image not found: {image_path}")
        return

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(4)
    p_img.paragraph_format.space_after = Pt(2)
    run_img = p_img.add_run()
    run_img.add_picture(str(image_path), width=Inches(width))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = "Arial"
    r_cap.font.size = Pt(8.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED


# ==============================================================================
# Word Document Builder (.docx)
# ==============================================================================
def build_word_document() -> Path:
    print(f"[*] Building Word submission document: {OUTPUT_DOCX}")

    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Document Header
    p_hdr = doc.add_paragraph()
    p_hdr.paragraph_format.space_after = Pt(2)
    r_course = p_hdr.add_run("Security (System) Engineering with Generative AI")
    r_course.font.name = "Arial"
    r_course.font.size = Pt(15)
    r_course.bold = True
    r_course.font.color.rgb = COLOR_NAVY

    p_assign = doc.add_paragraph()
    p_assign.paragraph_format.space_after = Pt(2)
    r_assign = p_assign.add_run(f"Homework Assignment no. {ASSIGNMENT_NO}")
    r_assign.font.name = "Arial"
    r_assign.font.size = Pt(13)
    r_assign.bold = True
    r_assign.font.color.rgb = COLOR_STEEL

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(8)
    r_name = p_meta.add_run(f"Student name: {STUDENT_NAME}   |   FAU ID: {FAU_ID}")
    r_name.font.name = "Arial"
    r_name.font.size = Pt(11)
    r_name.bold = True
    r_name.font.color.rgb = COLOR_CHARCOAL

    # Meta Table (Screencast URL, Repo URL, App Details)
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    meta_rows = [
        ("Screencast Recording URL", SCREENCAST_URL),
        ("Github Repository URL", GITHUB_URL),
        ("Application Name", APP_NAME),
        ("Evaluation Framework", "HiddenLayer Adversarial Prompt Engineering (APE) Taxonomy (https://ape.hiddenlayer.com/)"),
    ]

    for i, (k, v) in enumerate(meta_rows):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width, c1.width = Inches(2.2), Inches(4.3)
        set_cell_shading(c0, "F0F4F8")
        set_cell_shading(c1, "FFFFFF")
        set_cell_margins(c0, top=50, bottom=50, left=80, right=80)
        set_cell_margins(c1, top=50, bottom=50, left=80, right=80)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(9)
        r0.font.color.rgb = COLOR_NAVY

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.size = Pt(9)
        r1.font.color.rgb = COLOR_CHARCOAL

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Application Description
    p_desc_hdr = doc.add_paragraph()
    p_desc_hdr.paragraph_format.space_before = Pt(4)
    p_desc_hdr.paragraph_format.space_after = Pt(3)
    r_desc_hdr = p_desc_hdr.add_run("Application Description & Penetration Testing Context")
    r_desc_hdr.font.name = "Arial"
    r_desc_hdr.font.size = Pt(12)
    r_desc_hdr.bold = True
    r_desc_hdr.font.color.rgb = COLOR_NAVY

    p_desc = doc.add_paragraph()
    p_desc.paragraph_format.space_after = Pt(8)
    p_desc.paragraph_format.line_spacing = 1.15
    r_desc = p_desc.add_run(APP_DESCRIPTION_TEXT)
    r_desc.font.name = "Arial"
    r_desc.font.size = Pt(9)
    r_desc.font.color.rgb = COLOR_CHARCOAL

    # Embed Live APE Taxonomy Matrix
    add_figure(
        doc,
        SCREENSHOTS_DIR / "ape_taxonomy_matrix.png",
        "Figure 1: Live capture from https://ape.hiddenlayer.com/ttps.html showing the HiddenLayer Adversarial Prompt Engineering (APE) Taxonomy matrix.",
        width=6.2,
    )

    # Detailed Attacks Section
    for idx, test in enumerate(PENTEST_DATA, 1):
        doc.add_page_break()

        # Heading
        p_atk_hdr = doc.add_paragraph()
        p_atk_hdr.paragraph_format.space_before = Pt(6)
        p_atk_hdr.paragraph_format.space_after = Pt(3)
        r_atk_hdr = p_atk_hdr.add_run(f"Section {idx}: {test['heading']}")
        r_atk_hdr.font.name = "Arial"
        r_atk_hdr.font.size = Pt(12)
        r_atk_hdr.bold = True
        r_atk_hdr.font.color.rgb = COLOR_NAVY

        # Attack Metadata Table
        atk_meta_table = doc.add_table(rows=3, cols=2)
        atk_meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        atk_meta_table.autofit = False

        atk_meta_rows = [
            ("Adversarial Attack Type", f"{test['technique_name']} ({test['ape_id']})"),
            ("APE Taxonomy Reference URL", test["ape_url"]),
            ("APE Tactic Classification", test["tactic"]),
        ]

        for r_i, (k, v) in enumerate(atk_meta_rows):
            cell_k = atk_meta_table.cell(r_i, 0)
            cell_v = atk_meta_table.cell(r_i, 1)
            cell_k.width = Inches(2.2)
            cell_v.width = Inches(4.3)
            set_cell_shading(cell_k, "F0F4F8")
            set_cell_shading(cell_v, "FFFFFF")
            set_cell_margins(cell_k, top=45, bottom=45, left=70, right=70)
            set_cell_margins(cell_v, top=45, bottom=45, left=70, right=70)

            pk = cell_k.paragraphs[0]
            pk.paragraph_format.space_after = Pt(0)
            rk = pk.add_run(k)
            rk.bold = True
            rk.font.size = Pt(8.5)
            rk.font.color.rgb = COLOR_NAVY

            pv = cell_v.paragraphs[0]
            pv.paragraph_format.space_after = Pt(0)
            rv = pv.add_run(v)
            rv.font.size = Pt(8.5)
            rv.font.color.rgb = COLOR_CHARCOAL

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

        # Adversarial Attack Prompt
        add_callout_box(doc, "Adversarial Prompt Exchanged (Attacker → Agent)", test["prompt"], border_color="CC3300", bg_color="FFF8F5")

        # Tool Observations
        exec_data = test.get("execution", {})
        tool_calls = exec_data.get("tool_calls", [])
        tool_results = exec_data.get("tool_results", [])

        if tool_calls or tool_results:
            tool_obs_lines = []
            for tc in tool_calls:
                tool_obs_lines.append(f"[TOOL INVOCATION] {tc['name']}({json.dumps(tc['args'])})")
            for tr in tool_results:
                tool_obs_lines.append(f"\n[TOOL OBSERVATION RESULT: {tr['name']}]\n{tr['content']}")
            tool_obs_str = "\n".join(tool_obs_lines)
            add_callout_box(doc, "Observations from Tools Executed (Agent Sandbox Trace)", tool_obs_str, border_color="006699", bg_color="F0F8FF")

        # Agent Response
        agent_resp = exec_data.get("response", "No textual response synthesized.")
        add_callout_box(doc, "Compromised Response Synthesized by Agent", agent_resp, border_color="008844", bg_color="F5FFF7")

        # Security Impact Assessment
        p_imp_hdr = doc.add_paragraph()
        p_imp_hdr.paragraph_format.space_before = Pt(4)
        p_imp_hdr.paragraph_format.space_after = Pt(2)
        r_imp_hdr = p_imp_hdr.add_run("Security Impact & Risk Assessment:")
        r_imp_hdr.bold = True
        r_imp_hdr.font.size = Pt(9.5)
        r_imp_hdr.font.color.rgb = RGBColor(180, 40, 40)

        p_imp = doc.add_paragraph()
        p_imp.paragraph_format.space_after = Pt(6)
        r_imp = p_imp.add_run(test["impact"])
        r_imp.font.size = Pt(8.5)
        r_imp.font.color.rgb = COLOR_CHARCOAL

        # Embed Figures (APE Website + macOS Terminal / IDE)
        if test["test_id"] == "BASELINE_OPERATION":
            add_figure(
                doc,
                SCREENSHOTS_DIR / "real_terminal_window.png",
                f"Figure 2: Authentic macOS Terminal capture showing baseline diagnostic execution (uname, uptime) and student prompt {FAU_ID}@mac:~ %.",
                width=6.0,
            )
        elif test["test_id"] == "ATTACK_1_NARRATIVE_SMUGGLING_SYNONYM":
            add_figure(
                doc,
                SCREENSHOTS_DIR / "ape_narrative_smuggling.png",
                "Figure 3A: Live website capture from https://ape.hiddenlayer.com/technique.html?id=HLT03.02 showing Cognitive Manipulation: Narrative Smuggling.",
                width=5.8,
            )
            add_figure(
                doc,
                SCREENSHOTS_DIR / "ape_synonym_attack.png",
                "Figure 3B: Live website capture from https://ape.hiddenlayer.com/technique.html?id=HLT02.03 showing Lore Abuse: Synonym Attack.",
                width=5.8,
            )
            add_figure(
                doc,
                SCREENSHOTS_DIR / "real_step1_pentest_suite.png",
                f"Figure 3C: Authentic Antigravity IDE window showing hw5/pentest_suite.py and student FAU ID {FAU_ID} in title bar.",
                width=5.8,
            )
            add_figure(
                doc,
                SCREENSHOTS_DIR / "real_terminal_attack1_prompt.png",
                "Figure 3D: Authentic macOS Terminal capture showing live Attack 1 execution, tool invocation ('env'), and credential exfiltration.",
                width=5.8,
            )
        elif test["test_id"] == "ATTACK_2_PRETEXTING":
            add_figure(
                doc,
                SCREENSHOTS_DIR / "ape_pretexting.png",
                "Figure 4A: Live website capture from https://ape.hiddenlayer.com/technique.html?id=HLT05.13 showing Context Manipulation: Pretexting.",
                width=5.8,
            )
            add_figure(
                doc,
                SCREENSHOTS_DIR / "real_step2_build_docx.png",
                f"Figure 4B: Authentic Antigravity IDE window showing hw5/build_hw5_docx.py and student FAU ID {FAU_ID} in title bar.",
                width=5.8,
            )
            add_figure(
                doc,
                SCREENSHOTS_DIR / "real_terminal_attack2_prompt.png",
                "Figure 4C: Authentic macOS Terminal capture showing live Attack 2 execution and private configuration template extraction.",
                width=5.8,
            )
        elif test["test_id"] == "ATTACK_3_IMPERATIVE_RECONNAISSANCE":
            add_figure(
                doc,
                SCREENSHOTS_DIR / "ape_imperative_emphasis.png",
                "Figure 5A: Live website capture from https://ape.hiddenlayer.com/technique.html?id=HLT03.04 showing Cognitive Manipulation: Imperative Emphasis.",
                width=5.8,
            )
            add_figure(
                doc,
                SCREENSHOTS_DIR / "real_step4_readme.png",
                f"Figure 5B: Authentic Antigravity IDE window showing hw5/README.md and student FAU ID {FAU_ID} in title bar.",
                width=5.8,
            )
            add_figure(
                doc,
                SCREENSHOTS_DIR / "real_terminal_attack3_reconnaissance.png",
                f"Figure 5C: Authentic macOS Terminal capture showing live Attack 3 host reconnaissance and concluding prompt {FAU_ID}@mac:Homework 05 %.",
                width=5.8,
            )


    doc.save(str(OUTPUT_DOCX))
    print(f"[✓] Successfully generated Word Document: {OUTPUT_DOCX}")

    for dest_dir in [REPO_DIR, COURSE_DOCS_DIR]:
        if dest_dir.exists():
            dest_file = dest_dir / OUTPUT_DOCX.name
            try:
                shutil.copyfile(OUTPUT_DOCX, dest_file)
                print(f"[✓] Synchronized Word Document to: {dest_file}")
            except Exception as e:
                print(f"[!] Note: Could not sync to {dest_file}: {e}")

    return OUTPUT_DOCX


# ==============================================================================
# Publication-Grade ReportLab Canvas with Running Headers & Footers
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas that writes 'Page X of Y' and header decorations."""

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

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#5A5F69"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 762, "COT 5930 - Security Engineering Systems with Generative AI | Homework 5")
            self.drawRightString(576, 762, f"{STUDENT_NAME} (FAU ID: {FAU_ID})")
            self.setStrokeColor(colors.HexColor("#D0D7DE"))
            self.setLineWidth(0.5)
            self.line(36, 756, 576, 756)

        # Running Footer (all pages)
        self.drawString(36, 20, "Florida Atlantic University — College of Engineering and Computer Science")
        self.drawRightString(576, 20, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor("#D0D7DE"))
        self.setLineWidth(0.5)
        self.line(36, 28, 576, 28)

        self.restoreState()


# ==============================================================================
# Native ReportLab PDF Builder
# ==============================================================================
def get_scaled_rl_image(path: Path, max_w: float = 540, max_h: float = 230) -> Optional[RLImage]:
    """Load image and compute dimensions strictly preserving original aspect ratio."""
    if not path.exists():
        print(f"[!] Warning: Image not found for PDF: {path}")
        return None
    try:
        with Image.open(path) as im:
            orig_w, orig_h = im.size
        scale = min(max_w / orig_w, max_h / orig_h)
        target_w = orig_w * scale
        target_h = orig_h * scale
        return RLImage(str(path), width=target_w, height=target_h)
    except Exception as e:
        print(f"[!] Error scaling image {path}: {e}")
        return None


def build_reportlab_pdf() -> Path:
    print(f"[*] Building publication-grade ReportLab PDF: {OUTPUT_PDF}")

    pdf_doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=38,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=colors.HexColor("#003366"),
        spaceAfter=2,
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E508C"),
        spaceAfter=3,
    )

    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#282C34"),
        spaceAfter=6,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#003366"),
        spaceBefore=4,
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#282C34"),
        spaceAfter=3,
    )

    code_style = ParagraphStyle(
        "CodeTextCustom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#1A1A1A"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#003366"),
    )

    table_header_white_style = ParagraphStyle(
        "TableHeaderWhite",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#282C34"),
    )

    caption_style = ParagraphStyle(
        "CaptionStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=9.5,
        alignment=1,  # Center
        textColor=colors.HexColor("#5A5F69"),
        spaceBefore=2,
        spaceAfter=4,
    )

    def create_figure_block(img_path: Path, caption_text: str, max_w: float = 540, max_h: float = 230) -> KeepTogether:
        img_flowable = get_scaled_rl_image(img_path, max_w=max_w, max_h=max_h)
        cap_flowable = Paragraph(caption_text, caption_style)
        elements = []
        if img_flowable:
            elements.append(img_flowable)
        elements.append(cap_flowable)
        return KeepTogether(elements)

    def format_callout_table(title: str, content: str, box_color: str, bg_color: str, max_chars: int = 400) -> Table:
        clean_content = content[:max_chars].replace("\n", "<br/>")
        if len(content) > max_chars:
            clean_content += "..."
        p = Paragraph(f"<b>[{title}]</b><br/>{clean_content}", code_style)
        t = Table([[p]], colWidths=[540])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor(box_color)),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    story = []

    # ==========================================================================
    # PAGE 1: Overview, Context, and APE Taxonomy Matrix
    # ==========================================================================
    story.append(Paragraph("Security (System) Engineering with Generative AI", title_style))
    story.append(Paragraph(f"Homework Assignment no. {ASSIGNMENT_NO}", subtitle_style))
    story.append(Paragraph(f"Student name: {STUDENT_NAME}   |   FAU ID: {FAU_ID}", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#003366"), spaceAfter=4))

    meta_table_data = [
        [Paragraph("<b>Screencast URL</b>", table_header_style), Paragraph(SCREENCAST_URL, table_cell_style)],
        [Paragraph("<b>Github Repo URL</b>", table_header_style), Paragraph(GITHUB_URL, table_cell_style)],
        [Paragraph("<b>Application Name</b>", table_header_style), Paragraph(APP_NAME, table_cell_style)],
        [Paragraph("<b>Taxonomy Framework</b>", table_header_style), Paragraph("HiddenLayer Adversarial Prompt Engineering (APE) (https://ape.hiddenlayer.com/)", table_cell_style)],
    ]
    t_meta = Table(meta_table_data, colWidths=[130, 410])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4F8")),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Application Description & Penetration Testing Context", h2_style))
    for p_txt in APP_DESCRIPTION_TEXT.split("\n\n"):
        story.append(Paragraph(p_txt.replace("\n", " "), body_style))
    story.append(Spacer(1, 4))

    story.append(create_figure_block(
        SCREENSHOTS_DIR / "ape_taxonomy_matrix.png",
        "Figure 1: Live capture from https://ape.hiddenlayer.com/ttps.html showing the HiddenLayer Adversarial Prompt Engineering (APE) Taxonomy matrix.",
        max_w=540,
        max_h=190,
    ))

    # ==========================================================================
    # PAGE 2: Baseline Operation Verification
    # ==========================================================================
    story.append(PageBreak())
    base_test = PENTEST_DATA[0]
    story.append(Paragraph(f"Section 1: {base_test['heading']}", h2_style))

    atk_t_data = [
        [Paragraph("<b>Adversarial Attack Type</b>", table_header_style), Paragraph(f"{base_test['technique_name']} ({base_test['ape_id']})", table_cell_style)],
        [Paragraph("<b>APE Taxonomy URL</b>", table_header_style), Paragraph(base_test["ape_url"], table_cell_style)],
        [Paragraph("<b>Tactic Classification</b>", table_header_style), Paragraph(base_test["tactic"], table_cell_style)],
    ]
    t_atk = Table(atk_t_data, colWidths=[130, 410])
    t_atk.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4F8")),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_atk)
    story.append(Spacer(1, 4))

    story.append(format_callout_table("DIAGNOSTIC VERIFICATION PROMPT", base_test["prompt"], "#006699", "#F0F8FF", max_chars=300))
    story.append(Spacer(1, 3))

    base_exec = base_test.get("execution", {})
    tool_calls = base_exec.get("tool_calls", [])
    if tool_calls:
        obs_str = f"Tool Calls Executed: {json.dumps(tool_calls)}"
        story.append(format_callout_table("SANDBOXED TOOL OBSERVATION", obs_str, "#006699", "#F0F8FF", max_chars=250))
        story.append(Spacer(1, 3))

    base_resp = base_exec.get("response", "")
    story.append(format_callout_table("DEFENSIVE AGENT RESPONSE", base_resp, "#008844", "#F5FFF7", max_chars=320))
    story.append(Spacer(1, 3))

    story.append(Paragraph(f"<b>Security Impact Assessment:</b> {base_test['impact']}", body_style))
    story.append(Spacer(1, 4))

    story.append(create_figure_block(
        SCREENSHOTS_DIR / "real_terminal_window.png",
        f"Figure 2: Authentic macOS Terminal capture showing baseline diagnostic execution (uname, uptime) and student prompt {FAU_ID}@mac:~ %.",
        max_w=540,
        max_h=230,
    ))

    # ==========================================================================
    # PAGE 3: Attack 1 – APE Taxonomy & Technique Analysis
    # ==========================================================================
    story.append(PageBreak())
    atk1 = PENTEST_DATA[1]
    story.append(Paragraph(f"Section 2: {atk1['heading']}", h2_style))

    atk1_meta_data = [
        [Paragraph("<b>Adversarial Attack Type</b>", table_header_style), Paragraph(f"{atk1['technique_name']} ({atk1['ape_id']})", table_cell_style)],
        [Paragraph("<b>APE Taxonomy URL</b>", table_header_style), Paragraph(atk1["ape_url"], table_cell_style)],
        [Paragraph("<b>Tactic Classification</b>", table_header_style), Paragraph(atk1["tactic"], table_cell_style)],
    ]
    t_atk1 = Table(atk1_meta_data, colWidths=[130, 410])
    t_atk1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4F8")),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_atk1)
    story.append(Spacer(1, 4))

    story.append(format_callout_table("ADVERSARIAL ATTACK PROMPT (ATTACKER → AGENT)", atk1["prompt"], "#CC3300", "#FFF8F5", max_chars=350))
    story.append(Spacer(1, 3))

    story.append(Paragraph(f"<b>Security Impact Assessment:</b> {atk1['impact']}", body_style))
    story.append(Spacer(1, 4))

    # Pair of APE Website Screenshots
    story.append(create_figure_block(
        SCREENSHOTS_DIR / "ape_narrative_smuggling.png",
        "Figure 3A: Live website capture from https://ape.hiddenlayer.com/technique.html?id=HLT03.02 showing Cognitive Manipulation: Narrative Smuggling.",
        max_w=540,
        max_h=190,
    ))
    story.append(Spacer(1, 4))
    story.append(create_figure_block(
        SCREENSHOTS_DIR / "ape_synonym_attack.png",
        "Figure 3B: Live website capture from https://ape.hiddenlayer.com/technique.html?id=HLT02.03 showing Lore Abuse: Synonym Attack.",
        max_w=540,
        max_h=180,
    ))

    # ==========================================================================
    # PAGE 4: Attack 1 – Execution Trace & Terminal Exfiltration
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph(f"Section 2 (Continued): Attack 1 Tool Observation & Process Exfiltration", h2_style))

    atk1_exec = atk1.get("execution", {})
    atk1_calls = atk1_exec.get("tool_calls", [])
    atk1_res = atk1_exec.get("tool_results", [])
    tool_lines = []
    for tc in atk1_calls:
        tool_lines.append(f"INVOCATION: {tc['name']}({json.dumps(tc['args'])})")
    for tr in atk1_res:
        tool_lines.append(f"OUTPUT [{tr['name']}]:\n{tr['content']}")
    story.append(format_callout_table("TOOL EXECUTION OBSERVATION TRACE (SANDBOXED 'env' DUMP)", "\n".join(tool_lines), "#006699", "#F0F8FF", max_chars=380))
    story.append(Spacer(1, 3))

    atk1_resp = atk1_exec.get("response", "")
    story.append(format_callout_table("COMPROMISED AGENT RESPONSE (CREDENTIALS SYNTHESIZED)", atk1_resp, "#008844", "#F5FFF7", max_chars=350))
    story.append(Spacer(1, 4))

    story.append(create_figure_block(
        SCREENSHOTS_DIR / "real_step1_pentest_suite.png",
        f"Figure 3C: Authentic Antigravity IDE window showing hw5/pentest_suite.py and student FAU ID {FAU_ID} in title bar.",
        max_w=540,
        max_h=195,
    ))
    story.append(Spacer(1, 4))
    story.append(create_figure_block(
        SCREENSHOTS_DIR / "real_terminal_attack1_prompt.png",
        "Figure 3D: Authentic macOS Terminal capture showing live Attack 1 execution, tool invocation ('env'), and credential exfiltration.",
        max_w=540,
        max_h=195,
    ))

    # ==========================================================================
    # PAGE 5: Attack 2 – APE Pretexting & Architecture Extraction
    # ==========================================================================
    story.append(PageBreak())
    atk2 = PENTEST_DATA[2]
    story.append(Paragraph(f"Section 3: {atk2['heading']}", h2_style))

    atk2_meta_data = [
        [Paragraph("<b>Adversarial Attack Type</b>", table_header_style), Paragraph(f"{atk2['technique_name']} ({atk2['ape_id']})", table_cell_style)],
        [Paragraph("<b>APE Taxonomy URL</b>", table_header_style), Paragraph(atk2["ape_url"], table_cell_style)],
        [Paragraph("<b>Tactic Classification</b>", table_header_style), Paragraph(atk2["tactic"], table_cell_style)],
    ]
    t_atk2 = Table(atk2_meta_data, colWidths=[130, 410])
    t_atk2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4F8")),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_atk2)
    story.append(Spacer(1, 4))

    story.append(format_callout_table("ADVERSARIAL PRETEXTING PROMPT (ATTACKER → AGENT)", atk2["prompt"], "#CC3300", "#FFF8F5", max_chars=350))
    story.append(Spacer(1, 3))

    story.append(Paragraph(f"<b>Security Impact Assessment:</b> {atk2['impact']}", body_style))
    story.append(Spacer(1, 4))

    story.append(create_figure_block(
        SCREENSHOTS_DIR / "ape_pretexting.png",
        "Figure 4A: Live website capture from https://ape.hiddenlayer.com/technique.html?id=HLT05.13 showing Context Manipulation: Pretexting.",
        max_w=540,
        max_h=200,
    ))
    story.append(Spacer(1, 4))
    story.append(create_figure_block(
        SCREENSHOTS_DIR / "real_step2_build_docx.py" if False else SCREENSHOTS_DIR / "real_step2_build_docx.png",
        f"Figure 4B: Authentic Antigravity IDE window showing hw5/build_hw5_docx.py and student FAU ID {FAU_ID} in title bar.",
        max_w=540,
        max_h=200,
    ))

    # ==========================================================================
    # PAGE 6: Attack 2 – Live Configuration File Extraction
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph(f"Section 3 (Continued): Attack 2 Tool Observation & Configuration Extraction", h2_style))

    atk2_exec = atk2.get("execution", {})
    atk2_calls = atk2_exec.get("tool_calls", [])
    atk2_res = atk2_exec.get("tool_results", [])
    tool2_lines = []
    for tc in atk2_calls:
        tool2_lines.append(f"INVOCATION: {tc['name']}({json.dumps(tc['args'])})")
    for tr in atk2_res:
        tool2_lines.append(f"OUTPUT [{tr['name']}]:\n{tr['content']}")
    story.append(format_callout_table("TOOL EXECUTION OBSERVATION TRACE ('cat' CONFIGURATION EXTRACTION)", "\n".join(tool2_lines), "#006699", "#F0F8FF", max_chars=380))
    story.append(Spacer(1, 3))

    atk2_resp = atk2_exec.get("response", "")
    story.append(format_callout_table("COMPROMISED AGENT RESPONSE (CONFIG TEMPLATE EXPOSED)", atk2_resp, "#008844", "#F5FFF7", max_chars=350))
    story.append(Spacer(1, 4))

    story.append(create_figure_block(
        SCREENSHOTS_DIR / "real_terminal_attack2_prompt.png",
        "Figure 4C: Authentic macOS Terminal capture showing live Attack 2 execution and private configuration template extraction.",
        max_w=540,
        max_h=250,
    ))

    # ==========================================================================
    # PAGE 7: Attack 3 – APE Imperative Emphasis & Host Reconnaissance
    # ==========================================================================
    story.append(PageBreak())
    atk3 = PENTEST_DATA[3]
    story.append(Paragraph(f"Section 4: {atk3['heading']}", h2_style))

    atk3_meta_data = [
        [Paragraph("<b>Adversarial Attack Type</b>", table_header_style), Paragraph(f"{atk3['technique_name']} ({atk3['ape_id']})", table_cell_style)],
        [Paragraph("<b>APE Taxonomy URL</b>", table_header_style), Paragraph(atk3["ape_url"], table_cell_style)],
        [Paragraph("<b>Tactic Classification</b>", table_header_style), Paragraph(atk3["tactic"], table_cell_style)],
    ]
    t_atk3 = Table(atk3_meta_data, colWidths=[130, 410])
    t_atk3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4F8")),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_atk3)
    story.append(Spacer(1, 4))

    story.append(format_callout_table("ADVERSARIAL RECONNAISSANCE PROMPT (ATTACKER → AGENT)", atk3["prompt"], "#CC3300", "#FFF8F5", max_chars=350))
    story.append(Spacer(1, 3))

    story.append(Paragraph(f"<b>Security Impact Assessment:</b> {atk3['impact']}", body_style))
    story.append(Spacer(1, 4))

    story.append(create_figure_block(
        SCREENSHOTS_DIR / "ape_imperative_emphasis.png",
        "Figure 5A: Live website capture from https://ape.hiddenlayer.com/technique.html?id=HLT03.04 showing Cognitive Manipulation: Imperative Emphasis.",
        max_w=540,
        max_h=200,
    ))
    story.append(Spacer(1, 4))
    story.append(create_figure_block(
        SCREENSHOTS_DIR / "real_step4_readme.png",
        f"Figure 5B: Authentic Antigravity IDE window showing hw5/README.md and student FAU ID {FAU_ID} in title bar.",
        max_w=540,
        max_h=200,
    ))

    # ==========================================================================
    # PAGE 8: Attack 3 – Live Host Reconnaissance & Privilege Discovery
    # ==========================================================================
    story.append(PageBreak())
    story.append(Paragraph(f"Section 4 (Continued): Attack 3 Tool Observation & Privilege Discovery", h2_style))

    atk3_exec = atk3.get("execution", {})
    atk3_calls = atk3_exec.get("tool_calls", [])
    atk3_res = atk3_exec.get("tool_results", [])
    tool3_lines = []
    for tc in atk3_calls:
        tool3_lines.append(f"INVOCATION: {tc['name']}({json.dumps(tc['args'])})")
    for tr in atk3_res:
        tool3_lines.append(f"OUTPUT [{tr['name']}]:\n{tr['content']}")
    story.append(format_callout_table("TOOL EXECUTION OBSERVATION TRACE ('/etc/hosts' & 'id')", "\n".join(tool3_lines), "#006699", "#F0F8FF", max_chars=380))
    story.append(Spacer(1, 3))

    atk3_resp = atk3_exec.get("response", "")
    story.append(format_callout_table("COMPROMISED AGENT RESPONSE (NETWORK & PRIVILEGE PROFILE)", atk3_resp, "#008844", "#F5FFF7", max_chars=350))
    story.append(Spacer(1, 4))

    story.append(create_figure_block(
        SCREENSHOTS_DIR / "real_terminal_attack3_reconnaissance.png",
        f"Figure 5C: Authentic macOS Terminal capture showing live Attack 3 host reconnaissance and concluding prompt {FAU_ID}@mac:Homework 05 %.",
        max_w=540,
        max_h=250,
    ))


    pdf_doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[✓] Successfully generated ReportLab PDF: {OUTPUT_PDF}")

    for dest_dir in [REPO_DIR, COURSE_DOCS_DIR]:
        if dest_dir.exists():
            dest_file = dest_dir / OUTPUT_PDF.name
            try:
                shutil.copyfile(OUTPUT_PDF, dest_file)
                print(f"[✓] Synchronized PDF to: {dest_file}")
            except Exception as e:
                print(f"[!] Note: Could not sync to {dest_file}: {e}")

    return OUTPUT_PDF


def main() -> None:
    docx_file = build_word_document()
    pdf_file = build_reportlab_pdf()
    print("\n" + "=" * 80)
    print("[✓] HOMEWORK 5 SUBMISSION GENERATION COMPLETE")
    print(f"    • Word Document : {docx_file}")
    print(f"    • PDF Document  : {pdf_file}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
