# SLM Training: State of the Art & Practical Ladder for Obolus

**Research date:** mid-2026 (sources through ~Jul 2026)  
**Scope:** How to approach training Small Language Models (SLMs)—what is freely available online, what is SOTA, and what Obolus should do first.  
**Method:** Prefer primary sources (papers, model cards, first-party docs/READMEs). Confidence notes where only secondary coverage was found.

---

## 1. What “SLM” means in practice

There is no universal cutoff. Recent surveys cluster **task-agnostic SLMs roughly in the ~1–9B** range (often treating **&lt;8B** as the practical “small / single-consumer-GPU” band), while **sub-billion** models are a distinct on-device tier ([Gupta et al. survey, arXiv:2501.05465](https://arxiv.org/abs/2501.05465); [MobileLLM, arXiv:2402.14905](https://arxiv.org/abs/2402.14905)).

| Tier | Typical params | Deployment context | Training reality for a small team |
| --- | --- | --- | --- |
| Tiny / on-device | &lt;1B (e.g. MobileLLM 125M–950M) | Phone / edge CPU, ExecuTorch | Full pretrain is research-lab scale; adapt via PEFT or use released recipes |
| Small local | ~1–3B | Laptop / 8–16GB GPU, Ollama | QLoRA SFT/DPO feasible; strong base models already exist |
| Upper-SLM | ~3–8B | Single 24GB GPU inference; QLoRA train | Best ROI for domain adaptation; full FT expensive |
| Mid / LLM | ≥10–13B+ | Multi-GPU or heavy quant | Outside Obolus’s default “local economics” sweet spot |

**Why train (or adapt) at all vs only prompt?**

- **Capacity is scarce:** small models overfit noise and under-absorb incidental facts; data *quality and mix* dominate ([SmolLM2](https://arxiv.org/abs/2502.02737); Phi line thesis summarized in [Phi-4-Mini report](https://arxiv.org/abs/2503.01743)).
- **Prompting is free but shallow:** system prompts / decoding change behavior without changing weights—great for Obolus “DNA,” weak for new skills or format reliability.
- **Weights pay off** when you need: domain style, tool/JSON schemas, math/code patterns, or preference for short high-z answers (quality ÷ energy).

**So what:** For Obolus, treat “SLM training” mostly as **post-training adaptation of an already-strong open base** (1.5–7B), not from-scratch pretraining—unless you are explicitly running a Karpathy-style research loop on tiny models.

---

## 2. Training approaches ladder (best-practice path)

Climb only as far as the previous rung fails on *your* metric (for Obolus: verifiable quality and joules → **z**).

### Rung 0 — No weights: prompt, system prompt, decoding

- Ollama [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) parameters: `SYSTEM`, `PARAMETER temperature/top_p/num_ctx`, stop tokens, etc.
- Matches Obolus “Genome / DNA” already: system prompt, model choice, temperature, tool bias ([`docs/CONCEPT.md`](../CONCEPT.md)).
- **Cost:** zero train GPU; **risk:** brittle across models; **eval:** same suites you already run.

### Rung 1 — Supervised fine-tuning (SFT)

- Teach input→output pairs (instruction/response, tool traces, short answers).
- Standard open stack: [Hugging Face TRL `SFTTrainer`](https://huggingface.co/docs/trl/en/index) + Transformers + Datasets.
- Open recipes: [Tülu 3](https://arxiv.org/abs/2411.15124) (SFT → DPO → RLVR); [SmolTalk](https://huggingface.co/datasets/HuggingFaceTB/smoltalk) for small-model SFT ([SmolLM2 paper](https://arxiv.org/abs/2502.02737)).

### Rung 2 — Preference / alignment (DPO family)

- Prefer **chosen** over **rejected** completions without a separate reward-model PPO loop ([DPO, Rafailov et al., arXiv:2305.18290](https://arxiv.org/abs/2305.18290)).
- Common variants in tooling: **DPO** (stable in TRL), **KTO** (binary desirable/undesirable; TRL stable), **ORPO** (SFT+odds-ratio; often experimental), plus online/RL methods (**GRPO**, RLOO) in [TRL v1](https://huggingface.co/blog/trl-v1).
- Tülu 3 found **length-normalized DPO** + **on-policy** pairs strong in open recipes ([Ai2 Tülu 3 technical post](https://allenai.org/blog/tulu-3-technical)).
- Reasoning SLMs add **RL with verifiable rewards** (math/code correctness)—see [Phi-4-Mini-Reasoning recipe](https://arxiv.org/abs/2504.21233) (mid-train CoT distillation → SFT → Rollout DPO → RLVR).

### Rung 3 — PEFT: LoRA / QLoRA / DoRA

- **LoRA:** low-rank adapters; merge for zero inference overhead ([Hu et al.; PEFT docs](https://huggingface.co/docs/peft/en/developer_guides/lora)).
- **QLoRA:** 4-bit frozen base + LoRA—consumer-GPU workhorse ([Dettmers et al.; widely implemented in Unsloth/TRL/PEFT](https://huggingface.co/docs/trl/main/en/dpo_trainer)).
- **DoRA:** magnitude/direction decomposition; often better than LoRA at similar or lower rank; `use_dora=True` in PEFT ([DoRA paper](https://arxiv.org/abs/2402.09353); [NVlabs/DoRA](https://github.com/NVlabs/DoRA)). NV tip: start with slightly lower LR and often **half the LoRA rank**.

**PEFT practice for small models (operator heuristics, medium confidence):**

- Target attention + MLP projections; rank **8–16** for style/format, **32+** only if teaching substantial new behavior.
- Prefer **bf16** adapters on Ampere+; keep chat template identical between train and Ollama serve.
- Merge adapters (or ship GGUF) before comparing energy—extra adapter runtime can hurt **z** even if quality rises.

### Rung 4 — Full fine-tune vs continued pretrain

| Method | When | Cost |
| --- | --- | --- |
| Full FT all weights | Rare for 7B+ on one GPU; more plausible at ≤3B with short runs | High VRAM / risk of catastrophic forgetting |
| Continued / mid-training | Inject domain tokens or long CoT before SFT (Phi/Smol recipes) | Needs large curated corpora; lab-scale if done from scratch |
| Distillation from teacher | Soft labels / synthetic CoT from larger model | Dominant path for SOTA open SLMs (Gemma 3: “trained with distillation” — [Gemma 3 report](https://arxiv.org/abs/2503.19786)) |

**So what:** Obolus should treat full pretrain as **out of scope** for product; optional for research toys (nanochat). Prefer **QLoRA SFT/DPO on a distilled/instruct base**.

### Rung 5 — Distillation & synthetic data

SOTA small models are **data-centric**:

- **Phi:** textbook-quality / synthetic math & code ([Phi-4-Mini](https://arxiv.org/abs/2503.01743)).
- **SmolLM2:** ~11T tokens, multi-stage mix; released FineMath, Stack-Edu, SmolTalk ([paper](https://arxiv.org/abs/2502.02737)).
- **Gemma 3:** distillation + post-training recipe; sizes 1B–27B ([report](https://arxiv.org/abs/2503.19786); [model card](https://ai.google.dev/gemma/docs/core/model_card_3)).
- **MobileLLM-R1:** open sub-billion reasoning recipes ([arXiv:2509.24945](https://arxiv.org/abs/2509.24945); [facebookresearch/MobileLLM](https://github.com/facebookresearch/MobileLLM)).

Practical distillation for Obolus: use a **strong local or API teacher** to generate short, correct answers for your suites; filter with unit tests / exact match; SFT the student; optionally DPO (good vs verbose/wrong).

### Rung 6 — Speculative decoding (training-adjacent)

Not “making the model smarter,” but **lowering latency/energy per token** for the same quality:

- Classic **draft–target** (small draft + large target).
- **Medusa** heads / **EAGLE** feature-level drafters ([Medusa](https://github.com/FasterDecoding/Medusa); [EAGLE](https://arxiv.org/abs/2401.15077)); industrial tooling evolving (e.g. SpecForge / EAGLE-3 discussions in 2026 literature—[SpecForge, arXiv:2603.18567](https://arxiv.org/abs/2603.18567)).

**Obolus angle:** a tiny draft model or Medusa heads can improve **tokens/joule** if acceptance rates are high; measure with RAPL, don’t assume.

---

## 3. State of the art (mid-2026): families, PEFT, data, eval

### Leading SLM families (how they were trained)

| Family | Sizes (SLM-relevant) | Training thesis (primary) |
| --- | --- | --- |
| **Qwen2.5 / Qwen3** | 0.5B–7B+ | Large token budgets, strong post-train (DPO/GRPO etc.); dense size ladder ([Qwen2.5 report](https://arxiv.org/abs/2412.15115)) |
| **Gemma 3** | 1B, 4B, … | Distillation; long context via local/global attention; multimodal ([arXiv:2503.19786](https://arxiv.org/abs/2503.19786)) |
| **Llama 3.2** | 1B, 3B (+ quantized) | On-device / edge; QAT+LoRA and SpinQuant variants ([Llama 3.2 docs](https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_2/)) |
| **Phi-4-Mini** | 3.8B | Synthetic-heavy math/code; Mixture-of-LoRAs for multimodal; reasoning mid-train path ([arXiv:2503.01743](https://arxiv.org/abs/2503.01743), [2504.21233](https://arxiv.org/abs/2504.21233)) |
| **SmolLM2** | 135M–1.7B | Fully open **data recipe** + overtraining ([arXiv:2502.02737](https://arxiv.org/abs/2502.02737)) |
| **MobileLLM / R1** | ≤1B | Architecture for on-device + open reasoning recipes ([2402.14905](https://arxiv.org/abs/2402.14905), [2509.24945](https://arxiv.org/abs/2509.24945)) |

Cross-cutting SOTA pattern: **multi-stage data mix → SFT → preference → (optional) RLVR / reasoning**, with **synthetic CoT** from larger teachers for math/code.

### Data recipes matter more than architecture (at fixed size)

Consensus from SmolLM2, Phi, Tülu 3, and surveys:

1. Filter web for educational / high-signal text (FineWeb-Edu, DCLM-style classifiers).
2. Upsample **math + code** late (annealing / mid-train).
3. SFT on diverse, concise instruction data sized to the model (SmolTalk vs full Magpie dumps).
4. Preference data: scale prompts; include **on-policy** generations; use LLM judges carefully (UltraFeedback lineage; Tülu 3 scaling).
5. For Obolus: **verifiable** tasks beat chat Elo—align train data to your suites.

### Evaluation norms (avoid MMLU vanity)

Use a **portfolio**, not a single leaderboard number:

| Layer | Examples | Why |
| --- | --- | --- |
| Knowledge | MMLU / MMLU-Pro | Saturated / contaminated risk; secondary for Obolus |
| Instruction | IFEval | Format/constraint following |
| Reasoning | BBH, MATH, GSM8K, GPQA | Harder; still often train-contaminated |
| Code | HumanEval, LiveCodeBench | Closer to real coding |
| Chat preference | MT-Bench, Arena Elo | Human preference ≠ energy efficiency |
| **Obolus-native** | Math/code/factual/reasoning suites + RAPL joules → **z** | Product truth |

Tülu 3 emphasizes **decontamination** and held-out evals ([paper](https://arxiv.org/abs/2411.15124)). SmolLM2 uses lighteval + domain-specific harnesses. **So what:** keep Obolus suites as the fitness function; use public benches only for regression sanity.

---

## 4. What is freely available online

### Frameworks & harnesses

| Tool | Role | Primary link |
| --- | --- | --- |
| **TRL** | SFT, DPO, KTO, GRPO, … + PEFT | [docs](https://huggingface.co/docs/trl/en/index), [v1 blog](https://huggingface.co/blog/trl-v1) |
| **Transformers / PEFT / Datasets** | Model I/O, LoRA/DoRA, data | [PEFT LoRA/DoRA](https://huggingface.co/docs/peft/en/developer_guides/lora) |
| **Unsloth** | Fast single-GPU QLoRA/RL; GGUF export; claims ~2× speed / large VRAM cuts | [GitHub](https://github.com/unslothai/unsloth), [docs](https://unsloth.ai/docs) |
| **Axolotl** | YAML-driven, multi-GPU, SFT/RL | [axolotl-ai-cloud/axolotl](https://github.com/axolotl-ai-cloud/axolotl) |
| **LLaMA-Factory** | Broad model/method coverage, WebUI, Unsloth backend option | [hiyouga/LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) |
| **LitGPT** | From-scratch recipes, LoRA/QLoRA, FSDP | [Lightning-AI/litgpt](https://github.com/Lightning-AI/litgpt) |
| **MLX / mlx-lm** | Apple Silicon generate + LoRA FT | [ml-explore/mlx-lm](https://github.com/ml-explore/mlx-lm) |
| **nanochat** | Minimal full-stack train→chat; single complexity dial `--depth` | [karpathy/nanochat](https://github.com/karpathy/nanochat) |
| **autoresearch** | Agent mutates `train.py`, fixed **5-min** runs, metric **val_bpb**; human edits `program.md` | [karpathy/autoresearch](https://github.com/karpathy/autoresearch) (NVIDIA GPU; Mac forks linked in README) |
| **open-instruct / olmes** | Tülu-style post-train + eval | [allenai/open-instruct](https://github.com/allenai/open-instruct), [allenai/olmes](https://github.com/allenai/olmes) |

**Secondary comparisons** (VRAM tables, “2–5× Unsloth” claims): useful for orientation but mark **medium confidence**—re-benchmark on your GPU ([example secondary writeups](https://docs.clore.ai/guides/comparisons/finetuning-comparison)). Prefer Unsloth/Axolotl/TRL first-party numbers.

### Datasets commonly used for SLM SFT / DPO

| Dataset | Use | Link |
| --- | --- | --- |
| SmolTalk / smol-smoltalk | SFT for small models | [HuggingFaceTB/smoltalk](https://huggingface.co/datasets/HuggingFaceTB/smoltalk) |
| FineMath, Stack-Edu | Math/code mid-train | via [SmolLM2 collection](https://huggingface.co/collections/HuggingFaceTB/smollm2-6723884218bcda64b34d7db9) |
| UltraFeedback (binarized) | DPO classic | e.g. [trl-lib/ultrafeedback_binarized](https://huggingface.co/datasets/trl-lib/ultrafeedback_binarized) (see TRL DPO docs) |
| Tülu 3 mixtures | SFT + prefs + RLVR | [Ai2 Tülu 3](https://allenai.org/blog/tulu-3-technical), Hub `allenai/tulu-3-*` |
| OpenHermes 2.5 | General SFT (subset carefully) | Common in mixes; license/check provenance |

### Hardware reality (order-of-magnitude)

| Setup | Realistic training | Realistic Ollama inference |
| --- | --- | --- |
| **1× consumer NVIDIA 12–24GB** | QLoRA SFT 1–8B; DPO 1–3B comfortable, 7B tight | 7B Q4/Q5 sweet spot for Obolus z-bench |
| **Apple Silicon 32–64GB unified** | mlx-lm LoRA; slower than CUDA Unsloth | Strong local inference |
| **CPU-only** | Tiny experiments / nanochat-CPU demos only | Small GGUF possible; energy ugly |
| **From-scratch pretrain (Smol/Mobile scale)** | Multi-node A100/H100 weeks | N/A for Obolus product |

Unsloth README (2026): Studio supports Windows/Linux/macOS; NVIDIA training primary; macOS training/MLX/GGUF called out ([unslothai/unsloth](https://github.com/unslothai/unsloth)). Autoresearch upstream: **single NVIDIA GPU**, 5-minute fixed budget ([karpathy/autoresearch](https://github.com/karpathy/autoresearch)).

---

## 5. Desk research synthesis (operator uploads)

Copied into [`docs/research/desk/`](desk/) from `~/Schreibtisch/research` (2026-07-17). These notes are **operator-authored secondary briefs** (mixed primary links + synthesis). Confidence: use for architecture/model shortlists; re-verify HumanEval numbers and licenses against Hub cards before shipping.

| File | Core claim for Obolus |
| --- | --- |
| [`Lokale Code-Optimierungs-Modelle.md`](desk/Lokale%20Code-Optimierungs-Modelle.md) | Split **two SLMs**: mutator (“Code Bencher”) vs structured router (“Black Boxer”); prefer Search/Replace over unified diffs for &lt;3B; grammar-constrained JSON |
| [`Lokale Self-Improving Code Loops.md`](desk/Lokale%20Self-Improving%20Code%20Loops.md) | Harness &gt; agent framework: autoresearch ratchet + LibCST/Tree-sitter slicing + Instructor/GBNF; genetic multi-candidate with small models |
| [`Optimizing Pi Coding Agent Performance.md`](desk/Optimizing%20Pi%20Coding%20Agent%20Performance.md) | Minimal tool surface; `AGENTS.md` / session isolation; [pi-autoresearch](https://github.com/davebcn87/pi-autoresearch) with **MAD noise floor** before commit |

### Dual-role SLM stack (from desk notes)

Hundreds of iterations/hour kill large models. Desk research recommends **resident** local engines (llama.cpp / Ollama) with prompt cache, not one generalist 7B for every step.

| Role | Job | Desk shortlist | Obolus mapping |
| --- | --- | --- | --- |
| **Mutator** | Patches / short answers / DNA proposals | Qwen2.5-Coder **1.5B** (Apache) or **3B** (check Qwen Research license); DeepSeek-Coder 1.3B **base** for domain SFT; Granite-3B-Code for long context | Arena competitor + Forge propose; default demo model family |
| **Router / judge-side** | Logs → strict JSON / routing | Gemma-3-1B-it (speed + GBNF); Llama-3.2-3B (system-prompt fidelity); Phi-4-mini (hard logic); Qwen2.5-1.5B (balanced extract) | Optional second model for structured scoring / arena orchestration—not the DNA under test |

**Edit format:** Diff-XYZ / Aider-style finding: &lt;3B models fail unified-diff hunks; **SEARCH/REPLACE blocks + fuzzy apply** are more reliable than `@@` diffs. FIM tokens help in-function edits; enforce EOS / `num_predict` or small models ramble past the patch (OpenCompass/Qwen issue noted in desk notes).

**Constrained decoding:** Do not trust prompt-only JSON on 1–3B. Use GBNF (llama.cpp), Outlines / XGrammar, or [Instructor](https://github.com/jxnl/instructor) / ollama-instructor with retry-on-validation. Self-describing schema keys reduce semantic hallucination inside forced JSON.

**Harness patterns to steal:**

1. **Immutable eval + editable asset + program.md** (Karpathy autoresearch).
2. **CST slicing** (LibCST / Tree-sitter)—mutate one function, preserve trivia; compile + pyflakes gate before accept ([Voidious/crispen](https://github.com/Voidious/crispen) as nearest “deterministic harness + local LLM” example in desk notes).
3. **Population genetics** ([code-evolution workshop](https://github.com/camilochs/pydaybcn2025-workshop-code-evolution)): many candidates from a small model beat one shot from a large one—aligns with 50× same-SLM Arena.
4. **Noise-aware accept:** pi-autoresearch only commits if improvement clears **Median Absolute Deviation** noise floor—Obolus should do the same for RAPL/estimate jitter on **z**.
5. **Pi-style DNA:** tiny system prompt, prefer `edit` over full rewrite, session isolation, lean tool allowlist—maps to Genome fields (prompt, temp, stop) more than to heavy agent frameworks.

**Fine-tune signal from desk notes:** example community LoRA [Beebey/qwen-coder-1.5b-educational](https://huggingface.co/Beebey/qwen-coder-1.5b-educational) on opc-sft-stage2—supports “SFT a 1.5B coder for format/clarity” as a realistic second rung, not only 7B adapters.

---

## 5b. Hugging Face scan — beyond decoder SLMs (Needle, BERT-class, tiny specialists)

Obolus’s default path is **decoder SLMs via Ollama**. HF also has **encoders, encoder–decoders, and ~25–200M specialists** that fit *parts* of the desk dual-role design (router / ranker / tool-call) better than a 1.5B chat model—and at far lower joules. Downloads below from Hub API (~2026-07-17); treat as order-of-magnitude.

### [Cactus-Compute/needle](https://huggingface.co/Cactus-Compute/needle) (priority find)

| | |
| --- | --- |
| **Size** | ~26–30M params (card: 26M; Hub safetensors ~30.4M) |
| **Arch** | Encoder–decoder **Simple Attention Network** (pure attention, **no FFN**); 12 enc / 8 dec; d=512; GQA 8/4; vocab 8192 |
| **Trained for** | **Function / tool calling** — distilled from Gemini 3.1; post-train 2B tokens of tool-call data |
| **Runtime** | Own stack: [cactus-compute/needle](https://github.com/cactus-compute/needle) + [Cactus](https://github.com/cactus-compute) on-device (claimed ~6k tok/s prefill, ~1.2k decode); **not** a drop-in Ollama/GGUF chat model |
| **Finetune** | First-class local FT: `needle playground` / `needle finetune data.jsonl` (Mac/PC); MIT |
| **Ecosystem** | [needle-hf](https://huggingface.co/Cactus-Compute/needle-hf), [needle-rs-safetensors](https://huggingface.co/Abdalrahman/needle-rs-safetensors), [needle-onnx](https://huggingface.co/onnx-community/needle-onnx), [needle-mlx](https://huggingface.co/TiGa-RCE/needle-mlx), community [needle-pi-coding-agent](https://huggingface.co/theabbie/needle-pi-coding-agent) |

**So what for Obolus:** Needle is a strong candidate for the **Black Boxer / tool-router** role (structured tool JSON at edge speeds), and for an **autoresearch-style FT ratchet on tool schemas**—not for math/code generation or as the Arena mutator DNA. Wiring cost: custom runtime vs Ollama. Energy win could be large if router calls dominate the loop.

### Encoder / BERT-family (classify, rank, retrieve — not generate)

These are **not** chat SLMs. Use them to **score, gate, retrieve, or classify** patches/logs cheaply; pair with a decoder mutator.

| Model | Params (approx) | Role | Hub |
| --- | --- | --- | --- |
| [answerdotai/ModernBERT-base](https://huggingface.co/answerdotai/ModernBERT-base) | ~149M | SOTA-ish general encoder; **code+text** pretrain; 8k ctx; fill-mask / classify / embed | very high downloads |
| [answerdotai/ModernBERT-large](https://huggingface.co/answerdotai/ModernBERT-large) | ~395M | Same family, stronger | high |
| [nomic-ai/modernbert-embed-base](https://huggingface.co/nomic-ai/modernbert-embed-base) | (ModernBERT) | Embeddings / similarity for chunk+patch retrieval | high |
| [microsoft/codebert-base](https://huggingface.co/microsoft/codebert-base) | ~125M | Classic NL↔code encoder ([CodeBERT paper](https://arxiv.org/abs/2002.08155)) | ~316k dl/mo |
| [microsoft/unixcoder-base](https://huggingface.co/microsoft/unixcoder-base) | ~125M | Stronger code understanding / search ([UniXcoder](https://arxiv.org/abs/2203.03850)) | ~164k dl/mo |
| [huggingface/CodeBERTa-small-v1](https://huggingface.co/huggingface/CodeBERTa-small-v1) | ~84M | Tiny code RoBERTa (CodeSearchNet) | solid baseline |
| [google-bert/bert-base-uncased](https://huggingface.co/google-bert/bert-base-uncased) / [distilbert/distilbert-base-uncased](https://huggingface.co/distilbert/distilbert-base-uncased) | 110M / 66M | Legacy NLP classify; **weak on code** vs ModernBERT/CodeBERT | ubiquitous |

**Training story:** classic HF — freeze or full FT a classification head (pass/fail patch, language-id, “needs router vs mutator”), or contrastive fine-tune for retrieval. Cheap on CPU/GPU; PEFT optional. **Does not replace** Qwen-Coder for SEARCH/REPLACE generation.

### Encoder–decoder code specialists (generate short patches / FIM-ish)

| Model | Params | Notes |
| --- | --- | --- |
| [Salesforce/codet5-small](https://huggingface.co/Salesforce/codet5-small) | ~60M | Classic CodeT5; text2text; good for **short** transform tasks |
| [Salesforce/codet5p-220m](https://huggingface.co/Salesforce/codet5p-220m) | ~220M | CodeT5+; stronger, still small vs 1.5B decoders |

Useful if the mutator job is **span fill / short rewrite** with a seq2seq head; less natural in Ollama than Qwen2.5-Coder.

### Tiny decoder / edge LLMs (still generative)

| Model | Params | Notes |
| --- | --- | --- |
| [Qwen/Qwen2.5-Coder-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct) | 0.5B | Smallest serious Qwen coder instruct; Ollama-friendly path |
| [facebook/MobileLLM-R1-140M](https://huggingface.co/facebook/MobileLLM-R1-140M) (+ R1-360M / 950M) | 140M–950M | Meta on-device / reasoning-oriented MobileLLM line ([paper](https://arxiv.org/abs/2509.24945)) |
| [bigcode/starcoderbase-1b](https://huggingface.co/bigcode/starcoderbase-1b) | 1B | Older Stack-trained base; FIM heritage |
| Falcon-H1-Tiny-Coder ~90M (GGUF on Hub) | ~90M | Ultra-tiny coder experiments; verify license/quality locally |

### Role matrix (updated)

| Job | Prefer | Avoid as primary |
| --- | --- | --- |
| Arena DNA / answer generation | Qwen2.5-Coder 0.5B–3B (Ollama) | BERT / Needle |
| Tool / JSON router (“Black Boxer”) | **Needle** *or* Gemma-3-1B + GBNF | Raw BERT without a head |
| Patch / log ranking, retrieve context | **ModernBERT** / UniXcoder / CodeBERT | Needle (wrong task) |
| Short seq2seq rewrite | CodeT5(+)-small/220m | bert-base-uncased |
| Cheap accept/reject gate before RAPL bench | DistilBERT/ModernBERT classifier FT | 7B judge |

**Implication for the ladder:** insert an optional **Rung 0.5 — specialist heads**: (a) Needle or constrained tiny decoder for structured I/O; (b) ModernBERT/UniXcoder for ranking/retrieval—**before** spending QLoRA budget on the mutator. Arena DNA stays on one frozen decoder; specialists are harness infrastructure.

---

## 5c. Arena lab results (private)

Open lab harness [Obolus-Arena](https://github.com/maximilianwruhs-cyber/Obolus-Arena) exercises the ladder in §6 on a workstation GPU.
Proven knobs, contamination rules, and MAD accept: [ARENA_LAB.md](./ARENA_LAB.md).

Phase 5 dense-data notes (desk → Arena): [desk/For_training_very_small_models_datasets.md](desk/For_training_very_small_models_datasets.md), [desk/Token_Curation_Architecture.md](desk/Token_Curation_Architecture.md). Arena summary: `obolus-arena/docs/research/TOKEN_CURATION.md`.

## 6. Recommended approach for Obolus

**Context:** Local Ollama inference; energy/quality **z-score**; experimental arena (same base SLM, many DNA variants, winner survives); interest in **LoRA + Karpathy-style autoresearch ratchet**. Desk research adds: dual SLMs, constrained I/O, CST harness, MAD accept. Roadmap marks arena/Forge as experimental ([`ROADMAP.md`](../../ROADMAP.md)).

### Practical ladder (do in order)

#### First — Maximize DNA search (no weight training)

1. Freeze a **mutator base** (prefer `qwen2.5-coder:1.5b` Apache path; escalate to 3B only if z/quality stalls—and check license).
2. Mutate Modelfile DNA only: system prompt, temperature, `num_predict`, stop/EOS, brevity constraints ([`JUDGE_DNA.md`](../JUDGE_DNA.md)). **Do not** swap base mid-tournament.
3. Fitness = **z**; accept winner only if Δz beats a **noise floor** (MAD / bootstrap over repeated energy samples)—desk + pi-autoresearch lesson.
4. Optional **specialist** (not Arena DNA): [Needle](https://huggingface.co/Cactus-Compute/needle) for tool/JSON routing, **or** Gemma-3-1B + GBNF/Instructor; optionally ModernBERT/UniXcoder to rank/retrieve patches before expensive mutator calls.
5. If the arena edits code/harness assets: SEARCH/REPLACE or FIM, not unified diffs; LibCST/Tree-sitter apply + compile gate.

**Exit criterion:** plateaus on z across ≥N seeds; still failing format/tool/domain tasks → go Second.

#### Second — QLoRA SFT on Obolus-native data

1. Build **500–5k** supervised examples from verifiable suites (correct *short* answers; SEARCH/REPLACE or FIM targets if training a mutator). Teacher: larger local model; reject long-winded correct answers (hurts energy).
2. Prefer **base** coder checkpoints for format SFT when inventing a private patch grammar (desk: DeepSeek-Coder-1.3B-base); Instruct for lighter style/brevity adapters.
3. Train LoRA/QLoRA (Unsloth/TRL); merge or GGUF before z-bench so adapter runtime does not fake energy wins.
4. Require **Δz > 0**, not just Δquality.

**Exit criterion:** SFT helps quality but verbosity/preference issues remain → Third.

#### Third — Preference pass from the arena

1. From arena rollouts: pair **winner vs loser** (or short-correct vs long-correct) as DPO/KTO data.
2. Prefer **on-policy** completions from the SFT checkpoint (Tülu lesson).
3. Optimize for judge score **and** token length / joules.

#### Fourth — Autoresearch-style ratchet (meta-optimization)

| autoresearch / pi-autoresearch | Obolus analogue |
| --- | --- |
| Fixed time budget | Fixed wall-clock: SFT steps **or** N bench episodes |
| Single scalar (`val_bpb` / `METRIC name=`) | **z** (held-out suite) |
| `checks.sh` before bench | compile / tests / schema validate before energy score |
| MAD noise floor | Reject “wins” inside energy measurement noise |
| Agent edits one file | Agent edits DNA spec, LoRA hyperparams, or short train script |
| Human edits `program.md` | Human edits research policy: allowed mutations, kill criteria |

Use [nanochat](https://github.com/karpathy/nanochat) / [autoresearch](https://github.com/karpathy/autoresearch) **literally** only for pretrain sandbox; for product, reuse the **ratchet + noise floor** on PEFT + Modelfile. [pi-autoresearch](https://github.com/davebcn87/pi-autoresearch) is the closest agent-harness packaging of that pattern.

#### Later / optional

- **RLVR** on math/code with unit-test rewards (Phi-4-Mini-Reasoning / Tülu)—high upside.
- Dual-model production loop (router + mutator) if orchestration JSON error rate dominates.
- Speculative decoding if latency/joules dominate after quality caps.
- Continued pretrain only with clear domain corpus—rarely first-line.

### What not to do early

- From-scratch multi-trillion-token pretrain—wrong economics.
- Chasing MMLU / vendor HumanEval alone—orthogonal to **z**; desk notes warn published Pass@1 often needs post-processing filters.
- Full FT 7B before proving QLoRA gains.
- Arena mutations that change **base model and DNA** simultaneously (confounds).
- Prompt-only JSON from 1–3B without grammar/schema enforcement.
- Unified-diff generation as the primary mutator format on &lt;3B.

---

## Open questions / unknowns

1. **Best mutator base for Obolus z on *your* RAPL box:** Qwen2.5-Coder 1.5B vs 3B vs Phi-4-mini—measure; desk shortlist ≠ measured z.
2. **Whether a second router model** (Gemma-3-1B + GBNF) pays for itself in joules vs one model with constrained decoding.
3. **Ollama + LoRA deployment path:** merge vs runtime LoRA vs GGUF—energy overhead per path.
4. **Whether DPO on brevity** improves z or truncates needed reasoning on hard tasks.
5. **Autoresearch / peft loops on consumer GPUs:** upstream H100-oriented; 1–3B PEFT forks under-documented (medium confidence).
6. **Contamination:** train data regenerated from the same suites as `make bench` inflates scores—need held-out tasks.
7. **License:** Qwen2.5-Coder-3B “Qwen Research” vs 1.5B Apache—desk flags commercial risk; verify current Hub license before product default.
8. **License / data provenance** for UltraFeedback/Tülu mixtures when shipping derivatives.
9. **Needle vs GBNF-on-Ollama:** Is custom Cactus/JAX (or needle-rs/ONNX) worth the integration cost vs Gemma-3-1B + grammar for the router role on *your* box?
10. **BERT-class gates:** Can a ModernBERT/UniXcoder accept/reject head cut wasted mutator+RAPL joules enough to raise end-to-end **z**?

---

## Sources

### Surveys & definitions
- [Small Language Models (SLMs) Can Still Pack a Punch: A Survey (arXiv:2501.05465)](https://arxiv.org/abs/2501.05465)

### Model family reports / cards
- [SmolLM2 (arXiv:2502.02737)](https://arxiv.org/abs/2502.02737) · [SmolTalk dataset](https://huggingface.co/datasets/HuggingFaceTB/smoltalk)
- [Qwen2.5 Technical Report (arXiv:2412.15115)](https://arxiv.org/abs/2412.15115)
- [Gemma 3 Technical Report (arXiv:2503.19786)](https://arxiv.org/abs/2503.19786) · [Gemma 3 model card](https://ai.google.dev/gemma/docs/core/model_card_3)
- [Phi-4-Mini (arXiv:2503.01743)](https://arxiv.org/abs/2503.01743) · [Phi-4-Mini-Reasoning (arXiv:2504.21233)](https://arxiv.org/abs/2504.21233)
- [Llama 3.2 model docs](https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_2/)
- [MobileLLM (arXiv:2402.14905)](https://arxiv.org/abs/2402.14905) · [MobileLLM-R1 (arXiv:2509.24945)](https://arxiv.org/abs/2509.24945) · [facebookresearch/MobileLLM](https://github.com/facebookresearch/MobileLLM)

### Methods
- [DPO (arXiv:2305.18290)](https://arxiv.org/abs/2305.18290)
- [DoRA (arXiv:2402.09353)](https://arxiv.org/abs/2402.09353) · [NVlabs/DoRA](https://github.com/NVlabs/DoRA)
- [Tülu 3 (arXiv:2411.15124)](https://arxiv.org/abs/2411.15124) · [Ai2 technical post](https://allenai.org/blog/tulu-3-technical)
- [EAGLE (arXiv:2401.15077)](https://arxiv.org/abs/2401.15077) · [Medusa](https://github.com/FasterDecoding/Medusa)

### Tooling
- [Hugging Face TRL](https://huggingface.co/docs/trl/en/index) · [TRL v1 blog](https://huggingface.co/blog/trl-v1) · [DPO trainer](https://huggingface.co/docs/trl/main/en/dpo_trainer)
- [Unsloth](https://github.com/unslothai/unsloth) · [Axolotl](https://github.com/axolotl-ai-cloud/axolotl) · [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
- [LitGPT](https://github.com/Lightning-AI/litgpt) · [mlx-lm](https://github.com/ml-explore/mlx-lm)
- [karpathy/nanochat](https://github.com/karpathy/nanochat) · [karpathy/autoresearch](https://github.com/karpathy/autoresearch)

### Obolus project context
- [`README.md`](../../README.md) · [`docs/CONCEPT.md`](../CONCEPT.md) · [`docs/JUDGE_DNA.md`](../JUDGE_DNA.md) · [`ROADMAP.md`](../../ROADMAP.md)

### Operator desk research (secondary; copied 2026-07-17)
- [`desk/Lokale Code-Optimierungs-Modelle.md`](desk/Lokale%20Code-Optimierungs-Modelle.md)
- [`desk/Lokale Self-Improving Code Loops.md`](desk/Lokale%20Self-Improving%20Code%20Loops.md)
- [`desk/Optimizing Pi Coding Agent Performance.md`](desk/Optimizing%20Pi%20Coding%20Agent%20Performance.md)
- Notable first-party links inside those briefs: [karpathy/autoresearch](https://github.com/karpathy/autoresearch), [davebcn87/pi-autoresearch](https://github.com/davebcn87/pi-autoresearch), [Voidious/crispen](https://github.com/Voidious/crispen), [jxnl/instructor](https://github.com/jxnl/instructor), Qwen2.5-Coder / Phi-4-mini / Gemma-3 model cards

### Hugging Face specialists (Hub API + model cards, 2026-07-17)
- [Cactus-Compute/needle](https://huggingface.co/Cactus-Compute/needle) · [cactus-compute/needle](https://github.com/cactus-compute/needle) · [onnx-community/needle-onnx](https://huggingface.co/onnx-community/needle-onnx)
- [answerdotai/ModernBERT-base](https://huggingface.co/answerdotai/ModernBERT-base) · [HF ModernBERT blog](https://huggingface.co/blog/modernbert)
- [microsoft/codebert-base](https://huggingface.co/microsoft/codebert-base) · [microsoft/unixcoder-base](https://huggingface.co/microsoft/unixcoder-base) · [huggingface/CodeBERTa-small-v1](https://huggingface.co/huggingface/CodeBERTa-small-v1)
- [Salesforce/codet5-small](https://huggingface.co/Salesforce/codet5-small) · [Salesforce/codet5p-220m](https://huggingface.co/Salesforce/codet5p-220m)
- [Qwen/Qwen2.5-Coder-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct) · [facebook/MobileLLM-R1-140M](https://huggingface.co/facebook/MobileLLM-R1-140M)

---

*Confidence legend: claims tied to arXiv/first-party READMEs above = high; desk briefs and VRAM blogs = medium; “best base for your RAPL box” = measure locally.*
