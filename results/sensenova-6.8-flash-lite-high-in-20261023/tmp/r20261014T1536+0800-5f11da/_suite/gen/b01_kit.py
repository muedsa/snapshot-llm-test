"""B 类作品集共用构件：DSL 排版基元、多边形/折线扫描线填充、干跑门禁、色盲校验、渲染留痕。

本 kit 是在 A24 的 a24_pages.py 之上扩展的：A24 只需要矩形与文字，
B 类用例（山形剖面、雪线带、赛道丝带、对数螺旋、径向声场、瓶阵）需要任意多边形填充
与折线描边。两者都用同一套扫描线光栅化：把多边形按行切成矩形交给 <Container>，
所以整条几何链路仍然只用 class-DOM DSL 的 <Positioned>/<Container>/<Text>。

不写死机器路径；路径基准 suite_root，见 PATHS.md。

用法
    import b01_kit as K
    doc = K.Doc(1920, 1080, K.NIGHT)
    doc.fill([...], K.SNOW)
    doc.text(40, 40, "标题", 40, K.WHITE)
    gates = K.dry_run(doc, "case-01", 18, [])
"""
from __future__ import annotations

import datetime as dt
import json
import math
import pathlib
import sys
import uuid

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
sys.path.insert(0, str(HERE.parent))

TASK = "B01"
OUT = ROOT / "outputs" / RUN_ID / TASK
TMP = ROOT / "tmp" / RUN_ID / TASK
TZ = dt.timezone(dt.timedelta(hours=8))
TZ_NAME = "Asia/Shanghai (UTC+08:00)"

# ------------------------------------------------------------------ 字体与通用色
FONT = "Noto Sans CJK SC,Inter"
CJK_WIDE = set("←→★■▼▲●◆◇○★☆✓✕·•§±×°′″")


def now() -> str:
    return dt.datetime.now(TZ).replace(microsecond=0).isoformat(timespec="seconds")


def fmt(v) -> str:
    if isinstance(v, float) and abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return str(v)


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def attrs(d: dict) -> str:
    return " ".join('%s="%s"' % (k, esc(v)) for k, v in d.items() if v is not None)


def tw(s: str, fs: float) -> float:
    """文字宽度估算：CJK/全角 1em，ASCII 字母数字 0.56em，空格 0.30em。

    只用于判断装不装得下与计算居中/右对齐起点，真实排版由服务端完成。
    """
    w = 0.0
    for ch in s:
        o = ord(ch)
        if (0x2E80 <= o <= 0x9FFF or 0xA000 <= o <= 0xA4CF or 0x3000 <= o <= 0x303F
                or 0xFF00 <= o <= 0xFF60 or 0x3040 <= o <= 0x30FF
                or 0xFE30 <= o <= 0xFE4F or 0x2018 <= o <= 0x201F
                or ch in CJK_WIDE):
            w += fs
        elif ch == " ":
            w += fs * 0.30
        elif ch == "÷":
            w += fs * 0.62
        else:
            w += fs * 0.56
    return w


def pitch(fs: float) -> float:
    """一行文字的纵向占用。Text height=1.0 是行高倍数，字形落在 1em 内，
    行距 ≥ 1em 时相邻行字形不相撞。"""
    return fs * 1.2


def fit_lines(s: str, fs: float, maxw: float, sep: str = "") -> list[str]:
    """按估算宽度折行；sep 非空时按宽度插入分隔符。CJK 可任意断行。"""
    lines: list[str] = []
    cur = ""
    for ch in s:
        if tw(cur + ch, fs) > maxw and cur:
            lines.append(cur)
            cur = sep + ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ 几何原语
def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def ring(cx, cy, r0, r1, a0, a1, steps=None) -> list[tuple]:
    """环形扇区边界：外弧 a0→a1、连到内弧、内弧 a1→a0、闭合。

    角度为弧度，0 = +x，随 y 轴向下为正（与屏幕坐标一致）。
    """
    steps = steps or max(8, int(abs(a1 - a0) * 40))
    pts = []
    for i in range(steps + 1):
        t = lerp(a0, a1, i / steps)
        pts.append((cx + math.cos(t) * r1, cy + math.sin(t) * r1))
    for i in range(steps, -1, -1):
        t = lerp(a0, a1, i / steps)
        pts.append((cx + math.cos(t) * r0, cy + math.sin(t) * r0))
    return pts


