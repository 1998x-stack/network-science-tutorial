#!/usr/bin/env python3
"""Check the static course catalog and local chapter links (Python stdlib only)."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.active_links: list[str] = []
        self.h1: list[str] = []
        self._heading = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "h1":
            self._heading = True
            self.h1.append("")
        identifier = attributes.get("id")
        if identifier:
            if identifier in self.ids:
                self.duplicate_ids.add(identifier)
            self.ids.add(identifier)
        if tag in ("a", "link", "script", "img", "source"):
            name = "href" if tag in ("a", "link") else "src"
            url = attributes.get(name)
            if url:
                self.links.append((tag, url))
            if tag == "a" and "active" in (attributes.get("class") or "").split():
                self.active_links.append(url or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self._heading = False

    def handle_data(self, data: str) -> None:
        if self._heading and self.h1:
            self.h1[-1] += data


def parse_page(path: Path) -> Page:
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    page.close()
    return page


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "courses.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"courses.json: cannot read valid UTF-8 JSON: {exc}"]
    chapters = manifest.get("chapters") if isinstance(manifest, dict) else None
    if not isinstance(chapters, list) or not chapters:
        return ["courses.json: chapters must be a non-empty array"]
    if manifest.get("chapterCount") != len(chapters):
        errors.append("courses.json: chapterCount must equal chapters length")
    seen: set[str] = set()
    files: set[str] = set()
    for index, chapter in enumerate(chapters, 1):
        if not isinstance(chapter, dict):
            errors.append(f"chapter {index}: metadata must be an object")
            continue
        number, filename, title = chapter.get("num"), chapter.get("file"), chapter.get("title")
        expected = f"{index:02d}"
        if number != expected or filename != expected + ".html":
            errors.append(f"chapter {index}: expected num={expected} and file={expected}.html")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"chapter {index}: missing title")
        topics = chapter.get("topics")
        if not isinstance(topics, list) or not all(isinstance(t, str) and t.strip() for t in topics):
            errors.append(f"chapter {index}: topics must contain non-empty strings")
        if not isinstance(filename, str) or not re.fullmatch(r"[0-9]{2}\.html", filename):
            errors.append(f"chapter {index}: unsafe or invalid filename")
            continue
        if filename in seen:
            errors.append(f"chapter {index}: duplicate file {filename}")
        seen.add(filename)
        files.add(filename)

    pages: dict[str, Page] = {}
    for filename in ["index.html", *sorted(files)]:
        path = root / filename
        if not path.is_file():
            errors.append(f"missing page: {filename}")
            continue
        try:
            page = parse_page(path)
        except (OSError, UnicodeError) as exc:
            errors.append(f"{filename}: cannot read HTML: {exc}")
            continue
        pages[filename] = page
        for identifier in sorted(page.duplicate_ids):
            errors.append(f"{filename}: duplicate id #{identifier}")
        if len(page.h1) != 1:
            errors.append(f"{filename}: expected exactly one h1")
        for tag, url in page.links:
            # Existing first/last chapter use an inert link for the missing previous/next page.
            # Scope this legacy exception narrowly; other JavaScript URLs remain invalid.
            if tag == "a" and filename in ("01.html", "28.html") and url == "javascript:void(0)":
                continue
            parsed = urlsplit(url)
            if parsed.scheme in ("http", "https", "mailto", "tel") or url.startswith("//"):
                continue
            if parsed.scheme or parsed.netloc:
                errors.append(f"{filename}: unsupported link scheme: {url}")
                continue
            if not parsed.path:
                continue  # Check in-page fragment targets separately if that becomes necessary.
            target_path = unquote(parsed.path)
            if target_path.startswith("/"):
                errors.append(f"{filename}: use a relative URL instead of {url}")
                continue
            target = (root / filename).parent / target_path
            if not target.is_file():
                errors.append(f"{filename}: missing local {tag} target: {url}")

    catalog = pages.get("index.html")
    if catalog:
        catalog_links = {urlsplit(url).path for tag, url in catalog.links if tag == "a"}
        for filename in sorted(files - catalog_links):
            errors.append(f"index.html: missing catalog link to {filename}")
    for chapter in chapters:
        if not isinstance(chapter, dict) or chapter.get("file") not in pages:
            continue
        filename = chapter["file"]
        page = pages[filename]
        title = chapter.get("title")
        number = chapter.get("num")
        if isinstance(title, str) and isinstance(number, str) and number.isdecimal():
            expected_h1 = f"第{int(number)}章 {title}"
            if [heading.strip() for heading in page.h1] != [expected_h1]:
                errors.append(f"{filename}: heading differs from courses.json: {expected_h1}")
        if page.active_links != [filename]:
            errors.append(f"{filename}: expected exactly one active navigation link to itself")
        chapter_links = {urlsplit(url).path for tag, url in page.links if tag == "a"}
        for missing in sorted(files - chapter_links):
            errors.append(f"{filename}: sidebar missing chapter link to {missing}")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        print(f"Site check failed: {len(errors)} problem(s)", file=sys.stderr)
        return 1
    print("Site check passed: metadata, chapters, navigation, and local links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
