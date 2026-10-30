# 可视化与实验数据协议 v1.0.0

单一事实来源：Python 计算模型生成数据，浏览器只进行布局/绘制。核心结构：

```json
{
  "schema_version": "1.0.0",
  "experiment": {"id": "structure-generation", "model": "er", "params": {"n": 50, "p": 0.1}, "seed": 42},
  "graph": {
    "directed": false,
    "nodes": [{"id": "0", "degree": 2}],
    "edges": [{"source": "0", "target": "1"}]
  },
  "metrics": {
    "nodes": 50,
    "edges": 122,
    "density": 0.09959,
    "mean_degree": 4.88,
    "components": 1,
    "largest_component_fraction": 1.0,
    "mean_local_clustering": 0.1,
    "global_transitivity": 0.1,
    "average_shortest_path_lcc": 2.5
  }
}
```

上例是字段类型示范，数值不是某一次真实运行记录。实际数据使用 CLI 生成。

- `nodes[].id` 采用稳定字符串 ID；所有孤立点必须显式包含。
- 无向图的 `edges` 仅出现一次，且不能有自环或平行边。
- `average_shortest_path_lcc`: **只在最大连通分量内计算**；分量只有 1 个节点时为 0；没有节点时为 null；超过当前实验精确计算上限时为 null。
- `global_transitivity`: 闭合三元组比例，与平均局部聚集系数不是同一统计量。
- `seed` 控制 PRNG；重跑同输入保持拓扑和数值一致。算法版本升级后的结果可以变化，需要固定 git revision / 版本号。
- 浏览器不接受缺少版本号、断裂端点或重复节点 ID 的实验 JSON。
- S01 的协议仅覆盖**简单无向图**；S02+ 要引入有向/多层/时间数据时先给协议升级（兼容解析 + golden tests），不要静默复用旧语义。
