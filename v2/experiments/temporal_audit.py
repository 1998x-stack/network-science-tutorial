"""One leak-safe temporal protocol reused by chapters 16/20/21/22/26/28.

Only uses the synthetic events in capstone_28; no internet, hidden labels or
machine-learning training. Execute:
    cd v2 && python -m experiments.temporal_audit

Interpret all evaluation numbers as toy candidate-pool arithmetic, not a
real-world model score. Node universe remains fixed at A,B,C,D,E.
"""
from __future__ import annotations

from collections import defaultdict
import json
import math
from typing import Iterable

from .capstone_28 import CANDIDATES, EVENTS, NODES, report as capstone_report

TRAIN_END = 2
VALIDATION_END = 3
TEST_TIME = 5


def undirected(u: str, v: str) -> tuple[str, str]:
    if not isinstance(u, str) or not isinstance(v, str) or u == v:
        raise ValueError("undirected simple edge requires distinct IDs")
    return tuple(sorted((u, v)))


def validate_events(events=EVENTS, nodes=NODES):
    universe = set(nodes)
    if len(universe) != len(nodes):
        raise ValueError("node IDs must be unique")
    previous = -1
    for event in events:
        if len(event) != 3:
            raise ValueError("expected u,v,t event")
        u, v, t = event
        if u not in universe or v not in universe:
            raise ValueError("event includes unknown node")
        undirected(u, v)
        if type(t) is not int or t <= 0 or t < previous:
            raise ValueError("event timestamps must be positive, integer and ordered")
        previous = t
    return True


def snapshot(cutoff: int, events=EVENTS, nodes=NODES):
    validate_events(events, nodes)
    if type(cutoff) is not int or cutoff < 0:
        raise ValueError("nonnegative integer cutoff required")
    edges = {undirected(u, v) for u, v, t in events if t <= cutoff}
    return frozenset(edges)


def adjacency(edges: Iterable[tuple[str, str]], nodes=NODES):
    neighbors = {node: set() for node in nodes}
    for u, v in edges:
        if u == v or u not in neighbors or v not in neighbors:
            raise ValueError("wrong edge or node universe")
        neighbors[u].add(v)
        neighbors[v].add(u)
    return neighbors


def common_neighbors(u: str, v: str, edges):
    neighbors = adjacency(edges)
    if u == v or u not in neighbors or v not in neighbors:
        raise ValueError("invalid candidate")
    if undirected(u, v) in edges:
        raise ValueError("candidate is already an observed edge")
    return len(neighbors[u] & neighbors[v])


def probability_next_step(u: str, v: str, edges):
    neighbors = adjacency(edges)
    if u not in neighbors or v not in neighbors:
        raise ValueError("unknown node")
    degree = len(neighbors[u])
    return (1.0 / degree) if degree and v in neighbors[u] else 0.0


def gcn_normalized_edge(u: str, v: str, edges, add_self_loops: bool):
    neighbors = adjacency(edges)
    if u not in neighbors or v not in neighbors:
        raise ValueError("unknown node")
    if u != v and v not in neighbors[u]:
        return 0.0
    du = len(neighbors[u]) + int(add_self_loops)
    dv = len(neighbors[v]) + int(add_self_loops)
    if du == 0 or dv == 0:
        return 0.0
    if u == v and not add_self_loops:
        return 0.0
    return 1.0 / math.sqrt(du * dv)


def lightgcn_example(future_edge: bool):
    # U1-X, U1-Y, U2-Y, then hypothetical future U2-X
    edges = {("U1", "X"), ("U1", "Y"), ("U2", "Y")}
    if future_edge:
        edges.add(("U2", "X"))
    neighbors = adjacency(edges, ("U1", "U2", "X", "Y"))
    return {
        "future_user_item_in_training": future_edge,
        "U1_to_X_weight": 1 / math.sqrt(len(neighbors["U1"]) * len(neighbors["X"])),
        "U2_to_X_weight": (1 / math.sqrt(len(neighbors["U2"]) * len(neighbors["X"])))
            if "X" in neighbors["U2"] else 0.0,
    }


