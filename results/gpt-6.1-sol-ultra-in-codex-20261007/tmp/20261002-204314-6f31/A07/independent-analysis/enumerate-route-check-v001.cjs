const fs=require('fs'), path=require('path');
const n=JSON.parse(fs.readFileSync('tasks/A07-transit-topology/inputs/network.json','utf8'));
const facts=JSON.parse(fs.readFileSync(path.join(__dirname,'route-facts-v001.json'),'utf8'));
const station=Object.fromEntries(n.stations.map(s=>[s.id,s]));
const neighbor=Object.fromEntries(n.stations.map(s=>[s.id,[]]));
for(const l of n.lines)for(let i=1;i<l.stations.length;i++){
  const a=l.stations[i-1],b=l.stations[i];neighbor[a].push({id:b,line:l.id});neighbor[b].push({id:a,line:l.id});
}
function enumerate(from,to){
  const found=[];
  function visit(ids,lines){
    const current=ids.at(-1);
    if(current===to){
      const changes=lines.slice(1).map((l,i)=>l!==lines[i]?ids[i+1]:null).filter(Boolean);
      found.push({stations:ids,lines,edges:lines.length,transfers:changes.length,transfer_stations:changes,
        accessible:station[from].accessible&&station[to].accessible&&changes.every(id=>station[id].accessible)});
      return;
    }
    for(const e of neighbor[current])if(!ids.includes(e.id))visit([...ids,e.id],[...lines,e.line]);
  }
  visit([from],[]);return found;
}
function best(routes){return routes.reduce((a,b)=>!a||b.edges<a.edges||(b.edges===a.edges&&b.transfers<a.transfers)?b:a,null);}
const checks=n.queries.map((q,i)=>{
  const routes=enumerate(q.from,q.to),ordinary=best(routes),accessible=best(routes.filter(r=>r.accessible));
  const f=facts.queries[i];
  return {...q,simple_paths:routes,ordinary_best:[ordinary.edges,ordinary.transfers],accessible_best:[accessible.edges,accessible.transfers],
    agrees_with_dijkstra:ordinary.edges===f.ordinary.edge_count&&ordinary.transfers===f.ordinary.transfer_count&&
      accessible.edges===f.shortest_accessible.edge_count&&accessible.transfers===f.shortest_accessible.transfer_count};
});
const result={generated_at:new Date().toISOString(),task_id:'A07',method:'Independent DFS exhaustive enumeration of all simple station paths; positive edge costs make cycles unnecessary in these three journeys',checks,all_agree:checks.every(c=>c.agrees_with_dijkstra)};
fs.writeFileSync(path.join(__dirname,'enumeration-check-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result,null,2));
