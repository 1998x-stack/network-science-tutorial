# 网络科学教程｜从连接关系理解复杂系统

一套 **28 章中文网络科学课程**，覆盖图论、网络度量、随机网络、小世界与无标度结构、中心性、社团检测、传播动力学、网络表示学习、图神经网络和综合实践。

课程以独立 HTML 页面发布。正文从具体问题出发，明确模型假设、公式含义、可运行示例、适用边界和原始参考资料。前二十五章已完成第一轮内容重构与证据审校；其余章节保留既有内容，按相同质量门槛逐批升级。

## 在线入口

- GitHub Pages：<https://1998x-stack.github.io/network-science-tutorial/>
- 仓库：<https://github.com/1998x-stack/network-science-tutorial>
- 交互式 Graph Lab：<https://1998x-stack.github.io/network-science-tutorial/v2/apps/web/lab.html>
- ER / WS / BA 模型比较：<https://1998x-stack.github.io/network-science-tutorial/v2/apps/web/compare.html>

Pages 由 GitHub Actions 从主分支部署。首次启用时请在 Settings → Pages 确认 Source 为 GitHub Actions；部署完成后再访问在线入口。

## 快速开始

无需安装依赖即可阅读静态课程。克隆仓库后直接打开 `index.html`，或在仓库根目录运行：

```bash
python3 -m http.server 8000
```

浏览器访问 <http://localhost:8000/>。Graph Lab 和模型比较页面也可在本地服务器下打开。目录搜索和学习进度在浏览器本机运行；进度保存在当前浏览器的 `localStorage`，不会自动跨设备同步。

## 课程路线

| 章节 | 主题 | 主要问题 |
|---|---|---|
| 01 | 网络科学导论 | 为什么不同系统可以用同一种关系模型描述？ |
| 02 | 图论基础 | 如何定义节点、边、路径、连通性和图的表示？ |
| 03 | 网络基本度量 | 如何量化连接数量、路径距离和局部聚集？ |
| 04 | 随机网络模型 | 独立随机连边会产生哪些整体结构和阈值？ |
| 05 | 小世界网络 | 少量捷径如何缩短路径并保留局部团簇？ |
| 06–07 | 网络异质性与无标度结构 | 增长、优先连接和度分布如何解释枢纽？ |
| 08–11 | 中心性与社团检测 | 节点重要性和群体结构如何定义、比较？ |
| 12–16 | 动态与预测 | 传播、博弈、鲁棒性和链路预测如何建模并避免泄漏？ |
| 17–22 | 数据、网络层与学习 | 如何可视化、采集并保持关系层和事件时间的语义？ |
| 23–28 | 工程实践 | 如何用 Python、公开数据和图模型完成分析项目？ |

每一章都是独立入口。读者无需先读完上一章才能理解当前章节；必要概念会在本页重新定义，前置知识只作为延伸链接。

## 仓库结构

```text
.
├── index.html                    # GitHub Pages 主课程门户
├── 01.html ... 28.html           # 兼容离线阅读的课程原文入口
├── assets/lessons/               # 首批课程的独立 SVG 图解
├── courses.json                  # 根目录课程目录元数据
├── ERRATA.md                     # 已确认的科学勘误与修订状态
├── AGENTS.md                     # 后续内容编辑与审校规范
├── docs/                         # 内容架构与迁移约定
├── scripts/                      # 根站点结构与链接检查
├── tests/                        # 根站点检查器回归测试
├── .github/workflows/            # 根站点检查与 Pages 部署
└── v2/
    ├── content/lessons/          # 根章节确定性迁移正文快照
    ├── content/evidence/          # 每章事实与数据的证据账本
    ├── content/examples/          # 从章节提取的代码示例
    ├── content/quizzes/           # 草拟练习题
    ├── apps/web/                  # 课程阅读器、Graph Lab、比较页
    ├── apps/shared/               # 可复用的进度与交互逻辑
    ├── src/netsci/                # Python 图模型与指标实现
    ├── experiments/              # 固定参数和随机种子的实验产物
    ├── scripts/                   # 迁移、构建和静态检查
    └── tests/                     # Python、JavaScript 与浏览器回归测试
```

### 内容来源与构建关系

- 根目录 `NN.html` 是兼容阅读入口，也是 S03 迁移流程的原始来源。
- `v2/content/lessons/NN.html`、元数据和代码摘录由 `v2/scripts/migrate_lessons.py` 确定性生成；不要直接编辑生成快照。
- `v2/apps/web/` 页面由 `v2/scripts/build_web.py` 从课程目录、实验结果和迁移正文生成。
- 第 1–25 章的证据账本位于 `v2/content/evidence/`。这些章节包含独立 SVG、MathML、交互控件、可运行代码和参考文献。
- 其余章节的迁移状态不代表科学审校完成；请查看每章 JSON 的 `review_status`。

