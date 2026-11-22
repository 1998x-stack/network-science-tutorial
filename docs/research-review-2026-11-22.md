# 网络科学 · 第二轮研究级跨章审计

**日期**：2026-11-22　**范围**：第 16、20、21、22、24、26、28 章，以及首页与独立研究页。

## 研究目的和证据等级

本轮用两个不混淆的数据域进行复核。**合成时间网络**：五个匿名节点、六个按时记录的事件；它可以精确展示数据泄漏与时间尊重路径，但没有真实世界泛化证据。**NetworkX 内置公开历史图**：Zachary Karate Club 34 节点、78 无向边；它能验证静态图结构，不提供本研究任务可信的逐边时间序列。原始论文、独立推导和实际运行的测试必须明确分开。

| 章节 | 二轮审计重点 | 新增验证 / 失败反例 |
|---|---|---|
| 16 链路预测 | 先切事件时间，再生成训练邻接与候选池 | 插入未来 BD@5 后 CN(B,E) 从 0 误升到 1；BD 本身已非训练非边 |
| 20 时序与动态网络 | 接触路径的严格时间顺序与模型可见性分开 | 同一时刻的 AB、BC 按冻结批次无法连续传播 |
| 21 网络嵌入 | 随机游走语料不能提前看到测试边 | B→D 的无偏一阶概率从 0 错升到 1/3 |
| 22 GCN | 邻接归一化同样依赖训练时间截止 | 含自环的 GCN B–D 系数从 0 错变为 1/4 |
| 24 社交网络实例 | 公共数据只做可靠的静态拓扑分析 | NetworkX 34 节点、78 边、45 三角形，通过独立邻接枚举 |
| 26 LightGCN | 未来用户—物品边不能改变训练传播 | 错误加入未来 U2–X 后，U1–X 权重从 1/√2 变为 1/2 |
| 28 综合项目 | 训练、验证、测试标签与候选集合均明确 | 验证是否可重新并入历史图必须是预先约定而非事后选取 |

## 统一时间协议

六条合成事件如下：

```text
A B 1
A C 1
B C 2
C D 2
D E 3
B D 5
```

五节点集合始终为 `A B C D E`。研究版固定训练期 t≤2（AB、AC、BC、CD），验证时窗 t=3（DE），测试时窗 t=5（BD）。第 28 章最初 t≤3 历史图预测 BD@5 的设置并不矛盾：这是**模型选择后，在事前规定的许可下使用截至 t≤3 已知历史**；在其它数据集必须遵照官方协议，有些任务允许特定方式使用验证边，有些则不允许。不能机械认定任意模型测试前都永远不得读取验证数据；但**测试期未来边绝不可以成为构建测试预测所用的训练结构**。

合法 t≤3 图：

- B 的邻居 {A,C}，D 的邻居 {C,E}，E 的邻居 {D}。
- CN(B,D)=1；CN(B,E)=0。候选池固定为 BD、BE。
- 测试时窗 BD 为唯一观察正例，因此受限候选 Precision@1=1。它不说明真实世界准确率。

**故意违规**：提前把未来 BD@5 放进图，会令 BD 成为已存在边，测试资格丧失；CN(B,E) 从0增到1；无偏一阶游走 P(B→D) 由0增到1/3；含自环 GCN 的 B–D 消息系数由0变成1/4。这些变化来自明确的邻接和度数变化，不代表任何已训练图模型的真实预测结果。

另一独立的用户—物品图 U1–X、U1–Y、U2–Y 具有 LightGCN 的 U1–X 归一化系数 1/√2。若把未来 U2–X 提前加入训练，X 的度由1变为2，对应系数降至1/2，U2–X 新系数也是1/2。**不要将这张二部图与五节点合作图合并。**

## 严格时间路径的另外一条规则

对瞬时无向接触，本文约定每条时间尊重路径的接触时间必须严格递增。A–B@1、B–C@2、C–D@3 从 A@0 可依次抵达 D@3。错序 A–B@3、B–C@1、C–D@2 则不能从 A 到达 C、D；同一时刻 AB@1、BC@1 也不能在冻结的同时间批次中实现两跳。这是本课程采用的明确事件约定，不能替代所有领域的时间模型。

## 公共历史图实验和软件版本

`python -m experiments.public_karate_audit` 使用安装的 NetworkX 内置 Karate Club 图，无须下载网站文件。输出 JSON 包含 NetworkX 版本、34 节点、78 无向边、1 分量、度数和156、未加权三角形数45，以及独立手写邻接三角形枚举核验值45。该图的“club”属性可用于比较历史标签和社团检测，但静态数据不能证明个体之间的影响因果，也不能凭任意边序声称完成时序预测。

## 代码、执行与质量门禁

```bash
cd v2
python -m experiments.temporal_audit
python -m pip install 'networkx>=3.3,<4'
python -m experiments.public_karate_audit
python -m unittest tests.test_research_round -v
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/migrate_lessons.py --check
python scripts/build_web.py --check
python scripts/check_web.py
node --test tests/web/*.test.cjs
python tests/web/e2e.py
```

GitHub Actions 的 Python 与 Node 测试检查数值和证据约束，Chromium 在 1440、768、390、360px 宽度下打开图解/MathML，并切换未来边、LightGCN 和同时间路径的状态；仓库提交完成不等于所有门禁成功，须检验远端工作流结果。

## 原始来源和未覆盖任务

- [OGB 官方时间与链接预测评估协议](https://ogb.stanford.edu/docs/linkprop/)
- [OGB 排行榜实验协议](https://ogb.stanford.edu/docs/leader_rules/)
- [动态链接预测的负例采样评估方法](https://arxiv.org/abs/2311.18486)
- [GCN 原论文](https://arxiv.org/abs/1609.02907)
- [LightGCN 原论文](https://arxiv.org/abs/2002.02126)
- [时间网络综述](https://doi.org/10.1016/j.physrep.2012.03.001)
- [NetworkX Karate Club 官方数据文档](https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.karate_club_graph.html)

**后续尚未覆盖**：真实带时间戳公开图的下载及许可核查、时间外多随机种子模型训练、不同负例分布下的估计偏差与真实泛化误差区间、独立训练硬件资源开销。不能把这次合成数值或 Karate Club 静态图当作上述实验的完成证明。
