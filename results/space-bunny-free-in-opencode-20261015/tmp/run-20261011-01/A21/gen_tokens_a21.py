#!/usr/bin/env python
# A21：由 build_a21 的真实几何生成 design-tokens.json 与 content-map.json。
# 启动基准：总任务根 (suite_root)。用法：python gen_tokens_a21.py <round> <version>
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
BASE = ROOT / "tmp/run-20261011-01/A21"
sys.path.insert(0, str(BASE))
import build_a21 as B  # noqa: E402

# 稳定文案 ID → (需求来源, 第1轮原文)
COPY = [
    ("brand", "TASK.md「叠光 Layerlight」活动", "叠光 Layerlight"),
    ("title-1", "TASK.md 必须包含「让复杂信息变得清晰」", "让复杂信息变得清晰"),
    ("date", "TASK.md 必须包含「2026.11.07 19:30」", "2026.11.07 19:30"),
    ("badge", "TASK.md 必须包含「ONLINE LAUNCH」", "ONLINE LAUNCH"),
    ("speakers", "TASK.md 必须包含「讲者：林川 / 苏言」", "讲者：林川 / 苏言"),
    ("url", "TASK.md 必须包含「layerlight.example.org」", "layerlight.example.org"),
]

BRAND = [
    dict(id="B1", name="层条·上", component="圆角横条",
         params={"width": B.BAR_W, "height": B.BAR_H, "border_radius": B.BAR_H / 2,
                 "offset": [B.BAR_DX[0], B.BAR_DY[0]], "unit": "s（构件缩放因子）"},
         role="品牌三层的最上一层，颜色最深"),
    dict(id="B2", name="层条·中", component="圆角横条",
         params={"width": B.BAR_W, "height": B.BAR_H, "border_radius": B.BAR_H / 2,
                 "offset": [B.BAR_DX[1], B.BAR_DY[1]], "unit": "s（构件缩放因子）"},
         role="承载光斑的中层"),
    dict(id="B3", name="层条·下", component="圆角横条",
         params={"width": B.BAR_W, "height": B.BAR_H, "border_radius": B.BAR_H / 2,
                 "offset": [B.BAR_DX[2], B.BAR_DY[2]], "unit": "s（构件缩放因子）"},
         role="向右错位最远的一层，形成叠光的方向感"),
    dict(id="B4", name="光斑", component="圆盘",
         params={"diameter": B.DISC_D,
                 "center": ["层条·中右端点 x", "层条·中垂直中心 y"],
                 "unit": "s（构件缩放因子）"},
         role="品牌识别点，颜色为主题强调色"),
]


def typography(rd):
    C = B.CONTENT[rd]
    return {
        "families": {
            "display": B.FONT_SEMI, "body": B.FONT_MED, "mono": B.FONT_MONO,
            "note": "Inter 与 Noto Sans CJK SC 组合；中日韩字符由 Noto Sans CJK SC 承担，"
                    "拉丁字符由 Inter 承担（run 级字体查询确认过这两个族都可用）。",
        },
        "scale_px": {
            "title": C["title_size"], "date": 36 if rd != 2 or True else 36,
            "brand": 32, "badge": 30, "speakers": 30, "url": 28,
            "sponsor": 26, "attend": 26, "english": 26,
        },
        "line_height": {"title": 1.34, "body": 1.3, "note": "标题 1.34，正文 1.3"},
        "letter_spacing_px": {"badge": 6, "date": 2, "url": 1, "english": 2, "brand": 1},
        "rules": {
            "title_min_px": 56 if rd == 1 else 48,
            "body_min_px": 24,
            "title_max_lines": 3,
        },
        "hierarchy_note": "竖版与横版共用同一套字号与字族，仅空间位置不同——"
                          "这是题面「两图同一字体层级」的实现方式。",
    }


