const fs = require('fs');
const P = 'D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/exports/Execute_30_tasks_with_quality_2026-10-13_10-31.md';
const st1 = fs.statSync(P);
const raw = fs.readFileSync(P, 'utf8');
console.log('size=' + st1.size, 'mtime=' + st1.mtime.toISOString(), 'chars=' + raw.length);
console.log('hasYou=' + raw.includes('### **You**'), 'hasOffset=' + (raw.match(/\+08:00\]/g) || []).length, 'hasBracket=' + (raw.match(/\[2026/g) || []).length);
const i = raw.indexOf('### **You**');
console.log('--- around first You ---');
console.log(JSON.stringify(raw.slice(i, i + 700)));
console.log('--- first 5 [2026 occurrences ---');
const re = /\[2026[^\]]{0,40}\]/g;
let m, k = 0;
while ((m = re.exec(raw)) && k < 5) { console.log(JSON.stringify(m[0])); k++; }
