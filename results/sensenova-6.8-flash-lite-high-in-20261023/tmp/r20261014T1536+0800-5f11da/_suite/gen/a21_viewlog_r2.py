"""把 round-02 的看图事件追加进 viewing-evidence.json（不覆盖 round 1）。

时间说明：本轮渲染在 21:46:31 交付。压缩前的 4 次打开发生在交付后不久，
只能给到分钟级估计；压缩后的 10 次按当前会话墙钟记录到分钟。
不做更精细的补记。
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
VE = SUITE_ROOT / "tmp" / RUN_ID / "A21" / "viewing-evidence.json"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A21" / "round-02"
PREV = SUITE_ROOT / "tmp" / RUN_ID / "A21" / "preview" / "round-02"

PRE = "minute-level estimate（压缩前的会话中实际打开）"
POST = "minute-level（本次会话）"
TZ = dt.timezone(dt.timedelta(hours=8))


def ts(h, m):
    return dt.datetime(2026, 10, 19, h, m, tzinfo=TZ).isoformat(timespec="minutes")


def crop(view, art, crop_box, scale, t, obs, prec=POST):
    return {
        "event_id": None, "round": 2, "phase": "delivery", "artifact": art,
        "image": {"path": "tmp/%s/A21/preview/round-02/%s" % (RUN_ID, view),
                  "scale": scale,
                  "note": "裁切 %s，源图 sha256 与 round-02 交付 PNG 一致" % crop_box},
        "view_type": "crop-zoomed", "viewed_at": t, "viewed_at_precision": prec,
        "observed": obs,
    }


def whole(art, t, obs, phase="delivery", prec=POST):
    return {
        "event_id": None, "round": 2, "phase": phase, "artifact": art,
        "image": {"path": "outputs/%s/A21/round-02/%s.png" % (RUN_ID, art)},
        "view_type": "whole-1to1", "viewed_at": t,
        "viewed_at_precision": prec, "observed": obs,
    }


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    doc = json.loads(VE.read_text(encoding="utf-8"))
    prev_ids = [e["event_id"]
                for blk in doc["rounds"].values()
                for e in blk["image_open_events"]]
    nxt = max(int(i.split("-")[-1]) for i in prev_ids) + 1

    events = [
        whole("launch-portrait", ts(21, 48),
              "整图 1:1 首次查看。三行长标题 66px 字重足够、行距不挤不松；"
              "眉标带橙色竖条；蓝色强调条唯一且与标题、日期都有间距；"
              "发光球移到右中偏下后与三行标题的墨迹之间留有明显深色间隙；"
              "底部新增赞助方与报名状态牌两行，未压到任何元素",
              prec=PRE),
        whole("launch-wide", ts(21, 48),
              "整图 1:1 首次查看。左栏品牌行 + 眉标 + 两行长标题（第 2 行 15 字）"
              "依次向下，右栏发光球大图占整栏，左右分栏互不侵占；"
              "底部 5 行信息栈（日期/讲者/网址牌/赞助方/报名状态牌）"
              "比竖版更紧但行距仍清楚",
              prec=PRE),
        crop("launch-wide-title.png", "launch-wide", "[0,128,960,362]", 1.5,
             ts(21, 49),
             "1.5x 放大：眉标 ONLINE LAUNCH 字距展开、竖条完整；两行标题 52px "
             "笔画未变形、未出现横向压窄；第 2 行 15 字未折行，右缘距发光球辉光"
             "仍有深色缓冲", prec=PRE),
        crop("launch-portrait-kicker-title.png", "launch-portrait",
             "[0,258,1080,700]", 1.3, ts(21, 50),
             "1.3x 放大：三行标题 66px 逐行左对齐、行距一致；首行冒号收在行尾"
             "未折行；第三行「的结构化方法」下方留白足够，蓝色强调条位置清楚；"
             "发光球辉光只从右下角进入，不触任何字", prec=PRE),
        crop("launch-portrait-footer.png", "launch-portrait", "[0,1030,1080,1240]",
             1.6, ts(21, 57),
             "1.6x 放大（新增窗口，专查两条新增信息）：赞助方 30px 灰色一行排完，"
             "英文与中文之间斜杠分隔清楚；报名状态牌为主色描边、文字白色居中，"
             "牌内左右各有明显余量；牌体圆角收口完整"),
        crop("launch-portrait-info.png", "launch-portrait", "[0,640,1080,1010]",
             1.4, ts(21, 58),
             "1.4x 放大：日期橙色加粗最醒目、讲者灰色次之、网址牌收尾，层级未倒挂；"
             "网址牌由第一轮 632 宽收窄到 560 宽后，牌右缘与发光球外环之间留出"
             "清晰深色间隙，不再粘连"),
        crop("launch-portrait-orb.png", "launch-portrait", "[540,560,1080,1060]",
             1.5, ts(21, 58),
             "1.5x 放大：球体半径由 130 增到 165 后球感更足，三条光带自上而下"
             "递减宽度与亮度、圆头收口；外环细线完整；左下角可见报名状态牌边缘，"
             "与球体无重叠"),
        crop("launch-wide-footer.png", "launch-wide", "[0,600,960,730]", 2.0,
             ts(21, 59),
             "2.0x 放大：赞助方 28px 一行排完；报名状态牌与上方网址牌同属牌子族"
             "但边框色不同（主色青 vs 中性蓝），语义区分一眼可辨"),
        crop("launch-wide-info.png", "launch-wide", "[0,380,960,592]", 1.9,
             ts(21, 59),
             "1.9x 放大：横版由第一轮的横排改为纯竖排后，日期→讲者→网址牌三行"
             "对齐左基线，圆点垂直居中于牌；竖分隔线已随横排删除，版式更干净"),
        crop("launch-portrait-header.png", "launch-portrait", "[0,80,1080,260]",
             1.6, ts(22, 0),
             "1.6x 放大：主标记 76→72 后与字标基线仍对齐，中英分色与间距规则未变；"
             "右上线叠层水印缩到 288 并外移后与标题首行不相交"),
        crop("launch-wide-orb.png", "launch-wide", "[820,180,1440,620]", 1.4,
             ts(22, 0),
             "1.4x 放大：球缩小到半径 175 并右移后右栏更居中；裁切左缘可见标题第 2 行"
             "末字「法」，其墨迹止于球辉光左缘之前，无覆盖"),
        crop("launch-wide-header.png", "launch-wide", "[0,40,960,210]", 1.8,
             ts(22, 6),
             "1.8x 放大：主标记 52、字标 30，与竖版同一套间距规则；眉标竖条与"
             "字距完整"),
        whole("launch-portrait", ts(22, 8),
              "归档前复查通过：与 ev-a21-015 观察一致，交付字节未变"
              "（sha256 与 views-manifest 的 source_sha256 比对一致）。"
              "8 项必需文案全部在场，无占位词；三行标题与两条新增信息之间、"
              "与发光球之间均有净距", phase="archive"),
        whole("launch-wide", ts(22, 8),
              "归档前复查通过：与 ev-a21-016 观察一致，交付字节未变。"
              "两行长标题覆盖完整 27 字标题，底部 5 行信息栈收口在底部扩展空间内",
              phase="archive"),
    ]

    # 补 event_id 与交付 PNG 的真实 sha256
    man = json.loads((PREV / "views-manifest.json").read_text(encoding="utf-8"))
    sha_by_art = {}
    for v in man["views"]:
        if v["artifact"] not in sha_by_art:
            sha_by_art[v["artifact"]] = v["source_sha256"]
    for i, e in enumerate(events):
        e["event_id"] = "ev-a21-%03d" % (nxt + i)
        if e["view_type"] == "whole-1to1":
            e["image"]["sha256"] = sha_by_art[e["artifact"]]

    block = {
        "conclusion": ("两图通过实际看图验收：竖版三行、横版两行长标题均为完整 27 字、"
                       "字号 66/52 均 ≥48 且未变形压窄；新增赞助方与报名状态牌"
                       "各占一行、层级低于日期与网址；日期、讲者、ONLINE LAUNCH、"
                       "网址与品牌行全部保留；主色与 6 个品牌构件形态未变"
                       "（报名状态牌是牌子族的新实例而非新构件）；文字两两不碰撞、"
                       "标题不压发光球实体、上下与左右均有余量、无占位文字。"
                       "本轮首版即通过，未产生改进迭代——12 个查看视图逐张核对后"
                       "没有发现需要返工的缺陷。"),
        "image_open_events": events,
    }

    doc["rounds"]["2"] = block
    doc["updated_at"] = dt.datetime.now(TZ).isoformat(timespec="seconds")
    VE.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("appended round 2: %d events (%s .. %s)"
          % (len(events), events[0]["event_id"], events[-1]["event_id"]))
    print("round-1 events preserved:",
          len(doc["rounds"]["1"]["image_open_events"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
