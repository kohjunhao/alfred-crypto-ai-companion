# Alfred: Your Crypto AI Companion

Public repository:

`https://github.com/kohjunhao/alfred-crypto-ai-companion`

Alfred is a Flask-based cryptocurrency chatbot that uses:

- Regex intent parsing
- CoinGecko and DefiLlama for live market data
- Ollama for optional local LLM generation
- a safe fallback formatter when the local model is unavailable or rejected

## Files needed to run Alfred

These files should stay in the repository:

- `run.py`
- `requirements.txt`
- `alfred_app/__init__.py`
- `alfred_app/routes.py`
- `alfred_app/intent_parser.py`
- `alfred_app/data_fetcher.py`
- `alfred_app/llm_engine.py`
- `alfred_app/telemetry.py`
- `alfred_app/templates/index.html`
- `alfred_app/static/css/styles.css`
- `alfred_app/static/js/app.js`

## Setup

1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Optional: start Ollama

```bash
ollama serve
```

Alfred expects Ollama at `http://localhost:11434` and uses `llama3` by default.

4. Run Alfred

```bash
python run.py
```

Then open:

`http://127.0.0.1:5001`
