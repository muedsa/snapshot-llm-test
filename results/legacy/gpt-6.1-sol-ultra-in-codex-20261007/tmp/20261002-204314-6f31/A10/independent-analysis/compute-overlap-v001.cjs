const fs=require('fs'),path=require('path');
const alpha=128/255;
const composite=(front,back,a)=>front.map((v,i)=>v*a+back[i]*(1-a));
const white=[255,255,255],red=[255,0,0],blue=[0,0,255];
const afterRed=composite(red,white,alpha);
const individual=composite(blue,afterRed,alpha);
const grouped=composite(blue,white,.5);
const round=a=>a.map(Math.round);
const result={generated_at:new Date().toISOString(),task_id:'A10',run_id:'20261002-204314-6f31',
 scope:'Independent expected RGB computation before sampling actual PNG',
 sample_point_local:[180,100],background_rgb:white,rectangle_geometry:{red:[40,40,160,120],blue:[120,80,160,120],blue_on_top:true},
 experiment_1:{individual_color_alpha_hex:'80',alpha_fraction:'128/255',alpha_value:alpha,
  formula:'out=blue·a+(red·a+white·(1−a))·(1−a); channel arithmetic in encoded RGB',
  red_then_white_rgb:afterRed,overlap_exact_rgb:individual,overlap_nearest_integer_rgb:round(individual)},
 experiment_2:{group_opacity:.5,formula:'Opaque blue already replaces opaque red in overlap inside group; out=blue·0.5+white·0.5',
  flattened_overlap_rgb:blue,overlap_exact_rgb:grouped,overlap_nearest_integer_rgb:round(grouped)},
 expected_visible_difference:'Individual alpha retains the first red layer contribution in the overlap; group opacity fades only the final opaque blue at that location.',
 rounding_note:'128/255≈0.501960784 rather than exactly0.5. The ideal group channels127.5 are an 8-bit rounding boundary; actual Skia alpha quantization can yield127 or128. Preserve measured PNG RGB instead of silently adjusting theory.',
 actual_sampling_status:'pending real service PNG',actual_overlap_rgb:null,
 actual_cost_tokens:null};
fs.writeFileSync(path.join(__dirname,'overlap-facts-v001.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result,null,2));
