# Alfred: Your Crypto AI Companion

Public repository:

`https://github.com/kohjunhao/alfred-crypto-ai-companion`

Alfred is a complete CM3070-ready web app built from scratch with:

- Flask backend
- Regex-based intent parsing
- concurrent API retrieval with `ThreadPoolExecutor`
- CoinGecko + DefiLlama aggregation
- Ollama integration for local LLM responses
- deterministic fallback responses when Ollama is not running
- editorial-style frontend inspired by institutional research dashboards
- request timing diagnostics and JSONL logging for evaluation evidence

## Features

- `PRICE` intent for live market checks
- `TVL` intent for DeFi protocol checks
- `GENERAL CHAT` support for lightweight conversation
- `SIMPLE` mode for novice-friendly explanations
- `PRO` mode for compact table-style responses
- live metric snapshot panel
- safe boundaries: no trading, no wallet actions, no direct financial advice

## Project structure

```text
alfred_app/
  __init__.py
  data_fetcher.py
  intent_parser.py
  llm_engine.py
  routes.py
  static/
    css/styles.css
    js/app.js
  templates/
    index.html
run.py
requirements.txt
tests/
```

## Setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Optional: start Ollama

If you want real local LLM generation instead of Alfred's built-in fallback formatter:

```bash
ollama serve
ollama pull llama3
```

The app expects Ollama at `http://localhost:11434` and the model name `llama3`.

### 4. Run Alfred

```bash
python run.py
```

Then open:

`http://127.0.0.1:5001`

## Test the parser

```bash
python -m unittest discover -s tests
```

## Run the latency script

```bash
python scripts/run_latency_checks.py
```

This writes a CSV file to `evaluation_outputs/latency_results.csv`, which is useful for the Evaluation chapter.

## Run the model comparison scripts

```bash
python scripts/run_llm_prompt_comparison.py
python scripts/run_model_comparison.py
```

These write controlled and live comparison outputs for `llama3` and `qwen2.5:3b` into `evaluation_outputs/`.

## Notes

- CoinGecko handles most market data.
- DefiLlama handles protocol TVL data.
- If one source fails, Alfred still returns the data that was successfully retrieved.
- If Ollama is unavailable, Alfred still works using deterministic safe responses.
- Request logs are written to `logs/alfred_requests.jsonl`.
- You can force fallback mode with:

```bash
export ALFRED_FALLBACK_ONLY=1
python run.py
```

## Is local Ollama the right choice?

For this CM3070 project, yes. Local Ollama supports your report's privacy and transparency argument, and it fits the scope of a final-year student project well. The practical trade-off is that the best version of Alfred runs on the machine hosting the model. To keep the product usable for demos and screenshots even without Ollama, this app includes a safe fallback response engine.

## Suggested next upgrades

- add richer asset alias mapping
- show source timestamps more prominently
- add better handling for unsupported metrics such as non-applicable TVL
- add simple latency logging for report screenshots
