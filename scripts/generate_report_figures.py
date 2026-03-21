from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = PROJECT_ROOT / "report_figures"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_TITLE = load_font(26, bold=True)
FONT_HEADING = load_font(16, bold=True)
FONT_BODY = load_font(13)
FONT_SMALL = load_font(11)

PAPER = "#f3f3f1"
WHITE = "#ffffff"
GOLD = "#c4a000"
BLACK = "#1a1a1a"
GRID = "#d6d0bf"
MUTED = "#666055"
ACCENT_2 = "#887200"


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, value: str) -> None:
    x, y = xy
    draw.rectangle((x, y, x + 6, y + 18), fill=GOLD)
    draw.text((x + 14, y - 1), text.upper(), font=FONT_SMALL, fill=MUTED)
    draw.text((x + 14, y + 16), value, font=FONT_BODY, fill=BLACK)


def generate_gantt_chart() -> None:
    FIGURE_DIR.mkdir(exist_ok=True)
    width, height = 1700, 980
    image = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(image)

    draw.rectangle((40, 40, width - 40, height - 40), outline=BLACK, width=3)
    draw.text((70, 70), "Appendix Figure A1. Alfred project Gantt chart", font=FONT_TITLE, fill=BLACK)
    draw.text((70, 108), "Work plan used for the final project schedule and report completion.", font=FONT_BODY, fill=MUTED)

    tasks = [
        ("Planning", "Project proposal and topic definition", "2025-10-01", "2025-10-21"),
        ("Planning", "Literature collection and reading", "2025-10-22", "2025-11-20"),
        ("Planning", "Draft literature review", "2025-11-21", "2025-12-05"),
        ("Design", "Architecture and user-mode design", "2025-11-25", "2025-12-10"),
        ("Design", "Preliminary report preparation", "2025-12-01", "2025-12-18"),
        ("Implementation", "Flask backend scaffold", "2026-03-19", "2026-03-22"),
        ("Implementation", "Regex intent parser", "2026-03-19", "2026-03-22"),
        ("Implementation", "CoinGecko and DefiLlama integration", "2026-03-20", "2026-03-23"),
        ("Implementation", "Ollama integration and prompt tuning", "2026-03-20", "2026-03-24"),
        ("Implementation", "Frontend UI and mode switching", "2026-03-20", "2026-03-25"),
        ("Testing", "Unit testing and edge-case checks", "2026-03-23", "2026-03-26"),
        ("Testing", "Latency measurement runs", "2026-03-24", "2026-03-27"),
        ("Testing", "Novice and expert user testing", "2026-03-24", "2026-03-30"),
        ("Testing", "Evaluation chapter write-up", "2026-03-27", "2026-03-31"),
        ("Submission", "Final report editing", "2026-03-28", "2026-04-03"),
        ("Submission", "Final checks and submission", "2026-04-03", "2026-04-05"),
    ]

    parsed = [
        (section, label, datetime.fromisoformat(start), datetime.fromisoformat(end))
        for section, label, start, end in tasks
    ]
    start_date = min(item[2] for item in parsed)
    end_date = max(item[3] for item in parsed)
    total_days = (end_date - start_date).days + 1

    left = 390
    top = 170
    row_h = 42
    bar_h = 22
    timeline_w = width - left - 80
    day_w = timeline_w / total_days

    months: list[tuple[str, datetime, datetime]] = []
    cursor = datetime(start_date.year, start_date.month, 1)
    while cursor <= end_date:
        if cursor.month == 12:
            next_month = datetime(cursor.year + 1, 1, 1)
        else:
            next_month = datetime(cursor.year, cursor.month + 1, 1)
        months.append((cursor.strftime("%b %Y"), cursor, next_month))
        cursor = next_month

    y_header = top
    draw.text((70, y_header + 4), "TASK", font=FONT_HEADING, fill=BLACK)
    for label, month_start, month_end in months:
        month_x0 = left + int(((month_start - start_date).days) * day_w)
        month_x1 = left + int(((min(month_end, end_date) - start_date).days) * day_w)
        draw.rectangle((month_x0, y_header - 10, month_x1, y_header + 20), fill=WHITE, outline=BLACK, width=1)
        draw.text((month_x0 + 8, y_header - 2), label, font=FONT_SMALL, fill=BLACK)

    for index, (_, _, start, _) in enumerate(parsed):
        pass

    current_section = None
    for idx, (section, label, start, end) in enumerate(parsed):
        y = top + 36 + idx * row_h
        if section != current_section:
            draw.text((70, y - 10), section.upper(), font=FONT_SMALL, fill=ACCENT_2)
            current_section = section
        draw.text((70, y + 4), label, font=FONT_BODY, fill=BLACK)
        draw.line((left, y + row_h, width - 80, y + row_h), fill=GRID, width=1)

        bar_x0 = left + int(((start - start_date).days) * day_w)
        bar_x1 = bar_x0 + max(12, int((((end - start).days) + 1) * day_w))
        draw.rounded_rectangle((bar_x0, y + 6, bar_x1, y + 6 + bar_h), radius=0, fill=GOLD, outline=BLACK, width=2)

    for day_offset in range(total_days + 1):
        x = left + int(day_offset * day_w)
        draw.line((x, top + 26, x, height - 90), fill=GRID, width=1)

    draw.text((70, height - 75), "Figure generated from the Appendix A schedule so it can be inserted into the report as an actual chart.", font=FONT_SMALL, fill=MUTED)
    image.save(FIGURE_DIR / "gantt_chart.png")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def generate_model_comparison_chart() -> None:
    FIGURE_DIR.mkdir(exist_ok=True)
    width, height = 1500, 900
    image = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(image)

    draw.rectangle((40, 40, width - 40, height - 40), outline=BLACK, width=3)
    draw.text((70, 70), "Figure 5.1. Local model comparison for Alfred", font=FONT_TITLE, fill=BLACK)
    draw.text((70, 108), "Controlled prompt comparison and live end-to-end comparison on 21 March 2026.", font=FONT_BODY, fill=MUTED)

    controlled_rows = read_csv_rows(PROJECT_ROOT / "evaluation_outputs" / "llm_prompt_comparison.csv")
    live_rows = read_csv_rows(PROJECT_ROOT / "evaluation_outputs" / "model_comparison_results.csv")

    controlled_summary: dict[str, dict[str, float]] = {}
    live_summary: dict[str, dict[str, float]] = {}

    for model in {"llama3", "qwen2.5:3b"}:
        c_rows = [row for row in controlled_rows if row["model"] == model]
        l_rows = [row for row in live_rows if row["model"] == model]
        controlled_summary[model] = {
            "avg_ms": sum(float(row["elapsed_ms"]) for row in c_rows) / len(c_rows),
            "accepted": sum(1 for row in c_rows if row["engine"] == "ollama"),
            "kept": sum(1 for row in c_rows if row["reply_contains_expected_value"] == "True"),
        }
        live_summary[model] = {
            "avg_ms": sum(float(row["total_ms"]) for row in l_rows) / len(l_rows),
            "accepted": sum(1 for row in l_rows if row["engine"] == "ollama"),
            "kept": sum(1 for row in l_rows if row["reply_contains_expected_value"] == "True"),
        }

    draw_label(draw, (70, 150), "Controlled comparison", "fixed snapshots passed into llm_engine.py")
    draw_label(draw, (770, 150), "Live comparison", "full Flask pipeline with retrieval and guardrails")

    def draw_bar_group(origin_x: int, origin_y: int, title: str, summary: dict[str, dict[str, float]], max_value: float) -> None:
        draw.text((origin_x, origin_y), title, font=FONT_HEADING, fill=BLACK)
        baseline_y = origin_y + 250
        draw.line((origin_x, baseline_y, origin_x + 520, baseline_y), fill=BLACK, width=2)
        draw.line((origin_x, origin_y + 20, origin_x, baseline_y), fill=BLACK, width=2)

        models = ["llama3", "qwen2.5:3b"]
        for idx, model in enumerate(models):
            bar_x = origin_x + 90 + idx * 210
            value = summary[model]["avg_ms"]
            bar_h = int((value / max_value) * 180)
            draw.rectangle((bar_x, baseline_y - bar_h, bar_x + 90, baseline_y), fill=GOLD if idx == 0 else WHITE, outline=BLACK, width=2)
            draw.text((bar_x - 4, baseline_y + 12), model, font=FONT_BODY, fill=BLACK)
            draw.text((bar_x - 2, baseline_y - bar_h - 26), f"{value:.0f} ms", font=FONT_SMALL, fill=BLACK)
            draw.text((bar_x - 22, baseline_y + 38), f"Ollama accepts: {int(summary[model]['accepted'])}", font=FONT_SMALL, fill=MUTED)
            draw.text((bar_x - 22, baseline_y + 56), f"Value kept: {int(summary[model]['kept'])}", font=FONT_SMALL, fill=MUTED)

    controlled_max = max(value["avg_ms"] for value in controlled_summary.values()) * 1.15
    live_max = max(value["avg_ms"] for value in live_summary.values()) * 1.15
    draw_bar_group(70, 240, "Average response stage time", controlled_summary, controlled_max)
    draw_bar_group(770, 240, "Average total app response time", live_summary, live_max)

    note = (
        "Interpretation: qwen2.5:3b did not provide a clear advantage over llama3 in Alfred's current pipeline. "
        "Both models still relied on Alfred's safety guard to keep final replies aligned with the injected data."
    )
    draw.text((70, height - 95), note, font=FONT_SMALL, fill=MUTED)
    image.save(FIGURE_DIR / "model_comparison.png")


def main() -> None:
    generate_gantt_chart()
    generate_model_comparison_chart()
    print(f"Created figures in {FIGURE_DIR}")


if __name__ == "__main__":
    main()
