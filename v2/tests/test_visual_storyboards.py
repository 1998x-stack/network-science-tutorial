"""Independent illustration QA and scientific toy oracles for all 28 chapters.

The SVGs are evidence-linked visual teaching material. These tests intentionally
do not label toy computations as reproduced empirical benchmark results.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
NUMBERS = [f"{n:02}" for n in range(1, 29)]
SVG_NS = "{http://www.w3.org/2000/svg}"


class VisualHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.links=[]
        self.images=[]
        self.storyboards=0
        self.figures=0
        self.toc=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag=="a":
            self.links.append(a.get("href",""))
        if tag=="img":
            self.images.append(a.get("src",""))
        if tag=="figure":
            self.figures+=1
            if "visual-storyboard" in a.get("class","").split():
                self.storyboards+=1
        if tag=="nav" and "lesson-jump" in a.get("class","").split():
            self.toc+=1


class VisualStoryboardQuality(unittest.TestCase):
    def test_every_root_article_has_storyboard_toc_and_skip_link(self):
        for n in NUMBERS:
            with self.subTest(chapter=n):
                source=(REPO/f"{n}.html").read_text(encoding="utf-8")
                parsed=VisualHTML()
                parsed.feed(source)
                self.assertEqual(parsed.storyboards,1)
                self.assertEqual(parsed.toc,1)
                self.assertIn(f"assets/lessons/{n}-visual.svg",parsed.images)
                self.assertIn("lesson-content",parsed.ids)
                self.assertIn("#lesson-content",parsed.links)
                self.assertIn('<div class="diagram-viewport" tabindex="0" role="region"',source)
                self.assertIn('<figcaption><strong>检验点：</strong>',source)
                self.assertEqual(source.count("<h1>"),1)
                toc=re.search(r'<nav class="lesson-jump"[^>]*>([\s\S]*?)</nav>',source)
                self.assertIsNotNone(toc)
                anchors=re.findall(r'<a href="#([^"]+)">',toc.group(1))
                self.assertEqual(len(anchors),4)
                for anchor in anchors:
                    self.assertIn(anchor,parsed.ids)

    def test_v2_migration_preserves_narrative_and_resolves_diagram(self):
        for n in NUMBERS:
            with self.subTest(chapter=n):
                original=(REPO/f"{n}.html").read_text(encoding="utf-8")
                reviewed=(ROOT/"content/lessons"/f"{n}.html").read_text(encoding="utf-8")
                rendered=(ROOT/"apps/web/lessons"/f"{n}.html").read_text(encoding="utf-8")
                self.assertIn(f'data-visual-chapter="{n}"',original)
                self.assertIn(f'data-visual-chapter="{n}"',reviewed)
                self.assertIn(f'data-visual-chapter="{n}"',rendered)
                self.assertIn(f'src="../assets/lessons/{n}-visual.svg"',rendered)
                meta=json.loads((ROOT/"content/lessons"/f"{n}.json").read_text(encoding="utf-8"))
                self.assertEqual(meta["review_status"],"reviewed")

    def test_svg_mirrors_well_formed_semantically_labelled_and_self_contained(self):
        for n in NUMBERS:
            with self.subTest(chapter=n):
                a=REPO/"assets/lessons"/f"{n}-visual.svg"
                b=ROOT/"apps/web/assets/lessons"/f"{n}-visual.svg"
                self.assertTrue(a.is_file())
                self.assertEqual(a.read_bytes(),b.read_bytes())
                tree=ET.parse(a)
                root=tree.getroot()
                self.assertEqual(root.tag,SVG_NS+"svg")
                self.assertEqual(root.attrib.get("role"),"img")
                self.assertEqual(root.attrib.get("viewBox"),"0 0 1100 510")
                title=root.find(SVG_NS+"title")
                desc=root.find(SVG_NS+"desc")
                self.assertIsNotNone(title)
                self.assertIsNotNone(desc)
                self.assertGreaterEqual(len(title.text.strip()),7)
                self.assertGreaterEqual(len(desc.text.strip()),20)
                labelled=root.attrib.get("aria-labelledby","").split()
                self.assertEqual(labelled,[title.attrib["id"],desc.attrib["id"]])
                self.assertGreaterEqual(len(list(root.iter(SVG_NS+"text"))),10)
                self.assertFalse(list(root.iter(SVG_NS+"script")))
                self.assertFalse(list(root.iter(SVG_NS+"foreignObject")))
                self.assertFalse(list(root.iter(SVG_NS+"image")))
                for e in root.iter():
                    ids=[k for k in e.attrib if k=="href" or k.endswith("}href")]
                    self.assertFalse(ids,"image must be standalone and offline")
                for text in root.iter(SVG_NS+"text"):
                    size=text.attrib.get("font-size")
                    self.assertIsNotNone(size)
                    self.assertGreaterEqual(float(size),16.0)

    def test_homepage_visual_roadmap_is_accessible_and_clickable(self):
        home=(REPO/"index.html").read_text(encoding="utf-8")
        self.assertIn('id="learning-roadmap"',home)
        self.assertIn('src="assets/learning-route.svg"',home)
        self.assertIn('role="region"',home)
        route=ET.parse(REPO/"assets/learning-route.svg").getroot()
        self.assertIsNotNone(route.find(SVG_NS+"title"))
        self.assertIsNotNone(route.find(SVG_NS+"desc"))
        nav=re.search(r'<nav class="phase-links"[^>]*>([\s\S]*?)</nav>',home)
        self.assertIsNotNone(nav)
        self.assertEqual(len(re.findall(r'<a href="\d\d.html"',nav.group(1))),6)
        for start in ("01","04","08","12","17","24"):
            self.assertIn(f'href="{start}.html"',nav.group(1))

    def test_07_histogram_frequencies_match_executable_graph_not_just_edge_sum(self):
        g=nx.Graph()
        g.add_nodes_from(range(8))
        g.add_edges_from([(0,1),(0,2),(0,3),(0,4),(0,5),(1,2),(2,3)])
        degrees=[d for _,d in g.degree()]
        self.assertEqual(dict(sorted(Counter(degrees).items())),{0:2,1:2,2:2,3:1,5:1})
        self.assertEqual(sum(degrees),14)
        self.assertEqual(sum(d*d for d in degrees)/8,5.5)
        plot=(REPO/"assets/lessons/07-visual.svg").read_text(encoding="utf-8")
        self.assertIn("k=0,1,2：各 2 个",plot)
        self.assertIn("k=3,5：各 1 个",plot)
        source=(REPO/"07.html").read_text(encoding="utf-8")
        self.assertIn("P(3)=P(5)=1/8",source)
        self.assertNotIn("P(2)=1/2，P(3)=1/4",source)

    def test_04_expectation_and_05_rewiring_preserve_defined_semantics(self):
        self.assertAlmostEqual(math.comb(5,2)*.2,2)
        g=nx.cycle_graph(6)
        before=nx.shortest_path_length(g,0,3)
        g.remove_edge(0,1)
        g.add_edge(0,3)
        self.assertEqual((g.number_of_nodes(),g.number_of_edges()),(6,6))
        self.assertEqual(before,3)
        self.assertEqual(nx.shortest_path_length(g,0,3),1)

    def test_08_bridge_and_10_modularity_agree_with_diagram(self):
        g=nx.Graph()
        g.add_edges_from([("A","B"),("A","C"),("B","C"),
                          ("C","D"),("D","E"),("D","F"),("E","F")])
        self.assertEqual(g.number_of_edges(),7)
        self.assertEqual((g.degree("C"),g.degree("D")),(3,3))
        self.assertAlmostEqual(nx.community.modularity(g,[{"A","B","C"},{"D","E","F"}]),5/14)
        svg=(REPO/"assets/lessons/10-visual.svg").read_text(encoding="utf-8")
        self.assertIn("M 194 350 L 447 229",svg)
        self.assertNotIn("M 194 350 L 519 350",svg)
        g.remove_edge("C","D")
        self.assertEqual(nx.number_connected_components(g),2)

    def test_14_payoffs_16_candidates_and_22_gcn(self):
        g=nx.path_graph(list("ABCD"))
        s=dict(zip("ABCD","CCDD"))
        pay=[3*sum(s[v]=="C" for v in g.neighbors(u)) -
             (g.degree(u) if s[u]=="C" else 0) for u in "ABCD"]
        self.assertEqual(pay,[2,1,3,0])
        h=nx.Graph()
        h.add_edges_from([("A","B"),("A","C"),("B","C"),
                          ("B","D"),("C","D"),("D","E")])
        common=set(h["A"])&set(h["D"])
        self.assertEqual(common,{"B","C"})
        self.assertAlmostEqual(len(common)/len(set(h["A"])|set(h["D"])),2/3)
        coeff=1/math.sqrt((1+g.degree("A"))*(1+g.degree("B")))
        # This coefficient is for A-B of a four-node path, not the GCN toy.
        self.assertAlmostEqual(coeff,1/math.sqrt(2*3))
        self.assertAlmostEqual(1/math.sqrt(2*3),.4082482904638631)

    def test_25_dense_vs_csr_formula_is_theoretical_only(self):
        n,m=10**6,5*10**6
        dense=n*n*8
        csr=8*(n+1)+2*m*8+2*m*8
        self.assertEqual(dense,8_000_000_000_000)
        self.assertEqual(csr,168_000_008)
        text=(REPO/"25.html").read_text(encoding="utf-8")
        self.assertIn("没有计入对象开销",text)
        self.assertIn("非峰值内存",(REPO/"assets/lessons/25-visual.svg").read_text(encoding="utf-8"))
        self.assertIn("168 MB",text)

    def test_09_page_rank_diagram_uses_real_arrowheads(self):
        tree=ET.parse(REPO/"assets/lessons/09-visual.svg")
        marker=tree.find(".//"+SVG_NS+"marker")
        self.assertIsNotNone(marker)
        arrows=[tag for tag in tree.iter(SVG_NS+"path") if "marker-end" in tag.attrib]
        self.assertGreaterEqual(len(arrows),3)


if __name__ == "__main__":
    unittest.main()
