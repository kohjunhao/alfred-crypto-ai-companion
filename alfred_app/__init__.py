from pathlib import Path
import os

from flask import Flask

from .routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    log_dir = Path(os.getenv("ALFRED_LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    app.config.from_mapping(
        SECRET_KEY="alfred-dev-key",
        OLLAMA_URL=os.getenv("OLLAMA_URL", "http://localhost:11434"),
        OLLAMA_MODEL=os.getenv("OLLAMA_MODEL", "llama3"),
        REQUEST_TIMEOUT=int(os.getenv("ALFRED_REQUEST_TIMEOUT", "30")),
        FALLBACK_ONLY=os.getenv("ALFRED_FALLBACK_ONLY", "0") == "1",
        LOG_DIR=log_dir,
    )
    app.register_blueprint(bp)
    return app
