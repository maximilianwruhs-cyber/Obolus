# Obolus

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

> **Which local model gives you the best answers per joule on your machine.**

Obolus benchmarks your [Ollama](https://ollama.com) models for quality and energy — on **your** hardware, at **your** electricity price — then recommends the winner.

```
z = quality / (joules × price_factor)
```

`price_factor` is normalized around 25 ¢/kWh. Higher z is better.

Every other benchmark answers: *"How smart is this model?"*  
Obolus answers: **"Which model is worth running here, given energy and price?"**

## Quick start (≈10 minutes)

**Prerequisites:** [Python 3.10+](https://www.python.org/) and [Ollama](https://ollama.com) with at least one chat model (`ollama pull qwen2.5-coder:7b`).

```bash
git clone https://github.com/maximilianwruhs-cyber/Obolus.git
cd Obolus
make setup
make demo          # math suite → recommend
```

Or step by step:

```bash
make bench         # auto-detects first non-embed Ollama model
make recommend
```

One-liner (clone + setup + demo):

```bash
curl -fsSL https://raw.githubusercontent.com/maximilianwruhs-cyber/Obolus/main/scripts/install-obolus.sh | bash
```

## What you get

```
  Energy: RAPL (real watts) | or estimate (no RAPL)
  Electricity: 25.0 ¢/kWh (offline default)

  🏆 Best Overall: qwen2.5-coder:1.5b            z=0.1846
     Quality: 80.0%  |  Energy: 23.4J
```

Cost projections use your configured ¢/kWh (offline by default). Live spot pricing is opt-in.

## Commands

| Command | Description |
|---------|-------------|
| `make setup` | Create venv and install dependencies |
| `make demo` | Short stranger path: math bench → recommend |
| `make bench` | Benchmark auto-detected model (`math` suite) |
| `make bench-full` | Benchmark all task suites |
| `make recommend` | Show model recommendations + cost projections |
| `make compare` | Leaderboard from saved results |
| `make suites` | List suite sizes |
| `make test` | Run unit tests |
| `make clean` | Remove generated data |

CLI:

```bash
.venv/bin/python obulus.py bench --model qwen2.5-coder:7b --suite math
.venv/bin/python obulus.py recommend
.venv/bin/python obulus.py compare
```

## How it works

1. **Bench** — runs verifiable tasks (math, code, factual, reasoning) via Ollama; measures quality and joules (Intel RAPL when available, otherwise CPU×TDP estimate).
2. **Score** — `z = quality / (joules × price_factor)` with `price_factor = max(0.01, ¢/kWh / 25)`.
3. **Recommend** — picks the best saved run and projects €/mo at personal / team / enterprise query rates.

See [docs/PRODUCT.md](docs/PRODUCT.md) for goals and non-goals.

## Energy measurement

Intel RAPL (optional):

```bash
sudo chmod a+r /sys/class/powercap/intel-rapl:0/energy_uj
```

Without RAPL, Obolus uses an estimate and labels the run `energy_source: estimate`.

## Electricity price

| Mode | How |
|------|-----|
| **Offline (default)** | `OBULUS_ELECTRICITY_C_KWH=25` — no network |
| **Live (opt-in)** | `OBULUS_PRICE_SOURCE=awattar` — [aWATTar](https://www.awattar.at/) AT spot, then fallback |

Copy `.env.example` → `.env` to customize.

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API |
| `OBULUS_MODEL` | `qwen2.5-coder:7b` | Default model when not auto-detected |
| `OBULUS_ELECTRICITY_C_KWH` | `25` | Offline ¢/kWh |
| `OBULUS_PRICE_SOURCE` | `offline` | `offline` or `awattar` |

## Experimental

`make evolve` / `obulus.py evolve` is an experimental multi-model arena. It is **not** part of the v1 product surface. Prefer `bench` → `recommend`.

## License

[MIT](LICENSE) © Maximilian Wruhs
