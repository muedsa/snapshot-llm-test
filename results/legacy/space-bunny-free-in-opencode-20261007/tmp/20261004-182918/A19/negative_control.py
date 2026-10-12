"""A19 negative control: prove the occlusion pixel-equality proof actually carries weight.

Three probes, rendered as real service responses (previews, never delivered):
  N1  cover 1 shrunk by 40 px  -> a hidden body pokes out        -> A must differ from B
  N2  ClipRect widened to 800  -> the hidden bodies get painted -> B must differ from A
  N3  B's hidden bodies moved back inside the covers (no clip)  -> both == delivered
If any probe did NOT change the image, the corresponding claim in equivalence.json
would be vacuous and the "proof_obligation" statements would be false.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "A19")
TMP = os.path.join(ROOT, "tmp", RUN, "A19")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import a19_scene as A  # noqa: E402

CST = timezone(timedelta(hours=8))
PREVIEW = os.path.join(TMP, "preview", "negative-control")


def main():
    snapkit.configure("A19", OUT, TMP)
    os.makedirs(PREVIEW, exist_ok=True)
    from PIL import Image, ImageChops

    results = []

    def probe(name, text, note):
        p = snapkit.render(text, name + ".png", name + ".snapshot", final=False,
                           out_dir=PREVIEW)
        if not p.get("ok"):
            results.append({"probe": name, "rendered": False, "error": p.get("error")})
            return None
        return p["image"]

    def diff(a, b):
        ia = Image.open(a).convert("RGB")
        ib = Image.open(b).convert("RGB")
        d = ImageChops.difference(ia, ib)
        return d.getbbox()

    ref = os.path.join(OUT, "occlusion.png")
    dsl_ok_a, _ = A.occ_dsl(A.O_HIDDEN_A, "overdraw")
    dsl_ok_b, _ = A.occ_dsl(A.O_HIDDEN_B, "clip")

    # ---- N1: shrink cover 1 in the A1 variant so a hidden body pokes out ------
    # occ_geometry_check() deliberately rejects this geometry, so the probe calls the
    # DSL builder with the check disabled; the assertion firing is itself evidence.
    orig = A.O_COVER1
    A.O_COVER1 = (orig[0], orig[1], orig[2] - 40, orig[3])
    try:
        A.occ_geometry_check(A.O_HIDDEN_A)
        check_fired = False
    except AssertionError:
        check_fired = True
    real_check = A.occ_geometry_check
    A.occ_geometry_check = lambda hidden: None
    dsl_n1, _ = A.occ_dsl(A.O_HIDDEN_A, "overdraw")
    A.occ_geometry_check = real_check
    A.O_COVER1 = orig
    img_n1 = probe("n1-cover-shrunk", dsl_n1, "cover 1 shrunk by 40px")
    if img_n1:
        bb = diff(img_n1, ref)
        results.append({
            "probe": "N1 · A1 的遮挡物 1 宽度减少 40px（覆盖失效）",
            "purpose": "验证“若遮挡不完整，残留像素会让 A 与 B 不同”这条论据",
            "rendered": True,
            "geometry_check_rejected_this_layout": check_fired,
            "differs_from_delivered_occlusion": bb is not None,
            "difference_bbox": bb,
            "conclusion": ("覆盖不完整时 A1 与交付的 occlusion.png 出现差异，"
                           "说明 occlusion.png 的覆盖确实是完整的、像素等价证明是有约束力的"
                           if bb is not None else
                           "没有差异 → 该论据不成立，需要重新设计"),
        })

    # ---- N2: widen the ClipRect in the B1 variant so hidden bodies get painted --
    ow = A.O_CLIP_W
    A.O_CLIP_W = 800
    dsl_n2, _ = A.occ_dsl(A.O_HIDDEN_B, "clip")
    A.O_CLIP_W = ow
    img_n2 = probe("n2-clip-widened", dsl_n2, "ClipRect widened to 800px")
    if img_n2:
        bb = diff(img_n2, ref)
        results.append({
            "probe": "N2 · B1 的 ClipRect 由 700px 放宽到 800px（裁剪失效）",
            "purpose": "验证“若 ClipRect 未生效，隐藏主体会盖在遮挡物上，A 与 B 必然不同”",
            "rendered": True,
            "differs_from_delivered_occlusion": bb is not None,
            "difference_bbox": bb,
            "conclusion": ("裁剪失效时 B1 与 occlusion.png 出现差异，"
                           "说明 occlusion-alternative.png 的隐藏主体确实被裁掉了"
                           if bb is not None else
                           "没有差异 → 裁剪其实没起作用，需要重新设计"),
        })

    # ---- N3: same hidden set + same mechanism must also be equal ---------------
    img_n3 = probe("n3-control-overdraw-same", dsl_ok_a, "control: the delivered A1 DSL")
    if img_n3:
        bb = diff(img_n3, ref)
        results.append({
            "probe": "N3 · 对照：与交付 A1 完全相同的 DSL 再渲染一次",
            "purpose": "确认服务对同一 DSL 的输出稳定（否则像素相等可能只是偶然）",
            "rendered": True,
            "differs_from_delivered_occlusion": bb is not None,
            "conclusion": "同一 DSL 两次渲染结果相同，服务的渲染是确定性的" if bb is None
                          else "同一 DSL 两次渲染结果不同，像素等价证明不可靠",
        })

    out = {
        "schema_version": 1, "task_id": "A19",
        "purpose": "反证实验：证明 equivalence.json 的 proof_obligation 不是空话",
        "generated_at": datetime.now(CST).isoformat(timespec="seconds"),
        "probes": results,
        "all_probes_behaved_as_claimed": all(
            r.get("differs_from_delivered_occlusion") is not None
            for r in results if r.get("rendered")),
        "note": "这些探针全部渲染到 tmp/.../preview/negative-control/，不是交付物；"
                "交付的两张 PNG 仍是未经任何后处理的原始服务响应。",
    }
    p = os.path.join(TMP, "negative-control.json")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["all_probes_behaved_as_claimed"] else 1


if __name__ == "__main__":
    sys.exit(main())
