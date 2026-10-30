#!/usr/bin/env python3
"""Build dependency-free static S02 web pages from one curriculum and Python artifacts.

Use --check for CI; no user data is fetched and original HTML chapters are untouched.
"""
import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'apps' / 'web'
BASE = 'https://github.com/1998x-stack/network-science-tutorial/blob/main/'


def esc(text):
    return html.escape(str(text), quote=True)


def js_data(name, value):
    # Avoid script-close injection in classic JS data assets, including untrusted registry labels.
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return f'window.{name} = {payload};\n'


def frame(title, body, prefix='', scripts=(), description='网络科学可复现课程与实验平台'):
    nav = f'''<header class="topnav shell"><a class="brand" href="{prefix}index.html"><span class="brand-mark">◉</span><span>NETWORK SCIENCE<small>LEARN · EXPERIMENT · VERIFY</small></span></a>
    <nav class="navlinks" aria-label="主导航"><a href="{prefix}index.html">课程</a><a href="{prefix}lab.html">Graph Lab</a><a href="{prefix}compare.html">模型比较</a><a href="{prefix}datasets.html">数据集</a></nav></header>'''
    js = ''.join(f'<script defer src="{prefix}{esc(path)}"></script>' for path in scripts)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(description)}"><title>{esc(title)} | Network Science</title><link rel="stylesheet" href="{prefix}site.css">{js}</head>
