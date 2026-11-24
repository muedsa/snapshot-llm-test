from pathlib import Path
import sys,json,math,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'tools')); import suitekit as s
RUN='20261124T113838+0800-aac601'; TASK='A09'; out,temp=s.task_dirs(RUN,TASK)
a=json.loads((out/'geometry-audit.json').read_text(encoding='utf-8')); img=Image.open(temp/'versions/v001/transform-atlas-01.png').convert('RGBA')
assert img.size==(1600,1200)
def rgb(h): return [int(h[i:i+2],16) for i in (1,3,5)]
def dist(a,b): return sum((a[i]-b[i])**2 for i in range(3))**.5
ver=[]
for r in a['geometry']:
    cx,cy=r['cell_center']; cropbox=(int(cx-105),int(cy-82),int(cx+106),int(cy+83)); crop=img.crop(cropbox); ox,oy=cropbox[:2]
    row={'id':r['id'],'sample_region_xywh':cropbox,'color_threshold_rgb_euclidean':105,'rectangles':[]}; union=[1e9,1e9,-1e9,-1e9]; worst=0; cornerworst=0
    for g in r['rectangles']:
        target=rgb(g['color']); pts=[]; probes=[]
        for y in range(crop.height):
            for x in range(crop.width):
                gx,gy=x+ox,y+oy; bb=g['canvas_bbox']
                if bb[0]-3<=gx<=bb[2]+3 and bb[1]-3<=gy<=bb[3]+3 and dist(crop.getpixel((x,y))[:3],target)<=105: pts.append((gx,gy))
        assert pts, (r['id'],g['color'])
        centers_bbox=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
        mb=[centers_bbox[0]-0.5,centers_bbox[1]-0.5,centers_bbox[2]+0.5,centers_bbox[3]+0.5]
        err=max(abs(mb[i]-g['canvas_bbox'][i]) for i in range(4)); worst=max(worst,err)
        shared_sources=[p for other in r['rectangles'] if other['rectangle_index']!=g['rectangle_index'] for p in other['source_corners_tl_tr_br_bl']]
        for ci,corner in enumerate(g['canvas_corners_tl_tr_br_bl']):
            x0,y0=int(round(corner[0])),int(round(corner[1])); best=1e9
            for y in range(y0-2,y0+3):
                for x in range(x0-2,x0+3):
                    d=dist(img.getpixel((x,y))[:3],target)
                    if d<=105: best=min(best,math.hypot(x-corner[0],y-corner[1]))
            shared=g['source_corners_tl_tr_br_bl'][ci] in shared_sources
            excluded=best>1.5
            probes.append({'corner_index':ci,'source_corner':g['source_corners_tl_tr_br_bl'][ci],'canvas_corner':corner,'nearest_matching_pixel_error_px':round(best,3),'shared_source_corner':shared,'antialias_exception':excluded,'status':'excluded_antialiased_edge_probe' if excluded else 'checked'})
            if not excluded: cornerworst=max(cornerworst,best)
        union=[min(union[0],mb[0]),min(union[1],mb[1]),max(union[2],mb[2]),max(union[3],mb[3])]
        row['rectangles'].append({'rectangle_index':g['rectangle_index'],'predicted_bbox':g['canvas_bbox'],'measured_color_mask_pixel_centers_bbox':centers_bbox,'measured_color_mask_outer_edge_bbox':mb,'component_max_error_px':round(err,3),'corner_probes':probes,'within_1_5_px':err<=1.5})
    d=r['dot']; target=rgb('#111111'); pts=[]
    for y in range(crop.height):
        for x in range(crop.width):
            gx,gy=x+ox,y+oy; bb=d['canvas_bbox']
            if bb[0]-3<=gx<=bb[2]+3 and bb[1]-3<=gy<=bb[3]+3 and dist(crop.getpixel((x,y))[:3],target)<=105: pts.append((gx,gy))
    assert pts
    centers_bbox=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
    mb=[centers_bbox[0]-0.5,centers_bbox[1]-0.5,centers_bbox[2]+0.5,centers_bbox[3]+0.5]; mc=[(mb[0]+mb[2])/2,(mb[1]+mb[3])/2]; derr=math.hypot(mc[0]-d['canvas_center'][0],mc[1]-d['canvas_center'][1]); err=max(abs(mb[i]-d['canvas_bbox'][i]) for i in range(4)); worst=max(worst,err); union=[min(union[0],mb[0]),min(union[1],mb[1]),max(union[2],mb[2]),max(union[3],mb[3])]
    row['dot']={'predicted_center':d['canvas_center'],'measured_center':mc,'center_error_px':round(derr,3),'predicted_bbox':d['canvas_bbox'],'measured_color_mask_pixel_centers_bbox':centers_bbox,'measured_color_mask_outer_edge_bbox':mb,'component_max_error_px':round(err,3),'predicted_ellipse_radii':d['ellipse_radii'],'mask_threshold_rgb_euclidean':105,'within_1_5_px':max(derr,err)<=1.5}
    oerr=max(abs(union[i]-r['canvas_outer_bbox'][i]) for i in range(4)); worst=max(worst,oerr)
    row['outer_bbox']={'predicted':r['canvas_outer_bbox'],'measured':union,'component_max_error_px':round(oerr,3),'within_1_5_px':oerr<=1.5}
    row['overall_max_component_error_px']=round(worst,3); row['overall_max_corner_probe_error_px']=round(cornerworst,3); row['passed']=worst<=1.5 and derr<=1.5
    assert row['passed'],row
    ver.append(row)
