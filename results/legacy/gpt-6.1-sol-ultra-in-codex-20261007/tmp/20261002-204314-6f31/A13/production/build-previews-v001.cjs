'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../..'),s=require(path.join(root,'tmp/20261002-204314-6f31/_suite/suite.cjs'));
const {Canvas,tag,matrix2d}=require(path.join(root,'tmp/20261002-204314-6f31/_suite/dsl.cjs'));
fs.mkdirSync(__dirname,{recursive:true});
const write=(name,v)=>fs.writeFileSync(path.join(__dirname,name),typeof v==='string'?v:JSON.stringify(v,null,2)+'\n',{flag:'wx'});
const colors={navy:'#133E49',violet:'#7966FF',cyan:'#39DACA'};
const a=new Canvas(512,512,{background:'transparent',clipBehavior:'NONE'});
a.rect(96,96,256,256,'transparent',{border:'32 SOLID '+colors.navy,radius:40});
a.rect(160,160,256,256,'transparent',{border:'32 SOLID '+colors.violet,radius:40});
const b=new Canvas(512,512,{background:'transparent',clipBehavior:'NONE'});
const radial=[];
for(let i=0;i<6;i++){
  const theta=i*Math.PI/3,angle=theta+Math.PI/2;
  const cs=Math.cos(angle),sn=Math.sin(angle),cx=256+124*Math.cos(theta),cy=256+124*Math.sin(theta),len=176,thick=28;
  const tx=cx-cs*len/2+sn*thick/2,ty=cy-sn*len/2-cs*thick/2;
  const color=[colors.navy,colors.violet,colors.cyan][i%3];
  b.at(0,0,len,thick,tag('Transform',{matrix:matrix2d(cs,sn,-sn,cs,tx,ty),origin:'(0,0)'},tag('Container',{width:len,height:thick,color,borderRadius:8})));
  radial.push({type:'tangential rounded bar',index:i,theta_degrees:i*60,center:{x:cx,y:cy},length:len,thickness:thick,color});
}
write('preview-direction-designs-v001.json',{task_id:'A13',designs:[{id:'direction-A',name:'Layered windows',major_components:2,description:'Two offset hollow rounded squares,32px strokes,transparent interiors preserve overlap and common negative space.',components:[{rect:[96,96,256,256],stroke:32,radius:40,color:colors.navy},{rect:[160,160,256,256],stroke:32,radius:40,color:colors.violet}]},{id:'direction-B',name:'Radial aperture',major_components:6,description:'Six tangential bars form a rotational hexagonal aperture; distinct radial structure versus orthogonal stacked frames.',components:radial}],selection_status:'not_yet_viewed_or_selected',final_assets_not_yet_created:true});
(async()=>{
for(const [name,c,type] of [['direction-A',a,'baseline'],['direction-B',b,'alternative']]){
  const dsl=c.toString();write('preview-'+name+'-v001.snapshot',dsl);
  const r=await s.render('A13',dsl,{version_id:'A13-preview-v001-'+name,type,stem:'preview-'+name,width:512,height:512,case_id:'preview-'+name,purpose:'A13 genuinely distinct '+name+' geometric preview,before direction selection'});
  console.log(JSON.stringify({direction:name,ok:r.ok,meta_path:r.meta_path,image_path:r.image_path,error:r.error_summary}));
}
})().catch(e=>{console.error(e);process.exitCode=1});
