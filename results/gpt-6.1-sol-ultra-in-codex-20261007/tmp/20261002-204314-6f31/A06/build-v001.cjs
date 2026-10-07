'use strict';
const fs=require('node:fs');
const path=require('node:path');
const s=require('../_suite/suite.cjs');
const {Canvas}=require('../_suite/dsl.cjs');
const d=s.taskDirs('A06');
const inputPath=path.resolve('tasks/A06-dependency-graph/inputs/graph.json');
const g=JSON.parse(fs.readFileSync(inputPath,'utf8'));
const incoming=Object.fromEntries(g.nodes.map(n=>[n.id,[]]));
const outgoing=Object.fromEntries(g.nodes.map(n=>[n.id,[]]));
g.solid_edges.forEach(([a,b])=>{outgoing[a].push(b);incoming[b].push(a)});
const pending=g.nodes.map(n=>n.id),layer={},longest={},parents={};
while(pending.length){
  const available=pending.filter(id=>incoming[id].every(p=>layer[p]!==undefined));
  if(!available.length) throw new Error('Cycle in prerequisite graph');
  for(const id of available){
    layer[id]=incoming[id].length?Math.max(...incoming[id].map(p=>layer[p]))+1:0;
    longest[id]=incoming[id].length?Math.max(...incoming[id].map(p=>longest[p]))+1:1;
    parents[id]=incoming[id].filter(p=>longest[p]===longest[id]-1);
    pending.splice(pending.indexOf(id),1);
  }
}
const longestLength=Math.max(...Object.values(longest));
function collect(id){return parents[id].length?parents[id].flatMap(p=>collect(p).map(a=>[...a,id])):[[id]];}
const longestPaths=g.nodes.filter(n=>longest[n.id]===longestLength).flatMap(n=>collect(n.id));
const positions={N01:[740,158],N02:[560,226],N03:[1040,226],N04:[510,294],N05:[820,294],N06:[900,362],N07:[540,362],N08:[740,430],N09:[740,498],N10:[740,566],N11:[740,634],N12:[740,702],N13:[740,770],N14:[740,838]};
const routes=[
  [[820,210],[700,226]],[[970,210],[1180,226]],
  [[650,278],[650,294]],[[810,278],[890,294]],
  [[1250,278],[1250,340],[1130,340],[1130,362]],
  [[960,346],[1030,362]],[[650,346],[680,362]],
  [[1040,414],[960,430]],[[760,414],[800,430]],
  [[880,482],[880,498]],[[880,550],[880,566]],[[880,618],[880,634]],
  [[880,686],[880,702]],[[880,754],[880,770]],[[880,822],[880,838]],
  [[510,320],[454,320],[454,796],[740,796]],
];
const feedbackRoutes=[[[1020,524],[1384,524],[1384,458],[1020,458]],[[1020,592],[1450,592],[1450,444],[1020,444]]];
const c=new Canvas(1600,1000,{background:'#F7F6F2'});
const color={ink:'#18343E',muted:'#577078',line:'#2B7481',feedback:'#BC5C26',grid:'#E5EBE9'};
c.rect(0,0,1600,8,color.line);
c.text(60,39,1350,58,'从需求到可复现交付',42,color.ink,{bold:true});
c.text(62,104,1400,38,'先决关系向下推进；反馈沿右侧返回构建。并行分支汇合后继续交付。',23,color.muted);
c.text(489,139,450,32,'先决顺序  ↓',19,color.muted,{bold:true});
for(let i=0;i<=10;i++){
  const cy=184+i*68;
  c.line(487,cy,1338,cy,color.grid,1);
  c.text(468,cy-15,30,30,String(i).padStart(2,'0'),18,'#789097',{align:'CENTER'});
}
c.card(60,180,335,155,'#E8EFEA',{radius:18});
c.text(84,202,290,35,'先决图 · 11 层',24,color.ink,{bold:true});
c.text(84,251,290,32,'14 节点 / 16 条实线依赖',21,color.muted);
c.text(84,292,290,32,'2 条反馈独立于 DAG 排序',20,color.muted);
c.card(60,364,335,170,'#FFFFFF',{radius:18,border:'1 SOLID #DDE6E0'});
c.text(84,386,285,34,'并行准备，再汇合',23,color.ink,{bold:true});
c.text(84,433,285,84,'输入检查与字体查询并行；\n数据、内容、版式分别推进，\n在 DSL 构建之前汇合。',20,color.muted,{lineHeight:1.45});
c.card(60,562,335,179,'#FFFFFF',{radius:18,border:'1 SOLID #DDE6E0'});
c.text(84,584,285,34,'计算结果贯穿校验',23,color.ink,{bold:true});
c.text(84,631,285,88,'N04 → N13 是直接先决。\n左侧长线绕开中间节点，\n表示校验需要原始计算结果。',20,color.muted,{lineHeight:1.45});
c.text(62,780,333,58,'最长先决路径：11 个节点',22,color.ink,{bold:true});
c.text(62,825,333,78,'需求冻结 → 内容分支 →\n构建与检查 → 交付归档',20,color.muted,{lineHeight:1.4});
function arrowRoute(points,color,width){
  for(let i=1;i<points.length-1;i++)c.line(...points[i-1],...points[i],color,width);
  c.arrow(...points[points.length-2],...points[points.length-1],color,width,{headLength:10,headWidth:5});
}
routes.forEach((r,i)=>arrowRoute(r,color.line,i===15?3.2:3.6));
function dashedRoute(points){
  let travelled=0;
  for(let i=1;i<points.length;i++){
    const [a,b]=[points[i-1],points[i]],len=Math.hypot(b[0]-a[0],b[1]-a[1]);
    for(let j=0;j<len;){
      const phase=travelled%18,take=Math.min(len-j,18-phase);
      if(phase<10){const run=Math.min(take,10-phase);c.line(a[0]+(b[0]-a[0])*j/len,a[1]+(b[1]-a[1])*j/len,a[0]+(b[0]-a[0])*(j+run)/len,a[1]+(b[1]-a[1])*(j+run)/len,color.feedback,3.6);}
      j+=take;travelled+=take;
    }
  }
  const b=points.at(-1),a=points.at(-2),len=Math.hypot(b[0]-a[0],b[1]-a[1]),ux=(b[0]-a[0])/len,uy=(b[1]-a[1])/len;
  c.line(...b,b[0]-ux*13-uy*6,b[1]-uy*13+ux*6,color.feedback,3.6);
  c.line(...b,b[0]-ux*13+uy*6,b[1]-uy*13-ux*6,color.feedback,3.6);
}
feedbackRoutes.forEach(dashedRoute);
g.nodes.forEach(n=>{
 const [x,y]=positions[n.id];const main=layer[n.id]>=4;
 c.card(x,y,280,52,main?'#E0F0EF':'#FFFFFF',{radius:12,border:`1.5 SOLID ${main?'#8BB8B7':'#AABFC1'}`});
 c.text(x+16,y+8,61,36,n.id,23,color.line,{bold:true});
 c.text(x+87,y+8,181,36,n.label,24,color.ink,{bold:true});
});
c.text(1080,490,279,32,'F1 · 渲染失败',20,color.feedback,{bold:true});
c.text(1080,558,320,32,'F2 · 检查发现问题',20,color.feedback,{bold:true});
c.card(1090,652,450,99,'#F9EADC',{radius:16});
c.text(1114,669,410,32,'F1  失败后回到构建',22,'#8D451D',{bold:true});
c.text(1114,711,406,30,'N09 首轮渲染 → N08 DSL构建',19,'#935836');
c.card(1090,778,450,108,'#F9EADC',{radius:16});
c.text(1114,795,405,32,'F2  检查发现问题后修复',22,'#8D451D',{bold:true});
c.text(1114,836,405,37,'N10 视觉检查 → N08 DSL构建',19,'#935836');
c.line(60,922,1540,922,'#D1DBD8',1);
c.arrow(66,957,119,957,color.line,3.6,{headLength:12,headWidth:6});
c.text(139,940,280,38,'实线：先决依赖',20,color.ink);
dashedRoute([[453,957],[519,957]]);
c.text(540,940,360,38,'虚线：反馈，不参与拓扑排序',20,color.ink);
c.text(975,940,565,38,'交叉线无连接点，不形成额外依赖。',20,color.muted,{align:'END'});
const audit={schema_version:1,task_id:'A06',source:inputPath,source_kind:'provided_input',counts:{nodes:g.nodes.length,solid_edges:g.solid_edges.length,feedback_edges:g.feedback_edges.length,prerequisite_layers:11},topological_layers:Array.from({length:11},(_,i)=>({layer:i,nodes:g.nodes.filter(n=>layer[n.id]===i).map(n=>n.id)})),nodes:g.nodes.map(n=>({...n,layer:layer[n.id],incoming:incoming[n.id],outgoing:outgoing[n.id],bounds:{x:positions[n.id][0],y:positions[n.id][1],width:280,height:52}})),longest_prerequisite_paths:{node_count:longestLength,paths:longestPaths},solid_edges:g.solid_edges.map(([from,to],i)=>({id:`E${String(i+1).padStart(2,'0')}`,from,to,from_layer:layer[from],to_layer:layer[to],points:routes[i],representation:'solid teal polyline with arrowhead at target',all_segments_non_decreasing_y:routes[i].every((p,j)=>!j||p[1]>=routes[i][j-1][1])})),feedback_edges:g.feedback_edges.map(([from,to],i)=>({id:`F${i+1}`,from,to,points:feedbackRoutes[i],representation:'orange dashed right-side return, arrowhead entering target right border',explanation:i?'检查发现问题后修复，回到构建':'失败后回到构建',position:{side:'right',outer_lane_x:i?1450:1384,target_y:i?444:458}})),geometry:{orientation:'top_to_bottom',node_font_px:24,id_font_px:23,annotation_min_font_px:18,prerequisite_edge_direction:'all target layers later than source; route y never decreases',intersections_create_edges:false,feedback_excluded_from_dag:true}};
fs.writeFileSync(path.join(d.temp,'dependency-map-v001.snapshot'),c.toString(),{flag:'wx'});
fs.writeFileSync(path.join(d.temp,'graph-audit-v001.json'),JSON.stringify(audit,null,2)+'\n',{flag:'wx'});
(async()=>{const result=await s.render('A06',c.toString(),{version_id:'A06-v001',type:'baseline',stem:'dependency-map',width:1600,height:1000});console.log(JSON.stringify(result,null,2));})();
