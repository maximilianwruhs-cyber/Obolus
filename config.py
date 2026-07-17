"""
Obolus — Centralized Configuration
All paths resolved relative to this file's location. Override via .env or environment variables.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # python-dotenv is optional; env vars still work

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
AGENTS_DIR = PROJECT_ROOT / "agents"
DATA_DIR = PROJECT_ROOT / "data"
TOOLS_DIR = PROJECT_ROOT / "tools"
DOCS_DIR = PROJECT_ROOT / "docs"

# Ensure data dir exists at runtime
DATA_DIR.mkdir(exist_ok=True)

# ─── Ollama ───────────────────────────────────────────────────────────────────
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OBULUS_MODEL", "qwen2.5-coder:7b")

# ─── Electricity (offline-first) ──────────────────────────────────────────────
# price_source: "offline" (default) uses ELECTRICITY_C_KWH; "awattar" fetches live spot.
ELECTRICITY_C_KWH = float(os.getenv("OBULUS_ELECTRICITY_C_KWH", "25.0"))
PRICE_SOURCE = os.getenv("OBULUS_PRICE_SOURCE", "offline").strip().lower()

# ─── Arena Defaults (experimental evolve path) ────────────────────────────────
TOTAL_TOKENS_PER_ROUND = int(os.getenv("OBULUS_TOKENS_PER_ROUND", "2048"))
INITIAL_AGENT_BALANCE = float(os.getenv("OBULUS_INITIAL_BALANCE", "100.0"))

# ─── Optional Arena organ hints (Phase 11 product fold) ───────────────────────
# Absent by default: stranger path (make demo) does not require this file.
# Set OBULUS_ORGAN_HINTS to an absolute/relative path, or place data/organ_hints.json.
_ORGAN_HINTS_ENV = os.getenv("OBULUS_ORGAN_HINTS", "").strip()
ORGAN_HINTS_PATH = (
    Path(_ORGAN_HINTS_ENV).expanduser()
    if _ORGAN_HINTS_ENV
    else DATA_DIR / "organ_hints.json"
)
