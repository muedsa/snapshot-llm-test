const fs=require('fs'),path=require('path');
const dir=__dirname;
let source=fs.readFileSync(path.join(dir,'sidecar-audit.cjs'),'utf8');
source=source.replace('r.source===sourceRows[r.line-1]',"r.source===(/leading XML indentation removed/.test(e.printing_policy)?sourceRows[r.line-1].trimStart():sourceRows[r.line-1])");
source=source.replace("'sidecar-audit-v001.json'","'sidecar-audit-v002.json'");
source=source.replace("const result={schema_version:1,", "const result={schema_version:1,supersedes:'sidecar-audit-v001.json',correction:'v001 comparison falsely required XML indentation in printed snippets 03/04; the declared policy explicitly removes leading XML indentation while preserving literal interior spaces. v002 uses that documented rule. Original failed test/results preserved.',");
fs.writeFileSync(path.join(dir,'sidecar-audit-v002.cjs'),source,{flag:'wx'});
require('./sidecar-audit-v002.cjs');
