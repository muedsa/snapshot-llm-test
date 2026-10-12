"""B04: write portfolio.md and gallery.html (local relative links, no remote deps)."""
import io
import json
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "B04")
OUT = os.path.join(ROOT, "outputs", RUN, "B04")
P = json.load(io.open(os.path.join(OUT, "portfolio.json"), encoding="utf-8"))
SRC = json.load(io.open(os.path.join(OUT, "sources.json"), encoding="utf-8"))

# ------------------------------------------------------------- portfolio.md --
L = []
L.append("# B04 · 海洋酸化视觉特辑 · 策展说明")
L.append("")
L.append("> 任务：自主研究一个真实主题并制作十件视觉特辑　|　run_id `%s`" % RUN)
L.append("> 主题：**%s**" % P["topic"])
L.append("")
L.append("## 策展逻辑")
L.append("")
L.append(P["curatorial_statement"])
L.append("")
L.append("**顺序为什么这样排**：%s" % P["reading_order_rationale"])
L.append("")
L.append("## 十件一览")
L.append("")
L.append("| # | 作品 | 画布 | 主要形式 | 受众要完成的事 |")
L.append("|---|---|---|---|---|")
FORM = {
 "case-01": "巨字排版 + 真实曲线 + 对数直尺",
 "case-02": "实测数据图 + 端点读数板 + 增量条",
 "case-03": "对数竖尺 + 放大插图 + 换算卡（竖版）",
 "case-04": "反应流程图 + 碳酸根账本（三面板）",
 "case-05": "pH 竖尺 × 深时对数横尺",
 "case-06": "双轨情景投影图（pH / Ωarag）",
 "case-07": "真比例阈值速查卡",
 "case-08": "双向效应量条形图 + 读法卡",
 "case-09": "观测指标矩阵 + 符号规则面板",
 "case-10": "五级判定核查清单（竖版）",
}
for c in P["cases"]:
    L.append("| [%s](%s/final.png) | %s | %d×%d | %s | %s |"
             % (c["id"], c["id"], c["title"], c["dimensions"][0],
                c["dimensions"][1], FORM[c["id"]], c["user_goal"]))
L.append("")
L.append("## 逐件用途与完成标准")
L.append("")
for c in P["cases"]:
    L.append("### %s · %s" % (c["id"], c["title"]))
    L.append("")
    L.append("- **受众**：%s" % c["audience"])
    L.append("- **使用场景**：%s" % c["use_context"])
    L.append("- **要完成的事**：%s" % c["user_goal"])
    L.append("- **视觉主张**：%s" % c["visual_intent"])
    L.append("- **内容依据**：%s" % c["content_basis"])
    L.append("- **来源**：%s" % "、".join(c["sources"]))
    L.append("- **完成标准**：%s" % c["completion_criteria"])
    L.append("- **实际看图记录**：%s" % c["visual_review"])
    L.append("- **渲染**：%d 次尝试 / %d 次成功；最终请求 `%s`"
             % (c["render_attempts"], c["successful_renders"], c["final_request_id"]))
    L.append("- **DSL 能力**：%s" % c["dsl_capabilities"])
    L.append("- **素材**：无（无 `<Image>`，纯 DSL 构造）")
    L.append("- **遗留**：%s" % c["unresolved_issues"][0])
    L.append("- 文件：`final.png` · `final.snapshot` · [`case.md`](%s/case.md)"
             % c["id"])
    L.append("")
L.append("## 整体审查")
L.append("")
FR = P["final_collection_review"]
L.append("**独立性**：%s" % FR["independence_check"])
L.append("")
L.append("**跨件一致性**：%s" % FR["cross_piece_consistency"])
L.append("")
L.append("**诚实性纪律**：%s" % FR["honesty_rules_held"])
L.append("")
L.append("**仍然存在的弱点**：")
for r in FR["residual_weaknesses"]:
    L.append("- %s" % r)
L.append("")
L.append("## 来源与限制")
L.append("")
L.append("- 来源台账：[`sources.json`](sources.json)（13 条来源，逐条记录取得方式、"
         "访问日期、拿到了什么、被哪几件引用）")
