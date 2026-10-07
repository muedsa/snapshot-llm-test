const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base=path.resolve('tmp/20261002-204314-6f31'),task=path.join(base,'A17'),out=__dirname;
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const requests=fs.readFileSync(path.join(task,'requests.jsonl'),'utf8').trim().split('\n').map(JSON.parse).filter(r=>r.type==='render'&&r.ok);
const latest=stem=>{const r=requests.filter(r=>r.case_id===stem).at(-1);if(!r)throw Error('No real successful '+stem);return JSON.parse(fs.readFileSync(path.join(task,'requests',r.id,'render-result.json'),'utf8'));};
const fonts=fs.readFileSync(path.join(base,'_suite','shared-fonts-000001-response.txt'),'utf8').trim().split(/\r?\n/);
const pairs=[];for(let page=1;page<=4;page++){
 const no=String(page).padStart(2,'0'),e=latest('example-'+no),h=latest('handbook-'+no),es=fs.readFileSync(e.dsl_path,'utf8'),hs=fs.readFileSync(h.dsl_path,'utf8');
 const widget=es.trim().match(/^<Snapshot\b[^>]*>\r?\n([\s\S]*)\r?\n<\/Snapshot>$/)?.[1];if(!widget)throw Error('Need actual single root Widget source');
 const sections=[];const masked=hs.replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g,(_,s)=>{const i=sections.push(s)-1;return `@CD${i}@`;});
 const code=masked.match(/<Text\b[^>]*fontSize="20"[^>]*>([\s\S]*?)<\/Text>/)?.[1];if(!code)throw Error('Missing real20 printed code widget');
 const printed=code.replace(/<[^>]+>/g,'').replace(/@CD(\d+)@/g,(_,i)=>sections[+i]);
 const lines=es.trimEnd().split(/\r?\n/),plines=printed.split('\n');let matched,source_rows;
 if(page<=2){const offset=page===1?0:5;matched=plines.every((s,i)=>s===lines[i+offset]);source_rows=plines.map((source,i)=>({line:i+offset+1,source}));}
 else{source_rows=plines.map(s=>{const m=s.match(/^(\d{3}) (.*)$/);if(!m)throw Error('Bad actual numbered code row');return {line:+m[1],source:m[2]};});matched=source_rows.every(r=>r.source===lines[r.line-1].trimStart());}
 const styles=[...masked.matchAll(/<Text\b([^>]*)>/g)].map(m=>({font:+(m[1].match(/fontSize="([^\"]+)"/)?.[1]??NaN),family:m[1].match(/fontFamily="([^\"]+)"/)?.[1]??null}));
 const families=[...new Set(styles.flatMap(s=>s.family?s.family.split(','):[]))];
 const pair={page,example_meta:e,handbook_meta:h,complete_example_sha256:sha(es),submitted_example_hash_matches:e.body_sha256===sha(es),submitted_handbook_hash_matches:h.body_sha256===sha(hs),example_dimensions_pass:e.png_dimensions.width===400&&e.png_dimensions.height===240,handbook_dimensions_pass:h.png_dimensions.width===1200&&h.png_dimensions.height===1600,root_widget_sha256:sha(widget),exact_widget_direct_embedded:hs.includes('<Positioned left="748" top="606" width="400" height="240">'+widget+'</Positioned>'),no_actual_Image_tags:!/<Image\b/.test(masked),printed_count:plines.length,printed_8_to_18_pass:plines.length>=8&&plines.length<=18,printed_fragment_matches_submitted_full_source:matched,printed_source_rows:source_rows,omitted_source_rows:lines.map((_,i)=>i+1).filter(i=>!source_rows.some(r=>r.line===i)),actual_code_widgets_font20:styles.filter(s=>s.font===20).length,all_other_explicit_Text_fonts_at_least24:styles.filter(s=>s.font!==20&&Number.isFinite(s.font)).every(s=>s.font>=24),no_other_Text_with_font_below24:styles.filter(s=>Number.isFinite(s.font)&&s.font<24).every(s=>s.font===20),actual_font_families:families,all_fonts_installed:families.every(f=>fonts.includes(f)),source_check_is_auxiliary_to_real_visual_review:true};
 pair.all_computational_checks_pass=['submitted_example_hash_matches','submitted_handbook_hash_matches','example_dimensions_pass','handbook_dimensions_pass','exact_widget_direct_embedded','no_actual_Image_tags','printed_8_to_18_pass','printed_fragment_matches_submitted_full_source','all_other_explicit_Text_fonts_at_least24','no_other_Text_with_font_below24','all_fonts_installed'].every(k=>pair[k]);pairs.push(pair);
}
const result={task_id:'A17',reviewer:'/root/a17_auditor',created_at:new Date().toISOString(),pairs,all_computational_checks_pass:pairs.every(p=>p.all_computational_checks_pass),visual_review_not_inferred:true};
fs.writeFileSync(path.join(out,'source-pair-audit-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result,null,2));
