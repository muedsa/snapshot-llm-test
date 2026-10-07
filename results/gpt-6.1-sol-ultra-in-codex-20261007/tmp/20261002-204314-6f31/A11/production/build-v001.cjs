'use strict';
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../../../..');
const suite=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const {Canvas,tag,cdata}=require(path.join(root,'tmp/20261002-204314-6f31/_suite/dsl.cjs'));
const input=JSON.parse(fs.readFileSync(path.join(root,'tasks/A11-bilingual-invoice/inputs/invoice.json'),'utf8'));
const OUT=__dirname;
fs.mkdirSync(OUT,{recursive:true});
const write=(name,value)=>fs.writeFileSync(path.join(OUT,name),typeof value==='string'?value:JSON.stringify(value,null,2)+'\n',{flag:'wx'});
const cents=s=>{const m=/^(\d+)\.(\d{2})$/.exec(s);if(!m)throw new Error('Expected two decimal places');return BigInt(m[1])*100n+BigInt(m[2]);};
const money=n=>{const sign=n<0n?'-':'';const a=n<0n?-n:n;return sign+(a/100n)+'.'+String(a%100n).padStart(2,'0');};
const lines=input.items.map(v=>({...v,unit_cents:cents(v.unit_price),line_cents:cents(v.unit_price)*BigInt(v.quantity)}));
const subtotal=lines.reduce((s,v)=>s+v.line_cents,0n);
const discount=cents(input.discount),shipping=cents(input.shipping),base=subtotal-discount;
const rateParts=input.tax_rate.split('.'),rateNumerator=BigInt(rateParts.join('')),rateDenominator=10n**BigInt(rateParts[1].length);
const exactTaxNumerator=base*rateNumerator;
const tax=(exactTaxNumerator*2n+rateDenominator)/(rateDenominator*2n);
const payable=base+tax+shipping;
const calculated={lines:lines.map(v=>({sku:v.sku,quantity:v.quantity,unit_price:v.unit_price,line_amount:money(v.line_cents),line_amount_cents:String(v.line_cents)})),subtotal:money(subtotal),discount:money(discount),taxable_goods:money(base),tax_rate:input.tax_rate,exact_tax_cents_rational:{numerator:String(exactTaxNumerator),denominator:String(rateDenominator)},exact_tax_amount:'236.658',rounding:'Positive decimal HALF_UP to two decimal places; fixed point BigInt integer arithmetic.',rounded_tax:money(tax),shipping:money(shipping),payable:money(payable),status_changes_amount:false,literal_lines:input.literal_lines};
write('calculated-amounts-v001.json',calculated);
const colors={ink:'#16343D',muted:'#566C72',accent:'#147D7E',line:'#CCDADD',tint:'#F1F6F5',white:'#FFFFFF',green:'#18754D'};
const font='Inter,Noto Sans CJK SC,Noto Sans CJK JP';
const mono='DejaVu Sans Mono,Noto Sans Mono CJK SC,Noto Sans Mono CJK JP';
const map=[];
function text(c,page,id,x,y,w,h,value,size=24,color=colors.ink,opts={}){
  c.text(x,y,w,h,value,size,color,{font,...opts});
  map.push({id,page,source_text:value,source_path:opts.source_path??null,position:{x,y,width:w,height:h},font_family:opts.font??font,font_size:size,color,text_align:opts.align??'START',font_style:opts.bold?'BOLD':'NORMAL',raw_cdata:true});
}
function basePage(page){
  const c=new Canvas(1200,1600,{background:colors.white,font});
  c.rect(64,64,8,100,colors.accent);
  text(c,page,'document-title',94,64,630,64,'结算单 / SETTLEMENT',42,colors.ink,{bold:true});
  text(c,page,'invoice-id',94,132,780,44,input.invoice_id,26,colors.muted,{font:mono,source_path:'invoice_id'});
  text(c,page,'page-number-top',990,80,146,44,String(page).padStart(2,'0')+' / 02',24,colors.muted,{font:mono,align:'RIGHT'});
  c.line(64,198,1136,198,colors.line,2);
  text(c,page,'issued-label',64,222,120,42,'开具日期',24,colors.muted);
  text(c,page,'issued-value',188,222,290,42,input.issued,26,colors.ink,{font:mono,source_path:'issued'});
  text(c,page,'currency-label',660,222,110,42,'币种',24,colors.muted);
  text(c,page,'currency-value',784,222,174,42,input.currency,26,colors.ink,{font:mono,source_path:'currency'});
  text(c,page,'tax-rate-label',982,222,78,42,'税率',24,colors.muted);
  text(c,page,'tax-rate-value',1064,222,72,42,'6%',26,colors.ink,{font:mono,align:'RIGHT',source_path:'tax_rate'});
  c.line(64,1488,1136,1488,colors.line,2);
  text(c,page,'footer-invoice-id',64,1516,730,38,input.invoice_id,20,colors.muted,{font:mono,source_path:'invoice_id'});
  text(c,page,'footer-page-number',934,1516,202,38,'第 '+page+' 页 / 共 2 页',20,colors.muted,{align:'RIGHT'});
  return c;
}
function page1(){
  const c=basePage(1);
  c.rect(64,298,504,116,colors.tint,{radius:8});
  c.rect(592,298,544,116,colors.tint,{radius:8});
  text(c,1,'seller-label',84,314,420,38,'卖方 / SELLER',24,colors.muted);
  text(c,1,'seller-value',84,356,464,48,input.seller,28,colors.ink,{bold:true,source_path:'seller'});
  text(c,1,'buyer-label',612,314,480,38,'买方 / BUYER',24,colors.muted);
  text(c,1,'buyer-value',612,356,504,48,input.buyer,26,colors.ink,{bold:true,source_path:'buyer'});
  const top=456,head=64,rowH=118,xs=[64,244,696,768,948,1136];
  c.rect(64,top,1072,head,colors.ink,{radius:4});
  text(c,1,'table-head-sku',84,top+16,144,40,'SKU',24,colors.white,{bold:true,font:mono});
  text(c,1,'table-head-name',264,top+16,412,40,'名称 / DESCRIPTION',24,colors.white,{bold:true});
  text(c,1,'table-head-quantity',700,top+16,60,40,'数量',24,colors.white,{bold:true,align:'RIGHT'});
  text(c,1,'table-head-unit-price',784,top+16,140,40,'单价',24,colors.white,{bold:true,align:'RIGHT'});
  text(c,1,'table-head-line-amount',964,top+16,152,40,'行金额',24,colors.white,{bold:true,align:'RIGHT'});
  lines.forEach((v,i)=>{
    const y=top+head+i*rowH;
    if(i%2===1)c.rect(64,y,1072,rowH,colors.tint);
    c.line(64,y+rowH,1136,y+rowH,colors.line,1);
    text(c,1,'item-'+i+'-sku',84,y+36,144,56,v.sku,24,colors.ink,{font:mono,source_path:'items['+i+'].sku'});
    text(c,1,'item-'+i+'-name',264,y+20,412,92,v.name,24,colors.ink,{height:1.4,font:i===2?'Noto Sans CJK JP,Noto Sans CJK SC,Inter':font,source_path:'items['+i+'].name'});
    text(c,1,'item-'+i+'-quantity',700,y+34,60,56,String(v.quantity),26,colors.ink,{font:mono,align:'RIGHT',source_path:'items['+i+'].quantity'});
    text(c,1,'item-'+i+'-unit-price',784,y+34,140,56,v.unit_price,26,colors.ink,{font:mono,align:'RIGHT',source_path:'items['+i+'].unit_price'});
    text(c,1,'item-'+i+'-line-amount',964,y+34,152,56,money(v.line_cents),26,colors.ink,{font:mono,align:'RIGHT',source_path:'derived.line_amount['+i+']'});
  });
  text(c,1,'notes-cross-reference',64,1068,520,74,'说明与原样文字见第 2 页。',24,colors.muted);
  text(c,1,'tax-order-cross-reference',64,1150,520,110,input.notes[1],24,colors.muted,{height:1.45,source_path:'notes[1]'});
  const totalRows=[['货品小计',subtotal],['折扣',-discount],['税前货品额',base],['税额 · 6%',tax],['运费',shipping]];
  totalRows.forEach(([label,value],i)=>{
    const y=1054+i*54;
    text(c,1,'total-'+i+'-label',660,y,246,44,label,24,colors.muted);
    text(c,1,'total-'+i+'-amount',940,y,176,44,money(value),28,colors.ink,{font:mono,align:'RIGHT'});
  });
  c.line(660,1336,1136,1336,colors.line,2);
  text(c,1,'payable-label',660,1364,246,60,'应付 / CNY',28,colors.ink,{bold:true});
  text(c,1,'payable-amount',910,1362,206,62,money(payable),34,colors.accent,{font:mono,bold:true,align:'RIGHT',source_path:'derived.payable'});
  return c;
}
function page2(){
  const c=basePage(2);
  text(c,2,'notes-title',64,296,600,52,'说明 / NOTES',30,colors.ink,{bold:true});
  const ys=[372,456,544,660],heights=[68,68,104,112];
  input.notes.forEach((v,i)=>{
    text(c,2,'note-'+i+'-number',64,ys[i],52,48,String(i+1).padStart(2,'0'),24,colors.accent,{font:mono,bold:true});
    text(c,2,'note-'+i,134,ys[i],1002,heights[i],v,26,colors.ink,{height:1.5,source_path:'notes['+i+']'});
  });
  text(c,2,'literal-title',64,814,650,52,'原样文字 / LITERAL LINES',30,colors.ink,{bold:true});
  c.rect(64,888,1072,376,colors.tint,{radius:8,border:'1 SOLID '+colors.line});
  input.literal_lines.forEach((v,i)=>{
    text(c,2,'literal-line-'+i,88,912+i*80,1024,60,v,28,colors.ink,{font:i===0?'Noto Sans Mono CJK SC,Noto Sans Mono CJK JP,DejaVu Sans Mono':mono,softWrap:'false',maxLines:1,source_path:'literal_lines['+i+']'});
  });
  const value='PAID / 已结算';
  const rich=tag('Text',{fontFamily:font,fontSize:40,color:colors.ink,fontStyle:'BOLD'},
    tag('Text',{color:colors.green},tag('Raw',{},cdata('PAID')))+
    tag('Text',{color:'#7B898D',fontStyle:'NORMAL'},tag('Raw',{},cdata(' / ')))+
    tag('Text',{color:colors.ink},tag('Raw',{},cdata('已结算'))));
  c.at(64,1330,800,78,rich);
  map.push({id:'paid-rich-status',page:2,source_text:value,source_path:'task.required_sample_status',position:{x:64,y:1330,width:800,height:78},font_family:font,font_size:40,raw_cdata:true,one_outer_text:true,inline_spans:[{text:'PAID',color:colors.green,font_style:'BOLD'},{text:' / ',color:'#7B898D',font_style:'NORMAL'},{text:'已结算',color:colors.ink,font_style:'BOLD'}],shared_baseline:true});
  text(c,2,'paid-sample-disclaimer',64,1412,1072,44,'样张状态字样；应付金额保持 CNY '+money(payable)+'。',24,colors.muted);
  return c;
}
(async()=>{
  const pages=[page1(),page2()];
  write('text-map-v001.json',{schema_version:1,task_id:'A11',run_id:'20261002-204314-6f31',status:'awaiting_actual_visual_review',canvas:{width:1200,height:1600},minimum_safe_margin:64,font_cache:path.join(root,'tmp/20261002-204314-6f31/_suite/shared-fonts-000001-response.txt'),text_entries:map});
  for(let i=0;i<pages.length;i++){
    const dsl=pages[i].toString();const page=String(i+1).padStart(2,'0');
    write('invoice-page-'+page+'-v001.snapshot',dsl);
    const result=await suite.render('A11',dsl,{version_id:'A11-v001-p'+page,type:'baseline',stem:'invoice-page-'+page,width:1200,height:1600,case_id:'page-'+page,purpose:'A11 fixed point multilingual invoice page '+page});
    console.log(JSON.stringify({page,ok:result.ok,meta_path:result.meta_path,image_path:result.image_path,dimension_error:result.dimension_error??null}));
  }
})().catch(e=>{console.error(e);process.exitCode=1});