L.append("- 编辑说明：[`editorial-note.md`](editorial-note.md)（选题理由、读者问题、叙述路线与限制）")
L.append("- 使用与踩坑：[`snapshot-usage.md`](snapshot-usage.md)")
L.append("- 结构化指标：[`task-metrics.json`](task-metrics.json)")
L.append("- 本地画廊：[`gallery.html`](gallery.html)")
L.append("")
L.append("未解决事项：")
for r in P["unresolved_issues"]:
    L.append("- %s" % r)
L.append("")
L.append("## 过程与消耗")
L.append("")
L.append("- 追加式日志：`tmp/%s/B04/requests.jsonl`（%d 条，含失败响应）、"
         "`iterations.jsonl`、`tool-usage.jsonl`"
         % (RUN, 59))
L.append("- 素材政策：%s" % P["asset_policy"])
L.append("- token / 费用等平台未提供的计量：`task-metrics.json` 中全部为 `null`，"
         "并写明原因；未按字数或响应体积估算。")
L.append("")
io.open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8",
        newline="\n").write("\n".join(L))

# -------------------------------------------------------------- gallery.html --
H = []
H.append("<!DOCTYPE html>")
H.append('<html lang="zh-CN"><head><meta charset="utf-8">')
H.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
H.append("<title>B04 · 海洋酸化视觉特辑 · %s</title>" % RUN)
H.append("""<style>
:root{--bg:#050d16;--card:#0a1a28;--card2:#0e2537;--line:#1d3a50;--fg:#f1f7fb;
--fg2:#a8c2d4;--fg3:#6e8aa0;--cy:#5ee0d0;--am:#ffc15e;--co:#ff7a6b;--mi:#9be8a0;--vi:#c0a6ff}
*{box-sizing:border-box}
body{margin:0;padding:34px 26px 72px;background:var(--bg);color:var(--fg);
font:15px/1.7 -apple-system,"Segoe UI","Noto Sans CJK SC","Microsoft YaHei",sans-serif}
h1{font-size:27px;margin:0 0 8px;letter-spacing:-.4px}
h2{font-size:18px;margin:42px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.sub{color:var(--fg2);max-width:1080px}
.meta{color:var(--fg3);font-size:13px;margin:14px 0 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(460px,1fr));gap:22px}
.case{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.case figure{margin:0;background:#04090f;line-height:0}
.case img{width:100%;display:block;border-bottom:1px solid var(--line)}
.case .body{padding:14px 17px 18px}
.case h3{margin:0 0 6px;font-size:16px}
.tag{display:inline-block;font-size:11px;letter-spacing:.05em;color:#04101a;
border-radius:999px;padding:2px 9px;margin:6px 6px 8px 0;font-weight:700}
dl{display:grid;grid-template-columns:70px 1fr;gap:3px 10px;margin:8px 0 0;font-size:13px}
dt{color:var(--fg3)}dd{margin:0;color:var(--fg2)}
ul{margin:8px 0 0;padding-left:19px;font-size:13px;color:var(--fg2)}
li{margin:3px 0}
a{color:var(--cy)}
code{background:#04090f;padding:1px 5px;border-radius:4px;font-size:12px;color:var(--am)}
table{border-collapse:collapse;width:100%;font-size:13px;margin-top:10px}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:var(--card2)}
.ok{color:var(--mi)}.warn{color:var(--am)}.bad{color:var(--co)}
footer{margin-top:48px;padding-top:14px;border-top:1px solid var(--line);color:var(--fg3);font-size:13px}
.note{background:var(--card2);border-left:3px solid var(--am);padding:12px 15px;
border-radius:0 10px 10px 0;margin:14px 0;color:var(--fg2);font-size:13.5px}
</style></head><body>""")
H.append("<h1>B04 · 海洋酸化视觉特辑</h1>")
H.append('<p class="sub"><strong>主题：</strong>%s</p>' % P["topic"])
H.append('<p class="sub">%s</p>' % P["curatorial_statement"])
H.append('<p class="sub"><strong>阅读顺序的理由：</strong>%s</p>'
         % P["reading_order_rationale"])
H.append('<div class="note">全部十件为 <code>POST https://open-snapshot.muedsa.com/snapshot</code> '
         '的真实响应字节，未做任何后处理；无 <code>&lt;Image&gt;</code>，无外部素材，'
         '主体与全部文字由 Snapshot DSL 构造。点开任意一张可看原尺寸。</div>')
