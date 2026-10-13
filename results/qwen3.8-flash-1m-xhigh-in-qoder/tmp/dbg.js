const fs = require('fs');
const raw = fs.readFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/exports/Execute_30_tasks_with_quality_2026-10-13_10-31.md', 'utf8');
const re = /\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2})\]/g;
let m, n = 0, bad = 0;
const vals = [];
const badSamples = [];
while ((m = re.exec(raw))) {
  n++;
  const t = Date.parse(m[1]);
  if (isNaN(t)) { bad++; if (badSamples.length < 3) badSamples.push(JSON.stringify(m[1])); }
  else vals.push(t);
}
vals.sort((a, b) => a - b);
console.log('matches=' + n + ' NaN=' + bad + ' good=' + vals.length, badSamples.join(' '));
if (vals.length) {
  console.log('min=' + new Date(vals[0]).toISOString() + ' max=' + new Date(vals[vals.length - 1]).toISOString());
}
