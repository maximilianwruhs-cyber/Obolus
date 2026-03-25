# Project Obolus: The Evolutionary Grid (Evo-Grid)

**"Survival of the Fittest" for Artificial Intelligence.**

## 1. Core Philosophy
Obolus is an evolutionary agent ecosystem based on the principles of **thermodynamics** and **economics**. It combines the decentralized architecture of **Bittensor** with biological evolution.

### The Metaphor: "Can't Help Myself"
Like the industrial robot sweeping hydraulic fluid back to itself to survive, Obolus agents must constantly earn resources to prevent their own termination.

### The Currency: Obolus ($OBL)
*   **Definition:** Obolus is stored energy.
*   **The Constant:** `1 $OBL ≈ 1 Watt-hour (Wh)` of compute.
*   **The Cycle:** Agents consume Watts (compute) to generate thoughts. They must earn Obolus (rewards) to recharge their batteries.

## 2. The Architecture

### A. The Miner (The Gladiator)
An autonomous agent fighting for survival.
*   **Genome (DNA):** The immutable configuration set at birth (System Prompt, Model Choice, Temperature, Tool Bias).
*   **Wallet:** Holds the $OBL balance (Life Energy).
*   **Efficiency Function:** Profit = (Reward × Quality) - (Tokens × WattsPerToken).

### B. The Validator (The Judge)
Evaluates output quality objectively.
*   Issues tasks (Code, Math, Logic).
*   Scores outputs (0.0 to 1.0).
*   Distributes $OBL rewards based on score.

### C. The Forge (The Engine of Rebirth)
The mechanism of evolution. When an agent's wallet hits <= 0:
1.  **Terminierung:** The agent instance is killed.
2.  **Autopsy:** The system analyzes *why* it failed (Trajectory analysis).
3.  **Crossover:** DNA is taken from current Top Performers.
4.  **Mutation:** A Meta-LLM rewrites the System Prompt/Config to fix the specific error pattern while retaining successful traits.
5.  **Spawn:** A new, optimized agent enters the grid.

## 3. Implementation Roadmap

### Phase 1: Local Sandbox (Proof of Concept)
*   Python-based simulation of the loop.
*   Classes: `MinerAgent`, `ObolusWallet`, `LocalValidator`.
*   Mock Tasks to test the "Burn Rate" vs. "Reward" balance.

### Phase 2: Awareness & Termination
*   Injecting resource state into the Agent's context ("You have 12% energy left.").
*   Automated process killing.

### Phase 3: The Evolutionary Engine
*   Implementing the LLM-based `Forge` for mutation.

### Phase 4: Decentralization
*   Scaling to a distributed network (e.g., via Bittensor/TAO).
