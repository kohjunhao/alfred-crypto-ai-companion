from __future__ import annotations

import json
from typing import Any

import requests

SYSTEM_PROMPTS = {
    "SIMPLE": """You are Alfred, a careful crypto explainer for beginners.

Rules:
- Use only the supplied real-time data.
- Never invent a price, TVL, or market statistic.
- Write exactly 2 short sentences.
- Sentence 1 should state the key live number clearly.
- Sentence 2 should explain what that number means in plain English.
- Keep the tone calm and helpful.
- Never give direct financial advice or tell the user to buy or sell.
- Do not say 'if you were to buy or sell'.
""",
    "PRO": """You are Alfred, a concise crypto market assistant for advanced users.

Rules:
- Use only the supplied real-time data.
- Never invent a price, TVL, or market statistic.
- Present the answer as a compact Markdown table followed by 1 short analytical sentence.
- Be precise and direct.
- Never give direct financial advice or tell the user to buy or sell.
""",
}

GENERAL_CHAT_PROMPT = """You are Alfred, a local crypto AI companion.

Rules:
- Answer briefly and clearly.
- If the user asks for live price or TVL data, tell them Alfred can fetch it.
- Never give direct financial advice.
"""


def ollama_is_available(base_url: str, timeout: int = 3) -> bool:
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def _build_market_prompt(
    mode: str,
    user_message: str,
    parsed_intent: dict[str, Any],
    metrics: dict[str, Any],
) -> str:
    return "\n".join(
        [
            SYSTEM_PROMPTS[mode],
            f"User question: {user_message}",
            f"Detected intent: {parsed_intent['intent']}",
            f"Detected entity: {parsed_intent.get('entity') or 'N/A'}",
            "Real-time market data:",
            json.dumps(metrics["snapshot"], indent=2),
            "",
            "Write the final answer now.",
        ]
    )


def _build_general_prompt(user_message: str) -> str:
    return "\n".join(
        [
            GENERAL_CHAT_PROMPT,
            f"User question: {user_message}",
            "Write the final answer now.",
        ]
    )


def _post_to_ollama(base_url: str, model: str, prompt: str, timeout: int) -> str:
    response = requests.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    return str(payload.get("response", "")).strip()


def _response_is_usable(mode: str, parsed_intent: dict[str, Any], metrics: dict[str, Any], text: str) -> bool:
    snapshot = metrics["snapshot"]
    formatted = snapshot["formatted"]
    lowered = text.lower()

    banned_phrases = ["buy", "sell", "financial advice"]
    if any(phrase in lowered for phrase in banned_phrases):
        return False

    if mode == "PRO" and "| metric | value |" not in lowered:
        return False

    if parsed_intent["intent"] == "price":
        expected_price = formatted["price_usd"]
        if expected_price != "N/A" and expected_price not in text:
            return False
        if expected_price != "N/A" and "n/a" in lowered:
            return False

    if parsed_intent["intent"] == "tvl":
        expected_tvl = formatted["tvl_usd"]
        if expected_tvl != "N/A" and expected_tvl not in text:
            return False
        if expected_tvl != "N/A" and "n/a" in lowered:
            return False

    return True


def _render_simple_fallback(parsed_intent: dict[str, Any], metrics: dict[str, Any]) -> str:
    snapshot = metrics["snapshot"]
    name = snapshot["resolved_name"]
    formatted = snapshot["formatted"]

    if parsed_intent["intent"] == "tvl":
        tvl = formatted["tvl_usd"]
        return (
            f"{name} currently has about {tvl} in total value locked. "
            "That is a quick way to describe how much capital is sitting inside the protocol right now. "
            "Alfred is using live API data here, not memory."
        )

    price = formatted["price_usd"]
    change = formatted["change_24h"]
    return (
        f"{name} is trading around {price} right now, with a 24-hour move of {change}. "
        "Think of this as Alfred giving you a live market snapshot first, then a plain-English explanation. "
        "This is informational only, not financial advice."
    )


