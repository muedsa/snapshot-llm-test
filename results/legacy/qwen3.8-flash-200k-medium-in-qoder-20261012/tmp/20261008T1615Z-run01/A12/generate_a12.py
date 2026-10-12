"""A12: build the four breakpoint DSLs from one content file + one token table.

There is no per-canvas special case: the same hero(), card() and footer() code runs for all
four sizes and only reads BREAKS/TYPE. The vertical rhythm is solved, not hand-tuned:

  1. solve() picks the largest gap multiplier from a bounded band that still fits, so the
     micro-rhythm stays comparable between 360 and 1920 instead of one canvas being 4x looser;
  2. leftover slack is distributed 2:2:1 over hero->grid, grid->footer and top, with one
     part kept as bottom pad, which centres the composition instead of padding one gap wide;
  3. the meta block reflows by measurement: the three groups flow across the panel and wrap
     when they no longer fit, and on a single flow line the CTA moves up beside them.

Every text box that is emitted is recorded in self.regions, so content-map.json is the layout
engine's own output rather than a hand-written description of it, and check_a12.py measures
the same boxes.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A12"
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
sys.path.insert(0, str(TEMP))

from dslkit import Doc, TextFit, n  # noqa: E402
import plan_a12 as P  # noqa: E402

C = P.content
CARDS = P.cards
BODY_ROLES = ("meta", "body", "card_detail", "card_title", "cta", "website",
              "meta_label", "index", "kicker", "subtitle")
GM_BAND = [1.6, 1.4, 1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.55, 0.5]
SLACK_SPLIT = (2, 2, 1, 1)          # hero->grid, grid->footer, top, bottom


class Sheet:
    def __init__(self, bp, gm=1.0, top_off=0, extra_b1=0, extra_b2=0):
        self.bp = bp
        self.k = P.BP.index(bp)
        self.b = P.BREAKS[bp]
        self.W, self.H = self.b["canvas"]
        self.M = self.b["margin"]
        self.gm = gm
        self.top_off = top_off
        self.extra_b1 = extra_b1
        self.extra_b2 = extra_b2
        self.reset()

    def reset(self):
        self.fit = TextFit()
        self.regions = []
        self.problems = []
        self.doc = Doc(self.W, self.H, bg=P.PALETTE["paper"],
                       font="Inter,Noto Sans CJK SC", palette=P.PALETTE)

    def t(self, key):
        return P.TYPE[key][self.k]

    def g(self, v):
        return round(v * self.gm)

    # ---------------- primitives ----------------
    def txt(self, x, y, w, field, text, size, color, style=None, mono=False,
            align="START", prov="input", role="body"):
        nl = self.fit.lines(text, size, w)
        h = P.hh(size, nl)
        self.fit.check(f"{self.bp}/{field}", text, size, w, h, lines=nl)
        va = {"START": "TOP_LEFT", "END": "TOP_RIGHT", "CENTER": "TOP_CENTER"}[align]
        inner = self.doc.text(text, color=color, size=size, style=style,
                              align=None if align == "START" else align)
        if mono:
            inner = inner.replace(f'fontFamily="{self.doc.font}"',
                                  'fontFamily="Noto Sans Mono CJK SC"')
        self.doc.pos(x, y, w, h, self.doc.box(w, h, inner=inner, align=va))
        self.regions.append({"field": field, "text": text, "provenance": prov,
                             "role": role, "font_pt": size, "lines": nl, "mono": mono,
                             "box": [round(x, 1), round(y, 1), round(w, 1), h]})
        return h

    def rect(self, x, y, w, h, color, radius=None, border=None):
        self.doc.pos(x, y, w, h, self.doc.box(w, h, color=color, radius=radius,
                                              border=border))

    def pill(self, x, y, w, h, text, size, fg, bg, field):
        self.rect(x, y, w, h, bg, radius=h / 2)
        th = P.hh(size, 1)
        self.doc.pos(x + 12, y + (h - th) / 2, w - 24, th,
                     self.doc.box(w - 24, th,
                                  inner=self.doc.text(text, color=fg, size=size,
                                                      style="BOLD", align="CENTER"),
                                  align="CENTER"))
        self.regions.append({"field": field, "text": text, "provenance": "input",
                             "role": "cta", "font_pt": size, "lines": 1, "mono": False,
                             "box": [round(x + 12, 1), round(y + (h - th) / 2, 1),
                                     round(w - 24, 1), th]})

    def dot_row(self, x, y, d, gap, color, count=6):
        for i in range(count):
            self.doc.dot(x + i * (d + gap), y + d / 2, d, color)

    # ---------------- pieces ----------------
    def meta_groups(self, size):
        """Measured widths of the three 日期/时间/地点 groups. Boxes hold w/SLACK, not w:
        TextFit wraps at 0.96 of the box width, so a box sized to the raw estimate wraps two
        CJK label glyphs onto a second line and doubles the row height."""
        out = []
        for lab, val in (("日期", C["date"]), ("时间", C["time"]),
                         ("地点", C["location"])):
            lw = round(self.fit.w(lab, size) / self.fit.SLACK) + 2
            vw = round(self.fit.w(val, size) / self.fit.SLACK) + 2
            out.append((lab, val, lw, vw))
        return out

    def meta_plan(self, w, size):
        """Pure measurement of the meta flow: lines of (x-offset, label, value, lw, vw) plus
        the width each line uses. One line on a wide panel, more as the panel narrows."""
        sep = round(size * 1.2)
        lines, cur, cx = [], [], 0
        for lab, val, lw, vw in self.meta_groups(size):
            gw = lw + 8 + vw
            if cur and cx + gw > w:
                lines.append((cur, cx - sep))
                cur, cx = [], 0
            cur.append((cx, lab, val, lw, vw))
            cx += gw + sep
        if cur:
            lines.append((cur, cx - sep))
        return lines

    def meta_draw(self, x, y, lines, size, color, label_color):
        for i, (items, _) in enumerate(lines):
            yy = y + i * (P.hh(size, 1) + self.g(4))
            for off, lab, val, lw, vw in items:
                self.txt(x + off, yy, lw, "label_" + lab, lab, size, label_color,
                         style="BOLD", prov="derived", role="meta_label")
                self.txt(x + off + lw + 8, yy, vw, "value_" + lab, val, size, color,
                         role="meta")
        return len(lines) * P.hh(size, 1) + (len(lines) - 1) * self.g(4)

    def card_h(self, w):
        """Pure measurement: the tallest card at this width, so all cards share one height
        and none of them can be clipped by a shorter sibling's row band."""
        pad, aw = self.b["inner"], self.b["accentBar"]
        st, sd, si = self.t("cardTitle"), self.t("cardDetail"), self.t("cardIndex")
        tw = w - pad * 2 - aw
        row1 = max(P.hh(si, 1),
                   max(P.hh(st, self.fit.lines(c["title"], st, tw)) for c in CARDS))
        det = max(P.hh(sd, self.fit.lines(c["detail"], sd, tw)) for c in CARDS)
        return pad + row1 + self.g(4) + det + pad

    def card(self, x, y, w, cidx):
        b, card = self.b, CARDS[cidx]
        pad, aw = b["inner"], b["accentBar"]
        st, sd, si = self.t("cardTitle"), self.t("cardDetail"), self.t("cardIndex")
        tw = w - pad * 2 - aw
        nl_t = self.fit.lines(card["title"], st, tw)
        nl_d = self.fit.lines(card["detail"], sd, tw)
        chip_w = round(self.fit.w(card["id"], si) + 14)
        row1 = max(P.hh(si, 1), P.hh(st, nl_t))
        h = self.card_h(w)
        self.rect(x, y, w, h, "#FFFFFF", radius=14,
                  border=f"1 SOLID {P.PALETTE['line']}")
        self.rect(x, y + aw * 2, aw, h - aw * 4, P.PALETTE["accent"], radius=aw / 2)
        ix, iy = x + aw + pad, y + pad
        cy = iy + (row1 - P.hh(si, 1)) / 2 + 1
        self.rect(ix, cy, chip_w, P.hh(si, 1), P.PALETTE["accentSoft"], radius=8)
        self.txt(ix, cy, chip_w, "index_" + card["id"], card["id"], si,
                 P.PALETTE["accent"], style="BOLD", mono=True, align="CENTER",
                 prov="derived", role="index")
        self.txt(ix + chip_w + 8, iy, tw - chip_w - 8, "card_title_" + card["id"],
                 card["title"], st, P.PALETTE["ink"], style="BOLD", role="card_title")
        self.txt(ix, iy + row1 + self.g(4), tw, "card_detail_" + card["id"],
                 card["detail"], sd, P.PALETTE["ink2"], role="card_detail")
        return h

    def hero(self, x, y, w):
        b = self.b
        aw, pad = b["accentBar"], b["heroPad"]
        cx, cw = x + aw + pad, w - aw - pad * 2
        cy = y + pad
        h = self.txt(cx, cy, cw, "kicker", P.DERIVED_KICKER, self.t("kicker"),
                     P.PALETTE["onHeroAccent"], style="BOLD", prov="derived",
                     role="kicker")
        cy += h + self.g(8)
        cy += self.txt(cx, cy, cw, "title", C["title"], self.t("title"),
                       P.PALETTE["onHero"], style="BOLD", role="title") + self.g(6)
        cy += self.txt(cx, cy, cw, "subtitle", C["subtitle"], self.t("subtitle"),
                       P.PALETTE["onHeroDim"], role="subtitle") + self.g(14)
        ms = self.t("meta")
        cs = self.t("cta")
        pw = min(round(self.fit.w(C["cta"], cs) + 44), cw)
        ph = round(cs * P.LINE) + max(18, round(cs * 0.9))   # pill padding tracks
        # the CTA type size, so the phone does not pay a 26px band for 16pt text
        # reflow 1: the meta groups flow across the panel and wrap by measurement
        lines = self.meta_plan(cw, ms)
        self.meta_mode = f"{len(lines)}line"
        # reflow 2: on a single meta line the CTA takes the room beside it, so a wide band
        # does not spend a whole row on one pill and leave the right half of the panel empty
        self.cta_mode = "same_line" if len(lines) == 1 \
            and lines[0][1] + self.g(24) + pw <= cw else "below"
        band = max(P.hh(ms, 1), ph) if self.cta_mode == "same_line" else 0
        my = cy + round((band - P.hh(ms, 1)) / 2) if band else cy
        mh = self.meta_draw(cx, my, lines, ms, P.PALETTE["onHero"],
                            P.PALETTE["onHeroAccent"])
        if self.cta_mode == "same_line":
            self.pill(cx + cw - pw, cy + round((band - ph) / 2), pw, ph, C["cta"], cs,
                      "#FFFFFF", P.PALETTE["accent"], "cta")
            cy += band + self.g(6)
        else:
            cy += mh + self.g(6)
            self.pill(cx, cy, pw, ph, C["cta"], cs, "#FFFFFF", P.PALETTE["accent"], "cta")
            cy += ph
        d = max(6, round(self.t("kicker") * 0.4))
        row_w = 6 * d + 5 * round(d * 0.75)
        self.dot_row(x + w - pad - row_w, y + pad, d, round(d * 0.75),
                     P.PALETTE["accent2"])
        h = cy + pad - y
        panel = self.doc.box(w, h, radius=18, grad=(
            'gradientType="LINEAR" gradientColors="#0F1B2D,#16263D,#0F1B2D" '
            'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"'))
        bar = self.doc.box(aw, h - aw * 4, color=P.PALETTE["accent"], radius=aw / 2)
        self.doc.parts.insert(0, f'<Positioned left="{n(x)}" top="{n(y + aw * 2)}" '
                                f'width="{n(aw)}" height="{n(h - aw * 4)}">{bar}</Positioned>')
        self.doc.parts.insert(0, f'<Positioned left="{n(x)}" top="{n(y)}" '
                                f'width="{n(w)}" height="{n(h)}">{panel}</Positioned>')
        return h

    def footer(self, x, y, w):
        size = self.t("website")
        self.doc.line(x, y, x + w, y, 1, P.PALETTE["rule"])
        d = max(4, round(size * 0.28))
        self.doc.dot(x + d / 2, y + 6 + P.hh(size) / 2, d, P.PALETTE["accent"])
        self.txt(x + d + 8, y + 6, w - d - 8, "website", C["website"], size,
                 P.PALETTE["muted"], mono=True, role="website")
        return 6 + P.hh(size)

    # ---------------- assembly ----------------
    def build(self):
        self.reset()
        b = self.b
        gx = b["cardGap"][0]
        gy = self.g(b["cardGap"][1])
        cw = self.W - 2 * self.M
        y = self.M + self.top_off
        cols = b["cols"]
        rows_n = (len(CARDS) + cols - 1) // cols
        cwid = (cw - (cols - 1) * gx) / cols
        ch = self.card_h(cwid)
        hero_h = self.hero(self.M, y, cw)
        grid_y = y + hero_h + self.g(b["blockGap"]) + self.extra_b1
        yy = grid_y
        for r in range(rows_n):
            for c in range(cols):
                i = r * cols + c
                if i < len(CARDS):
                    self.card(self.M + c * (cwid + gx), yy, cwid, i)
            yy += ch + gy
        grid_bottom = yy - gy
        fy = grid_bottom + self.g(b["blockGap"]) + 8 + self.extra_b2
        foot = self.footer(self.M, fy, cw)
        bottom = fy + foot + self.M
        self.layout = {"gap_multiplier": self.gm,
                       "slack_split": {"top": self.top_off, "hero_to_grid": self.extra_b1,
                                       "grid_to_footer": self.extra_b2},
                       "meta_block": self.meta_mode, "cta_block": self.cta_mode,
                       "hero_h": round(hero_h, 1), "grid_top": round(grid_y, 1),
                       "grid_bottom": round(grid_bottom, 1), "card_w": round(cwid, 1),
                       "card_h": ch, "rows": rows_n, "cols": cols,
                       "footer_y": round(fy, 1), "bottom_used": round(bottom, 1),
                       "canvas_h": self.H, "limit": self.H - self.M,
                       "slack": round(self.H - self.M - bottom, 1)}
        if bottom > self.H - self.M:
            self.problems.append(f"overflow: {self.bp} bottom {bottom:.1f} > "
                                 f"{self.H - self.M}")
        return self.geom()

    def geom(self):
        """Safe margin and pairwise text-box overlap, checked on every solve() attempt."""
        for r in self.regions:
            x, y, w, h = r["box"]
            if (x < self.M - 0.5 or y < self.M - 0.5 or x + w > self.W - self.M + 0.5
                    or y + h > self.H - self.M + 0.5):
                self.problems.append(f"margin: {r['field']} {[round(v) for v in r['box']]} "
                                     f"outside safe margin {self.M}")
        boxes = [(r["field"], r["box"]) for r in self.regions]
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                (f1, (a1, b1, w1, h1)), (f2, (a2, b2, w2, h2)) = boxes[i], boxes[j]
                ox = min(a1 + w1, a2 + w2) - max(a1, a2)
                oy = min(b1 + h1, b2 + h2) - max(b1, b2)
                if ox > 0.5 and oy > 0.5:
                    self.problems.append(f"overlap: {f1} x {f2} by {ox:.1f}x{oy:.1f}")
        return self

    # ---------------- solve / gate ----------------
    def solve(self):
        for gm in GM_BAND:
            if not Sheet(self.bp, gm=gm).build().problems:
                self.gm = gm
                break
        else:
            self.gm = GM_BAND[-1]
        slack = Sheet(self.bp, gm=self.gm).build().layout["slack"]
        if slack > 0:
            # the last weight stays as bottom pad, so the composition ends up roughly
            # centred rather than top-heavy with a dead band under the footer
            usable = slack * (sum(SLACK_SPLIT) - SLACK_SPLIT[3]) / sum(SLACK_SPLIT)
            tot = sum(SLACK_SPLIT)
            self.top_off = int(usable * SLACK_SPLIT[2] / (tot - SLACK_SPLIT[3]))
            self.extra_b1 = int(usable * SLACK_SPLIT[0] / (tot - SLACK_SPLIT[3]))
            self.extra_b2 = int(usable * SLACK_SPLIT[1] / (tot - SLACK_SPLIT[3]))
        self.build()
        if self.problems:                      # the slack split overshot: fall back
            self.gm, self.top_off, self.extra_b1, self.extra_b2 = GM_BAND[-1], 0, 0, 0
            self.build()
        return self

    def gate(self):
        """Type floors, plus whatever build()/geom() already found."""
        fl = P.FLOORS[self.bp]
        for r in self.regions:
            if r["role"] == "card_title" and r["font_pt"] < fl.get("cardTitle", 0):
                self.problems.append(f"floor: {r['field']} {r['font_pt']} < cardTitle")
            if r["role"] in BODY_ROLES and r["font_pt"] < fl["body"]:
                self.problems.append(f"floor: {r['field']} {r['font_pt']} < body "
                                     f"{fl['body']}")
            if r["role"] == "title" and "title" in fl and r["font_pt"] < fl["title"]:
                self.problems.append(f"floor: title {r['font_pt']} < {fl['title']}")
        self.problems += ["fit: " + p for p in self.fit.problems]
        return self


