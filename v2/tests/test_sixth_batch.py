"""Scientific and artifact-quality checks for final chapters 26–28.

Independent NetworkX oracle checks the synthetic capstone and threshold graph.
Toy numerical results are not paper reproduction or real-world benchmarks.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import math
import re
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
NUMBERS = ("26", "27", "28")
SVG_NS = "{http://www.w3.org/2000/svg}"


def import_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FinalChapterReviewChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.migrate = import_script(ROOT / "scripts" / "migrate_lessons.py", "migrate_final")
        cls.capstone = import_script(ROOT / "experiments" / "capstone_28.py", "capstone_final")

    def test_reviewed_metadata_evidence_and_snapshot_hash(self):
        for chapter in NUMBERS:
            with self.subTest(chapter=chapter):
                html = (REPO / f"{chapter}.html").read_text(encoding="utf-8")
                meta = json.loads((ROOT / "content/lessons" / f"{chapter}.json").read_text(encoding="utf-8"))
                ledger = json.loads((ROOT / "content/evidence" / f"{chapter}.json").read_text(encoding="utf-8"))
                self.assertEqual(html.count("<h1>"), 1)
                self.assertEqual(html.count('<figure class="lesson-figure">'), 3)
                self.assertIn('<math xmlns="http://www.w3.org/1998/Math/MathML"', html)
                self.assertIn('class="language-python"', html)
                self.assertIn('data-demo="final-', html)
                self.assertIn(f'href="{chapter}.html" class="active"', html)
                self.assertEqual(meta["review_status"], "reviewed")
                self.assertEqual(meta["source_git_blob"], self.migrate.git_blob_sha(html))
                self.assertEqual(ledger["review_status"], "reviewed")
                self.assertEqual(ledger["chapter"], chapter)
                self.assertGreaterEqual(len(ledger["claims"]), 8)
                self.assertTrue(all(x["source_url"] and x["locator"] for x in ledger["claims"]))
                self.assertEqual(
                    (ROOT / "content/lessons" / f"{chapter}.html").read_text(encoding="utf-8"),
                    self.migrate.article(html),
                )
                self.assertNotIn("HitRate@10提升了约7%", html)

    def test_original_diagrams_are_well_formed_and_match_v2_copies(self):
        for chapter in NUMBERS:
            for letter in "abc":
                with self.subTest(chapter=chapter, figure=letter):
                    orig = REPO / "assets" / "lessons" / f"{chapter}-{letter}.svg"
                    mirror = ROOT / "apps" / "web" / "assets" / "lessons" / f"{chapter}-{letter}.svg"
                    self.assertEqual(orig.read_bytes(), mirror.read_bytes())
                    root = ET.parse(orig).getroot()
                    self.assertEqual(root.tag, SVG_NS+"svg")
                    self.assertTrue(root.attrib.get("viewBox"))
                    self.assertIsNotNone(root.find(SVG_NS+"title"))
                    self.assertIsNotNone(root.find(SVG_NS+"desc"))

    def test_mathml_parses_and_has_accessible_labels(self):
        for chapter in NUMBERS:
            html = (REPO / f"{chapter}.html").read_text(encoding="utf-8")
            fragments = re.findall(r"<math\b[\s\S]*?</math>", html)
            self.assertGreaterEqual(len(fragments), 1)
            for chunk in fragments:
                with self.subTest(chapter=chapter):
                    math_node = ET.fromstring(chunk)
                    self.assertTrue(math_node.attrib.get("aria-label"))

    def test_python_examples_extracted_and_actually_execute(self):
        for chapter in NUMBERS:
            metadata = json.loads((ROOT / "content/lessons" / f"{chapter}.json").read_text(encoding="utf-8"))
            tested = [e for e in metadata["examples"] if e["review_status"]=="tested"]
            self.assertGreaterEqual(len(tested), 1, chapter)
            for e in tested:
                with self.subTest(chapter=chapter, example=e["id"]):
                    path=ROOT/e["path"]
                    with contextlib.redirect_stdout(io.StringIO()):
                        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), {"__name__":"__main__"})

    def test_26_bpr_and_lightgcn_numeric_contracts(self):
        self.assertAlmostEqual(1/math.sqrt(2), .7071067811865475)
        self.assertAlmostEqual(math.log1p(math.exp(-2)), .1269280110429725)
        self.assertAlmostEqual(math.log1p(1), math.log(2))
        def distance(head,relation,tail):
            return math.dist([a+b for a,b in zip(head,relation)], tail)
        self.assertAlmostEqual(distance([1,2],[2,-1],[3,1]),0)
        self.assertAlmostEqual(distance([1,2],[2,-1],[3,2]),1)
        graph=nx.Graph()
        graph.add_edges_from([("U1","X"),("U1","Y"),("U2","Y")])
        self.assertEqual(dict(graph.degree()),{"U1":2,"X":1,"Y":2,"U2":1})
        self.assertAlmostEqual(1/math.sqrt(graph.degree("U1")*graph.degree("X")),1/math.sqrt(2))

    def test_27_brain_threshold_graph_with_isolated_nodes(self):
        weights={("A","B"):.8,("B","C"):.6,("A","C"):.2}
        for threshold,expected in ((.2,(3,1)),(.5,(2,1)),(.7,(1,2)),(1,(0,3))):
            with self.subTest(tau=threshold):
                g=nx.Graph()
                g.add_nodes_from("ABC")
                g.add_edges_from(pair for pair,w in weights.items() if w+1e-10>=threshold)
                self.assertEqual((g.number_of_edges(),nx.number_connected_components(g)),expected)

    def test_27_confounded_observation_does_not_create_within_group_difference(self):
        low_exposed,low_control=2/20,8/80
        high_exposed,high_control=32/80,8/20
        self.assertEqual(low_exposed,low_control)
        self.assertEqual(high_exposed,high_control)
        crude=(2+32)/100-(8+8)/100
        self.assertAlmostEqual(crude,.18)
        self.assertAlmostEqual(abs(3/4-1/4),.5)

    def test_28_capstone_matches_networkx_and_does_not_use_future_edges(self):
        cap=self.capstone
        original=cap.report(3)
        early=cap.report(1)
        self.assertEqual(original["train_edge_count"],5)
        self.assertEqual(early["train_edge_count"],2)
        self.assertFalse(original["future_edges_leaked"])
        self.assertEqual(original["degrees"],{"A":2,"B":2,"C":3,"D":2,"E":1})
        self.assertEqual(original["candidate_scores"],[
            {"u":"B","v":"D","common_neighbors":1},
            {"u":"B","v":"E","common_neighbors":0},
        ])
        self.assertEqual(original["precision_at_1_restricted_pool"],1.0)
        graph=nx.Graph()
        graph.add_nodes_from(cap.NODES)
        graph.add_edges_from(tuple(edge) for edge in cap.edge_set(3))
        self.assertEqual(graph.number_of_nodes(),5)
        self.assertEqual(graph.number_of_edges(),5)
        self.assertTrue(nx.is_connected(graph))
        self.assertAlmostEqual(nx.density(graph),.5)
        self.assertFalse(graph.has_edge("B","D"))
        self.assertEqual(len(list(nx.common_neighbors(graph,"B","D"))),1)
        self.assertEqual(len(list(nx.common_neighbors(graph,"B","E"))),0)
        with self.assertRaises(ValueError):
            cap.score("A","B",cap.edge_set(3))
        with self.assertRaises(ValueError):
            cap.edge_set(5)

    def test_28_cli_json_report_can_be_recomputed_without_network(self):
        with contextlib.redirect_stdout(io.StringIO()) as capture:
            self.capstone.main()
        data=json.loads(capture.getvalue())
        self.assertEqual(data["dataset_kind"],"synthetic_not_real_world")
        self.assertEqual(data["observed_test_positive_count"],1)
        self.assertEqual(data["candidate_pool_size"],2)
        self.assertFalse(data["future_edges_leaked"])


if __name__=="__main__":
    unittest.main()
