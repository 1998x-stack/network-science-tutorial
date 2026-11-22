"""Third reviewed batch: scientific oracles, executable examples and accessible assets."""
from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import random
import unittest
import xml.etree.ElementTree as ET
import networkx as nx

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
NUMBERS=("11","12","13","14","15")

class ThirdBatchOracleTests(unittest.TestCase):
    def test_11_kcore_peeling_and_overlapping_cliques(self):
        g=nx.Graph([("A","B"),("A","X"),("B","X"),("X","C"),
                    ("X","D"),("C","D"),("A","L1"),("D","L2")])
        self.assertEqual((len(g),g.number_of_edges()),(7,8))
        self.assertEqual(set(nx.k_core(g,1)),set(g))
        self.assertEqual(set(nx.k_core(g,2)),{"A","B","X","C","D"})
        self.assertEqual(set(nx.k_core(g,3)),set())
        self.assertEqual(nx.core_number(g)["X"],2)
        self.assertEqual({"A","B","X"}&{"X","C","D"},{"X"})

    def test_12_sir_one_step_path_and_contact_risk(self):
        g=nx.path_graph(5)
        state={v:("I" if v==0 else "S") for v in g}
        history=[dict(state)]
        for _ in range(5):
            next_state=dict(state)
            for v in g:
                if state[v]=="I":next_state[v]="R"
                elif state[v]=="S" and any(state[u]=="I" for u in g.neighbors(v)):
                    next_state[v]="I"
            state=next_state
            history.append(dict(state))
        self.assertEqual([sum(s[v]=="I" for v in g) for s in history],[1,1,1,1,1,0])
        self.assertEqual([sum(s[v]=="R" for v in g) for s in history],[0,1,2,3,4,5])
        self.assertAlmostEqual(1-(1-.3)**2,.51,places=12)

    def test_13_simple_vs_complex_progressive_cascade(self):
        g=nx.Graph([("A","C"),("B","C"),("B","D"),("C","D"),
                    ("C","E"),("D","E"),("E","F")])
        def hist(k):
            a={"A","B"}
            output=[set(a)]
            for _ in range(4):
                new={v for v in g if v not in a and
                     sum(u in a for u in g.neighbors(v))>=k}
                a=a|new
                output.append(set(a))
            return output
        self.assertEqual([len(x) for x in hist(1)],[2,4,5,6,6])
        self.assertEqual([len(x) for x in hist(2)],[2,3,4,5,5])
        self.assertNotIn("F",hist(2)[-1])
        self.assertIn("F",hist(1)[-1])

    def test_14_donation_voter_and_bounded_confidence(self):
        g=nx.path_graph(["A","B","C","D"])
        s={"A":1,"B":1,"C":0,"D":0}
        pay={v:3*sum(s[u] for u in g.neighbors(v))-g.degree(v)*s[v] for v in g}
        self.assertEqual([pay[v] for v in "ABCD"],[2,1,3,0])
        other=dict(s);other["B"]=s["C"]
        self.assertEqual([other[v] for v in "ABCD"],[1,0,0,0])
        x=[.1,.2,.9]
        epsilon=.2
        after=[sum(y for y in x if abs(y-v)<=epsilon)/
               sum(abs(y-v)<=epsilon for y in x) for v in x]
        for actual,expected in zip(after,[.15,.15,.9]):
            self.assertAlmostEqual(actual,expected,places=12)

    def test_15_star_path_comparable_removal_and_overload(self):
        star,path=nx.star_graph(6),nx.path_graph(7)
        self.assertEqual((len(star),star.number_of_edges()),(7,6))
        self.assertEqual((len(path),path.number_of_edges()),(7,6))
        def fraction(g,remove):
            h=g.copy();h.remove_node(remove)
            largest=max(len(c) for c in nx.connected_components(h))
            return largest,largest/len(h)
        self.assertEqual(fraction(star,6),(6,1))
        size,f=fraction(star,0)
        self.assertEqual(size,1)
        self.assertAlmostEqual(f,1/6)
        self.assertEqual(fraction(path,3),(3,.5))
        self.assertEqual(sum(6>5 for _ in range(2)),2)
        self.assertEqual(sum(6>6 for _ in range(2)),0)

    def test_source_code_examples_execute_individually(self):
        for n in NUMBERS:
            with self.subTest(chapter=n):
                path=ROOT/"content"/"examples"/n/"01.txt"
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(compile(path.read_text(encoding="utf-8"),str(path),"exec"),
                         {"__name__":"__main__"})

    def test_reviewed_evidence_and_accessible_svg(self):
        ns="{http://www.w3.org/2000/svg}"
        for n in NUMBERS:
            with self.subTest(chapter=n):
                html=(REPO/f"{n}.html").read_text(encoding="utf-8")
                self.assertEqual(html.count("<h1>"),1)
                for token in ('<figure class="lesson-figure"','<section id="references"',
                              'class="language-python"','<math'):
                    self.assertIn(token,html)
                meta=json.loads((ROOT/"content"/"lessons"/f"{n}.json").read_text(encoding="utf-8"))
                evidence=json.loads((ROOT/"content"/"evidence"/f"{n}.json").read_text(encoding="utf-8"))
                self.assertEqual(meta["review_status"],"reviewed")
                self.assertEqual(evidence["review_status"],"reviewed")
                self.assertGreaterEqual(len(evidence["claims"]),5)
                self.assertTrue(all(item.get("source_url") and item.get("locator")
                                    for item in evidence["claims"]))
                svg=ET.parse(REPO/"assets"/"lessons"/f"{n}.svg").getroot()
                self.assertTrue(svg.attrib.get("viewBox"))
                self.assertIsNotNone(svg.find(ns+"title"))
                self.assertIsNotNone(svg.find(ns+"desc"))

if __name__=="__main__":
    unittest.main()
