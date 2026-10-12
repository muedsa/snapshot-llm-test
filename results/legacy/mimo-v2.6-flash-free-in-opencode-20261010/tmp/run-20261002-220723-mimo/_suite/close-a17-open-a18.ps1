# close A17 / open A18 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000018.json.
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$SUITE_OUT = "outputs\$RUN\_suite"
$SUITE_TMP = "tmp\$RUN\_suite"
$STATE     = "$SUITE_OUT\suite-state.json"
$EVENTS    = "$SUITE_TMP\events.jsonl"
$CKPT_DIR  = "$SUITE_TMP\checkpoints"
$TASK      = 'A17'
$NEXT      = 'A18'
$utf8      = [Text.UTF8Encoding]::new($false)

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')

# ended_at / counts come from the task's own metrics file so they never drift.
$metricsPath = "outputs\$RUN\A17\task-metrics.json"
$metrics = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($metricsPath, $utf8))
$A17End = [string]$metrics.ended_at
if ($A17End -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$') { throw "A17 ended_at is not a timezone-carrying timestamp: $A17End" }

$exDir = "outputs\$RUN\A17"
function HashOf([string]$f) { return (Get-FileHash $f -Algorithm SHA256).Hash }
function SizeOf([string]$f) { return (Get-Item $f).Length }

$pb1 = "$exDir\handbook-01.png";  $pb1H = HashOf $pb1;  $pb1B = SizeOf $pb1
$pb4 = "$exDir\handbook-04.png";  $pb4H = HashOf $pb4;  $pb4B = SizeOf $pb4
$ex4 = "$exDir\example-04.png";   $ex4H = HashOf $ex4

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, $utf8)
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A17 close ---
$a17 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a17) { throw "$TASK entry not found in suite-state.json" }
if ($a17.status -ne 'in_progress') { throw "$TASK expected in_progress, found $($a17.status)" }