def bbox_of(pts: list[tuple]):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


# ------------------------------------------------------------------ Doc
class Doc:
    """收集 <Positioned> 片段，同时记录文字框与形状几何供门禁与证据引用。"""

    def __init__(self, w: int, h: int, bg: str = "#F5F7FA"):
        self.w, self.h = int(w), int(h)
        self.bg = bg
        self.parts: list[str] = []
        self.texts: list[dict] = []
        self.shapes: list[dict] = []

    # -- 基本矩形 ---------------------------------------------------------
    def rect(self, x, y, w, h, color=None, radius=0, border=None, opacity=None,
             grad=None, owner="rect"):
        """rect 是唯一的绘图原子；多边形填充也最终落成矩形。"""
        if w <= 0.02 or h <= 0.02:
            return
        a = {"width": fmt(math.ceil(w * 4) / 4), "height": fmt(math.ceil(h * 4) / 4)}
        if color:
            a["color"] = color
        if radius:
            a["borderRadius"] = fmt(radius)
        if border:
            a["border"] = border
        if grad:
            for k, v in grad.items():
                a[k] = v
        p = ('<Positioned left="%s" top="%s">'
             % (fmt(round(x, 2)), fmt(round(y, 2))))
        if opacity is not None:
            p = ('<Positioned left="%s" top="%s"><Opacity opacity="%s">'
                 % (fmt(round(x, 2)), fmt(round(y, 2)), fmt(opacity)))
        inner = '<Container %s/></Positioned>' % attrs(a)
        self.parts.append(p + inner + ("</Opacity>" if opacity is not None else ""))

    def line_h(self, x0, x1, y, color, w=1):
        self.rect(x0, y - w / 2, x1 - x0, w, color, owner="hline")

    def line_v(self, x, y0, y1, color, w=1):
        self.rect(x - w / 2, y0, w, y1 - y0, color, owner="vline")

    # -- 多边形扫描线填充 -------------------------------------------------
    def fill(self, pts: list[tuple], color, step: float = 1.0, owner="poly",
             pixel: bool = True):
        """偶奇规则按行填充任意多边形，每行切成若干矩形。

        step 是行高，必须 ≥1；1 表示逐像素行，边缘走 1px 锯齿，视觉上最干净。
        pixel=True 时每行矩形对齐整数像素网格（floor/ceil），避免半像素模糊。
        """
        if len(pts) < 3:
            return
        x0, y0, x1, y1 = bbox_of(pts)
        step = max(1.0, float(step))
        rh = int(round(step))
        ys = int(math.floor(y0))
        ye = int(math.ceil(y1))
        n = 0
        for yrow in range(ys, ye, rh):
            yc = yrow + rh * 0.5
            if not (y0 - 1e-9 <= yc <= y1 + 1e-9):
                continue
            xs = []
            m = len(pts)
            for i in range(m):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % m]
                if (ay <= yc < by) or (by <= yc < ay):
                    den = by - ay
                    t = (yc - ay) / den if abs(den) > 1e-12 else 0.0
                    xs.append(ax + t * (bx - ax))
            if len(xs) < 2:
                continue
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa, xb = xs[i], xs[i + 1]
                if xb - xa < 0.15:
                    continue
                if pixel:
                    lo, hi = int(math.floor(xa)), int(math.ceil(xb))
                else:
                    lo, hi = xa, xb
                if hi - lo <= 0:
                    continue
                self.rect(lo, yrow, hi - lo, rh, color, owner=owner)
                n += 1
        self.shapes.append({"kind": "fill", "bbox": [round(x0, 1), round(y0, 1),
                                                     round(x1, 1), round(y1, 1)],
                            "color": color, "rects": n, "points": len(pts)})

    def circle(self, cx, cy, r, color, step=1.0, owner="circle", segs=96):
        pts = [(cx + math.cos(2 * math.pi * i / segs) * r,
                cy + math.sin(2 * math.pi * i / segs) * r) for i in range(segs + 1)]
        self.fill(pts, color, step=step, owner=owner)

    # -- 折线描边 ---------------------------------------------------------
    def stroke(self, pts: list[tuple], color, width: float = 3.0, step: float = 1.0,
               owner="stroke", cap: bool = True):
        """折线描边：每段做垂直偏移四边形，顶点补菱形接头。"""
        if len(pts) < 2:
            return
        w2 = width / 2.0
        hw = w2
        for i in range(len(pts) - 1):
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            dx, dy = bx - ax, by - ay
            L = math.hypot(dx, dy)
            if L < 1e-9:
                continue
            nx, ny = -dy / L, dx / L
            quad = [(ax + nx * hw, ay + ny * hw), (bx + nx * hw, by + ny * hw),
                    (bx - nx * hw, by - ny * hw), (ax - nx * hw, ay - ny * hw)]
            self.fill(quad, color, step=step, owner=owner)
        if cap:
            for i in range(len(pts)):
                (vx, vy) = pts[i]
                self.fill([(vx, vy - hw), (vx + hw, vy), (vx, vy + hw),
                           (vx - hw, vy)], color, step=step, owner=owner)

    def arc(self, cx, cy, r0, r1, a0, a1, color, step=1.0, owner="arc"):
        self.fill(ring(cx, cy, r0, r1, a0, a1), color, step=step, owner=owner)

    # -- 文字 -------------------------------------------------------------
    def text(self, x, y, s, fs=20, color="#0F172A", bold=False, owner="txt",
             anchor="left", right=None, center=None):
        if anchor == "right" and right is not None:
            x = right - tw(s, fs)
        elif anchor == "center" and center is not None:
            x = center - tw(s, fs) / 2.0
        h = pitch(fs)
        t = {"text": s, "fontFamily": FONT, "fontSize": fmt(fs), "color": color,
             "height": "1.0", "softWrap": "FALSE", "textDirection": "LTR"}
        if bold:
            t["fontStyle"] = "BOLD"
        self.parts.append('<Positioned left="%s" top="%s" height="%s"><Text %s/>'
                          '</Positioned>' % (fmt(round(x, 2)), fmt(round(y, 2)),
                                             fmt(h), attrs(t)))
        self.texts.append({"x": round(x, 2), "y": round(y, 2), "w": round(tw(s, fs), 2),
                           "h": round(h, 2), "text": s, "fs": fs, "owner": owner})
        return round(x, 2)

    def text_r(self, right, y, s, fs=20, color="#0F172A", bold=False, owner="txt"):
        return self.text(0, y, s, fs, color, bold, owner, "right", right=right)

    def text_c(self, cx, y, s, fs=20, color="#0F172A", bold=False, owner="txt"):
        return self.text(0, y, s, fs, color, bold, owner, "center", center=cx)

    def para(self, x, y, s, fs=18, color="#3D4A5C", maxw=None, leading=1.2,
             bold=False, owner="para", anchor="left", right=None):
        """折行段落：每行独立文字，返回下一行的 y。"""
        maxw = maxw if maxw is not None else (self.w - x if anchor == "left"
                                              else self.w - 2 * x)
        lines = fit_lines(s, fs, maxw)
        yy = y
        for ln in lines:
            self.text(x, yy, ln, fs, color, bold, owner)
            yy += pitch(fs) * leading
        return yy

    # -- 输出 -------------------------------------------------------------
    def build(self) -> str:
        body = "\n".join(self.parts)
        return ('<Snapshot type="png" background="%s"><Container width="%d" height="%d">'
                '<Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">\n%s\n'
                '</Stack></Container></Snapshot>\n'
                % (self.bg, self.w, self.h, self.w, self.h, body))

    def stats(self) -> dict:
        return {"parts": len(self.parts), "texts": len(self.texts),
                "shapes": len(self.shapes)}


