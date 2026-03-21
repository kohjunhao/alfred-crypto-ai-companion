from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def append_request_log(log_dir: Path, payload: dict[str, Any]) -> None:
    log_path = log_dir / "alfred_requests.jsonl"
    enriched_payload = {"logged_at": _timestamp(), **payload}
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(enriched_payload, ensure_ascii=True) + "\n")