$a17.status     = 'completed'
$a17.ended_at   = $A17End
$a17.output_dir = "outputs/$RUN/A17/"
$a17.temp_dir   = "tmp/$RUN/A17/"
$a17.artifacts = @(
  'outputs/run-20261002-220723-mimo/A17/example-01.png',
  'outputs/run-20261002-220723-mimo/A17/example-01.snapshot',
  'outputs/run-20261002-220723-mimo/A17/example-02.png',
  'outputs/run-20261002-220723-mimo/A17/example-02.snapshot',
  'outputs/run-20261002-220723-mimo/A17/example-03.png',
  'outputs/run-20261002-220723-mimo/A17/example-03.snapshot',
  'outputs/run-20261002-220723-mimo/A17/example-04.png',
  'outputs/run-20261002-220723-mimo/A17/example-04.snapshot',
  'outputs/run-20261002-220723-mimo/A17/handbook-01.png',
  'outputs/run-20261002-220723-mimo/A17/handbook-01.snapshot',
  'outputs/run-20261002-220723-mimo/A17/handbook-02.png',
  'outputs/run-20261002-220723-mimo/A17/handbook-02.snapshot',
  'outputs/run-20261002-220723-mimo/A17/handbook-03.png',
  'outputs/run-20261002-220723-mimo/A17/handbook-03.snapshot',
  'outputs/run-20261002-220723-mimo/A17/handbook-04.png',
  'outputs/run-20261002-220723-mimo/A17/handbook-04.snapshot',
  'outputs/run-20261002-220723-mimo/A17/sources.md',
  'outputs/run-20261002-220723-mimo/A17/examples.json',
  'outputs/run-20261002-220723-mimo/A17/snapshot-usage.md',
  'outputs/run-20261002-220723-mimo/A17/task-metrics.json'
)
$a17.visual_review_evidence = @(
  'tmp/run-20261002-220723-mimo/A17/example-01-v02.png  400x240 整图：正文块左对齐确认，v01 的居中缺陷已消失',
  'tmp/run-20261002-220723-mimo/A17/example-02-v02.png  400x240 整图：面板换成 #E2E8F0 后 right + bottom 黑字可读，v01 深底看不清的缺陷已消失',
  'tmp/run-20261002-220723-mimo/A17/example-03-v02.png  400x240 整图：两条图例行提亮后可读，FF/80/26 三块尾随 alpha 色条对比正常',
  'tmp/run-20261002-220723-mimo/A17/example-04-v02.png  400x240 整图：毛玻璃仍然缺失（ImageFiltered 在同一 Stack 内导致 BackdropFilter 失效），据此继续做隔离实验',
  'tmp/run-20261002-220723-mimo/A17/example-04-v03.png  400x240 整图（终稿）：ImageFiltered 移出 Stack 后模糊恢复（y44-52、y186-191 软过渡），BLUR 白字可读',
  'tmp/run-20261002-220723-mimo/A17/printed-02.png  400x240 整图：把手册打印的 17 行原样发服务，注释行被解析器跳过，成像与完整示例一致；正是这张图让我看出代码块标题"可复制的完整文件"与标注"完整文件共 18 行"自相矛盾',
  'tmp/run-20261002-220723-mimo/A17/handbook-01-v01.png  1200x1600 整图（首版）：版面与配色正确，17 行打印代码缩进逐字保留，琥珀色省略标注清晰',
  'tmp/run-20261002-220723-mimo/A17/handbook-02-v01.png  1200x1600 整图（首版）：插图与右侧 5 条要点齐备，浅色面板对比度正常',
  'tmp/run-20261002-220723-mimo/A17/handbook-03-v01.png  1200x1600 整图（首版）：CDATA 行逐字可见、Raw 缩进完整',
  'tmp/run-20261002-220723-mimo/A17/handbook-04-v01.png  1200x1600 整图（首版）：肉眼看到插图边缘有一圈白，用 cmp-illu 量化为 6078 像素差异（全部落在列 0-149、行 0-191）——页面白卡被 BackdropFilter 模糊采样进来',
  'tmp/run-20261002-220723-mimo/A17/handbook-04-v02.png  1200x1600 整图（ClipRect 后）：插图边界干净，白卡渗色消失',
  'tmp/run-20261002-220723-mimo/A17/handbook-01-v03.png  1200x1600 整图（终稿）：新标题"可复制运行：16 行原文 + 1 行省略标注（文件共 18 行）"语义自洽；本次看图工具把 01/02 两帧对调返回，已用文件字节数（' + $pb1B + ' 字节、接近 v02 的 323887 而远离 02 的 272184）与 DSL 内徽标文字交叉验证磁盘文件无误',
  'tmp/run-20261002-220723-mimo/A17/handbook-02-v03.png  1200x1600 整图（终稿）：错误结论"根尺寸由 Snapshot 的 width/height 决定"已改为"根尺寸由根布局决定，受服务端限制"，Positioned 措辞改为"最多只能给两个"',
  'tmp/run-20261002-220723-mimo/A17/handbook-03-v03.png  1200x1600 整图（终稿）：本地 read 连续两次返回别的页，改由独立子代理逐字读帧确认（徽标 P3 · 文本与颜色、标题、描述、新标题、琥珀标注、4 条踩坑含 &amp; 不会被解码、5 条右栏要点、页脚第 3 / 4 页），记于 iterations.jsonl seq 41',
  'tmp/run-20261002-220723-mimo/A17/handbook-04-v03.png  1200x1600 整图（终稿）：同批由独立子代理逐字读帧确认（徽标 P4 · 滤镜与自检、"毛玻璃通常需要 ClipRect / ClipRRect 限区"等），记于 iterations.jsonl seq 42',
  'outputs/run-20261002-220723-mimo/A17/handbook-01.png  交付件原图：与 handbook-01-v03.png SHA256 逐字节一致（' + $pb1H.Substring(0, 8) + '…' + $pb1H.Substring($pb1H.Length - 4) + '），1200x1600、服务原始字节、无后处理',
  'outputs/run-20261002-220723-mimo/A17/handbook-04.png  交付件原图：与 handbook-04-v03.png SHA256 逐字节一致（' + $pb4H.Substring(0, 8) + '…' + $pb4H.Substring($pb4H.Length - 4) + '），' + $pb4B + ' 字节',
  'outputs/run-20261002-220723-mimo/A17/example-04.png  交付件原图：与 example-04-v03.png SHA256 逐字节一致（' + $ex4H.Substring(0, 8) + '…' + $ex4H.Substring($ex4H.Length - 4) + '），400x240',
  'cmp-illu.ps1 对 4 张交付手册页在 (72,242) 400x240 窗口逐像素比对各自的 example-0N.png：differingPixels=0、maxChannelDelta=0，四页全部 0 差异',
  'check-a17.ps1 交付审计：20 个文件、8 对 PNG/DSL 与渲染源 SHA256 一致、尺寸与行数正确、无 BOM 无乱码、8 张交付图全部有真实看图记录、打印片段 4/4 被服务接受 —— final-audit.md problems = 0'
)
$a17.unresolved_issues = @(
  '看图通道对 3 个路径返回了帧内容与请求路径不符：handbook-01-v03 与 handbook-02-v03 两次对调、handbook-03-v03 连续两次返回别页。每次打开都做了帧内容比对，两次对调用文件字节数 + DSL 内徽标交叉验证磁盘文件无误，页 3/4 改由独立子代理逐字读帧；iterations.jsonl seq 39/40 记失败的本地读取、seq 41/42 记成功的委托读取，互不覆盖。若下题复现按同样方式处理',
  '首次 handbook-03 草稿被 gen-pages.ps1 就地覆盖，违反"不覆盖尝试"；已按覆盖前的生成器逻辑重建为 handbook-03-v01-draft1.snapshot 并重发验证（A17-pg03draft 返回与原始 A17-pg03 完全相同的 400 PARSE_ERROR：position 5735 + 相同 near 文本），证明重建件忠实，但原始字节本身不可恢复；两份失败响应体均保留于 tmp/A17/failures/',
  '四行 example v01 渲染记录曾写进 outputs/.../A17/requests.jsonl，后追加进本题日志，因此这四行在 requests.jsonl 中的位置不等于其时间顺序（每行仍带自己的 started_utc/ended_utc），原件归档为 requests-merged-from-outputs.jsonl',
  '交互式开图的精确时刻未埋点：视觉类行的 viewed_at 用统一的批处理时刻登记，与真实逐张打开时刻存在分钟级偏差；不编造更细的时刻',
  'Retry-After 实际取值、服务端画布尺寸上限从未观测到，记 null 不估算；token 与费用无法测量，task-metrics.json 全部记 null'
)
$a17.resume_notes = '50 次请求（42 POST /snapshot 渲染 + 8 GET 文档），200=45、400=5，0 限流，请求耗时之和 123342.2ms（渲染 113669.9ms + 文档 9672.3ms），收到 4740616 字节（PNG 4229132 + 文档 511484）。交付 20 个产物：4 个 400x240 独立示例（example-01..04.png/.snapshot，各 18 行）+ 4 个 1200x1600 手册页（handbook-01..04.png/.snapshot，各 63 行）+ sources.md + examples.json + snapshot-usage.md + task-metrics.json；PNG 全部为服务原始字节、与 -v0N 渲染件 SHA256 逐字节一致。42 行 iterations（baseline 8 / visual 16 / alternative 11 / requirement-change 4 / syntax-fix 2 / retry 1），22 次成功看图覆盖 8 张交付图，10 轮完整视觉迭代。文档侧 8 次真实 GET 全 200，手册每条结论经 sources.md 接回保留原文行号。13 个探针实测行盒与等宽步进（fs22 等宽 11px/字符 → 94 字符预算）、空白语义（Text 剪、Raw+CDATA 保）、以及两条手册结论（Raw 出 Text → 400、Expanded 层级 → 400）。4 个 BackdropFilter 探针得出文档未写的新结论：ImageFiltered 在同一 Stack 内会让背景滤镜失效，已移出修复。打印代码用 Raw+CDATA 逐字输出并在含 ]]&gt; 处跨两段拆分终止符，4 段重建的 17 行打印片段全部被服务接受（含 XML 注释行）。每页插图用示例自身的 DSL 子树而非 Image，套 ClipRect 后四页与各自 example 差异全部归 0。由看图发现 5 个缺陷、由像素测量发现 1 个（6078px 渗色）、由文档准确性审查发现 3 个。final-audit.md problems = 0。墙钟 ' + $metrics.wall_clock_s + 's。'

