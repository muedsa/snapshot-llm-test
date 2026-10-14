const fs = require('fs');
const d = JSON.parse(fs.readFileSync('D:/mine/workspace/qwen3.8-flash-1m-xhigh-in-qoder/.qoder-credits/report.json', 'utf8'));
const kind = (v) => Array.isArray(v) ? 'array[' + v.length + ']' : (v === null ? 'null' : typeof v);

function shape(v, depth, name) {
  if (depth > 3) return;
  const pad = '  '.repeat(depth);
  if (Array.isArray(v)) {
    console.log(pad + name + ': array[' + v.length + ']');
    if (v.length && typeof v[0] === 'object' && v[0] !== null) shape(v[0], depth + 1, '[0]');
    else if (v.length) console.log(pad + '  sample: ' + JSON.stringify(v.slice(0, 3)));
    return;
  }
  if (v && typeof v === 'object') {
    console.log(pad + name + ': object{' + Object.keys(v).length + '}');
    for (const k of Object.keys(v)) shape(v[k], depth + 1, k);
    return;
  }
  console.log(pad + name + ': ' + kind(v) + ' = ' + JSON.stringify(v).slice(0, 160));
}

if (Array.isArray(d)) {
  console.log('ROOT array length=' + d.length);
  shape(d, 0, '[0]');
} else {
  for (const k of Object.keys(d)) shape(d[k], 0, k);
}
