const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const input=path.resolve('tasks/A07-transit-topology/inputs/network.json');
const bytes=fs.readFileSync(input), network=JSON.parse(bytes);
const stations=Object.fromEntries(network.stations.map(s=>[s.id,s]));
const memberships=Object.fromEntries(network.stations.map(s=>[s.id,[]]));
const adjacency=Object.fromEntries(network.stations.map(s=>[s.id,[]]));
const edges=[];
for(const line of network.lines){
  line.stations.forEach(id=>memberships[id].push(line.id));
  for(let i=1;i<line.stations.length;i++){
    const from=line.stations[i-1],to=line.stations[i];
    edges.push({from,to,line:line.id});
    adjacency[from].push({to,line:line.id}); adjacency[to].push({to:from,line:line.id});
  }
}
const compare=(a,b)=>a.edges-b.edges||a.transfers-b.transfers;
function solve(from,to,accessible){
  if(accessible&&(!stations[from].accessible||!stations[to].accessible))return null;
  const todo=[{station:from,last_line:null,edges:0,transfers:0,station_sequence:[from],edge_lines:[]}];
  const best=new Map();
  while(todo.length){
    todo.sort(compare);const cur=todo.shift(),key=cur.station+'|'+(cur.last_line??'START');
    if(best.has(key)&&compare(best.get(key),cur)<=0)continue;
    best.set(key,cur);
    if(cur.station===to)return describe(cur);
    for(const edge of adjacency[cur.station]){
      const change=cur.last_line!==null&&cur.last_line!==edge.line;
      if(accessible&&change&&!stations[cur.station].accessible)continue;
      todo.push({station:edge.to,last_line:edge.line,edges:cur.edges+1,transfers:cur.transfers+(change?1:0),
        station_sequence:[...cur.station_sequence,edge.to],edge_lines:[...cur.edge_lines,edge.line]});
    }
  }
  return null;
}
function describe(cur){
  const segments=[],transferStations=[];
  cur.edge_lines.forEach((line,i)=>{
    if(i===0||line!==cur.edge_lines[i-1]){
      segments.push({line,stations:[cur.station_sequence[i],cur.station_sequence[i+1]],edges:1});
      if(i)transferStations.push(cur.station_sequence[i]);
    }else{segments.at(-1).stations.push(cur.station_sequence[i+1]);segments.at(-1).edges++;}
  });
  const endpointsAccessible=stations[cur.station_sequence[0]].accessible&&stations[cur.station_sequence.at(-1)].accessible;
  const invalidTransfers=transferStations.filter(id=>!stations[id].accessible);
  return {station_sequence:cur.station_sequence,station_names:cur.station_sequence.map(id=>stations[id].name),
    edge_lines:cur.edge_lines,line_segments:segments,edge_count:cur.edges,station_count:cur.station_sequence.length,
    transfer_count:cur.transfers,transfer_stations:transferStations,
    accessible_journey_valid:endpointsAccessible&&!invalidTransfers.length,
    inaccessible_transfer_stations:invalidTransfers,
    inaccessible_same_line_pass_through:cur.station_sequence.slice(1,-1).filter((id,i)=>!stations[id].accessible&&cur.edge_lines[i]===cur.edge_lines[i+1])};
}
const result={generated_at:new Date().toISOString(),task_id:'A07',run_id:'20261002-204314-6f31',
  source:input,source_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),
  scope:'Independent route solving from task input; no image inspection claimed',
  optimization:['minimum station-to-station edge count','then minimum transfers'],
  transfer_definition:'Changing ridden line at a station; first boarding is zero transfers',
  accessibility_rule:'Only journey endpoints and actual line-change stations must be accessible; same-line through-running allowed at any station',
  station_count:network.stations.length,line_count:network.lines.length,bidirectional_neighbor_pair_count:edges.length,
  bidirectional_edges:edges,
  station_audit:network.stations.map(s=>({...s,lines:memberships[s.id],adjacent:adjacency[s.id]})),
  interchange_stations:network.stations.filter(s=>memberships[s.id].length>1).map(s=>({...s,lines:memberships[s.id]})),
  non_accessible_stations:network.stations.filter(s=>!s.accessible).map(s=>({id:s.id,name:s.name})),
  queries:network.queries.map((q,i)=>{
    const ordinary=solve(q.from,q.to,false),accessible=solve(q.from,q.to,true);
    return {id:'Q'+(i+1),...q,from_name:stations[q.from].name,to_name:stations[q.to].name,
      ordinary,shortest_accessible:accessible,
      ordinary_accessibility_explanation:ordinary.accessible_journey_valid?
        '起终点及实际换乘站有无障碍设施；途中未无障碍站仅同线通过。':
        '普通最短路在未无障碍站'+ordinary.inaccessible_transfer_stations.join(',')+'改变线路，不能作为无障碍旅程。'};
  })};
const output=path.join(__dirname,'route-facts-v001.json');
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result.queries,null,2));
