"""Small deterministic 3-model structural comparison; does not claim statistical significance."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, stdev
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from netsci.models import erdos_renyi, watts_strogatz, barabasi_albert
from netsci.metrics import summarize
from netsci.utils import write_json_atomic


def compare(n: int, degree: int, seeds: list[int]) -> dict:
    if n < 3 or degree < 2 or degree % 2 or degree >= n:
        raise ValueError("require n >=3 and even 2 <= degree < n")
    if len(seeds) != len(set(seeds)) or not seeds:
        raise ValueError("seeds must be distinct and nonempty")
    data = []
    p = degree / (n - 1)
    for seed in seeds:
        graphs = {
            "er": erdos_renyi(n, p, seed),
            "ws": watts_strogatz(n, degree, .08, seed),
            "ba": barabasi_albert(n, degree // 2, seed),
        }
        for model, graph in graphs.items():
            data.append({"model": model, "seed": seed, "metrics": summarize(graph)})
    aggregate = []
    keys = ("mean_degree", "mean_local_clustering", "average_shortest_path_lcc", "largest_component_fraction")
    for model in ("er", "ws", "ba"):
        rows = [r["metrics"] for r in data if r["model"] == model]
        summary = {}
        for key in keys:
            values = [float(r[key]) for r in rows if r[key] is not None]
            summary[key] = {"mean": mean(values) if values else None, "std": stdev(values) if len(values) >= 2 else None, "samples": len(values)}
        aggregate.append({"model": model, "summary": summary})
    return {
        "schema_version": "1.0.0",
        "experiment_id": "er-ws-ba-matched-expected-degree",
        "params": {"nodes": n, "expected_degree": degree, "ws_rewire_probability": .08, "seeds": seeds},
        "notes": ["ER degree is matched only in expectation", "BA initial graph influences finite-size results", "report summarizes samples, not causal effects or significance"],
        "runs": data,
        "summary": aggregate,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--nodes", type=int, default=80)
    p.add_argument("--degree", type=int, default=6)
    p.add_argument("--seeds", default="11,22,33,44,55")
    p.add_argument("--output", type=Path, default=Path("experiments/results/model-comparison.json"))
    args = p.parse_args()
    report = compare(args.nodes, args.degree, [int(x.strip()) for x in args.seeds.split(",")])
    write_json_atomic(args.output, report)
    print("Saved", args.output, "runs", len(report["runs"]))


if __name__ == "__main__":
    main()
