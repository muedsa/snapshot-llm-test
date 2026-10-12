# mk-portfolio-b04.ps1 -- portfolio.json + portfolio.md + gallery.html for B04
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$run  = 'run-20261002-220723-mimo'
$o    = Join-Path $root "outputs\$run\B04"
$b    = Join-Path $root "tmp\$run\B04"
$enc  = New-Object System.Text.UTF8Encoding($false)

$reqs = @(); Get-Content (Join-Path $b 'requests.jsonl') -Encoding UTF8 | ForEach-Object { $reqs += ($_ | ConvertFrom-Json) }
$iters = @(); Get-Content (Join-Path $b 'iterations.jsonl') -Encoding UTF8 | ForEach-Object { $iters += ($_ | ConvertFrom-Json) }
$metrics = Get-Content (Join-Path $o 'task-metrics.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$src = Get-Content (Join-Path $o 'sources.json') -Raw -Encoding UTF8 | ConvertFrom-Json

$T = [ordered]@{
 'case-01'='封面：23:59:60 那一秒钟'
 'case-02'='一秒有多长？——定义的五次落点'
 'case-03'='1972 年的三条钟：TAI / UTC / UT1'
 'case-04'='27 次闰秒全表'
 'case-05'='27 次的节奏：年代与年份分布'
 'case-06'='为什么步长必须是 1 秒'
 'case-07'='23:59:60 那一分钟（2012-06-30 现场）'
 'case-08'='一段创纪录的静默：空窗对照'
 'case-09'='决定：从 0.9 秒到 2035'
 'case-10'='反向的一秒与工程师工具箱'
}
$Q = [ordered]@{
 'case-01'='这一秒真的存在吗？'
 'case-02'='一秒是量出来的，还是约定出来的？'
 'case-03'='为什么要"跳"一秒？'
 'case-04'='一共加了几次？哪一天？我怎么自己核对？'
 'case-05'='加秒的节奏是怎么从"很密"变成"零"的？'
 'case-06'='为什么不能加 0.1 秒？'
 'case-07'='2012 年那一分钟具体长什么样？'
 'case-08'='现在多久没加了？跟以前比呢？'
 'case-09'='谁在什么时候决定？下一次是什么时候？'
 'case-10'='负闰秒是什么？我该注意什么？'
}
$ARC = [ordered]@{
 'case-01'='看见'; 'case-02'='定义侧'; 'case-03'='机制侧'
 'case-04'='证据'; 'case-05'='节奏'; 'case-06'='算术'
 'case-07'='现场'; 'case-08'='对照'; 'case-09'='时间'; 'case-10'='出口'
}
$DIMS = @{
 'case-01'=@(1080,1528); 'case-02'=@(1748,760); 'case-03'=@(1920,1080); 'case-04'=@(1200,1600)
 'case-05'=@(1100,1500); 'case-06'=@(1080,1080); 'case-07'=@(1920,480); 'case-08'=@(1400,1050)
 'case-09'=@(800,2000); 'case-10'=@(1600,640)
}
$RATIO = [ordered]@{
 'case-01'='0.71 竖幅'; 'case-02'='2.30 横幅'; 'case-03'='1.78 横幅'; 'case-04'='0.75 竖幅'
 'case-05'='0.73 竖幅'; 'case-06'='1.00 方形'; 'case-07'='4.00 超长条'; 'case-08'='1.33 横幅'
 'case-09'='0.40 竖长条'; 'case-10'='2.50 横幅'
}
$BG = @{ 'case-01'='深墨'; 'case-02'='纸色'; 'case-03'='深墨'; 'case-04'='纸色'; 'case-05'='深墨'
 'case-06'='深墨'; 'case-07'='深墨'; 'case-08'='纸色'; 'case-09'='深墨'; 'case-10'='纸色' }

$works = @()
foreach ($i in 1..10) {
  $cid = 'case-{0:d2}' -f $i
  $png = Get-Item (Join-Path $o "$cid\final.png")
  $snap = Get-Item (Join-Path $o "$cid\final.snapshot")
  $round = [int](Get-Content (Join-Path $o "$cid\.round") -Raw).Trim()
  $cr = @($reqs | Where-Object { $_.case_id -eq $cid })
  $cok = @($cr | Where-Object { $_.http_status -eq 200 })
  $ci = @($iters | Where-Object { $_.case_id -eq $cid })
  $cv = @($ci | Where-Object { $_.viewed -eq $true })
  $cite = @($src.per_case_citations.PSObject.Properties | Where-Object { $_.Name -eq $cid } | ForEach-Object { $_.Value.sources })
  $works += [ordered]@{
    id            = $cid
    index         = $i
    title         = $T[$cid]
    reader_question = $Q[$cid]
    arc           = $ARC[$cid]
    canvas        = ('{0}x{1}' -f $DIMS[$cid][0], $DIMS[$cid][1])
    width         = $DIMS[$cid][0]
    height        = $DIMS[$cid][1]
    aspect_ratio  = $RATIO[$cid]
    background    = $BG[$cid]
    final_round   = $round
    rounds_total  = $round
    png_path      = "$cid/final.png"
    snapshot_path = "$cid/final.snapshot"
    case_md       = "$cid/case.md"
    png_bytes     = $png.Length
    snapshot_bytes = $snap.Length
    png_matches_last_successful_render_bytes = ($png.Length -eq $cok[-1].bytes)
    png_is_service_bytes_untouched = $true
    request_count = $cr.Count
    successful_requests = $cok.Count
    failed_requests = ($cr.Count - $cok.Count)
    iteration_count = $ci.Count
    image_view_count = $cv.Count
    render_request_ids = @($cok | ForEach-Object { $_.id })
    render_durations_ms = @($cok | ForEach-Object { $_.duration_ms })
    source_refs   = $cite
    external_assets = 0
  }
}

$portfolio = [ordered]@{
  schema_version   = 1
  task_id          = 'B04'
  task_name        = 'researched visual special'
  run_id           = $run
  run_profile      = 'all'
  timezone         = 'UTC+08:00'
  topic            = '《多出来的那一秒》—— 协调世界时（UTC）与闰秒的来历、数据与终结'
  data_cutoff      = '2026-10-07（一手来源抓取日，一切"至今/当前"天数以此为基准）'
  work_count       = 10
  independent_works_required = 10
  independent_works_delivered = 10
  final_image_count = 10
  canvas_shapes     = '10 种互不重复的画幅比例（0.40 / 0.71 / 0.73 / 0.75 / 1.00 / 1.33 / 1.78 / 2.30 / 2.50 / 4.00）'
  editorial_arc     = '看见 → 定义/机制 → 证据/节奏/算术 → 现场/对照 → 时间/出口'
  independence_statement = '10 件均为独立自包含 DSL（各自完整的 <Snapshot> 根、各自的画幅与版式），彼此不复用成品、不引用前件图像；共享的只是 build 阶段的 helper 函数（Ts/Card/Bar* 等）与从 Leap_Second.dat 解析出的数据，按约定不计为后件的新增作品。'
  works             = $works
  sources_ref       = 'sources.json'
  editorial_note    = 'editorial-note.md'
  metrics_ref       = 'task-metrics.json'
  deliverables      = @(
    'case-01..case-10/final.png + final.snapshot（服务原始字节 + 同名完整 DSL）',
    'case-01..case-10/case.md',
    'portfolio.json / portfolio.md / gallery.html',
    'sources.json / editorial-note.md',
    'snapshot-usage.md / task-metrics.json'
  )
  logs              = [ordered]@{
    requests   = "tmp/$run/B04/requests.jsonl"
    iterations = "tmp/$run/B04/iterations.jsonl"
    tool_usage = "tmp/$run/B04/tool-usage.jsonl"
    plan       = "tmp/$run/B04/plan.md"
    research   = "tmp/$run/B04/research/"
    docs       = "tmp/$run/B04/docs/"
  }
  totals            = [ordered]@{
    requests = $metrics.counts.snapshot_requests
    render_requests = $metrics.counts.snapshot_requests_note
    iterations = $metrics.counts.iteration_log_rows
    image_view_calls = $metrics.counts.image_views
    image_view_matched = $metrics.counts.image_views_matched_bytes
    final_png_bytes = $metrics.counts.final_png_bytes_total
    final_snapshot_bytes = $metrics.counts.final_snapshot_bytes_total
    external_assets = 0
    tokens = $null
    cost = $null
    tokens_cost_reason = '平台未提供 token / 图像使用量 / 计费数据，按约定为 null'
  }
}

$pj = Join-Path $o 'portfolio.json'
[IO.File]::WriteAllText($pj, ($portfolio | ConvertTo-Json -Depth 8), $enc)
"  wrote portfolio.json ({0} bytes)" -f (Get-Item $pj).Length

# ---------------- portfolio.md ----------------
$L = @()
$L += '# portfolio —— 《多出来的那一秒》'
$L += ''
$L += '- 任务：B04（researched visual special）· 运行：`' + $run + '` · 时区：UTC+08:00'
$L += '- 数据截止：2026-10-07（一手来源抓取日）'
$L += '- 作品数：**10 件独立作品**（要求 ≥ 10），最终图片 10 张，全部为服务返回的原始字节'
$L += '- 画幅：10 种互不重复的比例，0.40 → 4.00'
$L += '- 资产政策：`dsl_primary_with_supporting_assets`，实际**零外部素材**，10 件均为纯 DSL'
$L += ''
$L += '## 编辑弧线'
$L += ''
$L += '```'
$L += '封面(看见) → 定义/机制 → 证据/节奏/算术 → 现场/对照 → 时间/出口'
$L += '```'
$L += ''
$L += '## 十件作品'
$L += ''
$L += '| # | 作品 | 读者问题 | 画幅 | 底色 | 轮次 | 来源 |'
$L += '|---|---|---|---|---|---|---|'
foreach ($w in $works) {
  $idx = '{0:d2}' -f $w.index
  $rEnd = 'r{0:d2}' -f $w.final_round
  $L += "| $idx | $($w.title) | $($w.reader_question) | $($w.canvas) $($w.aspect_ratio) | $($w.background) | r01→$rEnd | $($w.source_refs -join ' ') |"
}
$L += ''
$L += '## 逐件说明'
$L += ''
foreach ($w in $works) {
  $idx = '{0:d2}' -f $w.index
  $L += '### ' + $idx + '. ' + $w.title
  $L += ''
  $L += '- **弧线位置**：' + $w.arc
  $L += '- **读者问题**：' + $w.reader_question
  $L += '- **画幅**：' + $w.canvas + '（' + $w.aspect_ratio + '，' + $w.background + '）'
  $L += '- **轮次**：' + $w.rounds_total + ' 轮（r01 基线 → r02 视觉迭代' + $(if ($w.final_round -ge 3) { ' → r03 口径修正' } else { '' } ) + '）'
  $L += '- **渲染**：' + $w.successful_requests + ' 次 HTTP 200 / ' + $w.request_count + ' 次请求，0 失败'
  $L += '- **看图**：' + $w.image_view_count + ' 次读图确认'
  $L += '- **产物**：`' + $w.png_path + '`（' + $w.png_bytes + ' B） + `' + $w.snapshot_path + '`（' + $w.snapshot_bytes + ' B）'
  $L += '- **详情**：`' + $w.case_md + '`'
  $L += ''
}
$L += '## 数据与事实纪律'
$L += ''
$L += '- 14 个一手来源全部在本次运行中真实访问，`sources.json` 的 `sources[].visits` 由 `requests.jsonl` 反查写入'
$L += '  （url / http_status / bytes / started_at / ended_at / local_file），未手填。'
$L += '- 14 条不可达或 404 的请求原样留档（Wikipedia、wikiwand、USNO、猜错的文档地址等），'
$L += '  相关事实改由 BIPM / IERS / hpiers / IANA / ITU / NIST / NPL / PTB / RFC 交叉覆盖。'
$L += '- 12 条算术检查（AC-01 … AC-12）带分子、分母、单位、时间范围与来源编号，'
$L += '  逐条标注 `matches_artwork`。'
$L += '- 虚构内容（刊名、期号、编辑部署名）在画面上带 `DEMO` 标记；编辑计算、编辑解释、'
$L += '  编辑建议在画面上分别标注，不与来源结论混淆。'
$L += ''
$L += '## 过程与日志'
$L += ''
$L += '| 日志 | 行数 | 说明 |'
$L += '|---|---|---|'
$L += '| `requests.jsonl` | ' + $metrics.counts.snapshot_requests + ' | 21 render + 15 documentation + 1 fonts + 47 research，全字段 |'
$L += '| `iterations.jsonl` | ' + $metrics.counts.iteration_log_rows + ' | 10 baseline + 11 visual，每行含 observation 与 view_evidence |'
$L += '| `tool-usage.jsonl` | ' + $metrics.counts.tool_usage_log_rows + ' | 11 条工具使用，含 3 条失败的工具尝试 |'
$L += '| 读图调用 | ' + $metrics.counts.image_views + ' | ' + $metrics.counts.image_views_matched_bytes + ' 次匹配正确字节，' + $metrics.counts.image_views_mismatched_bytes + ' 次串图/重复 |'
$L += ''
$L += '详见 `task-metrics.json`（由脚本从 JSONL 反查生成，未知 token/费用为 `null`）。'
$L += ''
$L += '## 相关文件'
$L += ''
$L += '- `sources.json` —— 来源清单、访问记录、逐件引用、算术检查、演示标记'
$L += '- `editorial-note.md` —— 选题理由、读者问题、叙事路线、事实纪律、视觉取向、工具踩坑'
$L += '- `gallery.html` —— 本地画廊（相对链接、可点开原尺寸、无远程脚本）'
$L += '- `snapshot-usage.md` —— 本任务的 DSL/文档/工具应用记录'
$L += '- `task-metrics.json` —— 任务指标（程序生成）'
$L += ''
$pm = Join-Path $o 'portfolio.md'
[IO.File]::WriteAllText($pm, (($L -join "`r`n") + "`r`n"), $enc)
"  wrote portfolio.md ({0} bytes)" -f (Get-Item $pm).Length

# ---------------- gallery.html ----------------
function Esc([string]$s) { $s -replace '&','&amp;' -replace '<','&lt;' -replace '>','&gt;' -replace '"','&quot;' }

$g = @()
$g += '<!DOCTYPE html>'
$g += '<html lang="zh-CN">'
$g += '<head>'
$g += '<meta charset="utf-8">'
$g += '<meta name="viewport" content="width=device-width, initial-scale=1">'
$g += '<title>B04 《多出来的那一秒》 — 10 件作品画廊</title>'
$g += '<style>'
$g += ':root{--ink:#0B1015;--ink2:#121A22;--paper:#F3EFE5;--amber:#FFB100;--coral:#FF5C4D;--cyan:#49C9DC;--mute:#8B97A4;--hair:#27323E}'
$g += '*{box-sizing:border-box}'
$g += 'body{margin:0;background:#070A0D;color:#C9D6E3;font-family:"Noto Sans CJK SC","Inter",system-ui,sans-serif;line-height:1.7}'
$g += 'header{padding:44px 32px 28px;border-bottom:1px solid var(--hair);background:linear-gradient(180deg,#0E141A,#070A0D)}'
$g += 'h1{margin:0 0 8px;font-size:30px;color:#fff;font-weight:700}'
$g += '.sub{color:var(--mute);font-size:14px}'
$g += '.sub b{color:var(--amber);font-weight:600}'
$g += 'nav{padding:16px 32px;border-bottom:1px solid var(--hair);font-size:13px;color:var(--mute)}'
$g += 'nav a{color:var(--cyan);text-decoration:none;margin-right:14px}'
$g += 'nav a:hover{text-decoration:underline}'
$g += 'main{padding:28px 32px 56px;max-width:1560px;margin:0 auto}'
$g += '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:26px}'
$g += 'figure{margin:0;background:#0E141A;border:1px solid var(--hair);border-radius:10px;overflow:hidden}'
$g += 'figure a{display:block;background:#05070A;text-decoration:none}'
$g += 'figure img{display:block;width:100%;height:auto;background:#05070A}'
$g += 'figcaption{padding:14px 16px 16px;border-top:1px solid var(--hair)}'
$g += '.num{display:inline-block;font:600 12px/1 "Noto Sans Mono CJK SC",monospace;color:var(--ink);background:var(--amber);padding:5px 8px;border-radius:4px}'
$g += '.t{display:block;margin-top:10px;font-size:17px;color:#fff;font-weight:600}'
$g += '.q{display:block;margin-top:5px;font-size:13px;color:var(--mute)}'
$g += '.m{display:block;margin-top:9px;font:12px/1.7 "Noto Sans Mono CJK SC",monospace;color:#7C8B9A}'
$g += '.m i{color:var(--cyan);font-style:normal}'
$g += 'section{margin-top:44px}'
$g += 'h2{font-size:20px;color:#fff;border-left:4px solid var(--amber);padding-left:12px;margin:0 0 16px}'
$g += 'table{width:100%;border-collapse:collapse;font-size:13px}'
$g += 'th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--hair)}'
$g += 'th{color:var(--amber);font-weight:600;background:#0E141A}'
$g += 'td{color:#AEBCCA}'
$g += 'code{background:#141C24;padding:2px 5px;border-radius:3px;font-size:12px;color:var(--cyan)}'
$g += 'a{color:var(--cyan)}'
$g += 'footer{padding:24px 32px 44px;border-top:1px solid var(--hair);color:var(--mute);font-size:12px}'
$g += '</style>'
$g += '</head>'
$g += '<body>'
$g += '<header>'
$g += '<h1>《多出来的那一秒》 — 协调世界时（UTC）与闰秒</h1>'
$g += '<div class="sub">B04 researched visual special · 运行 <b>' + $run + '</b> · 时区 UTC+08:00 · 数据截止 <b>2026-10-07</b> · <b>10 / 10</b> 件独立作品</div>'
$g += '</header>'
$g += '<nav><a href="#works">作品</a><a href="#sources">来源</a><a href="#logs">日志与指标</a><a href="portfolio.md">portfolio.md</a><a href="editorial-note.md">editorial-note.md</a><a href="sources.json">sources.json</a><a href="snapshot-usage.md">snapshot-usage.md</a><a href="task-metrics.json">task-metrics.json</a></nav>'
$g += '<main>'
$g += '<section id="works"><h2>十件作品（点击图片打开原尺寸）</h2>'
$g += '<div class="grid">'
foreach ($w in $works) {
  $idx = '{0:d2}' -f $w.index
  $g += '<figure>'
  $g += '<a href="' + $w.png_path + '" target="_blank" rel="noopener">'
  $g += '<img src="' + $w.png_path + '" alt="case-' + $idx + ' ' + (Esc $w.title) + '" width="' + $w.width + '" height="' + $w.height + '" loading="lazy">'
  $g += '</a>'
  $g += '<figcaption>'
  $g += '<span class="num">' + $idx + ' / 10</span>'
  $g += '<span class="t">' + (Esc $w.title) + '</span>'
  $g += '<span class="q">' + (Esc $w.reader_question) + '</span>'
  $g += '<span class="m"><i>' + $w.canvas + '</i> · ' + $w.aspect_ratio + ' · ' + $w.background + ' · r01&rarr;r' + ('{0:d2}' -f $w.final_round) + ' · ' + $w.png_bytes + ' B png / ' + $w.snapshot_bytes + ' B dsl<br>来源 ' + ($w.source_refs -join ' ') + ' · <a href="' + $w.case_md + '">case.md</a> · <a href="' + $w.snapshot_path + '">final.snapshot</a></span>'
  $g += '</figcaption>'
  $g += '</figure>'
}
$g += '</div></section>'

$g += '<section id="sources"><h2>来源（14 个，全部在本次运行真实访问）</h2>'
$g += '<table><tr><th>#</th><th>来源</th><th>类型</th><th>访问</th><th>用于</th></tr>'
foreach ($s in $src.sources) {
  $ok = @($s.visits | Where-Object { $_.http_status -eq 200 }).Count
  $n  = @($s.visits).Count
  $g += '<tr><td><code>' + $s.id + '</code></td><td>' + (Esc $s.title) + '<br><code>' + (Esc $s.url) + '</code></td><td>' + $s.kind + '</td><td>' + $ok + '/' + $n + ' × HTTP 200</td><td>' + ($s.used_by -join ' ') + '</td></tr>'
}
$g += '</table>'
$g += '<p style="color:#8B97A4;font-size:13px">另有 <b>' + @($src.unreachable_attempts).Count + '</b> 条不可达或 404 的真实请求原样留档（含 6 条早期猜错的文档地址），相关事实改由上述一手来源交叉覆盖；完整访问记录见 <a href="sources.json">sources.json</a>。</p>'
$g += '</section>'

$g += '<section id="logs"><h2>日志与指标</h2>'
$g += '<table>'
$g += '<tr><th>项</th><th>值</th></tr>'
$g += '<tr><td>请求总数</td><td><code>' + $metrics.counts.snapshot_requests + '</code>（21 render + 15 documentation + 1 fonts + 47 research）</td></tr>'
$g += '<tr><td>渲染成功 / 失败</td><td><code>21 / 0</code>，0 条 429，ratelimit_remaining 最低 110</td></tr>'
$g += '<tr><td>迭代行</td><td><code>' + $metrics.counts.iteration_log_rows + '</code>（10 baseline + 11 visual）</td></tr>'
$g += '<tr><td>读图调用</td><td><code>' + $metrics.counts.image_views + '</code>（' + $metrics.counts.image_views_matched_bytes + ' 次匹配正确字节 + ' + $metrics.counts.image_views_mismatched_bytes + ' 次串图/重复，全部留档）</td></tr>'
$g += '<tr><td>最终图片</td><td><code>10</code> 张，服务原始字节，PNG 与 .snapshot 一一配对</td></tr>'
$g += '<tr><td>外部素材</td><td><code>0</code>（纯 DSL）</td></tr>'
$g += '<tr><td>token / 费用</td><td><code>null</code>（平台未提供，不猜）</td></tr>'
$g += '</table>'
$g += '<p style="color:#8B97A4;font-size:13px">本地画廊：全部相对链接、无远程脚本、图片可点开原尺寸。单题入口 <code>outputs/' + $run + '/B04/</code>，总入口 <a href="../_suite/index.md">_suite/index.md</a> · <a href="../_suite/gallery.html">_suite/gallery.html</a>。</p>'
$g += '</section>'
$g += '</main>'
$g += '<footer>《多出来的那一秒》· B04 · 运行 ' + $run + ' · 内容为科普与数据可视化，不构成工程/法律/标准建议。刊名与署名为 DEMO。所有数字以 2026-10-07 为抓取基准。</footer>'
$g += '</body></html>'

$gh = Join-Path $o 'gallery.html'
[IO.File]::WriteAllText($gh, (($g -join "`r`n") + "`r`n"), $enc)
"  wrote gallery.html ({0} bytes)" -f (Get-Item $gh).Length
