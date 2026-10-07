// Pure DSL scaffold shared by the two A17 producers. No request, view or state write.
const {Canvas}=require('../_suite/dsl.cjs');
const palette={ink:'#172D48',muted:'#536780',blue:'#2964D8',border:'#D8E3EE',navy:'#172D48',mint:'#7EE1C3'};
function handbook({page,title,intro,principles,codeLines,codeScope,exampleWidget,figureTitle,figureNotes,leftTitle,leftBody,rightTitle,rightBody}){
 if(codeLines.length<8||codeLines.length>18)throw Error('Print8–18 true lines');
 const c=new Canvas(1200,1600,{background:'#F1F4F8',font:'Inter,Noto Sans CJK SC'}),tx=(x,y,w,h,t,size=24,color=palette.ink,o={})=>c.text(x,y,w,h,t,size,color,o);
 tx(64,52,780,38,'SNAPSHOT / 从文字到图片',24,palette.blue,{bold:true});tx(944,52,208,38,`入门手册 ${String(page).padStart(2,'0')} / 04`,24,palette.muted,{align:'RIGHT'});
 tx(64,112,1088,74,title,46,palette.ink,{bold:true});tx(64,205,1088,92,intro,28,palette.muted,{lineHeight:1.35});
 c.rect(64,315,1088,2,palette.border);tx(64,341,1088,44,'先记住这些规则',28,palette.ink,{bold:true});
 principles.forEach((t,i)=>{c.circle(73,406+i*43,4,palette.blue);tx(92,386+i*43,1060,43,t,24,palette.ink);});
 tx(64,544,650,38,'可运行 DSL / 印刷片段',26,palette.ink,{bold:true});
 c.rect(64,594,650,554,palette.navy,{radius:14});tx(86,610,606,526,codeLines.join('\n'),20,'#F4F8FC',{font:'DejaVu Sans Mono',lineHeight:1.35});
 tx(64,1155,1088,32,codeScope,24,palette.muted);
 // The exact independent example's root widget is directly nested here.
 c.at(748,606,400,240,exampleWidget);tx(748,873,400,41,figureTitle,26,palette.ink,{bold:true});tx(748,926,400,192,figureNotes,24,palette.muted,{lineHeight:1.4});
 [[64,520,leftTitle,leftBody],[608,544,rightTitle,rightBody]].forEach(([x,w,t,b])=>{c.rect(x,1212,w,242,'#FFFFFF',{radius:14,border:'1 SOLID '+palette.border});tx(x+22,1233,w-44,38,t,26,palette.ink,{bold:true});tx(x+22,1283,w-44,148,b,24,palette.muted,{lineHeight:1.35});});
 c.rect(64,1496,1088,1,palette.border);tx(64,1513,820,38,'真实请求 → 实际看图 → 保存原图与完整 .snapshot',24,palette.muted);tx(1044,1513,108,38,String(page).padStart(2,'0'),24,palette.blue,{bold:true,align:'RIGHT'});
 return c.toString();
}
module.exports={handbook,palette};
