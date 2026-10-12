'use strict';
const fs=require('fs'),path=require('path'),base=path.resolve(__dirname,'..','producer-02-04');
const cases=[];
for(const id of ['02','03','04']){
const s=fs.readFileSync(path.join(base,'case-'+id+'-v001.snapshot'),'utf8'),dims=id==='03'?[1500,1120]:[1600,1120],outside=[];
for(const m of s.matchAll(/<Positioned left="([^"]+)" top="([^"]+)" width="([^"]+)" height="([^"]+)"/g)){
const [x,y,w,h]=m.slice(1).map(Number);
if(x<0||y<0||x+w>dims[0]+.0001||y+h>dims[1]+.0001)outside.push([x,y,w,h]);
}
cases.push({case_id:'case-'+id,canvas:dims,positioned_widgets:Array.from(s.matchAll(/<Positioned /g)).length,outside_canvas:outside});
}
const result={at:new Date().toISOString(),cases,scope:'Widget layout bounds only; transformed painted bounds and font pixels require actual visual review.',passed:cases.every(c=>c.outside_canvas.length===0)};
fs.writeFileSync(path.join(__dirname,'bounds-check-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
