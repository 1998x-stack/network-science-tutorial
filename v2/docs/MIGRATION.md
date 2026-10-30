# 旧课程安全迁移操作规则

1. 克隆原仓库并创建 `refactor/network-science-v2` 分支。确认 28 个 `01.html..28.html` 和 `courses.json` 完好，先运行原 `python3 scripts/check_site.py .` 与原 tests。
2. 将本骨架**作为新文件**拷入原仓库：`src/netsci/`、`apps/graph-lab/`、新增 `docs/`、`data/registry/`、`scripts/build_samples.py`、`pyproject.toml`；不要覆盖旧 `index.html`、`theme.css` 或 `courses.json`，也不要覆盖原 `tests/test_site.py`。
3. 额外运行 `PYTHONPATH=src python3 -m unittest discover -s tests -v`。运行 `PYTHONPATH=src python3 -m netsci.cli --model ws --nodes 80 --degree 6 --p 0.08 --seed 42 --output experiments/results/ws.json`。
4. 双击 `apps/graph-lab/index.html` 检查页面；三个示例数据在 `samples.js` 中，可用 Python `scripts/build_samples.py` 生成。用上传按钮导入导出的 JSON。
5. S03 时逐章把原 HTML 的正文迁移到 MDX；原 `01.html...28.html` 暂时保留，直到路由兼容和页面内容回归验证完成。
6. S03 内容审校优先处理 `ERRATA.md` 记录的 Euler 奇度顶点错误、ER 两种分布区别和不严谨的网络统计表述。
7. PR 里分别标记：正文变化、数学修订、算法实现、UI 改造、数据集变化。不要在没有独立验收结果时删掉旧站入口。

## 架构治理约定

- 旧站属于 `legacy` 只读兼容层，不允许新功能反向依赖其中的脚本。
- 实验的输入和输出为版本化数据协议，不准直接从 UI 调用任意研究代码。
- Python 包内禁止依赖 `apps/web` 资源；课程 Markdown 不承载算法真正实现。
- 无法在 CI 复现的图表不作为科学结论的唯一证据。
