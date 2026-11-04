# -*- coding: utf-8 -*-
"""Tiny DSL construction helpers shared by suite tasks.

Script base: suite_root. No third-party dependency.
Every helper returns a *string* fragment of Snapshot DSL; callers assemble the
tree and write it to a `.snapshot` file.
"""
from __future__ import annotations

from typing import Iterable


def esc(text: str) -> str:
    """Return text safe for a Text element body.

    The parser performs no HTML entity decoding, so text containing & < > must be
    wrapped in CDATA. `]]>` inside the payload is split across two CDATA sections.
    """
    s = str(text)
    if any(ch in s for ch in "&<>"):
        parts = s.split("]]>")
        body = "]]><![CDATA[".join(parts)
        return f"<![CDATA[{body}]]>"
    return s


def attr(value) -> str:
    """Quote an attribute value, escaping only the quote character."""
    s = str(value).replace('"', "&quot;")
    return f'"{s}"'


def text(
    x: float,
    y: float,
    content: str,
    *,
    width: float | None = None,
    size: float = 20,
    color: str = "#E9EFF9",
    bold: bool = False,
    align: str | None = None,
    family: str = "Inter,Noto Sans CJK SC",
    spacing: float | None = None,
    line_height: float | None = None,
    extra: str = "",
    opacity: float | None = None,
    max_lines: int | None = None,
    overflow: str | None = None,
    shadow: str | None = None,
    allow_wrap: bool = False,
    label: str = "",
) -> str:
    """Absolutely positioned single text element (`Positioned` + `Text`)."""
    if width is not None and not allow_wrap:
        check_fit(label or content[:16], content, width, size, spacing or 0.0)
    attrs = [f'left="{x:g}"', f'top="{y:g}"']
    if width is not None:
        attrs.append(f'width="{width:g}"')
    tattrs = [f'fontSize="{size:g}"', f'color="{color}"', f'fontFamily="{family}"']
    if bold:
        tattrs.append('fontStyle="BOLD"')
    if align:
        tattrs.append(f'textAlign="{align}"')
    if spacing is not None:
        tattrs.append(f'letterSpacing="{spacing:g}"')
    if line_height is not None:
        tattrs.append(f'height="{line_height:g}"')
    if max_lines is not None:
        tattrs.append(f'maxLines="{max_lines}"')
    if overflow:
        tattrs.append(f'overflow="{overflow}"')
    if shadow:
        tattrs.append(f'textShadow="{shadow}"')
    if extra:
        tattrs.append(extra)
    body = esc(content)
    node = f"<Text {' '.join(tattrs)}>{body}</Text>"
    if opacity is not None:
        node = f'<Opacity opacity="{opacity:g}">{node}</Opacity>'
    return f"<Positioned {' '.join(attrs)}>{node}</Positioned>"


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    color: str = "#0D1524",
    radius: float | None = None,
    border: str | None = None,
    extra: str = "",
    gradient: str | None = None,
) -> str:
    attrs = [f'width="{w:g}"', f'height="{h:g}"']
    if gradient:
        attrs.append(gradient)
    else:
        attrs.append(f'color="{color}"')
    if radius is not None:
        attrs.append(f'borderRadius="{radius:g}"')
    if border:
        attrs.append(f'border="{border}"')
    if extra:
        attrs.append(extra)
    return f'<Positioned left="{x:g}" top="{y:g}"><Container {" ".join(attrs)}/></Positioned>'


def line(x1: float, y1: float, x2: float, y2: float, color: str, width: float = 1.0) -> str:
    """Straight segment as a rotated 1px container (axis-aligned only)."""
    if y1 == y2:
        return rect(min(x1, x2), y1 - width / 2, abs(x2 - x1), width, color=color)
    if x1 == x2:
        return rect(x1 - width / 2, min(y1, y2), width, abs(y2 - y1), color=color)
    raise ValueError("line() only supports axis-aligned segments")


def stack(children: Iterable[str], *, w: float | None = None, h: float | None = None,
          clip: str = "HARD_EDGE") -> str:
    inner = "".join(children)
    attrs = ['alignment="TOP_LEFT"', f'clipBehavior="{clip}"']
    if w is not None:
        attrs.append(f'width="{w:g}"')
    if h is not None:
        attrs.append(f'height="{h:g}"')
    return f"<Stack {' '.join(attrs)}>{inner}</Stack>"


def document(width: float, height: float, children: Iterable[str], *,
             background: str | None = "#070C16") -> str:
    """Wrap absolutely positioned children in a fixed-size canvas.

    ``background=None`` omits the attribute so the canvas stays transparent.
    """
    inner = "".join(children)
    bg_attr = f' background="{background}"' if background else ""
    return (
        f'<Snapshot{bg_attr} type="png">'
        f'<Container width="{width:g}" height="{height:g}">'
        f'<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">{inner}</Stack>'
        f"</Container></Snapshot>"
    )


def fmt_int(value: float) -> str:
    return f"{int(round(value)):,}"


def fmt_money(value: float, unit: str = "元") -> str:
    return f"{fmt_int(value)} {unit}"


def fmt_pct(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}%"


def wan(value: float) -> str:
    return f"{value / 10000:.2f}"


# ------------------------------------------------------------------ text metrics
# Measured against the live service fonts (Inter + Noto Sans CJK SC) at 20 px:
#   CJK 20.00 px/char, digits 11.70, uppercase 13.50, lowercase 10.54,
#   "2026-04" 82 px, "5.00%" 57 px.
# See tmp/<run_id>/_suite/shared/text-metrics.json for the raw calibration.
_EM = {"cjk": 1.0, "digit": 0.585, "upper": 0.675, "lower": 0.527,
       "space": 0.28, "punct": 0.46, "symbol": 0.6}
WARNINGS: list[str] = []


def _char_em(ch: str) -> float:
    if ch == " ":
        return _EM["space"]
    code = ord(ch)
    if code < 128:
        if ch.isdigit():
            return _EM["digit"]
        if ch.isupper():
            return _EM["upper"]
        if ch.islower():
            return _EM["lower"]
        if ch in ".,:;'!|":
            return _EM["punct"]
        return _EM["symbol"]
    if 0xFF00 <= code <= 0xFF60:  # fullwidth punctuation
        return 1.0
    return _EM["cjk"]


def est_width(text: str, size: float, spacing: float = 0.0) -> float:
    """Estimated rendered width in CSS pixels for the service fonts."""
    s = str(text)
    return sum(_char_em(ch) * size for ch in s) + spacing * max(0, len(s) - 1)


def check_fit(label: str, text: str, width: float, size: float, spacing: float = 0.0) -> float:
    """Record a warning when the estimated text width exceeds its box."""
    w = est_width(text, size, spacing)
    if w > width * 1.01:
        WARNINGS.append(f"OVERFLOW {label}: est {w:.0f}px > box {width:.0f}px "
                        f"(size {size:g}) :: {str(text)[:60]}")
    return w


def drain_warnings() -> list[str]:
    out = list(WARNINGS)
    WARNINGS.clear()
    return out

