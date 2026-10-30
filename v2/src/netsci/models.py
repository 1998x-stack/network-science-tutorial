"""Reference ER / WS / BA generators. Determinism and graph simplicity are guaranteed."""
from __future__ import annotations

import random
from .core import Graph


def erdos_renyi(n: int, p: float, seed: int = 42) -> Graph:
    if not 0 <= p <= 1:
        raise ValueError("p must be between 0 and 1")
    g = Graph.with_nodes(n)
    rng = random.Random(seed)
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                g.add_edge(u, v)
    return g


def watts_strogatz(n: int, k: int, p: float, seed: int = 42) -> Graph:
    if n < 3 or not (2 <= k < n) or k % 2:
        raise ValueError("WS requires n >= 3 and even k with 2 <= k < n")
    if not 0 <= p <= 1:
        raise ValueError("p must be between 0 and 1")
    rng = random.Random(seed)
    g = Graph.with_nodes(n)
    original = [(u, (u + j) % n) for u in range(n) for j in range(1, k // 2 + 1)]
    for u, v in original:
        g.add_edge(u, v)
    for u, v in original:
        if rng.random() < p:
            candidates = [w for w in range(n) if w != u and w not in g.adjacency[u]]
            if candidates:
                w = rng.choice(candidates)
                g.remove_edge(u, v)
                g.add_edge(u, w)
    return g


def barabasi_albert(n: int, m: int, seed: int = 42) -> Graph:
    if m < 1 or n <= m:
        raise ValueError("BA requires n > m >= 1")
    rng = random.Random(seed)
    g = Graph.with_nodes(n)
    # Star with m+1 nodes: grows naturally and has strictly positive degrees.
    for v in range(1, m + 1):
        g.add_edge(0, v)
    for new in range(m + 1, n):
        targets: set[int] = set()
        # Each target is selected without replacement, weighted by degree.
        while len(targets) < m:
            options = [v for v in range(new) if v not in targets]
            weights = [len(g.adjacency[v]) for v in options]
            target = rng.choices(options, weights=weights, k=1)[0]
            targets.add(target)
        for target in sorted(targets):
            g.add_edge(new, target)
    return g
