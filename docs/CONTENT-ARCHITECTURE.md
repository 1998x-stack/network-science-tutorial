# 内容架构与迁移约定

根目录 `index.html` 是 GitHub Pages 主课程门户，链接到根目录 `01.html..28.html`，保持旧站 URL 和离线阅读稳定。V2 的 `apps/web/` 提供 Graph Lab、模型比较、数据集注册表和生成式阅读器。

## 内容来源

1. 根目录 `NN.html` 是兼容页面，也是迁移脚本的输入。
2. `v2/content/lessons/NN.html` 是从根页面 `.main-content` 区域提取的正文快照。
3. `v2/content/lessons/NN.json` 保存源 Git blob、标题层级、示例路径和审校状态。
4. `v2/content/evidence/NN.json` 保存关键定义、公式、实验数字与论文结论的证据定位。
5. `v2/apps/web/lessons/NN.html` 是阅读器生成产物，不作为手工编辑源。

## 审校状态

- `migrated_unreviewed`：内容已迁移，但事实和技术细节尚未逐条审校。
- `reviewed`：已有证据账本，核心公式和示例通过本章测试；仍不等于同行评审或完整论文复现。
- 单条证据状态使用 `verified`、`derived`、`illustrative` 或 `unverified`；派生值必须保留推导说明。

第 1–10 章已采用独立文章结构，包含问题、定义、渐进图解、MathML、代码、适用边界、参考资料和浏览器交互。后续章节应沿用 `AGENTS.md` 的门槛逐批升级。
