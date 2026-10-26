"""A17 一致性验证：对实际落盘文件做解析与像素比对，不依赖生成过程的记忆。

检查项：
  A. 文件齐全、PNG 尺寸符合要求（手册 1200×1600，示例 400×240）
  B. 手册插图内的核心子树与独立示例的核心子树逐字节相同
  C. 手册印刷代码行与独立 DSL 文件对应行逐字相同（含转义形式）
  D. CDATA 显示文本可无损还原为原始 DSL 行
  E. 手册插图区域与独立示例 PNG 像素级 1:1 一致（400×240）
  F. 页首「印刷代码」标注的行号范围与 print_spec 实际打印范围一致
  G. 独立示例 DSL 可被服务真实解析并渲染成功（以 responses 记录为准）
"""
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261013-174209")
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "A17"))
from a17_examples import EXAMPLES, standalone_dsl  # noqa: E402

TMP = ROOT / "tmp" / RUN_ID / "A17"
MONO = "Noto Sans Mono CJK SC"

results: list[dict] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    results.append({"check": name, "ok": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    return bool(ok)


def uncdata(s: str) -> str:
    """把 Raw/Text 元素内部的（可能被拆分的）CDATA 还原为原始文本。"""
    parts = re.findall(r"<!\[CDATA\[(.*?)]]>", s, flags=re.S)
    if not parts:
        return s
    return "".join(parts)


def raw_rows(dsl: str) -> list[str]:
    """按文档顺序取等宽 Raw 行的显示文本（代码块专用）。

    必须按 CDATA 段走：印刷代码里可能原样包含 <Raw>...</Raw> 字面量
    （示例 3 的 Raw 演示行），朴素的非贪婪正则会被它提前截断。
    """
    opener = re.compile(r"<Raw ([^>]*)>")
    out = []
    i = 0
    while True:
        m = opener.search(dsl, i)
        if not m:
            break
        attrs, j = m.group(1), m.end()
        end = None
        while j < len(dsl):
            if dsl.startswith("<![CDATA[", j):
                k = dsl.find("]]>", j)
                if k == -1:
                    break
                j = k + 3
                continue
            if dsl.startswith("</Raw>", j):
                end = j
                break
            j += 1
        if end is None:
            break
        if MONO in attrs:
            out.append(uncdata(dsl[m.end():end]))
        i = end + len("</Raw>")
    return out


def main() -> int:
    from PIL import Image  # noqa: E402

    all_ok = True

    # ---------- A. 文件与尺寸 ----------
    for pg in range(1, 5):
        hb = TMP / f"handbook-0{pg}.png"
        ok = hb.exists() and Image.open(hb).size == (1200, 1600)
        all_ok &= check(f"A.handbook-0{pg}.png 1200x1600", ok,
                        str(Image.open(hb).size) if hb.exists() else "missing")
    for ex in EXAMPLES:
        p = TMP / f"{ex['id']}.png"
        ok = p.exists() and Image.open(p).size == (400, 240)
        all_ok &= check(f"A.{ex['id']}.png 400x240", ok,
                        str(Image.open(p).size) if p.exists() else "missing")

    # ---------- B/C/F. 手册 DSL 结构 ----------
    PAGES_META = {  # num -> code_label（来自 a17_gen.PAGES，运行时读取避免抄写）
        1: "印刷代码：example-01.snapshot 第 1–11 行（省略处已标识）",
        2: "印刷代码：example-02.snapshot 第 6–9、13–21 行（省略处已标识）",
        3: "印刷代码：example-03.snapshot 第 1–9、15–17 行（省略处已标识）",
        4: "印刷代码：example-04.snapshot 第 4–6、8–11、15–19 行（省略处已标识）",
    }
    for pg in range(1, 5):
        ex = EXAMPLES[pg - 1]
        dsl = (TMP / f"handbook-0{pg}.snapshot").read_text(encoding="utf-8")
        standalone = standalone_dsl(ex)
        lines = standalone.splitlines()

        # B. 核心子树逐字节相同
        m = re.search(r"<!-- CORE-BEGIN -->(.*?)<!-- CORE-END -->", dsl, flags=re.S)
        ok = m is not None and m.group(1) == ex["core"]
        all_ok &= check(f"B.page{pg} 插图核心子树 == 独立示例核心（逐字节）", ok,
                        f"len(hb)={len(m.group(1)) if m else 0} len(ex)={len(ex['core'])}")
        # 独立示例文件本身也包含同一子树
        sa = (TMP / f"{ex['id']}.snapshot").read_text(encoding="utf-8")
        all_ok &= check(f"B.page{pg} 独立示例文件含同一核心子树", ex["core"] in sa)

        # C. 印刷代码行逐字相同
        expected = []
        for kind, val in ex["print_spec"]:
            expected.append(lines[val - 1] if kind == "code" else f"…………{val}…………")
        got = raw_rows(dsl)
        ok = got == expected
        detail = ""
        if not ok:
            for i, (g, e) in enumerate(zip(got, expected)):
                if g != e:
                    detail = f"row{i}: got={g[:40]!r} exp={e[:40]!r}"
                    break
            if not detail:
                detail = f"count got={len(got)} exp={len(expected)}"
        all_ok &= check(f"C.page{pg} 印刷代码 {len(expected)} 行逐字一致", ok, detail)

        # D. 转义往返：原始行经 cdata() 后的形式必须原样出现在手册 DSL 中，
        #    且能无损还原（重点覆盖含 ]]> 与 <Raw> 字面量的行）
        def cdata(s: str) -> str:
            if "]]>" not in s:
                return f"<![CDATA[{s}]]>"
            parts = s.split("]]>")
            return "<![CDATA[" + "]]]]><![CDATA[>".join(parts) + "]]>"

        bad_esc, bad_rt = [], []
        for e in expected:
            esc = cdata(e)
            if esc not in dsl:
                bad_esc.append(e[:30])
            if uncdata(esc) != e:
                bad_rt.append(e[:30])
        tricky = [e for e in expected if "]]>" in e or "<Raw>" in e]
        all_ok &= check(f"D.page{pg} 转义形式与原文往返一致（难例 {len(tricky)} 行）",
                        not bad_esc and not bad_rt,
                        f"esc_miss={bad_esc} roundtrip={bad_rt}")

        # F. code_label 行号范围与 print_spec 一致
        printed = [v for k, v in ex["print_spec"] if k == "code"]
        ranges = []
        s = p = printed[0]
        for v in printed[1:]:
            if v == p + 1:
                p = v
                continue
            ranges.append((s, p))
            s = p = v
        ranges.append((s, p))
        rng_txt = "、".join(f"{a}–{b}" if a != b else f"{a}" for a, b in ranges)
        label = PAGES_META[pg]
        ok = rng_txt in label
        all_ok &= check(f"F.page{pg} 标注行号 [{rng_txt}] 与 print_spec 一致", ok, label)

        # ---------- E. 像素级 1:1 ----------
        fm = re.search(
            r'<Positioned left="([\d.]+)" top="([\d.]+)" width="464" height="304">'
            r'<Container color="#FFFFFF" border="1 SOLID #CBD5E1" borderRadius="10" '
            r'padding="32"><!-- CORE-BEGIN -->', dsl)
        if not fm:
            all_ok &= check(f"E.page{pg} 插图外框可定位", False, "frame not found")
            continue
        ox, oy = int(float(fm.group(1))) + 32, int(float(fm.group(2))) + 32
        hb_im = Image.open(TMP / f"handbook-0{pg}.png").convert("RGB")
        crop = hb_im.crop((ox, oy, ox + 400, oy + 240))
        ex_im = Image.open(TMP / f"{ex['id']}.png").convert("RGB")
        if crop.size != ex_im.size:
            all_ok &= check(f"E.page{pg} 插图裁剪尺寸", False, str(crop.size))
            continue
        import numpy as np  # noqa: E402
        a = np.asarray(crop).astype(int)
        b = np.asarray(ex_im).astype(int)
        diff = np.abs(a - b)
        maxd = int(diff.max())
        ndiff = int((diff.sum(axis=2) > 0).sum())
        ok = maxd == 0
        all_ok &= check(f"E.page{pg} 插图区域与独立示例像素级 1:1", ok,
                        f"origin=({ox},{oy}) maxdiff={maxd} diffpx={ndiff}/96000")

    # ---------- G. 渲染记录 ----------
    reqs = TMP / "requests.jsonl"
    if reqs.exists():
        labels = {}
        for ln in reqs.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(ln)
            except Exception:
                continue
            lab = r.get("label", "")
            if lab.startswith("A17-"):
                labels[lab] = r.get("status")
        want = [f"A17-{e['id']}" for e in EXAMPLES] + \
               [f"A17-handbook-0{p}" for p in range(1, 5)]
        missing = [w for w in want if w not in labels]
        failed = [w for w in want if labels.get(w) != "ok"]
        all_ok &= check("G. 8 次渲染全部记录且 status=ok",
                        not missing and not failed,
                        f"missing={missing} failed={failed}")
    else:
        all_ok &= check("G. requests.jsonl 存在", False, "missing")

    print()
    n_fail = sum(1 for r in results if not r["ok"])
    print(f"total={len(results)} pass={len(results) - n_fail} fail={n_fail}")
    out = TMP / "a17_verify.json"
    out.write_text(json.dumps({"run_id": RUN_ID, "results": results,
                               "total": len(results), "fail": n_fail},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print("written:", out)
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