CHANGES = {
    1: [],
    2: [
        dict(area="文案 · 主标题", change="「让复杂信息变得清晰」→「当所有信息都想成为标题："
                                          "让复杂信息变得清晰的结构化方法」，按语义断为两行",
             reason="round-02.md 要求替换主标题；不依赖服务端自动折行，改由语义断点控制行数",
             constraint_check="行数 2 ≤ 3；字号 52 ≥ 48；未使用任何横向变形压窄字形"),
        dict(area="文案 · 新增", change="新增赞助方「Northstar Research / 云构工具」与"
                                       "「免费参加 · 无需报名」两行",
             reason="round-02.md 明确要求", constraint_check="竖版排在讲者与网址之间；"
                                                            "横版排在网址之前，两版阅读次序一致"),
        dict(area="版式 · 竖版", change="主构件缩放 1.02 → 0.96，标题起点 560 → 556，"
                                       "段间距 16 → 12、标题后间距 20 → 14",
             reason="文字段从 6 段增到 9 段，需要让出垂直空间而不侵占底部扩展带",
             constraint_check="底部扩展带仍为 232px；文字框两两不相交（gen_checks 断言）"),
        dict(area="版式 · 横版", change="左栏宽 780 → 800；主构件按「不越过 48px 安全边」"
                                       "反推缩放（1.00 → 0.987）并右置到中心 1167",
             reason="第 2 轮标题第二行 14 字 × 52px = 728px，780 栏宽只剩 52px 余量；"
                    "800 可留 70px",
             constraint_check="构件外接框 942…1392，离右安全边 48px；与左栏文字盒不相交"),
        dict(area="未改动", change="底色、主色、三层构件色、光斑色、字族、字号层级、"
                                   "4 个品牌构件的形态与比例、日期/讲者/ONLINE LAUNCH/网址",
             reason="round-02.md 要求主色与品牌构件形态不变，"
                    "并保留日期、讲者、ONLINE LAUNCH、网址",
             constraint_check="逐项与 round-01/design-tokens.json 比对一致"),
    ],
    3: [
        dict(area="主题 · 背景", change="#0B1020 → #F8FAFC（深色 → 浅色）",
             reason="round-03.md 要求改浅色主题", constraint_check="全部正文对比度 ≥4.5，见 contrast-audit.json"),
        dict(area="品牌构件配色", change="三层 #4338CA/#3730A3/#312E81 → #6366F1/#4F46E5/#4338CA；"
                                          "光斑 #FBBF24 → #D97706",
             reason="深色底上的低明度构件在浅底上不可见，需整体提亮；色相仍为同一靛蓝/琥珀系",
             constraint_check="**仅改配色**：B1–B4 的形状、尺寸、偏移、圆角比例逐项未变"),
        dict(area="文字色", change="primary #F8FAFC → #1E1B4B；secondary #A5B4FC → #3730A3；"
                                   "accent #FBBF24 → #B45309；rule #312E81 → #C7D2FE；"
                                   "badge 描边 #4F46E5 → #1E1B4B",
             reason="浅底上必须换成深色文字才能满足 4.5:1",
             constraint_check="逐段按 sRGB 线性化公式计算，最小值见 contrast-audit.json"),
        dict(area="文案 · 新增", change="网址上方新增英语短句「Clarity through structure」",
             reason="round-03.md 明确要求", constraint_check="26px ≥ 24；排在网址正上方"),
        dict(area="未改动", change="第 2 轮全部文案（长标题两行、日期、讲者、ONLINE LAUNCH、"
                                   "网址、赞助方、参加方式）与两尺寸构图关系",
             reason="round-03.md 要求保留", constraint_check="赞助方仍在图中，未因换主题消失"),
    ],
}


