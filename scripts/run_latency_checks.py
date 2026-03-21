from __future__ import annotations

import csv
from pathlib import Path
import sys

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
    ("SIMPLE", "What does TVL mean?"),
]


def main() -> None:
    app = create_app()
    client = app.test_client()

    output_dir = Path("evaluation_outputs")
    output_dir.mkdir(exist_ok=True)
    csv_path = output_dir / "latency_results.csv"

    rows: list[dict[str, str | float]] = []

    for mode, prompt in PROMPTS:
        response = client.post("/api/chat", json={"message": prompt, "mode": mode})
        payload = response.get_json()
        timings = payload["timings"]
        rows.append(
            {
                "mode": mode,
                "prompt": prompt,
                "engine": payload["engine"],
                "intent": payload["intent"],
                "entity": payload["entity"] or "",
                "parse_ms": timings["parse_ms"],
                "data_fetch_ms": timings["data_fetch_ms"],
                "llm_ms": timings["llm_ms"],
                "total_ms": timings["total_ms"],
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
                "entity",
                "parse_ms",
                "data_fetch_ms",
                "llm_ms",
                "total_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} latency rows to {csv_path}")


if __name__ == "__main__":
    main()