# ------------------------------------------------------------------ 干跑门禁
def hit(a: dict, b: dict) -> bool:
    return not (a["x"] + a["w"] <= b["x"] + 1e-6
                or b["x"] + b["w"] <= a["x"] + 1e-6
                or a["y"] + a["h"] <= b["y"] + 1e-6
                or b["y"] + b["h"] <= a["y"] + 1e-6)


def gate(gates: list, cid: str, check: str, ok, detail="") -> None:
    gates.append({"id": cid, "check": check, "passed": bool(ok),
                  "detail": str(detail)[:400]})


def dry_run(doc: Doc, name: str, min_fs: float, extras: list[dict] | None = None,
            max_parts: int = 9000, overlap_pairs: int = 12) -> list[dict]:
    """渲染前必须过的门禁：越界、同层文字重叠、字号下限、片段预算、形状越界。"""
    gates: list[dict] = list(extras or [])
    off = [t for t in doc.texts
           if t["x"] < -0.5 or t["y"] < -0.5
           or t["x"] + t["w"] > doc.w + 0.5 or t["y"] + t["h"] > doc.h + 0.5]
    gate(gates, name + "-01", "所有文字框在画布内", not off,
         "; ".join("%.0f..%.0f %.0f..%.0f %s" % (t["x"], t["x"] + t["w"], t["y"],
                                                 t["y"] + t["h"], t["text"][:24])
                   for t in off[:6]))
    cl = []
    for i in range(len(doc.texts)):
        for j in range(i + 1, len(doc.texts)):
            if hit(doc.texts[i], doc.texts[j]):
                cl.append("%s × %s" % (doc.texts[i]["text"][:18],
                                       doc.texts[j]["text"][:18]))
    gate(gates, name + "-02", "同层文字框互不重叠", not cl, "; ".join(cl[:overlap_pairs]))
    bad = [t for t in doc.texts if t["fs"] + 1e-6 < min_fs]
    gate(gates, name + "-03", "文字字号 ≥ %g px" % min_fs, not bad,
         "; ".join("%s=%g" % (t["text"][:18], t["fs"]) for t in bad[:6]))
    gate(gates, name + "-04", "片段数 ≤ %d（控制渲染负载与可复现性）" % max_parts,
         doc.stats()["parts"] <= max_parts, "parts=%d" % doc.stats()["parts"])
    sh_off = [s for s in doc.shapes
              if s["bbox"][0] < -2 or s["bbox"][1] < -2
              or s["bbox"][2] > doc.w + 2 or s["bbox"][3] > doc.h + 2]
    gate(gates, name + "-05", "所有形状在画布内", not sh_off,
         "; ".join(str(s["bbox"]) for s in sh_off[:6]))
    # 服务端不解析 HTML 实体：字面写 < > & 会被原样印出（如 "&lt;" 三个字）
    bad_ents = [t for t in doc.texts if any(c in t["text"] for c in "<>&")]
    gate(gates, name + "-06", "文字不含 < > & （DSL 不做实体解码，会原样印出）",
         not bad_ents, "; ".join(t["text"][:26] for t in bad_ents[:6]))
    return gates


