const fs=require('node:fs');
const original=fs.readFileSync('tasks/A03-semantic-debugging/inputs/broken.snapshot','utf8');
const fixed=original.replace('padding="24 32"','padding="(24,32)"');
fs.writeFileSync(`${__dirname}/padding-fixed-v002.snapshot`,fixed,{flag:'wx'});
console.log('Only original padding changed to documented EdgeInsets format.');
