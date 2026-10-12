const fs=require('fs'),path=require('path');
const original=fs.readFileSync(path.join(__dirname,'measure-text-residuals-v001.py'),'utf8');
const updated=original.replace('requests/A15-request-000001/response.png','requests/A15-request-000002/response.png').replace('text-residuals-baseline-v001.json','text-residuals-final-v002.json');
if(updated===original)throw new Error('Expected input version not found');
fs.writeFileSync(path.join(__dirname,'measure-text-residuals-v002.py'),updated,{flag:'wx'});
