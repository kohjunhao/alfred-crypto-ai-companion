from __future__ import annotations

import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from alfred_app import create_app

PROMPTS = [
    ("SIMPLE", "What is the price of Bitcoin right now?"),
    ("PRO", "What is the price of Ethereum right now?"),
    ("SIMPLE", "How much is Solana worth right now?"),
    ("PRO", "Show me the TVL of Aave."),
    ("PRO", "Show me the TVL of Uniswap."),
]


def expected_metric(payload: dict) -> tuple[str, str]:
    metrics = payload["metrics"]
    formatted = metrics["formatted"]
    if payload["intent"] == "tvl":
        return "tvl_usd", formatted["tvl_usd"]
    return "price_usd", formatted["price_usd"]


def main() -> None:
    app = create_app()
    client = app.test_client()

    output_dir = Path("evaluation_outputs")
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / "consistency_results.csv"

    rows: list[dict[str, str]] = []

    for mode, prompt in PROMPTS:
        response = client.post("/api/chat", json={"message": prompt, "mode": mode})
        payload = response.get_json()
        metric_name, expected_value = expected_metric(payload)
        reply = payload["reply"]
        contains_expected_value = expected_value != "N/A" and expected_value in reply
        rows.append(
            {
                "mode": mode,
                "prompt": prompt,
                "engine": payload["engine"],
                "intent": payload["intent"],
                "metric_checked": metric_name,
                "expected_value": expected_value,
                "reply_contains_expected_value": str(contains_expected_value),
            }
        )

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "mode",
                "prompt",
                "engine",
                "intent",
                "metric_checked",
                "expected_value",
                "reply_contains_expected_value",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} consistency rows to {csv_path}")


if __name__ == "__main__":
    main()
