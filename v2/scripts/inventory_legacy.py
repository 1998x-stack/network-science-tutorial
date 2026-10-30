"""Non-destructive inventory of an existing 28-chapter HTML course checkout."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path


class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings: list[str] = []
        self.in_heading = False
        self.pre_blocks = 0
        self.inline_styles = 0
        self.inline_scripts = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3"):
            self.in_heading = True
            self.headings.append("")
        elif tag == "pre":
            self.pre_blocks += 1
        elif tag == "style":
            self.inline_styles += 1
        elif tag == "script":
            self.inline_scripts += 1

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3"):
            self.in_heading = False

    def handle_data(self, text):
        if self.in_heading and self.headings:
            self.headings[-1] += text


def build_inventory(root: Path) -> dict:
    chapters = json.loads((root / "courses.json").read_text(encoding="utf-8"))["chapters"]
    result = []
    errors = []
    for ch in chapters:
        filename = ch["file"]
        path = root / filename
        if not path.is_file():
            errors.append(f"missing file: {filename}")
            continue
        content = path.read_bytes()
        parser = AuditParser()
        parser.feed(content.decode("utf-8"))
        actual = parser.headings[0].strip() if parser.headings else ""
        expect = f'第{int(ch["num"])}章 {ch["title"]}'
        if actual != expect:
            errors.append(f"heading mismatch in {filename}: {actual!r} expected {expect!r}")
        result.append({
            "chapter": ch["num"], "file": filename, "title": ch["title"],
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content), "headings": [x.strip() for x in parser.headings],
            "code_blocks": parser.pre_blocks, "style_tags": parser.inline_styles,
            "script_tags": parser.inline_scripts,
        })
    if len(chapters) != 28:
        errors.append(f"expected 28 chapters; manifest has {len(chapters)}")
    return {"schema_version": "1.0.0", "root": str(root), "chapters": result, "errors": errors}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, default=Path("."))
    p.add_argument("--output", type=Path, default=Path("migration-inventory.json"))
    args = p.parse_args()
    result = build_inventory(args.repo.resolve())
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Audited {len(result['chapters'])} chapters; {len(result['errors'])} errors; saved {args.output}")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
