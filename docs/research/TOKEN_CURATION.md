# Token curation for Obolus Arena (Phase 5)

Desk notes (2026-07-17):

- [`desk/For_training_very_small_models_datasets.md`](desk/For_training_very_small_models_datasets.md)
- [`desk/Token_Curation_Architecture.md`](desk/Token_Curation_Architecture.md)

## Locked decision

Stay on the **PEFT ladder** (dense SFT → DPO → recipe ratchet). Do **not** open FineWeb-scale continued pretrain. Upgrade **post-training token density** under the same product metric:

```
z = quality / (joules × price_factor)
```

## Four-tier quality rubric

Each training row is scored 0–5 on:

1. **Informational density** — facts / structure / logic vs fluff  
2. **Educational value** — teaches a concept or solves a problem  
3. **Syntactic cleanliness** — no HTML scraps, nav boilerplate, log noise  
4. **Reasoning signal** — step-by-step or deterministic code path (even if the *assistant* answer stays short)

Accept if mean score ≥ threshold (default **3**) and hard gates pass.

## Hard gates (Arena)

- Never train on Phase-1 holdout prompts (`train/eval_holdout.py`)
- Reject ultra-long assistant answers (hurts joules / **z**)
- Reject HTML / cookie / nav markers
- Prefer verifiable short answers (math / code return value)

## Post-train mix (default)

| Slice | Share | Source |
|-------|-------|--------|
| Short arithmetic | 40% | procedural generator |
| Math word problems | 35% | local Orca-Math-style + capped HF sample |
| Tiny Python-Edu | 25% | local “what does this return?” snippets |

## Anti-patterns

- **Style-over-substance:** encyclopedic tone ≠ educational value — heuristics reject fluff even if “textbook-shaped”  
- **Commonsense depletion:** not relevant for our short-answer math/code suite; do not replace the whole mix with pure textbooks  
- **Raw Common Crawl** — forbidden for this lab  
- **Eval leakage** — holdout prompts blocked before write

## Tooling

```bash
cd train
uv run python build_dense_dataset.py --out-dir ../data/sft --n 2000
uv run python curate.py --in ../data/sft/raw.jsonl --out ../data/sft/train.jsonl --min-score 3
```

`cargo run -- train sft` builds the dense curated mix by default.
