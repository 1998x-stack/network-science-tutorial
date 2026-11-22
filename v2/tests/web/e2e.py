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
        # S04/S05: ten independently authored lessons, standalone SVGs, MathML and tested controls.
        for number in ('01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25'):
            page.set_viewport_size({'width':1440,'height':900})
            page.set_content(inline_page(f'apps/web/lessons/{number}.html'))
            assert page.locator('.migrated-article figure').count()>=1
            assert page.locator('.migrated-article img').first.evaluate('(el)=>el.complete&&el.naturalWidth>0')
            assert page.locator('.migrated-article math').count()>=1
            assert page.locator('.migrated-article math').first.evaluate('(el)=>el.getBoundingClientRect().width>0&&el.getBoundingClientRect().height>0')
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
            elif number=='06':
                page.locator('[data-ba-node="E"]').click()
                assert '10%' in page.locator('[data-ba-result]').inner_text()
            elif number=='07':
                page.locator('[data-degree-k="3"]').click()
                assert '12.5%' in page.locator('[data-degree-result]').inner_text()
            elif number=='08':
                page.locator('[data-cent-kind="between"]').click()
                assert '6/10' in page.locator('[data-cent-result]').inner_text()
            elif number=='09':
                page.locator('[data-pr-steps]').evaluate('(el)=>{el.value="1";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-pr-node="B"]').inner_text()=='0.5156'
                assert '1.000000' in page.locator('[data-pr-note]').inner_text()
            elif number=='10':
                page.locator('[data-mod-part="all"]').click()
                assert page.locator('[data-mod-value]').inner_text()=='0.000000'
            elif number=='11':
                page.locator('[data-core-k="2"]').click()
                assert '5 个节点' in page.locator('[data-core-output]').inner_text()
                page.locator('[data-core-k="3"]').click()
                assert '0 个节点' in page.locator('[data-core-output]').inner_text()
            elif number=='12':
                page.locator('[data-sir-m="2"]').click()
                page.locator('[data-sir-beta]').evaluate('(el)=>{el.value="0.5";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert '75.00%' in page.locator('[data-sir-risk-output]').inner_text()
                page.locator('[data-sir-t]').evaluate('(el)=>{el.value="4";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-sir-r]').inner_text()=='4'
                assert page.locator('[data-sir-i]').inner_text()=='1'
            elif number=='13':
                page.locator('[data-cascade-step]').evaluate('(el)=>{el.value="4";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-cascade-count]').inner_text()=='5 / 6'
                page.locator('[data-cascade-rule="1"]').click()
                assert page.locator('[data-cascade-count]').inner_text()=='6 / 6'
            elif number=='14':
                page.locator('[data-game-benefit]').evaluate('(el)=>{el.value="4";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-game-b]').inner_text()=='2.0'
                page.locator('[data-voter-neighbor="C"]').click()
                assert 'C、D、D、D' in page.locator('[data-voter-result]').inner_text()
            elif number=='15':
                page.locator('[data-robust-choice="hub"]').click()
                assert page.locator('[data-robust-r]').inner_text()=='0.167'
                page.locator('[data-overload-cap="6"]').click()
                assert page.locator('[data-overload-fail]').inner_text()=='0'
            elif number=='16':
                page.locator('[data-lp-pair="AE"]').click()
                assert page.locator('[data-lp-cn]').inner_text()=='0'
                assert page.locator('[data-lp-aa]').inner_text()=='0.0000'
                page.locator('[data-lp-pair="AD"]').click()
                assert page.locator('[data-lp-cn]').inner_text()=='2'
                assert page.locator('[data-lp-aa]').inner_text()=='1.8205'
            elif number=='17':
                picture=page.locator('[data-layout-image]')
                previous=picture.get_attribute('src')
                page.locator('[data-layout-mode="circular"]').click()
                assert picture.get_attribute('src')!=previous
                assert picture.evaluate('(el)=>el.complete&&el.naturalWidth>0')
                assert '圆周示意' in page.locator('[data-layout-output]').inner_text()
                page.locator('[data-layout-mode="schematic"]').click()
                assert picture.get_attribute('src')==previous
            elif number=='18':
                page.locator('[data-collection-view="graph"]').click()
                assert page.locator('[data-collection-count]').inner_text()=='4'
                page.locator('[data-collection-view="events"]').click()
                assert page.locator('[data-collection-count]').inner_text()=='6'
            elif number=='19':
                page.locator('[data-multi-mode="flat"]').click()
                assert page.locator('[data-multi-length]').inner_text()=='2'
                page.locator('[data-multi-mode="blocked"]').click()
                assert page.locator('[data-multi-length]').inner_text()=='不可达'
                page.locator('[data-multi-mode="allowed"]').click()
                assert page.locator('[data-multi-length]').inner_text()=='3'
            elif number=='20':
                page.locator('[data-temporal-schedule="scrambled"]').click()
                assert page.locator('[data-temporal-count]').inner_text()=='2 / 4'
                assert page.locator('[data-temporal-arrival]').inner_text()=='不可达'
                page.locator('[data-temporal-schedule="simultaneous"]').click()
                assert page.locator('[data-temporal-count]').inner_text()=='2 / 4'
                page.locator('[data-temporal-schedule="ordered"]').click()
                assert page.locator('[data-temporal-arrival]').inner_text()=='3'
            elif number=='21':
                page.locator('[data-n2v-q]').evaluate('(el)=>{el.value="0.5";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-n2v-d]').inner_text()=='0.500'
                assert '1.000' in page.locator('[data-n2v-note]').inner_text()
            elif number=='22':
                page.locator('[data-gcn-x]').evaluate('(el)=>{el.value="2";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-gcn-output]').inner_text()=='0.8165'
                page.locator('[data-gat-logit]').evaluate('(el)=>{el.value="-1";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-gat-c]').inner_text()=='0.269'
            elif number=='23':
                page.locator('[data-bridge-choice="drop"]').click()
                assert page.locator('[data-bridge-components]').inner_text()=='3'
                assert page.locator('[data-bridge-lcc]').inner_text()=='3 / 7'
            elif number=='24':
                page.locator('[data-label-choice="swap"]').click()
                assert page.locator('[data-label-raw]').inner_text()=='0%'
                assert page.locator('[data-label-aligned]').inner_text()=='100%'
                page.locator('[data-projection-n]').evaluate('(el)=>{el.value="10";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-projection-edges]').inner_text()=='45'
            elif number=='25':
                page.locator('[data-memory-n]').evaluate('(el)=>{el.value="20000";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-memory-dense]').inner_text()=='3200.0 MB'
                page.locator('[data-sampling-leaves]').evaluate('(el)=>{el.value="9";el.dispatchEvent(new Event("input",{bubbles:true}))}')
                assert page.locator('[data-sampling-uniform]').inner_text()=='0.1000'
                assert page.locator('[data-sampling-walk]').inner_text()=='0.5000'
            if number in ('06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25'):
                captures=ROOT/'screenshots'
                captures.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(captures/f'lesson-{number}-desktop.png'),full_page=True)
                page.set_viewport_size({'width':390,'height':840})
                page.screenshot(path=str(captures/f'lesson-{number}-mobile.png'),full_page=True)
                page.set_viewport_size({'width':1440,'height':900})
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
    print('Chromium E2E passed: root portal, V2 reader, first-twenty-five responsive lessons and controls, Graph Lab, comparison, registry and legacy viewer.')

if __name__=='__main__':run()
