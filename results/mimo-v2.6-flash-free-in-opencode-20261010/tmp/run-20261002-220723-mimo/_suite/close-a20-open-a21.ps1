# close A20 / open A21 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000021.json.
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
$TASK      = 'A20'
$NEXT      = 'A21'
$utf8      = [Text.UTF8Encoding]::new($false)

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')

$metricsPath = "outputs\$RUN\A20\task-metrics.json"
$metrics = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($metricsPath, $utf8))
$A20End = [string]$metrics.ended_at
if ($A20End -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$') { throw "$TASK ended_at is not a timezone-carrying timestamp: $A20End" }
$wallS = [Math]::Round(($metrics.wall_clock_total_ms / 1000.0), 1)

$exDir = "outputs\$RUN\A20"
function HashOf([string]$f) { return (Get-FileHash $f -Algorithm SHA256).Hash }
function SizeOf([string]$f) { return (Get-Item $f).Length }

# ------------------------------------------------------------------- required ----
$required = @('annotated-map.png','annotated-map.snapshot','label-layout.json','layout-audit.json','snapshot-usage.md','task-metrics.json')
foreach ($f in $required) { if (-not (Test-Path "$exDir\$f")) { throw "missing required deliverable $f" } }

$png = "$exDir\annotated-map.png"; $pngH = HashOf $png; $pngB = SizeOf $png
$dsl = "$exDir\annotated-map.snapshot"; $dslH = HashOf $dsl; $dslB = SizeOf $dsl
$layH = HashOf "$exDir\label-layout.json"; $audH = HashOf "$exDir\layout-audit.json"

# delivered bytes must equal the served bytes
$srcPng = "tmp\$RUN\A20\annotated-map-v09.png"
$srcDsl = "tmp\$RUN\A20\annotated-map-v09.snapshot"
if ($pngH -ne (HashOf $srcPng)) { throw 'delivered PNG is not byte-identical to the service response' }
if ($dslH -ne (HashOf $srcDsl)) { throw 'delivered snapshot is not byte-identical to the served DSL' }

# real image size, read from the PNG IHDR rather than trusted from a report
$fs = [IO.File]::OpenRead($png); $buf = New-Object byte[] 24
[void]$fs.Read($buf, 0, 24); $fs.Close()
$w = [BitConverter]::ToUInt32(@($buf[19],$buf[18],$buf[17],$buf[16]), 0)
$h = [BitConverter]::ToUInt32(@($buf[23],$buf[22],$buf[21],$buf[20]), 0)
if ($w -ne 1600 -or $h -ne 1100) { throw "final PNG is ${w}x${h}, expected 1600x1100" }

$audit = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$exDir\layout-audit.json", $utf8))
if ($audit.problems.Count -ne 0) { throw "layout-audit.json still reports $($audit.problems.Count) problems" }
foreach ($vc in @('center6_zoom','leaders_zoom','whole_view')) {
  $v = [string]$audit.visual_checks.$vc
  if ($v -notmatch 'CONFIRMED') { throw "visual check $vc is not confirmed" }
}
$layout = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$exDir\label-layout.json", $utf8))
if ($layout.markers.Count -ne 24) { throw "label-layout has $($layout.markers.Count) markers, expected 24" }
$mp = $layout.mapping
if ($mp.logical_origin -ne 'bottom-left' -or $mp.logical_x_direction -ne 'right' -or $mp.logical_y_direction -ne 'up') { throw 'logical origin/direction is not bottom-left / right / up' }
if ($mp.plot_rect.left -ne 280 -or $mp.plot_rect.top -ne 160 -or $mp.plot_rect.width -ne 1040 -or $mp.plot_rect.height -ne 760) { throw 'plot_rect is not (280,160,1040,760)' }
if ($null -ne $mp.y_axis_flipped) { throw 'mapping.y_axis_flipped is back - it was ambiguous against the spec phrase and must stay replaced by explicit corner evidence' }
if ($mp.pixel_y_inversion_applied -ne $true -or $mp.pixel_y_inversion_correct -ne $true) { throw 'mapping must record that the pixel-y inversion is applied AND correct' }
if ($mp.data_mirrored -ne $false) { throw 'mapping.data_mirrored must be false - the spec forbids getting the inversion wrong' }
if ($mp.corner_checks.Count -ne 4 -or @($mp.corner_checks | Where-Object { $_.pass -ne $true }).Count -ne 0) { throw 'mapping corner_checks must hold 4 passing entries' }
if ($layout.center6.Count -ne 6 -or $layout.top3.Count -ne 3) { throw 'center6/top3 must hold exactly 6 and 3 entries' }
$nLeader = @($layout.markers | Where-Object { $null -ne $_.leader }).Count
if ($nLeader -ne 4) { throw "label-layout records $nLeader leader lines, expected 4" }
$nRing = @($layout.markers | Where-Object { $_.marker.isTop3 -eq $true }).Count
if ($nRing -ne 3) { throw "label-layout records $nRing top-3 ringed markers, expected 3" }
$nNeed = @($layout.markers | Where-Object { $_.label.needsLeader -eq $true }).Count
if ($nNeed -ne 4) { throw "label-layout marks $nNeed labels as needing a leader, expected 4" }

$req = Get-Content "tmp\$RUN\A20\requests.jsonl" -Encoding UTF8
$iters = Get-Content "tmp\$RUN\A20\iterations.jsonl" -Encoding UTF8

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, $utf8)
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A20 close ---
$a20 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a20) { throw "$TASK entry not found in suite-state.json" }
if ($a20.status -ne 'in_progress') { throw "$TASK expected in_progress, found $($a20.status)" }

