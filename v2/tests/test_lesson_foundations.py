"""Deterministic checks for the five reviewed introductory lessons."""
import json
import math
from pathlib import Path
import networkx as nx

def konigsberg_multigraph():
    graph=nx.MultiGraph()
    graph.add_edges_from([("north","island_a"),("north","island_a"),("south","island_a"),("south","island_a"),("island_a","island_b"),("north","island_b"),("south","island_b")])
    return graph

def test_lesson_01_konigsberg_has_four_odd_vertices():
    graph=konigsberg_multigraph()
    assert graph.number_of_edges()==7
    assert sorted(dict(graph.degree()).values())==[3,3,3,5]
    assert nx.is_connected(graph)
    assert not nx.has_eulerian_path(graph)
    assert not nx.has_eulerian_circuit(graph)

def test_lesson_02_graph_representations_preserve_edges():
    graph=nx.Graph([("A","B"),("A","C"),("B","C"),("C","D")])
    nodes=["A","B","C","D"]
    matrix=nx.to_numpy_array(graph,nodelist=nodes,dtype=int)
    adjacency={node:set(graph.neighbors(node)) for node in nodes}
    assert (matrix==matrix.T).all()
    assert int(matrix.sum())==2*graph.number_of_edges()
    assert sum(dict(graph.degree()).values())==2*graph.number_of_edges()
    assert adjacency["C"]=={"A","B","D"}
    tree=nx.path_graph(6)
    assert nx.is_tree(tree) and tree.number_of_edges()==tree.number_of_nodes()-1

def test_lesson_03_four_node_metric_values_are_exact():
    graph=nx.Graph([(0,1),(1,2),(2,0),(2,3)])
    assert graph.number_of_nodes()==4 and graph.number_of_edges()==4
    assert nx.density(graph)==2/3
    assert nx.clustering(graph,2)==1/3
    assert math.isclose(nx.average_clustering(graph),7/12)
    assert nx.transitivity(graph)==3/5
    assert nx.average_shortest_path_length(graph)==4/3
    disconnected=graph.copy();disconnected.add_edge(4,5)
    lcc=max(nx.connected_components(disconnected),key=len)
    assert math.isclose(nx.average_shortest_path_length(disconnected.subgraph(lcc)),4/3)

def test_lesson_04_er_expectations_and_thresholds_are_distinct():
    n,p=100,0.04
    assert math.isclose(p*n*(n-1)/2,198)
    assert math.isclose(p*(n-1),3.96)
    assert math.log(n)/n>1/n
    graph=nx.erdos_renyi_graph(1000,0.01,seed=42)
    assert graph.number_of_nodes()==1000
    assert sum(dict(graph.degree()).values())==2*graph.number_of_edges()

def test_lesson_05_ws_rewiring_shortens_paths_before_clustering_disappears():
    n,k,seed=500,6,42
    regular=nx.watts_strogatz_graph(n,k,0.0,seed=seed)
    rewired=nx.watts_strogatz_graph(n,k,0.05,seed=seed)
    expected=3*(k-2)/(4*(k-1))
    assert math.isclose(nx.average_clustering(regular),expected)
    assert nx.is_connected(regular) and nx.is_connected(rewired)
    assert nx.average_clustering(rewired)<nx.average_clustering(regular)
    assert nx.average_shortest_path_length(rewired)<nx.average_shortest_path_length(regular)
    assert regular.number_of_edges()==rewired.number_of_edges()==n*k//2

def test_reviewed_evidence_ledgers_have_locators_and_valid_statuses():
    root=Path(__file__).resolve().parents[1]/"content"/"evidence"
    allowed={"verified","derived","illustrative"}
    for number in ("01","02","03","04","05","06","07","08","09","10"):
        ledger=json.loads((root/f"{number}.json").read_text(encoding="utf-8"))
        assert ledger["chapter"]==number and ledger["review_status"]=="reviewed"
        assert ledger["claims"]
        for claim in ledger["claims"]:
            assert claim.get("source_url") and claim.get("locator")
            assert claim.get("status") in allowed

# The original checks were plain functions, which unittest discover did not collect.
# Register them as real unittest cases so CI executes every mathematical assertion.
import unittest
class FoundationChecks(unittest.TestCase):
    def test_euler(self): test_lesson_01_konigsberg_has_four_odd_vertices()
    def test_graph_representation(self): test_lesson_02_graph_representations_preserve_edges()
    def test_metrics(self): test_lesson_03_four_node_metric_values_are_exact()
    def test_er(self): test_lesson_04_er_expectations_and_thresholds_are_distinct()
    def test_ws(self): test_lesson_05_ws_rewiring_shortens_paths_before_clustering_disappears()
    def test_evidence(self): test_reviewed_evidence_ledgers_have_locators_and_valid_statuses()
