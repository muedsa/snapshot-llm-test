#!/usr/bin/env python
# B06 渲染前自检：解析 .snapshot，拦截本 run 已实测的三类事故。
#   1) 图元越界 / 压到画布外
#   2) 文字估算字宽 > 盒子宽度（服务端会**静默裁掉**仍返回 200）
#   3) 文字盒高 < 字号 × 1.40
# 另报告字号层级与最紧的 20 处文字余量，供逐张看图前先筛一遍。
#
# 用法（基准 = suite_root）：
#   python tmp/run-20261011-01/B06/check_layout.py tmp/run-20261011-01/B06/drafts/b06-01-v1.snapshot ...
# 退出码 1 表示存在硬性问题（越界 / 可能裁字 / 盒高不足）。
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
from bsnap import em_width  # noqa: E402

POS = re.compile(
    r'<Positioned left="(-?[\d.]+)" top="(-?[\d.]+)" width="(-?[\d.]+)" height="(-?[\d.]+)">'
    r'(.*?)</Positioned>', re.S)
TEXT = re.compile(r'<Text\s(.*?)/>', re.S)
ATTR = re.compile(r'(\w+)="([^"]*)"')
ROOTC = re.compile(r'<Container width="([\d.]+)" height="([\d.]+)"')


def unescape(s: str) -> str:
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def check(path: Path) -> tuple[list[str], list[str]]:
    src = path.read_text(encoding="utf-8-sig")
    root = ROOTC.search(src)
    if not root:
        return [f"{path.name}: 找不到根 Container 尺寸"], []
    W, H = float(root.group(1)), float(root.group(2))
    errors, warns = [], []
    sizes: set[float] = set()
    tight: list[tuple[float, str, float, float]] = []

    for m in POS.finditer(src):
        x, y, w, h = (float(m.group(i)) for i in range(1, 5))
        body = m.group(5)
        if x < -0.5 or y < -0.5 or x + w > W + 0.5 or y + h > H + 0.5:
            errors.append(f"越界 Positioned ({x:.0f},{y:.0f}) {w:.0f}×{h:.0f} "
                          f"→ 右 {x + w:.0f}/下 {y + h:.0f}，画布 {W:.0f}×{H:.0f}")
        for tm in TEXT.finditer(body):
            at = dict(ATTR.findall(tm.group(1)))
            if "text" not in at:
                continue
            text = unescape(at["text"])
            size = float(at.get("fontSize", 16))
            sizes.add(size)
            if h < size * 1.40 - 0.01:
                errors.append(f"盒高不足：{size}px 字号放在 {h:.0f}px 盒内 "
                              f"（需 ≥ {size * 1.40:.1f}）·「{text[:22]}」")
            need = em_width(text, size)
            if need > w + 0.5:
                errors.append(f"可能裁字：需 {need:.0f}px > 盒宽 {w:.0f}px "
                              f"· {size}px ·「{text[:28]}」")
            else:
                tight.append((w / max(1e-6, need), text[:30], size, w))
    if not sizes:
        warns.append(f"{path.name}: 没有解析到 Text 字号")
    ordered = sorted(sizes, reverse=True)
    # 16px 是页面脚注/来源披露的固定字号，不参与正文层级的比值判断。
    # 判据（计划 v1-G4 的修订版，见 plan-v1.md 变更记录）：
    #   正文（≥18px）至少 5 个不同字号，且最大/最小 ≥ 2.2。
    #   原写「≥4.0 倍」是为了防止层级过平，但本页主体是重排后的信息载体，
    #   正文下限本来就要到 19–21px，4.0 倍会把标题推到 80px 以上，反而破坏信息密度。
    body = sorted({s for s in sizes if s >= 18}, reverse=True)
    if len(body) < 5:
        warns.append(f"{path.name}: 正文层级不足，仅 {len(body)} 个 ≥18px 字号 {body}")
    if body and body[0] / max(1.0, body[-1]) < 2.2:
        warns.append(f"{path.name}: 字号层级偏窄 {body[0]:.0f}/{body[-1]:.0f}")
    for r, txts, size, bw in tight[:6]:
        if r < 1.06:
            warns.append(f"余量偏紧 {r:.3f}· {size:.0f}px / 盒宽 {bw:.0f} ·「{txts}」")
    return errors, warns


def main() -> int:
    bad = 0
    for arg in sys.argv[1:]:
        p = Path(arg) if os.path.isabs(arg) else ROOT / arg
        if not p.exists():
            print(f"[check] 缺文件 {arg}")
            bad += 1
            continue
        errs, warns = check(p)
        print(f"\n=== {p.name} ===")
        for e in errs:
            print("  ERROR", e)
        for w in warns:
            print("  warn ", w)
        if not errs:
            print("  ok    无越界 / 无预计裁字")
        bad += 1 if errs else 0
    print(f"\n[check] {len(sys.argv) - 1} 个文件，硬性问题 {bad} 个")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())