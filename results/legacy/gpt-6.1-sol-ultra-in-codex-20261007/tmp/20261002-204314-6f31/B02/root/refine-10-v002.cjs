const fs=require('node:fs'),path=require('node:path');let d=fs.readFileSync(path.join(__dirname,'case-10-v001.snapshot'),'utf8');
// Static source audit before any first service submission; not a visual iteration.
d=d.replace(/(<Positioned left="1434" top=")319(" width="99" height="45">)/,'$1'+'284'+'$2');
// Replace only the three morning schedule fill/label pairs, not shared branding.
for(const top of [402,494,586])d=d.replace(new RegExp('(<Positioned left="455" top="'+top+'"[\\s\\S]*?<Container[^>]*?color=")#789588("[^>]*?/>\\s*</Positioned>)'),'$1#C8D4C3$2');
for(const top of [401,493,585])d=d.replace(new RegExp('(<Positioned left="470" top="'+top+'"[\\s\\S]*?<Text[^>]*?color=")#F5EBDD("[^>]*?>)'),'$1#263C50$2');
fs.writeFileSync(path.join(__dirname,'case-10-v002.snapshot'),d,{flag:'wx'});
fs.writeFileSync(path.join(__dirname,'static-refinement-10-v002.json'),JSON.stringify({scope:'pre-service source refinement based on independent audit; no visual claim',changes:'18:15标签升到轴上第二层，上午班底色改浅sage tint配墨蓝文字，提高可读性。'},null,2)+'\n',{flag:'wx'});
