# close A15 / open A16 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000016.json.
$ErrorActionPreference = 'Stop'
[System.Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$SUITE_OUT = "outputs\$RUN\_suite"
$SUITE_TMP = "tmp\$RUN\_suite"
$STATE     = "$SUITE_OUT\suite-state.json"
$EVENTS    = "$SUITE_TMP\events.jsonl"
$CKPT_DIR  = "$SUITE_TMP\checkpoints"
$TASK      = 'A15'
$NEXT      = 'A16'

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')

# ended_at is taken from the task's own metrics file so the two never drift.
$metricsPath = "outputs\$RUN\A15\task-metrics.json"
$metrics = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($metricsPath, [Text.UTF8Encoding]::new($false)))
$A15End = [string]$metrics.ended_at
if ($A15End -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$') { throw "A15 ended_at is not a timezone-carrying timestamp: $A15End" }

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, [Text.UTF8Encoding]::new($false))
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A15 close ---
$a15 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a15) { throw "A15 entry not found in suite-state.json" }
if ($a15.status -ne 'in_progress') { throw "A15 expected in_progress, found $($a15.status)" }

$a15.status     = 'completed'
$a15.ended_at   = $A15End
$a15.output_dir = "outputs/$RUN/A15/"
$a15.temp_dir   = "tmp/$RUN/A15/"
$a15.artifacts = @(
  'outputs/run-20261002-220723-mimo/A15/reconstructed.png',
  'outputs/run-20261002-220723-mimo/A15/reconstructed.snapshot',
  'outputs/run-20261002-220723-mimo/A15/reconstruction-audit.json',
  'outputs/run-20261002-220723-mimo/A15/comparison.md',
  'outputs/run-20261002-220723-mimo/A15/snapshot-usage.md',
  'outputs/run-20261002-220723-mimo/A15/task-metrics.json'
)
$a15.visual_review_evidence = @(
  'tasks/A15-reference-reconstruction/inputs/reference.png  原尺寸整图打开，与复刻并排比对 —— 看出参考把选中导航项、三个 KPI 标签、三个 KPI 变化值、三条活动标题、四个表头、三行项目名、三段状态胶囊文字全部排成更重的字重，而首版全部是常规字重；先由看图发现，随后才用墨量探针量化（当时这 17 个元素比值 1.40–1.92）',
  'tmp/run-20261002-220723-mimo/A15/reconstructed-v03.png  原尺寸整图（字重修正前）：结构、位置、配色、图表比例全对，唯一肉眼可见差异是字重偏轻',
  'tmp/run-20261002-220723-mimo/A15/reconstructed-v06.png  原尺寸整图（字重+字号修正后）：字重与参考一致，59 个文本元素 dx=dy=0，未见新缺陷',
  'tmp/run-20261002-220723-mimo/A15/reconstructed-v07.png  原尺寸整图（终稿）：导航选中胶囊修正后无新缺陷',
  'tmp/run-20261002-220723-mimo/A15/view-A15-final-thumb-720x450.png  720x450 缩略：版面骨架与参考一致（220 深色侧栏 + 浅色主区、三张 KPI 卡、图表卡与活动卡并排、下方通栏表格卡）',
  'tmp/run-20261002-220723-mimo/A15/view-A15-zoom-top-left.png  760x300 局部：字标、选中导航胶囊、标题、导出按钮、KPI 首卡清晰无裁切',
  'tmp/run-20261002-220723-mimo/A15/view-A15-zoom-chart.png  760x310 局部：五条网格线、六条柱、顶角圆角与零线贴合、刻度与月份标签对齐',
  'tmp/run-20261002-220723-mimo/A15/view-A15-zoom-table.png  1140x230 局部：三行顺序、Owner/DUE、三个状态胶囊（In progress / Review / Done）与表头带全部正确',
  'tmp/run-20261002-220723-mimo/A15/view-A15-zoom-sidebar.png  400x200 局部：PRO WORKSPACE 卡三行齐备、与主区分界干净',
  'outputs/run-20261002-220723-mimo/A15/reconstructed.png  交付件原图重新打开：与 reconstructed-v07.png SHA256 逐字节一致（C6C41F6E…C029），1440x900、服务原始字节、无后处理',
  'outputs/run-20261002-220723-mimo/A15/reconstruction-audit.json  mk-audit.ps1 产出：几何 44/44（最大 1px）、文本 59/59（最大 3px）、指定锚点 15/15 全通过，墨量比 45/59 恰为 1.000',
  '注：五张缩略/局部观察图全部裁自本作品自己的输出 PNG，只存 tmp/ 作观察用；参考图的局部检查走像素探针而非裁图，因为题目明令禁止裁块'
)
$a15.unresolved_issues = @(
  'KPI 标签（REVENUE / ORDERS / REFUND RATE）墨量比 1.052–1.062、墨迹宽 61/64、54/55、83/85 —— 参考这三段全大写文本的字距推进量无法用单一 Inter 字号同时复现宽度与墨量，取 fs 13.6 折中，剩余约 6% 偏轻；远在 ±8px 内，已在 comparison.md 与 task-metrics.open_issues 中量化记录',
  '活动标题 Dataset updated / Render complete 的 p 降部比参考低约 1px（墨迹高 16 vs 15），属字形降部差异而非字号或位置差异，宽度 140/139、142/141 在 1px 内',
  'Apr 柱顶边实测 484 vs 参考 485（1px 圆角抗锯齿取整差）；柱底、柱左、柱宽全部零误差',
  '不宣称逐像素完全复刻：文字墨迹仍有 1–3px 级别残差，题目也明确不要求 DSL 树与参考来源一致',
  '交互式开图的精确时刻未埋点：iterations.jsonl 视觉类行的 started_at/ended_at 置 null，改用相邻渲染/文档请求的真实时间戳作为区间上下界并写入 view_window，不编造时刻'
)
$a15.resume_notes = '8 次请求全部 200（6 次 POST /snapshot 渲染 + 2 次文档 GET），0 失败、0 重试、0 限流，请求耗时之和 25933.3ms（渲染 20501.0ms + 文档 5432.3ms）。交付 6 个产物：reconstructed.png（1440x900，113766 字节，SHA256 C6C41F6E…C029，服务原始字节无后处理）+ reconstructed.snapshot（13680 字节，无 BOM、无 Image、无 Transform）+ reconstruction-audit.json + comparison.md + snapshot-usage.md + task-metrics.json。方法：7 个参考测量探针（probe-ref1..7）先量出侧栏 220、卡片盒、五条网格线 y405/441/477/513/549、柱几何 x=357+101i 宽 54 以及全部 59 个文本墨迹盒；gen.ps1 用固定元素表 + placement 生成 7 版 DSL（v01..v07，v02 为未提交草稿）；compare.ps1 在完全相同窗口测两边墨迹盒回写位置（只在宽度误差 >8px 时改字号）；probe-anchors.ps1 测 44 个几何锚点；probe-weight.ps1 测平移不变的墨量比。6 轮渲染、15 行 iterations、10 次看图、2 轮完整视觉迭代。1 个由看图发现的真实缺陷（字重全错，17 个元素），2 个由测量发现的缺陷（导航胶囊差 2px、KPI 标签偏轻 5–6%）。终态：几何 44/44 最大 1px、文本 59/59 最大 3px 且 dx=dy=0、指定 15 锚点（四象限+图表+表格）全通过、墨量 45/59 逐像素相同。3 个测量工具自身缺陷已修复（窗口漏 +rw、-ResetOnly 未挡住写入、measure 别名遮蔽脚本函数）。墙钟 6005s，首个可用图 3541s。'

