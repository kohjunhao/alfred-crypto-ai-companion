from __future__ import annotations

from time import perf_counter

from flask import Blueprint, current_app, jsonify, render_template, request

from .data_fetcher import get_combined_metrics
from .intent_parser import determine_intent
from .llm_engine import generate_response, ollama_is_available
from .telemetry import append_request_log

bp = Blueprint("alfred", __name__, template_folder="templates", static_folder="static")


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/api/health")
def health():
    if current_app.config["FALLBACK_ONLY"]:
        ollama_ready = False
    else:
        ollama_ready = ollama_is_available(current_app.config["OLLAMA_URL"])

    return jsonify(
        {
            "app": "alfred",
            "status": "ok",
            "mode": "fallback-only" if current_app.config["FALLBACK_ONLY"] else "ollama-or-fallback",
            "ollama_url": current_app.config["OLLAMA_URL"],
            "ollama_model": current_app.config["OLLAMA_MODEL"],
            "ollama_ready": ollama_ready,
        }
    )


@bp.post("/api/chat")
def chat():
    started_at = perf_counter()
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    mode = str(payload.get("mode", "SIMPLE")).upper()

    if not message:
        return jsonify({"error": "Please enter a message before sending."}), 400

    if mode not in {"SIMPLE", "PRO"}:
        return jsonify({"error": "Mode must be SIMPLE or PRO."}), 400

    parse_started = perf_counter()
    parsed = determine_intent(message)
    parse_time_ms = round((perf_counter() - parse_started) * 1000, 2)

    metrics = None
    warnings: list[str] = []
    data_fetch_ms = 0.0

    if parsed.needs_live_data:
        if not parsed.entity:
            warnings.append("Alfred detected a market-style question but could not find the asset or protocol name.")
        else:
            fetch_started = perf_counter()
            metrics = get_combined_metrics(parsed.entity)
            data_fetch_ms = round((perf_counter() - fetch_started) * 1000, 2)
            warnings.extend(metrics.get("warnings", []))

    llm_started = perf_counter()
    response = generate_response(
        mode=mode,
        user_message=message,
        parsed_intent=parsed.to_dict(),
        metrics=metrics,
        ollama_url=current_app.config["OLLAMA_URL"],
        ollama_model=current_app.config["OLLAMA_MODEL"],
        request_timeout=current_app.config["REQUEST_TIMEOUT"],
        fallback_only=current_app.config["FALLBACK_ONLY"],
    )
    llm_time_ms = round((perf_counter() - llm_started) * 1000, 2)
    total_time_ms = round((perf_counter() - started_at) * 1000, 2)

    if response["engine"] == "fallback" and response.get("reason") == "guardrail_rejected":
        warnings.append("Alfred used the safe fallback formatter because the local model response did not pass the project guardrail.")

    timings = {
        "parse_ms": parse_time_ms,
        "data_fetch_ms": data_fetch_ms,
        "llm_ms": llm_time_ms,
        "total_ms": total_time_ms,
    }

    append_request_log(
        current_app.config["LOG_DIR"],
        {
            "message": message,
            "mode": mode,
            "intent": parsed.intent,
            "entity": parsed.entity,
            "engine": response["engine"],
            "model": response["model"],
            "reason": response.get("reason"),
            "warnings": warnings,
            "timings": timings,
            "metrics": metrics["snapshot"] if metrics else None,
        },
    )

    return jsonify(
        {
            "reply": response["text"],
            "engine": response["engine"],
            "model": response["model"],
            "reason": response.get("reason"),
            "mode": mode,
            "intent": parsed.intent,
            "entity": parsed.entity,
            "warnings": warnings,
            "metrics": metrics["snapshot"] if metrics else None,
            "timings": timings,
        }
    )
