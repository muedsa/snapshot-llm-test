const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sourceStamp=path.resolve('tasks/A09-transform-atlas/inputs/stamp.json');
const sourceTransforms=path.resolve('tasks/A09-transform-atlas/inputs/transforms.json');
const stampBytes=fs.readFileSync(sourceStamp),transformBytes=fs.readFileSync(sourceTransforms);
const stamp=JSON.parse(stampBytes),transforms=JSON.parse(transformBytes);
const multiply=(A,B)=>[
 [A[0][0]*B[0][0]+A[0][1]*B[1][0],A[0][0]*B[0][1]+A[0][1]*B[1][1]],
 [A[1][0]*B[0][0]+A[1][1]*B[1][0],A[1][0]*B[0][1]+A[1][1]*B[1][1]]
];
const clean=v=>Math.abs(v)<1e-12?0:Math.abs(v-1)<1e-12?1:Math.abs(v+1)<1e-12?-1:v;
function operation([name,arg]){
 if(name==='rotate_clockwise_deg'){
  const rad=arg*Math.PI/180,c=Math.cos(rad),s=Math.sin(rad);return [[c,-s],[s,c]];
 }
 if(name==='mirror_horizontal')return [[-1,0],[0,1]];
 if(name==='mirror_vertical')return [[1,0],[0,-1]];
 if(name==='scale_uniform')return [[arg,0],[0,arg]];
 if(name==='scale_xy')return [[arg[0],0],[0,arg[1]]];
 throw new Error('Unknown operation '+name);
}
const move=(point,M,targetPivot)=>[
 targetPivot[0]+M[0][0]*(point[0]-stamp.pivot[0])+M[0][1]*(point[1]-stamp.pivot[1]),
 targetPivot[1]+M[1][0]*(point[0]-stamp.pivot[0])+M[1][1]*(point[1]-stamp.pivot[1])
];
const matrix4=(M,tx,ty)=>[M[0][0],M[1][0],0,0,M[0][1],M[1][1],0,0,0,0,1,0,tx,ty,0,1].map(clean);
const entries=transforms.map((tr,i)=>{
 let M=[[1,0],[0,1]];
 const intermediate=[];
 for(const op of tr.operations){M=multiply(operation(op),M);intermediate.push({operation:op,linear_matrix:M.map(row=>row.map(clean))});}
 M=M.map(row=>row.map(clean));
 const col=i%4,row=Math.floor(i/4),cell={x:152+col*332,y:193+row*282,width:300,height:250};
 const center=[cell.x+150,cell.y+125];
 const localShift=[60-M[0][0]*60-M[0][1]*60,60-M[1][0]*60-M[1][1]*60];
 const worldShift=[center[0]-M[0][0]*60-M[0][1]*60,center[1]-M[1][0]*60-M[1][1]*60];
 const rectangles=stamp.rectangles.map((r,j)=>{
  const [x,y,w,h]=r.xywh,original=[[x,y],[x+w,y],[x+w,y+h],[x,y+h]];
  return {index:j,color:r.color,original_corners:original,local_corners:original.map(p=>move(p,M,stamp.pivot)),world_corners:original.map(p=>move(p,M,center))};
 });
 const dotLocal=move(stamp.dot.center,M,stamp.pivot),dotWorld=move(stamp.dot.center,M,center);
 const extent=[stamp.dot.radius*Math.hypot(M[0][0],M[0][1]),stamp.dot.radius*Math.hypot(M[1][0],M[1][1])];
 const polygonPoints=rectangles.flatMap(r=>r.world_corners);
 const bounds={left:Math.min(...polygonPoints.map(p=>p[0]),dotWorld[0]-extent[0]),top:Math.min(...polygonPoints.map(p=>p[1]),dotWorld[1]-extent[1]),right:Math.max(...polygonPoints.map(p=>p[0]),dotWorld[0]+extent[0]),bottom:Math.max(...polygonPoints.map(p=>p[1]),dotWorld[1]+extent[1])};
 const localBounds={left:Math.min(...rectangles.flatMap(r=>r.local_corners).map(p=>p[0]),dotLocal[0]-extent[0]),top:Math.min(...rectangles.flatMap(r=>r.local_corners).map(p=>p[1]),dotLocal[1]-extent[1]),right:Math.max(...rectangles.flatMap(r=>r.local_corners).map(p=>p[0]),dotLocal[0]+extent[0]),bottom:Math.max(...rectangles.flatMap(r=>r.local_corners).map(p=>p[1]),dotLocal[1]+extent[1])};
 return {id:tr.id,operations:tr.operations,intermediate,linear_matrix:M,
  local_pivot_affine_4x4_column_major:matrix4(M,...localShift),world_affine_4x4_column_major:matrix4(M,...worldShift),
  centered_alignment_linear_only_4x4_column_major:matrix4(M,0,0),
  cell,cell_center:center,rectangles,dot:{original_center:stamp.dot.center,original_radius:stamp.dot.radius,color:stamp.dot.color,local_center:dotLocal,world_center:dotWorld,axis_aligned_extent:extent},
  local_bounds:localBounds,world_bounds:bounds,
  all_subject_inside_cell:bounds.left>=cell.x&&bounds.top>=cell.y&&bounds.right<=cell.x+cell.width&&bounds.bottom<=cell.y+cell.height};
});
const result={generated_at:new Date().toISOString(),task_id:'A09',run_id:'20261002-204314-6f31',
 scope:'Independent input mathematics; layout is exact geometrically centered 4×3 cell grid for root use; actual rendered geometry must be compared separately',
 sources:{stamp:sourceStamp,transforms:sourceTransforms,stamp_sha256:crypto.createHash('sha256').update(stampBytes).digest('hex'),transforms_sha256:crypto.createHash('sha256').update(transformBytes).digest('hex')},
 formula:'M starts identity; M←operation_matrix·M in listed order. Image y increases downward, so clockwise rotation is [[cos,-sin],[sin,cos]]. Point output = target_pivot+M·(point-(60,60)).',
 matrix_variants:'local_pivot_affine applies alignment=null with pivot translation. world_affine also places final center in cell. centered_alignment_linear_only applies alignment=CENTER on fixed 120×120 child, positioned at cell_center-(60,60). These variants are alternatives, not translations to combine twice.',
 grid:{canvas:[1600,1200],columns:4,rows:3,cell_width:300,cell_height:250,gap:32,outer_width:1296,outer_height:814,origin:[152,193],geometric_center:[800,600]},
 transforms:entries,
 order_example:{T07:entries[6].linear_matrix,T08:entries[7].linear_matrix,dot_T07_local:entries[6].dot.local_center,dot_T08_local:entries[7].dot.local_center,
 explanation:'T07=R90·H=[[0,-1],[-1,0]], dot becomes (71,29). T08=H·R90=[[0,1],[1,0]], dot becomes (49,91).'},
 tolerance_px:1.5,antialias_exception:'Use fully painted interiors and tolerate antialias pixels at edges; 30-degree corners need analytic edge fit or pixel-center distance, not one exact-color extreme pixel.'};
fs.writeFileSync(path.join(__dirname,'transform-facts-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({grid:result.grid,transforms:entries.map(e=>({id:e.id,M:e.linear_matrix,dot:e.dot.local_center,local_bounds:e.local_bounds,inside:e.all_subject_inside_cell})),order_example:result.order_example},null,2));
