"""Read-only service-PNG QA against independently calculated stamp geometry.

No image editing, generating, cropping or final artifact writing. Pixel centers
are (integer x+0.5, integer y+0.5). Pure fills and AA candidates are reported
separately; analytic corners/bounds use 1.5 px tolerance.
"""
import argparse, collections, datetime, hashlib, json, math, pathlib
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('png')
parser.add_argument('facts')
parser.add_argument('output')
args = parser.parse_args()
image_path = pathlib.Path(args.png)
im = Image.open(image_path).convert('RGB')
pixels = im.load()
facts = json.loads(pathlib.Path(args.facts).read_text(encoding='utf-8'))
tolerance = 1.5

def rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1,3,5))

def near_color(value, color):
    return max(abs(a-b) for a,b in zip(value,color)) <= 3

def bbox(points, cover_pixels=True):
    if not points:
        return None
    # points denote pixel centers. Convert back to occupied pixel cell limits.
    extra = .5 if cover_pixels else 0
    return dict(left=min(p[0] for p in points)-extra,
                top=min(p[1] for p in points)-extra,
                right=max(p[0] for p in points)+extra,
                bottom=max(p[1] for p in points)+extra)

def expected_bbox(points):
    return dict(left=min(p[0] for p in points), top=min(p[1] for p in points),
                right=max(p[0] for p in points), bottom=max(p[1] for p in points))

def errors(actual, expected):
    return {k: actual[k]-expected[k] for k in expected} if actual else None