# ------------------------------------------------------------------ A16 open -----
$a16 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a16) { throw "$NEXT entry not found" }
if ($a16.status -ne 'pending') { throw "$NEXT expected pending, found $($a16.status)" }
$a16.status      = 'in_progress'
$a16.started_at  = $closeTs
$a16.output_dir  = "outputs/$RUN/$NEXT/"
$a16.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000016.json"
$src.status          = 'in_progress'

# --------------------------------------------------------------- write state ------
$stateText = $src | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText($STATE, $stateText, [Text.UTF8Encoding]::new($false))

# ----------------------------------------------------------------- events ---------
$evLines = New-Object System.Collections.Generic.List[string]
$ev29 = [ordered]@{
  seq  = 29
  ts   = $closeTs
  type = 'task_completed'
  task = $TASK
  artifacts = 6
  renders = 6
  views = 10
  visual_iterations = 2
  note = 'A15 参考界面复刻完成：reconstructed.png（1440x900，服务原始字节，SHA256 C6C41F6E…C029）+ reconstructed.snapshot（无 BOM / 无 Image / 无 Transform）+ reconstruction-audit.json + comparison.md + snapshot-usage.md + task-metrics.json 共 6 个产物。8 次请求全部 200（6 渲染 + 2 文档），0 失败、0 重试、0 限流，请求耗时之和 25933.3ms。参考图仅被观察与像素采样，未裁块、未描图、未嵌入，输出中参考像素数为 0。7 个参考测量探针先量出几何与全部 59 个文本墨迹盒，7 版 DSL、6 轮渲染、15 行 iterations、10 次看图、2 轮完整视觉迭代。由看图发现的缺陷：字重全错（参考把选中导航/KPI 标签/KPI 变化/活动标题/表头/项目名/状态文字排得更重，首版全常规），17 个元素当时墨量比 1.40–1.92。由测量发现的缺陷：导航选中胶囊 182x46 vs 参考 184x48（2px），KPI 标签偏轻 5–6%。终态：几何 44/44 最大 1px、文本 59/59 最大 3px 且 dx=dy=0、指定 15 锚点（四象限+图表+表格）全通过、墨量 45/59 逐像素相同。task-metrics.ended_at = ' + $A15End + '（本事件时刻为状态落盘时刻）。'
}
$ev30 = [ordered]@{
  seq  = 30
  ts   = $closeTs
  type = 'task_started'
  task = $NEXT
  note = ''
}
foreach ($e in @($ev29, $ev30)) {
  $o = [pscustomobject]$e
  $evLines.Add(($o | ConvertTo-Json -Depth 6 -Compress))
}
$append = [string]::Join([Environment]::NewLine, $evLines.ToArray()) + [Environment]::NewLine
[IO.File]::AppendAllText($EVENTS, $append, [Text.UTF8Encoding]::new($false))

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
  checkpoint_id    = 'state-000016'
  checkpoint_seq   = 16
  event_seq        = 30
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000016.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A15 关闭：reconstructed.png + reconstructed.snapshot + reconstruction-audit.json + comparison.md + snapshot-usage.md + task-metrics.json 共 6 个产物全部落盘，PNG 为 1440x900 服务原始字节并与 reconstructed-v07.png 逐字节 SHA256 一致。8 次请求（6 渲染 + 2 文档，全 200、0 重试），15 行 iterations，10 次看图，2 轮真实视觉迭代；几何锚点 44/44（最大 1px）、文本锚点 59/59（最大 3px）、指定 15 锚点全通过。suite-state.json 中 A15=completed、A16=in_progress。A16 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000016.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), [Text.UTF8Encoding]::new($false))

Write-Output "A15 -> completed (ended_at $A15End)"
Write-Output "A16 -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 29 (task_completed A15), seq 30 (task_started A16)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000016.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
