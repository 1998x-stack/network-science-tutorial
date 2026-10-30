"""One renderer-independent artifact contract for reproducible lessons."""
from __future__ import annotations

from datetime import datetime, timezone
from .core import Graph
from .metrics import summarize

SCHEMA_VERSION = "1.0.0"


def build_artifact(g: Graph, *, model: str, params: dict[str, int | float], seed: int) -> dict:
    g.validate()
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment": {
            "id": "structure-generation",
            "model": model,
            "params": dict(sorted(params.items())),
            "seed": seed,
        },
        "graph": {
            "directed": False,
            "nodes": [{"id": str(u), "degree": len(g.adjacency[u])} for u in sorted(g.adjacency)],
            "edges": [{"source": str(u), "target": str(v)} for u, v in g.edges()],
        },
        "metrics": summarize(g),
    }
