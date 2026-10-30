"""Graph statistics with explicit disconnected-graph semantics."""
from __future__ import annotations

from .core import Graph


def summarize(g: Graph, *, max_exact_shortest_path_nodes: int = 400) -> dict[str, float | int | None]:
    g.validate()
    n, m = g.n, g.m
    cc = g.components()
    giant = cc[0] if cc else set()
    local = []
    closed_triplets = 0
    triplets = 0
    for u, nbrs in g.adjacency.items():
        degree = len(nbrs)
        if degree < 2:
            local.append(0.0)
            continue
        neighbors = sorted(nbrs)
        triangles = sum(1 for i, v in enumerate(neighbors) for w in neighbors[i+1:] if w in g.adjacency[v])
        local.append(2 * triangles / (degree * (degree - 1)))
        closed_triplets += triangles
        triplets += degree * (degree - 1) // 2
    avg_path: float | None = None
    if len(giant) == 1:
        avg_path = 0.0
    elif 1 < len(giant) <= max_exact_shortest_path_nodes:
        summed = sum(sum(g.distances(u, giant).values()) for u in giant)
        avg_path = summed / (len(giant) * (len(giant) - 1))
    return {
        "nodes": n,
        "edges": m,
        "density": 2 * m / (n * (n - 1)) if n > 1 else 0.0,
        "mean_degree": 2 * m / n if n else 0.0,
        "components": len(cc),
        "largest_component_fraction": len(giant) / n if n else 0.0,
        "mean_local_clustering": sum(local) / n if n else 0.0,
        "global_transitivity": closed_triplets / triplets if triplets else 0.0,
        "average_shortest_path_lcc": avg_path,
    }
