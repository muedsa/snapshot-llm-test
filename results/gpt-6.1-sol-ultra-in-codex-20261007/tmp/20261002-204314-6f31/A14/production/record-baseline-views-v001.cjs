'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const lines=[1,1,2,1,1,1,2,2],observations=[
'Original K01 actual full image: 开始,林川,开放,09:00,brand anddate complete;1 title line,1speaker line; readable clear check badge and safe margins.',
'Original K02 actual full image: full title,周禾 / 许宁,满额,09:40 visible;1 title line,1speaker line; distinct solid-square/full badge.',
'Original K03 actual full image: original title complete but last级 sits alone on second line. Speaker顾行,候补,10:20 complete. Generic title size rule should avoid singleton tail.',
'Original K04 actual full image: literal A < B & C > D and all Chinese title displayed,苏言/open/11:00 complete.1title line,1speaker line,no entities or tag interpretation.',
'Original K05 actual full image: full Color, Alpha & Contrast / 从颜色到可读性,孟澄/open/13:00 readable.1title line,1speaker line.',
'Original K06 actual full image: canceled card retains full title,许宁,取消 and13:40. Additional 本场取消 plus redcross make state explicit, unchanged non-gray main system.1title line.',
'Original K07 actual full image: full title on2lines, first line ends视 and second觉检查; improve balanced layout generically. Long Northstar Research · 林川 complete on1speaker line;候补/14:20 visible.',
'Original K08 actual full image: full long title withcurly quotes on2lines,周禾/open/15:00 complete. Could improve balance by same long-title rule used across all titles>26 visualunits.'
];
const views=[];
for(let i=0;i<8;i++){
const id='K'+String(i+1).padStart(2,'0'),req=String(i+1).padStart(6,'0'),image_path=path.join(root,'tmp/20261002-204314-6f31/A14/requests/A14-request-'+req+'/response.png');
const view=s.view('A14',image_path,{tool:'view_image',reviewer:'invoice_producer',version_id:'A14-v001-'+id,case_id:id,observation:observations[i],title_line_count:lines[i],speaker_line_count:1});
views.push(view);
s.iteration('A14',{type:'baseline',version_id:'A14-v001-'+id,parent_version:null,case_id:id,completed:true,phase:'actual-image-reviewed',request_id:'A14-request-'+req,image_path,after_view_id:view.id,observation:observations[i],unresolved_issues:i===2?['Last title character isolated on second line.']:i===6?['Word视觉 split over title lines.']:[]});
}
fs.writeFileSync(path.join(__dirname,'producer-baseline-reviews-v001.json'),JSON.stringify(views,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(views.map(v=>({id:v.case_id,view_id:v.id,title_lines:v.title_line_count}))));
