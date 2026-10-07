'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..');
const s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const before=fs.readFileSync(path.join(__dirname,'invoice-page-01-v001.snapshot'),'utf8');
const fixed=before.replace(/(<Text fontFamily="DejaVu Sans Mono,Noto Sans Mono CJK SC,Noto Sans Mono CJK JP" fontSize=")26("[^>]*textAlign="RIGHT"[^>]*><Raw><!\[CDATA\[\d+\.\d{2}\]\]><\/Raw><\/Text>)/g,'$128$2')
  .replace('fontSize="34" color="#147D7E" fontStyle="BOLD" textAlign="RIGHT"','fontSize="28" color="#147D7E" fontStyle="BOLD" textAlign="RIGHT"');
// Exactly 8 item amounts + the payable amount change; quantities remain 26px.
const changed=(before.match(/fontSize="26"[^>]*textAlign="RIGHT"[^>]*><Raw><!\[CDATA\[\d+\.\d{2}\]\]>/g)||[]).length;
if(changed!==8||fixed===before||fixed.includes('fontSize="34"'))throw new Error('Unexpected monetary replacement');
fs.writeFileSync(path.join(__dirname,'invoice-page-01-v002.snapshot'),fixed,{flag:'wx'});
const map=JSON.parse(fs.readFileSync(path.join(__dirname,'text-map-draft-v002.json'),'utf8'));
for(const e of map.text_entries)if(e.page===1&&(/item-\d+-(unit-price|line-amount)/.test(e.id)||e.id==='payable-amount'))e.font_size=28;
map.status='awaiting_actual_v002_review';
map.monetary_alignment={font_family:'DejaVu Sans Mono',all_currency_strings_have_two_decimals:true,all_amount_font_sizes:28,unit_price:{x:784,width:140,font_size:28,text_align:'RIGHT'},line_amount:{x:964,width:152,font_size:28,text_align:'RIGHT'},summary_rows:{x:940,width:176,font_size:28,text_align:'RIGHT'},payable:{x:910,width:206,font_size:28,text_align:'RIGHT',font_style:'BOLD'},note:'All money strings use same monospaced size and same right edge within each amount column; the payable retains bold teal emphasis.'};
fs.writeFileSync(path.join(__dirname,'text-map-draft-v003.json'),JSON.stringify(map,null,2)+'\n',{flag:'wx'});
(async()=>{
const result=await s.render('A11',fixed,{version_id:'A11-v002-p01',parent_version:'A11-v001-p01',type:'visual',stem:'invoice-page-01',width:1200,height:1600,case_id:'page-01',before_view_id:'A11-view-000001',changes:'Actual independent pixel/whole-page inspection found different monetary font sizes shifted decimal points horizontally despite common right edge. Set every monetary amount to DejaVu Sans Mono28px, preserving existing right edges and bold teal payable.',purpose:'A11 same-size currency decimal column alignment visual correction'});
console.log(JSON.stringify({ok:result.ok,meta_path:result.meta_path,image_path:result.image_path,dimension_error:result.dimension_error??null}));
})().catch(e=>{console.error(e);process.exitCode=1});
