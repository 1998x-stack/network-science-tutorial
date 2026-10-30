#!/usr/bin/env python3
"""Deterministically extract the 28 legacy lessons, examples and draft assignments.

The source of truth remains repository-root NN.html; generated articles are
read-only snapshots and are intentionally not editorially reviewed.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
START = '<div class="main-content">'
END = '<div class="footer-nav">'
CODE = re.compile(r'<pre[^>]*>\s*<code[^>]*>([\s\S]*?)</code>\s*</pre>', re.I)
HEADINGS = re.compile(r'<h([23])[^>]*>([\s\S]*?)</h\1>', re.I)
TAGS = re.compile(r'<[^>]*>')
H1 = re.compile(r'<h1[^>]*>[\s\S]*?</h1>\s*', re.I)


def article(source: str) -> str:
    """Extract the original author's content, without sidebar or navigation."""
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError('missing or duplicate legacy content markers')
    body = source.split(START, 1)[1].split(END, 1)[0]
    body = H1.sub('', body, count=1).strip() + '\n'
    if not body or re.search(r'<script\b|\bon\w+\s*=|javascript\s*:', body, re.I):
        raise ValueError('unexpected unsafe markup in source article')
    return body


def git_blob_sha(content: str) -> str:
    data = content.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def outline(body: str) -> list[dict]:
    return [{'depth': int(m.group(1)), 'title': html.unescape(TAGS.sub('', m.group(2))).strip()}
            for m in HEADINGS.finditer(body)]


def outputs_for(num: str, source: str, chapter: dict) -> dict[str, str]:
    body = article(source)
    examples = []
    output = {f'content/lessons/{num}.html': body}
    for idx, m in enumerate(CODE.finditer(body), 1):
        sample_id = f'{idx:02d}'
        path = f'content/examples/{num}/{sample_id}.txt'
        code = html.unescape(m.group(1)).replace('\r\n', '\n').strip('\n') + '\n'
        examples.append({'id':sample_id,'path':path,'language':'unclassified','review_status':'not_executed'})
        output[path] = code
    meta = {
        'schema_version':1,'chapter':num,'title':chapter['title'],
        'source_path':f'{num}.html','source_git_blob':git_blob_sha(source),
        'review_status':'migrated_unreviewed','headings':outline(body),'examples':examples,
    }
    output[f'content/lessons/{num}.json'] = json.dumps(meta, ensure_ascii=False, indent=2) + '\n'
    tasks = {
        'schema_version':1,'chapter':num,'status':'draft_not_graded',
        'questions':[
            {'id':'concept','type':'free_response','prompt':f'解释「{chapter["topics"][0]}」的核心假设、含义与适用边界。'},
            {'id':'application','type':'free_response','prompt':f'围绕「{chapter["topics"][-1]}」设计一个能够复现的网络科学实验，说明数据、指标和评估方法。'},
        ],
        'lab':chapter.get('lab'),
    }
    output[f'content/quizzes/{num}.json'] = json.dumps(tasks, ensure_ascii=False, indent=2) + '\n'
    return output


def expected(root: Path=ROOT, repo: Path=REPO) -> dict[str,str]:
    chapters = json.loads((root/'content/curriculum.json').read_text(encoding='utf-8'))['chapters']
    if len(chapters) != 28 or [c['num'] for c in chapters] != [f'{i:02d}' for i in range(1,29)]:
        raise ValueError('curriculum requires 28 ordered chapters')
    files = {}
    for ch in chapters:
        num = ch['num']
        files.update(outputs_for(num, (repo/f'{num}.html').read_text(encoding='utf-8'), ch))
    return files


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true', help='verify tracked snapshots exactly match root originals')
    args = p.parse_args()
    files = expected(); outdated = []
    for relative, content in sorted(files.items()):
        dest = ROOT / relative
        if not dest.is_file() or dest.read_text(encoding='utf-8') != content:
            outdated.append(relative)
            if not args.check:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding='utf-8')
    if outdated and args.check:
        print('Stale lesson artifacts: '+', '.join(outdated))
        return 1
    print(('Verified' if args.check else 'Migrated'), '28 chapters',len(files),'assets')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
