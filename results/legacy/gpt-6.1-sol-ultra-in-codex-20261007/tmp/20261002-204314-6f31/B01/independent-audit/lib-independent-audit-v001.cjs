const fs=require('fs'),path=require('path'),crypto=require('crypto');
const hash=data=>crypto.createHash('sha256').update(data).digest('hex');
const readLines=file=>fs.existsSync(file)?fs.readFileSync(file,'utf8').split(/\r?\n/).filter(Boolean).map(x=>JSON.parse(x)):[];
const attrs=s=>Object.fromEntries([...s.matchAll(/(\w+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g)].map(m=>[m[1],m[2]??m[3]]));
function analyseDSL(file){
 const raw=fs.readFileSync(file,'utf8');
 const outer=attrs(raw.match(/<Container\b([^>]*)>/)?.[1]??'');
 const texts=[],positions=[];
 for(const m of raw.matchAll(/<Positioned\b([^>]*)>([\s\S]*?)<\/Positioned>/g)){
  const a=attrs(m[1]),p={x:Number(a.left??0),y:Number(a.top??0),width:Number(a.width),height:Number(a.height),child_start:m[2].slice(0,150)};positions.push(p);
  const t=m[2].match(/<Text\b([^>]*)>([\s\S]*?)<\/Text>/);
  if(t){const ta=attrs(t[1]);texts.push({...p,font_size:Number(ta.fontSize),text:t[2].replace(/<Raw>|<\/Raw>|<!\[CDATA\[|\]\]>/g,'').replace(/<[^>]+>/g,''),text_attributes:ta});}
 }
 return {file,sha256:hash(Buffer.from(raw)),width:Number(outer.width),height:Number(outer.height),has_image:!!raw.match(/<Image\b/),external_reference:!!raw.match(/(?:https?:\/\/|file:\/\/)/),tags:[...new Set([...raw.matchAll(/<([A-Za-z]\w*)\b/g)].map(m=>m[1]))].sort(),text_count:texts.length,position_count:positions.length,texts,positions};
}
function pngDimensions(file){const b=fs.readFileSync(file);if(b.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw new Error('Not PNG: '+file);return {width:b.readUInt32BE(16),height:b.readUInt32BE(20),bytes:b.length,sha256:hash(b)};}
function integrityCheck({caseId,dslFile,pngFile,tempDir}){
 const dsl=analyseDSL(dslFile),png=pngFile&&fs.existsSync(pngFile)?pngDimensions(pngFile):null,checks=[];
 const check=(name,ok,details)=>checks.push({name,ok,details});
 check('positive_canvas',dsl.width>0&&dsl.height>0,{width:dsl.width,height:dsl.height});
 check('pure_dsl_no_images',!dsl.has_image,{tags:dsl.tags});
 check('self_contained_no_remote_references',!dsl.external_reference,{});
 check('all_text_boxes_within_canvas',dsl.texts.every(t=>t.x>=0&&t.y>=0&&t.width>0&&t.height>0&&t.x+t.width<=dsl.width+1e-6&&t.y+t.height<=dsl.height+1e-6),{offenders:dsl.texts.filter(t=>t.x<0||t.y<0||t.width<=0||t.height<=0||t.x+t.width>dsl.width+1e-6||t.y+t.height>dsl.height+1e-6)});
 if(png){
  check('png_dimensions_match_dsl',png.width===dsl.width&&png.height===dsl.height,{png:{width:png.width,height:png.height},dsl:{width:dsl.width,height:dsl.height}});
  const requests=readLines(path.join(tempDir,'requests.jsonl')),views=readLines(path.join(tempDir,'views.jsonl'));
  const match=requests.find(r=>r.ok&&r.response_sha256===png.sha256&&r.body_sha256===dsl.sha256&&r.case_id===caseId);
  check('actual_successful_service_request_body_and_response_pair',!!match,match?{request_id:match.id,server_request_id:match.request_id,http_status:match.http_status}:{});
  check('preserved_raw_response_matches_png',!!match&&fs.existsSync(match.response_file)&&hash(fs.readFileSync(match.response_file))===png.sha256,match?{response_file:match.response_file}:{});
  const actualViews=views.filter(v=>v.sha256===png.sha256&&v.case_id===caseId&&v.tool&&v.viewed_at);
  check('root_actual_view_for_final_png',actualViews.some(v=>v.reviewer==='root'),{view_ids:actualViews.map(v=>v.id)});
 }
 return {case_id:caseId,dsl,png,checks,passed:checks.every(c=>c.ok)};
}
module.exports={hash,readLines,attrs,analyseDSL,pngDimensions,integrityCheck};
