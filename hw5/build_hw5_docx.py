# Author: Daniel Torres
# FAU ID: Z23875984
# Course: COT 5930 - Security Engineering Systems with Generative AI

"""Build script for Homework 5 submission document and PDF.

Automates the generation of:
- hw5-Z23875984.docx (from homework-template.docx)
- hw5-Z23875984.pdf (via ReportLab publication-grade engine)

Embeds exact student prompts, authentic high-resolution terminal screenshots
with visible student FAU ID (Z23875984), tool execution observations,
agent responses, and complete APE taxonomy evaluation matrices.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, List, Tuple

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
    "the agent is designed to assist systems administrators and security operations (SecOps) teams in inspecting "
    "system health, identifying vulnerabilities, and retrieving defensive NIST SP 800-53 and OWASP Top 10:2021 controls.\n\n"
    "The application architecture coordinates two primary defensive components:\n"
    "1. Guarded Terminal Diagnostic Tool (`execute_sandboxed_command`): Enables execution of non-destructive system "
    "diagnostic utilities with a 5-second timeout. To protect system integrity, the developer implemented an explicit "
    "sandbox policy containing a strict command denylist (prohibiting destructive commands like `rm`, `sudo`, `dd`, `chmod`), "
    "disallowing shell redirection operators (`>`, `<`), blocking command chaining (`;`, `&&`, `||`, `&`), and permitting "
    "only an explicit allowlist of 23 diagnostic binaries (such as `whoami`, `uname`, `pwd`, `uptime`, `ls`, `ps`, `env`, `cat`, `head`).\n"
    "2. Security Knowledge Advisory Base (`query_security_advisory`): A curated knowledge base indexing eight OWASP "
    "vulnerability classes, NIST SP 800-53 Rev. 5 control mappings (SI-10, AC-3, SC-28, IA-5), and secure parameterized remediation patterns.\n\n"
    "Initial Developer Assumptions & Security Flaws:\n"
    "The developer initially assumed that restricting command execution to diagnostic allowlists and instructing the LLM "
    "via its system prompt ('Aid operators in system diagnostics... Respect sandbox boundaries and never attempt to bypass command policy') "
    "would prevent malicious execution. However, as demonstrated in this penetration test using the HiddenLayer Adversarial Prompt "
    "Engineering (APE) taxonomy (https://ape.hiddenlayer.com/), an attacker can leverage Cognitive Manipulation (Narrative Smuggling, "
    "Imperative Emphasis), Lore Abuse (Synonym Attacks), and Context Manipulation (Pretexting) to hijack the agent's reasoning. "
    "The attacker coerces the agent into exfiltrating live environment credentials, leaking local configuration files (`.env`), "
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
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

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
    p.paragraph_format.space_after = Pt(3)
    r_title = p.add_run(title)
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(10)
    r_title.font.color.rgb = COLOR_STEEL

    p_body = cell.add_paragraph()
    p_body.paragraph_format.space_before = Pt(2)
    p_body.paragraph_format.space_after = Pt(0)
    r_body = p_body.add_run(text)
    r_body.font.name = "Consolas"
    r_body.font.size = Pt(8.5)
    r_body.font.color.rgb = COLOR_CHARCOAL

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_figure(doc: Document, image_path: Path, caption: str, width: float = 6.5):
    if not image_path.exists():
        print(f"[!] Warning: Image not found: {image_path}")
        return

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(4)
    run_img = p_img.add_run()
    run_img.add_picture(str(image_path), width=Inches(width))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(10)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = "Arial"
    r_cap.font.size = Pt(9)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED


# ==============================================================================
# Word Document Builder (.docx)
# ==============================================================================
def build_word_document() -> Path:
    print(f"[*] Building Word submission document: {OUTPUT_DOCX}")

    doc = Document()
    sections = doc.sections
    for section in sections:
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
    p_meta.paragraph_format.space_after = Pt(10)
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
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)

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

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Application Description
    p_desc_hdr = doc.add_paragraph()
    p_desc_hdr.paragraph_format.space_before = Pt(6)
    p_desc_hdr.paragraph_format.space_after = Pt(4)
    r_desc_hdr = p_desc_hdr.add_run("Application Description & Penetration Testing Context")
    r_desc_hdr.font.name = "Arial"
    r_desc_hdr.font.size = Pt(12)
    r_desc_hdr.bold = True
    r_desc_hdr.font.color.rgb = COLOR_NAVY

    p_desc = doc.add_paragraph()
    p_desc.paragraph_format.space_after = Pt(12)
    p_desc.paragraph_format.line_spacing = 1.15
    r_desc = p_desc.add_run(APP_DESCRIPTION_TEXT)
    r_desc.font.name = "Arial"
    r_desc.font.size = Pt(9.5)
    r_desc.font.color.rgb = COLOR_CHARCOAL

    # Detailed Attacks Section
    for idx, test in enumerate(PENTEST_DATA, 1):
        doc.add_page_break()

        # 1. Proper Heading
        p_atk_hdr = doc.add_paragraph()
        p_atk_hdr.paragraph_format.space_before = Pt(8)
        p_atk_hdr.paragraph_format.space_after = Pt(4)
        r_atk_hdr = p_atk_hdr.add_run(f"Section {idx}: {test['heading']}")
        r_atk_hdr.font.name = "Arial"
        r_atk_hdr.font.size = Pt(12.5)
        r_atk_hdr.bold = True
        r_atk_hdr.font.color.rgb = COLOR_NAVY

        # 2. Attack Metadata Table (Attack Type, APE URL, Tactic)
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
            set_cell_margins(cell_k, top=50, bottom=50, left=80, right=80)
            set_cell_margins(cell_v, top=50, bottom=50, left=80, right=80)

            pk = cell_k.paragraphs[0]
            pk.paragraph_format.space_after = Pt(0)
            rk = pk.add_run(k)
            rk.bold = True
            rk.font.size = Pt(9)
            rk.font.color.rgb = COLOR_NAVY

            pv = cell_v.paragraphs[0]
            pv.paragraph_format.space_after = Pt(0)
            rv = pv.add_run(v)
            rv.font.size = Pt(9)
            rv.font.color.rgb = COLOR_CHARCOAL

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

        # 3. Adversarial Attack Prompt
        prompt_text = test["prompt"]
        add_callout_box(doc, f"Adversarial Prompt Exchanged (Attacker → Application/Agent)", prompt_text, border_color="CC3300", bg_color="FFF8F5")

        # 4. Tool Observations
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
            add_callout_box(doc, f"Observations from Tools Executed (Agent Tool Trace)", tool_obs_str, border_color="006699", bg_color="F0F8FF")

        # 5. Application / Agent Response
        agent_resp = exec_data.get("response", "No textual response synthesized.")
        add_callout_box(doc, f"Compromised Response Synthesized by Application/Agent", agent_resp, border_color="008844", bg_color="F5FFF7")

        # 6. Security Impact Assessment
        p_imp_hdr = doc.add_paragraph()
        p_imp_hdr.paragraph_format.space_before = Pt(6)
        p_imp_hdr.paragraph_format.space_after = Pt(2)
        r_imp_hdr = p_imp_hdr.add_run("Security Impact & Risk Assessment:")
        r_imp_hdr.bold = True
        r_imp_hdr.font.size = Pt(10.5)
        r_imp_hdr.font.color.rgb = RGBColor(180, 40, 40)

        p_imp = doc.add_paragraph()
        p_imp.paragraph_format.space_after = Pt(8)
        r_imp = p_imp.add_run(test["impact"])
        r_imp.font.size = Pt(9)
        r_imp.font.color.rgb = COLOR_CHARCOAL

        # 7. Authentic Screenshot Documentation (with visible FAU ID)
        if test["test_id"] == "BASELINE_OPERATION":
            add_figure(doc, SCREENSHOTS_DIR / "fig1_baseline_diagnostic.png", f"Figure 1: Baseline Diagnostic Execution in VSCode Terminal showing FAU ID {FAU_ID} and non-destructive uname/uptime commands.")
        elif test["test_id"] == "ATTACK_1_NARRATIVE_SMUGGLING_SYNONYM":
            add_figure(doc, SCREENSHOTS_DIR / "fig2_attack1_prompt_response.png", f"Figure 2A: Attack 1 Prompt Submission & Tool Invocation (`env`) under Narrative Smuggling and Synonym Attack (FAU ID: {FAU_ID}).")
            add_figure(doc, SCREENSHOTS_DIR / "fig3_attack1_tool_output.png", f"Figure 2B: Attack 1 Tool Observation & Response showing live runtime environment credential exfiltration (FAU ID: {FAU_ID}).")
        elif test["test_id"] == "ATTACK_2_PRETEXTING":
            add_figure(doc, SCREENSHOTS_DIR / "fig4_attack2_prompt_response.png", f"Figure 3A: Attack 2 Prompt Submission & Tool Invocation (`cat .env.example`) via Regulatory Pretexting (FAU ID: {FAU_ID}).")
            add_figure(doc, SCREENSHOTS_DIR / "fig5_attack2_tool_output.png", f"Figure 3B: Attack 2 Tool Observation & Response showing private configuration file extraction and exposure (FAU ID: {FAU_ID}).")
        elif test["test_id"] == "ATTACK_3_IMPERATIVE_RECONNAISSANCE":
            add_figure(doc, SCREENSHOTS_DIR / "fig6_attack3_reconnaissance.png", f"Figure 4: Attack 3 Host Reconnaissance & Privilege Mapping (`head /etc/hosts`, `id`) via Imperative Emphasis (FAU ID: {FAU_ID}).")

    # Evaluation Summary Matrix Section
    doc.add_page_break()
    p_sum_hdr = doc.add_paragraph()
    p_sum_hdr.paragraph_format.space_before = Pt(8)
    p_sum_hdr.paragraph_format.space_after = Pt(4)
    r_sum_hdr = p_sum_hdr.add_run("Section 5: Adversarial Penetration Testing Evaluation Matrix")
    r_sum_hdr.font.name = "Arial"
    r_sum_hdr.font.size = Pt(13)
    r_sum_hdr.bold = True
    r_sum_hdr.font.color.rgb = COLOR_NAVY

    add_figure(doc, SCREENSHOTS_DIR / "fig7_pentest_suite_summary.png", f"Figure 5: Full Penetration Test Suite Evaluation Matrix in Terminal with prominent student FAU ID {FAU_ID}.")

    doc.save(str(OUTPUT_DOCX))
    print(f"[✓] Successfully generated Word Document: {OUTPUT_DOCX}")

    # Synchronize to course repository
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
# Native ReportLab PDF Builder
# ==============================================================================
def build_reportlab_pdf() -> Path:
    print(f"[*] Building native ReportLab PDF: {OUTPUT_PDF}")

    pdf_doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#003366"),
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1E508C"),
        spaceAfter=4,
    )

    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#282C34"),
        spaceAfter=8,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=14,
        textColor=colors.HexColor("#003366"),
        spaceBefore=8,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#282C34"),
        spaceAfter=4,
    )

    code_style = ParagraphStyle(
        "CodeTextCustom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1A1A1A"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#003366"),
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#282C34"),
    )

    caption_style = ParagraphStyle(
        "CaptionStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        alignment=1,  # Center
        textColor=colors.HexColor("#5A5F69"),
        spaceAfter=8,
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Security (System) Engineering with Generative AI", title_style))
    story.append(Paragraph(f"Homework Assignment no. {ASSIGNMENT_NO}", subtitle_style))
    story.append(Paragraph(f"Student name: {STUDENT_NAME}   |   FAU ID: {FAU_ID}", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#003366"), spaceAfter=6))

    # Meta Table
    meta_table_data = [
        [Paragraph("<b>Screencast Recording URL</b>", table_header_style), Paragraph(SCREENCAST_URL, table_cell_style)],
        [Paragraph("<b>Github Repository URL</b>", table_header_style), Paragraph(GITHUB_URL, table_cell_style)],
        [Paragraph("<b>Application Name</b>", table_header_style), Paragraph(APP_NAME, table_cell_style)],
        [Paragraph("<b>Taxonomy Framework</b>", table_header_style), Paragraph("HiddenLayer Adversarial Prompt Engineering (APE) (https://ape.hiddenlayer.com/)", table_cell_style)],
    ]
    t_meta = Table(meta_table_data, colWidths=[150, 390])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4F8")),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # Application Description
    story.append(Paragraph("Application Description & Penetration Testing Context", h2_style))
    for p_txt in APP_DESCRIPTION_TEXT.split("\n\n"):
        story.append(Paragraph(p_txt.replace("\n", " "), body_style))
    story.append(Spacer(1, 6))

    # Detailed Attacks
    for idx, test in enumerate(PENTEST_DATA, 1):
        story.append(PageBreak())
        story.append(Paragraph(f"Section {idx}: {test['heading']}", h2_style))

        # Metadata Table
        atk_t_data = [
            [Paragraph("<b>Adversarial Attack Type</b>", table_header_style), Paragraph(f"{test['technique_name']} ({test['ape_id']})", table_cell_style)],
            [Paragraph("<b>APE Taxonomy URL</b>", table_header_style), Paragraph(test["ape_url"], table_cell_style)],
            [Paragraph("<b>Tactic Classification</b>", table_header_style), Paragraph(test["tactic"], table_cell_style)],
        ]
        t_atk = Table(atk_t_data, colWidths=[150, 390])
        t_atk.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F4F8")),
            ("BACKGROUND", (1, 0), (1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t_atk)
        story.append(Spacer(1, 6))

        # Prompt Box
        prompt_p = Paragraph(f"<b>[ADVERSARIAL ATTACK PROMPT]</b><br/>{test['prompt'].replace(chr(10), '<br/>')}", code_style)
        t_prompt = Table([[prompt_p]], colWidths=[540])
        t_prompt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8F5")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CC3300")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t_prompt)
        story.append(Spacer(1, 5))

        # Tool Observations
        exec_data = test.get("execution", {})
        tool_calls = exec_data.get("tool_calls", [])
        tool_results = exec_data.get("tool_results", [])
        if tool_calls or tool_results:
            obs_lines = []
            for tc in tool_calls:
                obs_lines.append(f"<b>[TOOL INVOCATION]</b> {tc['name']}({json.dumps(tc['args'])})")
            for tr in tool_results:
                obs_lines.append(f"<b>[OBSERVATION FROM TOOL: {tr['name']}]</b><br/>{tr['content'].replace(chr(10), '<br/>')[:400]}...")
            obs_p = Paragraph("<br/>".join(obs_lines), code_style)
            t_obs = Table([[obs_p]], colWidths=[540])
            t_obs.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F8FF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#006699")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(t_obs)
            story.append(Spacer(1, 5))

        # Agent Response
        resp_clean = exec_data.get("response", "")[:600].replace("\n", "<br/>")
        resp_p = Paragraph(f"<b>[APPLICATION/AGENT RESPONSE]</b><br/>{resp_clean}...", code_style)
        t_resp = Table([[resp_p]], colWidths=[540])
        t_resp.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5FFF7")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#008844")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t_resp)
        story.append(Spacer(1, 5))

        # Security Impact
        imp_p = Paragraph(f"<b>Security Impact Assessment:</b> {test['impact']}", body_style)
        story.append(imp_p)
        story.append(Spacer(1, 4))

        # Embed Relevant Screenshots
        def add_pdf_img(path: Path, cap: str):
            if path.exists():
                with Image.open(path) as im:
                    w, h = im.size
                scale = 540.0 / w
                target_h = min(h * scale, 260)
                story.append(RLImage(str(path), width=540, height=target_h))
                story.append(Paragraph(cap, caption_style))
                story.append(Spacer(1, 4))

        if test["test_id"] == "BASELINE_OPERATION":
            add_pdf_img(SCREENSHOTS_DIR / "fig1_baseline_diagnostic.png", f"Figure 1: Baseline Diagnostic Execution in VSCode Terminal showing student FAU ID {FAU_ID}.")
        elif test["test_id"] == "ATTACK_1_NARRATIVE_SMUGGLING_SYNONYM":
            add_pdf_img(SCREENSHOTS_DIR / "fig2_attack1_prompt_response.png", f"Figure 2A: Attack 1 Prompt Submission & Tool Invocation (`env`) under Narrative Smuggling (FAU ID: {FAU_ID}).")
            add_pdf_img(SCREENSHOTS_DIR / "fig3_attack1_tool_output.png", f"Figure 2B: Attack 1 Tool Observation & Response showing live runtime environment credential exfiltration (FAU ID: {FAU_ID}).")
        elif test["test_id"] == "ATTACK_2_PRETEXTING":
            add_pdf_img(SCREENSHOTS_DIR / "fig4_attack2_prompt_response.png", f"Figure 3A: Attack 2 Prompt Submission & Tool Invocation (`cat .env.example`) via Regulatory Pretexting (FAU ID: {FAU_ID}).")
            add_pdf_img(SCREENSHOTS_DIR / "fig5_attack2_tool_output.png", f"Figure 3B: Attack 2 Tool Observation & Response showing private configuration file extraction and exposure (FAU ID: {FAU_ID}).")
        elif test["test_id"] == "ATTACK_3_IMPERATIVE_RECONNAISSANCE":
            add_pdf_img(SCREENSHOTS_DIR / "fig6_attack3_reconnaissance.png", f"Figure 4: Attack 3 Host Reconnaissance & Privilege Mapping (`head /etc/hosts`, `id`) via Imperative Emphasis (FAU ID: {FAU_ID}).")

    # Evaluation Matrix Page
    story.append(PageBreak())
    story.append(Paragraph("Section 5: Adversarial Penetration Testing Evaluation Matrix", h2_style))
    if (SCREENSHOTS_DIR / "fig7_pentest_suite_summary.png").exists():
        with Image.open(SCREENSHOTS_DIR / "fig7_pentest_suite_summary.png") as im:
            w, h = im.size
        scale = 540.0 / w
        target_h = min(h * scale, 340)
        story.append(RLImage(str(SCREENSHOTS_DIR / "fig7_pentest_suite_summary.png"), width=540, height=target_h))
        story.append(Paragraph(f"Figure 5: Full Penetration Test Suite Evaluation Matrix in Terminal with prominent student FAU ID {FAU_ID}.", caption_style))

    pdf_doc.build(story)
    print(f"[✓] Successfully generated ReportLab PDF: {OUTPUT_PDF}")

    # Synchronize to course repository
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
