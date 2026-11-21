"""Chromium inline E2E fallback for environments blocking localhost/file navigation.

Loads the actual generated HTML/CSS/JS, then verifies behavior without network requests.
The separate `node --test` checks validate data and scientific invariants.
"""
from __future__ import annotations
import base64
import pathlib
import re
from playwright.sync_api import sync_playwright

ROOT=pathlib.Path(__file__).resolve().parents[2]


def inline_page(relative):
    page=ROOT/relative
    html=page.read_text(encoding='utf-8')
    scripts=re.findall(r'<script defer src="([^"]+)"></script>',html)
    html=re.sub(r'<script defer src="[^"]+"></script>','',html)
    css_files=re.findall(r'<link rel="stylesheet" href="([^"]+)">',html)
    for name in css_files:
        css=(page.parent/name).resolve().read_text(encoding='utf-8')
        html=html.replace(f'<link rel="stylesheet" href="{name}">',f'<style>{css}</style>')
    for name in re.findall(r'<img[^>]+src="([^"]+)"',html):
        asset=(page.parent/name).resolve()
        if asset.is_file():
            encoded=base64.b64encode(asset.read_bytes()).decode('ascii')
            html=html.replace(f'src="{name}"',f'src="data:image/svg+xml;base64,{encoded}"')
    payload='\n'.join('<script>'+((page.parent/name).resolve().read_text(encoding='utf-8')).replace('</script>','<\\/script>')+'</script>' for name in scripts)
    return html.replace('</body>',payload+'</body>')


def run():
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
        page.on('pageerror',lambda exc: errors.append(str(exc)))
        # mock same-origin local storage; about:blank does not grant persistent web storage.
        page.set_content('<body></body>')
        page.evaluate('''() => {const kv=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>kv.get(k)??null,setItem:(k,v)=>kv.set(k,String(v))}});}''')
        page.set_content(inline_page('../index.html'))
        assert page.locator('.lesson').count()==28
        assert '已完成 0 / 28' in page.locator('#progress-count').inner_text()
        page.locator('#chapter-search').fill('PageRank')
        assert page.locator('.lesson:visible').count()==1
        page.locator('#chapter-search').fill('')
        page.locator('[data-filter="生成机制"]').click()
        assert page.locator('.lesson:visible').count()==4
        page.locator('[data-filter="全部"]').click()
        page.set_content(inline_page('apps/web/index.html'))
        assert page.locator('.lesson').count()==28
        assert '28 章' in page.locator('#progress-count').inner_text()
        page.locator('#search').fill('PageRank')
        assert page.locator('.lesson:visible').count()==1
        page.locator('#search').fill('')
        page.locator('[data-filter="生成机制"]').click()
        assert page.locator('.lesson:visible').count()==4
        page.locator('[data-filter="全部"]').click()
        page.locator('.lesson[data-number="04"] input').check()
        assert '已完成 1 / 28' in page.locator('#progress-count').inner_text()
        page.locator('.lesson[data-number="04"] .open-lesson').dispatch_event('click',{'button':1,'ctrlKey':True})
        # Page links are verified in static-generation tests. Do not navigate from about:blank.
        # S04: five independently authored lessons, standalone SVGs, MathML and real controls.
        for number in ('01','02','03','04','05'):
            page.set_viewport_size({'width':1440,'height':900})
            page.set_content(inline_page(f'apps/web/lessons/{number}.html'))
            assert page.locator('.migrated-article figure').count()>=1
            assert page.locator('.migrated-article img').first.evaluate('(el)=>el.complete&&el.naturalWidth>0')
            assert page.locator('.migrated-article math').count()>=1
            for width in (768,390,360):
                page.set_viewport_size({'width':width,'height':840})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+3'), (number,width)
            page.set_viewport_size({'width':1440,'height':900})
            if number=='01':
                page.locator('[data-lesson-action="euler-check"]').click()
                assert '4 个奇度顶点' in page.locator('#euler-result').inner_text()
            elif number=='02':
                page.locator('[data-lesson-action="representation"][data-value="list"]').click()
                assert not page.locator('[data-representation-panel="list"]').is_hidden()
                assert page.locator('[data-representation-panel="matrix"]').is_hidden()
            elif number=='03':
                page.locator('[data-lesson-action="metric"][data-value="clustering"]').click()
                assert '邻居' in page.locator('#metric-result').inner_text()
            elif number=='04':
                page.locator('[data-er-p]').evaluate('(el)=>{el.value="0.1";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-er-degree]').inner_text()=='9.900'
            elif number=='05':
                page.locator('[data-ws-beta]').evaluate('(el)=>{el.value="0.5";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert '中等重连' in page.locator('[data-ws-regime]').inner_text()
            page.emulate_media(media='print')
            assert page.locator('.migrated-article figure').first.is_visible()
            page.emulate_media(media='screen')
        page.set_content(inline_page('apps/web/lab.html'))
        assert page.locator('#metrics .metric').count()==8
        assert 'ER' in page.locator('#experiment-title').inner_text()
        page.locator('#model').select_option('ws')
        assert 'WS' in page.locator('#experiment-title').inner_text()
        assert page.locator('#graph').evaluate('(el)=>el.width>0&&el.height>0')
        page.locator('#zoom-in').click()
        assert page.locator('#error').inner_text()==''
        page.locator('#upload').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"schema_version":"0.0.0"}'})
        page.wait_for_function("document.getElementById('error').textContent.includes('不支持的实验数据协议')")
        assert 'WS' in page.locator('#experiment-title').inner_text()
        page.set_content(inline_page('apps/web/compare.html'))
        assert page.locator('#comparison-table tr').count()==3
        assert page.locator('#plot rect').count()==3
        page.locator('#metric-selector').select_option('mean_degree')
        assert '平均度' in page.locator('#metric-explainer').inner_text()
        page.set_content(inline_page('apps/web/datasets.html'))
        assert page.locator('.dataset-list article').count()==5
        page.set_viewport_size({'width':390,'height':840})
        page.set_content(inline_page('apps/web/index.html'))
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+3')
        page.set_content(inline_page('apps/graph-lab/index.html'))
        assert page.locator('#metrics .metric').count()==8
        page.locator('[data-model="ba"]').click()
        assert 'BA' in page.locator('#chart-title').inner_text()
        assert not errors,errors
        page.set_viewport_size({'width':1440,'height':900})
        page.set_content(inline_page('apps/web/index.html'))
        path=ROOT/'screenshots/s02-web-home.png';path.parent.mkdir(parents=True,exist_ok=True)
        page.screenshot(path=str(path),full_page=True)
        page.set_content(inline_page('apps/web/lab.html'))
        page.screenshot(path=str(ROOT/'screenshots/s02-graph-lab.png'),full_page=True)
        browser.close()
    print('Chromium E2E passed: root portal, V2 reader, first-five responsive lessons and controls, Graph Lab, comparison, registry and legacy viewer.')

if __name__=='__main__':run()
