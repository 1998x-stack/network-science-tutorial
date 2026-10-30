(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.NetsciContract = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const VERSION = '1.0.0';
  const MAX_NODES = 3000, MAX_EDGES = 60000;
  const METRICS = Object.freeze([
    ['nodes', '节点数'], ['edges', '边数'], ['mean_degree', '平均度'],
    ['mean_local_clustering', '平均聚集系数'], ['global_transitivity', '全局传递性'],
    ['largest_component_fraction', '最大连通分量占比'], ['average_shortest_path_lcc', '最大连通分量平均路径'],
    ['density', '网络密度']
  ]);
  function fail(message) { throw new Error(message); }
  function validScalar(value) { return value === null || (typeof value === 'number' && Number.isFinite(value)); }
  function validate(input) {
    if (!input || typeof input !== 'object' || input.schema_version !== VERSION) fail('不支持的实验数据协议（需要 1.0.0）');
    if (!input.experiment || typeof input.experiment !== 'object' || typeof input.experiment.model !== 'string') fail('缺少实验元信息');
    if (!input.graph || typeof input.graph !== 'object' || input.graph.directed !== false) fail('当前仅支持无向简单图');
    const {nodes, edges} = input.graph;
    if (!Array.isArray(nodes) || !Array.isArray(edges) || nodes.length > MAX_NODES || edges.length > MAX_EDGES) fail('图为空间数据格式错误或超过浏览器规模限制');
    const ids = new Set();
    for (const n of nodes) {
      if (!n || typeof n.id !== 'string' || !n.id || ids.has(n.id)) fail('节点 ID 无效或重复');
      if (n.degree != null && (!Number.isSafeInteger(n.degree) || n.degree < 0)) fail('节点度数无效');
      ids.add(n.id);
    }
    const seenEdges = new Set();
    for (const e of edges) {
      if (!e || !ids.has(e.source) || !ids.has(e.target) || e.source === e.target) fail('无效边：端点不存在或存在自环');
      const key = JSON.stringify([e.source, e.target].sort());
      if (seenEdges.has(key)) fail('无向简单图不能包含重复边');
      seenEdges.add(key);
    }
    if (!input.metrics || typeof input.metrics !== 'object') fail('缺少可信指标');
    for (const [k] of METRICS) if (!validScalar(input.metrics[k])) fail('指标缺失或不是有限数：' + k);
    if (input.metrics.nodes !== nodes.length || input.metrics.edges !== edges.length) fail('指标中的节点/边数量与图数据不一致');
    return input;
  }
  function format(value, digits=3) {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value !== 'number' || !Number.isFinite(value)) return 'N/A';
    return Number.isInteger(value) ? String(value) : value.toFixed(digits);
  }
  return { VERSION, METRICS, MAX_NODES, MAX_EDGES, validate, format };
});
