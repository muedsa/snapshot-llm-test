const fs=require('fs'),path=require('path'),crypto=require('crypto');
const run='20261002-204314-6f31',root=path.resolve(__dirname,'../../..');
const docs=[
 ['A10-request-000001','widgets/painting/opacity/','Whole subtree opacity applied after opaque blue replaces red; distinguishes group alpha from per-color alpha.'],
 ['A10-request-000002','widgets/painting/image-filtered/','ImageFiltered reads child subtree; Gaussian pixels can extend beyond layout. Parser provides Gaussian output bounds automatically.'],
 ['A10-request-000003','widgets/painting/color-filtered/','MULTIPLY can color transparent gaps within determined child painting bounds; cannot assume it only touches opaque content.'],
 ['A10-request-000004','widgets/painting/clip-oval/','Square child produces circle; clipping must enclose complete filtered effect for experiment6.'],
];
const d=docs.map(([id,url,application])=>{let p=path.resolve(__dirname,'../requests',id,'readable.txt');return {request_id:id,url:'https://snapshot.muedsa.com/'+url,cache_path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),application,reused_existing_successful_request:true,new_http_requests:0};});
let p=path.resolve(__dirname,'../../_suite/requests/shared-request-000001/readable.txt');d.push({request_id:'shared-request-000001',url:'https://snapshot.muedsa.com/widgets/painting/backdrop-filter/',cache_path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),application:'BackdropFilter samples already painted background and needs explicit rounded clip; foreground text must be outside filter or child foreground remains clear.',reused_existing_successful_request:true,new_http_requests:0});
const r={task_id:'A10',run_id:run,reviewer:'a10_audit_resume',read_at:new Date().toISOString(),docs:d,scope:'Actual read of cached successful official documentation; no additional HTTP claims.'};
fs.writeFileSync(path.join(__dirname,'document-read-v002.json'),JSON.stringify(r,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({written:'document-read-v002.json',documents:d.length}));
