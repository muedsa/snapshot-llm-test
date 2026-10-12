# -*- coding: utf-8 -*-
"""件-10《阅读路线与证据分级》：把整套手册的留痕倒回来看的元页面。

页面上每个数字都由 meta_stats.py 现场从真实日志算出（requests/iterations/
build-log/tool-usage 四份 jsonl + 九份 case.md + 九份 final.snapshot + 九个生成器
脚本），存进 research/meta.json；本件不引入任何新数据，只做呈现与自我审查。
1080×1520 深空底。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B04"))
import b04kit as B  # noqa: E402

W, H = 1080, 1520
MX, MW = 72, 936
CELL0, CELL1, CELL2 = "#16203A", "#1E2C4A", "#2F5D70"
SAFE, DANGER, AMBER = "#2E7B86", "#5C2415", "#3A2A18"
CYAN, EMBER, CORONA = B.CYAN, B.EMBER, B.CORONA
hrule, vrule = B.hrule, B.vrule
AY, BY, CY, DY, EY, FY, FYB = 196, 492, 670, 982, 1214, 1340, 1452

HOST = {"eclipse.gsfc.nasa.gov": "gsfc", "nssdc.gsfc.nasa.gov": "nssdc",
        "science.nasa.gov": "sci", "en.wikipedia.org": "wiki"}


def page_label(url):
    u = url.replace("https://", "")
    host, rest = u.split("/", 1)
    return "%s %s" % (HOST.get(host, host), rest)


def edges_case(key, edges):
    return [e for e in edges if e["from"] == key or e["to"] == key]


def build():
    M = json.loads((ROOT / "tmp" / RID / "B04" / "research" / "meta.json")
                   .read_text(encoding="utf-8"))
    cs, T = M["cases"], M["totals"]
    inp, edges = M["inputs_per_case"], M["shared_input_edges"]
    srcs, srcs_img = M["sources_per_case"], M["sources_per_case_on_image"]
    mk, okp, fails = M["image_marks"], M["ok_pages"], M["failed_pages"]
    keys = ["case-%02d" % n for n in range(1, 10)]
    tot = {k: sum(mk[c][k] for c in keys)
           for k in [u"推算", u"已证实", u"来源结论", u"原文", u"限制", u"演示"]}
    deg = [k for k in keys if not edges_case(k, edges)]
    cnt = {k: len(edges_case(k, edges)) for k in keys if k not in deg}
    lo = min(cnt.values())
    least = sorted(k for k, v in cnt.items() if v == lo)
    nbrs = sorted({(e["to"] if e["from"] == k else e["from"])
                   for k in least for e in edges_case(k, edges)})
    blocked_self = 0
    for ln in (ROOT / "tmp" / RID / "B04" / "build-log.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(ln)
        if r.get("case") == "10" and r.get("request_sent") is False:
            blocked_self += 1
    d, tf = B.doc(W, H)

    B.header(d, tf, "hd", "拾", "阅读路线与证据分级",
             u"十件成品 · 快照内 %d 次真实请求 · %d 条迭代留痕 · 成功 %d 页／失败 %d 页"
             % (T["http_requests"], T["iterations"], T["distinct_ok_pages"], len(fails)),
             size=46)

    # ================= A · 共享输入矩阵 =================
    B.tlab(d, tf, "a-t", MX, AY, MW, 22, u"A · 阅读路线的地基：前九件共用了哪几份推算产物",
           17, d.P["t0"], style="BOLD")
    B.mono(d, tf, "a-n", MX, AY + 22, MW, 30,
           u"格值＝行、列两件共同读取的 research/*.json 份数；对角＝该件自己读了几份输入。"
           u"关系不靠回忆，由生成器脚本里的 load() 逐份抠出。件-10 只读 meta.json，不入矩阵。",
           10.5, d.P["t2"], lines=2)
    x0, cw, y0, rh = 200, 40, AY + 70, 24
    d.rect(x0 - 3, y0 - 3, 9 * cw - 1, 9 * rh - 1, "#05080F")
    for i, k in enumerate(keys):
        B.mono(d, tf, "a-ch%d" % i, x0 + i * cw, AY + 52, cw - 4, 15, k[-2:], 11,
               d.P["t2"], align="CENTER")
        B.mono(d, tf, "a-rh%d" % i, x0 - 12, y0 + i * rh + 4, 40, 15, k[-2:], 11,
               d.P["t2"], align="END")
        for j in range(9):
            if i == j:
                val, col, fg = len(inp[k]), AMBER, CORONA
            else:
                val = len(set(inp[k]) & set(inp[keys[j]]))
                col = [CELL0, CELL1, CELL2, CYAN][min(val, 3)]
                fg = d.P["t2"] if val == 0 else B.PAPER
            d.rect(x0 + j * cw, y0 + i * rh, cw - 4, rh - 4, col)
            if val:
                B.mono(d, tf, "a-c%d%d" % (i, j), x0 + j * cw, y0 + i * rh + 4,
                       cw - 4, 15, str(val), 11, fg, align="CENTER")
    px = x0 + 9 * cw + 26
    pw = MX + MW - px
    B.tlab(d, tf, "a-lt", px, AY + 52, pw, 16, u"怎么读这张矩阵", 12.5, d.P["t0"], style="BOLD")
    for i, (t, c) in enumerate([(u"对角金底＝该件自己的输入份数", CORONA),
                               (u"0＝最深格，两件没共用任何推算产物", CELL0),
                               (u"1–2＝深蓝到青蓝，多为 catalog/derived", CELL2),
                               (u"3＝最亮青底，整块共用同一批统计", CYAN)]):
        yy = AY + 76 + i * 17
        d.rect(px, yy + 2, 11, 11, c)
        B.mono(d, tf, "a-l%d" % i, px + 17, yy, pw - 17, 14, t, 10, d.P["t1"])
    top = sorted(edges, key=lambda e: (-e["w"], e["from"]))[:4]
    B.mono(d, tf, "a-e0", px, AY + 152, pw, 14, u"%d 条非零边里最粗的四对：" % len(edges),
           10.5, d.P["t0"])
    for i, e in enumerate(top):
        B.mono(d, tf, "a-e%d" % (i + 1), px, AY + 168 + i * 15, pw, 13,
               u"%s↔%s 共 %d：%s" % (e["from"][-2:], e["to"][-2:], e["w"],
                                     " ".join(f[:-5] for f in e["shared"])), 10, d.P["t2"])
    B.mono(d, tf, "a-i1", px, AY + 238, pw, 14,
           u"孤岛：%s 与任何一件都没有共用输入。" % u"、".join(k[-2:] for k in deg),
           10, EMBER)
    B.mono(d, tf, "a-i2", px, AY + 254, pw, 14,
           u"边最少：%s 只与 %s 相连。" % (u"、".join(k[-2:] for k in least),
                                        u"、".join(n[-2:] for n in nbrs)), 10, d.P["t2"])

    # ================= B · 证据四级 =================
    B.tlab(d, tf, "b-t", MX, BY, MW, 22, u"B · 证据分级：图上每块内容属于哪一级，各出现多少次",
           17, d.P["t0"], style="BOLD")
    B.mono(d, tf, "b-n", MX, BY + 22, MW, 15,
           u"计数＝九份 final.snapshot 文本里这些自标词出现的次数（字符串计数，不是估算）。",
           10.5, d.P["t2"])
    for i, (name, why, col, n, wd) in enumerate([
            (u"已证实", u"只由几何／算术必然得出、与目录数据无关的事实", CYAN,
             tot[u"已证实"], u"已证实"),
            (u"来源结论", u"NASA 页面上的陈述，转述并注明出处", B.MOON,
             tot[u"来源结论"], u"来源结论"),
            (u"我的推算", u"由真实数据经模型／算术得到，图上逐处自标", CORONA, tot[u"推算"], u"推算"),
            (u"演示／虚构", u"编造数值或占位数据——本册一条都没有", EMBER, tot[u"演示"], u"演示")]):
        yy = BY + 44 + i * 28
        d.rect(MX, yy + 1, 6, 22, col)
        B.tlab(d, tf, "b-l%d" % i, MX + 16, yy, 150, 16, name, 12.5, col, style="BOLD")
        B.mono(d, tf, "b-c%d" % i, MX + 168, yy, 68, 16, u"%d 处" % n, 12,
               d.P["t0"] if n else EMBER, align="END")
        B.mono(d, tf, "b-w%d" % i, MX + 246, yy + 2, 440, 15, why, 10.5, d.P["t1"])
        where = u" ".join(u"%s×%d" % (c[-2:], mk[c][wd]) for c in keys if mk[c][wd])
        B.mono(d, tf, "b-p%d" % i, 700, yy + 2, 308, 15,
               (where if where else u"（无）"), 10, col if where else d.P["t2"], align="END")
    B.mono(d, tf, "b-x", MX + 16, BY + 160, 920, 15,
           u"另两类自标：%d 处“原文”（逐字引用后照排上去）、%d 处“限制”（F 区就是本页自己的）。"
           % (tot[u"原文"], tot[u"限制"]), 10.5, d.P["t2"])

    # ================= C · 十件账 =================
    # (左边界, 宽, 表题, 对齐)——表头与数值同盒，右端天然对齐
    cols = [(72, 40, u"编号", "END"), (118, 330, u"标题", "START"), (352, 98, u"尺寸", "END"),
            (466, 90, u"DSL", "END"), (574, 66, u"渲染", "END"), (656, 50, u"迭代", "END"),
            (720, 48, u"推算", "END"), (784, 48, u"点名", "END"), (848, 48, u"图内", "END"),
            (940, 68, u"闸门", "END")]
    B.tlab(d, tf, "c-t", MX, CY, MW, 22, u"C · 前九件的账（本件在表外）：图幅、DSL、渲染、留痕、自标、点名来源",
           17, d.P["t0"], style="BOLD")
    hrule(d, MX, CY + 24, MW, d.P["border"], 1)
    for x, wd, t, al in cols:
        B.tlab(d, tf, "c-h%d" % x, x, CY + 28, wd, 15, t, 10.5, d.P["t2"], align=al)
    rowh = 19
    for i, c in enumerate(cs):
        yy = CY + 46 + i * rowh
        k = c["case"]
        if i % 2:
            d.rect(MX, yy - 3, MW, rowh, "#0B1120")
        B.mono(d, tf, "c-%d-0" % i, 72, yy, 40, 15, k[-2:], 11, EMBER, align="END")
        B.tlab(d, tf, "c-%d-1" % i, 118, yy, 330, 15, c["title"] or u"（未交付）", 11, d.P["t0"])
        B.mono(d, tf, "c-%d-2" % i, 352, yy, 98, 15,
               "%d×%d" % tuple(c["dimensions"]) if c["dimensions"] else u"—", 10.5,
               d.P["t1"], align="END")
        B.mono(d, tf, "c-%d-3" % i, 466, yy, 90, 15, "{:,}".format(c["final_snapshot_bytes"] or 0),
               10.5, d.P["t1"], align="END")
        B.mono(d, tf, "c-%d-4" % i, 574, yy, 66, 15,
               "%d/%d" % (c["render_ok"], c["render_requests"]), 10.5,
               CYAN if c["render_ok"] == c["render_requests"] else EMBER, align="END")
        B.mono(d, tf, "c-%d-5" % i, 656, yy, 50, 15, str(c["iterations_logged"]), 10.5,
               d.P["t1"], align="END")
        B.mono(d, tf, "c-%d-6" % i, 720, yy, 48, 15, str(mk[k][u"推算"]), 10.5,
               CORONA if mk[k][u"推算"] else EMBER, align="END")
        B.mono(d, tf, "c-%d-7" % i, 784, yy, 48, 15, str(len(srcs[k])), 10.5,
               d.P["t1"] if srcs[k] else EMBER, align="END")
        B.mono(d, tf, "c-%d-8" % i, 848, yy, 48, 15, str(len(srcs_img[k])), 10.5,
               d.P["t1"] if srcs_img[k] else EMBER, align="END")
        B.mono(d, tf, "c-%d-9" % i, 940, yy, 68, 15, str(c["gate_blocked_attempts"]), 10.5,
               CORONA if c["gate_blocked_attempts"] else d.P["t2"], align="END")
    yy = CY + 46 + 10 * rowh
    hrule(d, MX, yy - 6, MW, d.P["border"], 1)
    B.mono(d, tf, "c-sum", MX, yy + 1, MW, 15,
           u"合计：渲染 %d/%d 全部 200 · 迭代 %d 条（baseline %d／visual %d／语法修复 %d／重试 %d）· "
           u"成品 DSL %s B · 成品 PNG %s B"
           % (T["renders_ok"], T["renders"], T["iterations"],
              T["iteration_types"].get("baseline", 0), T["iteration_types"].get("visual", 0),
              T["iteration_types"].get("syntax-fix", 0), T["iteration_types"].get("retry", 0),
              "{:,}".format(T["final_dsl_bytes"]), "{:,}".format(T["final_png_bytes"])),
           10.5, d.P["t1"])
    B.mono(d, tf, "c-note", MX, yy + 18, MW, 14,
           u"推算＝该件成品图面上“推算”自标次数；点名＝case.md 写出的 sources/probe/research 路径数；"
           u"图内＝成品 DSL 上印出的同类路径数；闸门＝被 TextFit 本地拦下、未提交服务的次数。",
           10, d.P["t2"])
    B.mono(d, tf, "c-note2", MX, yy + 32, MW, 14,
           u"02、03 的后两列都是 0（早期 case.md 只写“见 sources/ 目录”，未逐一点名）。"
           u"这是留痕缺陷，D 区把整份成功清单补齐在这里。", 10, EMBER)

    # ================= D · 来源账 =================
    B.tlab(d, tf, "d-t", MX, DY, MW, 22,
           u"D · 来源账：%d 次文档抓取，成功 %d 次／失败 %d 次，去重后 %d 页全列在下面"
           % (T["document_requests"], T["document_by_status"]["200"], len(fails),
              T["distinct_ok_pages"]), 17, d.P["t0"], style="BOLD")
    n200, n404, nto = (T["document_by_status"]["200"], T["document_by_status"]["404"],
                       T["document_by_status"]["0"])
    bw = MW / float(T["document_requests"])
    d.rect(MX, DY + 26, n200 * bw, 17, SAFE)
    d.rect(MX + n200 * bw, DY + 26, n404 * bw, 17, DANGER)
    d.rect(MX + (n200 + n404) * bw, DY + 26, nto * bw, 17, AMBER)
    B.mono(d, tf, "d-b1", MX + 6, DY + 27, n200 * bw - 10, 14, u"成功（200）%d 次" % n200, 10, B.PAPER)
    B.mono(d, tf, "d-b2", MX + n200 * bw + 5, DY + 27, n404 * bw - 8, 14, u"404 %d 次" % n404,
           10, B.MOON)
    B.mono(d, tf, "d-b3", MX + (n200 + n404) * bw + 4, DY + 27, nto * bw - 6, 14,
           u"超时 %d" % nto, 9.5, CORONA)
    hosts = sorted(T["document_hosts"].items(), key=lambda kv: -kv[1])
    B.mono(d, tf, "d-h0", MX, DY + 48, MW, 14,
           u"按主机：" + u"　".join("%s %d" % (h, n) for h, n in hosts), 10, d.P["t1"])
    per = 9
    for i, u in enumerate(okp):
        ci, ri = divmod(i, per)
        B.mono(d, tf, "d-p%d" % i, MX + ci * 312, DY + 64 + ri * 13, 306, 14,
               u"%2d %s" % (i + 1, page_label(u)), 9.5, d.P["t2"])
    fy = DY + 64 + per * 13 + 2
    B.mono(d, tf, "d-f0", MX, fy, MW, 14,
           u"失败逐条留在 requests.jsonl（含 curl 原文），头两条样本：", 10, d.P["t1"])
    B.mono(d, tf, "d-f1", MX, fy + 15, MW, 14,
           u"　".join("%s %s" % (f["status"], f["url"].replace("https://", "")) for f in fails[:2]),
           9.5, d.P["t2"])
    wf = [f for f in fails if str(f["status"]) == "0"]
    B.mono(d, tf, "d-f3", MX, fy + 31, MW, 14,
           u"en.wikipedia.org 的 4 次全部连不上（curl 28），已计入 %d 条失败：这些页面一律未当作已读来源"
           u"引用。另有 %d 次 /fonts 查询（27 个字体族）、%d 次渲染全部 200、%d 次提交被闸门拦下。"
           % (len(wf), T["fonts_queries"], T["renders"], T["gate_blocked"]), 9.5, d.P["t2"])

    # ================= E · 三条阅读路线 =================
    B.tlab(d, tf, "e-t", MX, EY, MW, 22, u"E · 三条阅读路线（按共用的推算产物接起来）",
           17, d.P["t0"], style="BOLD")
    for i, (t, chain, col, why) in enumerate([
            (u"只想知道为什么有全食也有环食", u"01 → 06 → 09", CYAN,
             u"本影锥够不够长 → 最长能有多久 → 那一段里能不能裸眼"),
            (u"今年真要出门看一次", u"02 → 05 → 07 → 09", EMBER,
             u"在账本里挑一次 → 读它的路径页 → 算影速与落点 → 定摘镜时刻"),
            (u"要核对数据本身", u"02 → 08 → 03 → 04 → 10", CORONA,
             u"逐行解析 → 投到地图上 → 查周期与退行 → 回到本页看口径")]):
        yy = EY + 26 + i * 30
        d.rect(MX, yy + 1, 4, 24, col)
        B.tlab(d, tf, "e-t%d" % i, MX + 14, yy, 300, 16, t, 12, d.P["t0"], style="BOLD")
        B.mono(d, tf, "e-c%d" % i, MX + 330, yy, 180, 16, chain, 11.5, col)
        B.mono(d, tf, "e-w%d" % i, MX + 14, yy + 16, 920, 13, why, 9.5, d.P["t2"])

    # ================= F · 全套限制 =================
    B.tlab(d, tf, "f-t", MX, FY, MW, 22, u"F · 这十页共同的限制（不是某一页的）",
           17, d.P["t0"], style="BOLD")
    for i, ln in enumerate([
            u"服务没有矢量 path：圆、环、折线全由矩形扫描线拼出，放大必见接缝；但比例一律线性，"
            u"没有一张图偷偷改过“同一像素＝同一秒／同一千米”。",
            u"目录食分是地心值、经纬度按最近 1° 量化（±0.5°，赤道约 ±56 km），站点实际值另有出入；",
            u"接触时刻、离轴窗口、裸眼占比、影速等一律是推算（图上共自标 %d 次），不是 NASA 的结论。"
            % tot[u"推算"],
            u"全册只用 UT 与地方真太阳时，不采用任何国家时区，也不换算成“钟表几点”。",
            u"观测安全以 NASA 安全页原文为准（件-09 逐字引用），本册不替代它，更不是医疗建议。"]):
        B.mono(d, tf, "f-l%d" % i, MX, FY + 20 + i * 15, MW, 15, ln, 10, d.P["t1"], lines=2)

    B.footband(d, tf, "fb", [
        u"本页数字来源：meta_stats.py 读取四份 jsonl（requests %d／iterations %d／build-log／"
        u"tool-usage %d 行）与九份 case.md、九份 DSL → meta.json（快照 %sZ）。"
        % (T["http_requests"], T["iterations"], T["tool_usage_records"],
           M["generated_at"][:16].replace("T", " ")),
        u"口径：文档请求按 URL 逐条计（同页重抓分别计次）；渲染＝实际提交的 POST；快照内闸门拦下 %d 次，"
        u"本件自己又被拦 %d 次（build-log 记 request_sent:false，一律未向服务发出请求）。"
        % (T["gate_blocked"], blocked_self),
        u"十件成品：01 本影锥／02 账本／03 沙罗／04 食季／05 2024 档案／06 时长／07 影速／"
        u"08 食甚点地理／09 裸眼窗口／10 本页。每件入口见各自 case-NN/case.md。",
    ], size=10, y=FYB)

    info = {"renders": T["renders"], "docs": T["document_requests"],
            "iters": T["iterations"], "tiers": (tot[u"已证实"], tot[u"来源结论"],
                                               tot[u"推算"], tot[u"演示"])}
    return d, tf, info
