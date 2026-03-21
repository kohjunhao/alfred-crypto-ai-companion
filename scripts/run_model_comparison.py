from __future__ import annotations

import csv
import os
from pathlib import Path
import statistics
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from alfred_app import create_app

PROMPTS = [
    ("PRO", "What is the price of Bitcoin right now?"),
    ("SIMPLE", "What is the price of Ethereum right now?"),
    ("PRO", "Show me the TVL of Aave."),
    ("SIMPLE", "How much is Solana worth right now?"),
    ("PRO", "Show me the TVL of Uniswap."),
    ("SIMPLE", "What is the price of Dogecoin right now?"),
]

MODELS = ["llama3", "qwen2.5:3b"]


def expected_metric(payload: dict[str, Any]) -> tuple[str, str]:
    metrics = payload.get("metrics") or {}
    formatted = metrics.get("formatted") or {}
    if payload.get("intent") == "tvl":
        return "tvl_usd", formatted.get("tvl_usd", "N/A")
    return "price_usd", formatted.get("price_usd", "N/A")


def run_batch(model_name: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    original_model = os.environ.get("OLLAMA_MODEL")
    original_fallback = os.environ.get("ALFRED_FALLBACK_ONLY")
    os.environ["OLLAMA_MODEL"] = model_name
    os.environ["ALFRED_FALLBACK_ONLY"] = "0"

    try:
        app = create_app()
        client = app.test_client()
        rows: list[dict[str, Any]] = []

        for mode, prompt in PROMPTS:
            response = client.post("/api/chat", json={"message": prompt, "mode": mode})
            payload = response.get_json()
            metric_name, expected_value = expected_metric(payload)
            reply = payload["reply"]
            contains_expected_value = expected_value != "N/A" and expected_value in reply

            rows.append(
                {
                    "model": model_name,
                    "mode": mode,
                    "prompt": prompt,
                    "intent": payload["intent"],
                    "entity": payload["entity"] or "",
                    "engine": payload["engine"],
                    "reason": payload.get("reason") or "",
                    "metric_checked": metric_name,
                    "expected_value": expected_value,
                    "reply_contains_expected_value": contains_expected_value,
                    "parse_ms": payload["timings"]["parse_ms"],
                    "data_fetch_ms": payload["timings"]["data_fetch_ms"],
                    "llm_ms": payload["timings"]["llm_ms"],
                    "total_ms": payload["timings"]["total_ms"],
                }
            )
    finally:
        if original_model is None:
            os.environ.pop("OLLAMA_MODEL", None)
        else:
            os.environ["OLLAMA_MODEL"] = original_model

        if original_fallback is None:
            os.environ.pop("ALFRED_FALLBACK_ONLY", None)
        else:
            os.environ["ALFRED_FALLBACK_ONLY"] = original_fallback

    summary = {
        "model": model_name,
        "prompt_count": len(rows),
        "avg_total_ms": round(statistics.mean(row["total_ms"] for row in rows), 2),
        "avg_llm_ms": round(statistics.mean(row["llm_ms"] for row in rows), 2),
        "ollama_count": sum(1 for row in rows if row["engine"] == "ollama"),
        "fallback_count": sum(1 for row in rows if row["engine"] == "fallback"),
        "guardrail_rejected_count": sum(1 for row in rows if row["reason"] == "guardrail_rejected"),
        "consistency_success_count": sum(1 for row in rows if row["reply_contains_expected_value"]),
        "consistency_success_rate": round(
            100 * sum(1 for row in rows if row["reply_contains_expected_value"]) / len(rows), 2
        ),
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "model",
                "mode",
                "prompt",
                "intent",
                "entity",
                "engine",
                "reason",
                "metric_checked",
                "expected_value",
                "reply_contains_expected_value",
                "parse_ms",
                "data_fetch_ms",
                "llm_ms",
                "total_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, summaries: list[dict[str, Any]]) -> None:
    lines = [
        "# Model comparison summary",
        "",
        "| Model | Prompts | Avg total ms | Avg llm ms | Ollama replies | Fallback replies | Guardrail rejects | Consistency success |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        lines.append(
            "| {model} | {prompt_count} | {avg_total_ms} | {avg_llm_ms} | {ollama_count} | {fallback_count} | {guardrail_rejected_count} | {consistency_success_count}/{prompt_count} ({consistency_success_rate}%) |".format(
                **summary
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    output_dir = PROJECT_ROOT / "evaluation_outputs"
    output_dir.mkdir(exist_ok=True)

    all_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []

    for model_name in MODELS:
        rows, summary = run_batch(model_name)
        all_rows.extend(rows)
        summaries.append(summary)

    write_csv(output_dir / "model_comparison_results.csv", all_rows)
    write_summary(output_dir / "model_comparison_summary.md", summaries)

    print("Created evaluation_outputs/model_comparison_results.csv")
    print("Created evaluation_outputs/model_comparison_summary.md")


if __name__ == "__main__":
    main()
