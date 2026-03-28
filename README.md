# ⚡ Obolus

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Part of: AgenticOS](https://img.shields.io/badge/ecosystem-AgenticOS-blue)](https://github.com/maximilianwruhs-cyber)

> **Maximizing Intelligence per Watt.**

Obolus measures how much intelligence you get per watt of energy — on **your** hardware, with **your** models, at **your** electricity price.

```
z = (Quality × Efficiency) × (1 − Variance)
```

Every other benchmark answers: *"How smart is this model?"*  
Obolus answers: **"Which model gives me the best results for the least energy on my machine?"**

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/maximilianwruhs-cyber/Obolus.git
cd obulus
make setup

# 2. Run a benchmark (auto-detects your Ollama models)
make bench

# 3. See recommendations
make recommend
```

> **Prerequisites:** [Python 3.10+](https://python.org) and [Ollama](https://ollama.ai) with at least one model pulled (`ollama pull qwen2.5-coder:7b`).

## What You Get

### Model Recommendations with Live Energy Pricing
```
  ╔══════════════════════════════════════════════════════════════╗
  ║  OBOLUS RECOMMENDATION — Your Hardware Profile              ║
  ╠══════════════════════════════════════════════════════════════╣
  ║  ⚡ Electricity: LIVE 4.6 ¢/kWh                             ║
  ║  🟢 Very cheap — great time for heavy inference             ║
  ║                                                              ║
  ║  🏆 Best Overall: qwen2.5-coder:1.5b            z=0.1846   ║
  ║     Quality: 80.0%  |  Energy: 23.4J                       ║
  ║                                                              ║
  ║  💰 enterprise (10000 q/day)      €0.0060/mo   €0.07/yr    ║
  ║  ☁️  Claude 3.5                   $2.16/mo   (saves 100%)  ║
  ╚══════════════════════════════════════════════════════════════╝
```

### Evolutionary Arena
Models compete head-to-head. The Forge mutates losers — changing system prompts *and* model size — until only the most efficient survive.

```
  ⚡ Electricity: LIVE 4.6 ¢/kWh (Very cheap — full power)

  🟢 qwen2.5-coder:1.5b  z=14.0  Q=0.84  E=16.6  ✅
  🟡 qwen2.5-coder:7b    z=1.5   Q=0.67  E=2.2   ✅
  
  [CONVERGED] 1.5b wins — 80% quality at half the energy.
```

## Commands

| Command | Description |
|---------|-------------|
| `make setup` | Create venv and install dependencies |
| `make bench` | Benchmark with auto-detected model |
| `make bench-full` | Benchmark all task suites |
| `make evolve` | Run evolutionary multi-model arena |
| `make recommend` | Show model recommendations + costs |
| `make compare` | Compare results across models |
| `make test` | Run all tests |
| `make clean` | Remove generated data |

Or use the CLI directly:
```bash
python obulus.py bench --model qwen2.5-coder:7b --suite math
python obulus.py evolve --epochs 20 --patience 5
python obulus.py recommend
```

## How It Works

### Benchmark
Runs verifiable tasks (math, code, factual, reasoning) against your local model via Ollama, measuring both **quality** (correctness) and **energy** (joules via Intel RAPL or CPU load estimate).

### Fitness Scorer
The evolutionary fitness formula:
- **Q (Quality)** = 0.5 × pass_rate + 0.3 × time_score + 0.2 × similarity
- **E (Efficiency)** = baseline_energy / actual_energy
- **V (Variance)** = coefficient of variation across trials
- **z = (Q × E) × (1 − V)**

### Evolutionary Arena
1. Auto-discovers all Ollama models
2. Spawns one agent per model with diverse system prompts
3. Each epoch: multi-trial evaluation → fitness scoring → approval
4. Failed agents are reborn in the **Forge** with mutated prompts/models
5. Convergence detection stops early when no improvement

### Live Energy Pricing
Fetches real-time electricity spot prices from [aWATTar](https://www.awattar.at/) (Austrian energy market). When electricity is expensive, agents earn fewer rewards — creating genuine economic pressure for efficiency.

## Project Structure

```
obulus/
├── obulus.py                  # CLI entry point
├── config.py                  # Configuration (env-based)
├── Makefile                   # One-command workflows
│
├── src/
│   ├── benchmark/
│   │   ├── runner.py          # Benchmark orchestrator
│   │   ├── task_suite.py      # 30 verifiable tasks
│   │   ├── evaluator.py       # Multi-strategy scorer
│   │   ├── energy_meter.py    # Intel RAPL / CPU load energy
│   │   ├── fitness_scorer.py  # Evolutionary fitness (z-score)
│   │   ├── recommender.py     # Model recommendations + costs
│   │   ├── model_discovery.py # Auto-discover Ollama models
│   │   ├── leaderboard.py     # Persistent mutation leaderboard
│   │   └── awattar.py         # Live electricity pricing
│   ├── core/                  # Agent primitives (genome, wallet, brain)
│   ├── simulation/            # Arena, forge, validators
│   └── integration/           # Hardware sensorium
│
├── agents/                    # Agent DNA files (system prompts)
├── tools/                     # Agent-invocable tools
├── tests/                     # Unit tests
├── docs/                      # Scientific foundations & concept
└── data/                      # Runtime state (gitignored)
```

## Energy Measurement

Obolus uses **Intel RAPL** (Running Average Power Limit) for real energy measurement:
```bash
sudo chmod a+r /sys/class/powercap/intel-rapl:0/energy_uj
```
Without RAPL access, it falls back to a CPU load × TDP estimate.

## Configuration

Copy `.env.example` to `.env` and customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OBULUS_MODEL` | `qwen2.5-coder:7b` | Default model (overridden by auto-discovery) |
| `OBULUS_INITIAL_BALANCE` | `100.0` | Starting $OBL per agent |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## AgenticOS Ecosystem

| Project | Description |
|---------|-------------|
| [**AOS**](https://github.com/maximilianwruhs-cyber/AOS) | Sovereign AI layer for Ubuntu — the brain of the ecosystem |
| [**AOS Customer Edition**](https://github.com/maximilianwruhs-cyber/AOS-Customer-Edition) | Zero-touch deployment — one `curl` command installs everything |
| [**AOS Intelligence Dashboard**](https://github.com/maximilianwruhs-cyber/AOS-Intelligence-Dashboard) | VS Codium extension for real-time energy monitoring & LLM leaderboard |
| [**HSP**](https://github.com/maximilianwruhs-cyber/HSP) | Hardware Sonification Pipeline — turn machine telemetry into music |
| [**HSP VS Codium Extension**](https://github.com/maximilianwruhs-cyber/HSP-VS-Codium-Extension) | VS Codium sidebar for live HSP telemetry visualization |

## License

[MIT](LICENSE) © Maximilian Wruhs
