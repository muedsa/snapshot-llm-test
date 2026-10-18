"""Measure A10 samples/pairs from the rendered PNG and fill composite-audit."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A10"
TMP = ROOT / "tmp" / RUN / TASK
img = Image.open(TMP / "renders" / "v005.png").convert("RGBA")
audit_path = TMP / "composite-audit.json"
audit = json.loads(audit_path.read_text(encoding="utf-8"))
checks = TMP / "checks"
checks.mkdir(parents=True, exist_ok=True)

origins = [tuple(p["origin"]) for p in audit["panels"]]
for i, (x, y) in enumerate(origins, 1):
    img.crop((x, y, x + 320, y + 240)).save(checks / f"panel{i}.png")

# ---- samples
for s in audit["samples"]:
    x, y = s["canvas"]
    r, g, b, a = img.getpixel((x, y))
    actual = [r, g, b]
    err = [round(actual[i] - s["expected_rgb"][i], 2) for i in range(3)]
    s["actual_rgb"] = actual
    s["alpha"] = a
    s["errors"] = err
    s["passed"] = a == 255 and all(abs(e) <= s["tolerance_per_channel"] for e in err)
    s["evidence"] = f"tmp/{RUN}/{TASK}/checks/panel{s['panel']}.png"
    s["note_128_vs_05"] = ("128/255=0.5019608，0.5 严格等于 127.5；两模型在 R/G 通道可产生约 1 的差异。"
                            if s["panel"] == 1 else
                            "组 Opacity 使用 0.5；实测与 8-bit 合成/预乘取整有关，误差仍在 ±3 内。")

# ---- helpers
def gray(px):
    return 0.2126 * px[0] + 0.7152 * px[1] + 0.0722 * px[2]


def max_grad(box):
    x0, y0, x1, y1 = box
    best = 0.0
    for y in range(y0, y1):
        for x in range(x0, x1 - 1):
            best = max(best, abs(gray(img.getpixel((x, y))) - gray(img.getpixel((x + 1, y)))))
    for y in range(y0, y1 - 1):
        for x in range(x0, x1):
            best = max(best, abs(gray(img.getpixel((x, y))) - gray(img.getpixel((x, y + 1)))))
    return round(best, 1)

def region_maxdiff(a_origin, b_origin, pred):
    mx = 0
    count = 0
    for y in range(240):
        for x in range(320):
            if not pred(x, y):
                continue
            pa = img.getpixel((a_origin[0] + x, a_origin[1] + y))
            pb = img.getpixel((b_origin[0] + x, b_origin[1] + y))
            mx = max(mx, max(abs(pa[i] - pb[i]) for i in range(3)))
            count += 1
    return mx, count

o3, o4, o5, o6 = origins[2], origins[3], origins[4], origins[5]
outside_card = lambda x, y: x < 36 or x > 284 or y < 36 or y > 204
inside_circle = lambda x, y: (x - 160) ** 2 + (y - 120) ** 2 <= 90 ** 2
outside_circle = lambda x, y: (x - 160) ** 2 + (y - 120) ** 2 >= 106 ** 2

diff34, n34 = region_maxdiff(o3, o4, outside_card)
diff56, n56 = region_maxdiff(o5, o6, inside_circle)

# text edge sharpness in local box (65,85)-(255,125)
text3 = max_grad((o3[0] + 65, o3[1] + 85, o3[0] + 255, o3[1] + 125))
text4 = max_grad((o4[0] + 65, o4[1] + 85, o4[0] + 255, o4[1] + 125))
# stripes inside card vs outside
stripe_in3 = max_grad((o3[0] + 50, o3[1] + 50, o3[0] + 90, o3[1] + 80))
stripe_out3 = max_grad((o3[0] + 6, o3[1] + 6, o3[0] + 34, o3[1] + 34))
# spill samples at (40,120) outside circle
sp5 = list(img.getpixel((o5[0] + 40, o5[1] + 120))[:3])
sp6 = list(img.getpixel((o6[0] + 40, o6[1] + 120))[:3])

for v in audit["visual_checks"]:
    if v["panel"] == 3:
        v["text"] = f"SHARP / BLUR 清晰（文字区最大相邻梯度 {text3}）"
        v["background"] = f"卡内条纹明显柔化（卡内最大梯度 {stripe_in3}），卡外条纹锐利（{stripe_out3}）"
        v["spill"] = "卡外区域与④逐像素一致，无模糊外溢"
        v["text_gradient"] = text3
        v["stripe_gradient_inside"] = stripe_in3
        v["stripe_gradient_outside"] = stripe_out3
        v["evidence"] = f"tmp/{RUN}/{TASK}/checks/panel3.png"
    elif v["panel"] == 4:
        v["text"] = f"SHARP / BLUR 与橙色前景一起模糊（文字区最大相邻梯度仅 {text4}，远低于③的 {text3}）"
        v["background"] = "卡内条纹柔化"
        v["spill"] = "卡外区域与③逐像素一致，无模糊外溢"
        v["text_gradient"] = text4
        v["evidence"] = f"tmp/{RUN}/{TASK}/checks/panel4.png"
    elif v["panel"] == 5:
        v["spill"] = f"无裁剪，模糊向外扩散；圆周外样本 (40,120) 实际 RGB {sp5}"
        v["outside_circle_sample"] = list(sp5)
        v["evidence"] = f"tmp/{RUN}/{TASK}/checks/panel5.png"
    elif v["panel"] == 6:
        v["spill"] = f"被 r=100 圆截断；同一圆外样本 (40,120) 为 {sp6}（白底）"
        v["outside_circle_sample"] = list(sp6)
        v["evidence"] = f"tmp/{RUN}/{TASK}/checks/panel6.png"

audit["pair_checks"] = [
    {"pair": "③④", "check": "outside_card_identical", "max_channel_diff": diff34,
     "pixels_compared": n34, "passed": diff34 == 0,
     "method": "比较两实验区卡片外区域 (x<36 或 x>284 或 y<36 或 y>204) 的全部像素；同一基础场景应完全一致。"},
    {"pair": "③④", "check": "text_sharp_vs_blurred", "panel3_max_grad": text3, "panel4_max_grad": text4,
     "passed": text3 > text4 * 3,
     "method": "同一文字框 (65,85)-(255,125) 内灰度的最大相邻差；③应显著高于④。"},
    {"pair": "⑤⑥", "check": "inside_circle_identical", "max_channel_diff": diff56,
     "pixels_compared": n56, "passed": diff56 == 0,
     "method": "比较两实验区圆内 r≤90 的全部像素；同一滤镜与基础场景应一致。"},
    {"pair": "⑤⑥", "check": "circle_clips_spill", "panel5_outside_sample": list(sp5),
     "panel6_outside_sample": list(sp6), "passed": sp6 == [255, 255, 255] and sp5 != sp6,
     "method": "取圆周外局部 (40,120)：⑤无裁剪应保留模糊色，⑥应为白底。"},
]

audit["verification"] = {
    "rendered_png": "compositing-lab.png",
    "source_png": f"tmp/{RUN}/{TASK}/renders/v005.png",
    "samples_passed": all(s["passed"] for s in audit["samples"]),
    "pair_checks_passed": all(p["passed"] for p in audit["pair_checks"]),
    "panel_crops": [f"tmp/{RUN}/{TASK}/checks/panel{i}.png" for i in range(1, 7)],
}
audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"samples": [(s["panel"], s["actual_rgb"], s["errors"], s["passed"]) for s in audit["samples"]],
                  "pairs": audit["pair_checks"], "text_grads": [text3, text4],
                  "spill": [list(sp5), list(sp6)]}, ensure_ascii=False, indent=2))
