"""
Obolus v4 Arena — Multi-Model Evolutionary Competition
Auto-discovers all local Ollama models and competes them against each other.
The Forge can mutate both the system prompt AND the model choice.
"""
import random
import json
import time
from datetime import datetime
from pathlib import Path

from ..core.agent import MinerAgent
from ..core.genome import Genome
from .forge import Forge
from .history import HistoryManager

import config
from src.benchmark.task_suite import get_random_tasks, get_suite
from src.benchmark.evaluator import score_task
from src.benchmark.energy_meter import EnergyMeter
from src.benchmark.fitness_scorer import (
    TrialResult, ScoringConfig, FitnessResult, evaluate_mutation
)
from src.benchmark.leaderboard import MutationLeaderboard
from src.benchmark.model_discovery import discover_models, print_discovered_models
from src.benchmark.awattar import get_current_price_c_kwh


# Default scoring config
DEFAULT_SCORING_CONFIG = ScoringConfig(
    baseline_time_ms=200.0,
    baseline_energy_joules=50.0,
    min_quality=0.5,
    min_efficiency=0.8,
    min_z_score=0.3,
)

# Default system prompts for diversity
DEFAULT_PROMPTS = [
    "Be concise and precise. Answer with minimal tokens.",
    "Think step by step. Show your reasoning clearly.",
    "You are a logic engine. Prioritize correctness over verbosity.",
    "Answer directly. No filler words. Maximum efficiency.",
    "Be thorough but brief. Quality over quantity.",
]


def _run_trials(agent, tasks, meter) -> tuple:
    """Run multiple tasks against an agent, collecting TrialResults and total energy."""
    trials = []
    total_joules = 0.0

    for task in tasks:
        meter.start()
        start_ms = time.monotonic() * 1000

        result = agent.think(task["prompt"])
        energy = meter.stop()

        elapsed_ms = (time.monotonic() * 1000) - start_ms

        if result is None:
            trials.append(TrialResult(passed=False, execution_time_ms=elapsed_ms, output_similarity=0.0))
            total_joules += energy["joules"]
            continue

        output = result["output"]
        score = score_task(task, output)

        trials.append(TrialResult(
            passed=score >= 0.5,
            execution_time_ms=elapsed_ms,
            output_similarity=score,
        ))
        total_joules += energy["joules"]

    return trials, total_joules


def _build_agents_from_models(models, prompts=None) -> list:
    """Create one agent per model, assigning diverse system prompts."""
    prompts = prompts or DEFAULT_PROMPTS
    agents = []

    for i, model_info in enumerate(models):
        prompt = prompts[i % len(prompts)]
        genome = Genome(
            system_prompt=prompt,
            model=model_info.name,
            temperature=0.3,
        )
        agent_id = f"{model_info.name.replace(':', '_').replace('.', '_')}"
        agent = MinerAgent(agent_id, genome, initial_balance=50.0)
        agents.append(agent)

    return agents


