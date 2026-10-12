'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const base=__dirname;
const recorded_at=new Date().toISOString();
function save(n,v){fs.writeFileSync(path.join(base,n),typeof v==='string'?v:JSON.stringify(v,null,2),{encoding:'utf8',flag:'wx'});}
save('local-command-failure-v001.json',{recorded_at,type:'local_shell_quoting_error',message:'node -e inline regex inspection exited1: Unterminated regexp literal. No DSL file changed; switching to a saved script.',service_request:false});
let source=fs.readFileSync(path.join(base,'generate-v001.cjs'),'utf8');
function replaceOnce(a,b){if(!source.includes(a))throw Error('Missing revision source '+a);source=source.replace(a,b);}
replaceOnce('function contour(cx,cy,rx,ry,k){const p=[];for(let j=0;j<=96;j++){const a=j/96*Math.PI*2;', 'function contour(cx,cy,rx,ry,k,segments=40){const p=[];for(let j=0;j<=segments;j++){const a=j/segments*Math.PI*2;');
replaceOnce('contour(282,670,180-k*17,122-k*10,k)', 'contour(282,670,180-k*17,122-k*10,k,24)');
replaceOnce("label(c,1171,968,335,'携带饮水 · 核对天气与路线\\n沿途未承诺可饮水源',20,'#C6D1BC');", "c.text(1171,968,335,76,'携带饮水 · 核对天气与路线\\n沿途未承诺可饮水源',20,'#C6D1BC');");
replaceOnce('label(c,50,1077,1480,','label(c,50,1070,1480,');
replaceOnce('for(const build of [harbor,theatre,ridge])','for(const build of [ridge])');
replaceOnce("function write(name,data){fs.writeFileSync(path.join(base,name),", "function write(name,data){name=name.replace('-v001.snapshot','-v002.snapshot').replace('-metadata-v001.json','-metadata-servicefix-v001.json').replace('-content-v001.md','-content-servicefix-v001.md').replace('source-read-evidence-v001.json','source-read-evidence-v002.json');fs.writeFileSync(path.join(base,name),");
save('generate-case-07-v002.cjs',source);
vm.runInNewContext(source,{require:require,__dirname:base,console:console},{filename:'generate-case-07-v002.cjs'});
const p07=fs.readFileSync(path.join(base,'case-07-v002.snapshot'),'utf8');
const count=(p07.match(/<[A-Za-z][^>]*>/g)||[]).length;
if(count>=4096)throw Error('Still exceeds conservative full tag count: '+count);
let p06=fs.readFileSync(path.join(base,'case-06-v002.snapshot'),'utf8');
const old='<Positioned left="302" top="496" width="596" height="45.9"><Text fontFamily="Inter,Noto Sans CJK SC" fontSize="27" color="#F7D6BF" fontStyle="BOLD">';
if(!p06.includes(old))throw Error('Stage alignment target missing');
p06=p06.replace(old,old.replace('fontStyle="BOLD">','fontStyle="BOLD" textAlign="CENTER">'));
save('case-06-v003.snapshot',p06);
save('revision-service-limit-v001.json',{recorded_at,case_07:{parent:'case-07-v001.snapshot',new:'case-07-v002.snapshot',basis:'root req15 actualHTTP400 RENDER_ERROR Document contains more than4096 elements',category:'syntax-fix/service-limit',changes:['主等高线16条×40段，副等高线9条×24段，旧两组均96段','所有原地形圈数量与路线数据保持','出发前两行说明文本盒高34→76','页脚top1077→1070使底边1095.5不越1100'],conservative_start_element_count:count,original_start_element_count:(fs.readFileSync(path.join(base,'case-07-v001.snapshot'),'utf8').match(/<[A-Za-z][^>]*>/g)||[]).length,visual_iteration:false},case_06:{parent:'case-06-v002.snapshot',new:'case-06-v003.snapshot',basis:'root req14实际服务图中舞台标题偏左',category:'visual-candidate',changes:['舞台Text增加textAlign CENTER'],new_visual_review_completed:false},performed_service_request:false});
console.log(JSON.stringify({case07_tags:count,case07:'case-07-v002.snapshot',case06:'case-06-v003.snapshot'}));
