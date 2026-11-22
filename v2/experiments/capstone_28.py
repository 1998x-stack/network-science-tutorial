"""Deterministic synthetic temporal-link capstone. No network access or external dependencies.

Run: python3 v2/experiments/capstone_28.py
"""
from __future__ import annotations
import json
from typing import Iterable

EVENTS = (
    ("A", "B", 1), ("A", "C", 1),
    ("B", "C", 2), ("C", "D", 2),
    ("D", "E", 3), ("B", "D", 5),
)
NODES = tuple("ABCDE")
CANDIDATES = (("B", "D"), ("B", "E"))


def edge_set(cutoff: int):
    if not isinstance(cutoff, int) or cutoff < 0 or cutoff >= 5:
        raise ValueError("cutoff is an integer before test time 5")
    result = set()
    for u, v, t in EVENTS:
        if t <= cutoff:
            if u not in NODES or v not in NODES or u == v:
                raise ValueError("malformed event")
            result.add(frozenset((u, v)))
    return result


def neighbors(vertex: str, edges: Iterable[frozenset[str]]):
    if vertex not in NODES:
        raise ValueError("vertex outside node universe")
    return {next(iter(edge - {vertex})) for edge in edges if vertex in edge}


def score(u: str, v: str, edges):
    if u == v or u not in NODES or v not in NODES:
        raise ValueError("candidate needs distinct declared nodes")
    if frozenset((u, v)) in edges:
        raise ValueError("candidate already exists in training graph")
    return len(neighbors(u, edges) & neighbors(v, edges))


def report(cutoff: int = 3):
    train = edge_set(cutoff)
    future = {frozenset((u, v)) for u, v, t in EVENTS if t == 5}
    if not train.isdisjoint(future):
        raise AssertionError("future-edge leakage")
    scored = [(u, v, score(u, v, train)) for u, v in CANDIDATES]
    ranking = sorted(scored, key=lambda x: (-x[2], x[0], x[1]))
    precision_1 = float(frozenset(ranking[0][:2]) in future)
    degrees = {u: len(neighbors(u, train)) for u in NODES}
    if sum(degrees.values()) != 2 * len(train):
        raise AssertionError("undirected handshake invariant")
    return {
        "schema_version": "1.0.0",
        "dataset_kind": "synthetic_not_real_world",
        "train_cutoff_inclusive": cutoff,
        "test_time": 5,
        "nodes": list(NODES),
        "node_count": len(NODES),
        "train_edge_count": len(train),
        "degrees": degrees,
        "candidate_scores": [
            {"u": u, "v": v, "common_neighbors": s} for u, v, s in scored
        ],
        "ranked_candidates": [f"{u}-{v}" for u, v, _ in ranking],
        "precision_at_1_restricted_pool": precision_1,
        "candidate_pool_size": len(CANDIDATES),
        "observed_test_positive_count": len(future),
        "future_edges_leaked": False,
        "limitations": [
            "one positive event; two manually selected candidates",
            "unobserved future edge is not a verified permanent negative",
            "no valid generalization or deployment metric"
        ],
    }


def main():
    result = report()
    assert result["train_edge_count"] == 5
    assert result["degrees"] == {"A": 2, "B": 2, "C": 3, "D": 2, "E": 1}
    assert [x["common_neighbors"] for x in result["candidate_scores"]] == [1, 0]
    assert result["precision_at_1_restricted_pool"] == 1.0
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