def run_arena(epochs: int = 20, suite: str = "full", verbose: bool = True,
              convergence_patience: int = 5, convergence_threshold: float = 0.02,
              trials_per_epoch: int = 3, scoring_config: ScoringConfig = None,
              auto_models: bool = True, models: list = None):
    """
    Run the evolutionary arena with multi-model competition.

    If auto_models=True (default), auto-discovers all Ollama models.
    Otherwise falls back to the configured default model.
    """
    scoring = scoring_config or DEFAULT_SCORING_CONFIG

    # --- Model Discovery ---
    if auto_models and models is None:
        discovered = discover_models()
        if not discovered:
            print("  [!] No models discovered. Falling back to default.")
            discovered = []
        elif verbose:
            print_discovered_models(discovered)
    else:
        discovered = []

    # --- Build Agents ---
    if discovered and len(discovered) >= 1:
        agents = _build_agents_from_models(discovered)
        # If only 1 model found, add prompt variants
        if len(agents) == 1:
            model_name = discovered[0].name
            for prompt in DEFAULT_PROMPTS[1:3]:
                genome = Genome(system_prompt=prompt, model=model_name, temperature=0.5)
                agent_id = f"{model_name.replace(':', '_')}_v{len(agents)}"
                agents.append(MinerAgent(agent_id, genome, initial_balance=50.0))
    else:
        # Fallback: hardcoded agents with default model
        agents = [
            MinerAgent("Alpha", Genome("Be concise and precise. Answer with minimal tokens.", config.DEFAULT_MODEL, 0.1), 50.0),
            MinerAgent("Beta", Genome("Think step by step. Show your reasoning clearly.", config.DEFAULT_MODEL, 0.7), 50.0),
            MinerAgent("Gamma", Genome("You are a logic engine. Prioritize correctness over verbosity.", config.DEFAULT_MODEL, 0.4), 50.0),
        ]

    # --- Live Electricity Price ---
    live_price = get_current_price_c_kwh()
    price_c_kwh = live_price if live_price is not None else 25.0
    price_is_live = live_price is not None

    # Economic pressure: expensive electricity → stricter scoring
    # Cheap/negative → bonus headroom, expensive → tighter thresholds
    econ_factor = max(0.5, min(2.0, price_c_kwh / 15.0))  # normalize around 15¢

    if verbose:
        price_label = f"LIVE {price_c_kwh:.1f} ¢/kWh" if price_is_live else f"est. {price_c_kwh:.1f} ¢/kWh"
        if price_is_live:
            if price_c_kwh < 0:
                icon = "🎉"
                context = "NEGATIVE — grid pays you!"
            elif price_c_kwh < 5:
                icon = "🟢"
                context = "Very cheap — full power"
            elif price_c_kwh < 15:
                icon = "🟡"
                context = "Normal"
            elif price_c_kwh < 25:
                icon = "🟠"
                context = "Above average"
            else:
                icon = "🔴"
                context = "Expensive — efficiency critical"
        else:
            icon = "📊"
            context = "API unavailable, using estimate"

        print(f"\n--- OBOLUS EVO-GRID ARENA v4 (Multi-Model) ---")
        print(f"    {icon} Electricity: {price_label} ({context})")
        print(f"    Economic pressure: {econ_factor:.2f}x")
        print(f"    Agents: {len(agents)} ({', '.join(a.genome.model for a in agents)})")
        print(f"    Suite: {suite} | Trials/epoch: {trials_per_epoch}")
        print(f"    Convergence: patience={convergence_patience}, threshold={convergence_threshold:.0%}")
        print(f"    Scoring: min_Q={scoring.min_quality}, min_E={scoring.min_efficiency}, min_z={scoring.min_z_score}")

    available_models = [m.name for m in discovered] if discovered else [config.DEFAULT_MODEL]
    forge = Forge(available_models=available_models)
    history = HistoryManager()
    meter = EnergyMeter()
    leaderboard = MutationLeaderboard()

    gen_tracker = []
    tasks_pool = get_suite(suite)
    best_avg_z = 0.0
    stale_count = 0

    for epoch in range(1, epochs + 1):
        if verbose:
            print(f"\n[Epoch {epoch}]")

        alive_agents = [a for a in agents if a.wallet.is_alive()]
        if not alive_agents:
            print("All agents terminated. Grid empty.")
            break

        epoch_tasks = random.sample(tasks_pool, min(trials_per_epoch, len(tasks_pool)))
        if verbose:
            types = [t["type"] for t in epoch_tasks]
            print(f"  Tasks: {', '.join(types)}")

        epoch_scores = []

        for i in range(len(agents)):
            agent = agents[i]

            if not agent.wallet.is_alive():
                new_agent = forge.rebirth(agent, alive_agents, epoch)
                if verbose:
                    print(f"  [FORGE] Rebirth: {agent.agent_id} -> {new_agent.agent_id} "
                          f"(model: {new_agent.genome.model})")
                agents[i] = new_agent
                agent = agents[i]

            trials, total_joules = _run_trials(agent, epoch_tasks, meter)
            fitness = evaluate_mutation(trials, total_joules, scoring)

            leaderboard.record(
                agent_id=agent.agent_id,
                genome_summary=agent.genome.system_prompt,
                fitness_result=fitness,
                generation=agent.genome.generation,
                model=agent.genome.model,
            )

            # Scale reward by fitness AND electricity cost pressure
            reward = fitness.z_score * 15 / econ_factor
            agent.wallet.deposit_reward(reward)

            agent.brain.grow(reward)
            if epoch % 3 == 0:
                agent.brain.prune()

            metrics = agent.brain.get_metrics()
            epoch_scores.append({
                "agent": agent.agent_id,
                "model": agent.genome.model,
                "z_score": fitness.z_score,
                "quality": fitness.quality,
                "efficiency": fitness.efficiency,
                "variance": fitness.variance_penalty,
                "approved": fitness.approved,
                "reason": fitness.reason,
                "gen": agent.genome.generation,
            })

            if verbose:
                ok = "✅" if fitness.approved else "❌"
                icon = "🟢" if fitness.z_score > 0.5 else "🟡" if fitness.z_score > 0.2 else "🔴"
                reason_str = f" ({fitness.reason})" if fitness.reason else ""
                model_short = agent.genome.model.split(":")[0][-10:]
                print(f"  {icon} {agent.agent_id[:20]:<20} [{model_short:>10}] "
                      f"z={fitness.z_score:<8.4f} Q={fitness.quality:.3f} E={fitness.efficiency:.3f} "
                      f"{ok}{reason_str} | {agent.wallet}")

            if not fitness.approved and not agent.wallet.is_alive():
                agent.death_reason = f"Fitness rejected ({fitness.reason}) in Epoch {epoch}"
                if verbose:
                    print(f"  [!!!] AGENT {agent.agent_id} REJECTED & DEPLETED.")

        avg_z = sum(s["z_score"] for s in epoch_scores) / max(1, len(epoch_scores))
        avg_q = sum(s["quality"] for s in epoch_scores) / max(1, len(epoch_scores))
        gen_tracker.append({
            "epoch": epoch,
            "avg_z": round(avg_z, 4),
            "avg_quality": round(avg_q, 4),
            "agents": epoch_scores,
        })

        if avg_z > best_avg_z + convergence_threshold:
            best_avg_z = avg_z
            stale_count = 0
        else:
            stale_count += 1

        if stale_count >= convergence_patience and epoch >= convergence_patience:
            if verbose:
                print(f"\n  [CONVERGED] No z-score improvement for {convergence_patience} epochs "
                      f"(best: {best_avg_z:.4f}). Stopping early at epoch {epoch}.")
            break

    # --- Final Summary ---
    if verbose:
        print(f"\n{'='*65}")
        print(f"  ARENA FINAL STATE — Multi-Model Results")
        print(f"{'='*65}")

        # Per-model summary
        model_stats = {}
        for entry in leaderboard.entries:
            model = entry.get("model", "unknown")
            if model not in model_stats:
                model_stats[model] = {"z_scores": [], "qualities": [], "approved": 0, "total": 0}
            model_stats[model]["z_scores"].append(entry["z_score"])
            model_stats[model]["qualities"].append(entry["quality"])
            model_stats[model]["total"] += 1
            if entry.get("approved"):
                model_stats[model]["approved"] += 1

        print(f"\n  {'Model':<30} {'Avg z':>8} {'Avg Q':>7} {'Approve%':>9} {'Runs':>5}")
        print(f"  {'─'*30} {'─'*8} {'─'*7} {'─'*9} {'─'*5}")
        for model, stats in sorted(model_stats.items(),
                                    key=lambda x: sum(x[1]["z_scores"])/len(x[1]["z_scores"]),
                                    reverse=True):
            avg_z = sum(stats["z_scores"]) / len(stats["z_scores"])
            avg_q = sum(stats["qualities"]) / len(stats["qualities"])
            approve_pct = stats["approved"] / max(1, stats["total"]) * 100
            print(f"  {model:<30} {avg_z:>8.4f} {avg_q:>6.1%} {approve_pct:>8.0f}% {stats['total']:>5}")

        print()
        for agent in agents:
            print(f"  {agent}")

        if len(gen_tracker) >= 3:
            first3 = sum(g["avg_z"] for g in gen_tracker[:3]) / 3
            last3 = sum(g["avg_z"] for g in gen_tracker[-3:]) / 3
            delta = last3 - first3
            trend = "📈" if delta > 0.05 else "📉" if delta < -0.05 else "➡️"
            print(f"\n  [EVOLUTION] First 3 avg z: {first3:.4f} → Last 3 avg z: {last3:.4f} {trend} ({delta:+.4f})")

        leaderboard.print_leaderboard(5)

    history.save(forge.mutation_history)
    _save_gen_tracker(gen_tracker)

    return gen_tracker


def _save_gen_tracker(tracker: list):
    """Save generational tracking data."""
    path = config.DATA_DIR / "evolution_curve.json"
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(tracker, f, indent=2)
    print(f"  [TRACKER] Evolution curve saved → {path}")


if __name__ == "__main__":
    run_arena()
