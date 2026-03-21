from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def build_styles():
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        spaceAfter=8,
    )
    heading1 = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceBefore=6,
        spaceAfter=12,
        textColor=colors.HexColor("#1a1a1a"),
    )
    heading2 = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        spaceBefore=10,
        spaceAfter=8,
    )
    title = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=14,
    )
    subtitle = ParagraphStyle(
        "SubtitleCustom",
        parent=body,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    code = ParagraphStyle(
        "CodeCustom",
        parent=body,
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        leftIndent=8,
        rightIndent=8,
        spaceAfter=8,
    )
    small = ParagraphStyle(
        "SmallCustom",
        parent=body,
        fontSize=9,
        leading=12,
    )
    return {
        "body": body,
        "heading1": heading1,
        "heading2": heading2,
        "title": title,
        "subtitle": subtitle,
        "code": code,
        "small": small,
    }


def inline_md(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    return text


def parse_table(table_lines: list[str]):
    rows = []
    for idx, line in enumerate(table_lines):
        parts = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if idx == 1 and all(set(part) <= {":", "-"} for part in parts):
            continue
        rows.append(parts)
    return rows


def build_pdf(source_path: Path, output_path: Path) -> None:
    styles = build_styles()
    story = []
    text = source_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            story.append(PageBreak())
            i += 1
            continue

        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            story.append(Preformatted("\n".join(code_lines), styles["code"]))
            story.append(Spacer(1, 6))
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            data = parse_table(table_lines)
            tbl = Table(data, repeatRows=1)
            tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1ebcc")),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1a1a1a")),
                        ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#1a1a1a")),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                        ("LEADING", (0, 0), (-1, -1), 11),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#faf8f0")]),
                    ]
                )
            )
            story.append(tbl)
            story.append(Spacer(1, 10))
            continue

        if stripped.startswith("# "):
            story.append(Paragraph(inline_md(stripped[2:]), styles["title"]))
            i += 1
            continue

        if stripped.startswith("## "):
            story.append(Paragraph(inline_md(stripped[3:]), styles["subtitle"]))
            i += 1
            continue

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text_content = stripped[level:].strip()
            style = styles["heading1"] if level == 1 else styles["heading2"]
            story.append(Paragraph(inline_md(text_content), style))
            if level == 1:
                story.append(HRFlowable(width="100%", thickness=1.1, color=colors.HexColor("#1a1a1a"), spaceAfter=10))
            i += 1
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                item_text = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append(ListItem(Paragraph(inline_md(item_text), styles["body"])))
                i += 1
            story.append(ListFlowable(items, bulletType="1", leftIndent=18))
            story.append(Spacer(1, 6))
            continue

        if stripped.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                item_text = lines[i].strip()[2:]
                items.append(ListItem(Paragraph(inline_md(item_text), styles["body"])))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=18))
            story.append(Spacer(1, 6))
            continue

        paragraph_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line:
                break
            if next_line == "---" or next_line.startswith("#") or next_line.startswith("|") or next_line.startswith("```") or next_line.startswith("- ") or re.match(r"^\d+\.\s+", next_line):
                break
            paragraph_lines.append(next_line)
            i += 1

        paragraph_text = " ".join(paragraph_lines)
        style = styles["small"] if paragraph_text.startswith("**") else styles["body"]
        story.append(Paragraph(inline_md(paragraph_text), style))

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="CM3070 Final Project Report - Alfred",
        author="Koh Jun Hao",
    )
    doc.build(story)


def main():
    if len(sys.argv) >= 3:
        source = Path(sys.argv[1])
        output = Path(sys.argv[2])
    else:
        source = Path("CM3070_full_report_draft.md")
        output = Path("CM3070_full_report_draft.pdf")
    build_pdf(source, output)
    print(f"Created PDF at {output}")


if __name__ == "__main__":
    main()
