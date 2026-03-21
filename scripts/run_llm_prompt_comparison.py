from __future__ import annotations

import csv
import os
from pathlib import Path
from time import perf_counter
from typing import Any

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from alfred_app.llm_engine import generate_response

FIXTURES = [
    {
        "label": "bitcoin_price_pro",
        "mode": "PRO",
        "user_message": "What is the price of Bitcoin right now?",
        "parsed_intent": {"intent": "price", "entity": "bitcoin", "needs_live_data": True},
        "metrics": {
            "snapshot": {
                "query": "bitcoin",
                "resolved_name": "Bitcoin",
                "symbol": "BTC",
                "price_usd": 70525,
                "change_24h": 2.34,
                "market_cap": 1400000000000,
                "volume_24h": 35000000000,
                "fdv": 1480000000000,
                "tvl_usd": None,
                "tvl_change": None,
                "category": None,
                "chain": None,
                "sources": ["CoinGecko"],
                "retrieved_at": "2026-03-21T10:00:00+00:00",
                "formatted": {
                    "price_usd": "$70,525",
                    "market_cap": "$1.40T",
                    "volume_24h": "$35.00B",
                    "fdv": "$1.48T",
                    "tvl_usd": "N/A",
                    "change_24h": "2.34%",
                    "tvl_change": "N/A",
                },
            }
        },
    },
    {
        "label": "ethereum_price_simple",
        "mode": "SIMPLE",
        "user_message": "What is the price of Ethereum right now?",
        "parsed_intent": {"intent": "price", "entity": "ethereum", "needs_live_data": True},
        "metrics": {
            "snapshot": {
                "query": "ethereum",
                "resolved_name": "Ethereum",
                "symbol": "ETH",
                "price_usd": 2149,
                "change_24h": -1.15,
                "market_cap": 258000000000,
                "volume_24h": 16000000000,
                "fdv": 258000000000,
                "tvl_usd": None,
                "tvl_change": None,
                "category": None,
                "chain": None,
                "sources": ["CoinGecko"],
                "retrieved_at": "2026-03-21T10:00:00+00:00",
                "formatted": {
                    "price_usd": "$2,149",
                    "market_cap": "$258.00B",
                    "volume_24h": "$16.00B",
                    "fdv": "$258.00B",
                    "tvl_usd": "N/A",
                    "change_24h": "-1.15%",
                    "tvl_change": "N/A",
                },
            }
        },
    },
    {
        "label": "aave_tvl_pro",
        "mode": "PRO",
        "user_message": "Show me the TVL of Aave.",
        "parsed_intent": {"intent": "tvl", "entity": "aave", "needs_live_data": True},
        "metrics": {
            "snapshot": {
                "query": "aave",
                "resolved_name": "Aave",
                "symbol": "AAVE",
                "price_usd": 172.13,
                "change_24h": 4.22,
                "market_cap": 2600000000,
                "volume_24h": 210000000,
                "fdv": 2750000000,
                "tvl_usd": 25190000000,
                "tvl_change": 1.84,
                "category": "Lending",
                "chain": "Ethereum",
                "sources": ["CoinGecko", "DefiLlama"],
                "retrieved_at": "2026-03-21T10:00:00+00:00",
                "formatted": {
                    "price_usd": "$172.13",
                    "market_cap": "$2.60B",
                    "volume_24h": "$210.00M",
                    "fdv": "$2.75B",
                    "tvl_usd": "$25.19B",
                    "change_24h": "4.22%",
                    "tvl_change": "1.84%",
                },
            }
        },
    },
    {
        "label": "uniswap_tvl_pro",
        "mode": "PRO",
        "user_message": "Show me the TVL of Uniswap.",
        "parsed_intent": {"intent": "tvl", "entity": "uniswap", "needs_live_data": True},
        "metrics": {
            "snapshot": {
                "query": "uniswap",
                "resolved_name": "Uniswap",
                "symbol": "UNI",
                "price_usd": 10.42,
                "change_24h": 3.10,
                "market_cap": 6200000000,
                "volume_24h": 450000000,
                "fdv": 10400000000,
                "tvl_usd": 1700000000,
                "tvl_change": -0.75,
                "category": "DEX",
                "chain": "Ethereum",
                "sources": ["CoinGecko", "DefiLlama"],
                "retrieved_at": "2026-03-21T10:00:00+00:00",
                "formatted": {
                    "price_usd": "$10.42",
                    "market_cap": "$6.20B",
                    "volume_24h": "$450.00M",
                    "fdv": "$10.40B",
                    "tvl_usd": "$1.70B",
                    "change_24h": "3.10%",
                    "tvl_change": "-0.75%",
                },
            }
        },
    },
]

