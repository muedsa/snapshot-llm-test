const fs=require('node:fs');
const input=fs.readFileSync(`${__dirname}/parent-fixed-v004.snapshot`,'utf8');
const fixed=input.replace('<Snapshot width="1280" height="800"','<Snapshot').replace('<Container padding="(24,32)" borderRadius="24">','<Container width="1280" height="800" padding="(24,32)" borderRadius="24">');
fs.writeFileSync(`${__dirname}/bounds-fixed-v005.snapshot`,fixed,{flag:'wx'});
console.log('Removed ignored root dimensions and set finite1280x800 outer Container; all existing content retained to inspect remaining semantics.');
