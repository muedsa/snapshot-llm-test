const fs=require('node:fs'),path=require('node:path');let d=fs.readFileSync(path.join(__dirname,'case-10-v001.snapshot'),'utf8');
d=d.replace('<Positioned left="280" top="223" width="276" height="42">','<Positioned left="229" top="223" width="460" height="42">').replace('14:00 开始','14:00 开始 / 15:30 完成').replace('15:30 完成</Raw>','15:30 完成</Raw>');
d=d.replace('<![CDATA[15:30 完成]]>','<![CDATA[顺时针一圈 · 90分钟]]>').replace('<Positioned left="283" top="884" width="286" height="43">','<Positioned left="240" top="884" width="400" height="43">');
// Move complete phase rows, including dividers, by +22 / +44.
for(const [from,to] of [[774,818],[787,831],[829,873],[870,914],[628,650],[641,663],[683,705],[724,746]])d=d.replaceAll('top="'+from+'"','top="'+to+'"');
fs.writeFileSync(path.join(__dirname,'case-10-v002.snapshot'),d,{flag:'wx'});
fs.writeFileSync(path.join(__dirname,'iterate-10-v002.json'),JSON.stringify({type:'visual',parent_version:'B01-version-000004',before_view_id:'B01-view-000004',changes:'右列阶段间隔146改168px并整体移动各阶段分隔线/文字；起止时间并置于环上闭合点，下方改顺时针一圈90分钟。'},null,2)+'\n',{flag:'wx'});
