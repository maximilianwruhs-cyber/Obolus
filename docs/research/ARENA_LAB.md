# Obolus Arena lab — proven knobs

Open lab harness: [Obolus-Arena](https://github.com/maximilianwruhs-cyber/Obolus-Arena).  
Public product still ships **MCP-first** benchmarking (`make demo`); this note captures what the lab verified so product docs stay honest.

Organ hints from Arena are **optional and display-only** — they never change `best_overall`.

## Metric (shared with product)

```
z = quality / (joules × price_factor)
price_factor = max(0.01, ¢/kWh / 25)
```

Offline default: **25 ¢/kWh**. Energy: RAPL when available, else estimate (always labeled).

## Ladder that worked on this workstation (0.5B)

Base: `Qwen/Qwen2.5-Coder-0.5B-Instruct` / Ollama `qwen2.5-coder:0.5b`

| Stage | What | Ollama tag (lab) |
|-------|------|------------------|
| DNA arena | Frozen model, mutate system/temp/num_predict, sole survivor | any frozen tag |
| QLoRA SFT | Dense curated mix (arith + word math + tiny Python); **never** train on eval holdout | `obolus-arena-sft` / `-dense` |
| Token curation | 4-tier filter (density / educational / syntactic / reasoning) — see Arena `TOKEN_CURATION.md` | n/a |
| DPO | Preference pairs (synthetic brevity default) on SFT merged | `obolus-arena-dpo` |
| Recipe ratchet | Mutate one SFT hyperparam → mini-SFT → keep/discard on **z** | `obolus-arena-ratchet` |
| Dogfood mutator | Ultra-small SEARCH/REPLACE skill organ: DNA over frozen coder → apply+pytest → dense SFT | `obolus-arena-mutator` |

Contamination rule: Phase-1 math suite prompts (`math_001`–`math_015`) are **eval-only**. Dogfood holdout tasks (`split=holdout` in Arena `dogfood/tasks.jsonl`) are likewise eval-only for the mutator.

## Accept / noise

Same doctrine as product eval noise floor: challenger must clear `max(ε, k·MAD)` on holdout **z** / pass_rate before promote. Experimental organs may graduate via `organs seal` when MAD holdout clears a minimum floor (human-in-the-loop; overnight promote stays dry-run).

## Same ladder on 1.5B

Same ladder on `Qwen/Qwen2.5-Coder-1.5B-Instruct` / `qwen2.5-coder:1.5b` (see Arena `docs/PLAN.md`).

## Future (10× direction)

Arena’s north star is a **local metabolism of skill organs** (mutator, router, answerer) that promote only under **z**, then optionally export tags+z hints into public Obolus. Phases **7–26** live in Arena [`docs/NORTH_STAR.md`](https://github.com/maximilianwruhs-cyber/Obolus-Arena/blob/main/docs/NORTH_STAR.md): mutator gate, organ registry, JSON router, metabolism timer, product fold v0.1→v0.2, safe apply zone, organ promotion, patch ranker, overnight metabolism, ranker SFT (`obolus-arena-ranker`), mutator×ranker coupling, suite-aware dogfood apply, mutator trace harvest, metabolize **hold** pack, lab **readiness** gate, operator overnight hold, hold report, lab smoke, **ship bar**. Public stranger path stays `make demo`. **Ship bar cleared 2026-07-18** (`production_ready` via Arena `--authorize-production`); organ hints remain display-only in recommend.

### Product fold v0.2 (optional, display-only)

```bash
# In Obolus-Arena (after readiness / organ scores):
cargo run -- organs fold --obolus-root ../Obolus --require-readiness
# In Obolus — recommend shows role/metric hints; does NOT change best_overall
# make demo still works without the file
obulus.py recommend
```

## Pointers

- Arena policy: `Obolus-Arena/program.md`
- Arena phase map: `Obolus-Arena/docs/PLAN.md`
- Arena north star: `Obolus-Arena/docs/NORTH_STAR.md`
- Ship bar / repro: `Obolus-Arena/docs/SHIP_BAR.md`, `Obolus-Arena/docs/REPRO.md`
- Broader SLM research: [SLM_TRAINING.md](./SLM_TRAINING.md)

## Example ladder ranking (single seed; estimate energy)

| Rank label | Model | z |
|------------|-------|---|
| ratchet | `obolus-arena-ratchet` | 0.0447 |
| base | `qwen2.5-coder:0.5b` | 0.0402 |
| dpo | `obolus-arena-dpo` | 0.0212 |
| sft | `obolus-arena-sft` | 0.0210 |

Energy method and DNA seed jitter move absolute z; use the same seed/pop when comparing.
