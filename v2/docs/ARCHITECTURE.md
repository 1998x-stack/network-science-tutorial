# Network Science Tutorial V2 — 全栈架构与重构蓝图

状态：V2 目标架构设计 + S00 可运行验证骨架。保留 28 章原有 HTML，不对原仓库执行覆盖性操作。

## 0. 产品边界与工程目标

- **Reader（课程门户）**：章节、公式、图解、互动演示、测验、学习进度。
- **Lab（可复现实验）**：确定性算法、固定输入、参数、种子、结果、消融和回归。
- **Dataset（数据资产）**：公开来源、许可证、原始快照、解析规则、校验和、版本化划分。
- **Analysis（科学计算）**：图模型、结构指标、随机生成、传播、检测、嵌入、GNN。
- **Visualization（表达层）**：交互式网络图、统计图、动画、解释图、可下载报告。
- **Assessment（评测层）**：数值正确性、统计稳定性、基线对照、跨算法公平比较。
- **Platform（工程层）**：构建、部署、性能、安全、监控、CI、兼容迁移。

最重要的原则：**教材内容、算法实现、数据集、实验配置、计算结果、交互 UI 都不能相互硬编码。**

## 1. 目标仓库结构

```text
network-science-tutorial/
├── apps/
│   ├── web/                         # Astro + Starlight/MDX 内容与目录
│   │   ├── src/pages/               # 课程、实验、数据集、模型比较、搜索
│   │   ├── src/components/          # LessonHeader, Formula, Quiz, LabEmbed
│   │   ├── src/islands/             # 按需 hydration 的交互模块
│   │   └── public/                  # 图片、静态实验 JSON、兼容入口
│   ├── graph-lab/                   # 独立图形渲染器；首阶段为零依赖静态页面
│   │   ├── index.html
│   │   ├── app.js
│   │   ├── styles.css
│   │   └── samples.js
│   └── api/                         # S04 可选 FastAPI；大图与远程运行时才启用
├── content/
│   ├── curriculum.yaml              # 唯一课程目录；自动生成导航与索引
│   ├── lessons/
│   │   ├── 01-introduction/
│   │   │   ├── index.mdx            # 理论文本 + 交互组件引用
│   │   │   ├── objectives.yaml      # 目标、先修、掌握标准
│   │   │   ├── references.bib       # 文献出处
│   │   │   └── assets/              # 章节图解（非算法输出）
│   │   └── ... 28-final-project/
│   ├── labs/                         # 每实验独立配置与教案
│   │   ├── structure-benchmark/
│   │   │   ├── lab.yaml
│   │   │   ├── README.md
│   │   │   └── questions.yaml
│   │   ├── ranking-community/
│   │   └── embedding-gnn/
│   ├── quizzes/                      # 习题、答案、评分 rubrics
│   └── legacy/                       # 原 01.html...28.html 的审计归档
├── src/netsci/                      # Python 安装包：以 netsci.* 为公开 API
│   ├── core/                         # GraphSchema、节点 ID、图的语义
│   ├── models/                       # ER、WS、BA、configuration、SBM、LFR
│   ├── metrics/                      # 路径、聚类、中心性、同配性、谱指标
│   ├── community/                    # GN、Louvain、Leiden、InfoMap（可选库）
│   ├── dynamics/                     # SIS、SIR、IC、LT、级联失效、意见博弈
│   ├── prediction/                   # CN、AA、RA、Katz、PPR、链路基线
│   ├── embedding/                    # DeepWalk、Node2Vec、struc2vec
│   ├── gnn/                          # GCN、GAT、GraphSAGE（torch extra）
│   ├── datasets/                     # registry、下载器、解析器、数据校验
│   ├── experiments/                  # 配置、runner、基线与 sweep
│   ├── evaluation/                   # metric、bootstrap、泄漏检测
│   ├── visualization/                # 输出数据契约与静态报告构建器
│   ├── utils/                        # RNG、原子文件 I/O、哈希、日志与配置
│   └── cli.py                        # netsci generate / evaluate / inspect
├── data/
│   ├── registry/datasets.json        # 来源、许可、格式、期望统计、校验和
│   ├── raw/                          # 不入 Git；原始只读快照
│   ├── interim/                      # 不入 Git；清洗中间产物
│   └── processed/                    # 不入 Git；图与切分产物
├── experiments/
│   ├── configs/                      # 逐实验 YAML/TOML 配置
│   ├── results/                      # 不入 Git；版本化运行结果
│   ├── golden/                       # 小型黄金输出、容差与回归基线
│   └── reports/                      # 自动生成图表、HTML/CSV/JSON
├── notebooks/                        # 用于探索；不得成为唯一算法实现
├── scripts/                          # 内容迁移、数据下载、样例构建
├── tests/
│   ├── unit/                         # 数学与基础数据结构单测
│   ├── property/                     # 图不变量/随机性质
│   ├── integration/                  # dataset -> model -> report
│   ├── visual/                       # Playwright 截图、交互、无障碍
│   ├── regression/                   # 黄金指标、结果哈希、版本兼容
│   └── performance/                  # 容量、峰值内存、延迟基线
├── benchmarks/                       # 数据集/算法/硬件环境全记录
├── docs/                             # ADR、科学勘误、迁移、技术规范
├── pyproject.toml                     # Python 包与可选依赖
├── pnpm-workspace.yaml                # S02 Web monorepo 才引入
├── .github/workflows/                 # 分级 CI
└── README.md
```

