.PHONY: setup demo bench bench-full evolve recommend compare suites test clean help

PYTHON = .venv/bin/python3
VENV = .venv

help: ## Show this help
	@echo ""
	@echo "  OBULUS — best local model per joule"
	@echo ""
	@echo "  Usage: make <command>"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -e ".[dev]"

setup: $(VENV)/bin/activate ## Create venv and install dependencies
	@echo ""
	@echo "  Setup complete. Run 'make demo' (or 'make bench')."
	@echo ""
	@if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then \
		echo "  Ollama is not running. Start it with: ollama serve"; \
		echo "  Then pull a model: ollama pull qwen2.5-coder:7b"; \
		echo ""; \
	fi

_detect_model = \
	MODEL=$$(curl -s http://localhost:11434/api/tags 2>/dev/null | $(PYTHON) -c "import sys,json;d=json.load(sys.stdin);ms=[m['name'] for m in d.get('models',[]) if 'embed' not in m['name']];print(ms[0] if ms else '')" 2>/dev/null); \
	if [ -z "$$MODEL" ]; then \
		echo "  No Ollama models found. Run: ollama pull qwen2.5-coder:7b"; \
		exit 1; \
	fi; \
	echo "  Auto-detected model: $$MODEL"

demo: $(VENV)/bin/activate ## Stranger path: math bench → recommend
	@$(_detect_model); \
	$(PYTHON) obulus.py bench --model "$$MODEL" --suite math; \
	$(PYTHON) obulus.py recommend

bench: $(VENV)/bin/activate ## Benchmark a model (auto-detects first available)
	@$(_detect_model); \
	$(PYTHON) obulus.py bench --model "$$MODEL" --suite math

bench-full: $(VENV)/bin/activate ## Benchmark all suites
	@$(_detect_model); \
	$(PYTHON) obulus.py bench --model "$$MODEL" --suite full

evolve: $(VENV)/bin/activate ## Experimental: evolutionary arena
	@echo "  Note: evolve is experimental — not part of the v1 product surface."
	$(PYTHON) obulus.py evolve

recommend: $(VENV)/bin/activate ## Show model recommendations & cost projections
	$(PYTHON) obulus.py recommend

compare: $(VENV)/bin/activate ## Compare benchmark results across models
	$(PYTHON) obulus.py compare

suites: $(VENV)/bin/activate ## List available benchmark suites
	$(PYTHON) obulus.py suites

test: $(VENV)/bin/activate ## Run all tests
	$(PYTHON) -m pytest tests/ -v
	$(PYTHON) tests/test_fitness_scorer.py

clean: ## Remove generated data and caches
	rm -rf data/*.json __pycache__ src/**/__pycache__
	@echo "  Cleaned generated data and caches."
