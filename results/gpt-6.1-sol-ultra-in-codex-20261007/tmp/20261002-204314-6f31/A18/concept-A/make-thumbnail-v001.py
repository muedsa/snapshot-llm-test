from pathlib import Path
from PIL import Image
import json,hashlib
base=Path(__file__).resolve().parent
meta=json.loads((base/'render-v001.json').read_text(encoding='utf-8'))
raw=Path(meta['image_path']).read_bytes()
dest=base/'concept-A-v001.png'
with dest.open('xb') as f:f.write(raw)
image=Image.open(meta['image_path'])
qa=base/'concept-A-thumbnail-v001.png'
if qa.exists():raise FileExistsError(qa)
image.resize((400,250),Image.Resampling.LANCZOS).save(qa)
proof={'raw_copy_path':str(dest),'raw_service_path':meta['image_path'],'bytes_unchanged':dest.read_bytes()==raw,'SHA256':hashlib.sha256(raw).hexdigest(),'thumbnail_path':str(qa),'thumbnail_width':400,'thumbnail_height':250,'thumbnail_is_QA_only':True}
p=base/'thumbnail-provenance-v001.json'
with p.open('x',encoding='utf-8') as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps(proof,ensure_ascii=False))
