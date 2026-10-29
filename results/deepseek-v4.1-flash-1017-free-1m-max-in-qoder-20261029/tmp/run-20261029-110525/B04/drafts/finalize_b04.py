#!/usr/bin/env python3
"""Write per-case notes for B04 from meta + sources, and verify PNG pairing."""
import json, os
from pathlib import Path
from PIL import Image
SCRIPT = Path(__file__).resolve()
SUITE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN = SCRIPT.parents[2].name
OUT = SUITE / 'outputs' / RUN / 'B04'
meta = json.loads((SCRIPT.parent / 'meta.json').read_text(encoding='utf-8'))
src = json.loads((OUT / 'sources.json').read_text(encoding='utf-8'))
claims = src['claims']
reads = {
 1: "先读左栏两段，再沿右图从左到右：文本 DSL → POST /snapshot → PNG。两条灰色小字分别说明失败结构与重试边界。",
 2: "三个标签 chip 是输入；两条箭头分别落到 Element 树与 Widget 树；再汇入 RenderBox。底部一行提醒未知属性与未知标签的不同处理。",
 3: "从外到内四层矩形表示约束逐层收紧；右侧三行分别讲有界主轴、无界主轴与画布来源。",
 4: "大字 Ag 上画三条水平参考线：ascent、baseline、descent。读图时先看基线，再看字盒。",
 5: "上排是五枚颜色样板；下排渐变条从左到右为青、蓝、紫，标签写明 LINEAR 与 3 stops。",
 6: "上方三条是概念卡；下方分配条把 fixed 120 与 flex 1、flex 2 的比例画出来，剩余 280 按 1:2 分配。",
 7: "浅蓝底板就是固定画布；绿色与赭色方块按 left/top 叠放，后画的赭色在上。",
 8: "唯一的图示是旋转 30° 的方块；矩阵说明与“布局尺寸不变”的提醒在图下方。",
 9: "把同一条五色条纹并置三次：顶部原图、左侧清晰副本、右侧 ImageFiltered 副本；最下方是加密条纹上的 BackdropFilter 面板。",
 10: "深色块是失败响应示例；三行说明依次是错误分类、证据保留与重试边界。",
}
for c in meta['cases']:
    cid = c['id']
    d = OUT / f"case-{cid:02d}"
    png = d / 'final.png'
    snap = d / 'final.snapshot'
    w, h = Image.open(png).size
    assert snap.exists() and png.stat().st_size > 1024, d
    rel_claims = [cl for cl in claims if cid in cl['used_in_cases']]
    L = [f"# {cid:02d} · {c['title']}", "",
         f"- 受众：{c['audience']}",
         f"- 使用场景：{c['use_context']}",
         f"- 用户目标：{c['user_goal']}",
         f"- 内容依据：{c['content_basis']}",
         f"- 视觉意图：{c['visual_intent']}",
         f"- 主图：`final.png`（{w}×{h}，服务真实响应）",
         f"- DSL：`final.snapshot`",
         f"- DSL 能力：{'、'.join(c['dsl_capabilities'])}",
         "- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。",
         "", "## 图示读法", "", reads[cid], "", "## 依据条目", ""]
    for cl in rel_claims:
        L.append(f"- `{cl['id']}`（{cl['source']} · {cl['section']}）：{cl['statement']}")
    L += ["", "## 文件", "",
          "- [final.png](final.png)", "- [final.snapshot](final.snapshot)",
          "- [sources.json](../sources.json)", "- [editorial-note.md](../editorial-note.md)", ""]
    (d / 'case.md').write_text('\n'.join(L), encoding='utf-8')
    print(cid, w, h, len(rel_claims), 'claims')
print('finalized')
