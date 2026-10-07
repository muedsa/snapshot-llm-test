const fs=require('node:fs');
const input=fs.readFileSync(`${__dirname}/padding-fixed-v002.snapshot`,'utf8');
const a=-8*Math.PI/180,c=Math.cos(a),s=Math.sin(a);
const matrix='('+[c,s,0,0,-s,c,0,0,0,0,1,0,0,0,0,1].join(',')+')';
const fixed=input.replace('<Transform rotate="-8">',`<Transform matrix="${matrix}" alignment="CENTER">`);
fs.writeFileSync(`${__dirname}/matrix-fixed-v003.snapshot`,fixed,{flag:'wx'});
console.log(JSON.stringify({changed:'Original Transform rotate replaced by documented required matrix, other original blocks retained',matrix}));