**目录不是微服务列表**。S00-S01 维持单 Python 包和静态站点，避免把研究课程过早做成分布式服务。只有当需要浏览器动态任务、GPU 作业或大图服务时才启用 API/queue/worker。

## 2. 依赖方向和模块契约

```text
curriculum --> lesson page --> LabEmbed ------> artifact (JSON)
                      |                           ^
                figure/notebook                    |
                                                  experiment runner
                                  dataset registry --> load/validate --> graph model
                                                                   |      |
                                                                   v      v
                                                             algorithms -> metrics
                                                                   |
                                                             evaluator + reports
```

**可依赖**：UI -> artifacts、runner -> algorithms/datasets/metrics、experiments -> evaluation。
**不可依赖**：core -> UI、models -> Web API、datasets -> React、GNN -> lesson HTML。
**禁止**：在 HTML 里复制数学算法；用随机画面伪装真实实验指标；自动下载未审核许可数据；用 Notebook 作为唯一可执行实现。

## 3. 唯一的数据与实验协议

每次运行必须记录：experiment_id、algorithm/model、params、seed、dataset_id/version、code revision、dependency lock hash、split_id、metrics、artifact schema version、source provenance、运行状态（成功/失败/跳过）。

- `Graph`：node IDs 要显式且稳定；孤立节点必须保留；声明 directed/weighted/multigraph/temporal/multilayer 语义。
- `Artifact`：带 `schema_version`，含节点/边属性、可视化需要的指标，不允许 UI 重新计算 authoritative metrics。
- `DatasetSplit`：训练/验证/测试划分必须由单独模块生成；时间链路预测需要按时间切分；负采样的分布与种子要冻结。
- `Metric`：含 `name, definition, value, scope, warnings, units`；不连通图平均路径必须标明 LCC 限定或使用全图可达对定义。
- `Prediction`：必须明确定义 task、label、negative universe、transductive/inductive 设定。

**S00 实现范围**：仅支持简单无向图及 `schema_version=1.0.0`。有向、加权、时序、多层图需升级协议，不可静默丢字段。

## 4. 28 章与可执行实验映射

