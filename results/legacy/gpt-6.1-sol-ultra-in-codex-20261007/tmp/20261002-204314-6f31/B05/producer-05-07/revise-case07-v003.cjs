const fs=require('node:fs'),path=require('node:path');
const {Canvas}=require('../../_suite/dsl.cjs');const {txt,P}=require('../ui.cjs');
const p=__dirname,prev=fs.readFileSync(path.join(p,'case-07-v002.snapshot'),'utf8');
const old=new Canvas(1600,1100),fresh=new Canvas(1600,1100);
txt(old,100,845,521,39,'衣物已放入？请确认舱门关闭。',28,'#D3E4E4');
txt(fresh,100,819,521,53,'衣物已放入？请确认舱门关闭。',28,'#D3E4E4');
if(prev.split(old.children[0]).length!==2)throw new Error('Expected original note once');
let d=prev.replace(old.children[0],fresh.children[0]);
// Move the entire circular door subassembly up 22px, leaving a clean gap to the note.
const od=new Canvas(1600,1100),nd=new Canvas(1600,1100);
function door(c,dy){c.circle(360,668+dy,171,'#274650',{border:'12 SOLID #526F76'});c.circle(360,668+dy,142,'#D2E8E1',{border:'5 SOLID #92B8AF'});c.circle(360,668+dy,126,'#739B9A');c.polyline([[247,694],[270,674],[298,689],[326,670],[354,685],[382,670],[410,688],[438,675],[470,694]].map(([x,y])=>[x,y+dy]),'#C7EAE0',15,{roundCaps:true});c.polyline([[264,725],[286,707],[313,725],[340,707],[367,725],[396,707],[426,725],[451,709]].map(([x,y])=>[x,y+dy]),'#B6D6CE',10,{roundCaps:true});}
door(od,0);door(nd,-22);
const oldDoor=od.children.join('\n'),newDoor=nd.children.join('\n');
if(d.split(oldDoor).length!==2)throw new Error('Expected complete door subtree once');d=d.replace(oldDoor,newDoor);
fs.writeFileSync(path.join(p,'case-07-v003.snapshot'),d,{flag:'wx'});
const m=JSON.parse(fs.readFileSync(path.join(p,'case-07-metadata-v002.json'),'utf8'));m.created_at=new Date().toISOString();m.parent_version='case-07-v002.snapshot';m.revision_reason='Actual request-12 view: door-check note sat against deep-card bottom and lower edge was cropped. Raised note y845→819, increased box39→53px, and moved door22px upward so note clears the ring and lower rounded edge.';m.checks.visual_verified=false;m.checks.visual_review_owner='root';
fs.writeFileSync(path.join(p,'case-07-metadata-v003.json'),JSON.stringify(m,null,2),{flag:'wx'});
fs.writeFileSync(path.join(p,'producer-visual-observation-case07-v001.json'),JSON.stringify({created_at:new Date().toISOString(),viewer:'b04_cases_05_07',task_id:'B05',viewed_image:'tmp/20261002-204314-6f31/B05/requests/B05-request-000012/response.png',view_time:'2026-10-06T11:19:40Z',view_time_source:'clock immediately after view tool',observations:['5372 already checked, C1 waiting-to-start, order/period/4yuan and return-without-charge text are complete','The note about loading clothing and closing the door is too close to the lower rounded edge and visibly clipped below'],changes:['Raise note26px and increase its layout height14px','Move circular door and waves up22px to preserve vertical gap to raised note'],revision:'case-07-v003.snapshot',pending:'root real render and subsequent image inspection',new_visual_pass_claim:false},null,2),{flag:'wx'});
console.log(JSON.stringify({snapshot:path.join(p,'case-07-v003.snapshot'),metadata:path.join(p,'case-07-metadata-v003.json')}));
