import unittest
from netsci.core import Graph
from netsci.models import erdos_renyi, watts_strogatz, barabasi_albert
from netsci.metrics import summarize
from netsci.experiment import build_artifact


class CoreTests(unittest.TestCase):
    def test_graph_edges_and_components(self):
        g = Graph.with_nodes(4)
        g.add_edge(0, 1)
        self.assertEqual(g.edges(), [(0, 1)])
        self.assertEqual([len(c) for c in g.components()], [2, 1, 1])
        self.assertEqual(summarize(g)["largest_component_fraction"], .5)
        with self.assertRaises(ValueError):
            g.add_edge(2, 2)

    def test_er_extremes(self):
        self.assertEqual(erdos_renyi(10, 0).m, 0)
        self.assertEqual(erdos_renyi(10, 1).m, 45)

    def test_models_seed_and_invariants(self):
        for maker, args in ((erdos_renyi, (35, .15)), (watts_strogatz, (40, 4, .3)), (barabasi_albert, (40, 3))):
            g1, g2 = maker(*args, seed=19), maker(*args, seed=19)
            self.assertEqual(g1.edges(), g2.edges())
            g1.validate()
        self.assertEqual(watts_strogatz(40, 4, .5).m, 80)
        self.assertEqual(barabasi_albert(40, 3).m, 3 * (40 - 3))

    def test_triangle_metrics(self):
        g = Graph.with_nodes(3)
        for u, v in ((0, 1), (1, 2), (0, 2)):
            g.add_edge(u, v)
        metrics = summarize(g)
        self.assertAlmostEqual(metrics["global_transitivity"], 1.)
        self.assertAlmostEqual(metrics["mean_local_clustering"], 1.)
        self.assertAlmostEqual(metrics["average_shortest_path_lcc"], 1.)

    def test_output_contract(self):
        g = erdos_renyi(9, .2, seed=42)
        result = build_artifact(g, model="er", params={"p": .2, "n": 9}, seed=42)
        self.assertEqual(result["schema_version"], "1.0.0")
        self.assertEqual(len(result["graph"]["edges"]), result["metrics"]["edges"])
        self.assertEqual(len(result["graph"]["nodes"]), 9)

    def test_invalid_models(self):
        for fun, args in ((erdos_renyi, (10, 1.2)), (watts_strogatz, (10, 3, .2)), (barabasi_albert, (3, 3))):
            with self.assertRaises(ValueError):
                fun(*args)


if __name__ == "__main__":
    unittest.main()
