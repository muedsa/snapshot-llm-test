const {Canvas}=require('../_suite/dsl.cjs');
const P={paper:'#F5EBDD',ink:'#263C50',clay:'#BC5338',sage:'#789588',line:'#CFC3B0',light:'#FFFCF4'};
const T=(c,x,y,w,h,t,s=24,col=P.ink,b=false)=>c.text(x,y,w,h,t,s,col,{bold:b});
function mark(c,x,y,s=1){c.rect(x,y,28*s,32*s,P.clay,{radius:3*s});c.rect(x+18*s,y+10*s,28*s,32*s,P.ink,{radius:3*s});for(let i=0;i<4;i++)c.line(x+(11+i*5)*s,y+(7+i*5)*s,x+(13+i*5)*s,y+(9+i*5)*s,P.paper,2*s);}
function header(c,label){mark(c,48,40);T(c,111,39,c.width-190,40,'再线 / RETHREAD   ·   '+label,23,P.ink,true);c.line(48,99,c.width-48,99,P.line,1);}
function footer(c,note='自拟社区项目 · 静态设计演示 · 澄巷12号为虚构地址'){T(c,48,c.height-46,c.width-96,35,note,18,P.ink);}
function stitch(c,x,y,w,h,col=P.ink){for(let a=x+8;a<x+w-4;a+=18){c.line(a,y,a+8,y,col,2);c.line(a,y+h,a+8,y+h,col,2);}for(let a=y+8;a<y+h-4;a+=18){c.line(x,a,x,a+8,col,2);c.line(x+w,a,x+w,a+8,col,2);}}
function patch(c,x,y,w,h,col=P.clay){c.rect(x,y,w,h,col,{radius:5});stitch(c,x+8,y+8,w-16,h-16,P.paper);}
module.exports={Canvas,P,T,mark,header,footer,stitch,patch};
