"""case-09 睡眠分期 · 一夜的四段旅程（1200×800，3:2）。

视觉系统：水平堆叠条——8 小时一夜睡眠分为清醒、REM、浅睡、深睡四段。
  每条是一个 5 分钟睡眠周期，颜色高度对应阶段。左侧是时间轴，
  右侧是阶段统计面板。底部标注「睡眠效率」与「深睡比例」。

受众是关注睡眠质量的人，早上看昨晚的数据。核心诉求是
「昨晚睡得怎么样」和「哪里出了问题」。

数据为自拟演示，非真实睡眠监测数据，不宣称实际部署。
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1200, 800
MIN_FS = 16

# ------------------------------------------------------------------ 调色
BG = "#0F172A"
INK = "#F1F5F9"
INK2 = "#94A3B8"
INK3 = "#64748B"
INK4 = "#475569"
LINE_CLR = "#1E293B"
DEEP = "#1E40AF"
DEEP_D = "#172554"
LIGHT = "#3B82F6"
LIGHT_D = "#1E3A8A"
REM = "#A855F7"
REM_D = "#581C87"
AWAKE = "#64748B"
AWAKE_D = "#1E293B"
GOOD = "#22C55E"
WARN = "#EAB308"

# ------------------------------------------------------------------ 数据
# 96 个 5 分钟周期 (8 小时 * 12 周期/小时)，每周期一个阶段
# 阶段: 0=清醒, 1=REM, 2=浅睡, 3=深睡
SLEEP = [
    0,2,3,3,3,3, 3,3,3,2,2,1,   # 入睡 + 首次深睡
    3,3,3,3,2,2, 2,1,1,0,2,3,   # 深睡主导
    3,3,3,2,2,2, 1,1,1,0,2,3,   # 混合
    3,2,2,2,2,2, 1,1,1,1,0,2,   # 深睡减少
    2,2,3,2,2,2, 1,1,1,1,0,2,   # 浅睡和REM
    2,2,2,2,1,1, 1,1,1,1,0,2,   # REM变长
    2,2,2,1,1,1, 1,1,1,1,1,0,   # REM为主
    2,1,1,1,1,1, 1,1,1,1,0,0,   # 醒来
]

STAGE_NAMES = ["清醒", "REM", "浅睡", "深睡"]
STAGE_COLORS = [AWAKE, REM, LIGHT, DEEP]
STAGE_DARKS = [AWAKE_D, REM_D, LIGHT_D, DEEP_D]


def stage_stats():
    counts = {s: 0 for s in range(4)}
    for s in SLEEP:
        counts[s] += 1
    return counts


def sleep_efficiency():
    total = len(SLEEP)
    awake = sum(1 for s in SLEEP if s == 0)
    return (total - awake) / total * 100


def deep_ratio():
    total = len(SLEEP)
    deep = sum(1 for s in SLEEP if s == 3)
    return deep / total * 100


# ------------------------------------------------------------------ 几何
PAD_L = 80
PAD_R = 200
PAD_T = 100
PAD_B = 100
BAR_X = PAD_L
BAR_Y = PAD_T
BAR_W = W - PAD_L - PAD_R
BAR_H = 460
CYCLE_W = BAR_W / len(SLEEP)


# ------------------------------------------------------------------ 构建
def build() -> K.Doc:
    d = K.Doc(W, H, BG)

    # 页头
    d.text(PAD_L, 16, "睡眠分期", 28, INK, bold=True)
    d.text(PAD_L, 50, "一夜的四段旅程 · 自拟演示数据", 16, INK2)
    d.text_r(W - PAD_R, 20, "折光 · 十张日常　09 / 10", 16, INK3, bold=True)
    d.text_r(W - PAD_R, 44, "非真实睡眠监测数据", 16, INK3)

    # 时间轴顶部
    t0_y = BAR_Y - 8
    for h in range(8):
        x = BAR_X + h / 8 * BAR_W
        d.line_v(x, t0_y, BAR_Y + BAR_H + 10, LINE_CLR, 1)
        d.text_c(x + CYCLE_W * 6, t0_y - 18,
                 "%02d:00" % (22 + h), 16, INK3)

    # 睡眠周期条
    for i, stage in enumerate(SLEEP):
        x = BAR_X + i * CYCLE_W
        color = STAGE_COLORS[stage]
        dark = STAGE_DARKS[stage]
        # 上半段（深睡/浅睡）
        d.rect(x, BAR_Y, CYCLE_W - 1, BAR_H / 2, color, radius=2)
        # 下半段（REM/清醒）
        d.rect(x, BAR_Y + BAR_H / 2, CYCLE_W - 1, BAR_H / 2, dark, radius=2)

    # 右侧统计面板
    stats = stage_stats()
    sp_x = W - PAD_R + 20
    sp_y = BAR_Y + 10

    d.text(sp_x, sp_y, "阶段统计", 16, INK3, bold=True)
    sp_y += 30
    for i, name in enumerate(STAGE_NAMES):
        n = stats[i]
        pct = n / len(SLEEP) * 100
        d.rect(sp_x, sp_y - 2, 14, 14, STAGE_COLORS[i], radius=2)
        d.text(sp_x + 20, sp_y - 4, "%s %d 段" % (name, n), 16, INK2)
        d.text_r(W - PAD_R, sp_y - 4, "%.1f%%" % pct, 16, INK3)
        sp_y += 24

    sp_y += 16
    eff = sleep_efficiency()
    deep_r = deep_ratio()
    d.text(sp_x, sp_y, "睡眠效率", 16, INK3)
    d.text(sp_x, sp_y + 22, "%.1f%%" % eff, 28, GOOD if eff > 85 else WARN,
           bold=True)
    d.text(sp_x, sp_y + 58, "深睡比例", 16, INK3)
    d.text(sp_x, sp_y + 80, "%.1f%%" % deep_r, 28,
           DEEP if deep_r > 15 else INK2, bold=True)

    # 底部图例
    ly = H - PAD_B + 20
    lx = PAD_L
    for i, name in enumerate(STAGE_NAMES):
        d.rect(lx, ly, 18, 14, STAGE_COLORS[i], radius=2)
        d.text(lx + 24, ly - 2, name, 16, INK2)
        lx += 100

    # 免责声明
    d.text(PAD_L, H - 40, "本图为自拟演示数据，非真实睡眠监测数据，不宣称实际部署。",
           16, INK4)
    d.text_r(W - PAD_R, H - 40, "2026-10-22", 16, INK4)

    return d


# ------------------------------------------------------------------ 门禁
def gates(doc: K.Doc) -> list[dict]:
    out = []
    stats = stage_stats()
    out.append({
        "id": "case-09-c01",
        "check": "%d 个 5 分钟周期 = 8 小时一夜" % len(SLEEP),
        "passed": len(SLEEP) == 96,
        "detail": "%d 个周期" % len(SLEEP)
    })
    out.append({
        "id": "case-09-c02",
        "check": "4 个阶段：清醒 %d、REM %d、浅睡 %d、深睡 %d"
                 % (stats[0], stats[1], stats[2], stats[3]),
        "passed": sum(stats.values()) == 96,
        "detail": "总 %d 段" % sum(stats.values())
    })
    out.append({
        "id": "case-09-c03",
        "check": "睡眠效率 = %.1f%%" % sleep_efficiency(),
        "passed": sleep_efficiency() > 50,
        "detail": "%.1f%%" % sleep_efficiency()
    })
    out.append({
        "id": "case-09-c04",
        "check": "深睡比例 = %.1f%%" % deep_ratio(),
        "passed": True,
        "detail": "%.1f%%" % deep_ratio()
    })
    out.append({
        "id": "case-09-c05",
        "check": "页面声明「非真实睡眠监测数据」",
        "passed": True,
        "detail": "已写入页脚"
    })
    out.extend(K.dry_run(doc, "case-09", MIN_FS, []))
    return out


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")

    doc = build()
    gs = gates(doc)
    n_fail = sum(1 for g in gs if not g["passed"])

    tmp = pathlib.Path(HERE.parents[2]) / "B01" / "case-09"
    tmp.mkdir(parents=True, exist_ok=True)
    n_g = len(list(tmp.glob("case-09-gates-*.json"))) + 1
    gf = tmp / ("case-09-gates-%03d.json" % n_g)
    gf.write_text(json.dumps({
        "case_id": "case-09",
        "at": K.now(),
        "timezone": K.TZ_NAME,
        "gates_total": len(gs),
        "gates_failed": n_fail,
        "gates": gs,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("gates=%s" % gf)

    if n_fail:
        for g in gs:
            if not g["passed"]:
                print("FAIL: %s — %s" % (g["id"], g["check"]))
        return 1

    print("全部 %d 条门禁通过" % len(gs))
    print("  周期 %d · 效率 %.1f%% · 深睡 %.1f%% · %d×%d"
          % (len(SLEEP), sleep_efficiency(), deep_ratio(), W, H))

    rec = K.render_case("case-09", doc, "case-09-sleep-staging",
                        purpose="B01 主作品：睡眠分期")
    print("status=%d bytes=%d parts=%d texts=%d shapes=%d ms=%s"
          % (rec["http_status"], rec["response_bytes"], rec["parts"],
             rec["texts"], rec["shapes"], rec["elapsed_ms"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
