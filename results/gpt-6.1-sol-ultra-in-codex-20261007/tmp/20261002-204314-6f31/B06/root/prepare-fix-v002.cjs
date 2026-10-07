const fs=require('node:fs'),path=require('node:path');let source=fs.readFileSync(path.join(__dirname,'build-v001.cjs'),'utf8');
function change(a,b){if(!source.includes(a))throw Error('Missing exact source:'+a);source=source.replace(a,b);}
change("function save(id,c,extra){const p=", "function save(id,c,extra){if(id==='case-09')return;const p=");
source=source.replaceAll("+'-v001.snapshot'","+'-v002.snapshot'").replaceAll("+'-metadata-v001.json'","+'-metadata-v002.json'");
change("c.line(195,638,195,819,'#A58761',3)","c.line(195,638,195,651,'#A58761',3);c.line(195,802,195,819,'#A58761',3)");
change("c.line(473,693,473,874,orange,3)","c.line(473,693,473,708,orange,3);c.line(473,854,473,874,orange,3)");
change("r.next+'\\n14:'+String(r.ready).padStart(2,'0')+'领取'", "r.next+'\\n14:'+String(r.ready).padStart(2,'0')+(i===1?'':'领取')");
change("i===1?22:28,'#412F2D',true);});", "i===1?22:28,'#412F2D',true);if(i===1)txt(c,157,y+117,317,44,'小满 · 14:35领取',24,'#B6CDCA');});");
change("确认重要文件已有可访问的备份。\\n家庭照片与视频保留。", "确认重要文件已有\\n可访问的备份。\\n家庭照片与视频保留。");
change("s[0],27,purple,true);txt(c,x+8,493,w-16,51,s[1]+'GB',30,purple,true)","s[0],27,i===0?'#FFFFFF':purple,true);txt(c,x+8,493,w-16,51,s[1]+'GB',30,i===0?'#FFFFFF':purple,true)");
change("wx('production-notes-v001.json'", "wx('production-notes-v002.json'");
fs.writeFileSync(path.join(__dirname,'build-v002.cjs'),source,{flag:'wx'});console.log('source-v002-prepared');
