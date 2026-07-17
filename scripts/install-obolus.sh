#!/usr/bin/env bash
# Obolus one-liner install: clone (if needed) → venv → demo
set -euo pipefail

REPO_URL="${OBULUS_REPO_URL:-https://github.com/maximilianwruhs-cyber/Obolus.git}"
INSTALL_DIR="${OBULUS_DIR:-$HOME/Obolus}"
DEFAULT_MODEL="${OBULUS_MODEL:-qwen2.5-coder:7b}"

echo ""
echo "  Obolus — best local model per joule"
echo ""

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "  Missing dependency: $1"
    echo "  Install it, then re-run this script."
    exit 1
  fi
}

need git
need python3
need curl

if [ ! -d "$INSTALL_DIR/.git" ]; then
  echo "  Cloning into $INSTALL_DIR ..."
  git clone "$REPO_URL" "$INSTALL_DIR"
else
  echo "  Using existing clone at $INSTALL_DIR"
fi

cd "$INSTALL_DIR"

if [ ! -x .venv/bin/python3 ]; then
  echo "  Creating venv and installing..."
  make setup
else
  echo "  venv present — ensuring package is installed..."
  .venv/bin/pip install -e ".[dev]" -q
fi

if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo ""
  echo "  Ollama is not reachable at http://localhost:11434"
  echo "  Start it (ollama serve), pull a model, then:"
  echo "    cd $INSTALL_DIR && make demo"
  echo ""
  exit 0
fi

MODEL="$(curl -s http://localhost:11434/api/tags | .venv/bin/python3 -c "
import sys, json
d = json.load(sys.stdin)
ms = [m['name'] for m in d.get('models', []) if 'embed' not in m['name']]
print(ms[0] if ms else '')
" 2>/dev/null || true)"

if [ -z "$MODEL" ]; then
  echo "  No chat models found. Pulling $DEFAULT_MODEL ..."
  if command -v ollama >/dev/null 2>&1; then
    ollama pull "$DEFAULT_MODEL"
    MODEL="$DEFAULT_MODEL"
  else
    echo "  Install Ollama, pull a model, then: cd $INSTALL_DIR && make demo"
    exit 0
  fi
fi

echo "  Running demo with $MODEL ..."
make demo

echo ""
echo "  Done. Next time: cd $INSTALL_DIR && make demo"
echo ""
