"""Offline public-data topology oracle; NOT a temporal link-prediction experiment.

NetworkX bundles the Zachary Karate Club network; this script reads it from
the installed NetworkX package and never requests/downloads a remote file.

Run: cd v2 && python -m experiments.public_karate_audit
Install: python -m pip install 'networkx>=3.3,<4'
"""
from __future__ import annotations
import json


def public_report():
    import networkx as nx

    graph = nx.karate_club_graph()
    nodes = graph.number_of_nodes()
    edges = graph.number_of_edges()
    degree = dict(graph.degree())
    triangles = sum(nx.triangles(graph).values()) // 3
    components = nx.number_connected_components(graph)
    if (nodes, edges, triangles, components) != (34, 78, 45, 1):
        raise AssertionError("upstream public dataset changed; reevaluate the protocol")
    if sum(degree.values()) != 2 * edges:
        raise AssertionError("handshake invariant failed")
    # An independent implementation of triangle count from adjacency sets.
    adj = {n: set(graph.neighbors(n)) for n in graph.nodes}
    manual_triangles = sum(
        1 for a in graph.nodes for b in adj[a] for c in (adj[a] & adj[b])
        if a < b < c
    )
    if manual_triangles != triangles:
        raise AssertionError("triangle oracle mismatch")
    return {
        "schema_version":"1.0.0",
        "dataset_kind":"NetworkX bundled publicly documented historical Karate Club graph",
        "source":"https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.karate_club_graph.html",
        "networkx_version":nx.__version__,
        "nodes":nodes,
        "edges":edges,
        "degree_sum":sum(degree.values()),
        "connected_components":components,
        "triangles_unweighted":triangles,
        "triangles_independent_oracle":manual_triangles,
        "density_unweighted_simple":nx.density(graph),
        "historical_groups":sorted(set(nx.get_node_attributes(graph, "club").values())),
        "limitations":[
            "static historical network, no time-stamped event sequence",
            "triangle counts ignore edge weights and are not causal claims",
            "not trained/tested on future links, no performance benchmark"
        ]
    }


def main():
    print(json.dumps(public_report(),ensure_ascii=False,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
