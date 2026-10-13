const fs = require('fs');
const R = JSON.parse(fs.readFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/.qoder-credits/report.json', 'utf8'));
const B = R.totals.billedInputTokens;
const nf = (n) => Math.round(n).toLocaleString('en-US');
const pc = (x, d = 2) => (x * 100).toFixed(d) + '%';
const L = [];

L.push('##TABLE-CATEGORY');
for (const c of [...R.byCategory].sort((a, b) => b.tokens - a.tokens)) {
  L.push(`| ${c.label} | ${nf(c.tokens)} | ${pc(c.share)} |`);
}
L.push('##TABLE-ATTR');
for (const a of [...R.byAttr].slice(0, 10)) {
  L.push(`| ${a.attr} | ${nf(a.tokens)} | ${pc(a.share)} |`);
}
L.push('##TABLE-TOOL');
for (const t of [...R.byTool].sort((a, b) => b.tokens - a.tokens)) {
  L.push(`| ${t.tool} | ${nf(t.tokens)} | ${t.calls} | ${nf(t.perCall)} | ${pc(t.share)} |`);
}
L.push('##TABLE-BANDS');
const bands = [[0, 100000, '<10万'], [100000, 200000, '10–20万'], [200000, 300000, '20–30万'], [300000, 400000, '30–40万'], [400000, 500000, '40–50万'], [500000, 600001, '50–60万']];
for (const [lo, hi, lab] of bands) {
  const s = R.byRequest.filter(r => r.inputTokens >= lo && r.inputTokens < hi);
  const sum = s.reduce((a, r) => a + r.inputTokens, 0);
  L.push(`| ${lab} | ${s.length} | ${pc(s.length / R.byRequest.length)} | ${nf(sum)} | ${pc(sum / B)} |`);
}
L.push('##TABLE-FILES');
const bf = [...R.byFile].sort((a, b) => b.billed - a.billed).slice(0, 12);
for (const f of bf) {
  L.push(`| ${f.label} | ${f.tool} | ${nf(f.selfTokens)} | ${f.reads} | ${nf(f.trips)} | ${nf(f.billed)} | ${pc(f.share)} | ${(f.billed / f.selfTokens).toFixed(0)}× |`);
}
L.push('##TABLE-COMPACT');
for (const c of R.compactionCost.items) {
  L.push(`| ${c.index} | ${c.at} | ${nf(c.preTokens)} | ${nf(c.postTokens)} | ${nf(c.savedTokens)} | ${c.messagesSummarized} | ${c.nextRequestIndex} | ${nf(c.nextInputTokens)} |`);
}
L.push('##TABLE-SEG');
const marks = [0, ...R.compactionCost.items.map(c => c.nextRequestIndex), R.byRequest.length + 1];
for (let i = 0; i < marks.length - 1; i++) {
  const seg = R.byRequest.filter(r => r.index > marks[i] && r.index <= marks[i + 1] - 1);
  if (!seg.length) continue;
  const sum = seg.reduce((a, r) => a + r.inputTokens, 0);
  L.push(`| ${i + 1} | ${seg[0].index}–${seg[seg.length - 1].index} | ${seg.length} | ${nf(sum / seg.length)} | ${nf(Math.max(...seg.map(r => r.inputTokens)))} | ${nf(sum)} | ${pc(sum / B)} |`);
}
L.push('##SCALARS');
const spanH = 24.20;
const kvs = {
  billed: nf(B),
  credits: R.totals.credits.toFixed(3),
  creditsPerM: (R.totals.credits / (B / 1e6)).toFixed(3),
  avgTrip: nf(B / R.byRequest.length),
  avgCreditsTrip: (R.totals.credits / R.byRequest.length).toFixed(3),
  amp: (B / R.totals.netContextTokens).toFixed(1),
  perHour: (R.totals.credits / spanH).toFixed(1),
  perTask: (R.totals.credits / 30).toFixed(2),
  perTurn: (R.totals.credits / R.session.turns).toFixed(1),
  billedPerTurn: nf(B / R.session.turns),
  toolCover: pc(R.byTool.reduce((a, t) => a + t.tokens, 0) / B),
  fileCover: pc(R.byFile.reduce((a, f) => a + f.billed, 0) / B),
  fixedOverhead: pc((R.byCategory.find(c => c.key === 'system').tokens + R.byCategory.find(c => c.key === 'attachment').tokens + R.byCategory.find(c => c.key === 'compact_summary').tokens) / B),
  sysResendX: Math.round(R.byCategory.find(c => c.key === 'system').tokens / R.context.systemPromptTokens),
  bashResidency: (R.byCategoryDetail.find(c => c.key === 'tool_result').children[0].trips / R.byTool.find(t => t.tool === 'Bash').calls).toFixed(0),
  writeBilled: nf(R.byFile.filter(f => f.kind === 'write').reduce((a, f) => a + f.billed, 0)),
  readBilled: nf(R.byFile.filter(f => f.kind === 'read').reduce((a, f) => a + f.billed, 0)),
  writeShare: pc(R.byFile.filter(f => f.kind === 'write').reduce((a, f) => a + f.billed, 0) / B),
  readShare: pc(R.byFile.filter(f => f.kind === 'read').reduce((a, f) => a + f.billed, 0) / B),
  bigShare: pc(R.byRequest.filter(r => r.inputTokens >= 400000).reduce((a, r) => a + r.inputTokens, 0) / B),
  bigReq: R.byRequest.filter(r => r.inputTokens >= 400000).length,
  compactPreShare: pc(R.compactionCost.totals.preTokens / B),
  peakPct: pc(R.context.peakSessionTokens / R.context.contextWindow),
  netPct: pc(R.context.netContextTokens / R.context.contextWindow),
  triggerPct: pc(R.context.observedAutoTriggerTokens / R.context.contextWindow),
  msgs: nf(R.compactionCost.items.reduce((a, c) => a + c.messagesSummarized, 0)),
};
for (const k of Object.keys(kvs)) L.push(`${k} = ${kvs[k]}`);
fs.writeFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/tmp/report-tables.md', L.join('\n'), 'utf8');
console.log(L.join('\n'));
