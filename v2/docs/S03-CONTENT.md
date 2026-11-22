# S03 / S04 — 内容迁移与首批审校

根目录 `NN.html` 是当前课程兼容入口和迁移源；`v2/content/lessons/NN.html` 是从 `.main-content` 提取的正文快照；`v2/apps/web/lessons/NN.html` 是静态构建产物。不要手工编辑生成文件。每章证据账本保存在 `v2/content/evidence/NN.json`。

## S03：全量正文迁移

迁移保留章节结构和代码片段，不自动把伪代码改写成可运行 Python，也不把迁移状态当作科学认可。

```bash
python3 v2/scripts/migrate_lessons.py
python3 v2/scripts/build_web.py
python3 v2/scripts/migrate_lessons.py --check
python3 v2/scripts/build_web.py --check
python3 v2/scripts/check_web.py
```

## S04：首批十章独立内容审校

第 01–10 章重写为独立课程文章。每页包含具体问题、完整定义、渐进图解、可访问 MathML、固定依赖的 Python 示例、确定性不变量测试、适用边界和原始参考资料。交互控件用于参数探索或状态切换，默认内容无需 JavaScript 也可理解。

只有当证据账本声明 `reviewed` 且代码块标记为 `language-python` 时，迁移元数据才分别记录章节审校和已测试示例。该状态代表仓库自动化门禁覆盖，不等于完整论文复现或同行评审。

## 自动化验收

```bash
cd v2
python scripts/migrate_lessons.py --check
python scripts/build_web.py --check
python scripts/check_web.py
PYTHONPATH=src python -m unittest discover -s tests -v
node --test tests/web/*.test.cjs
python -m playwright install chromium
python tests/web/e2e.py
```

Chromium E2E 覆盖根课程门户、V2 阅读器、Graph Lab、模型比较、数据集入口，以及首批十章在 1440、768、390、360px 视口下的溢出、图像、MathML 和交互控件。

## S05：第 06–10 章事实核验与交互

新增 BA 权重选择、度频率计数、中心性口径切换、PageRank 逐步迭代和模块度分区比较。每个交互的默认数值由固定的教学图推导，代码示例在 unittest 流水线中实际执行。正式论文结论与教学小图分开标注。

## S06：第 11–15 章信息流、传播、博弈与鲁棒性

各章独立完成问题定义、模型前提、数学公式、可访问 SVG、固定输入的 Python 实验、源论文边界与交互式小图。新增 k-core 逐层剥离、SIR 风险与路径状态、两种同步社会级联、捐赠博弈/Voter 及枢纽删除与容量调整。各章证据账本单独维护，保持根 HTML 与 V2 快照一致。
