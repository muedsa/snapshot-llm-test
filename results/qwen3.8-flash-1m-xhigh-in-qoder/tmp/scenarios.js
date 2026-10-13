const fs = require('fs');
const R = JSON.parse(fs.readFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/.qoder-credits/report.json', 'utf8'));
const B = R.totals.billedInputTokens;
const C = R.totals.credits;
const rate = C / B; // credits per token
const nf = (n) => Math.round(n).toLocaleString('en-US');
const pc = (x) => (x * 100).toFixed(2) + '%';
const L = [];
const p = (s) => L.push(s);

p('rate credits/token = ' + rate.toFixed(9) + ' ; per 1M = ' + (rate * 1e6).toFixed(3));
p('requests=' + R.byRequest.length + ' per-user-turn=' + (R.byRequest.length / R.session.turns).toFixed(0));

// scenario A: lower compaction trigger
const post = R.compactionCost.items.map(c => c.nextInputTokens);
const avgPost = post.reduce((a, b) => a + b, 0) / post.length;
const avgPre = R.compactionCost.items.map(c => c.preTokens).reduce((a, b) => a + b, 0) / 6;
const avgObs = B / R.byRequest.length;
p('avgPost(nextInput after compact)=' + Math.round(avgPost) + ' avgPre(trigger point)=' + Math.round(avgPre) + ' avgObservedPerTrip=' + Math.round(avgObs));
for (const T of [400000, 450000, 500000]) {
  const newAvg = (avgPost + T) / 2;
  const scale = newAvg / avgObs;
  p(`trigger->${nf(T)}: modelled avg context=${nf(newAvg)} scale=${(scale * 100).toFixed(1)}% billed=${nf(B * scale)} credits=${(C * scale).toFixed(0)} saved=${nf(C * (1 - scale))} credits (${pc(1 - scale)})`);
  const nCompact = (6 * (avgPre - avgPost) / (T - avgPost));
  p(`   compactions would rise 6 -> ${nCompact.toFixed(1)}; their own input cost = ${nf(nCompact * T)} tokens = ${(nCompact * T * rate).toFixed(0)} credits (now ${nf(R.compactionCost.totals.preTokens)} = ${(R.compactionCost.totals.preTokens * rate).toFixed(0)} credits)`);
}

// scenario B: halve top-file residency
const bf = [...R.byFile].sort((a, b) => b.billed - a.billed);
const top12 = bf.slice(0, 12).reduce((s, f) => s + f.billed, 0);
const top50 = bf.slice(0, 50).reduce((s, f) => s + f.billed, 0);
p('top12 files billed=' + nf(top12) + ' (' + pc(top12 / B) + ') halving saves ' + nf(top12 / 2) + ' tokens = ' + (top12 / 2 * rate).toFixed(0) + ' credits');
p('top50 files billed=' + nf(top50) + ' (' + pc(top50 / B) + ') halving saves ' + nf(top50 / 2) + ' tokens = ' + (top50 / 2 * rate).toFixed(0) + ' credits');

// scenario C: Bash halved
const bash = R.byTool.find(t => t.tool === 'Bash').tokens;
p('Bash billed=' + nf(bash) + ' (' + pc(bash / B) + ') halving saves ' + (bash / 2 * rate).toFixed(0) + ' credits');
const bashRes = R.byCategoryDetail.find(c => c.key === 'tool_result').children[0];
p('tool_result|Bash tokens=' + nf(bashRes.tokens) + ' trips=' + nf(bashRes.trips) + ' per-request-slot=' + (bashRes.tokens / bashRes.trips).toFixed(1));
p('tool_use|Bash per-call=' + nf(R.byAttr.find(a => a.attr === 'tool_use|Bash').tokens / 1586));

// scenario D: Write halved
const w = R.byTool.find(t => t.tool === 'Write').tokens;
p('Write billed=' + nf(w) + ' (' + pc(w / B) + ') halving saves ' + (w / 2 * rate).toFixed(0) + ' credits');

// fixed overhead per request
const sysT = R.byCategory.find(c => c.key === 'system').tokens;
const attT = R.byCategory.find(c => c.key === 'attachment').tokens;
const csT = R.byCategory.find(c => c.key === 'compact_summary').tokens;
p('system+attachment+compact per request=' + nf((sysT + attT + csT) / R.byRequest.length) + ' credits/hour-equivalent');

// thinking share in credits
for (const k of ['assistant_thinking', 'assistant_tool_use', 'tool_result', 'system', 'attachment', 'compact_summary', 'user_input', 'assistant_text']) {
  const t = R.byCategory.find(c => c.key === k).tokens;
  p(`${k}: ${nf(t)} tokens = ${(t * rate).toFixed(0)} credits (${pc(t / B)})`);
}

// cost of one extra request at current context
p('marginal cost at final context ' + nf(R.context.netContextTokens) + ' = ' + (R.context.netContextTokens * rate).toFixed(3) + ' credits/request');
p('marginal cost at peak ' + nf(R.context.peakSessionTokens) + ' = ' + (R.context.peakSessionTokens * rate).toFixed(3) + ' credits/request');
p('one 30k-token file kept alive for 1000 requests = ' + nf(30000 * 1000) + ' tokens = ' + (30000 * 1000 * rate).toFixed(0) + ' credits');

fs.writeFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/tmp/scenarios.txt', L.join('\n'), 'utf8');
console.log(L.join('\n'));
