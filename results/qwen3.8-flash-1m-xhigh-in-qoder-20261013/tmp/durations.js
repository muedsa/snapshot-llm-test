const fs = require('fs');
const path = 'D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/exports/Execute_30_tasks_with_quality_2026-10-13_10-31.md';
const raw = fs.readFileSync(path, 'utf8');
const re = /\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2})\]/g;
const all = [];
let m;
while ((m = re.exec(raw))) all.push({ t: new Date(m[1]).getTime(), line: raw.slice(Math.max(0, m.index - 300), m.index).split('\n').slice(-3).join(' | ') });
const S = new Date('2026-10-12T02:09:34.569Z').getTime();
const E = new Date('2026-10-13T02:21:34.387Z').getTime();
const inWin = [...new Set(all.filter(a => a.t >= S - 1000 && a.t <= E + 1000).map(a => a.t))].sort((a, b) => a - b);
const out = [];
const p = (...a) => out.push(a.join(' '));
const fmt = (t) => new Date(t).toISOString().slice(11, 19) + 'Z';
p('all stamps=' + all.length + ' in-window unique=' + inWin.length + ' (outside window=' + (new Set(all.map(a=>a.t)).size - inWin.length) + ')');
p('window hours=' + ((E - S) / 3600000).toFixed(2) + ' firstStamp=' + fmt(inWin[0]) + ' lastStamp=' + fmt(inWin[inWin.length - 1]));
let active = 0, idle = 0;
const big = [];
for (let i = 1; i < inWin.length; i++) {
  const d = inWin[i] - inWin[i - 1];
  if (d < 900000) active += d; else { idle += d; big.push({ from: inWin[i - 1], to: inWin[i], d }); }
}
p('active(<15min steps)=' + (active / 3600000).toFixed(2) + 'h   idle(>=15min steps)=' + (idle / 3600000).toFixed(2) + 'h  count=' + big.length);
p('--- steps >= 5 min ---');
for (const x of [...big].sort((a, b) => b.d - a.d)) p(`${(x.d / 60000).toFixed(1)} min  ${fmt(x.from)} -> ${fmt(x.to)}   next-block: ${all.filter(a=>a.t===x.to)[0]?.line.replace(/\s+/g,' ').slice(-140)}`);
const b2 = [[0, 60000], [60000, 300000], [300000, 900000], [900000, 3600000], [3600000, Infinity]];
p('--- in-window step buckets ---');
for (const [lo, hi] of b2) {
  let c = 0, s = 0;
  for (let i = 1; i < inWin.length; i++) { const d = inWin[i] - inWin[i - 1]; if (d >= lo && d < hi) { c++; s += d; } }
  p(`${lo / 1000}s-${hi === Infinity ? 'inf' : hi / 1000}s: count=${c} hours=${(s / 3600000).toFixed(2)}`);
}
fs.writeFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/tmp/durations.txt', out.join('\n'), 'utf8');
console.log(out.join('\n'));
