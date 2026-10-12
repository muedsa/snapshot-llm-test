"""Read-only visual QA derivative generator. Never modifies actual service bytes.

Example: python inspect-image.py INPUT.png OUTPUT.png --crop 0 0 600 600
All QA outputs must be kept in the task temporary directory, with a new name.
"""
from pathlib import Path
import argparse, json
from PIL import Image
p=argparse.ArgumentParser()
p.add_argument('input');p.add_argument('output');p.add_argument('--crop',nargs=4,type=int);p.add_argument('--max-width',type=int)
a=p.parse_args();src=Path(a.input).resolve();dst=Path(a.output).resolve()
if src==dst or dst.exists():raise SystemExit('Refuse to overwrite source or any prior preview')
im=Image.open(src);original=im.size
if a.crop:im=im.crop(tuple(a.crop))
if a.max_width and im.width>a.max_width:im=im.resize((a.max_width,round(im.height*a.max_width/im.width)),Image.Resampling.LANCZOS)
dst.parent.mkdir(parents=True,exist_ok=True);im.save(dst)
print(json.dumps({'source':str(src),'preview':str(dst),'original_size':original,'preview_size':im.size,'crop':a.crop,'purpose':'QA derivative, not a final service image'}))
