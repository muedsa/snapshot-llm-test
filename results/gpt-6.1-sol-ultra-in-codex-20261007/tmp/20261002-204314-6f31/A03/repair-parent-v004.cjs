const fs=require('node:fs');
const input=fs.readFileSync(`${__dirname}/matrix-fixed-v003.snapshot`,'utf8');
const live='<Positioned right="20"><Text color="white">LIVE</Text></Positioned>';
const withoutRowLive=input.replace(live,'');
const fixed=withoutRowLive.replace('<Column>','<Stack><Column>').replace('</Column>','</Column>'+live+'</Stack>');
fs.writeFileSync(`${__dirname}/parent-fixed-v004.snapshot`,fixed,{flag:'wx'});
console.log('Moved existing LIVE Positioned from Row to direct Stack child; retained all original blocks. Root dimension semantics remain unchanged for explicit diagnosis.');
