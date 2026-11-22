"""Independent scientific contracts for deeply reviewed lessons 21–25.

Source chapter HTML is authoring authority. Generated V2 snapshots are checked
against the source and runnable Python examples; benchmarks are not claimed.
"""
from __future__ import annotations

import contextlib
import io
import json
import math
import re
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
NUMBERS = ("21", "22", "23", "24", "25")
NS = "{http://www.w3.org/2000/svg}"


class FifthBatchScientificChecks(unittest.TestCase):
    def test_provenance_and_reviewed_source_snapshots(self):
        from importlib.util import module_from_spec, spec_from_file_location
        script = ROOT / "scripts" / "migrate_lessons.py"
        spec = spec_from_file_location("netsci_migrate_test", script)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        for number in NUMBERS:
            with self.subTest(chapter=number):
                source = (REPO / f"{number}.html").read_text(encoding="utf-8")
                meta = json.loads((ROOT / "content/lessons" / f"{number}.json").read_text(encoding="utf-8"))
                ledger = json.loads((ROOT / "content/evidence" / f"{number}.json").read_text(encoding="utf-8"))
                self.assertEqual(meta["source_git_blob"], mod.git_blob_sha(source))
                self.assertEqual(meta["review_status"], "reviewed")
                self.assertEqual(ledger["chapter"], number)
                self.assertEqual(ledger["review_status"], "reviewed")
                self.assertGreaterEqual(len(ledger["claims"]), 6)
                self.assertTrue(all(x.get("source_url") and x.get("locator") for x in ledger["claims"]))
                self.assertEqual(source.count("<h1>"), 1)
                self.assertEqual(source.count('<figure class="lesson-figure">'), 2)
                self.assertNotIn("大家好", source)
                self.assertNotIn("我在实际项目", source)
                self.assertIn('<math xmlns="http://www.w3.org/1998/Math/MathML"', source)
                self.assertIn('class="language-python"', source)
                self.assertIn(f'data-demo="', source)
                self.assertEqual(
                    (ROOT / "content/lessons" / f"{number}.html").read_text(encoding="utf-8"),
                    mod.article(source)
                )
                for letter in ("a", "b"):
                    svgroot = REPO / "assets/lessons" / f"{number}-{letter}.svg"
                    svgweb = ROOT / "apps/web/assets/lessons" / f"{number}-{letter}.svg"
                    self.assertEqual(svgroot.read_bytes(), svgweb.read_bytes())
                    self.assertTrue(ET.parse(svgroot).getroot().attrib.get("viewBox"))
                    parsed = ET.parse(svgroot).getroot()
                    self.assertIsNotNone(parsed.find(NS + "title"))
                    self.assertIsNotNone(parsed.find(NS + "desc"))

    def test_mathml_parses_and_has_accessible_labels(self):
        for number in NUMBERS:
            source = (REPO / f"{number}.html").read_text(encoding="utf-8")
            maths = re.findall(r"<math\b[\s\S]*?</math>", source)
            self.assertGreaterEqual(len(maths), 1, number)
            for frag in maths:
                parsed = ET.fromstring(frag)
                self.assertTrue(parsed.attrib.get("aria-label"))

    def test_all_declared_tested_python_examples_really_execute(self):
        for number in NUMBERS:
            metadata = json.loads((ROOT / "content/lessons" / f"{number}.json").read_text(encoding="utf-8"))
            tested = [item for item in metadata["examples"] if item["review_status"] == "tested"]
            self.assertGreaterEqual(len(tested), 1, number)
            for item in tested:
                with self.subTest(chapter=number, example=item["id"]):
                    src = ROOT / item["path"]
                    namespace = {"__name__": "__main__"}
                    with contextlib.redirect_stdout(io.StringIO()):
                        exec(compile(src.read_text(encoding="utf-8"), str(src), "exec"), namespace)

    def test_21_node2vec_conditional_probability(self):
        def prob(p,q):
            raw = (1/p, 1, 1/q)
            return tuple(x/sum(raw) for x in raw)
        a=prob(1,2)
        self.assertTrue(all(math.isclose(x,y) for x,y in zip(a,(.4,.4,.2))))
        b=prob(1,.5)
        self.assertTrue(math.isclose(b[2],.5))
        self.assertTrue(math.isclose(sum(b),1.0))

    def test_22_gcn_with_independent_networkx_adjacency(self):
        graph=nx.Graph([(0,1),(1,2)])
        H=graph.copy()
        H.add_edges_from((i,i) for i in graph.nodes)
        degrees=dict(H.degree())
        # networkx Graph.degree counts self-loop twice; use adjacency neighbors
        d={u:len(H[u]) for u in H}
        self.assertEqual(d,{0:2,1:3,2:2})
        result=sum((1 if u==0 else 0)/math.sqrt(d[u]*d[1]) for u in H[1])
        self.assertAlmostEqual(result,1/math.sqrt(6))
        self.assertNotAlmostEqual(result,1/3,places=3)

    def test_23_bridge_and_isolated_node_independent_bfs(self):
        pairs=[("A","B"),("B","C"),("C","A"),("D","E"),("E","F"),("F","D"),("C","D")]
        nodes=set("ABCDEFG")
        def components(edges):
            adj={v:set() for v in nodes}
            for a,b in edges:
                adj[a].add(b);adj[b].add(a)
            seen=set();sizes=[]
            for v in sorted(nodes):
                if v in seen:continue
                todo=[v];seen.add(v);count=0
                while todo:
                    x=todo.pop();count+=1
                    for y in adj[x]-seen:
                        seen.add(y);todo.append(y)
                sizes.append(count)
            return sorted(sizes)
        self.assertEqual(components(pairs),[1,6])
        reduced=[e for e in pairs if set(e)!={"C","D"}]
        self.assertEqual(components(reduced),[1,3,3])
        g=nx.Graph();g.add_nodes_from(nodes);g.add_edges_from(pairs)
        self.assertEqual(set(map(frozenset,nx.bridges(g))),{frozenset("CD")})
        self.assertEqual(nx.number_connected_components(g),2)
        self.assertAlmostEqual(nx.density(g),1/3)

    def test_24_karate_data_and_permutation_invariance(self):
        g=nx.karate_club_graph()
        self.assertEqual((g.number_of_nodes(),g.number_of_edges()),(34,78))
        self.assertEqual(set(nx.get_node_attributes(g,"club").values()),{"Mr. Hi","Officer"})
        truth=("A","A","B","B")
        labels=("B","B","A","A")
        self.assertEqual(sum(a==b for a,b in zip(truth,labels)),0)
        self.assertEqual(sum(a==("A" if b=="B" else "B") for a,b in zip(truth,labels)),4)
        self.assertEqual(4*3//2,6)
        self.assertEqual(100*99//2,4950)

    def test_25_sparsity_budget_and_periodic_star(self):
        n,m=1_000_000,5_000_000
        self.assertEqual(8*n*n,8_000_000_000_000)
        self.assertEqual(8*(n+1)+32*m,168_000_008)
        g=nx.star_graph(5)
        self.assertEqual(g.number_of_nodes(),6)
        self.assertEqual(g.degree(0),5)
        self.assertAlmostEqual(g.degree(0)/(2*g.number_of_edges()),.5)
        self.assertAlmostEqual(1/g.number_of_nodes(),1/6)


if __name__ == "__main__":
    unittest.main()
