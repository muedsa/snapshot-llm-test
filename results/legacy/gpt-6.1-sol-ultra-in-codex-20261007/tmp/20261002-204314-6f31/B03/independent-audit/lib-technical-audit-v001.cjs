const fs=require('node:fs'),crypto=require('node:crypto');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const attrs=s=>Object.fromEntries([...s.matchAll(/(\w+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g)].map(m=>[m[1],m[2]??m[3]]));
function parse(file){
 const raw=fs.readFileSync(file,'utf8'),root={tag:'DOCUMENT',children:[],text:''},stack=[root];let count=0;
 for(const m of raw.matchAll(/<!\[CDATA\[([\s\S]*?)\]\]>|<\/?([A-Za-z]\w*)\b([^>]*?)>/g)){
  if(m[1]!==undefined){stack.at(-1).text+=m[1];continue;}
  if(m[0].startsWith('</')){if(stack.at(-1).tag!==m[2])throw Error('Unexpected closing '+m[2]+' in '+file);stack.pop();continue;}
  const n={tag:m[2],attrs:attrs(m[3]),children:[],text:'',index:count++,source_offset:m.index};stack.at(-1).children.push(n);if(!m[3].trimEnd().endsWith('/'))stack.push(n);
 }
 if(stack.length!==1)throw Error('Unclosed tree in '+file);
 const nodes=[];function visit(n,anc){if(n.tag!=='DOCUMENT')nodes.push({node:n,ancestors:anc});for(const k of n.children)visit(k,[...anc,n]);}visit(root,[]);
 const canvas=nodes.find(x=>x.node.tag==='Container')?.node.attrs;
 const positions=nodes.filter(x=>x.node.tag==='Positioned').map(({node,ancestors})=>{const a=node.attrs,parents=ancestors.filter(n=>n.tag==='Positioned');return {node,x:Number(a.left??0),y:Number(a.top??0),absolute_x:Number(a.left??0)+parents.reduce((s,p)=>s+Number(p.attrs.left??0),0),absolute_y:Number(a.top??0)+parents.reduce((s,p)=>s+Number(p.attrs.top??0),0),width:Number(a.width),height:Number(a.height)};});
 const textOf=n=>n.text+n.children.map(textOf).join('');
 const texts=nodes.filter(x=>x.node.tag==='Text').map(({node,ancestors})=>{const ps=ancestors.filter(n=>n.tag==='Positioned'),p=ps.at(-1),transform_ancestors=ancestors.filter(n=>n.tag==='Transform');return {node,text:textOf(node),x:ps.reduce((s,p)=>s+Number(p.attrs.left??0),0),y:ps.reduce((s,p)=>s+Number(p.attrs.top??0),0),width:Number(p?.attrs.width),height:Number(p?.attrs.height),font_size:Number(node.attrs.fontSize),transform_ancestors:transform_ancestors.map(n=>n.attrs.matrix)};});
 const linePositions=positions.flatMap(p=>{let n=p.node.children[0],opacity=null;if(n?.tag==='Opacity'){opacity=Number(n.attrs.opacity);n=n.children[0];}if(n?.tag!=='Transform'||n.children[0]?.tag!=='Container')return [];const m=n.attrs.matrix.replace(/[()]/g,'').split(',').map(Number),container=n.children[0].attrs;return [{...p,matrix:m,color:container.color,opacity,from:[p.absolute_x,p.absolute_y],to:[p.absolute_x+p.width*m[0],p.absolute_y+p.width*m[1]]}];});
 return {file,raw,sha256:hash(Buffer.from(raw)),root,nodes,positions,texts,lines:linePositions,width:Number(canvas.width),height:Number(canvas.height),element_count:count,tags:[...new Set(nodes.map(n=>n.node.tag))].sort()};
}
const readLines=file=>fs.existsSync(file)?fs.readFileSync(file,'utf8').split(/\r?\n/).filter(Boolean).map(JSON.parse):[];
function png(file){const b=fs.readFileSync(file);if(b.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw Error('Not PNG');return {width:b.readUInt32BE(16),height:b.readUInt32BE(20),sha256:hash(b),bytes:b.length};}
module.exports={hash,attrs,parse,readLines,png};