def earliest_arrivals(contacts, source="A", start=0, nodes=("A", "B", "C", "D")):
    """Strictly increasing, instantaneous, undirected contacts.

    The arrival vector is frozen during each equal-timestamp batch; one may not
    chain two contacts with the same time as an instantaneous path.
    """
    nodes = tuple(nodes)
    if source not in nodes:
        raise ValueError("source unknown")
    if type(start) is not int:
        raise ValueError("integer start required")
    times = defaultdict(list)
    for u, v, t in contacts:
        if u not in nodes or v not in nodes or u == v:
            raise ValueError("contact invalid")
        if type(t) is not int:
            raise ValueError("integer timestamp required")
        times[t].append((u, v))
    arrivals = {node: None for node in nodes}
    arrivals[source] = start
    for t in sorted(times):
        frozen = dict(arrivals)
        pending = {}
        for u, v in times[t]:
            if frozen[u] is not None and frozen[u] < t:
                if frozen[v] is None or t < frozen[v]:
                    pending[v] = t
            if frozen[v] is not None and frozen[v] < t:
                if frozen[u] is None or t < frozen[u]:
                    pending[u] = t
        for node, arrival in pending.items():
            if arrivals[node] is None or arrival < arrivals[node]:
                arrivals[node] = arrival
    return arrivals


def audit_report():
    past = snapshot(TRAIN_END)
    available = snapshot(VALIDATION_END)
    full = snapshot(TEST_TIME)  # ONLY for deliberately contaminated counterexample
    future = full - available
    validation = available - past
    if future != {("B", "D")}:
        raise AssertionError("unexpected future label in toy data")
    if validation != {("D", "E")}:
        raise AssertionError("unexpected validation event")
    if not available.isdisjoint(future):
        raise AssertionError("test edge contaminated the legal graph")
    clean = adjacency(available)
    contam = adjacency(full)
    eligible = [undirected(*pair) for pair in CANDIDATES
                if undirected(*pair) not in available]
    scores = {f"{u}-{v}":common_neighbors(u, v, available) for u, v in eligible}
    # The future B-D edge illegitimately makes B-E appear more plausible and
    # turns B-D itself into an already-seen edge.
    contaminated_be = len(contam["B"] & contam["E"])
    b_to_d = probability_next_step("B", "D", available)
    b_to_d_leak = probability_next_step("B", "D", full)
    clean_lightgcn = lightgcn_example(False)
    leak_lightgcn = lightgcn_example(True)
    temporal_ordered = earliest_arrivals([
        ("A", "B", 1), ("B", "C", 2), ("C", "D", 3)
    ])
    temporal_reordered = earliest_arrivals([
        ("A", "B", 3), ("B", "C", 1), ("C", "D", 2)
    ])
    simultaneous = earliest_arrivals([
        ("A", "B", 1), ("B", "C", 1), ("C", "D", 2)
    ])
    return {
        "schema_version": "1.0.0",
        "data_kind": "synthetic_without_real_world_performance_claims",
        "node_universe": list(NODES),
        "train_end_inclusive": TRAIN_END,
        "validation_end_inclusive": VALIDATION_END,
        "test_time": TEST_TIME,
        "training_edges": sorted(map(list, past)),
        "validation_new_edges": sorted(map(list, validation)),
        "test_new_edges": sorted(map(list, future)),
        "clean_graph_edges_before_test": len(available),
        "clean_candidate_scores": scores,
        "clean_restricted_precision_at_1": capstone_report(3)["precision_at_1_restricted_pool"],
        "clean_random_walk_probability_B_to_D": b_to_d,
        "illegal_future_edge_walk_probability_B_to_D": b_to_d_leak,
        "clean_GCN_edge_B_D_with_self_loops": gcn_normalized_edge("B", "D", available, True),
        "illegal_GCN_edge_B_D_with_self_loops": gcn_normalized_edge("B", "D", full, True),
        "illegal_training_B_D_becomes_observed": undirected("B", "D") in full,
        "clean_common_neighbors_B_E": len(clean["B"] & clean["E"]),
        "illegal_common_neighbors_B_E": contaminated_be,
        "clean_LightGCN": clean_lightgcn,
        "illegal_LightGCN": leak_lightgcn,
        "temporal_path_ordered": temporal_ordered,
        "temporal_path_reordered": temporal_reordered,
        "temporal_path_simultaneous": simultaneous,
        "limitations": [
            "only six timestamped synthetic events, no real-world generalization",
            "future edges are used only to demonstrate why leaking is invalid",
            "unobserved pairs are neither permanent nor confirmed negatives",
            "GCN / LightGCN rows show operator coefficients, not trained models",
            "validation graph may be updated before testing only if the protocol allows"
        ],
    }


def main():
    print(json.dumps(audit_report(), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
