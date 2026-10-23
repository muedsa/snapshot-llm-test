"""A10 诊断：定位 ③ 卡片内区域读到 (179,255,255) 的原因。

③④ 实测：卡片内区域统一读到 (179,255,255)。反推：
  若为 70% 白罩在模糊底色上：(179,255,255) = 0.702*255 + 0.298*x → x = (0,255,255) 纯青。
  这不可能来自深灰条 #1E293B 与白 #FFFFFF 的模糊。
所以要么 (a) BackdropFilter 实际未模糊（罩色直接透出），要么 (b) 模糊输出本身就是青色。

三种变体（同一画布、同一罩色 #B3FFFFFF）：
  noblur      —— 条形 + 70% 白罩（无滤镜），基线：确认罩色是否被正确解析为「70% 白」。
                 深条 [60,120) 处应为 0.702*255 + 0.298*(30,41,59) ≈ (223,224,227)。
  backdrop    —— 同 noblur，但罩前插 BackdropFilter（ClipRRect 包裹），应为 σ=6 模糊后的条形
                 再加罩。若结果与 noblur 相同，说明 BackdropFilter 没有起模糊作用。
  subtree     —— 把罩与条形整体放进 ImageFiltered，对照「子树模糊」的正确形态。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_diag.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))

import a10_client as CL                     # noqa: E402
import a10_scenes as C                      # noqa: E402
import suite as S                           # noqa: E402
from PIL import Image                       # noqa: E402

CW, CH = 400, 320
# 300×240 的 320×240 区域：深灰竖条周期 24（bar 14 / 间隙 10），罩卡 240×160 在 (40,40)
BARS = "".join(C.rect(40.0 + k * 24.0, 40.0, 14.0, 160.0, "#1E293B") for k in range(12))


def _wrap(inner: str) -> str:
    return ('<Snapshot type="png" background="#E9EEF5">'
            '<Container width="' + C.n(CW) + '" height="' + C.n(CH) + '">'
            + C.stack(C.rect(0.0, 0.0, 320.0, 240.0, "#FFFFFF"), inner, w=CW, h=CH)
            + "</Container></Snapshot>")


VEIL_AARRGBB = C.rect(40.0, 40.0, 240.0, 160.0, "#B3FFFFFF", radius=20.0)   # 误用：#AARRGGBB 写法
VEIL_RRGGBBAA = C.rect(40.0, 40.0, 240.0, 160.0, "#FFFFFFB3", radius=20.0)  # 正确：白 70%


def _backdrop_variant(veil: str) -> str:
    return _wrap(
        BARS
        + C.pos(40.0, 40.0, 240.0, 160.0,
                '<ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">'
                + '<BackdropFilter sigmaX="6" sigmaY="6" tileMode="CLAMP">'
                + C.container(240.0, 160.0)
                + "</BackdropFilter></ClipRRect>")
        + veil)


VARIANTS: dict[str, str] = {
    # (a) 无滤镜基线，误用 #B3FFFFFF：实测罩卡内为 (179,255,255) 不透明青，
    #     证明渲染器按 #RRGGBBAA 解析 8 位色（B3 被当成 R，FF 被当成 A）。
    "veil-wrong": _wrap(BARS + VEIL_AARRGBB),
    # (b) 无滤镜基线，正确 #FFFFFFB3：深条 [60,120) 处应为
    #     0.702*255 + 0.298*(30,41,59) ≈ (223,224,227)，验证「白 70%」写法。
    "veil-right": _wrap(BARS + VEIL_RRGGBBAA),
    # (c) 正确罩色 + BackdropFilter：只模糊罩下背景，条形的明暗应仍能在罩下看出。
    "veil-right-blur": _backdrop_variant(VEIL_RRGGBBAA),
    # (d) 正确罩色 + 子树整体模糊：对照 ImageFiltered 的形态。
    "veil-right-subtree": _wrap(
        '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">'
        + C.stack(BARS + VEIL_RRGGBBAA, w=320.0, h=240.0)
        + "</ImageFiltered>"),
}

# 采样点（画布坐标，0 索引）：罩内深条 / 罩内间隙 / 罩外
PTS = {"in_bar_local_60_120": (60, 120),
       "in_gap_local_70_120": (70, 120),
       "in_bar_local_200_100": (200, 100),
       "in_gap_local_210_100": (210, 100),
       "outside_local_16_100": (16, 100)}


def one(name: str, dsl: str, tmp: Path) -> dict:
    res = CL.render("A10", dsl, "diag-" + name, kind="probe",
                    purpose="诊断 ③ 卡内 (179,255,255)：确认罩色解析与 BackdropFilter 是否真正模糊",
                    timeout=120, attempts=4, dsl_name="diag-" + name + ".snapshot")
    log = res["log"] or {}
    info = {"status": res["status"], "elapsed_ms": log.get("elapsed_ms"),
            "error": log.get("error"), "request_id": res["request_id"]}
    if res["status"] == 200 and res["body"]:
        p = tmp / "preview" / ("diag-" + name + ".png")
        p.write_bytes(res["body"])
        im = Image.open(p).convert("RGBA")
        assert im.size == (CW, CH), im.size
        info["pixels"] = {k: list(im.getpixel(v)) for k, v in PTS.items()}
    return info


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import concurrent.futures
    tmp = S.task_dirs("A10")[1]
    (tmp / "preview").mkdir(parents=True, exist_ok=True)
    names = list(VARIANTS)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(names)) as ex:
        rec = dict(zip(names,
                       ex.map(lambda n: one(n, VARIANTS[n], tmp), names)))
    for name in names:
        info = rec[name]
        print("=" * 72)
        print(name, "status", info["status"], info.get("elapsed_ms"), "ms")
        if "pixels" in info:
            for k, v in info["pixels"].items():
                print("   %-24s %s" % (k, v))
        else:
            print("   ERROR", (info.get("error") or "")[:200])

    print("=" * 72)
    print("判读：veil-wrong 卡内应为不透明青 (179,255,255)；veil-right 卡内深条处应≈(223,224,227)、"
          "间隙处应≈(250,250,250)。veil-right-blur 与 veil-right-subtree 应在深条/间隙之间"
          "出现可辨的明暗差（模糊后差值缩小但不消失），且卡外保持不变。")
    (tmp / "diag-results.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
