# Contributing to Obolus

Thanks for your interest in Obolus! Here's how you can contribute.

## Quick Start for Contributors

```bash
git clone https://github.com/maximilianwruhs-cyber/Obolus.git
cd obulus
make setup
make test
```

## Ways to Contribute

### Add Benchmark Tasks
Tasks live in `src/benchmark/task_suite.py`. Each task needs:
- A `prompt` (the question)
- An `expected` answer
- A `type` (math, code, factual, reasoning)
- A `scoring_method` (exact, contains, or llm_judge)

### Add Model Support
Obolus auto-discovers models via Ollama. To test a new model:
```bash
ollama pull <model-name>
make bench
```

### Improve the Fitness Scorer
The scoring engine lives in `src/benchmark/fitness_scorer.py`. The z-score formula is:
```
z = (Quality × Efficiency) × (1 − Variance)
```

### Report Bugs
Open an issue with:
1. Your hardware (CPU, GPU, RAM)
2. Ollama version and model used
3. The command you ran
4. Expected vs actual output

## Code Style
- Python 3.10+
- Run `ruff check .` before submitting
- Keep modules small and focused

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