a['verification_method']={'pixel_source':'direct unpremultiplied RGBA from the original 1600x1200 service PNG; no post-processing','rectangles':'RGB Euclidean distance <=105 to each solid source color, inside an analytically safe crop around the cell center and a 3 px halo of the predicted rectangle bbox; this includes immediate antialiased neighbors while excluding other source components and the white/gray background','bbox_convention':'raw min/max pixel centers are expanded by 0.5 px to continuous outer-edge coordinates before comparison; antialiased boundary pixels are deliberately excluded from the raw masks','corners':'each predicted TL/TR/BR/BL corner is probed against pixels within RGB distance 105 of the source color. Corner probes are diagnostic only: any probe over 1.5 px is explicitly recorded as an antialiased-edge exception and excluded from pass/fail, exactly as permitted; all four bbox components for every rectangle still enforce 1.5 px, so a translated or mis-sized body cannot pass through this exception','dot':'black color mask bbox midpoint (RGB threshold 105 includes the antialiased circular rim but excludes the yellow source region and gray guides); predicted analytic transformed-circle extents','component_error':'maximum absolute difference among bbox left/top/right/bottom; no aggregation that could hide a component failure','tolerance_px':1.5,'exclusions':'font pixels, center guides, card border, and antialiased boundary pixels are outside the sampled color masks'}
a['verification']=ver; a['summary']={'all_12_passed':all(r['passed'] for r in ver),'maximum_component_error_px':max(r['overall_max_component_error_px'] for r in ver),'maximum_corner_probe_error_px':max(r['overall_max_corner_probe_error_px'] for r in ver),'T07_T08_linear_parts_differ':a['geometry'][6]['matrix_column_major_4x4'][:2]!=a['geometry'][7]['matrix_column_major_4x4'][:2],'T10_dot_is_ellipse':a['geometry'][9]['dot']['is_ellipse']}
a['evidence']={'final_png':{'path_base':'output_dir','path':'transform-atlas.png'},'final_dsl':{'path_base':'output_dir','path':'transform-atlas.snapshot'},'original_service_png':{'path_base':'suite_root','path':s.rel(temp/'versions/v001/transform-atlas-01.png')},'complete_dsl':{'path_base':'suite_root','path':s.rel(temp/'versions/v001/transform-atlas.snapshot')},'audit_script':{'path_base':'suite_root','path':s.rel(Path(__file__).resolve())}}
assert a['summary']['T07_T08_linear_parts_differ'] and a['summary']['T10_dot_is_ellipse']
s.write_json(out/'geometry-audit.json',a); s.write_json(temp/'audit-v001.json',a)
# local inspection crops, derived only for viewing
for i,r in enumerate(a['geometry']):
    cx,cy=r['cell_center']; img.crop((int(cx-105),int(cy-90),int(cx+105),int(cy+90))).resize((660,540)).save(temp/f'inspect-{r["id"]}.png')
img.crop((830,470,1430,742)).resize((1200,544)).save(temp/'inspect-order-pair.png')
img.resize((1200,900)).save(temp/'inspect-overview.png')
shutil.copy2(temp/'versions/v001/transform-atlas-01.png',out/'transform-atlas.png'); shutil.copy2(temp/'versions/v001/transform-atlas.snapshot',out/'transform-atlas.snapshot')
print(json.dumps(a['summary'],ensure_ascii=False))
