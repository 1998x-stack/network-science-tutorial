"""Second five-lesson regression tests: real unittest discovery and executable examples."""
from __future__ import annotations
import contextlib
from collections import Counter
import io
import json
import math
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import networkx as nx

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
NUMBERS=("06","07","08","09","10")

class SecondBatchOracleTests(unittest.TestCase):
    def test_06_ba_generator_and_handshake(self):
        g=nx.barabasi_albert_graph(200,2,seed=7)
        self.assertEqual(g.number_of_nodes(),200)
        self.assertEqual(g.number_of_edges(),396)
        self.assertEqual(sum(dict(g.degree()).values()),792)
        small=nx.Graph([("A","B"),("A","C"),("A","D"),("B","E"),("C","D")])
        self.assertEqual([small.degree(v) for v in "ABCDE"],[3,2,2,2,1])
        self.assertEqual(sum(dict(small.degree()).values()),10)

    def test_07_empirical_distribution_includes_isolates(self):
        g=nx.Graph()
        g.add_nodes_from(range(8))
        g.add_edges_from([(0,1),(0,2),(0,3),(0,4),(0,5),(1,2),(2,3)])
        count=Counter(dict(g.degree()).values())
        self.assertEqual(dict(sorted(count.items())),{0:2,1:2,2:2,3:1,5:1})
        degrees=list(dict(g.degree()).values())
        self.assertEqual(sum(degrees)/8,1.75)
        self.assertEqual(sum(d*d for d in degrees)/8,5.5)

    def test_08_centrality_bridge_normalization(self):
        g=self.bridge_graph()
        degree=nx.degree_centrality(g)
        between=nx.betweenness_centrality(g,normalized=True,endpoints=False)
        self.assertAlmostEqual(degree[2],0.6,places=12)
        self.assertAlmostEqual(between[2],0.6)
        self.assertAlmostEqual(between[3],0.6)
        self.assertTrue(all(abs(between[k])<1e-12 for k in (0,1,4,5)))
        eig=nx.eigenvector_centrality(g,max_iter=1000)
        self.assertEqual(set(eig),set(g))

    def test_09_pagerank_stationary_and_dangling(self):
        g=nx.DiGraph()
        g.add_nodes_from("ABCD")
        g.add_edges_from([("A","B"),("B","C"),("C","B")])
        oracle=nx.pagerank(g,alpha=.85,tol=1e-12,max_iter=1000)
        current={v:.25 for v in "ABCD"}
        for _ in range(250):
            new={v:.15/4 for v in "ABCD"}
            for v in "ABCD":
                outgoing=list(g.successors(v))
                if not outgoing: outgoing=list("ABCD")
                for w in outgoing: new[w]+=.85*current[v]/len(outgoing)
            current=new
        for node in "ABCD": self.assertAlmostEqual(current[node],oracle[node],places=9)
        self.assertAlmostEqual(sum(oracle.values()),1,places=12)
        self.assertGreater(oracle["B"],oracle["C"])
        self.assertAlmostEqual(oracle["A"],oracle["D"],places=12)

    def test_10_modularity_and_louvain(self):
        g=self.bridge_graph()
        q=nx.community.modularity(g,[{0,1,2},{3,4,5}])
        self.assertAlmostEqual(q,5/14,places=12)
        self.assertAlmostEqual(nx.community.modularity(g,[set(g)]),0,places=12)
        found=nx.community.louvain_communities(g,seed=42)
        self.assertEqual(set().union(*found),set(g))
        self.assertEqual(sum(map(len,found)),g.number_of_nodes())

    def test_06_to_10_examples_are_executable(self):
        for number in NUMBERS:
            with self.subTest(chapter=number):
                path=ROOT/"content"/"examples"/number/"01.txt"
                code=path.read_text(encoding="utf-8")
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(compile(code,str(path),"exec"),{"__name__":"__main__"})

    def test_06_to_10_reviewed_content_and_svg_xml(self):
        for number in NUMBERS:
            with self.subTest(chapter=number):
                root=REPO/f"{number}.html"
                html=root.read_text(encoding="utf-8")
                self.assertEqual(html.count('<h1>'),1)
                self.assertIn('<section id="references"',html)
                self.assertIn('class="language-python"',html)
                self.assertIn('<math',html)
                self.assertIn(f'assets/lessons/{number}.svg',html)
                meta=json.loads((ROOT/"content"/"lessons"/f"{number}.json").read_text(encoding="utf-8"))
                evidence=json.loads((ROOT/"content"/"evidence"/f"{number}.json").read_text(encoding="utf-8"))
                self.assertEqual(meta["review_status"],"reviewed")
                self.assertEqual(evidence["review_status"],"reviewed")
                self.assertTrue(all(x.get("source_url") and x.get("locator") for x in evidence["claims"]))
                svg=ET.parse(REPO/"assets"/"lessons"/f"{number}.svg").getroot()
                ns="{http://www.w3.org/2000/svg}"
                self.assertTrue(svg.attrib.get("viewBox"))
                self.assertIsNotNone(svg.find(ns+"title"))
                self.assertIsNotNone(svg.find(ns+"desc"))

    @staticmethod
    def bridge_graph():
        return nx.Graph([(0,1),(1,2),(2,0),(2,3),(3,4),(4,5),(5,3)])

if __name__=="__main__":
    unittest.main()
