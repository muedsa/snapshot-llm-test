const fs=require('node:fs'),path=require('node:path'),lib=require('./lib-independent-audit-v001.cjs');
const before=path.join(__dirname,'drafts-v001'),out=path.join(__dirname,'drafts-v002');fs.mkdirSync(out,{recursive:true});
const read=n=>fs.readFileSync(path.join(before,n),'utf8');
const system=JSON.parse(read('design-system.json'));
system.scope='实际最终十触点候选所用规则；审查范围限于B02，未声明30题套件完成';
system.palette.core.find(c=>c.name==='clay').actual_role='补丁与重点动作/已完成数据/交接强调';
system.evidence.note='已与selection-v001.json的实际最终候选源hash逐项核对；独立审计记录另附。';
const files={'project-brief.md':read('project-brief.md'),'design-system.json':JSON.stringify(system,null,2)+'\n','touchpoint-map.json':read('touchpoint-map.json')};
for(const [n,s]of Object.entries(files))fs.writeFileSync(path.join(out,n),s,{flag:'wx'});
const manifest={schema_version:1,created_at:new Date().toISOString(),reviewer:'b01_independent_audit',scope:'B02额外项目交付文档，v002修正真实palette用途；另行审计最终候选一致性',parent:'drafts-v001',changes:[{file:'design-system.json',field:'palette.core.clay.actual_role',before:'补丁与重点动作/已完成数据/下午班',after:'补丁与重点动作/已完成数据/交接强调',reason:'实际case10下午班为墨蓝#263C50，陶土用于交接带/强调，依据真实DSL修正'},{file:'design-system.json',field:'scope/evidence.note',reason:'说明核对最终候选的B02限定范围'}],files:Object.entries(files).map(([n,s])=>({name:n,path:path.join(out,n),sha256:lib.hash(Buffer.from(s))})),source_hashes_unchanged:true};
fs.writeFileSync(path.join(out,'draft-manifest.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
const base=path.resolve(__dirname,'..'),events=[
 {id:'B02-independent-view-000001',case_id:'case-04',request_id:'B02-request-000011',version_id:'B02-version-000011',file:'requests/B02-request-000011/response.png',viewed_at:'2026-10-06T06:00:38Z',observation:'实际以view_image original打开完整1200×1400服务PNG。剪刀两条刀刃并行向上、双环柄朝下，配关闭示意/刀刃并拢注释，与归位指令一致；六针可直接数出，剪刀/拆线器/软尺数量及四类工具T03表达无歧义。全文和页脚完整，保留。'},
 {id:'B02-independent-view-000002',case_id:'case-06',request_id:'B02-request-000013',version_id:'B02-version-000013',file:'requests/B02-request-000013/response.png',viewed_at:'2026-10-06T06:01:04Z',observation:'实际以view_image original打开完整1500×1100服务PNG。四步定位/固定/平针/收线与独立几何顺序明确；第一栏短双箭头处于损伤右侧与补丁右缘间，未跨全补丁宽，并注明本例10mm/边及非比例图。三行正文、完成检查和下部安全/洗标说明均完整，无裁切，保留。'}
].map(({file,...e})=>({...e,task_id:'B02',reviewer:'b01_independent_audit',tool:'view_image',detail:'original',image_path:path.join(base,file),sha256:lib.hash(fs.readFileSync(path.join(base,file))),actual_view:true,timezone:'UTC',time_note:'viewed_at为查看后读取clock工具取得的UTC完成确认时间，并非view_image原生时间戳；顺序与实际工具调用一致。'}));
fs.writeFileSync(path.join(__dirname,'independent-view-import-v001.json'),JSON.stringify({schema_version:1,created_at:new Date().toISOString(),actual_extra_image_view_count:2,events},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({draft_directory:out,files:manifest.files,view_import_file:path.join(__dirname,'independent-view-import-v001.json'),actual_extra_image_views:2}));
