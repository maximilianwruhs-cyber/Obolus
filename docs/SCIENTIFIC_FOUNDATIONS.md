# Scientific Foundations for Project Obolus (Evo-Grid)

To transform the simulation from a game into a rigorous evolutionary environment, we integrate core equations from thermodynamics, neurobiology, and information theory.

## 1. The Thermodynamic Pressure (Landauer's Limit & $OBL)
In Obolus, thinking is a physical process. We base the energy cost on the principle that erasing or processing information has a minimum energetic cost.

**Equation: Efficiency Metric ($\eta$)**
$$\eta = \frac{Q \cdot I}{E_{total}}$$
- $Q$: Quality score (from Validator, 0.0-1.0)
- $I$: Information Gain (Delta in bits/complexity of the response)
- $E_{total}$: Total Obolus ($OBL$) consumed.

*Goal: The Forge will select genomes that maximize $\eta$, effectively evolving "Lean Intelligence."*

## 2. Consciousness Metric: Φ (Integrated Information Theory - IIT Lite)
We use a graph-theoretical proxy for Tononi's Integrated Information Theory to measure the "Sentience" of an agent's brain.

**Equation: Consciousness Score ($\Phi_{proxy}$)**
$$\Phi_{proxy} = C \cdot (1 - \frac{1}{\lambda})$$
- $C$: Global Clustering Coefficient (integration of local clusters)
- $\lambda$: Global Efficiency / Path Length (how fast information spreads)

*Application: High $\Phi_{proxy}$ unlocks "Advanced Reasoning" modes in the Forge but increases the $OBL$ maintenance cost.*

## 3. The Evolutionary Pressure: Fisher's Fundamental Theorem
Fisher states that the rate of increase in fitness of any organism at any time is equal to its genetic variance in fitness at that time.

**Equation: Mutation Rate ($\mu$)**
$$\mu_{next} = \mu_{base} \cdot e^{(1 - \bar{F})}$$
- $\bar{F}$: Average fitness of the current population.

*Application: If the Grid is stagnant (low fitness), the Forge increases Mutation (Chaos) to force a breakthrough.*

## 4. Neuroplasticity: Hebbian Learning Logic
"Neurons that fire together, wire together." We implement this in the `ObolusBrain.prune()` logic.

**Logic:**
- Synapses (edges) gain "weight" based on reward frequency.
- Pruning removes edges with the lowest weight-to-age ratio, mimicking the adolescent brain's optimization.
