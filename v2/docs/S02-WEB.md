# S02 · 课程门户、可视化组件与多模型比较

## 本阶段范围

S02 在 S01 基础上提供 **构建可验证、运行时零依赖的静态 Web 门户**。不启动新 API 服务，不改变科学算法、节点/边/指标含义，不迁移 28 章完整教材正文，不改动原 GitHub 仓库 `main`。

由于当前执行环境无法从 npm registry 安装 Astro/React，选择与目标架构兼容的轻量 HTML + CSS + 可共享 JavaScript 组件，保持 file:// 浏览器预览能力。未来升级 Astro/MDX 时只迁移页面模板，公共 view contract 和 Python artifact 保持不变。目标架构与当前实现技术选择需要明确区分。

## 组件及责任

| 文件 | 责任 | 禁止事项 |
|---|---|---|
| `content/curriculum.json` | 28 章唯一编目 | 不存运行期 UI 状态 |
| `scripts/build_web.py` | 静态构建；生成 28 篇概要/目录/数据资源 | 不把概要标为完整章节 |
| `apps/shared/contract.js` | Artifact v1 结构、唯一节点 ID、简单无向边、值域与规模限制 | 不推测或计算统计指标 |
| `apps/shared/layout.js` | 有界确定性力导向显示坐标 | 不承担科学模型生成 |
| `apps/shared/canvas.js` | Canvas 渲染、节点选择/邻居高亮/缩放/键盘 | 不更改图拓扑 |
| `apps/shared/comparison.js` | 从多次真实 runs 计算均值和样本标准差 | 不生成训练/评测数据 |
| `apps/shared/progress.js` | 读写旧版 localStorage 学习进度 | 不跨域合并私有数据 |
| `apps/web/index.html` | 课程目录、搜索、筛选、勾选完成 | 不硬编码另一份章节列表 |
| `apps/web/lessons/NN.html` | 本章简介和原文链接 | 不声称已完成 S03 内容迁移 |
| `apps/web/lab.html` | 网络结构画布、真实指标与元数据 | 不以 canvas 视觉结果替代数据评测 |
| `apps/web/compare.html` | ER / WS / BA 五随机种子对照 | 不声称显著性、置信区间或因果结论 |
| `apps/web/datasets.html` | 数据来源/许可状态的静态展示 | 不自动抓取外部数据 |
| `apps/graph-lab/` | 旧 Graph Lab 兼容入口，复用 shared view | 不重复维护计算或布局算法 |

## 数据流

```text
content/curriculum.json ── build_web.py ──> apps/web/index.html
                                        └─> apps/web/lessons/*.html
                                        └─> apps/web/data/curriculum.js

Python src/netsci ── scripts/build_samples.py ──> apps/graph-lab/samples.js
           └──── scripts/compare_models.py ──> experiments/model-comparison.json
                                                └─ build_web.py ──> apps/web/data/comparison.js

apps/shared/contract.js → apps/shared/canvas.js ← layout.js
            ↑                       ↑
        apps/web/lab.js       apps/graph-lab/app.js

apps/web/compare.js ← comparison.js ← Python comparison artifacts
```

## 运行

```bash
# 在根目录重建静态课程页面和模型比较资源
python3 scripts/build_web.py

# 验证代码生成产物没有漂移 + 所有相对引用存在
python3 scripts/build_web.py --check
python3 scripts/check_web.py

# Python + Node 纯逻辑测试
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/web/*.test.cjs

# 本地 HTTP 预览（推荐）
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000/apps/web/index.html

# 可直接双击打开 apps/web/index.html 和 apps/graph-lab/index.html。
# 注意 localStorage 以 origin 为作用域，file:// 的跨页面可用性依浏览器实现。

# Chromium 内联资源交互回归（需要 playwright Python 与 Chromium）
python3 tests/web/e2e.py
```

## S02 验收与限制

- Python S01 测试：12 项通过。
- Node JS 新增回归：10 项通过。
- `scripts/build_web.py --check`：34 个构建产物与源码一致。
- Chromium 交互：验证课程搜索与学完标记、模型切换、JSON 错误处理、Canvas 渲染与缩放、表格与图、数据集及移动端布局、旧 Lab 入口。
- **限制**：此环境对 localhost/file:// 的浏览器导航有限制；上述 Chromium 测试将本地文件 CSS、JS 内联到 HTML 进行验证，不能替代 HTTP 完整导航、文件协议及部署端到端测试。S03/CI 在可访问的浏览器环境需要补充真正的路由 E2E。
- **限制**：Graph Lab 支持 <= 3000 节点、<= 60000 边；图规模较大时跳过 O(n²) 力导向，而使用稳定初始布局。大规模 WebGL/LOD 属于后续优化。
- **限制**：新站点本地存储与旧站只有在同源下才能共享；如果使用不同主机、端口或 `file://`，不会自动迁移进度。
- **限制**：比较均值与标准差来自五个种子和固定参数；没有进行显著性检验；图示布局不属于统计分析输入。

## 下一阶段 S03

1. 先建立原 28 个 HTML 的逐章节哈希与代码块清单；修复已确认的科学勘误。
2. 将完整正文转换到 MDX/结构化内容，明确保留段落、公式、代码、图片和原始引用。
3. 教材算法片段不直接复制到 MDX：保存为独立代码源文件，并通过章节配置引用。
4. 每章建立 `objectives`, `prerequisites`, `references`, `labs`，至少提供一个测试或可复现输出。
5. 保留旧 `/01.html` 至 `/28.html` 路径；完成后再开启新的正文入口，不出现空白链接或丢失内容。
