# Obolus Product

**Which local model gives you the best answers per joule on your machine.**

## Goals

- Benchmark local Ollama models for quality and energy on *your* hardware
- Rank models with a single, documented z-score
- Project local electricity cost at personal / team / enterprise query rates
- Work offline by default (fixed ¢/kWh; RAPL or CPU estimate)

## Non-goals (v1)

- AgenticOS / AOS / HSP / OpenClaw / NUC coupling
- Evolutionary arena, forge, wallets, or on-chain rewards as the product
- Live electricity APIs as a hard dependency (aWATTar is opt-in)
- Process reapers, host mutation tools, or datacenter agent personas
- Cloud SaaS or remote telemetry

Private training lab (DNA → QLoRA → DPO → recipe ratchet → dogfood mutator) lives in
[obolus-arena](https://github.com/maximilianwruhs-cyber/obolus-arena); see
[docs/research/ARENA_LAB.md](research/ARENA_LAB.md) for proven knobs that may
later inform product defaults — not shipped in the stranger path.

**Optional (Phase 22 product fold v0.2):** Arena can fold local **organ** hints (tag + score + role/metric) via `organs fold`. Copy lands in `data/organ_hints.json` (or set `OBULUS_ORGAN_HINTS`); `obulus.py recommend` shows an extra **display-only** section — hints never override `best_overall`. Absent by default — stranger path below does not require Arena. See [ARENA_LAB.md](research/ARENA_LAB.md) and Arena `docs/SHIP_BAR.md`. Organ metabolism stays behind the Arena ship bar.

## Stranger path

```bash
git clone https://github.com/maximilianwruhs-cyber/Obolus.git
cd Obolus
make setup
# Ollama running + at least one chat model pulled
make demo    # math suite → recommend
```

## Pricing

| Mode | Env | Behavior |
|------|-----|----------|
| Offline (default) | `OBULUS_PRICE_SOURCE=offline` | Use `OBULUS_ELECTRICITY_C_KWH` (default 25) |
| Live opt-in | `OBULUS_PRICE_SOURCE=awattar` | Fetch aWATTar AT spot; fall back to default |

## Energy

| Source | When |
|--------|------|
| `rapl` | Intel RAPL sysfs readable |
| `estimate` | Otherwise (CPU% × TDP) |

Always labeled in benchmark output and saved JSON.
