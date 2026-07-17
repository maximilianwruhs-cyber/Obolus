#!/usr/bin/env python3
"""
Obolus CLI — best local model per joule
Usage:
    python obulus.py bench --model qwen2.5-coder:7b --suite math
    python obulus.py recommend
    python obulus.py compare
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.benchmark.runner import run_benchmark, compare_models, save_results
from src.benchmark.task_suite import list_suites
from src.benchmark.recommender import print_recommendation


def cmd_bench(args):
    """Run benchmark against a model."""
    summary = run_benchmark(
        model=args.model,
        suite=args.suite,
        ollama_url=args.ollama_url,
        temperature=args.temperature,
        verbose=not args.quiet,
    )
    save_results(summary)


def cmd_compare(args):
    """Compare benchmark results across models."""
    compare_models()


def cmd_suites(args):
    """List available task suites."""
    print("\n  Available Benchmark Suites:")
    print(f"  {'─'*35}")
    for name, count in list_suites().items():
        print(f"    {name:<12} {count:>3} tasks")
    print()


def cmd_evolve(args):
    """Experimental evolutionary arena (not v1 product surface)."""
    print("\n  Note: evolve is experimental — prefer `bench` then `recommend`.\n")
    from src.simulation.arena import run_arena
    run_arena(
        epochs=args.epochs,
        suite=args.suite,
        convergence_patience=args.patience,
        auto_models=not args.no_auto_models,
    )


def cmd_recommend(args):
    """Show model recommendations and cost projections."""
    print_recommendation()


def main():
    parser = argparse.ArgumentParser(
        description="Obolus — which local model is best per joule on your machine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python obulus.py bench --model qwen2.5-coder:7b --suite math
  python obulus.py recommend
  python obulus.py compare
        """,
    )
    sub = parser.add_subparsers(dest="command")

    # bench
    bench = sub.add_parser("bench", help="Benchmark a model (quality + energy)")
    bench.add_argument("--model", required=True, help="Ollama model name (e.g. qwen2.5-coder:7b)")
    bench.add_argument("--suite", default="math",
                       choices=list(list_suites().keys()),
                       help="Task suite (default: math)")
    bench.add_argument("--ollama-url", default=None, help="Ollama URL (default: from .env)")
    bench.add_argument("--temperature", type=float, default=0.3)
    bench.add_argument("--quiet", action="store_true", help="Suppress per-task output")
    bench.set_defaults(func=cmd_bench)

    # compare
    cmp = sub.add_parser("compare", help="Compare benchmark results (leaderboard)")
    cmp.set_defaults(func=cmd_compare)

    # suites
    s = sub.add_parser("suites", help="List available task suites")
    s.set_defaults(func=cmd_suites)

    # evolve (experimental)
    evo = sub.add_parser("evolve", help="Experimental: evolutionary arena")
    evo.add_argument("--agents", nargs="*", default=None, help="Agent .md filenames")
    evo.add_argument("--ollama-url", default=None, help="Ollama URL")
    evo.add_argument("--suite", default="math", choices=list(list_suites().keys()),
                     help="Benchmark suite for evaluation (default: math)")
    evo.add_argument("--epochs", type=int, default=20, help="Max epochs (default: 20)")
    evo.add_argument("--patience", type=int, default=5, help="Convergence patience (default: 5)")
    evo.add_argument("--no-auto-models", action="store_true",
                     help="Disable auto-model discovery (use default model only)")
    evo.set_defaults(func=cmd_evolve)

    # recommend
    rec = sub.add_parser("recommend", help="Show model recommendations & cost projections")
    rec.set_defaults(func=cmd_recommend)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n  Quick start: python obulus.py bench --model qwen2.5-coder:7b --suite math\n")
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
