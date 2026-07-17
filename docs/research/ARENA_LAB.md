# Obolus Arena lab — proven knobs (private)

Private harness: [obolus-arena](https://github.com/maximilianwruhs-cyber/obolus-arena) (not production-ready).  
Public product still ships **MCP-first** benchmarking; this note captures what the lab already verified so product docs stay honest.

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

- Simple ε floor for DNA sole-survivor
- Recipe ratchet: `max(ε, mad_k × MAD)` over champion re-scores (default 3 samples, `mad_k=1`) — same idea as pi-autoresearch

## Recipe bounds (ratchet editable asset)

| Knob | Bounds |
|------|--------|
| `lr` | `[1e-5, 5e-4]` |
| `epochs` | `[0.5, 3.0]` |
| `lora_r` | `{8, 16, 32}` |
| `n` | `[100, 2000]` |
| `batch_size` | `[1, 8]` |
| `grad_accum` | `[1, 32]` |
| `max_seq_len` | `[128, 1024]` |

## What belongs in the public product vs lab

| In public Obolus | Stays in Arena lab |
|------------------|--------------------|
| z-score, offline price, RAPL/estimate | DNA forge / sole-survivor population |
| Math suite benchmarking | QLoRA / DPO / recipe overnight loops |
| Recommend best local model | Adapter export / Ollama tag factory |

## Dogfood mutator (specialized skill organ)

Arena Phase 6 trains a one-skill editor on **local** mutation traces + synthetic dogfood fixtures (no FineWeb). The harness is the product: exact SEARCH/REPLACE apply, pytest gate, then optional LoRA. Phase **6b** is toy microbench (`--suite microbench`); Phase **6c** dogfoods **fixture mirrors** of product helpers (z / price_factor / evaluator / energy) via `--suite obolus` — never live public tree mid-flight. Fixed train/eval scaffold — DNA mutates policy, not the holdout suite.

## Next scale

Same ladder on `Qwen/Qwen2.5-Coder-1.5B-Instruct` / `qwen2.5-coder:1.5b` (see Arena `docs/PLAN.md`).

## Future (10× direction — not a ship claim)

Arena’s north star is a **local metabolism of skill organs** (mutator, router, answerer) that promote only under **z**, then optionally export tags+z hints into public Obolus. Phases **7–12** live in Arena [`docs/NORTH_STAR.md`](https://github.com/maximilianwruhs-cyber/obolus-arena/blob/main/docs/NORTH_STAR.md). **Phases 7–9 done:** mutator gate, organ registry, JSON router (`router run` — bench|mutate|abstain, joules vs always-mutator). Next: metabolism timer (Phase 10). Public stranger path stays `make demo`. Still **not production-ready**.

## Pointers

- Arena policy: `obolus-arena/program.md`
- Arena phase map: `obolus-arena/docs/PLAN.md`
- Arena north star: `obolus-arena/docs/NORTH_STAR.md`
- Broader SLM research: [SLM_TRAINING.md](./SLM_TRAINING.md)

## Example ladder ranking (single seed; estimate energy)

| Rank label | Model | z |
|------------|-------|---|
| ratchet | `obolus-arena-ratchet` | 0.0447 |
| base | `qwen2.5-coder:0.5b` | 0.0402 |
| dpo | `obolus-arena-dpo` | 0.0212 |
| sft | `obolus-arena-sft` | 0.0210 |

Energy method and DNA seed jitter move absolute z; use the same seed/pop when comparing.
