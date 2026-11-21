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

## S04：首批五章独立内容审校

第 01–05 章重写为独立课程文章。每页包含具体问题、完整定义、渐进图解、可访问 MathML、固定依赖的 Python 示例、确定性不变量测试、适用边界和原始参考资料。交互控件用于参数探索或状态切换，默认内容无需 JavaScript 也可理解。

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

Chromium E2E 覆盖根课程门户、V2 阅读器、Graph Lab、模型比较、数据集入口，以及首批五章在 1440、768、390、360px 视口下的溢出、图像、MathML 和交互控件。
