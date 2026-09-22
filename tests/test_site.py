"""Regression tests for the dependency-free course site validator."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_site import validate  # noqa: E402


class SiteValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        chapters = [
            {"num": f"{i:02d}", "file": f"{i:02d}.html", "title": f"课程{i}", "topics": ["图论"]}
            for i in (1, 2)
        ]
        self.manifest = {"chapterCount": 2, "chapters": chapters}
        self.write_manifest()
        (self.root / "theme.css").write_text("body {}", encoding="utf-8")
        self.write_page("index.html", '<h1>课程目录</h1><a href="01.html">1</a><a href="02.html">2</a>')
        nav = '<a href="01.html" class="{active1}">1</a><a href="02.html" class="{active2}">2</a>'
        for i in (1, 2):
            n = f"{i:02d}"
            links = nav.format(active1="active" if i == 1 else "", active2="active" if i == 2 else "")
            self.write_page(f"{n}.html", f'<h1>第{i}章 课程{i}</h1>{links}<a href="index.html">目录</a>')

    def write_manifest(self):
        (self.root / "courses.json").write_text(json.dumps(self.manifest, ensure_ascii=False), encoding="utf-8")

    def write_page(self, filename, body):
        (self.root / filename).write_text(f'<!doctype html><html lang="zh-CN"><head><link rel="stylesheet" href="theme.css"></head><body>{body}</body></html>', encoding="utf-8")

    def test_valid_fixture(self):
        self.assertEqual(validate(self.root), [])

    def test_metadata_count_mismatch(self):
        self.manifest["chapterCount"] = 3
        self.write_manifest()
        self.assertIn("chapterCount", " ".join(validate(self.root)))

    def test_broken_local_link(self):
        path = self.root / "01.html"
        path.write_text(path.read_text(encoding="utf-8") + '<a href="missing.html">bad</a>', encoding="utf-8")
        self.assertIn("missing local", " ".join(validate(self.root)))

    def test_duplicate_id(self):
        path = self.root / "index.html"
        path.write_text(path.read_text(encoding="utf-8") + '<p id="same"></p><p id="same"></p>', encoding="utf-8")
        self.assertIn("duplicate id", " ".join(validate(self.root)))

    def test_missing_sidebar_link(self):
        path = self.root / "01.html"
        path.write_text(path.read_text(encoding="utf-8").replace('<a href="02.html" class="">2</a>', ''), encoding="utf-8")
        self.assertIn("sidebar missing", " ".join(validate(self.root)))

    def test_unsafe_chapter_filename(self):
        self.manifest["chapters"][0]["file"] = "../outside.html"
        self.write_manifest()
        self.assertIn("unsafe or invalid", " ".join(validate(self.root)))


if __name__ == "__main__":
    unittest.main()
