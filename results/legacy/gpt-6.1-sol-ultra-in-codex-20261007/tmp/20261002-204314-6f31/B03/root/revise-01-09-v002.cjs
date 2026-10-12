const source=require('node:fs').readFileSync(require('node:path').join(__dirname,'generate-v001.cjs'),'utf8');
const a=source.indexOf("{\nconst c=new Canvas(1200,1600,{background:'#081329'})"),b=source.indexOf("{\nconst c=new Canvas(1500,1100,{background:'#0B1825'})"),d=source.indexOf("{\nconst c=new Canvas(1200,1600,{background:'#F4ECDD'})"),e=source.indexOf("{\nconst c=new Canvas(1500,1100,{background:'#EFF3F2'})");if([a,b,d,e].some(n=>n<0))throw Error('Source markers missing');
let head=source.slice(0,a).replaceAll("'-v001.snapshot'","'-v002.snapshot'").replaceAll("'-metadata-v001.json'","'-metadata-v002.json'");
let one=source.slice(a,b).replace("70,143,1060,190,'把夜晚，\\n留给耳朵。',78","70,143,1060,225,'把夜晚，\\n留给耳朵。',70").replace("73,338,1050,52","73,390,1050,52");one=one.replace("c.at(140,495,920,560", "for(let i=0;i<17;i++)c.line(884+i*6,436,884+i*6,646,'#B5F8F0AA',2);\nc.at(140,495,920,560");
let nine=source.slice(d,e).replace("face(x,y-z,w,z,.866,.5,0,1", "face(x-.866*d,y+.5*d-z,w,z,.866,.5,0,1").replace("face(x+.866*(14+q*24),y-z+.5*(14+q*24)+27+row*34", "face(x-.866*d+.866*(14+q*24),y+.5*d-z+.5*(14+q*24)+27+row*34");
eval(head+one+nine);
