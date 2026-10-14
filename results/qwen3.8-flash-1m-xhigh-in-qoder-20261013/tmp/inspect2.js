const fs = require('fs');
const R = JSON.parse(fs.readFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/.qoder-credits/report.json', 'utf8'));
const out = [];
const p = (...a) => out.push(a.join(' '));

p('=== session ===');
p(JSON.stringify(R.session, null, 1));
p('=== context ===');
p(JSON.stringify(R.context, null, 1));
p('=== totals ===');
p(JSON.stringify(R.totals, null, 1));
p('=== creditsCoverage ===');
p(JSON.stringify(R.creditsCoverage, null, 1));
p('=== availability ===');
p(JSON.stringify(R.availability, null, 1));
p('=== byCategory ===');
for (const c of R.byCategory) p(`${c.key}\t${c.label}\t${c.tokens}\t${(c.share * 100).toFixed(2)}%`);
p('=== byTool ===');
for (const t of R.byTool) p(`${t.tool}\ttokens=${t.tokens}\tcalls=${t.calls}\tperCall=${t.perCall}\tshare=${(t.share * 100).toFixed(2)}%`);
p('=== byAttr ===');
for (const a of R.byAttr) p(`${a.attr}\t${a.tokens}\t${(a.share * 100).toFixed(2)}%`);
p('=== byCategoryDetail (children) ===');
for (const c of R.byCategoryDetail) {
  p(`- ${c.key} ${c.label} tokens=${c.tokens} share=${(c.share * 100).toFixed(2)}%`);
  for (const ch of c.children || []) p('    * ' + JSON.stringify(ch));
}
p('=== compactionCost ===');
p(JSON.stringify(R.compactionCost, null, 1));
p('=== byFile: top 30 by billed ===');
const byBilled = [...R.byFile].sort((a, b) => b.billed - a.billed);
for (const f of byBilled.slice(0, 30)) p(JSON.stringify(f));
p('=== byFile: top 20 by selfTokens ===');
for (const f of [...R.byFile].sort((a, b) => b.selfTokens - a.selfTokens).slice(0, 20)) p(JSON.stringify(f));
p('=== byFile: aggregate by kind ===');
const byKind = {};
for (const f of R.byFile) {
  byKind[f.kind] = byKind[f.kind] || { files: 0, billed: 0, reads: 0, selfTokens: 0 };
  byKind[f.kind].files++;
  byKind[f.kind].billed += f.billed;
  byKind[f.kind].reads += f.reads;
  byKind[f.kind].selfTokens += f.selfTokens;
}
for (const k of Object.keys(byKind)) p(k + ' ' + JSON.stringify(byKind[k]));
p('=== byFile: aggregate by tool ===');
const byFtool = {};
for (const f of R.byFile) {
  byFtool[f.tool] = byFtool[f.tool] || { files: 0, billed: 0, reads: 0 };
  byFtool[f.tool].files++;
  byFtool[f.tool].billed += f.billed;
  byFtool[f.tool].reads += f.reads;
}
for (const k of Object.keys(byFtool)) p(k + ' ' + JSON.stringify(byFtool[k]));
p('=== files total count / billed sum ===');
p('files=' + R.byFile.length + ' billedSum=' + R.byFile.reduce((s, f) => s + f.billed, 0));

const top = (a) => a[0] === undefined ? -Infinity : a[0];
const byReq = [...R.byRequest].sort((a, b) => b.inputTokens - a.inputTokens);
p('=== byRequest top 15 by inputTokens ===');
for (const r of byReq.slice(0, 15)) p(JSON.stringify(r));
p('=== byRequest: count fields / ranges ===');
p('len=' + R.byRequest.length);
p('keys=' + JSON.stringify(Object.keys(R.byRequest[0])));
p('first=' + JSON.stringify(R.byRequest[0]));
p('last=' + JSON.stringify(R.byRequest[R.byRequest.length - 1]));
p('sum input=' + R.byRequest.reduce((s, r) => s + (r.inputTokens || 0), 0));
p('sum credits=' + R.byRequest.reduce((s, r) => s + (r.credits || 0), 0).toFixed(3));
const ratios = R.byRequest.map(r => r.ratio);
p('ratio min=' + Math.min(...ratios) + ' max=' + Math.max(...ratios));
p('=== other top-level keys ===');
p(Object.keys(R).join(', '));
for (const k of Object.keys(R)) {
  if (['schemaVersion','generatedAt','source','usageSource','availability','session','context','totals','creditsCoverage','compactionCost','proxy','byCategory','byCategoryDetail','byTool','byFile','byAttr','byRequest'].includes(k)) continue;
  p('EXTRA ' + k + ' = ' + JSON.stringify(R[k]).slice(0, 2000));
}
fs.writeFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/tmp/report-dump.txt', out.join('\n'), 'utf8');
console.log('written, lines=' + out.length);
