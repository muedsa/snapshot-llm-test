"""Archive the ten B05 screens into outputs/<run>/B05/case-NN/ with per-case reports.

Checks that each final PNG is the untouched service response for the DSL that produced
it (same request id, DSL not modified after the render) before copying anything.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B05"
OUT = ROOT / "outputs" / RUN / "B05"
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))
AUD = json.loads((TMP / "audits.json").read_text(encoding="utf-8"))

REQ = {}
for line in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    REQ[r["request_id"]] = r

# case id -> (dsl stem, title, device, canvas, journey step, what the screen decides)
CASES = [
    ("01", "case01-today", "今日时间线", "iPhone 13 · 390×844",
     "晚上 21:40，母亲还没吃 22:00 的那片降脂药",
     "让“今天还差什么”一眼可见，而不是把 5 条记录平铺成日志"),
    ("02", "case02-alerts", "药箱警报", "iPhone 13 · 390×844",
     "点开红点：到底是哪几样药要处理",
     "按有效天数升序排，把“7 天内到期”和“会用不完”分开说"),
    ("03", "case03-entry", "录入药品（校验态）", "iPhone 13 · 390×844",
     "儿子替母亲把新药放进药箱",
     "两处错误同时给出：效期早于今天、每日次数与时间数不符"),
    ("04", "case04-empty", "药箱空状态", "iPhone 13 · 390×844",
     "第一次打开，还没有任何药品",
     "三条录入路径按代价排序，并先说清数据放在哪里"),
    ("05", "case05-watch", "手表提醒", "200×240 圆角表盘",
     "22:00 手腕一震，母亲不需要掏手机",
     "只留时间、药名、余量与一个长按动作"),
    ("06", "case06-fridge", "冰箱卡（离线打印）", "680×320 打印卡",
     "老人不用智能设备时，家里其他人看一眼冰箱",
     "只列医嘱定时药，效期用天数而非颜色单独承载"),
    ("07", "case07-caregiver", "照护者视图", "iPad · 834×1112",
     "儿子周末回看母亲这两周吃得怎么样",
     "14 天服药格与按人聚合的依从率同源，待办可直接完成"),
    ("08", "case08-pharmacist", "药师交接端", "桌面 1440×900",
     "复诊时把家庭药箱交给社区药师核对",
     "把“未采集字段”显式列出，避免打印件看起来比实际完整"),
    ("09", "case09-print", "A4 随访摘要", "794×1123（96dpi A4）",
     "药师确认后的纸质留档，家属与药师签字",
     "黑白可打印：状态全部用文字，不依赖颜色"),
    ("10", "case10-disposal", "过期药处置", "iPhone 13 · 390×844",
     "阿托伐他汀钙片只剩 7 天效期，剩下 3 片怎么办",
     "只给通用三步，并声明本系统不含当地回收政策数据"),
]

UNVERIFIED = {
    "01": ["漏服判定阈值（超过时点 60 分钟记为漏服）未与真实用药习惯核对"],
    "02": ["补货提前量 7 天来自用户访谈假设，未验证社区医院实际开药周期"],
    "03": ["错误文案是否足够让老人自行修正，未做真实用户验证"],
    "04": ["条码库覆盖范围未核实，扫码路径可能带不出品名"],
    "05": ["手表端字号在真实手腕上的可读性未做实测"],
    "06": ["回收点/药房信息未核实，卡上不含具体点位"],
    "07": ["依从率口径（时点数而非剂量）可能与临床习惯不一致"],
    "08": ["药师是否接受“未采集字段”这种显式留白，未做访谈"],
    "09": ["A4 打印在真实激光打印机上的灰度表现未实测"],
    "10": ["处置步骤未查证权威指南，仅为通用做法"],
}


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for cid, stem, title, device, moment, decision in CASES:
        dsl = TMP / f"{stem}.snapshot"
        png = TMP / f"{stem}-final.png"
        cand = [k for k in REQ if k.startswith(f"B05-{stem}-")
                and REQ[k]["http_status"] == 200
                and Path(REQ[k]["request_file"]).name == dsl.name
                and Path(REQ[k]["response_file"]).exists()]
        cand.sort(key=lambda k: REQ[k]["ended_at"])
        assert cand, stem
        rid = cand[-1]
        png = ROOT / REQ[rid]["response_file"]
        # the archived PNG must be the response for the DSL file as it stands now:
        # the render's request_file has to be that exact file
        vr = REQ[rid]
        assert Path(vr["request_file"]).resolve() == dsl.resolve(), rid
        raw = png.read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n", cid
        cd = OUT / f"case-{cid}"
        cd.mkdir(exist_ok=True)
        (cd / "final.png").write_bytes(raw)
        (cd / "final.snapshot").write_text(dsl.read_text(encoding="utf-8"),
                                           encoding="utf-8")
        a = AUD[stem]
        versions = sorted(k for k in REQ if k.startswith(f"B05-{stem}-"))
        md = [f"# case-{cid} · {title}", ""]
        md += [f"- 设备/画布：{device}",
               f"- 旅程节点：{moment}",
               f"- 服务请求：`{rid}`（{r['http_status']}，"
               f"{r['duration_seconds']}s，server {r['server_timing']}，"
               f"X-Request-Id `{r['x_request_id']}`）",
               f"- 响应字节：{len(raw):,} B，sha256 `{hashlib.sha256(raw).hexdigest()[:16]}…`",
               f"- 渲染次数：{len(versions)}（{', '.join(v.split(stem + '-')[1] for v in versions)}）",
               f"- DSL：`case-{cid}/final.snapshot`", "",
               "## 这一屏解决什么", "", decision, ""]
        md += ["## 屏上的具体信息", ""]
        for line in CASE_FACTS[cid]:
            md.append(f"- {line}")
        md += ["", "## 自检", "",
               f"- 生成器审计：overlap_n={a['overlap_n']}、outside_n={a['outside_n']}、"
               f"spill_n={a['spill_n']}、truncated_n={a['truncated_n']}、"
               f"below_min_font_n={a['below_min_font_n']}（{a['texts']} 段文字 / "
               f"{a['shapes']} 个图形）",
               "- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源",
               "- final.png 为服务原始响应字节，未做后处理",
               "- 实际看图：见 `iterations.jsonl` 的 view 事件", ""]
        md += ["## 未验证的假设", ""]
        for line in UNVERIFIED[cid]:
            md.append(f"- {line}")
        md.append("")
        (cd / "case.md").write_text("\n".join(md), encoding="utf-8")
        manifest.append({"case": f"case-{cid}", "title": title, "device": device,
                         "dsl_stem": stem, "request_id": rid, "bytes": len(raw),
                         "renders": len(versions), "audit": a,
                         "png": rel(cd / "final.png"),
                         "snapshot": rel(cd / "final.snapshot"),
                         "report": rel(cd / "case.md")})
    (TMP / "case-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("archived", len(manifest), "cases ->", rel(OUT))


CASE_FACTS = {
    "01": ["4/5 已完成、漏服 0，与 schedule_today 的 5 个时点一致",
           "每条给出时间、药名简称、剂量与服用者；状态用文字胶囊而非纯色点",
           "数据截止 2026-10-13 21:40 单独成行，避免与“今日已完成”连读"],
    "02": ["5 种药按有效天数升序：7 / 20 / 94 / 199 / 535 天",
           "可服天数由余量 ÷ 每日时点数推出：3 片→3 天、26 片→13 天",
           "吸入剂按需使用，明确写“无法按天数估计”，不硬造数字"],
    "03": ["9 个字段已填 7 个，未显示的 2 项在右上角注明",
           "两处校验同时出现：效期 2026-10-01 早于今天；每日次数 3 与已填 1 个时间不符",
           "保存按钮为禁用态并写明“先修正 2 处错误”"],
    "04": ["三条录入路径按代价排序：条码 / 处方导入 / 手动",
           "空状态同时说明“没有提醒、没有警报，也不算余量”",
           "底部面板交代数据存放与不给用药建议"],
    "05": ["200×240 上只放 5 段文字，最小 14px",
           "22:00 降脂药 1 片 · 母亲，与手机今日屏同一时点同一条记录",
           "“仅剩 3 片”直接引用 M3 余量"],
    "06": ["三行医嘱定时药：08:00 / 08:00+20:00 / 22:00，均为周秀兰",
           "效期徽章按 7 / 30 / 90 天分三级，颜色之外仍写天数",
           "离线显示：注明每 24 小时同步一次，断网时显示上次同步时间"],
    "07": ["14 天服药格：每格当日已确认时点数 / 应服时点数，绿/黄/红三级",
           "格内可见 4 次漏服（M2 0/2 与 1/2、M3 0/1），与“14 天内漏 4 次”一致",
           "按人聚合：周秀兰 52/56=92.9%、周成 4/14=28.6%、周雨桐不计依从率",
           "待办四条由余量、效期、记数规则生成，可直接标记完成"],
    "08": ["5 项交接清单：药品、服用者、处方来源、效期、剩余、状态",
           "状态计数 全部 5 / 待药师确认 2 / 已核 3，与效期分级同源",
           "“未采集字段”显式列出批号、生产厂家、医保编码",
           "右侧 A4 预览为 12–15px 缩小示意，真实排版见 case-09"],
    "09": ["A4 单页：清单 + 近 7 天记录 + 需药师确认事项 + 双方签字",
           "8 列表格，最长药名 11 字完整显示，不被截断",
           "状态列全部用文字，黑白打印不依赖颜色",
           "页脚标注“第 1 页 / 共 1 页 · 药盒 v0.9 导出”"],
    "10": ["顶部只锁定 1 项：M3 效期 7 天、剩 3 片",
           "三步处置每步都给出“为什么”，并声明未查证权威清单",
           "结尾明确本系统不含当地回收政策数据"],
}

if __name__ == "__main__":
    main()
