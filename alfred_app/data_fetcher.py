from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

import requests

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
DEFILLAMA_BASE_URL = "https://api.llama.fi"
REQUEST_TIMEOUT = 10

SESSION = requests.Session()
SESSION.headers.update(
    {
        "Accept": "application/json",
        "User-Agent": "Alfred-CM3070-Project/1.0",
    }
)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _format_money(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    abs_value = abs(float(value))
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"${value:,.0f}"
    return f"${value:,.2f}"


def _request_json(url: str, params: dict[str, Any] | None = None) -> Any:
    response = SESSION.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def search_coingecko(entity: str) -> dict[str, Any] | None:
    payload = _request_json(
        f"{COINGECKO_BASE_URL}/search",
        params={"query": entity},
    )
    coins = payload.get("coins", [])
    if not coins:
        return None

    lowered = entity.lower()

    for coin in coins:
        if coin.get("id", "").lower() == lowered:
            return coin
        if coin.get("symbol", "").lower() == lowered:
            return coin
        if coin.get("name", "").lower() == lowered:
            return coin

    return coins[0]


def get_rich_market_data(entity: str) -> dict[str, Any]:
    coin = search_coingecko(entity)
    if not coin:
        return {
            "source": "CoinGecko",
            "available": False,
            "error": f"No CoinGecko asset match found for '{entity}'.",
        }

    market_rows = _request_json(
        f"{COINGECKO_BASE_URL}/coins/markets",
        params={
            "vs_currency": "usd",
            "ids": coin["id"],
            "price_change_percentage": "24h",
        },
    )
    if not market_rows:
        return {
            "source": "CoinGecko",
            "available": False,
            "error": f"CoinGecko returned no market rows for '{entity}'.",
        }

    market = market_rows[0]
    return {
        "source": "CoinGecko",
        "available": True,
        "asset_name": market.get("name"),
        "symbol": str(market.get("symbol", "")).upper(),
        "coingecko_id": market.get("id"),
        "price_usd": market.get("current_price"),
        "change_24h": market.get("price_change_percentage_24h"),
        "market_cap": market.get("market_cap"),
        "volume_24h": market.get("total_volume"),
        "fdv": market.get("fully_diluted_valuation"),
        "high_24h": market.get("high_24h"),
        "low_24h": market.get("low_24h"),
        "last_updated": market.get("last_updated"),
    }


@lru_cache(maxsize=1)
def _load_protocol_index() -> list[dict[str, Any]]:
    payload = _request_json(f"{DEFILLAMA_BASE_URL}/protocols")
    return payload if isinstance(payload, list) else []


def _find_protocol(entity: str) -> dict[str, Any] | None:
    lowered = entity.lower()
    protocols = _load_protocol_index()

    for protocol in protocols:
        slug = str(protocol.get("slug", "")).lower()
        name = str(protocol.get("name", "")).lower()
        symbol = str(protocol.get("symbol", "")).lower()
        if lowered in {slug, name, symbol}:
            return protocol

    for protocol in protocols:
        haystack = " ".join(
            [
                str(protocol.get("slug", "")).lower(),
                str(protocol.get("name", "")).lower(),
                str(protocol.get("symbol", "")).lower(),
            ]
        )
        if lowered in haystack:
            return protocol

    return None


def get_defi_tvl(entity: str) -> dict[str, Any]:
    protocol = _find_protocol(entity)
    if not protocol:
        return {
            "source": "DefiLlama",
            "available": False,
            "error": f"No DefiLlama protocol match found for '{entity}'.",
        }

    change = protocol.get("change_1d")
    if change is None:
        change = protocol.get("change_7d")

    tvl_value = protocol.get("tvl")
    if tvl_value == 0:
        tvl_value = None

    return {
        "source": "DefiLlama",
        "available": True,
        "protocol_name": protocol.get("name"),
        "slug": protocol.get("slug"),
        "symbol": protocol.get("symbol"),
        "category": protocol.get("category"),
        "chain": protocol.get("chain"),
        "tvl_usd": tvl_value,
        "tvl_change": change,
        "mcap": protocol.get("mcap"),
    }


def _merge_snapshot(entity: str, market: dict[str, Any], defi: dict[str, Any]) -> dict[str, Any]:
    resolved_name = (
        market.get("asset_name")
        or defi.get("protocol_name")
        or entity.title()
    )
    resolved_symbol = market.get("symbol") or defi.get("symbol") or entity.upper()

    snapshot = {
        "query": entity,
        "resolved_name": resolved_name,
        "symbol": resolved_symbol,
        "price_usd": market.get("price_usd"),
        "change_24h": market.get("change_24h"),
        "market_cap": market.get("market_cap"),
        "volume_24h": market.get("volume_24h"),
        "fdv": market.get("fdv"),
        "tvl_usd": defi.get("tvl_usd"),
        "tvl_change": defi.get("tvl_change"),
        "category": defi.get("category"),
        "chain": defi.get("chain"),
        "sources": [
            source
            for source in (
                "CoinGecko" if market.get("available") else None,
                "DefiLlama" if defi.get("available") and defi.get("tvl_usd") is not None else None,
            )
            if source
        ],
        "retrieved_at": _now_iso(),
    }

    snapshot["formatted"] = {
        "price_usd": _format_money(snapshot["price_usd"]),
        "market_cap": _format_money(snapshot["market_cap"]),
        "volume_24h": _format_money(snapshot["volume_24h"]),
        "fdv": _format_money(snapshot["fdv"]),
        "tvl_usd": _format_money(snapshot["tvl_usd"]),
        "change_24h": "N/A" if snapshot["change_24h"] is None else f"{snapshot['change_24h']:.2f}%",
        "tvl_change": "N/A" if snapshot["tvl_change"] is None else f"{snapshot['tvl_change']:.2f}%",
    }
    return snapshot


def get_combined_metrics(entity: str) -> dict[str, Any]:
    results: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_map = {
            "market": executor.submit(get_rich_market_data, entity),
            "defi": executor.submit(get_defi_tvl, entity),
        }
        for key, future in future_map.items():
            try:
                results[key] = future.result()
            except requests.RequestException as exc:
                results[key] = {
                    "source": "CoinGecko" if key == "market" else "DefiLlama",
                    "available": False,
                    "error": f"{key} request failed: {exc}",
                }
            except Exception as exc:  # pragma: no cover - safety net
                results[key] = {
                    "source": "CoinGecko" if key == "market" else "DefiLlama",
                    "available": False,
                    "error": f"{key} request failed unexpectedly: {exc}",
                }

    market = results.get("market", {})
    defi = results.get("defi", {})

    for source_result in (market, defi):
        error = source_result.get("error")
        if error:
            warnings.append(error)

    return {
        "snapshot": _merge_snapshot(entity, market, defi),
        "market": market,
        "defi": defi,
        "warnings": warnings,
    }
