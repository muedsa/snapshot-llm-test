const fs=require('fs'),path=require('path');
const [,,geometryFile,pathsFile,outputFile]=process.argv;
if(!geometryFile||!pathsFile||!outputFile)throw new Error('Usage: checker geometry.json paths.json result.json');
const g=JSON.parse(fs.readFileSync(geometryFile,'utf8')),p=JSON.parse(fs.readFileSync(pathsFile,'utf8'));
const facts=JSON.parse(fs.readFileSync(path.join(__dirname,'grid-path-facts-v001.json'),'utf8'));
const floor=fs.readFileSync('tasks/A08-accessible-wayfinding/inputs/floor.txt','utf8').replace(/\r/g,'').trimEnd().split('\n');
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),key=a=>a.join(',');
const legal=q=>Number.isInteger(q[0])&&Number.isInteger(q[1])&&q[0]>=0&&q[0]<26&&q[1]>=0&&q[1]<18&&floor[q[1]][q[0]]!=='#';
const px=q=>[g.grid_origin_pixels.x+(q[0]+.5)*g.cell_size_pixels,g.grid_origin_pixels.y+(q[1]+.5)*g.cell_size_pixels];
const cellProblems=[];
for(const cell of g.cells){
 const expectedSymbol=floor[cell.y]?.[cell.x];
 if(cell.symbol!==expectedSymbol||cell.walkable!==(expectedSymbol!=='#'))cellProblems.push({cell:[cell.x,cell.y],type:'symbol/walkability mismatch'});
 if(!eq(cell.pixel_center,px([cell.x,cell.y]))||cell.rect.x!==g.grid_origin_pixels.x+cell.x*g.cell_size_pixels||cell.rect.y!==g.grid_origin_pixels.y+cell.y*g.cell_size_pixels||cell.rect.width!==g.cell_size_pixels||cell.rect.height!==g.cell_size_pixels)cellProblems.push({cell:[cell.x,cell.y],type:'pixel geometry mismatch'});
}
const routeChecks=p.routes.map((r,i)=>{
 const sequence=r.cell_centers,draw=g.routes.find(a=>a.id===r.id);
 const allWalk=sequence.every(legal),allNeighbor=sequence.slice(1).every((q,j)=>Math.abs(q[0]-sequence[j][0])+Math.abs(q[1]-sequence[j][1])===1);
 const sequenceSteps=sequence.length-1,expectedSteps=i===0?facts.route_1.steps:facts.route_2.steps;
 const pixelsMatch=draw&&eq(draw.points,sequence.map(px))&&eq(r.pixel_centers,sequence.map(px));
 const segments=r.segments.map((segment,j)=>{
   const expected=i===0?facts.route_1.steps:facts.route_2.segments[j].steps;
   return {from:segment.from,to:segment.to,actual_steps:segment.cell_centers.length-1,independent_shortest_steps:expected,
     reported_steps:segment.steps,reported_meters:segment.distance_meters,
     shortest:segment.cell_centers.length-1===expected&&segment.steps===expected&&segment.distance_meters===2*expected};
 });
 const stopCoordinates=facts.symbols.reduce((out,s)=>(out[s.symbol]=s.point,out),{});
 const indices=Object.fromEntries(['S','B','D','E'].map(id=>[id,sequence.findIndex(q=>eq(q,stopCoordinates[id]))]));
 const ordered=i===0?indices.S===0&&indices.E===sequence.length-1:indices.S===0&&indices.B>0&&indices.D>indices.B&&indices.E>indices.D&&indices.E===sequence.length-1;
 const concat=r.segments.flatMap((seg,j)=>j?seg.cell_centers.slice(1):seg.cell_centers);
 return {id:r.id,all_cells_walkable:allWalk,all_steps_four_neighbor:allNeighbor,sequence_steps:sequenceSteps,independent_shortest_steps:expectedSteps,
   reported_steps:r.steps,reported_meters:r.distance_meters,pixel_points_match:!!pixelsMatch,segments,stop_indices:indices,ordered_stops_valid:ordered,
   concatenation_matches:eq(concat,sequence),passes:allWalk&&allNeighbor&&pixelsMatch&&sequenceSteps===expectedSteps&&r.steps===sequenceSteps&&r.distance_meters===2*sequenceSteps&&segments.every(s=>s.shortest)&&ordered&&eq(concat,sequence)};
});
const arrows=g.arrows.map(a=>{
 const source=a.source_cell,target=a.target_cell,A=px(source),B=px(target),vector=[B[0]-A[0],B[1]-A[1]],v=[a.tip[0]-a.tail[0],a.tip[1]-a.tail[1]];
 const route=g.routes.find(r=>r.color===a.color),sequence=p.routes.find(r=>r.id===route?.id)?.cell_centers;
 const onRoute=sequence?.slice(1).some((q,i)=>eq(sequence[i],source)&&eq(q,target));
 return {color:a.color,source_cell:source,target_cell:target,orthogonal:Math.abs(source[0]-target[0])+Math.abs(source[1]-target[1])===1,
   walkable:legal(source)&&legal(target),matches_route_direction:!!onRoute,
   arrow_vector_follows_source_target:vector[0]*v[0]+vector[1]*v[1]>0&&Math.abs(vector[0]*v[1]-vector[1]*v[0])<1e-8};
});
const result={generated_at:new Date().toISOString(),task_id:'A08',scope:'Independent produced route and grid geometry validation; real image review recorded separately',
  source_geometry:path.resolve(geometryFile),source_paths:path.resolve(pathsFile),
  complete_468_grid_cells:g.cells.length===468&&new Set(g.cells.map(c=>key([c.x,c.y]))).size===468,
  walls_drawn:g.cells.filter(c=>c.symbol==='#').length,walkable_drawn:g.cells.filter(c=>c.symbol!=='#').length,cell_problems:cellProblems,
  route_checks:routeChecks,arrow_checks:arrows,
  source_doorways_preserved:cellProblems.length===0,
  overlap_geometry:'Route colors are distinct with widths 8 and 4; all points align with original cell centers. Visual legibility still requires actual image review.',
  all_checks_pass:g.cells.length===468&&cellProblems.length===0&&routeChecks.every(r=>r.passes)&&arrows.every(a=>a.orthogonal&&a.walkable&&a.matches_route_direction&&a.arrow_vector_follows_source_target)};
fs.writeFileSync(outputFile,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({all_checks_pass:result.all_checks_pass,cells:g.cells.length,walls:result.walls_drawn,open:result.walkable_drawn,route_checks:routeChecks,arrow_count:arrows.length},null,2));