def build_all():
    return {bp: Sheet(bp).solve().gate() for bp in P.BP}


def emit(sheets):
    out = {}
    for bp, s in sheets.items():
        dsl = s.doc.dsl()
        (TEMP / f"{bp}.snapshot").write_text(dsl, encoding="utf-8")
        out[bp] = {"bytes": len(dsl.encode("utf-8")),
                   "positioned_elements": dsl.count("<Positioned"),
                   "text_items": dsl.count("<Text "),
                   "recorded_regions": len(s.regions),
                   "floors": P.FLOORS[bp],
                   "text_fit_checks": s.fit.n,
                   "text_fit_problems": s.fit.problems,
                   "layout": s.layout, "problems": s.problems}
    return out


if __name__ == "__main__":
    sheets = build_all()
    rep = emit(sheets)
    cmap = {
        "schema_version": 1, "path_base": "suite_root", "task_id": "A12", "run_id": RID,
        "source_content": "tasks/A12-responsive-system/inputs/content.json",
        "generated_by": f"tmp/{RID}/A12/generate_a12.py",
        "canvases": {bp: {"size": P.BREAKS[bp]["canvas"],
                          "safe_margin": P.BREAKS[bp]["margin"],
                          "hero_placement": P.HERO_MODE[bp],
                          "card_columns": P.BREAKS[bp]["cols"],
                          "gap_multiplier_used": sheets[bp].gm} for bp in P.BP},
        "provenance_note": "input = byte-for-byte from inputs/content.json; derived = "
                           "computed from it (card ids C1..C6, the kicker that counts them, "
                           "and the 日期/时间/地点 row labels). No input string is shortened, "
                           "summarised or dropped at any breakpoint.",
        "retention": {bp: {
            "input_fields": sorted({r["field"] for r in sheets[bp].regions
                                    if r["provenance"] == "input"}),
            "input_field_count": sum(1 for r in sheets[bp].regions
                                     if r["provenance"] == "input"),
        } for bp in P.BP},
        "layout_report": rep,
        "fields": {bp: {r["field"]: {"text": r["text"], "provenance": r["provenance"],
                                     "role": r["role"], "font_pt": r["font_pt"],
                                     "lines": r["lines"], "mono": r["mono"],
                                     "box": r["box"]} for r in sheets[bp].regions}
                   for bp in P.BP},
    }
    (TEMP / "content-map.json").write_text(
        json.dumps(cmap, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (TEMP / "design-tokens.json").write_text(
        json.dumps(P.tokens_doc(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for bp in P.BP:
        print(bp, json.dumps(rep[bp], ensure_ascii=False))