$base = "outputs/run-20261002-220723-mimo/A20/"
$a20.status     = 'completed'
$a20.ended_at   = $A20End
$a20.output_dir = "outputs/$RUN/A20/"
$a20.temp_dir   = "tmp/$RUN/A20/"
$a20.artifacts = @(
  $base + 'annotated-map.png',
  $base + 'annotated-map.snapshot',
  $base + 'label-layout.json',
  $base + 'layout-audit.json',
  $base + 'snapshot-usage.md',
  $base + 'task-metrics.json'
)
$a20.visual_review_evidence = @(
  'tmp/run-20261002-220723-mimo/A20/annotated-map-v08.png  基线整图 1600x1100（本地读取）：24/24 标签含 id+名称+数值、24 点圆、3 个 Top-3 红环、轴/刻度/量程/单位指数/Top3 榜单/图例齐全；同时发现 2 处真实边距缺陷 —— y 轴题注左缘 x=8（标题 x=41）、右上角注记右缘 x=1594 仅离画布 5px',
  'tmp/run-20261002-220723-mimo/A20/zoom-center6-v08.png  中心 6 点 3x（源区 560,440-1060,700，本地读取）：M06/M08/M09/M10/M11/M12 与 4 条引导线全部到位',
  'tmp/run-20261002-220723-mimo/A20/zoom-tight-v08.png  中心密集簇 5x（源区 700,460-980,650，本地读取）：M09 水平引导线终止于本点蓝点、M08 折线带一个可见折弯进红环、M11 短横线连回点、M18 竖线下行进标签；不透明标签底片正确盖住其下的网格线，无任何底片压住点圆',
  'tmp/run-20261002-220723-mimo/A20/annotated-map-v09.png  修复后整图（本地读取）：y 题注左缘 40、右上注记右缘 1558（41px 边距与标题镜像），其余测量带不变',
  'tmp/run-20261002-220723-mimo/A20/v-center-01.png  交付字节上的中心 6 点 3x 裁剪（本地读取），按题面要求「先放大中心 6 点与引导线，再看整体」的顺序复核',
  'outputs/run-20261002-220723-mimo/A20/annotated-map.png  交付件 1600x1100（本地整图读取；SHA-256 ' + $pngH.Substring(0,16) + ' 与 v09 逐字节相同）',
  'measure.ps1  GDI+ 像素带扫描（仅作佐证，不计入看图）：右上注记右缘 1594->1558、y 题注左缘 8->40，标题 41、副标题 41..760、x 刻度 275..284、x 题注 280、Top3 榜单 280..970、图例 1482/1493 全部不变',
  'outputs/run-20261002-220723-mimo/A20/label-layout.json  24 个条目各含逻辑坐标、像素锚点、标签盒与引导线折线；mapping 用 corner_checks 四角实测证明「映射到像素时不要反转错误」——(0,0)->(280,920) 左下、(100,0)->(1320,920) 右下、(0,100)->(280,160) 左上、(100,100)->(1320,160) 右上，4/4 通过，pixel_y_inversion_applied/correct 均为 true、data_mirrored=false；此前含义含混的 y_axis_flipped 已删除，v10 的 snapshot 与交付 v09 SHA-256 完全相同故未重渲染，v08/v09/v10 全部保留',
  'layout-audit.json  11 组规则 / 2066 项逐对断言全 0 违规：标签两两最小 7.9px（阈值 4）、标签离非本点最小 18px（半径+6）、归属最小优势 +6.94px、边界最小余量 274.5px、线穿标签 0/7 段、线连错点 0、线线交叉 0（限 3）且不画连接点、点圆最小边隙 11.86px 故未启用缩到 8px 的豁免；visual_checks 三项均由 pending 改为 CONFIRMED',
  'iterations.jsonl 4 行（baseline 1 / visual 1 / syntax-fix 1 / alternative 1），2 行带图，1 轮完整视觉迭代；requests.jsonl 2 次渲染 200=2、0 失败 0 重试，限流余量 119，请求耗时之和 7193.7ms；看图 6 次（全部本地读取），另有 7 次 read 返回串了缓冲区，如实计为失败尝试并改用像素测量复核'
)
$a20.unresolved_issues = @(
  '7 次 read 返回的图像缓冲区与请求路径不一致（读裁剪图回整图、读交付整图回中心裁剪）。文件本身 MD5/SHA-256 两两不同且与重新裁剪的副本一致，判定为查看通道串缓冲区；所有几何结论改用 measure.ps1 的 GDI+ 像素扫描复核，交付整图另有 SHA-256 与已成功整图查看的 v09 完全相同作为依据。该现象与快照服务无关，未影响任何渲染请求',
  '看图精确时钟未被采集：iterations.jsonl 以 viewed_at_basis 记录可证明的时间窗（渲染结束 -> 下一次渲染开始），不编造具体时刻',
  'token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明原因，不用字数或账号余量估造',
  'y 轴 100 刻度位于主图区上边框之外（其余 4 个刻度在框内），属刻意取舍：把 5 个刻度全部外移会让 100 刻度与 y 轴题注相撞，故保持现状并在 snapshot-usage.md 说明；75 刻度与 M02 标签、25 刻度与 M24 标签最近处约 6.8-10px 但不重叠，已由 label_intersections 断言覆盖'
)
$a20.resume_notes = '2 次请求全部 POST /snapshot，200=2、失败 0、重试 0，限流余量 119，请求耗时之和 7193.7ms，收到 331030 字节。文档类请求 0 次：复用 A17 落盘的 tag-attrs.md 与既往 ai-guide/DSL/字体查证结果。交付 6 个产物：annotated-map.png/.snapshot（1600x1100，' + $pngB + '/' + $dslB + ' 字节，SHA-256 与服务响应逐字节相同）+ label-layout.json（' + (SizeOf "$exDir\label-layout.json") + ' 字节，24 个标签的逻辑坐标/像素锚点/标签盒/引导线折线/mapping）+ layout-audit.json（' + (SizeOf "$exDir\layout-audit.json") + ' 字节，11 组规则 2066 项断言 0 违规，visual_checks 三项 CONFIRMED）+ snapshot-usage.md + task-metrics.json。求解：px=280+x*10.4、py=920-y*7.6，主图区 (280,160) 1040x760；贪心候选求解 24/24 全部落位，超 24px 的 4 个标签（M09/M11/M08/M18）走正交折线引导，线线交叉 0（限 3）且不画连接点；中心 6 点两种口径一致 = M09/M08/M10/M12/M11/M06；Top-3 = M10=93、M08=91、M23=90。映射的「不要反转错误」用四角实测证明：(0,0)->(280,920) 左下、(100,0)->(1320,920) 右下、(0,100)->(280,160) 左上、(100,100)->(1320,160) 右上，4/4 通过，data_mirrored=false；替换掉了原先含义含混的 y_axis_flipped，v10 snapshot 与交付 v09 SHA-256 相同故未重渲染。看图 6 次，1 轮完整视觉迭代（看 v08 发现 2 处边距缺陷 -> 改 -> 渲染 v09 -> 像素复核）。墙钟 ' + $wallS + 's。'

