"""Fourth batch: leak-safe links, layout invariants, source projections, multiplex paths, temporal paths."""
from __future__ import annotations
import contextlib
import csv
import io
import json
import math
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import networkx as nx

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
NUMBERS=("16","17","18","19","20")

class FourthBatchScientificChecks(unittest.TestCase):
    def test_16_training_graph_scores_and_no_future_edge(self):
        g=nx.Graph([("A","B"),("A","C"),("B","C"),("B","D"),("C","D"),("D","E")])
        self.assertFalse(g.has_edge("A","D"))
        common=set(nx.common_neighbors(g,"A","D"))
        self.assertEqual(common,{"B","C"})
        cn=len(common)
        j=cn/len(set(g["A"])|set(g["D"]))
        aa=sum(1/math.log(g.degree(z)) for z in common)
        self.assertEqual(cn,2)
        self.assertAlmostEqual(j,2/3)
        self.assertAlmostEqual(aa,2/math.log(3))
        self.assertAlmostEqual(next(nx.adamic_adar_index(g,[("A","D")]))[2],aa)
        self.assertEqual(len(set(g["A"])&set(g["E"])),0)

    def test_17_two_layouts_preserve_exact_graph_invariants(self):
        g=nx.Graph([("A","B"),("A","C"),("B","C"),("C","D"),
                    ("D","E"),("D","F"),("E","F")])
        edges={frozenset(e) for e in g.edges()}
        circular=nx.circular_layout(g)
        spring=nx.spring_layout(g,seed=7,iterations=100)
        self.assertEqual(set(circular),set(spring))
        self.assertEqual(set(spring),set(g))
        self.assertEqual(len(edges),7)
        self.assertEqual(dict(g.degree())["C"],3)
        self.assertEqual(dict(g.degree())["D"],3)
        self.assertEqual({frozenset(e) for e in g.edges()},edges)

    def test_18_synthetic_collection_projection_and_missing_bridge(self):
        records=[("A","B",1),("B","A",2),("B","C",3),("C","C",4),("C","D",5),("D","E",6)]
        pairs={frozenset((u,v)) for u,v,_ in records if u!=v}
        g=nx.Graph();g.add_nodes_from("ABCDE")
        g.add_edges_from(tuple(pair) for pair in pairs)
        self.assertEqual(len(records),6)
        self.assertEqual((len(g),g.number_of_edges()),(5,4))
        self.assertTrue(nx.is_connected(g))
        h=g.copy();h.remove_edge("C","D")
        self.assertEqual(sorted(map(len,nx.connected_components(h))),[2,3])

    def test_19_layered_and_flattened_shortest_paths_differ(self):
        actors=list("ABCD");s=[("A","B"),("B","C")];c=[("A","C"),("C","D")]
        supra=nx.Graph()
        for layer in ("social","collab"):
            supra.add_nodes_from((v,layer) for v in actors)
        supra.add_edges_from(((u,"social"),(v,"social")) for u,v in s)
        supra.add_edges_from(((u,"collab"),(v,"collab")) for u,v in c)
        supra.add_edges_from(((v,"social"),(v,"collab")) for v in actors)
        start,goal=("B","social"),("D","collab")
        self.assertEqual((len(supra),supra.number_of_edges()),(8,8))
        self.assertEqual(nx.shortest_path_length(supra,start,goal),3)
        h=supra.copy()
        h.remove_edges_from([((v,"social"),(v,"collab")) for v in actors])
        self.assertFalse(nx.has_path(h,start,goal))
        self.assertEqual(nx.shortest_path_length(nx.Graph(s+c),"B","D"),2)

    def test_20_strict_time_order_and_same_timestamp_batch(self):
        plans={
            "ordered":[("A","B",1),("B","C",2),("C","D",3)],
            "scrambled":[("A","B",3),("B","C",1),("C","D",2)],
            "simultaneous":[("A","B",1),("B","C",1),("C","D",1)]
        }
        def arrival(events):
            a={"A":0}
            for t in sorted(set(e[2] for e in events)):
                old=dict(a);new=dict(a)
                for u,v,when in events:
                    if when!=t:continue
                    for p,q in ((u,v),(v,u)):
                        if old.get(p,float("inf"))<t:
                            new[q]=min(new.get(q,float("inf")),t)
                a=new
            return a
        self.assertEqual(arrival(plans["ordered"]),{"A":0,"B":1,"C":2,"D":3})
        self.assertEqual(arrival(plans["scrambled"]),{"A":0,"B":3})
        self.assertEqual(arrival(plans["simultaneous"]),{"A":0,"B":1})
        for events in plans.values():
            g=nx.Graph((u,v) for u,v,_ in events)
            self.assertEqual(nx.shortest_path_length(g,"A","D"),3)

    def test_examples_execute_with_no_remote_dependencies(self):
        for n in NUMBERS:
            with self.subTest(chapter=n):
                path=ROOT/"content"/"examples"/n/"01.txt"
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(compile(path.read_text(encoding="utf-8"),str(path),"exec"),
                         {"__name__":"__main__"})

    def test_evidence_ledgers_and_accessible_artwork(self):
        ns="{http://www.w3.org/2000/svg}"
        for n in NUMBERS:
            with self.subTest(chapter=n):
                html=(REPO/f"{n}.html").read_text(encoding="utf-8")
                for token in ('class="lesson-article"','<figure class="lesson-figure"',
                              '<section id="references"','class="language-python"','<math'):
                    self.assertIn(token,html)
                self.assertEqual(html.count("<h1>"),1)
                metadata=json.loads((ROOT/"content"/"lessons"/f"{n}.json").read_text(encoding="utf-8"))
                ledger=json.loads((ROOT/"content"/"evidence"/f"{n}.json").read_text(encoding="utf-8"))
                self.assertEqual(metadata["review_status"],"reviewed")
                self.assertEqual(ledger["review_status"],"reviewed")
                self.assertGreaterEqual(len(ledger["claims"]),5)
                self.assertTrue(all(item.get("source_url") and item.get("locator")
                                    for item in ledger["claims"]))
                root=ET.parse(REPO/"assets"/"lessons"/f"{n}.svg").getroot()
                self.assertTrue(root.attrib.get("viewBox"))
                self.assertIsNotNone(root.find(ns+"title"))
                self.assertIsNotNone(root.find(ns+"desc"))
        for name in ("17-schematic.svg","17-circular.svg"):
            root=ET.parse(REPO/"assets"/"lessons"/name).getroot()
            self.assertIsNotNone(root.find(ns+"desc"))

if __name__=="__main__":
    unittest.main()