| 章节 | 课程实验 / 编程练习 | 主负责模块 |
|---|---|---|
| 01-02 | 图建模、Euler 路径、邻接表与邻接矩阵互换 | core |
| 03 | 度分布、聚集系数、距离、连通分量 | metrics |
| 04 | ER 连通阈值/巨分量相变 | models + evaluation |
| 05 | WS 重连概率对 C/L 的影响 | models + visualization |
| 06 | BA 增长、度分布和幂律拟合检验 | models + metrics |
| 07 | Gini、二阶矩、同配性、富俱乐部 | metrics |
| 08 | Degree/Betweenness/Closeness/Eigenvector | metrics |
| 09 | PageRank/HITS/PPR、死端处理 | ranking |
| 10 | Modularity / GN / Louvain / Leiden | community |
| 11 | Infomap / overlap / k-core / NMI | community + evaluation |
| 12 | SIS/SIR、阈值、免疫策略 | dynamics |
| 13 | IC/LT、信息级联、传播范围 | dynamics |
| 14 | Voter/Deffuant、复制动力学 | dynamics |
| 15 | random failure vs targeted removal、LCC 曲线 | dynamics + metrics |
| 16 | CN/Jaccard/AA/RA/Katz、严格数据切分 | prediction |
| 17 | force/circular/hierarchical 与布局偏差 | visualization |
| 18 | 原始数据、清洗、许可证、provenance | datasets |
| 19 | Multiplex、supra adjacency、耦合依赖 | core/multilayer |
| 20 | 时间尊重路径、窗口敏感性、动态社团 | core/temporal |
| 21 | DeepWalk/Node2Vec/struc2vec | embedding |
| 22 | GCN/GAT/GraphSAGE Cora 节点分类 | gnn |
| 23 | 完整 Python library API 实战 | core + metrics |
| 24 | Karate/公开合著网络对照 | datasets + community |
| 25 | NX/igraph 峰值内存和耗时对比 | benchmarks |
| 26 | 图推荐/知识图谱/异构图 | gnn + prediction |
| 27 | 数据偏差、动态图与现实应用反例 | lessons + evaluation |
| 28 | 三条端到端 capstone 实验与研究报告 | experiments |

## 5. 三条 Capstone 线路

### A 结构 → 动力学 → 鲁棒性
- 固定 n、接近平均度，比较 ER/WS/BA；不能只固定模型各自的默认参数。
- 计算 `P(k), clustering, LCC, shortest_path_LCC, assortativity`，用多种随机种子汇总均值与置信区间。
- 使用同一 SIR/SIS 参数、接触/更新规则和初始条件，比较 outbreak size、peak、duration。
- 分别模拟随机移除、初始按度移除、每轮重算度攻击；输出 `LCC(f)`、AUC 与效率变化。
- 明确阈值理论所依赖的网络假设，避免把某个模型结论推广到所有网络。

### B 结构特征 → 排序 → 社团 → 链路预测
- Karate 和 LFR 基准；中心性与 PageRank 结果进行已知小图黄金测试。
- 社团包含 Louvain、Leiden、Infomap 和随机基准，记录 modularity、conductance、NMI/ARI（有标签时）。
- 链路预测独立使用时间划分（有时间字段）或固定静态 edge holdout，报告训练图中的连通性变化。
- 正负样本训练/验证/测试显式生成；报告 ROC-AUC、AP、Precision@K 以及分组误差。

### C 随机游走嵌入 → GNN → 节点分类/链路预测
- 公共基准如 Cora/CiteSeer/OGB（按来源许可及版本审核）；训练集索引、split、seed 严格共享。
- transductive 对比：DeepWalk、Node2Vec、简单特征基线、GCN、GAT、GraphSAGE。
- inductive 单独对比：拆分未见节点或子图；不能把 DeepWalk 的纯查表模型当成自然支持 inductive 的模型。
- 消融：无节点属性、无边、邻居采样、深度、隐藏维、游走长度、随机种子。
- 报告 Macro-F1、ROC-AUC/AP（按具体任务）、方差、耗时、峰值显存、置信区间和失败/超时。

## 6. Web / 可视化边界

- **阅读页**：理论、公式、名词解释、测验、章节路线图、引用出处。
- **实验页**：参数面板、运行配置、模型/数据集选择、比较表、结果重放、导出。
- **图形渲染器**：小图 Canvas/SVG、节点选择、邻居高亮、缩放、hover；大图切换 WebGL/LOD/服务器聚合结果。
- **动画**：传播事件时间轴使用离散事件日志重放；不能用 CSS 假动画代替真实状态历史。
- **图表**：结构指标曲线、置信区间、CCDF、攻击曲线、训练指标、消融矩阵。
- **内容组件**：`<GraphDemo/>`, `<ParameterSweep/>`, `<CodeTabs/>`, `<Equation/>`, `<Exercise/>`, `<ExperimentResult/>`，输入必须来自版本化实验 JSON。
- **无障碍与性能**：键盘操作、文本替代、移动端响应、减少动画偏好、图上限、数据和资源懒加载。
- **离线兼容**：保留原 28 章可用的 `file://` 入口；新 standalone Graph Lab 也应可双击打开，生产站点可采用静态构建。

