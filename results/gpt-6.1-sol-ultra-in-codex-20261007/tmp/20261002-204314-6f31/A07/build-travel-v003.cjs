'use strict';
const fs=require('node:fs'),path=require('node:path');
const {Canvas}=require('../_suite/dsl.cjs'),s=require('../_suite/suite.cjs');
const facts=JSON.parse(fs.readFileSync(path.join(__dirname,'independent-analysis/route-facts-v001.json'),'utf8'));
if(s.sha256(fs.readFileSync(facts.source))!==facts.source_sha256)throw Error('Independent route input changed');
const T={bg:'#F7F6F2',ink:'#18343E',muted:'#577078',R:'#C94745',B:'#286AA7',G:'#1A836F',border:'#DDE6E0',warn:'#F9EADC',warnInk:'#8D451D'};
const c=new Canvas(720,1280,{background:T.bg,font:'Inter,Noto Sans CJK SC'});
const single={softWrap:false,maxLines:1};
function txt(x,y,w,value,size=20,color=T.ink,bold=false,h=34){c.text(x,y,w,h,value,size,color,{bold,...single});}
function badge(x,y,line,w=40){c.card(x,y,w,30,T[line],{radius:8});c.text(x,y,w,30,line,20,'#FFFFFF',{bold:true,align:'center',...single});}
function segment(y,seg){badge(48,y+1,seg.line);txt(106,y,566,seg.stations.join(' → '),20);}
function panel(y,h,q){c.card(28,y,664,h,'#FFFFFF',{radius:18,border:'1 SOLID '+T.border});txt(48,y+15,405,`${q.id.slice(1).padStart(2,'0')}  ${q.from_name} → ${q.to_name}`,26,T.ink,true,42);txt(478,y+21,192,`${q.ordinary.edge_count}区间 / ${q.ordinary.transfer_count}换乘`,22,T.muted,true,36);txt(48,y+56,624,`${q.from}  →  ${q.to}`,20,T.muted);}
c.rect(0,0,720,112,T.ink);
txt(28,18,664,'澄川 · 三线出行',36,'#FFFFFF',true,55);
txt(28,75,664,'旅行卡 / 虚构城市 · 三条普通路线与无障碍核验',20,'#DAE7E5');
for(const [i,line,name] of [[0,'R','红线'],[1,'B','蓝线'],[2,'G','绿线']]){const x=28+i*228;c.card(x,132,208,42,'#FFFFFF',{radius:12,border:'1 SOLID '+T.border});badge(x+12,138,line);txt(x+64,137,132,name,20,T[line],true);}
const q1=facts.queries[0],q2=facts.queries[1],q3=facts.queries[2];
panel(197,260,q1);
segment(287,q1.ordinary.line_segments[0]);segment(323,q1.ordinary.line_segments[1]);
txt(48,359,624,'中心 S04：R → B',20,T.muted);
c.card(48,396,624,40,'#E8F3EE',{radius:10});
txt(60,400,600,'可作无障碍旅程；S03 / S09 均为同线通过。',20,T.G,true);
panel(477,426,q2);
segment(568,q2.ordinary.line_segments[0]);segment(603,q2.ordinary.line_segments[1]);
c.card(48,638,624,40,T.warn,{radius:10});
txt(60,642,600,'无障碍不适用：东桥 S05 设施不足，不能换乘。',20,T.warnInk,true);
c.line(48,688,672,688,T.border,1);
txt(48,694,624,'无障碍替代 · 6区间 / 2换乘',22,T.G,true);
segment(733,q2.shortest_accessible.line_segments[0]);segment(768,q2.shortest_accessible.line_segments[1]);segment(803,q2.shortest_accessible.line_segments[2]);
txt(48,840,624,'工坊 S08（G→B）· 中心 S04（B→R）换乘',20,T.muted);
txt(48,872,624,'S14 公园 / S05 东桥仅同线通过',20,T.G);
panel(923,224,q3);
segment(1014,q3.ordinary.line_segments[0]);segment(1049,q3.ordinary.line_segments[1]);
txt(48,1086,624,'工坊 S08：B → G；可作无障碍旅程',20,T.G,true);
txt(48,1117,624,'S05 东桥仅乘 G 线通过，无需在那里换乘。',20,T.muted);
txt(28,1167,664,'每个相邻区间等时；先比区间，再比换乘。',20,T.muted);
txt(28,1199,664,'首乘不算换乘；设施不足站可同线通过。',20,T.muted);
txt(28,1231,664,'无障碍只要求起终点与实际换乘站设施达标。',20,T.muted);
const dsl=c.toString();
fs.writeFileSync(path.join(__dirname,'travel-card-v003.snapshot'),dsl,{flag:'wx'});
fs.writeFileSync(path.join(__dirname,'travel-card-content-v003.json'),JSON.stringify({task_id:'A07',run_id:'20261002-204314-6f31',version_id:'A07-travel-v003',facts_source:path.join(__dirname,'independent-analysis/route-facts-v001.json'),visual_tokens:T,canvas:{width:720,height:1280},minimum_body_font_size:20,panels:[{query:q1.id,y:197,height:260},{query:q2.id,y:477,height:426},{query:q3.id,y:923,height:224}],ordinary_routes:[q1,q2,q3].map(q=>({query_id:q.id,from:q.from,to:q.to,station_sequence:q.ordinary.station_sequence,line_segments:q.ordinary.line_segments,edge_count:q.ordinary.edge_count,transfer_count:q.ordinary.transfer_count,accessible:q.ordinary.accessible_journey_valid})),accessible_alternative:{query_id:q2.id,...q2.shortest_accessible},visual_review_status:'awaiting actual revised image view'},null,2)+'\n',{flag:'wx'});
(async()=>{const r=await s.render('A07',dsl,{version_id:'A07-travel-v003',type:'visual',parent_version:'A07-travel-v002',before_view_id:'A07-view-000008',changes:'Clarify that the Q2 S05 transfer prohibition is for accessible trips by changing the notice prefix from ordinary route to accessibility',stem:'travel-card',width:720,height:1280,purpose:'A07 phone travel card complete ordinary and accessible routes'});process.stdout.write(JSON.stringify({ok:r.ok,http_status:r.http_status,image:r.image_path,meta:r.meta_path,dimensions:r.png_dimensions,error:r.error_summary})+'\n');})().catch(e=>{process.stderr.write(String(e.stack??e));process.exitCode=1;});
