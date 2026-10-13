const fs = require('fs');
const R = JSON.parse(fs.readFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/.qoder-credits/report.json', 'utf8'));
const B = R.totals.billedInputTokens, C = R.totals.credits;
const nf = (n) => Math.round(n).toLocaleString('en-US');
const toMin = (t) => { const [h, m] = t.split(':').map(Number); return h * 60 + m; };
let prev = toMin(R.byRequest[0].time);
const abs = [];
for (const r of R.byRequest) { let m = toMin(r.time); while (m < prev) m += 1440; abs.push(m); prev = m; }
const per = {};
R.byRequest.forEach((r, i) => {
  const h = Math.floor(abs[i] / 60) % 24;
  per[h] = per[h] || { req: 0, billed: 0, credits: 0, peak: 0 };
  per[h].req++; per[h].billed += r.inputTokens; per[h].credits += r.credits;
  per[h].peak = Math.max(per[h].peak, r.inputTokens);
});
const L = [];
L.push('| 本地钟点 | 请求数 | 计费输入 | 占比 | Credits | 该小时最大上下文 |');
L.push('|---|---|---|---|---|---|');
for (let h = 0; h < 24; h++) {
  const p = per[h] || { req: 0, billed: 0, credits: 0, peak: 0 };
  L.push(`| ${String(h).padStart(2, '0')}:00 | ${p.req} | ${nf(p.billed)} | ${(p.billed / B * 100).toFixed(2)}% | ${p.credits.toFixed(1)} | ${nf(p.peak)} |`);
}
const sorted = Object.entries(per).sort((a, b) => b[1].billed - a[1].billed);
L.push('top3 hours: ' + sorted.slice(0, 3).map(([h, v]) => `${String(h).padStart(2, '0')}:00(${(v.billed / B * 100).toFixed(2)}%)`).join(', '));
L.push('bottom3 hours: ' + sorted.slice(-3).reverse().map(([h, v]) => `${String(h).padStart(2, '0')}:00(${(v.billed / B * 100).toFixed(2)}%)`).join(', '));
L.push('span check hours=' + ((abs[abs.length - 1] - abs[0]) / 60).toFixed(2));
fs.writeFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/tmp/hourly.md', L.join('\n'), 'utf8');
console.log(L.join('\n'));