def assert_gates(gates: list[dict], ctx: str) -> None:
    bad = [g for g in gates if not g["passed"]]
    if bad:
        lines = ["[%s] 门禁未通过 %d/%d：" % (ctx, len(bad), len(gates))]
        for g in bad:
            lines.append("  - %s %s :: %s" % (g["id"], g["check"], g["detail"]))
        raise SystemExit("\n".join(lines))


# ------------------------------------------------------------------ 色盲与对比度
def _srgb_to_lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(h: str) -> tuple:
    s = h.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) == 8:
        s = s[:6]
    return tuple(int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def rel_lum(h: str) -> float:
    r, g, b = hex_rgb(h)
    return 0.2126 * _srgb_to_lin(r) + 0.7152 * _srgb_to_lin(g) \
        + 0.0722 * _srgb_to_lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = rel_lum(a), rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _lin_to_oklabc(rgb):
    r, g, b = rgb
    l_ = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m_ = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s_ = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_ = l_ ** (1 / 3) if l_ >= 0 else -((-l_) ** (1 / 3))
    m_ = m_ ** (1 / 3) if m_ >= 0 else -((-m_) ** (1 / 3))
    s_ = s_ ** (1 / 3) if s_ >= 0 else -((-s_) ** (1 / 3))
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def _oklabc_to_lin(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l_, m_, s_ = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
            -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
            -0.0041960863 * l_ - 0.0415859152 * m_ + 1.0457819996 * s_)

_CVD = {
    "deutan": ((0.3678225234979229, 0.8659911847676002, -0.2427136835442655),
               (0.2880713130430416, 0.6625793770424613, 0.0543922124382803),
               (-0.0122626959097204, 0.0479275307173712, 0.9662377535219188)),
    "tritan": ((0.9584878079597711, 0.0321177886119577, 0.0171841884044650),
               (0.0351052399271156, 0.9724961093332689, 0.0044053349905373),
               (0.0583598196022901, 0.3079200249104371, 0.6337199122195417)),
}


def _mat_mul(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def _lin(h: str) -> tuple:
    return tuple(_srgb_to_lin(c) for c in hex_rgb(h))


def d_e(a: str, b: str, cvd: str | None = None) -> float:
    """OKLab ΔE，可选先做色觉缺陷模拟。用于类别色可分性自检。"""
    va = _lin_to_oklabc(_lin(a))
    vb = _lin_to_oklabc(_lin(b))
    if cvd:
        va = _lin_to_oklabc(_mat_mul(_CVD[cvd], _lin(a)))
        vb = _lin_to_oklabc(_mat_mul(_CVD[cvd], _lin(b)))
    return math.hypot(va[0] - vb[0], va[1] - vb[1], va[2] - vb[2]) * 100


def check_palette(name: str, pairs: list[tuple], gates: list[dict],
                  min_deutan: float = 8.0, min_tritan: float = 8.0,
                  min_normal: float = 15.0) -> dict:
    """类别色对可分性自检：每个色对在 deutan / tritan / 正常视觉下的 ΔE。"""
    out = []
    ok = True
    for a, b in pairs:
        r = {"pair": [a, b], "normal": round(d_e(a, b), 1),
             "deutan": round(d_e(a, b, "deutan"), 1),
             "tritan": round(d_e(a, b, "tritan"), 1)}
        r["passed"] = (r["deutan"] >= min_deutan and r["tritan"] >= min_tritan
                       and r["normal"] >= min_normal)
        ok = ok and r["passed"]
        out.append(r)
    gate(gates, name + "-cbr", "类别色对色盲可分（deutan/tritan ≥ %g, normal ≥ %g）"
         % (min_deutan, min_normal), ok,
         "; ".join("%s↔%s d=%g t=%g n=%g" % (p["pair"][0], p["pair"][1],
                                             p["deutan"], p["tritan"], p["normal"])
                   for p in out))
    return {"pairs": out, "all_passed": ok}


# ------------------------------------------------------------------ 渲染与留痕
def rel(p: pathlib.Path) -> str:
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def append_jsonl(path: pathlib.Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def log_iteration(rec: dict) -> dict:
    append_jsonl(TMP / "iterations.jsonl", rec)
    return rec


def save_gates(case_id: str, gates: list, note: str = "") -> str:
    """干跑门禁结果按轮次编号落盘，不覆盖任何历史轮次。

    这是渲染前的本地检查证据：每次跑门禁都新增一个编号文件，
    失败的门禁同样保留，方便事后对照「为什么那一版没渲」。
    """
    import re
    d = TMP / case_id
    d.mkdir(parents=True, exist_ok=True)
    prev = [int(m.group(1)) for f in d.glob(case_id + "-gates-*.json")
            if (m := re.search(r"-gates-(\d+)\.json$", f.name))]
    n = (max(prev) + 1) if prev else 1
    p = d / ("%s-gates-%03d.json" % (case_id, n))
    rec = {"case_id": case_id, "at": now(), "timezone": TZ_NAME, "note": note,
           "gates_total": len(gates), "gates_failed": len([g for g in gates
                                                           if not g["passed"]]),
           "gates": gates}
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    # 门禁干跑也是一次工具调用：本地断言检查，不花服务请求。
    tool_call(case_id, "python gate dry-run", "check",
              "%s：%d 条门禁，%d 条未通过 → %s"
              % (note[:40], rec["gates_total"], rec["gates_failed"],
                 pathlib.Path(p).name))
    return rel(p)


def log_tool(rec: dict) -> dict:
    append_jsonl(TMP / "tool-usage.jsonl", rec)
    return rec


def tool_call(case_id: str | None, tool: str, action: str, note: str,
              count: int = 1) -> dict:
    """B 类任务要求逐条留痕工具使用；每次真实调用记录一次。"""
    rec = {"at": now(), "timezone": TZ_NAME, "case_id": case_id,
           "tool": tool, "action": action, "note": note, "count": count}
    return log_tool(rec)


def sha256_bytes(b: bytes) -> str:
    import hashlib
    return hashlib.sha256(b).hexdigest()


def render_case(case_id: str, doc: Doc, label: str, purpose: str,
                attempt_note: str = "") -> dict:
    """过门禁后渲染单件作品并落 final.png / final.snapshot（字节不做任何后处理）。

    返回记录：请求 ID、字节数、哈希、DSL 哈希、片段统计。
    """
    import snap_client as C
    dsl = doc.build()
    case_dir = OUT / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    res = C.render(TASK, dsl, label, kind="render", purpose=purpose, attempts=3,
                   timeout=90,
                   extra={"case_id": case_id, "note": attempt_note})
    rec = {"at": now(), "timezone": TZ_NAME, "case_id": case_id, "label": label,
           "request_id": res["request_id"], "http_status": res["status"],
           "response_bytes": len(res["body"]) if res["body"] else 0,
           "attempts": res["attempt"],
           "started_at": res["meta"].get("started_at"),
           "ended_at": res["meta"].get("ended_at"),
           "elapsed_ms": res["meta"].get("elapsed_ms"),
           "parts": doc.stats()["parts"], "texts": doc.stats()["texts"],
           "shapes": doc.stats()["shapes"],
           "dimensions": [doc.w, doc.h], "dsl_chars": len(dsl)}
    if res["status"] == 200 and res["body"]:
        png = case_dir / "final.png"
        png.write_bytes(res["body"])
        dpath = case_dir / "final.snapshot"
        dpath.write_bytes(dsl.encode("utf-8"))
        rec["png"] = rel(png)
        rec["snapshot"] = rel(dpath)
        rec["png_sha256"] = sha256_bytes(png.read_bytes())
        rec["png_bytes"] = png.stat().st_size
        rec["snapshot_sha256"] = sha256_bytes(dpath.read_bytes())
        rec["snapshot_bytes"] = dpath.stat().st_size
        # 三条独立的比对：内存响应体、落盘的服务响应文件、交付的 final.png。
        # 之前只比内存体与自己，是恒真的，证明不了字节没被后处理。
        rec["png_matches_response_body"] = \
            sha256_bytes(res["body"]) == rec["png_sha256"]
        rpath = ROOT / res["log"].get("response_path") \
            if res["log"].get("response_path") else None
        rec["response_file"] = res["log"].get("response_path")
        rec["png_matches_response_file"] = bool(
            rpath is not None and rpath.exists()
            and sha256_bytes(rpath.read_bytes()) == rec["png_sha256"])
        rec["png_matches_response"] = rec["png_matches_response_file"]
        rec["png_written"] = True
    else:
        rec["png_written"] = False
        rec["error"] = res["meta"].get("error")
    log_iteration(rec)
    # B 类要求逐条留痕工具使用：每次真实渲染记录一次。
    tool_call(case_id, "snapshot POST /snapshot", "render",
              "%s：%d 次尝试 → HTTP %s，%d 片段，%d 文字，%d 形状"
              % (label, rec["attempts"], rec["http_status"], rec["parts"],
                 rec["texts"], rec["shapes"]),
              count=rec["attempts"])
    return rec


def ihdr_size(png: pathlib.Path) -> tuple:
    b = png.read_bytes()[:24]
    if len(b) < 24 or b[:8] != b"\x89PNG\r\n\x1a\n":
        return (0, 0)
    return (int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big"))
