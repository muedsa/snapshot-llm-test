const {Canvas,tag}=require('../_suite/dsl.cjs');const P={bg:'#F4F2EB',ink:'#1C343D',muted:'#536873',mint:'#BCE9D7',teal:'#176B68',coral:'#D56548',line:'#D5DDD5',white:'#FFFFFF'};
function txt(c,x,y,w,h,t,z=30,col=P.ink,bold=false){c.text(x,y,w,h,t,z,col,{bold});}
function arc(c,cx,cy,r,a0,a1,col,w=6){const p=[];for(let i=0;i<=60;i++){const a=a0+(a1-a0)*i/60;p.push([cx+r*Math.cos(a),cy+r*Math.sin(a)]);}c.polyline(p,col,w,{roundCaps:true});}
function logo(c,x,y){arc(c,x,y,18,-2.6,.35,P.teal,6);arc(c,x+13,y+7,18,.55,3.5,P.coral,6);}
function phone(id,title,sub,time){const c=new Canvas(720,1440,{background:P.bg});txt(c,40,22,640,36,'2026.10.08  '+time+'   /   北院',20,P.muted);logo(c,58,92);txt(c,103,64,360,51,'洗序',34,P.ink,true);txt(c,544,75,140,37,id,20,P.muted);txt(c,40,147,640,150,title,45,P.ink,true);txt(c,40,296,640,92,sub,28,P.muted);return c;}
function button(c,y,label,secondary=false,x=40,w=640){c.card(x,y,w,88,secondary?P.white:P.teal,{radius:22,border:secondary?'2 SOLID '+P.line:undefined});txt(c,x+16,y+21,w-32,53,label,30,secondary?P.ink:P.white,true);}
function foot(c){c.line(40,1360,680,1360,P.line,1);txt(c,40,1378,640,34,'静态概念原型 · 全部状态/费用/机器为演示',19,P.muted);}
function card(c,x,y,w,h,fill=P.white){c.card(x,y,w,h,fill,{radius:26});}
function check(c,x,y,col=P.teal){c.line(x,y+14,x+13,y+27,col,6,{roundCaps:true});c.line(x+13,y+27,x+42,y,col,6,{roundCaps:true});}
module.exports={P,Canvas,txt,arc,logo,phone,button,foot,card,check};
