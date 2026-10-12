const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const input = path.resolve('tasks/A06-dependency-graph/inputs/graph.json');
const raw = fs.readFileSync(input);
const graph = JSON.parse(raw);
const ids = graph.nodes.map(n => n.id);
const incoming = Object.fromEntries(ids.map(id => [id, []]));
const outgoing = Object.fromEntries(ids.map(id => [id, []]));
for (const [from, to] of graph.solid_edges) {
  if (!outgoing[from] || !incoming[to]) throw new Error('Unknown node');
  outgoing[from].push(to); incoming[to].push(from);
}
const remaining = Object.fromEntries(ids.map(id => [id, incoming[id].length]));
const queue = ids.filter(id => !remaining[id]);
const topo = [];
while (queue.length) {
  const id = queue.shift(); topo.push(id);
  for (const next of outgoing[id]) if (!--remaining[next]) queue.push(next);
}
if (topo.length !== ids.length) throw new Error('Solid graph contains cycle');
const layer = {}, paths = {};
for (const id of topo) {
  layer[id] = incoming[id].length ? 1 + Math.max(...incoming[id].map(p => layer[p])) : 0;
  if (!incoming[id].length) paths[id] = [[id]];
  else {
    const bestLength = Math.max(...incoming[id].map(p => paths[p][0].length));
    paths[id] = incoming[id].filter(p => paths[p][0].length === bestLength)
      .flatMap(p => paths[p].map(pth => [...pth, id]));
  }
}
const maxNodes = Math.max(...ids.map(id => paths[id][0].length));
const longestPaths = ids.filter(id => paths[id][0].length === maxNodes).flatMap(id => paths[id]);
const result = {
  generated_at: new Date().toISOString(), task_id: 'A06', run_id: '20261002-204314-6f31',
  scope: 'Independent input and graph analysis; no actual image inspection claimed',
  source: input, source_sha256: crypto.createHash('sha256').update(raw).digest('hex'),
  node_count: ids.length, solid_edge_count: graph.solid_edges.length,
  feedback_edge_count: graph.feedback_edges.length,
  dag_sort_excludes_feedback: true, topological_order: topo,
  topological_layers: Object.entries(layer).reduce((out, [id, level]) => {
    (out[level] ??= []).push(id); return out;
  }, {}),
  node_audit: graph.nodes.map(n => ({...n, layer: layer[n.id], in_neighbors: incoming[n.id], out_neighbors: outgoing[n.id]})),
  longest_path_node_count: maxNodes, longest_solid_paths: longestPaths,
  non_adjacent_layer_solid_edges: graph.solid_edges.filter(([f,t]) => layer[t] !== layer[f] + 1),
  feedback_semantics: [
    {from: 'N09', to: 'N08', meaning: '首轮渲染失败后回到DSL构建', diagram_label: '失败后回到构建'},
    {from: 'N10', to: 'N08', meaning: '视觉检查发现问题后回到DSL构建修改/修复', diagram_label: '检查发现问题后修复 · 回到构建'}
  ],
  visual_risks: [
    'N03→N06越过一个拓扑层，路线不能看似接入N04或N05。',
    'N04→N13是远距离先决边，必须实线、向前箭头，不能误作反馈或漏掉。',
    'N09→N08与N10→N08为两条独立虚线反馈；各有箭头与说明，均不进入拓扑层。',
    '线交叉处无连接点不是新的依赖；不能在非端点画连接圆点。',
    'N06与N07并行后在N08汇合，N02分叉到N04/N05，N01分叉到N02/N03。',
    'N10→N11仍是输入指定的普通先决边，与N10→N08反馈共存。'
  ]
};
const out = path.join(__dirname, 'independent-facts-v001.json');
fs.writeFileSync(out, JSON.stringify(result, null, 2) + '\n', {flag:'wx'});
console.log(JSON.stringify(result, null, 2));
