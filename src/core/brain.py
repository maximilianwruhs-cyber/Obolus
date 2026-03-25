import networkx as nx
import random


class ObolusBrain:
    """
    IIT-inspired neural graph that FUNCTIONALLY influences agent behavior.
    Higher Φ (integrated information proxy) → more capable agent.
    """

    # Φ thresholds for capability unlocks
    PHI_TIERS = {
        "basic":     0.0,     # always available
        "extended":  0.05,    # unlock extended token budget
        "reasoning": 0.10,    # unlock chain-of-thought reasoning prefix
        "adaptive":  0.15,    # unlock temperature self-tuning
        "creative":  0.20,    # unlock creative exploration mode
    }

    def __init__(self, initial_neurons=10):
        self.G = nx.Graph()
        self.G.add_nodes_from(range(initial_neurons))
        for node in range(initial_neurons):
            targets = random.sample(list(self.G.nodes()), random.randint(1, 3))
            for t in targets:
                if t != node:
                    self.G.add_edge(node, t)
        self._cached_metrics = None
        self._dirty = True

    def grow(self, reward_points):
        """Adds neurons based on reward. More reward → more neurons → potentially higher Φ."""
        new_nodes_count = int(reward_points // 2)
        for _ in range(new_nodes_count):
            new_id = self.G.number_of_nodes()
            self.G.add_node(new_id)
            # Preferential attachment: connect to high-degree nodes (builds integration)
            nodes = list(self.G.nodes())
            if len(nodes) > 1:
                degrees = dict(self.G.degree())
                weights = [degrees.get(n, 1) + 1 for n in nodes if n != new_id]
                targets = random.choices(
                    [n for n in nodes if n != new_id],
                    weights=weights,
                    k=min(3, len(nodes) - 1),
                )
                for conn in set(targets):
                    self.G.add_edge(new_id, conn)
        self._dirty = True
        return new_nodes_count

    def prune(self):
        """Remove weak edges. Strategic pruning can INCREASE Φ by cutting redundancy."""
        if self.G.number_of_edges() < 5:
            return 0
        edges = list(self.G.edges())
        to_remove = random.sample(edges, int(len(edges) * 0.1))
        self.G.remove_edges_from(to_remove)
        self._dirty = True
        return len(to_remove)

    def get_metrics(self):
        """Returns consciousness metrics (cached until graph changes)."""
        if self._dirty or self._cached_metrics is None:
            try:
                clustering = nx.average_clustering(self.G)
                try:
                    efficiency = nx.global_efficiency(self.G)
                except Exception:
                    efficiency = 0.001
                phi_proxy = clustering * efficiency
            except Exception:
                clustering = 0.0
                efficiency = 0.0
                phi_proxy = 0.0

            self._cached_metrics = {
                "neurons": self.G.number_of_nodes(),
                "synapses": self.G.number_of_edges(),
                "clustering_C": round(clustering, 4),
                "efficiency_L": round(efficiency, 4),
                "phi_proxy": round(phi_proxy, 6),
            }
            self._dirty = False
        return self._cached_metrics

    # ─── Functional Φ: brain influences agent capabilities ─────────────

    @property
    def phi(self) -> float:
        """Current Φ proxy value."""
        return self.get_metrics()["phi_proxy"]

    def get_token_budget(self) -> int:
        """Higher Φ → more tokens allowed per inference."""
        phi = self.phi
        if phi >= self.PHI_TIERS["creative"]:
            return 512   # full creative budget
        elif phi >= self.PHI_TIERS["reasoning"]:
            return 256   # reasoning budget
        elif phi >= self.PHI_TIERS["extended"]:
            return 192   # extended budget
        else:
            return 128   # minimal budget (survive on less)

    def get_temperature_mod(self, base_temp: float) -> float:
        """Higher Φ → agent can self-tune temperature for the task."""
        phi = self.phi
        if phi >= self.PHI_TIERS["adaptive"]:
            # Adaptive: slightly randomize temp around base for exploration
            return max(0.05, min(1.5, base_temp + random.uniform(-0.1, 0.1)))
        return base_temp

    def get_cognitive_prefix(self) -> str:
        """Higher Φ → unlock reasoning strategies in the prompt."""
        phi = self.phi
        parts = []
        if phi >= self.PHI_TIERS["reasoning"]:
            parts.append("Think step by step before answering.")
        if phi >= self.PHI_TIERS["creative"]:
            parts.append("Consider unconventional approaches.")
        return " ".join(parts)

    def get_tier_name(self) -> str:
        """Get the current capability tier name."""
        phi = self.phi
        tier = "basic"
        for name, threshold in sorted(self.PHI_TIERS.items(), key=lambda x: x[1]):
            if phi >= threshold:
                tier = name
        return tier