def main() -> None:
    rd = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    ver = sys.argv[2] if len(sys.argv) > 2 else "v2"
    T = B.THEMES[rd]
    drafts = BASE / f"drafts/round-{rd:02d}"
    drafts.mkdir(parents=True, exist_ok=True)

    data = json.loads((drafts / f"texts-{ver}.json").read_text(encoding="utf-8"))
    tokens = {
        "schema_version": 1, "task_id": "A21", "round": rd, "path_base": "output_dir",
        "colors": {
            "background": {"value": T["bg"], "role": "画布底色", "theme": "深色" if rd != 3 else "浅色"},
            "layer_top": {"value": T["layers"][0], "role": "品牌构件 B1", "theme": "深色" if rd != 3 else "浅色"},
            "layer_mid": {"value": T["layers"][1], "role": "品牌构件 B2", "theme": "深色" if rd != 3 else "浅色"},
            "layer_low": {"value": T["layers"][2], "role": "品牌构件 B3", "theme": "深色" if rd != 3 else "浅色"},
            "light_spot": {"value": T["disc"], "role": "品牌构件 B4", "theme": "深色" if rd != 3 else "浅色"},
            "text_primary": {"value": T["primary"], "role": "主标题 / 网址 / 字标", "theme": "深色" if rd != 3 else "浅色"},
            "text_secondary": {"value": T["secondary"], "role": "讲者 / 赞助方", "theme": "深色" if rd != 3 else "浅色"},
            "accent": {"value": T["accent"], "role": "日期 / 参加方式 / 光斑", "theme": "深色" if rd != 3 else "浅色"},
            "rule": {"value": T["rule"], "role": "扩展区分隔线", "theme": "深色" if rd != 3 else "浅色"},
            "badge_border": {"value": T["badge_bd"], "role": "ONLINE LAUNCH 徽标描边", "theme": "深色" if rd != 3 else "浅色"},
        },
        "primary_color": {
            "value": T["layers"][1],
            "note": "两尺寸与三轮共用的主色；第 3 轮改为浅色主题时仅调整明度层级，"
                    "色相仍为同一靛蓝系。",
        },
        "typography": typography(rd),
        "brand_geometry": [dict(b, inherited_from=None, allowed_change="仅允许整体缩放与平移，形态不变")
                           for b in BRAND],
        "brand_geometry_inheritance": (
            "首轮定义" if rd == 1 else
            f"继承自 round-{rd-1:02d}，形态、尺寸、偏移、圆角比例逐项未变；"
            "本轮只做了缩放、平移（第 2 轮）与配色（第 3 轮），"
            "符合 round-02/03 的「允许移动和缩放装饰、构件形态不变」。"),
        "brand_mark_bbox_unit_s": {"width": B.MARK_W, "height": B.MARK_H,
                                   "note": "构件外接框以缩放因子 s 为单位；居中时用 "
                                           "x0 = cx − 456·s/2、y0 = cy − 180·s/2。"},
        "composition": {
            "portrait": "1080×1350 纵向堆叠：预留带 → 品牌行 → 大构件 → 标题 → 日期 → "
                        "徽标 → 讲者 →（赞助/参加/英文）→ 网址 → 预留带",
            "wide": "1440×810 左右分栏：左栏文字竖向序列，右侧大构件；上下预留带更窄",
            "note": "两图分别构图，不是同一张缩放；共用同一套令牌与品牌构件。",
        },
        "changes": CHANGES[rd],
        "changes_note": ("首轮无上轮可比版本，changes 为空数组（题面规定首轮为空）。"
                         if rd == 1 else f"与 round-{rd-1:02d} 的实际变化逐条列出，"
                                          "并附约束核对；未改动项同样记录，便于回归对照。"),
        "inherited_from": (None if rd == 1 else f"round-{rd-1:02d}"),
    }

    src = {c[0]: c for c in COPY}
    entries = []
    for key in ("brand", "title-1", "title-2", "date", "badge", "speakers",
                "sponsor", "attend", "english", "url"):
        box = {}
        for which in ("portrait", "wide"):
            hit = [t for t in data[which]["texts"] if t[0] == key]
            box[which] = None
            for tid, text, x, y, w, h, size, color, align in hit:
                box[which] = {"text": text, "box": [round(x, 2), round(y, 2),
                                                    round(x + w, 2), round(y + h, 2)],
                              "font_size_px": size, "lines": 1, "color": color,
                              "align": align}
        actual = next((v["text"] for v in box.values() if v), None)
        if actual is None:
            continue
        if key in ("title-2", "sponsor", "attend", "english"):
            state = "新增"
            req = ("round-02.md：主标题替换为长标题后拆两行" if key == "title-2"
                   else "round-02.md：新增赞助方与参加方式" if key in ("sponsor", "attend")
                   else "round-03.md：网址上方新增英语短句")
        elif rd == 1 or key in ("date", "badge", "speakers", "url", "brand"):
            state = "继承"
            req = src.get(key, ("", ""))[1] or "round-02/03 要求保留"
        else:
            state = "替换"
            req = src.get(key, ("", ""))[1]
        entries.append({
            "copy_id": key, "original_text": src.get(key, (key, ""))[1],
            "actual_text": actual, "state": state, "requirement_source": req,
            "boxes": box,
        })

    cmap = {
        "schema_version": 1, "task_id": "A21", "round": rd, "path_base": "output_dir",
        "entries": entries,
        "checks": [],
    }
    (drafts / f"design-tokens-{ver}-raw.json").write_text(
        json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")
    (drafts / f"content-map-{ver}-raw.json").write_text(
        json.dumps(cmap, ensure_ascii=False, indent=2), encoding="utf-8")
    print("tokens + content-map written;", len(entries), "entries")


if __name__ == "__main__":
    main()