"""Second-round cross-chapter research audit: external oracle + strict time contracts."""
from __future__ import annotations
import json
import math
from pathlib import Path
import re
import unittest

import networkx as nx

from experiments import temporal_audit as audit
from experiments import public_karate_audit as karate

V2=Path(__file__).resolve().parents[1]
ROOT=V2.parent
CROSS_CHAPTERS=("16","20","21","22","26","28")


class SecondRoundScientificAudit(unittest.TestCase):
    def test_01_fixed_timeline_and_node_universe(self):
        self.assertTrue(audit.validate_events())
        self.assertEqual(audit.snapshot(2),{
            ("A","B"),("A","C"),("B","C"),("C","D")
        })
        self.assertEqual(audit.snapshot(3)-audit.snapshot(2),{("D","E")})
        self.assertEqual(audit.snapshot(5)-audit.snapshot(3),{("B","D")})
        self.assertEqual(set(audit.adjacency(audit.snapshot(2))),set("ABCDE"))
        self.assertEqual(len(audit.adjacency(audit.snapshot(2))["E"]),0)

    def test_02_invalid_and_unsorted_events_are_rejected(self):
        with self.assertRaises(ValueError):audit.validate_events([("A","A",1)])
        with self.assertRaises(ValueError):audit.validate_events([("A","B",2),("B","C",1)])
        with self.assertRaises(ValueError):audit.validate_events([("A","B",True)])
        with self.assertRaises(ValueError):audit.snapshot(-1)
        with self.assertRaises(ValueError):audit.snapshot(3.5)
        with self.assertRaises(ValueError):audit.validate_events([("A","X",1)])

    def test_03_candidate_scoring_and_future_guard(self):
        past=audit.snapshot(3)
        self.assertEqual(audit.common_neighbors("B","D",past),1)
        self.assertEqual(audit.common_neighbors("B","E",past),0)
        with self.assertRaises(ValueError):
            audit.common_neighbors("B","D",audit.snapshot(5))
        with self.assertRaises(ValueError):
            audit.common_neighbors("A","B",past)
        g=nx.Graph()
        g.add_nodes_from("ABCDE")
        g.add_edges_from(past)
        self.assertEqual(len(list(nx.common_neighbors(g,"B","D"))),1)
        self.assertEqual(len(list(nx.common_neighbors(g,"B","E"))),0)

    def test_04_future_edge_changes_untargeted_features(self):
        past=audit.snapshot(3)
        contaminated=audit.snapshot(5)
        self.assertEqual(len(audit.adjacency(past)["B"] & audit.adjacency(past)["E"]),0)
        self.assertEqual(len(audit.adjacency(contaminated)["B"] & audit.adjacency(contaminated)["E"]),1)
        self.assertEqual(audit.probability_next_step("B","D",past),0)
        self.assertAlmostEqual(audit.probability_next_step("B","D",contaminated),1/3)
        self.assertEqual(audit.gcn_normalized_edge("B","D",past,True),0)
        self.assertAlmostEqual(audit.gcn_normalized_edge("B","D",contaminated,True),1/4)
        self.assertAlmostEqual(audit.gcn_normalized_edge("B","D",contaminated,False),1/3)

    def test_05_bipartite_future_edge_changes_normalized_weight(self):
        clean=audit.lightgcn_example(False)
        leaked=audit.lightgcn_example(True)
        self.assertAlmostEqual(clean["U1_to_X_weight"],1/math.sqrt(2))
        self.assertEqual(clean["U2_to_X_weight"],0)
        self.assertAlmostEqual(leaked["U1_to_X_weight"],.5)
        self.assertAlmostEqual(leaked["U2_to_X_weight"],.5)
        self.assertFalse(clean["future_user_item_in_training"])
        self.assertTrue(leaked["future_user_item_in_training"])

    def test_06_same_time_contact_cannot_chain_in_strict_model(self):
        r=audit.audit_report()
        self.assertEqual(r["temporal_path_ordered"],{"A":0,"B":1,"C":2,"D":3})
        self.assertEqual(r["temporal_path_reordered"],{"A":0,"B":3,"C":None,"D":None})
        self.assertEqual(r["temporal_path_simultaneous"],{"A":0,"B":1,"C":None,"D":None})
        self.assertIsNone(audit.earliest_arrivals([("A","B",1),("B","C",1)])["C"])

    def test_07_audit_report_not_adding_future_labels(self):
        report=audit.audit_report()
        self.assertEqual(report["training_edges"],[["A","B"],["A","C"],["B","C"],["C","D"]])
        self.assertEqual(report["validation_new_edges"],[["D","E"]])
        self.assertEqual(report["test_new_edges"],[["B","D"]])
        self.assertEqual(report["clean_graph_edges_before_test"],5)
        self.assertEqual(report["clean_candidate_scores"],{"B-D":1,"B-E":0})
        self.assertEqual(report["clean_restricted_precision_at_1"],1)
        self.assertTrue(report["illegal_training_B_D_becomes_observed"])
        self.assertEqual(report["illegal_common_neighbors_B_E"],1)
        self.assertIn("synthetic",report["data_kind"])
        self.assertGreaterEqual(len(report["limitations"]),4)

    def test_08_public_karate_offline_data_and_independent_triangle_oracle(self):
        r=karate.public_report()
        self.assertEqual((r["nodes"],r["edges"],r["connected_components"]),(34,78,1))
        self.assertEqual((r["triangles_unweighted"],r["triangles_independent_oracle"]),(45,45))
        self.assertEqual(r["degree_sum"],156)
        self.assertAlmostEqual(r["density_unweighted_simple"],156/(34*33))
        self.assertIn("static",r["limitations"][0])
        self.assertTrue(r["networkx_version"])

    def test_09_cross_chapter_links_and_homepage_hub(self):
        for chapter in CROSS_CHAPTERS:
            with self.subTest(chapter=chapter):
                html=(ROOT/f"{chapter}.html").read_text(encoding="utf-8")
                self.assertIn('href="research/temporal-leakage.html"',html)
                self.assertIn("研究级交叉验证",html)
        portal=(ROOT/"index.html").read_text(encoding="utf-8")
        self.assertIn('href="research/temporal-leakage.html"',portal)
        self.assertIn('href="24.html"',portal)
        guide=(ROOT/"research/temporal-leakage.html").read_text(encoding="utf-8")
        self.assertIn('data-temporal-cutoff="5"',guide)
        self.assertIn('data-ui-item-future',guide)
        self.assertIn("ogb.stanford.edu/docs/linkprop",guide)

    def test_11_deep_reader_links_resolve_to_research_page(self):
        target=ROOT/"research/temporal-leakage.html"
        self.assertTrue(target.is_file())
        for chapter in CROSS_CHAPTERS:
            with self.subTest(chapter=chapter):
                file=V2/"apps/web/lessons"/f"{chapter}.html"
                content=file.read_text(encoding="utf-8")
                relative="../../../../research/temporal-leakage.html"
                self.assertIn(f'href="{relative}"',content)
                self.assertNotIn('href="research/temporal-leakage.html"',content)
                self.assertEqual((file.parent/relative).resolve(),target.resolve())

    def test_12_leakage_diagram_depicts_correct_future_edge(self):
        import xml.etree.ElementTree as ET
        graphic=ROOT/"research/contamination-path.svg"
        ns="{http://www.w3.org/2000/svg}"
        root=ET.parse(graphic).getroot()
        self.assertIsNotNone(root.find(ns+"title"))
        self.assertIsNotNone(root.find(ns+"desc"))
        edges={tag.attrib["d"] for tag in root.findall(".//"+ns+"path")}
        # The legal left-hand subgraph shows only D-E; the incorrect
        # right-hand graph adds future B-D, not B-E.
        self.assertIn("M288 174 L373 272",edges)
        self.assertIn("M786 174 L871 272",edges)
        self.assertIn("M628 174 L786 174",edges)
        self.assertNotIn("M130 174 L288 174 L373 272",edges)
        self.assertNotIn("M628 174 L871 272",edges)

    def test_10_claim_ledgers_trace_scope(self):
        for chapter in CROSS_CHAPTERS:
            claims=json.loads((V2/"content/evidence"/f"{chapter}.json").read_text(encoding="utf-8"))["claims"]
            found=[item for item in claims if item["id"]==f"round2-{chapter}-temporal"]
            self.assertEqual(len(found),1)
            self.assertIn("ogb.stanford.edu/docs/linkprop",found[0]["source_url"])
            self.assertTrue(found[0]["locator"])
        for module in ("temporal_audit.py","public_karate_audit.py"):
            self.assertTrue((V2/"experiments"/module).is_file())


if __name__=="__main__":
    unittest.main()
