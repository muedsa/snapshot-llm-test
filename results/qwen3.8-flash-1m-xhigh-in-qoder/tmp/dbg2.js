const fs = require('fs');
const raw = fs.readFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/exports/Execute_30_tasks_with_quality_2026-10-13_10-31.md', 'utf8');
const lines = raw.split('\n').slice(0, 40);
for (let i = 0; i < lines.length; i++) {
  if (/2026|10:09/.test(lines[i])) {
    console.log(i + 1, JSON.stringify(lines[i]));
    if (i === 20) console.log('codes:', [...lines[i]].map(c => c.charCodeAt(0)).join(','));
  }
}
console.log('--- counts of candidate patterns ---');
const pats = [/\[\d{4}-\d{2}-\d{2}T/g, /\[\d{4}-\d{2}-\d{2}/g, /2026-10-12T10:09:34/g, /2026-10-12T/g];
for (const p of pats) {
  const c = (raw.match(p) || []).length;
  console.log(String(p).padEnd(40), c);
}
