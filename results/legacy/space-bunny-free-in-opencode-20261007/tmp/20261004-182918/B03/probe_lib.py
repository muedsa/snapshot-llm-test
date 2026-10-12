"""Shared helpers for B03 capability probes and works.

Everything here only emits DSL text; rendering goes through snapkit.
"""
from __future__ import annotations

import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))

import dsllib as D  # noqa: E402
import snapkit  # noqa: E402
import state as S  # noqa: E402

# Local-only hardening. Two real parser facts learned from probe 04:
#  1. attribute values must not contain a raw double quote, and
#  2. the parser does NOT decode XML entities, so &quot; renders literally.
# Fix: when a Text payload contains a double quote, emit it as CDATA instead of
# a text="" attribute. Shared dsllib is left untouched (other tasks run here).
_EL = D.el
_CDATA = D.cdata


def _el_cdata(tag: str, a=None, children=None, text=None, indent: int = 0):
    if text is not None and '"' in str(text) and not children:
        return _EL(tag, a, [_CDATA(str(text))], None, indent)
    return _EL(tag, a, children, text, indent)


D.el = _el_cdata
_TXT_EL = D.text_el


def _text_el(s: str, **kw):
    """D.text_el, but force the CDATA branch whenever a quote is present."""
    return _TXT_EL(s, **kw)

TASK = "B03"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
PROBE_OUT = os.path.join(TMP, "probes")
DRAFTS = os.path.join(TMP, "drafts")

snapkit.configure(TASK, OUT, TMP)
for _p in (PROBE_OUT, DRAFTS):
    os.makedirs(_p, exist_ok=True)

_seq = {"n": 0}


def draft(dsl: str, tag: str) -> str:
    """Save a numbered copy of the DSL into tmp/B03/drafts for traceability."""
    _seq["n"] += 1
    name = "v%03d-%s.snapshot" % (_seq["n"], tag)
    with open(os.path.join(DRAFTS, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    return name


def probe(dsl: str, tag: str) -> dict:
    name = draft(dsl, tag)
    return snapkit.render(dsl, "probe-%s.png" % tag, name, final=False,
                          out_dir=PROBE_OUT)


def render_final(dsl: str, case_dir: str, name: str) -> dict:
    d = os.path.join(OUT, case_dir)
    os.makedirs(d, exist_ok=True)
    draft(dsl, case_dir)
    return snapkit.render(dsl, name + ".png", name + ".snapshot", final=True,
                          out_dir=d)


def render_preview(dsl: str, tag: str) -> dict:
    p = os.path.join(TMP, "preview")
    os.makedirs(p, exist_ok=True)
    draft(dsl, tag)
    return snapkit.render(dsl, "prev-%s.png" % tag, "prev-%s.snapshot" % tag,
                          final=False, out_dir=p)


# ---------- matrix helpers (column-major 4x4, screen y down) ----------

def col_major(m: list[list[float]]) -> str:
    """m is row-major 4x4 -> column-major string for Transform.matrix."""
    vals = []
    for c in range(4):
        for r in range(4):
            vals.append("%.6g" % m[r][c])
    return "(" + ",".join(vals) + ")"


def mat_identity() -> list[list[float]]:
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def mat_mul(a, b):
    out = [[0.0] * 4 for _ in range(4)]
    for r in range(4):
        for c in range(4):
            out[r][c] = sum(a[r][k] * b[k][c] for k in range(4))
    return out


def mat_rot(deg_ccw: float):
    """Counter-clockwise degrees on screen (y down) -> rotation matrix."""
    t = math.radians(deg_ccw)
    c, s = math.cos(t), math.sin(t)
    return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def mat_scale(sx, sy=None):
    sy = sx if sy is None else sy
    return [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def mat_skew(sx_deg, sy_deg=0.0):
    tx, ty = math.tan(math.radians(sx_deg)), math.tan(math.radians(sy_deg))
    return [[1, tx, 0, 0], [ty, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def mat_persp(d: float):
    """m[2][3] (row2,col3) = d : classic CSS perspective-ish divide."""
    m = mat_identity()
    m[2][3] = d
    return m


def mat_translate(dx, dy):
    m = mat_identity()
    m[0][3] = dx
    m[1][3] = dy
    return m


def combine(*mats):
    out = mat_identity()
    for m in mats:
        out = mat_mul(out, m)
    return out


def transform(child: str, matrix: str, origin: str = "(0,0)",
              alignment: str | None = None, indent: int = 0) -> str:
    a = {"matrix": matrix, "origin": origin}
    if alignment:
        a["alignment"] = alignment
    return D.el("Transform", a, [child], indent=indent)


def hud(kids, w, h, bg="#0B1020FF", tag="Container", extra=None):
    return D.el(tag, dict({"width": w, "height": h, **dict(extra or {})}, ) if not extra
                else {"width": w, "height": h, **extra}, kids)