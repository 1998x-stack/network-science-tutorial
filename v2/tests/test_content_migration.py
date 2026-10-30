"""S03 content migration checks independent from legacy content editorial correctness."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'migrate_lessons.py'
spec = importlib.util.spec_from_file_location('migrate_lessons', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SAMPLE = '''<!DOCTYPE html><html lang="zh-CN"><div class="sidebar">navigation</div>
<div class="main-content"><h1>第1章 网络科学导论</h1>
<p>正文 &amp; 课程</p><h2>数学 &amp; 图</h2><p>A &lt; B</p>
<table><tr><td>test</td></tr></table><pre><code>print(&quot;hello&quot;)\nprint(1 &lt; 2)</code></pre>
<div class="highlight"><strong>提示</strong> 内容</div>
<div class="footer-nav"><a href="02.html">下一章</a></div></div></html>'''
CHAPTER = {'title':'网络科学导论','topics':['图论','网络度量'],'lab':'structure'}

class MigrationTests(unittest.TestCase):
    def test_preserves_body_and_removes_navigation(self):
        article = mod.article(SAMPLE)
        self.assertIn('正文 &amp; 课程', article)
        self.assertIn('<table>', article)
        self.assertNotIn('下一章', article)
        self.assertNotIn('<h1>', article)
        self.assertEqual(mod.article(SAMPLE), article)

    def test_artifacts_preserve_unescaped_original_code(self):
        outputs = mod.outputs_for('01', SAMPLE, CHAPTER)
        self.assertEqual(outputs['content/examples/01/01.txt'], 'print("hello")\nprint(1 < 2)\n')
        meta = json.loads(outputs['content/lessons/01.json'])
        self.assertEqual(meta['source_git_blob'],mod.git_blob_sha(SAMPLE))
        self.assertEqual(meta['headings'],[{'depth':2,'title':'数学 & 图'}])
        self.assertEqual(len(meta['examples']),1)
        self.assertEqual(meta['review_status'],'migrated_unreviewed')
        self.assertEqual(json.loads(outputs['content/quizzes/01.json'])['status'],'draft_not_graded')

    def test_reject_unsafe_markup(self):
        for payload in ['<script>alert(1)</script>','<img onerror="alert(1)">', '<a href="javascript:alert(1)">']:
            with self.assertRaises(ValueError):
                mod.article(SAMPLE.replace('<p>A &lt; B</p>',payload))

    def test_strict_source_markers(self):
        with self.assertRaises(ValueError): mod.article('<h1>Bad</h1>')

    def test_root_reproducibility_when_available(self):
        if not all((mod.REPO/f'{i:02d}.html').is_file() for i in range(1,29)):
            self.skipTest('full original repository absent in local scaffold; checked in GitHub CI')
        outputs = mod.expected()
        self.assertEqual(sum(p.startswith('content/lessons/') and p.endswith('.html') for p in outputs),28)
        self.assertEqual(sum(p.startswith('content/quizzes/') for p in outputs),28)
        self.assertTrue(all((mod.ROOT / p).read_text(encoding='utf-8') == content for p,content in outputs.items()))

if __name__=='__main__':unittest.main()
