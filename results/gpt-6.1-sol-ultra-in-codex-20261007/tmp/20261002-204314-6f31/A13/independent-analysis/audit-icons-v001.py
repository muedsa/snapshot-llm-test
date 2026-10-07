"""Read-only raw RGBA pair audit; any32px files are QA derivatives, never final icons."""
from PIL import Image
from pathlib import Path
import json,sys,hashlib,datetime
color,black,out=map(Path,sys.argv[1:4]);out=out.resolve()
if out.exists():raise SystemExit('Refuse prior evidence overwrite')
ims=[Image.open(p).convert('RGBA')for p in [color,black]]
def data_stats(im):
 vals=list(im.getdata());alpha=[v[3]for v in vals];bbox=im.getchannel('A').getbbox()
 return {'dimensions':list(im.size),'alpha_nonzero':sum(v>0 for v in alpha),'alpha_zero':sum(v==0 for v in alpha),'alpha_255':sum(v==255 for v in alpha),'alpha_antialiased_partial':sum(0<v<255 for v in alpha),'alpha_levels':sorted(set(alpha)),'alpha_bbox':list(bbox)if bbox else None,'true_transparent_canvas':sum(v==0 for v in alpha)>0,'outer_edge_all_alpha_zero':all(im.getpixel((x,y))[3]==0 for x,y in [(x,0)for x in range(im.width)]+[(x,im.height-1)for x in range(im.width)]+[(0,y)for y in range(im.height)]+[(im.width-1,y)for y in range(im.height)])}
pair=[]
for p,im in zip([color,black],ims):pair.append({'png':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),**data_stats(im)})
bad=[{'xy':[n%ims[1].width,n//ims[1].width],'rgba':list(v)}for n,v in enumerate(ims[1].getdata())if v[3]>0 and any(v[k]!=0 for k in range(3))]
a0=list(ims[0].getchannel('A').getdata());a1=list(ims[1].getchannel('A').getdata());mismatches=sum(v!=w for v,w in zip(a0,a1))if ims[0].size==ims[1].size else None
r={'task_id':'A13','reviewer':'a10_audit_resume','measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual raw Snapshot PNG alpha/RGB measurement; not an image transformation or synthesized expected output.','pair':pair,'black_pixels_with_alpha_gt0_and_any_rgb_not0':len(bad),'black_violation_examples':bad[:20],'black_nontransparent_rgb_exact0_pass':not bad,'same_alpha_array_exactly':mismatches==0,'alpha_mismatch_pixels':mismatches,'both_dimensions_512':all(im.size==(512,512)for im in ims),'sources_preserved':True}
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:r[k]for k in ['both_dimensions_512','black_nontransparent_rgb_exact0_pass','black_pixels_with_alpha_gt0_and_any_rgb_not0','same_alpha_array_exactly','alpha_mismatch_pixels']},indent=2))