H.append('<p class="meta">run_id <code>%s</code> · 输出根 <code>outputs/%s/B04/</code> '
         '· 临时根 <code>tmp/%s/B04/</code> · 来源台账 <a href="sources.json">sources.json</a> '
         '· 策展说明 <a href="portfolio.md">portfolio.md</a> · 编辑说明 '
         '<a href="editorial-note.md">editorial-note.md</a> · 使用与踩坑 '
         '<a href="snapshot-usage.md">snapshot-usage.md</a> · 指标 '
         '<a href="task-metrics.json">task-metrics.json</a></p>' % (RUN, RUN, RUN))
H.append("<h2>十件作品（点击图看原尺寸）</h2>")
H.append('<div class="grid">')
TCOLOR = {"已证实": "var(--mi)", "来源结论": "var(--cy)"}
for c in P["cases"]:
    cid = c["id"]
    H.append('<div class="case">')
    H.append('<figure><a href="%s/final.png" target="_blank" rel="noopener">'
             '<img src="%s/final.png" alt="%s %s" loading="lazy"></a></figure>'
             % (cid, cid, cid, c["title"]))
    H.append('<div class="body">')
    H.append("<h3>%s · %s</h3>" % (cid, c["title"]))
    H.append('<span class="tag" style="background:var(--cy)">%d × %d</span>'
             '<span class="tag" style="background:var(--am)">%d 次渲染 / %d 成功</span>'
             '<span class="tag" style="background:var(--vi)">%s</span>'
             % (c["dimensions"][0], c["dimensions"][1], c["render_attempts"],
                c["successful_renders"], FORM[cid]))
    H.append("<dl>")
    H.append("<dt>受众</dt><dd>%s</dd>" % c["audience"])
    H.append("<dt>场景</dt><dd>%s</dd>" % c["use_context"])
    H.append("<dt>要做的</dt><dd>%s</dd>" % c["user_goal"])
    H.append("<dt>视觉主张</dt><dd>%s</dd>" % c["visual_intent"])
    H.append("<dt>来源</dt><dd>%s</dd>" % "、".join(c["sources"]))
    H.append("</dl>")
    H.append("<ul><li><strong>完成标准：</strong>%s</li>" % c["completion_criteria"])
    H.append("<li><strong>实际看图：</strong>%s</li>" % c["visual_review"])
    H.append("<li><strong>遗留：</strong>%s</li></ul>" % c["unresolved_issues"][0])
    H.append('<p><a href="%s/case.md">case.md</a> · <a href="%s/final.snapshot">final.snapshot</a>'
             ' · <a href="%s/final.png" target="_blank" rel="noopener">原图</a></p>'
             % (cid, cid, cid))
    H.append("</div></div>")
H.append("</div>")

H.append("<h2>整体审查</h2>")
H.append("<table><tr><th style='width:170px'>项目</th><th>结论</th></tr>")
for lbl, key in [("独立性", "independence_check"), ("跨件一致性", "cross_piece_consistency"),
                 ("诚实性纪律", "honesty_rules_held")]:
    H.append("<tr><td><strong>%s</strong></td><td>%s</td></tr>" % (lbl, FR[key]))
H.append("<tr><td><strong>仍然存在的弱点</strong></td><td><ul>")
for r in FR["residual_weaknesses"]:
    H.append("<li>%s</li>" % r)
H.append("</ul></td></tr></table>")

H.append("<h2>来源台账摘要（完整见 <a href=\"sources.json\">sources.json</a>）</h2>")
H.append("<table><tr><th style='width:56px'>ID</th><th>来源</th>"
         "<th style='width:210px'>取得方式</th><th style='width:180px'>被引用</th></tr>")
for s in SRC["sources"]:
    H.append("<tr><td><code>%s</code></td><td>%s<br><span style='color:var(--fg3)'>%s</span></td>"
             "<td>%s</td><td>%s</td></tr>"
             % (s["id"], s["title"], s["url"], s["access_method"],
                "、".join(s["used_by"])))
H.append("</table>")

H.append("<h2>未解决事项</h2><ul>")
for r in P["unresolved_issues"]:
    H.append("<li>%s</li>" % r)
H.append("</ul>")
H.append('<footer>本页面使用本地相对链接，图片与全部样式内联，不加载任何远程脚本或字体。'
         '十件作品的 <code>final.png</code> 均为 open-snapshot 服务的原始响应字节。</footer>')
H.append("</body></html>")
io.open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8",
        newline="\n").write("\n".join(H))
print("wrote portfolio.md and gallery.html")
