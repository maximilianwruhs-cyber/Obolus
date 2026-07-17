# Obolus Roadmap

## ✅ v0.1 — Local model economics (shipped)

- Single-model benchmarking (quality + energy)
- Intel RAPL measurement with CPU×TDP estimate fallback (labeled)
- Math / code / factual / reasoning task suites
- Product z-score: `quality / (joules × price_factor)`
- Offline electricity price by default; aWATTar opt-in
- Recommender with cost projections vs cloud APIs
- Stranger path: `make setup` → `make demo`

## Experimental (not v1 product)

- Evolutionary arena / Forge / multi-model mutation
- Separate fitness formula in `fitness_scorer.py`
- Integration hooks (sensorium, thermal governor, dashboard)

## 🔜 Next

- [ ] Smart model router (cheapest model that meets a quality bar)
- [ ] Real-world task suites (summarization, JSON extraction, refactor)
- [ ] Hardware-specific optimization profiles
- [ ] Optional local dashboard for visualization
- [ ] Export as Ollama Modelfile with optimized parameters

## Later (maybe)

- Decentralized / on-chain leaderboard — only if it stays true to local economics
