# -*- coding: utf-8 -*-
"""A03: restore browsable version PNGs from preserved raw responses and fix evidence links."""
import json
import os
import shutil
import sys
from pathlib import Path

from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
TASK = "A03"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
VER = TMP / "versions"
VER.mkdir(parents=True, exist_ok=True)

MAP = {
    "A03-R0005.bin": "attempt-05-bounded.png",
    "A03-R0007.bin": "final-v1-backdrop.png",
    "A03-R0008.bin": "final-v1b-rebalanced.png",
    "A03-R0012.bin": "final-v2-sigma18.png",
    "A03-R0013.bin": "final-v3-sigma10-round.png",
    "A03-R0014.bin": "final-v4-sigma10.png",
}
for src, dst in MAP.items():
    s = TMP / "responses" / src
    if s.exists() and s.stat().st_size:
        shutil.copyfile(s, VER / dst)
        print("restored", dst, s.stat().st_size)

# crop of the BackdropFilter version to document issue I12
crop_src = VER / "final-v1-backdrop.png"
if crop_src.exists():
    img = Image.open(crop_src)
    box = img.crop((230, 430, 1050, 610))
    box = box.resize((int(box.width * 1.35), int(box.height * 1.35)), Image.LANCZOS)
    box.save(TMP / "preview-backdrop.png")
    print("wrote preview-backdrop.png", box.size)

# patch repair-log evidence paths
log_path = OUT / "repair-log.json"
log = json.loads(log_path.read_text(encoding="utf-8"))
for issue in log["issues"]:
    if issue["id"] == "I12":
        issue["observed"]["evidence"] = f"tmp/{RUN_ID}/A03/preview-backdrop.png"
for v in log["versions"]:
    if v["version"] == "final-v1":
        v["png"] = f"tmp/{RUN_ID}/A03/versions/final-v1-backdrop.png"
    if v["version"] == "final-v2":
        v["png"] = f"tmp/{RUN_ID}/A03/versions/final-v4-sigma10.png"
log["versions"].append({
    "version": "final-v2b", "parent": "final-v1", "type": "visual",
    "dsl": f"outputs/{RUN_ID}/A03/system-pulse.snapshot",
    "response": f"tmp/{RUN_ID}/A03/responses/A03-R0013.bin",
    "png": f"tmp/{RUN_ID}/A03/versions/final-v3-sigma10-round.png",
    "http_status": 200, "viewed": True,
    "note": "σ 降到 10、彩色条端点为圆角；实图确认色带可辨但端点与卡边衔接略生硬",
})
log["versions"].append({
    "version": "final-v3", "parent": "final-v2b", "type": "visual",
    "dsl": f"outputs/{RUN_ID}/A03/system-pulse.snapshot",
    "response": f"tmp/{RUN_ID}/A03/responses/A03-R0014.bin",
    "png": f"outputs/{RUN_ID}/A03/system-pulse.png",
    "http_status": 200, "viewed": True,
    "note": "彩色条改直角端点，与卡片边界衔接自然；最终交付",
})
log["artifact_versions"] = {
    "note": "同一输出路径的历次渲染已按原始响应字节还原到临时目录，便于逐版查看",
    "versions_dir": f"tmp/{RUN_ID}/A03/versions/",
    "files": [f"tmp/{RUN_ID}/A03/versions/{v}" for v in MAP.values() if (VER / v).exists()],
}
log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("patched", log_path.relative_to(SUITE_ROOT).as_posix())
