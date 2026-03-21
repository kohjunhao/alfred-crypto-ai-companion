from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

PRICE_KEYWORDS = {
    "price",
    "worth",
    "cost",
    "usd",
    "market",
    "marketcap",
    "market cap",
    "fdv",
    "volume",
    "change",
    "trading",
    "buying",
    "selling",
}

TVL_KEYWORDS = {
    "tvl",
    "total value locked",
    "locked",
    "defi",
    "apy",
    "yield",
    "liquidity",
    "protocol",
}

STOP_WORDS = {
    "24h",
    "a",
    "about",
    "alfred",
    "an",
    "and",
    "cap",
    "can",
    "check",
    "current",
    "does",
    "explain",
    "for",
    "get",
    "give",
    "hello",
    "hey",
    "how",
    "i",
    "in",
    "is",
    "latest",
    "live",
    "me",
    "mean",
    "mode",
    "much",
    "now",
    "of",
    "please",
    "pro",
    "simple",
    "right",
    "show",
    "tell",
    "the",
    "today",
    "value",
    "what",
    "whats",
}

ALIASES = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "avax": "avalanche",
    "arb": "arbitrum",
    "op": "optimism",
    "link": "chainlink",
    "uni": "uniswap",
    "aavegotchi": "aavegotchi",
}

PRICE_PATTERN = re.compile(
    r"\b(price|worth|cost|usd|market cap|marketcap|fdv|volume|change|buying|selling|trading)\b",
    re.IGNORECASE,
)
TVL_PATTERN = re.compile(
    r"\b(tvl|total value locked|locked|defi|apy|yield|liquidity|protocol)\b",
    re.IGNORECASE,
)


@dataclass
class ParsedIntent:
    intent: str
    entity: str | None
    normalized_message: str
    matched_keywords: list[str]
    needs_live_data: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_message(message: str) -> str:
    lowered = message.strip().lower()
    lowered = re.sub(r"[^a-z0-9\s\-]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def _collect_keywords(normalized_message: str) -> list[str]:
    matched: list[str] = []
    for keyword in sorted(TVL_KEYWORDS | PRICE_KEYWORDS, key=len, reverse=True):
        if keyword in normalized_message:
            matched.append(keyword)
    return matched


def extract_entity(normalized_message: str) -> str | None:
    tokens = normalized_message.split()
    candidate_tokens: list[str] = []

    for token in tokens:
        if token in STOP_WORDS:
            continue
        if token in PRICE_KEYWORDS or token in TVL_KEYWORDS:
            continue
        if token.isdigit():
            continue
        candidate_tokens.append(ALIASES.get(token, token))

    if not candidate_tokens:
        return None

    entity = " ".join(candidate_tokens[:3]).strip()
    return entity or None


def determine_intent(message: str) -> ParsedIntent:
    normalized = normalize_message(message)
    if not normalized:
        return ParsedIntent(
            intent="general_chat",
            entity=None,
            normalized_message="",
            matched_keywords=[],
            needs_live_data=False,
        )

    matched_keywords = _collect_keywords(normalized)
    entity = extract_entity(normalized)

    if TVL_PATTERN.search(normalized):
        return ParsedIntent(
            intent="tvl",
            entity=entity,
            normalized_message=normalized,
            matched_keywords=matched_keywords,
            needs_live_data=True,
        )

    if PRICE_PATTERN.search(normalized):
        return ParsedIntent(
            intent="price",
            entity=entity,
            normalized_message=normalized,
            matched_keywords=matched_keywords,
            needs_live_data=True,
        )

    return ParsedIntent(
        intent="general_chat",
        entity=entity,
        normalized_message=normalized,
        matched_keywords=matched_keywords,
        needs_live_data=False,
    )
