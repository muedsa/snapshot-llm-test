const fs=require('node:fs'),path=require('node:path'),s=require('../suite.cjs'),d=s.taskDirs('shared'),p=path.join(d.output,'gallery.md'),old=fs.readFileSync(p,'utf8');
fs.writeFileSync(path.join(__dirname,'gallery-before-title-repair-v001.md'),old,{flag:'wx'});
const legacy=t=>String(t).replace(/[\[\]<>]/g,'').replace(/\r?\n/g,' ');
const safe=t=>String(t).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('[','\\[').replaceAll(']','\\]').replace(/\r?\n/g,' ');
let text=old;const corrections=[];
for(const t of s.readState().tasks)for(const a of t.artifacts){if(!a.title||!/[<>\[\]]/.test(a.title))continue;const from=legacy(a.title),to=safe(a.title);if(!text.includes(from))throw Error('Expected prior title missing '+a.id);text=text.replaceAll(from,to);corrections.push({artifact_id:a.id,task_id:t.id,original_title:a.title,prior_generated_title:from,corrected_markdown_title:to});}
if(!corrections.length)throw Error('No genuine title correction');fs.writeFileSync(p,text);
const audit=s.inspectLinks(p),record={run_id:s.readState().run_id,corrected_at:new Date().toISOString(),scope:'Preserve literal title characters in Markdown heading and alt text; original PNG/DSL untouched.',corrections,links_passed:!audit.issues.length,link_issues:audit.issues,new_HTTP:0,new_render:0,new_image_views:0};fs.writeFileSync(path.join(__dirname,'title-repair-v001.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});if(audit.issues.length)throw Error(JSON.stringify(audit.issues));console.log(JSON.stringify(record,null,2));