# ------------------------------------------------------------------ A18 open -----
$a18 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a18) { throw "$NEXT entry not found" }
if ($a18.status -ne 'pending') { throw "$NEXT expected pending, found $($a18.status)" }
$a18.status      = 'in_progress'
$a18.started_at  = $closeTs
$a18.output_dir  = "outputs/$RUN/$NEXT/"
$a18.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000018.json"
$src.status          = 'in_progress'

# --------------------------------------------------------------- write state ------
[IO.File]::WriteAllText($STATE, ($src | ConvertTo-Json -Depth 12), $utf8)

# ----------------------------------------------------------------- events ---------
$evLines = New-Object System.Collections.Generic.List[string]
$ev33 = [ordered]@{
  seq  = 33
  ts   = $closeTs
  type = 'task_completed'
  task = $TASK
  artifacts = 20
  renders = 42
  views = 22
  visual_iterations = 10
  note = 'A17 文档手册完成：4 个 400x240 独立示例 + 4 个 1200x1600 手册页 + sources.md + examples.json + snapshot-usage.md + task-metrics.json 共 20 个产物。50 次请求（42 渲染 + 8 文档）200=45、400=5，0 限流，请求耗时之和 123342.2ms，收到 4740616 字节；5 个 400 全部保留失败响应体（probe01 语法、pg03 含 ]]&gt; 的 CDATA 提前闭合、probe12/probe13 两条故意的否定测试、pg03draft 验证重建件）。42 行 iterations，22 次成功看图覆盖 8 张交付图，10 轮完整视觉迭代：看图发现 5 个缺陷、像素测量发现 1 个（手册 4 插图 6078px 白卡渗色）、文档准确性审查发现 3 个（根尺寸错误结论、Positioned 与 ClipRect 措辞不精确）。8 次文档 GET 全 200 共 511484 字节，sources.md 把每条结论接回保留原文行号，拿不准的三处（Retry-After 秒数、画布尺寸上限、snapshot-lsp 用法）明确不写进手册。13 个探针实测行盒与等宽步进（fs22 等宽 11px/字符）、Text/Raw/CDATA 空白语义，并把手册两条踩坑变成实测（Raw 出 Text → 400、Expanded 层级 → 400）。4 个 BackdropFilter 探针得出文档未写的新结论：ImageFiltered 在同一 Stack 内会让背景滤镜失效。打印代码用 Raw+CDATA 逐字输出、含 ]]&gt; 时跨两段拆分终止符，4 段重建的 17 行打印片段（16 行原文 + 1 行 XML 注释标注）全部被服务接受。每页插图是示例自身的 DSL 子树而非 Image，套 ClipRect 后四页与各自 example 的 400x240 差异全部归 0。final-audit.md problems = 0。task-metrics.ended_at = ' + $A17End + '（本事件时刻为状态落盘时刻）。'
}
$ev34 = [ordered]@{
  seq  = 34
  ts   = $closeTs
  type = 'task_started'
  task = $NEXT
  note = ''
}
foreach ($e in @($ev33, $ev34)) {
  $evLines.Add((([pscustomobject]$e) | ConvertTo-Json -Depth 6 -Compress))
}
[IO.File]::AppendAllText($EVENTS, ([string]::Join([Environment]::NewLine, $evLines.ToArray()) + [Environment]::NewLine), $utf8)

