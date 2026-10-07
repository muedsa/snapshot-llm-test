const fs=require('node:fs'),path=require('node:path'),rd=__dirname;
const report=fs.readFileSync(path.join(rd,'report-round-v002.md'),'utf8')+'\n\n归档过程：shared包装脚本试图由Node启动子进程时发生真实EPERM，在publisher执行前失败，无产物或状态变更。错误保留于round-orchestration-000001.json；恢复为通过exec_command分别顺序直接调用publisher、真实completed边界和archive工具，每步核成功再下一步，不请求扩大权限。服务生成与视觉质量没有受影响。\n';
fs.writeFileSync(path.join(rd,'report-round-v003.md'),report,{flag:'wx'});
const manifest=JSON.parse(fs.readFileSync(path.join(rd,'publish-manifest-v002.json'),'utf8'));manifest.additional_files.find(a=>a.relative_output==='round-01/snapshot-usage.md').source='report-round-v003.md';
fs.writeFileSync(path.join(rd,'publish-manifest-v003.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