技术选择建议：阅读站优先 Astro/Starlight + MDX；交互组件采用局部 React Islands；小图用 Canvas，超过万节点优先 Sigma.js/WebGL；统计图用 Plotly/ECharts 或 Vega-Lite；Python 分析用 NetworkX / igraph，GNN 才引入 PyTorch/PyG。库只在相关模块启用，避免基础课程依赖 CUDA/GPU。

## 7. 数据集治理

- Registry 为权威来源：id、version、source URL、引用、许可状态、校验和、原始图类型、规模、读取器、推荐任务、PII 状态。
- `raw` 不修改，`interim` 记录清洗参数，`processed` 带 ID 映射、节点/边 schema、拆分指纹。
- 大文件及原始个人数据不入 Git；不承诺未经验证的公开可再分发许可。
- 引入 `DataCard`：网络构造假设、缺失边、采样偏差、时间覆盖、限制与伦理。
- 训练评估优先采用规范化 benchmark splits；训练图中不能保留作为未知链路进行测试的测试边。

## 8. 质量门禁与科研审稿

| 层级 | 检查 | 验收 |
|---|---|---|
| Content | 28章目录、链接、章节目标、引用、公式勘误 | 旧链接 100% 可访问；关键公式审稿 |
| Core | 图不变量、路径、三角形、度数和已知小图黄金值 | pytest/stdlib tests 通过 |
| Model | ER 极端 p、WS 边数、BA 边数、固定种子 | 不变量、确定性通过 |
| Experiment | 种子、数据拆分、样本与负采样、环境与代码版本 | 同环境重复运行可比 |
| Visual | contract、交互、键盘、缩放、节点突出、离线运行 | Playwright 浏览器测试通过 |
| Evaluation | 统计显著性、多个 seeds、baseline、无泄漏 | 评测报告携带证据与限制 |
| Performance | 运行时、峰值内存/显存、图规模与复杂度 | 降级/限制清晰，无 OOM |
| CI | Python lint/test、web typecheck/build、broken links、secret scan | PR 必须 green |

## 9. 逐阶段迁移路线与退出标准

- **S00 冻结旧版与基线（当前开始）**：main 不改动；为 28 个 HTML 建哈希清单，确认 `courses.json`，记录已有勘误；输出迁移库存报告。完成标准：旧站链接与目录没有损坏。
- **S01 Python Core + Experiment Contract（本骨架已部分实现）**：ER/WS/BA/metrics/CLI/JSON/单测。完成标准：可离线生成稳定的可视化数据、六项基础单测通过。
- **S02 Web Shell 与可视化组件**：将 Graph Lab 逐步整合到阅读站；抽离样式系统、图表、路由和章节索引，完成 E2E。完成标准：阅读进度保留、实验结果可离线查看、图表和结果一致。
- **S03 课程内容拆分与核验**：28 章 HTML -> MDX + snippets + labs + exercises；修正 ERRATA；维护原路径重定向/兼容页。完成标准：逐章节内容对齐与公式测试。
- **S04 Dataset Registry + 实验 A**：真实数据、合规下载、结构/传播/鲁棒性联合实验。完成标准：多种子可复现报告与统计置信区间。
- **S05 实验 B**：rank/community/link prediction，独立 evaluator 与泄漏测试。完成标准：基线齐全且协议一致。
- **S06 实验 C**：embedding、GNN，CPU smoke + GPU integration，公平对照。完成标准：独立测试集、多个种子与消融。
- **S07 工程收敛**：按需引入 API/任务队列；可选持久化运行历史；基准、无障碍、文档、科研审查完备。

每阶段必须做到：明确验收结果、迁移前后对照、失败可以回滚，不在一次 PR 中同时更改 28 章内容、算法正确性、Web 外观和依赖管理。

## 10. 当前 S00 原型说明

该 zip 内已包含可以运行的 `src/netsci/core.py`、`models.py`、`metrics.py`、`experiment.py`、`cli.py`、`apps/graph-lab`、`scripts/build_samples.py` 与测试。它是分层设计的首批验证，不是“完整的 28 章源码重构”或“已在 GitHub 提交”。
