const fs=require('fs'),path=require('path'),crypto=require('crypto');
const source=path.resolve('tasks/A08-accessible-wayfinding/inputs/floor.txt');
const bytes=fs.readFileSync(source);
const rows=bytes.toString('utf8').replace(/\r/g,'').trimEnd().split('\n');
const legend=JSON.parse(fs.readFileSync('tasks/A08-accessible-wayfinding/inputs/legend.json','utf8'));
const rowLengths=rows.map(r=>r.length);
if(rows.length!==18||rowLengths.some(v=>v!==26))throw new Error('Input grid dimension mismatch');
const symbolPoints={};let walkableCount=0,wallCount=0;
for(let y=0;y<rows.length;y++)for(let x=0;x<rows[y].length;x++){
 const ch=rows[y][x];if(ch==='#')wallCount++;else walkableCount++;
 if(ch!=='.'&&ch!=='#')symbolPoints[ch]=[x,y];
}
const key=p=>p.join(',');
const eq=(a,b)=>a[0]===b[0]&&a[1]===b[1];
const walk=p=>p[0]>=0&&p[0]<26&&p[1]>=0&&p[1]<18&&rows[p[1]][p[0]]!=='#';
function bfs(from,to){
 const queue=[from],parent=new Map([[key(from),null]]),distance=new Map([[key(from),0]]);
 for(let idx=0;idx<queue.length;idx++){
  const p=queue[idx];if(eq(p,to)){
    const sequence=[];let at=p;while(at){sequence.push(at);at=parent.get(key(at));}sequence.reverse();
    return {sequence,steps:sequence.length-1,meters:(sequence.length-1)*legend.cell_meters,reachable:true,
      bfs_distance:distance.get(key(to)),searched_cells:idx+1};
  }
  for(const [dx,dy] of [[1,0],[0,1],[-1,0],[0,-1]]){
    const np=[p[0]+dx,p[1]+dy],nk=key(np);if(walk(np)&&!parent.has(nk)){
      parent.set(nk,p);distance.set(nk,distance.get(key(p))+1);queue.push(np);
    }
  }
 }
 return {reachable:false,sequence:[],steps:null,meters:null,searched_cells:queue.length};
}
function check(sequence){
 return {all_cells_walkable:sequence.every(walk),all_steps_four_neighbor:sequence.slice(1).every((p,i)=>Math.abs(p[0]-sequence[i][0])+Math.abs(p[1]-sequence[i][1])===1),
  walls_entered:sequence.filter(p=>!walk(p)),coordinates_in_bounds:sequence.every(p=>p[0]>=0&&p[0]<26&&p[1]>=0&&p[1]<18)};
}
const shortest=bfs(symbolPoints.S,symbolPoints.E);
const segments=[['S','B'],['B','D'],['D','E']].map(([from,to])=>({from,to,...bfs(symbolPoints[from],symbolPoints[to])}));
const tour=segments.flatMap((seg,i)=>i?seg.sequence.slice(1):seg.sequence);
function allConnected(start){const reached=new Set([key(start)]),queue=[start];for(let i=0;i<queue.length;i++){
 const p=queue[i];for(const [dx,dy] of [[1,0],[0,1],[-1,0],[0,-1]]){const np=[p[0]+dx,p[1]+dy];if(walk(np)&&!reached.has(key(np))){reached.add(key(np));queue.push(np);}}
 }return reached;}
const connected=allConnected(symbolPoints.S);
const edgeKey=(a,b)=>[key(a),key(b)].sort().join('|');
const r1Edges=new Set(shortest.sequence.slice(1).map((p,i)=>edgeKey(shortest.sequence[i],p)));
const r2EdgeOccurrences=new Map();tour.slice(1).forEach((p,i)=>{
 const k=edgeKey(tour[i],p);(r2EdgeOccurrences.get(k)??(r2EdgeOccurrences.set(k,[]),r2EdgeOccurrences.get(k))).push({from:tour[i],to:p,index:i});
});
const result={generated_at:new Date().toISOString(),task_id:'A08',run_id:'20261002-204314-6f31',source,
 source_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),scope:'Independent BFS facts from original input; no image review claimed',
 dimensions:{columns:26,rows:18,row_lengths:rowLengths,cells:26*18,walkable_cells:walkableCount,wall_cells:wallCount},
 movement:'4-neighbor only',cell_meters:legend.cell_meters,coordinates:'zero-based (x,y) cell centers; upper left origin',
 source_typo_resolution:'TASK.md/task.json writes A/A/B/D; actual floor symbols and legend define four zones A/B/C/D. Use the original floor and legend without rewriting them.',
 symbols:Object.entries(symbolPoints).map(([symbol,point])=>({symbol,name:legend[symbol],point})),
 route_1:{from:'S',to:'E',...shortest,check:check(shortest.sequence)},
 route_2:{ordered_required_stops:['S','B','D','E'],segments,sequence:tour,steps:tour.length-1,meters:(tour.length-1)*legend.cell_meters,
  check:check(tour),each_segment_shortest:true,B_sequence_index:tour.findIndex(p=>eq(p,symbolPoints.B)),D_sequence_index:tour.findIndex(p=>eq(p,symbolPoints.D))},
 connectivity:{walkable_cells_reachable_from_S:connected.size,all_walkable_cells_connected:connected.size===walkableCount,symbols_reachable:Object.fromEntries(Object.entries(symbolPoints).map(([k,p])=>[k,connected.has(key(p))]))},
 overlap:{undirected_shared_edge_count:[...r2EdgeOccurrences.keys()].filter(k=>r1Edges.has(k)).length,
  shared_edges:[...r2EdgeOccurrences].filter(([k])=>r1Edges.has(k)).map(([edge,occurrences])=>({edge,occurrences})),
  route_2_repeated_edges:[...r2EdgeOccurrences].filter(([k,v])=>v.length>1).map(([edge,occurrences])=>({edge,occurrences}))},
 visual_recommendation:'Use a wider solid route-1 underlay and a narrower contrasting dashed route-2 on exactly the same cell centers; route-1 margins remain visible in shared stretches. At B branch, route-2 enters and returns on one repeated edge, so show up/down arrowheads separately and annotate B arrival before D. Do not offset routes into wall cells or widen one-cell doorways.'};
fs.writeFileSync(path.join(__dirname,'grid-path-facts-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({dimensions:result.dimensions,symbols:result.symbols,route1:[shortest.steps,shortest.meters],route2:[result.route_2.steps,result.route_2.meters],segments:segments.map(s=>({from:s.from,to:s.to,steps:s.steps,meters:s.meters})),connectivity:result.connectivity,shared:result.overlap.undirected_shared_edge_count,repeated:result.overlap.route_2_repeated_edges},null,2));