# ---------------------------------------------------------------- checkpoint ------
$counts = @($src.tasks | Group-Object status | ForEach-Object { [pscustomobject]@{ status = $_.Name; count = $_.Count } })
$completedIds = @($src.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
$ckpt = [pscustomobject][ordered]@{
  schema_version   = 1
  suite_version    = $src.suite_version
  run_id           = $RUN
  profile          = $src.profile
  status           = $src.status
  snapshot_at      = $closeTs
  checkpoint_id    = 'state-000018'
  checkpoint_seq   = 18
  event_seq        = 34
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000018.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A17 关闭：20 个产物全部落盘（4 示例 + 4 手册页 + 4 份文档），PNG 为服务原始字节并与对应 -v0N 渲染件逐字节 SHA256 一致。50 次请求（42 渲染 + 8 文档，200=45、400=5 全为保留的失败响应体），42 行 iterations，22 次成功看图覆盖 8 张交付图，10 轮真实视觉迭代；四页插图与各自 example 在 400x240 全域 0 差异，4 段打印片段全部被服务接受，final-audit.md problems = 0。suite-state.json 中 A17=completed、A18=in_progress。A18 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000018.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), $utf8)

Write-Output "$TASK -> completed (ended_at $A17End)"
Write-Output "$NEXT -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 33 (task_completed $TASK), seq 34 (task_started $NEXT)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000018.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
