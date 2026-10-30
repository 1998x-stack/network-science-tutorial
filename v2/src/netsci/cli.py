"""Run a topology experiment and export a versioned JSON visualization artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from .experiment import build_artifact
from .utils import write_json_atomic
from .models import erdos_renyi, watts_strogatz, barabasi_albert


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate reproducible network-science experiment")
    parser.add_argument("--model", choices=("er", "ws", "ba"), required=True)
    parser.add_argument("--nodes", type=int, default=70)
    parser.add_argument("--p", type=float, default=0.1, help="ER edge probability / WS rewiring probability")
    parser.add_argument("--degree", type=int, default=4, help="WS initial even node degree")
    parser.add_argument("--attach", type=int, default=2, help="BA edges per new node")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.model == "er":
        g, params = erdos_renyi(args.nodes, args.p, args.seed), {"n": args.nodes, "p": args.p}
    elif args.model == "ws":
        g, params = watts_strogatz(args.nodes, args.degree, args.p, args.seed), {"n": args.nodes, "k": args.degree, "p": args.p}
    else:
        g, params = barabasi_albert(args.nodes, args.attach, args.seed), {"n": args.nodes, "m": args.attach}
    artifact = build_artifact(g, model=args.model, params=params, seed=args.seed)
    write_json_atomic(args.output, artifact)
    print(f"Saved {args.output} | n={g.n} m={g.m} seed={args.seed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
