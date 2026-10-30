"""Independent numerical reference checks when NetworkX is available."""
import unittest
try:
    import networkx as nx
except ImportError:
    nx = None

from netsci.models import erdos_renyi, watts_strogatz, barabasi_albert
from netsci.metrics import summarize


@unittest.skipUnless(nx is not None, "NetworkX extra not installed")
class OracleTests(unittest.TestCase):
    def test_compare_metrics_to_networkx(self):
        for make, args in ((erdos_renyi, (65, .13)), (watts_strogatz, (64, 6, .2)), (barabasi_albert, (65, 3))):
            g = make(*args, seed=13)
            h = nx.Graph()
            h.add_nodes_from(g.adjacency)
            h.add_edges_from(g.edges())
            got = summarize(g)
            self.assertEqual(got["edges"], h.number_of_edges())
            self.assertAlmostEqual(got["density"], nx.density(h))
            self.assertAlmostEqual(got["mean_local_clustering"], nx.average_clustering(h))
            self.assertAlmostEqual(got["global_transitivity"], nx.transitivity(h))
            cc = max(nx.connected_components(h), key=len)
            self.assertAlmostEqual(got["average_shortest_path_lcc"], nx.average_shortest_path_length(h.subgraph(cc)))

    def test_isolates_and_empty_graph(self):
        g = erdos_renyi(4, 0)
        self.assertEqual(summarize(g)["components"], 4)
        self.assertEqual(summarize(g)["average_shortest_path_lcc"], 0)
        self.assertIsNone(summarize(erdos_renyi(0, 0))["average_shortest_path_lcc"])


if __name__ == "__main__":
    unittest.main()