# ------------------------------------------------------------------ A21 open -----
$a21 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a21) { throw "$NEXT entry not found" }
if ($a21.status -ne 'pending') { throw "$NEXT expected pending, found $($a21.status)" }
$a21.status      = 'in_progress'
$a21.started_at  = $closeTs
$a21.output_dir  = "outputs/$RUN/$NEXT/"
$a21.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000021.json"
$src.status          = 'in_progress'

# --------------------------------------------------------------- write state ------
[IO.File]::WriteAllText($STATE, ($src | ConvertTo-Json -Depth 12), $utf8)

# ----------------------------------------------------------------- events ---------
$evLines = New-Object System.Collections.Generic.List[string]
$ev39 = [ordered]@{
  seq  = 39
  ts   = $closeTs
  type = 'task_completed'
  task = $TASK
  artifacts = 6
  renders = 2
  views = 6
  visual_iterations = 1
  note = 'A20 密集标注题完成：6 个产物。annotated-map.png/.snapshot 1600x1100 为服务原始响应字节、SHA-256 与服务响应逐字节相同（' + $pngH.Substring(0,16) + '），PNG 尺寸由 IHDR 实读校验。2 次渲染 200=2、失败 0、重试 0，限流余量 119，请求耗时之和 7193.7ms，收到 331030 字节。映射 px=280+x*10.4 / py=920-y*7.6，主图区 (280,160) 1040x760 不翻转、锚点零移动；交付前把 label-layout 里含义含混的 y_axis_flipped 换成四个逻辑角到主图区角的实测（corner_checks 4/4 通过、data_mirrored=false、pixel_y_inversion_correct=true），对应题面「映射到像素时不要反转错误」要的是反转做对，v10 snapshot 与交付 v09 SHA-256 完全相同故不重渲染，v08/v09/v10 全部保留。24/24 点全部落位且每个标签含 id+名称+数值，正文 20px；超 24px 的 4 个标签走正交折线引导（DSL 无线段元素，用 2px Container 拼 L/Z 形），7 段线穿标签 0、连错点 0、线线交叉 0（限 3）且不画连接点；标签两两最小 7.9px（阈值 4）、标签离非本点最小 18px、归属最小优势 +6.94px、边界最小余量 274.5px；点圆最小边隙 11.86px 故未启用缩到 8px 的豁免。中心 6 点两种口径一致 = M09/M08/M10/M12/M11/M06，Top-3 = M10=93/M08=91/M23=90 以红环+琥珀底片+加粗+榜单四处标注；轴、0-100 量程、单位「指数」全部标注。layout-audit.json 11 组规则 2066 项断言 0 违规，visual_checks 三项 CONFIRMED。看图 6 次（先放大中心 6 点与引导线再看整体，按题面顺序），1 轮完整视觉迭代：看 v08 发现 y 题注左缘 x=8、右上注记右缘离画布仅 5px 两处真实缺陷 -> 改边距 -> 渲染 v09 -> 像素复核为 40/1558 且其余测量带不变。另有 7 次 read 返回串了缓冲区，如实计为失败尝试并改用 GDI+ 像素扫描复核，与快照服务无关。'
}
$ev40 = [ordered]@{
  seq  = 40
  ts   = $closeTs
  type = 'task_started'
  task = $NEXT
  note = 'A21 真实需求变更：双尺寸发布物，3 个预置轮次（round-01 本轮、rounds/round-02.md、rounds/round-03.md），minimum_final_pngs=6'
}
foreach ($e in @($ev39, $ev40)) {
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
  checkpoint_id    = 'state-000021'
  checkpoint_seq   = 21
  event_seq        = 40
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000021.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A20 关闭：6 个产物落盘，交付 PNG 经 IHDR 实读为 1600x1100 且与服务响应 SHA-256 相同。2 次渲染 200=2、0 失败 0 重试；24/24 标签、4 条正交折线引导、0 线线交叉、0 线穿标签、0 连错点；标签两两 7.9px、离非本点 18px、边界余量 274.5px；点圆最小边隙 11.86px 未启用缩点豁免。layout-audit 11 组规则 2066 项断言 0 违规，visual_checks 三项 CONFIRMED。看图 6 次，1 轮完整视觉迭代（v08 发现 2 处边距缺陷 -> v09 修复并像素复核）。suite-state.json 中 A20=completed、A21=in_progress。A21 于本时刻启动，3 个预置轮次。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000021.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), $utf8)

Write-Output "$TASK -> completed (ended_at $A20End)"
Write-Output "$NEXT -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 39 (task_completed $TASK), seq 40 (task_started $NEXT)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000021.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
Write-Output ("completed: " + ($completedIds -join ','))
Write-Output "final PNG ${w}x${h}  sha256=$($pngH.Substring(0,32))  dsl $dslB bytes"
Write-Output "audit problems=0  markers=$($layout.markers.Count)  requests=$($req.Count)  iterations=$($iters.Count)"
