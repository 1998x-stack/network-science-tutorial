#!/usr/bin/env python3
"""Static page integrity checks using only stdlib; no dependencies or network."""
from __future__ import annotations
import html.parser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'apps/web'

class Links(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self, tag, attrs):
        fields=dict(attrs)
        if tag in ('a','script','link','img'):
            prop='src' if tag in ('script','img') else 'href'
            if fields.get(prop):self.urls.append(fields[prop])

def main():
    files=[WEB/'index.html',WEB/'lab.html',WEB/'compare.html',WEB/'datasets.html',*(WEB/'lessons').glob('*.html'),ROOT/'apps/graph-lab/index.html']
    errors=[]
    if len(list((WEB/'lessons').glob('*.html')))!=28:errors.append('lesson summaries count is not 28')
    for page in files:
        if not page.exists():errors.append(str(page)+' missing');continue
        parser=Links();parser.feed(page.read_text(encoding='utf-8'))
        for u in parser.urls:
            parsed=urlsplit(u)
            if parsed.scheme in ('https','mailto') or u.startswith('#'):continue
            if parsed.scheme or parsed.netloc or parsed.path.startswith('/'):
                errors.append(f'{page.relative_to(ROOT)}: unsupported URL {u}');continue
            if parsed.path:
                target=(page.parent/unquote(parsed.path)).resolve()
                if not target.is_relative_to(ROOT.resolve()):errors.append(f'{page.name}: path escapes project root {u}')
                elif not target.is_file():errors.append(f'{page.relative_to(ROOT)}: broken link {u}')
    for e in errors:print('ERROR:',e,file=sys.stderr)
    if errors:return 1
    print(f'Static link check passed ({len(files)} pages including legacy viewer)')
    return 0
if __name__=='__main__':raise SystemExit(main())
