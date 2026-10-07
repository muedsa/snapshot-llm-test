const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs'),rd=__dirname,d=s.taskDirs('A22');
const map=JSON.parse(fs.readFileSync(path.join(rd,'layout-map-v002.json'),'utf8'));map.version_id='A22-round-02-dashboard-v003';map.created_at=new Date().toISOString();
const old='2026-09 利润 -5,632；2026-08 退款率13.32%，净收入减少10,000。',now='2026-09 利润 -5,632；2026-08 退款率13.32%，净收入较更正前少10,000。';
if(map.texts.find(t=>t.id==='conclusion-detail').text!==old)throw Error('Unexpected detail');map.texts.find(t=>t.id==='conclusion-detail').text=now;
fs.writeFileSync(path.join(rd,'layout-map-v003.json'),JSON.stringify(map,null,2)+'\n',{flag:'wx'});
const raw=fs.readFileSync(path.join(d.temp,'requests/A22-request-000004/input.snapshot'),'utf8');if(raw.split(old).length!==2)throw Error('Expected unique detail');
(async()=>{const r=await s.render('A22',raw.replace(old,now),{version_id:map.version_id,parent_version:'A22-round-02-dashboard-v002',type:'visual',before_view_id:'A22-view-000005',round_id:'round-02',width:1600,height:1000,changes:'将净收入减少10000明确为较更正前少10000，避免误解为实际月环比（Aug比Jul+1932）。'});console.log(JSON.stringify({ok:r.ok,image_path:r.image_path,meta_path:r.meta_path,version_id:r.version_id}));})().catch(e=>{console.error(e.stack);process.exitCode=1;});
