const fs = require('fs');
const R = JSON.parse(fs.readFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/.qoder-credits/report.json', 'utf8'));
const B = R.totals.billedInputTokens;
const kind = {};
for (const f of R.byFile) {
  kind[f.kind] = kind[f.kind] || { files: 0, billed: 0, events: 0, selfTokens: 0 };
  kind[f.kind].files++; kind[f.kind].billed += f.billed; kind[f.kind].events += f.reads; kind[f.kind].selfTokens += f.selfTokens;
}
const w = kind.write, r = kind.read;
console.log('write', JSON.stringify(w));
console.log('read ', JSON.stringify(r));
console.log('total ratio billed write/read =', (w.billed / r.billed).toFixed(2));
console.log('per-file ratio =', ((w.billed / w.files) / (r.billed / r.files)).toFixed(2), '(write per file', Math.round(w.billed / w.files).toLocaleString('en-US'), ', read per file', Math.round(r.billed / r.files).toLocaleString('en-US'), ')');
console.log('per-event ratio =', ((w.billed / w.events) / (r.billed / r.events)).toFixed(2), '(write per event', Math.round(w.billed / w.events).toLocaleString('en-US'), ', read per event', Math.round(r.billed / r.events).toLocaleString('en-US'), ')');
console.log('write selfTokens total', w.selfTokens.toLocaleString('en-US'), 'billed/self =', (w.billed / w.selfTokens).toFixed(1));
console.log('read  selfTokens total', r.selfTokens.toLocaleString('en-US'), 'billed/self =', (r.billed / r.selfTokens).toFixed(1));
console.log('bash billed/trips =', (R.byCategoryDetail.find(c => c.key === 'tool_result').children[0].tokens / R.byCategoryDetail.find(c => c.key === 'tool_result').children[0].trips).toFixed(1));
console.log('top file billed/trips =', (17735094 / 28920).toFixed(0), 'selfTokens 37575 -> billed/self =', (17735094 / 37575).toFixed(0));
console.log('fixed overhead per 1000 requests =', (40965 * 1000 / 1e6).toFixed(2), 'M tokens =', (40965 * 1000 * (R.totals.credits / B)).toFixed(1), 'credits');