MODELS = ["llama3", "qwen2.5:3b"]


def expected_value(parsed_intent: dict[str, Any], metrics: dict[str, Any]) -> str:
    formatted = metrics["snapshot"]["formatted"]
    if parsed_intent["intent"] == "tvl":
        return formatted["tvl_usd"]
    return formatted["price_usd"]


def run_case(model_name: str, fixture: dict[str, Any]) -> dict[str, Any]:
    started_at = perf_counter()
    result = generate_response(
        mode=fixture["mode"],
        user_message=fixture["user_message"],
        parsed_intent=fixture["parsed_intent"],
        metrics=fixture["metrics"],
        ollama_url="http://localhost:11434",
        ollama_model=model_name,
        request_timeout=30,
        fallback_only=False,
    )
    elapsed_ms = round((perf_counter() - started_at) * 1000, 2)
    target_value = expected_value(fixture["parsed_intent"], fixture["metrics"])
    reply_contains_expected_value = target_value in result["text"]
    return {
        "model": model_name,
        "fixture": fixture["label"],
        "mode": fixture["mode"],
        "intent": fixture["parsed_intent"]["intent"],
        "engine": result["engine"],
        "reason": result["reason"],
        "expected_value": target_value,
        "reply_contains_expected_value": reply_contains_expected_value,
        "elapsed_ms": elapsed_ms,
    }


def main() -> None:
    output_dir = PROJECT_ROOT / "evaluation_outputs"
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / "llm_prompt_comparison.csv"
    summary_path = output_dir / "llm_prompt_comparison_summary.md"

    original_model = os.environ.get("OLLAMA_MODEL")
    rows: list[dict[str, Any]] = []
    try:
        for model_name in MODELS:
            os.environ["OLLAMA_MODEL"] = model_name
            for fixture in FIXTURES:
                rows.append(run_case(model_name, fixture))
    finally:
        if original_model is None:
            os.environ.pop("OLLAMA_MODEL", None)
        else:
            os.environ["OLLAMA_MODEL"] = original_model

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "model",
                "fixture",
                "mode",
                "intent",
                "engine",
                "reason",
                "expected_value",
                "reply_contains_expected_value",
                "elapsed_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# LLM prompt comparison summary",
        "",
        "| Model | Cases | Avg ms | Ollama replies | Fallback replies | Guardrail rejects | Value kept in final reply |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for model_name in MODELS:
        model_rows = [row for row in rows if row["model"] == model_name]
        case_count = len(model_rows)
        avg_ms = sum(row["elapsed_ms"] for row in model_rows) / case_count
        ollama_count = sum(1 for row in model_rows if row["engine"] == "ollama")
        fallback_count = sum(1 for row in model_rows if row["engine"] == "fallback")
        guardrail_count = sum(1 for row in model_rows if row["reason"] == "guardrail_rejected")
        value_kept = sum(1 for row in model_rows if row["reply_contains_expected_value"])
        lines.append(
            f"| {model_name} | {case_count} | {avg_ms:.2f} | {ollama_count} | {fallback_count} | {guardrail_count} | {value_kept}/{case_count} |"
        )

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Created {csv_path.relative_to(PROJECT_ROOT)}")
    print(f"Created {summary_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
