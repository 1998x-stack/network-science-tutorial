# Network Science Tutorial V2 · 可运行架构原型

这是针对原仓库 28 章课程的**非破坏性重构起点**，不是覆盖原仓库的完整替代版本。

- [全量重构架构](docs/ARCHITECTURE.md)
- [安全迁移规约](docs/MIGRATION.md)
- [实验与可视化数据契约](docs/CONTRACTS.md)
- [数据集注册表](data/registry/datasets.json)

## 核心代码与实验（Python >=3.10，无运行时第三方依赖）

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m netsci.cli --model er --nodes 80 --p 0.0759493670886076 --seed 42 --output experiments/results/er.json
PYTHONPATH=src python3 -m netsci.cli --model ws --nodes 80 --degree 6 --p 0.08 --seed 42 --output experiments/results/ws.json
PYTHONPATH=src python3 -m netsci.cli --model ba --nodes 80 --attach 3 --seed 42 --output experiments/results/ba.json
```

三个模型结果都遵守相同的 `schema_version=1.0.0` 协议。`average_shortest_path_lcc` 只在最大连通分量上计算。

## 可视化（双击网页即可）

打开 `apps/graph-lab/index.html`。内置 ER/WS/BA 三个真实 Python 生成的网络样例；支持参数概览、缩放、节点悬停与选择、边透明度/节点大小调整、JSON 导入/导出。

```bash
python3 scripts/build_samples.py   # 从核心 Python 代码重新生成离线网页演示数据
```

前端只负责布局和可视化，绝不重新生成网络或“估算”指标。当前实现为单机教学用图查看器，不适合数百万节点的大图。

## 向既有仓库安全集成

请参考 `docs/MIGRATION.md`。**原来的 `index.html` 和 `01.html..28.html` 不应直接删除、覆盖**；这套代码是 S00/S01 原型，不代表 28 章已完成 MDX 内容迁移或 GitHub 已提交。

## 多随机种子结构对比 / 旧站审计

```bash
python3 scripts/compare_models.py --nodes 80 --degree 6 --seeds 11,22,33,44,55 --output experiments/results/model-comparison.json
python3 scripts/inventory_legacy.py --repo /path/to/original/network-science-tutorial --output migration-inventory.json
```

比较脚本以**期望平均度**对齐 ER/WS/BA，输出每个种子的明细、均值与样本标准差，暂不声称统计显著性。旧站审计只读原仓库文件，记录每章的哈希、章节标题和代码块数量。
