# -*- coding: utf-8 -*-
"""Write B01's gallery.html: local relative links, clickable full-size,
no remote script, indexing all ten cases."""
from __future__ import annotations

import io
import json
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B01")

port = json.load(io.open(os.path.join(OUT, "portfolio.json"), encoding="utf-8"))
CS = port["cases"]

# a thumbnail needs a scaled copy; the originals must stay byte-identical to the
# service response, so the scaled copies live in this directory and are labelled
# as contact-sheet derivatives
THUMBS = os.path.join(OUT, "_thumbs")
os.makedirs(THUMBS, exist_ok=True)
try:
    from PIL import Image
    for c in CS:
        src = os.path.join(OUT, c["id"], "final.png")
        im = Image.open(src).convert("RGB")
        im.thumbnail((720, 720), Image.LANCZOS)
        im.save(os.path.join(THUMBS, c["id"] + ".jpg"), quality=88)
    HAVE_THUMBS = True
except Exception as e:  # noqa: BLE001
    print("thumbnail generation failed, falling back to direct images:", e)
    HAVE_THUMBS = False

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#0d0f13;color:#e8ebf0;
 font:15px/1.7 "Inter","Noto Sans CJK SC",system-ui,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:48px 28px 80px}
h1{font-size:30px;letter-spacing:.02em;margin:0 0 6px}
.sub{color:#8b94a3;margin:0 0 8px}
.statement{background:#141821;border:1px solid #232a35;border-left:3px solid #4f8ef7;
 border-radius:8px;padding:16px 20px;color:#b9c2d0;margin:28px 0 40px}
.statement b{color:#e8ebf0;font-weight:600}
.disc{color:#7d8695;font-size:13px;border-top:1px solid #1e242e;padding-top:14px;
 margin-top:26px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));
 gap:26px}
figure{margin:0;background:#141821;border:1px solid #232a35;border-radius:10px;
 overflow:hidden;display:flex;flex-direction:column}
figure a.sheet{display:block;background:#0b0d11;line-height:0;
 border-bottom:1px solid #232a35}
figure img{width:100%;height:auto;display:block}
figcaption{padding:14px 16px 16px;flex:1;display:flex;flex-direction:column}
.id{font-size:11px;letter-spacing:.16em;color:#5f6b7d;text-transform:uppercase}
.tt{font-size:16px;font-weight:600;margin:4px 0 2px;color:#eef1f6}
.meta{font-size:12px;color:#7d8695;margin-bottom:10px}
.goal{font-size:13px;color:#aab3c1;margin:0 0 12px}
.sig{font-size:13px;color:#9fb4cf;border-left:2px solid #2f4a6b;padding-left:10px;
 margin:0 0 12px}
.why{font-size:13px;color:#98a1b0;margin:0 0 14px}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:auto;padding-top:10px}
.tag{font-size:11px;color:#8fa3bd;background:#1b2330;border:1px solid #27303e;
 border-radius:4px;padding:2px 7px}
.links{margin-top:12px;padding-top:10px;border-top:1px solid #1e242e;
 font-size:12px}
.links a{color:#6fa8f0;text-decoration:none;margin-right:14px}
.links a:hover{text-decoration:underline}
footer{margin-top:56px;color:#6b7484;font-size:13px;border-top:1px solid #1e242e;
 padding-top:20px}
footer code{background:#151a22;padding:1px 5px;border-radius:3px;color:#93a4b8}
"""

rows = []
for c in CS:
    img = ("_thumbs/%s.jpg" % c["id"]) if HAVE_THUMBS else (c["png"])
    rows.append("""    <figure>
      <a class="sheet" href="{png}" target="_blank" rel="noopener">
        <img src="{img}" alt="{tt} — {w}×{h} 用例成品图" loading="lazy">
      </a>
      <figcaption>
        <div class="id">{cid}</div>
        <div class="tt">{tt}</div>
        <div class="meta">{w} × {h} · {kb} KB · DSL {n} 元素（上限的 {pct}%） · {kind}</div>
        <p class="goal"><b>用户要完成的事</b>：{goal}</p>
        <p class="sig"><b>最有辨识度的视觉选择</b>：{sig}</p>
        <p class="why">{why}</p>
        <div class="links">
          <a href="{png}" target="_blank" rel="noopener">原尺寸 PNG</a>
          <a href="{snap}" target="_blank" rel="noopener">完整 DSL</a>
          <a href="{md}">case.md</a>
        </div>
        <div class="tags">
          <span class="tag">纯 DSL 主体</span>
          <span class="tag">无 &lt;Image&gt;</span>
          <span class="tag">无外部素材</span>
          <span class="tag">示例数据自拟</span>
        </div>
      </figcaption>
    </figure>""".format(
        cid=c["id"], tt=c["title"], w=c["dimensions"][0], h=c["dimensions"][1],
        kb=round(c["png_bytes"] / 1024), n=c["dsl_element_count"],
        pct=c["dsl_element_limit_used_percent"], kind=c["use_context"],
        goal=c["user_goal"], sig=c["visual_intent"], why=c["curatorial_reason"],
        img=img, png=c["png"], snap=c["snapshot"], md="%s/case.md" % c["id"]))

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B01 · 十张真实场景的炫酷用例 — 作品画廊</title>
<style>%s</style>
</head>
<body>
<div class="wrap">
  <h1>B01 · 十张真实场景的炫酷用例</h1>
  <p class="sub">Snapshot DSL · run %s · 10 件独立完整用例 · 全部为服务真实渲染的原始响应字节</p>

  <div class="statement">
    <b>策展说明</b>：%s
  </div>

  <div class="disc"><b>素材与数据声明</b>：%s</div>

  <div class="grid">
%s
  </div>

  <footer>
    <p>本页面使用相对路径，可直接用浏览器本地打开（<code>file://</code>），不加载任何远程脚本、字体或样式。</p>
    <p>缩略图位于 <code>_thumbs/</code>，是从 <code>final.png</code> 等比缩小后的展示副本；点击缩略图打开的是<strong>未经任何处理的原始 PNG</strong>，与 <code>final.snapshot</code> 一一配对。</p>
    <p>同目录另交付 <code>portfolio.json</code>（逐件映射与自定完成标准）、<code>portfolio.md</code>（策展逻辑）、<code>snapshot-usage.md</code>（文档应用、逐件自检、问题修复表）、<code>task-metrics.json</code>（请求/迭代/耗时与消耗记录）。</p>
  </footer>
</div>
</body>
</html>
""" % (CSS, RUN, port["curatorial_statement"], port["brand_disclaimer"], "\n".join(rows))

io.open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8",
        newline="\n").write(HTML)
print("gallery.html written,", len(HTML), "bytes; thumbs:", HAVE_THUMBS)