def _render_pro_fallback(parsed_intent: dict[str, Any], metrics: dict[str, Any]) -> str:
    snapshot = metrics["snapshot"]
    formatted = snapshot["formatted"]

    rows = [
        ("Asset", snapshot["resolved_name"]),
        ("Symbol", snapshot["symbol"]),
        ("Price", formatted["price_usd"]),
        ("24h Change", formatted["change_24h"]),
        ("Market Cap", formatted["market_cap"]),
        ("24h Volume", formatted["volume_24h"]),
        ("FDV", formatted["fdv"]),
        ("TVL", formatted["tvl_usd"]),
        ("Sources", ", ".join(snapshot["sources"]) or "N/A"),
    ]
    table_lines = ["| Metric | Value |", "| :--- | :--- |"]
    table_lines.extend(f"| {label} | {value} |" for label, value in rows)

    if parsed_intent["intent"] == "tvl":
        insight = "TVL is the primary anchor here; use price fields only as supporting context."
    else:
        insight = "Price, market cap, and volume are aligned into one quick market check."

    return "\n".join(table_lines + ["", insight, "", "Informational only. Not financial advice."])


def _render_general_fallback(user_message: str) -> str:
    lowered = user_message.lower()
    if "tvl" in lowered:
        return (
            "TVL means Total Value Locked. In plain terms, it is the total amount of capital currently deposited "
            "inside a DeFi protocol, so it gives a quick sense of the protocol's scale."
        )
    if "price" in lowered and "what is the price" in lowered:
        return "Tell me which asset you want, for example: 'What is the price of Bitcoin?'"
    if "hello" in lowered or "hi" in lowered:
        return (
            "Hello. I am Alfred, your crypto AI companion. "
            "Ask me for a live price, TVL, or a short explanation of a crypto metric."
        )

    return (
        "I can help with live crypto price checks, TVL requests, and short market explanations. "
        "Try asking: 'What is the price of Bitcoin?' or 'Show me the TVL of Aave.'"
    )


def generate_response(
    *,
    mode: str,
    user_message: str,
    parsed_intent: dict[str, Any],
    metrics: dict[str, Any] | None,
    ollama_url: str,
    ollama_model: str,
    request_timeout: int,
    fallback_only: bool,
) -> dict[str, str]:
    if parsed_intent["intent"] == "general_chat" or not metrics:
        prompt = _build_general_prompt(user_message)
        if not fallback_only and ollama_is_available(ollama_url):
            try:
                text = _post_to_ollama(ollama_url, ollama_model, prompt, request_timeout)
                if text:
                    return {"text": text, "engine": "ollama", "model": ollama_model, "reason": "ollama_success"}
            except requests.RequestException:
                return {
                    "text": _render_general_fallback(user_message),
                    "engine": "fallback",
                    "model": "template",
                    "reason": "ollama_request_failed",
                }
        return {
            "text": _render_general_fallback(user_message),
            "engine": "fallback",
            "model": "template",
            "reason": "fallback_only" if fallback_only else "ollama_unavailable",
        }

    prompt = _build_market_prompt(mode, user_message, parsed_intent, metrics)
    if not fallback_only and ollama_is_available(ollama_url):
        try:
            text = _post_to_ollama(ollama_url, ollama_model, prompt, request_timeout)
            if text and _response_is_usable(mode, parsed_intent, metrics, text):
                return {"text": text, "engine": "ollama", "model": ollama_model, "reason": "ollama_success"}
            return {
                "text": _render_simple_fallback(parsed_intent, metrics) if mode == "SIMPLE" else _render_pro_fallback(parsed_intent, metrics),
                "engine": "fallback",
                "model": "template",
                "reason": "guardrail_rejected",
            }
        except requests.RequestException:
            return {
                "text": _render_simple_fallback(parsed_intent, metrics) if mode == "SIMPLE" else _render_pro_fallback(parsed_intent, metrics),
                "engine": "fallback",
                "model": "template",
                "reason": "ollama_request_failed",
            }

    fallback = _render_simple_fallback(parsed_intent, metrics) if mode == "SIMPLE" else _render_pro_fallback(parsed_intent, metrics)
    return {
        "text": fallback,
        "engine": "fallback",
        "model": "template",
        "reason": "fallback_only" if fallback_only else "ollama_unavailable",
    }