def distance_to_segment(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def polygon_relation(p, polygon):
    cross=[]
    for a,b in zip(polygon, polygon[1:]+polygon[:1]):
        cross.append((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
    inside=all(v >= -1e-8 for v in cross) or all(v <= 1e-8 for v in cross)
    distance=min(distance_to_segment(p,a,b) for a,b in zip(polygon,polygon[1:]+polygon[:1]))
    return inside,distance

def aa_blend(value, color, background):
    direction=[color[i]-background[i] for i in range(3)]
    length2=sum(v*v for v in direction)
    if not length2:
        return False
    alpha=sum((value[i]-background[i])*direction[i] for i in range(3))/length2
    residual=math.sqrt(sum((value[i]-(background[i]+alpha*direction[i]))**2 for i in range(3)))
    return .15 <= alpha <= 1.015 and residual <= 18

entries=[]
for tr in facts['transforms']:
    cell=tr['cell']
    bounds=(int(cell['x']),int(cell['y']),int(cell['x']+cell['width']),int(cell['y']+cell['height']))
    counts=collections.Counter(pixels[x,y] for y in range(bounds[1],bounds[3]) for x in range(bounds[0],bounds[2]))
    background=counts.most_common(1)[0][0]
    all_pure=[]
    rectangles=[]
    for rectangle in tr['rectangles']:
        color=rgb(rectangle['color'])
        pure=[(x+.5,y+.5) for y in range(bounds[1],bounds[3]) for x in range(bounds[0],bounds[2]) if near_color(pixels[x,y],color)]
        all_pure.extend(pure)
        polygon=rectangle['world_corners']
        corner_checks=[]
        for corner in polygon:
            pure_distance=min((math.hypot(p[0]-corner[0],p[1]-corner[1]) for p in pure), default=None)
            aa=[]
            for y in range(max(bounds[1],math.floor(corner[1]-3)),min(bounds[3],math.ceil(corner[1]+3))):
                for x in range(max(bounds[0],math.floor(corner[0]-3)),min(bounds[2],math.ceil(corner[0]+3))):
                    if aa_blend(pixels[x,y],color,background):
                        aa.append((x+.5,y+.5))
            aa_distance=min((math.hypot(p[0]-corner[0],p[1]-corner[1]) for p in aa), default=None)
            pure_ok=pure_distance is not None and pure_distance <= tolerance
            aa_exception=not pure_ok and aa_distance is not None and aa_distance <= tolerance
            corner_checks.append(dict(expected=corner,nearest_pure_pixel_distance=pure_distance,
                nearest_AA_supported_pixel_distance=aa_distance,pure_pass=pure_ok,
                antialias_edge_exception=aa_exception,passes=pure_ok or aa_exception))
        outside=[]
        for point in pure:
            inside,distance=polygon_relation(point,polygon)
            if not inside and distance > tolerance:
                outside.append(dict(pixel_center=point,distance=distance))
        expected=expected_bbox(polygon)
        measured=bbox(pure)
        bound_errors=errors(measured,expected)
        bounds_pass=bound_errors is not None and max(abs(v) for v in bound_errors.values()) <= tolerance
        inner_count=0
        inner_mismatch=0
        for y in range(max(bounds[1],math.floor(expected['top'])),min(bounds[3],math.ceil(expected['bottom']))):
            for x in range(max(bounds[0],math.floor(expected['left'])),min(bounds[2],math.ceil(expected['right']))):
                inside,distance=polygon_relation((x+.5,y+.5),polygon)
                if inside and distance > tolerance:
                    inner_count+=1
                    if not near_color(pixels[x,y],color):
                        inner_mismatch+=1
        rectangles.append(dict(index=rectangle['index'],color=rectangle['color'],pure_pixel_count=len(pure),
            corners=corner_checks,expected_bounds=expected,measured_pure_bounds=measured,bound_errors=bound_errors,
            bounds_within_1_5px=bounds_pass,pure_pixels_outside_polygon_over_1_5px_count=len(outside),
            first_outliers=outside[:8],analytic_interior_pixels_over_1_5px_from_edge=inner_count,
            interior_wrong_color_count=inner_mismatch,
            passes=bool(pure) and all(c['passes'] for c in corner_checks) and bounds_pass and not outside and not inner_mismatch))
    dot=tr['dot']
    dot_color=rgb(dot['color'])
    dc=dot['world_center']; extent=dot['axis_aligned_extent']
    dot_limits=(max(bounds[0],math.floor(dc[0]-extent[0]-3)),max(bounds[1],math.floor(dc[1]-extent[1]-3)),
                min(bounds[2],math.ceil(dc[0]+extent[0]+3)),min(bounds[3],math.ceil(dc[1]+extent[1]+3)))
    dot_pure=[(x+.5,y+.5) for y in range(dot_limits[1],dot_limits[3]) for x in range(dot_limits[0],dot_limits[2]) if near_color(pixels[x,y],dot_color)]
    all_pure.extend(dot_pure)
    measured_center=[sum(p[i] for p in dot_pure)/len(dot_pure) for i in range(2)] if dot_pure else None
    center_error=math.dist(measured_center,dc) if measured_center else None
    dot_expected=dict(left=dc[0]-extent[0],top=dc[1]-extent[1],right=dc[0]+extent[0],bottom=dc[1]+extent[1])
    dot_bounds=bbox(dot_pure);dot_errors=errors(dot_bounds,dot_expected)
    dot_pass=center_error is not None and center_error <= tolerance and dot_errors is not None and max(abs(v) for v in dot_errors.values()) <= tolerance
    combined=bbox(all_pure);combined_errors=errors(combined,tr['world_bounds'])
    combined_pass=combined_errors is not None and max(abs(v) for v in combined_errors.values()) <= tolerance
    entries.append(dict(id=tr['id'],cell_bounds=bounds,estimated_flat_background=background,
        rectangles=rectangles,dot=dict(expected_center=dc,measured_pure_centroid=measured_center,
            center_error_px=center_error,pure_pixel_count=len(dot_pure),expected_bounds=dot_expected,
            measured_pure_bounds=dot_bounds,bound_errors=dot_errors,passes=dot_pass),
        expected_subject_bounds=tr['world_bounds'],measured_pure_subject_bounds=combined,
        subject_bound_errors=combined_errors,subject_bounds_within_1_5px=combined_pass,
        passes=all(r['passes'] for r in rectangles) and dot_pass and combined_pass))

report=dict(generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),task_id='A09',
    source_png=str(image_path.resolve()),source_png_sha256=hashlib.sha256(image_path.read_bytes()).hexdigest(),
    image_size=im.size,tolerance_px=tolerance,
    method='Per 300×250 cell exact interior fill segmentation (RGB distance ≤3), pixel centers x+0.5/y+0.5, predicted-corner nearest-fill/AA distance, bounds occupied-cell extents, pure pixels outside analytic quadrilateral, full-color interior coverage and black-dot centroid. AA-supported corners explicitly separated from pure-fill matches.',
    limitations='AA color blend is estimated against modal cell background; if edge crosses a guide line, residual can be affected. This quantitative check does not replace actual image inspection. Geometry facts independently computed from input; any artifact mismatch is preserved in output.',
    transforms=entries,all_checks_pass=all(t['passes'] for t in entries),
    antialias_corner_exceptions=sum(c['antialias_edge_exception'] for t in entries for r in t['rectangles'] for c in r['corners']))
with pathlib.Path(args.output).open('x',encoding='utf-8') as f:
    json.dump(report,f,ensure_ascii=False,indent=2)
    f.write('\n')
print(json.dumps(dict(all_checks_pass=report['all_checks_pass'],AA_corner_exceptions=report['antialias_corner_exceptions'],
    transforms=[dict(id=t['id'],passes=t['passes'],dot_center_error=t['dot']['center_error_px'],
        max_subject_bound_error=max(abs(v) for v in t['subject_bound_errors'].values()) if t['subject_bound_errors'] else None,
        failed_rectangles=[r['index'] for r in t['rectangles'] if not r['passes']]) for t in entries]),ensure_ascii=False,indent=2))