## 开发与质量检查

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_site.py .
cd v2
python3 scripts/migrate_lessons.py --check
python3 scripts/build_web.py --check
python3 scripts/check_web.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/web/*.test.cjs
python3 -m playwright install chromium
python3 tests/web/e2e.py
```

静态检查验证文件、章节导航、链接和构建快照，不等于科学审稿；数值单测验证公式与图不变量，不等于真实世界数据复现；Chromium E2E 验证指定视口与控件行为，未执行的设备不得标为通过。

## 逐批内容审校：第 01–25 章

| 章节 | 本轮处理 |
|---|---|
| 01 | 校准七桥问题的四个奇度顶点，重建网络建模的三层视角 |
| 02 | 补齐图类型、邻接表示、握手定理、连通性和树 |
| 03 | 区分平均聚集系数、全局传递性与 LCC 路径口径 |
| 04 | 区分 G(n,p)/G(n,m)、巨分量阈值与全图连通阈值 |
| 05 | 校准 Milgram 完成链统计、WS 重连机制和可导航性边界 |
| 06 | BA 增长、优先连接概率、有限规模幂律解释边界 |
| 07 | 全节点度分布、分布矩、幂律检验与度同配性 |
| 08 | 度、介数和特征向量中心性的不同定义与桥梁例子 |
| 09 | 有向随机游走、悬挂节点、随机跳转和 HITS 对比 |
| 10 | 模块度手算、Girvan–Newman、Louvain 与分辨率限制 |
| 11 | 信息流最短编码、重叠社团、k-core 精确剥离与适用边界 |
| 12 | SIR/SIS 状态机、独立接触概率、SIR 渗流与 SIS HMF 阈值区分 |
| 13 | 简单/复杂传播、同步阈值级联、社会强化与弱关系限制 |
| 14 | 捐赠博弈一轮收益、Voter 中性复制、有界信任连续意见 |
| 15 | 星形/路径移除、剩余 LCC 占比、渗流与负载级联区别 |
| 16 | CN / Jaccard / Adamic–Adar、时间外预测、候选池与结构泄漏 |
| 17 | 布局与拓扑的区别、圆周与人工布局、力导向公式、图形编码 |
| 18 | 事件源数据、方向/去重/自环语义、缺失偏差与数据隐私 |
| 19 | multiplex 节点—层状态、supra-adjacency 与跨层可达性 |
| 20 | 时间尊重路径、严格递增事件顺序、最早到达及静态聚合陷阱 |
| 21 | DeepWalk 窗口目标、node2vec 二阶转移、struc2vec 结构角色与未来边泄漏 |
| 22 | GCN 对称归一化、GAT 邻域 softmax、GraphSAGE 采样、过平滑和过压缩 |
| 23 | NetworkX 图类型、孤立点、桥与分量、BFS 与 API 交叉验证 |
| 24 | Karate Club 34/78 来源、社区标签置换、ca-GrQc 合著投影与隐私边界 |
| 25 | 稀疏 CSR 存储、复杂度、星形图采样偏差、igraph/Neo4j/分布式选型 |

## 参考文献与许可

课程优先链接原始论文、教材和官方 API 文档。图解由本项目独立绘制；不复制第三方文章的文字、图像或代码。仓库未声明覆盖全部历史素材的通用许可证；再分发前请检查各来源许可并补充项目许可证。

## 第五批：21–25 极深度可视化与科学审计（2026-11-22）

第 21–25 章均完成完整 HTML 重写、原始资料定位、每篇至少六项证据论断、原创 SVG 双图、MathML、真实离线 JS 交互及可复算 Python 示例。V2 阅读器内容由 `v2/scripts/migrate_lessons.py`、`v2/scripts/build_web.py` 从根目录确定性生成，不单独编辑快照。所有论文分数/真实数据集统计与教学模拟分开标注。

实验边界：21–22 的 Python 核对纯数值，不代表训练了 DeepWalk/GNN；23 的 NetworkX、24 的两类置换与 25 的内存公式为可复算模型，未声称在大型社交数据集进行端到端 benchmark。25 的 CSR 理论大小不包括 Python 容器开销、激活或算法工作区。

```bash
cd v2
python scripts/migrate_lessons.py --check
python scripts/build_web.py --check
PYTHONPATH=src python -m unittest discover -s tests -v
node --test tests/web/*.test.cjs
python tests/web/e2e.py
```