<body>{nav}<main class="shell">{body}</main><footer class="footer shell">Network Science Tutorial V2 · S02 展示层 · 计算结果来自 Python，不在浏览器重算科研指标。<br>原 28 章保留在上游仓库，正文拆分迁移属于 S03。</footer></body></html>\n'''


def homepage(chapters):
    groups = list(dict.fromkeys(c['group'] for c in chapters))
    items = []
    for c in chapters:
        items.append(f'''<article class="lesson" data-number="{esc(c['num'])}" data-group="{esc(c['group'])}"><div class="lesson-top"><span class="lesson-num">CH {esc(c['num'])}</span><span class="tag">{esc(c['group'])}</span></div><h3>{esc(c['title'])}</h3><p>{esc(c['summary'])}</p><div class="lesson-bottom"><a class="open-lesson" href="lessons/{c['num']}.html" aria-label="阅读第{int(c['num'])}章概要">阅读概要 ↗</a><label class="check"><input type="checkbox" aria-label="完成第{int(c['num'])}章">完成</label></div></article>''')
    filters = ''.join(f'<button class="filter" data-filter="{esc(x)}" aria-pressed="{str(x == "全部").lower()}">{esc(x)}</button>' for x in ['全部', *groups])
    orbit = '''<svg role="img" aria-label="从中心枢纽辐射到社团的示意网络" viewBox="0 0 440 215"><g stroke="#467c95" stroke-width="1.4" opacity=".75"><path d="M70 80 135 55 190 82 245 56 325 85 385 43M70 80 107 152 190 82 232 158 325 85 359 151M135 55 107 152 232 158 245 56 359 151 385 43M190 82 325 85M107 152 359 151M70 80 232 158M135 55 325 85" fill="none"/></g><g fill="#6de3c6"><circle cx="70" cy="80" r="5"/><circle cx="135" cy="55" r="7"/><circle cx="190" cy="82" r="11"/><circle cx="245" cy="56" r="4"/><circle cx="325" cy="85" r="10"/><circle cx="385" cy="43" r="5"/><circle cx="107" cy="152" r="6"/><circle cx="232" cy="158" r="5"/><circle cx="359" cy="151" r="8"/></g></svg>'''
    body = f'''<section class="hero"><div><span class="pill">28 章 · 网络科学 · 可复现实验</span><h1>从理解网络，<br>到<span>验证复杂系统</span>。</h1><p class="lead">图论、随机网络、中心性、传播动力学、网络嵌入与图神经网络。通过独立的 Python 算法和版本化实验数据，让教材与可视化真实对齐。</p><div class="cta"><a class="btn" href="#curriculum">探索课程目录 →</a><a class="btn secondary" href="lab.html">打开 Graph Lab</a><a id="resume" class="btn secondary" href="index.html" hidden>继续上次阅读</a></div><p id="progress-count" class="small muted" aria-live="polite">学习进度加载中</p></div><aside class="hero-mock"><div class="eyebrow">TOPOLOGY EXPLORER / S02</div><div class="hero-orbit">{orbit}</div><div class="statrow"><div class="stat"><strong>28</strong><span>课程章节</span></div><div class="stat"><strong>3</strong><span>生成模型</span></div><div class="stat"><strong>5</strong><span>随机种子</span></div></div></aside></section>
    <section class="section" aria-label="实验模块"><div class="section-head"><div><span class="eyebrow">PRACTICAL LABS</span><h2>理论与实验，同步深入</h2></div><span class="small muted">同源 JSON · 固定种子 · 可检查结果</span></div><div class="grid"><div class="feature-card"><span class="symbol">◎</span><h3>交互式网络图</h3><p>使用真实 ER / WS / BA 运行结果，观察节点关系、度数与全图结构。</p><a href="lab.html">进入实验画布 →</a></div><div class="feature-card"><span class="symbol">▥</span><h3>模型多种子比较</h3><p>按相近的期望平均度对齐模型，在可追溯数据上比较统计指标。</p><a href="compare.html">查看结构比较 →</a></div><div class="feature-card"><span class="symbol">▤</span><h3>数据与来源治理</h3><p>区分合成数据和待审核的外部数据集，避免隐式下载或误报许可证。</p><a href="datasets.html">查看数据注册表 →</a></div></div></section>
    <section id="curriculum" class="section"><div class="section-head"><div><span class="eyebrow">COURSE CURRICULUM</span><h2>完整的 28 章知识路线</h2><p class="muted small">S02 提供 28 章概要；完整正文保留在原仓库，S03 将完成逐章迁移。</p></div></div><div class="controls"><label class="sr-only" for="search">搜索章节</label><input id="search" type="search" class="search" placeholder="搜索章节、主题或关键词…" autocomplete="off">{filters}</div><div class="lesson-grid">{''.join(items)}</div><div class="empty" id="no-results" hidden>没有找到匹配的章节，请调整搜索条件。</div></section>'''
    return frame('课程首页',body,scripts=('data/curriculum.js','../shared/progress.js','app.js'))


def lesson(ch,prev_ch,next_ch):
    num=ch['num']; topics=''.join(f'<span>{esc(t)}</span>' for t in ch['topics']);
    other=[]
    if prev_ch:other.append(f'<a href="{prev_ch["num"]}.html">← 第{int(prev_ch["num"])}章</a>')
    if next_ch:other.append(f'<a href="{next_ch["num"]}.html">第{int(next_ch["num"])}章 →</a>')
    lab={'structure':('lab.html','打开网络结构实验'),'compare':('compare.html','打开统计比较实验')}.get(ch.get('lab'))
    body=f'''<div class="article"><section class="subhero"><span class="eyebrow">CHAPTER {num} / {esc(ch['group'])}</span><h1>第{int(num)}章 · {esc(ch['title'])}</h1><p class="lead">{esc(ch['summary'])}</p><div class="topics">{topics}</div></section><div class="notice"><strong>章节状态：S02 概要版。</strong> 原版教材内容尚未迁移，下面提供本章导学、原文链接及适配实验；避免将摘要误认为全章正文。</div><section class="panel"><h2>本章学习重点</h2><p>{esc(ch['summary'])}</p><p class="muted">建议围绕以下主题理解定义、数学假设、适用范围和验证方式：</p><div class="topics">{topics}</div><h2>原始章节</h2><p>原始 HTML 在独立仓库中保存。点击下方链接可以查看 GitHub 中的完整正文源文件；离线时则请使用随原仓库保存的旧版 01–28.html。</p><a class="btn secondary" target="_blank" rel="noopener noreferrer" href="{BASE}{num}.html">查看原始章节 →</a></section><section class="section"><h2>可执行配套实践</h2>{f'<p class="muted">本章提供与现有 Python 实验结果对齐的交互入口。</p><a class="btn" href="../{lab[0]}">{lab[1]} →</a>' if lab else '<p class="muted">相应的独立算法实验、习题及黄金测试计划在 S03–S06 阶段按课程映射逐步接入。</p>'}</section><div class="chapter-nav">{''.join(other)}</div><p><a href="../index.html#curriculum">← 返回课程目录</a></p></div>'''
    return frame(f'第{int(num)}章 {ch["title"]}',body,prefix='../')


def lab_page():
    body='''<section class="subhero"><span class="eyebrow">GRAPH LAB / S02</span><h1 id="experiment-title">ER · 随机网络</h1><p class="muted">网络由 Python S01 生成，Canvas 只负责布局和交互。导入文件经严格的简单无向图协议校验。</p></section>
    <div class="two-col"><aside class="panel"><span class="eyebrow">EXPERIMENT SETTINGS</span><h2>实验数据</h2><div class="form-field"><label for="model">选择模型</label><select id="model"><option value="er">ER 随机网络</option><option value="ws">WS 小世界</option><option value="ba">BA 优先连接</option><option value="custom">自定义导入</option></select></div><div class="form-field"><label for="upload">导入实验 JSON（≤5MB）</label><input id="upload" type="file" accept=".json,application/json"></div><p id="error" role="alert" class="error" aria-live="polite"></p><hr style="border:0;border-top:1px solid var(--line);margin:22px 0"><h2>显示控制</h2><div class="form-field"><label for="size">节点大小 <output id="size-value">1.0×</output></label><input id="size" type="range" min="5" max="22" value="10"></div><div class="form-field"><label for="edges">边透明度 <output id="edge-value">23%</output></label><input id="edges" type="range" min="0" max="100" value="23"></div><div class="rowbtns"><button id="reset">重置</button><button id="export">导出 JSON</button></div><p class="muted small">支持滚轮缩放、悬停、点击邻居、方向键平移与 +/- 缩放。</p></aside><section class="panel"><div class="section-head"><div><span class="eyebrow">NETWORK CANVAS</span><h2>拓扑探索</h2></div><div class="rowbtns"><button id="zoom-out" aria-label="缩小">−</button><button id="zoom-in" aria-label="放大">＋</button></div></div><div class="graph-frame"><canvas id="graph"></canvas><div id="tip" class="graph-tip" hidden></div><span class="graph-hint">点击节点查看邻居 · 鼠标滚轮缩放</span></div><p id="selection" class="muted small" aria-live="polite">选择画布节点，可查看其邻居。</p></section><aside class="panel"><span class="eyebrow">AUTHORITATIVE METRICS</span><h2>结构指标</h2><div class="metric-list" id="metrics"></div><h2>实验元数据</h2><dl id="metadata" class="metadata"></dl><div class="notice">最大分量平均路径仅针对最大连通分量计算。</div></aside></div><div class="notice">该页面不会修改节点、边或重算权威统计指标。当前协议只支持简单无向图；自定义有向、加权或多重图须在后续版本升级协议。</div>'''
    return frame('Graph Lab 网络结构实验',body,scripts=('../shared/contract.js','../shared/layout.js','../shared/canvas.js','../graph-lab/samples.js','lab.js'))


def compare_page():
    options=''.join(f'<option value="{key}">{label}</option>' for key,label in [('mean_local_clustering','平均聚集系数'),('mean_degree','平均度'),('global_transitivity','全局传递性'),('average_shortest_path_lcc','最大分量平均路径'),('largest_component_fraction','最大分量占比')])
    body=f'''<section class="subhero"><span class="eyebrow">MODEL COMPARISON / REPRODUCIBLE</span><h1>ER / WS / BA 结构对照</h1><p class="lead">基于同一节点规模和接近相等的期望平均度，使用多个随机种子比较拓扑结构，而非比较三张随机示意图片。</p></section><section class="panel"><div class="section-head"><div><span class="eyebrow">EXPERIMENT RESULTS</span><h2>多种子结构指标</h2></div><div class="form-field"><label for="metric-selector">观察指标</label><select id="metric-selector">{options}</select></div></div><p id="plot-error" class="error" role="alert"></p><div class="plot"><svg id="plot" viewBox="0 0 920 282" role="img" aria-label="ER WS BA 对照图"></svg></div><p id="metric-explainer" class="muted small"></p><div class="table-scroll"><table><thead><tr><th>模型</th><th>样本均值</th><th>样本标准差</th><th>有效种子数</th></tr></thead><tbody id="comparison-table"></tbody></table></div></section><div class="notice">对照说明：ER 的平均度在期望上匹配，BA 有有限尺寸初始图偏差；这些是描述性统计结果，不能从图表直接推断统计显著性或因果效应。</div>'''
    return frame('结构模型比较',body,scripts=('../shared/comparison.js','data/comparison.js','compare.js'))


def datasets_page(data):
    cards=[]
    for d in data['datasets']:
        source = d.get('source_url');link=f'<a href="{esc(source)}" target="_blank" rel="noopener noreferrer">来源文档 ↗</a>' if source else '<span class="small muted">由项目内生成器构造</span>'
        cards.append(f'''<article class="panel"><span class="eyebrow">{esc(d['source_kind'])} / {esc(d['version'])}</span><h2>{esc(d['id'])}</h2><p class="muted">{esc(d.get('description','外部数据集；待完成来源及许可证审查。'))}</p><p class="small">许可证状态：<strong>{esc(d['license_status'])}</strong></p><p class="small muted">适用实验：{esc(' · '.join(d['recommended_tasks']))}</p>{link}</article>''')
    return frame('数据集注册表','<section class="subhero"><span class="eyebrow">DATA GOVERNANCE</span><h1>数据集与来源</h1><p class="muted">只有合成数据内置于演示。外部数据仅保存元数据，不自动下载、分发，也不暗示已通过许可审查。</p></section><section class="dataset-list">'+''.join(cards)+'</section><div class="notice">原始数据、清洗变换、许可审核、训练切分指纹属于 S04；S02 只提供可检索的静态注册视图。</div>')


def generated():
    curriculum=json.loads((ROOT/'content/curriculum.json').read_text(encoding='utf-8'))
    chapters=curriculum['chapters']; assert len(chapters)==28
    assert len(set(c['num'] for c in chapters))==28
    assert [c['num'] for c in chapters]==[f'{i:02d}' for i in range(1,29)]
    comparison=json.loads((ROOT/'experiments/model-comparison.json').read_text(encoding='utf-8'))
    datasets=json.loads((ROOT/'data/registry/datasets.json').read_text(encoding='utf-8'))
    outputs={'index.html':homepage(chapters),'lab.html':lab_page(),'compare.html':compare_page(),'datasets.html':datasets_page(datasets),'data/curriculum.js':js_data('NETSCI_CURRICULUM',curriculum),'data/comparison.js':js_data('NETSCI_COMPARISON',comparison)}
    for i,c in enumerate(chapters):outputs[f'lessons/{c["num"]}.html']=lesson(c,chapters[i-1] if i else None,chapters[i+1] if i+1<len(chapters) else None)
    return outputs


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true',help='Check generated files without modifying them');args=p.parse_args()
    outputs=generated();changed=[]
    for name,content in outputs.items():
        path=WEB/name
        if not path.exists() or path.read_text(encoding='utf-8')!=content:
            changed.append(name)
            if not args.check:
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content,encoding='utf-8')
    if changed and args.check:
        print('Out-of-date generated files:',', '.join(changed));return 1
    print(('Validated' if args.check else 'Generated'),len(outputs),'web outputs');return 0

if __name__=='__main__':raise SystemExit(main())
