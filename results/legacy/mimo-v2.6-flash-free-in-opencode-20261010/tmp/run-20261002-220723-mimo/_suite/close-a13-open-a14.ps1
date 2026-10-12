# close A13 / open A14 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000014.json.
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
$TASK      = 'A13'
$NEXT      = 'A14'

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')
$A13End  = '2026-10-03T17:01:04+08:00'   # matches task-metrics.json ended_at exactly

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, [Text.UTF8Encoding]::new($false))
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A13 close ---
$a13 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a13) { throw "A13 entry not found in suite-state.json" }
if ($a13.status -ne 'in_progress') { throw "A13 expected in_progress, found $($a13.status)" }

$a13.status     = 'completed'
$a13.ended_at   = $A13End
$a13.output_dir = "outputs/$RUN/A13/"
$a13.temp_dir   = "tmp/$RUN/A13/"
$a13.artifacts = @(
  'outputs/run-20261002-220723-mimo/A13/symbol-color.png',
  'outputs/run-20261002-220723-mimo/A13/symbol-color.snapshot',
  'outputs/run-20261002-220723-mimo/A13/symbol-black.png',
  'outputs/run-20261002-220723-mimo/A13/symbol-black.snapshot',
  'outputs/run-20261002-220723-mimo/A13/brand-banner.png',
  'outputs/run-20261002-220723-mimo/A13/brand-banner.snapshot',
  'outputs/run-20261002-220723-mimo/A13/launch-poster.png',
  'outputs/run-20261002-220723-mimo/A13/launch-poster.snapshot',
  'outputs/run-20261002-220723-mimo/A13/brand-system.json',
  'outputs/run-20261002-220723-mimo/A13/rationale.md',
  'outputs/run-20261002-220723-mimo/A13/brand-audit.json',
  'outputs/run-20261002-220723-mimo/A13/snapshot-usage.md',
  'outputs/run-20261002-220723-mimo/A13/task-metrics.json'
)
$a13.visual_review_evidence = @(
  'tmp/run-20261002-220723-mimo/A13/preview-a-layers.png  方向A首稿整图：三道光带沿自身轴线偏移，塌成一条共线长条 —— 必须看图才能发现',
  'tmp/run-20261002-220723-mimo/A13/preview-b-rings.png  方向B首稿整图：圆环内出现一颗偏心墨点，看起来像失误',
  'tmp/run-20261002-220723-mimo/A13/preview-a-layers-v2.png + preview-b-rings-v2.png  两方向修正版整图：A 为三条平行胶囊、四边留白 74px；B 为双环、留白 76px',
  'tmp/run-20261002-220723-mimo/A13/preview-a-layers-v2-thumb32.png + preview-b-rings-v2-thumb32.png  两方向 32x32 缩略：A 仍保三条独立光带与两条通透通道；B 两孔在交叠处压到约 2.6px 而发糊 —— 据此选定方向A',
  'tmp/run-20261002-220723-mimo/A13/render-01-symbol-color.png + render-01-brand-banner.png  首轮终图整图：标记整体平移 (+6.4,+103.4) 并被底边裁切，根因是 Transform origin 写成盒子尺寸 (256,88) 而非光带中心 (128,44)',
  'tmp/run-20261002-220723-mimo/A13/render-02-symbol-color.png  修正后图标整图：居中，四边留白 66px',
  'tmp/run-20261002-220723-mimo/A13/render-02-symbol-black.png  黑色图标整图：形状与彩色版一致，视觉上无差异',
  'tmp/run-20261002-220723-mimo/A13/render-02-brand-banner.png  横幅整图：标记、分隔线、字标、副标题四者共用一条视觉中线，无文字重叠',
  'tmp/run-20261002-220723-mimo/A13/render-02-launch-poster.png  海报整图：五条必需文案齐全；发现上边距 214px 大于下边距 180px，构图偏低',
  'tmp/run-20261002-220723-mimo/A13/render-02-symbol-color-native32.png  服务端 32x32 原生渲染：仍是三条光带、两条通道',
  'tmp/run-20261002-220723-mimo/A13/symbol-color-thumb32.png + symbol-black-thumb32.png  交付版 32x32 缩略：两版均为三条独立斜向笔画，通道张开（5.65px 笔画 / 1.4px 通道）',
  'tmp/run-20261002-220723-mimo/A13/render-03-launch-poster.png  上移 24px 后的海报整图：上边距 190px、下边距 204px，下大于上',
  'outputs/run-20261002-220723-mimo/A13/symbol-color.png / symbol-black.png / brand-banner.png  交付件原图：与被审渲染件 SHA256 逐字节一致',
  'outputs/run-20261002-220723-mimo/A13/launch-poster.png  交付件原图（v3 替换后重新打开确认）',
  'outputs/run-20261002-220723-mimo/A13/brand-audit.json  verify.ps1 产出：29/29 PASS（P5 A2 K2 G1 M1 S5 C7 N4 H2），其中 M/S/G/K 为真实像素扫描结果'
)
$a13.unresolved_issues = @(
  '看图时刻未单独埋点，iterations.jsonl 中 15 行视觉类记录的 started_at/ended_at/duration_ms 记 null，改用 anchored_after_request（其后首个请求的真实结束时刻）定位区间，不编造时刻',
  '两枚图标的 alpha 有 872 个软边像素相差 1 个级别（#38BDF8/#F6B94A 与 #000000 的预乘舍入差异），并非几何不一致；校验按"实心覆盖差 0 像素 + 抖动 ≤1"判定，已在 brand-system.json 与 snapshot-usage.md 中写明',
  '横幅右侧 10% alpha 水印只出了一版，未做强度 A/B；其余三件均未出现需要二次迭代的视觉缺陷',
  'rationale.md 以三种口径同时报告字数（含换行 299 / 非空白 267 / 汉字及全角 206），因"≤300字"的计数口径存在歧义',
  '共享准备阶段的文档/字体请求日志 started_utc/ended_utc 为 null，本题因此不填写其具体访问时刻；本题新增文档/字体请求为 0',
  '标记的最小应用场景（如 favicon 16x16、单色印刷最小线宽）未在本题交付范围内实测'
)
$a13.resume_notes = '20 个 POST /snapshot 全部 200（0 失败、0 重试）：5 探针 + 4 方向预览 + 3 轮终稿（01/02/03，第 03 轮仅重渲变更的海报）。512x512 透明彩色图标、512x512 透明纯黑图标、1200x400 横幅、1080x1350 海报共 4 张终图 + 4 份同名 .snapshot + brand-system.json + rationale.md（299/267/206 三口径均 ≤300）+ brand-audit.json（29/29 PASS）+ snapshot-usage.md + task-metrics.json，共 13 个产物，SHA256 与尺寸逐个复核一致。23 行 iterations（probe5 / baseline1 / visual_view8 / incomplete_visual4 / fix3 / checker2），21 次看图，4 轮真实视觉迭代：方向A塌线、方向B杂点、origin 写错致整体平移裁切、海报上下留白颠倒。横幅与海报内的标记由 Get-Bars 按 176/300/360 三种倍率重新发射，无 Image/base64/URL/transform/scale。字体与文档 0 新请求。请求耗时之和 40998.6ms，墙钟 4014.6s。'

# ------------------------------------------------------------------ A14 open -----
$a14 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a14) { throw "$NEXT entry not found" }
if ($a14.status -ne 'pending') { throw "$NEXT expected pending, found $($a14.status)" }
$a14.status      = 'in_progress'
$a14.started_at  = $closeTs
$a14.output_dir  = "outputs/$RUN/$NEXT/"
$a14.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000014.json"
$src.status          = 'in_progress'

# --------------------------------------------------------------- write state ------
$stateText = $src | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText($STATE, $stateText, [Text.UTF8Encoding]::new($false))

# ----------------------------------------------------------------- events ---------
$evLines = New-Object System.Collections.Generic.List[string]
$ev25 = [ordered]@{
  seq  = 25
  ts   = $closeTs
  type = 'task_completed'
  task = $TASK
  artifacts = 13
  renders = 20
  views = 21
  visual_iterations = 4
  note = 'A13 品牌交付完成：symbol-color.png / symbol-black.png（均 512x512 透明）、brand-banner.png（1200x400）、launch-poster.png（1080x1350）四张 PNG + 四份同名 .snapshot（与被渲染版本逐字节 SHA256 一致）+ brand-system.json + rationale.md + brand-audit.json + snapshot-usage.md + task-metrics.json。20 次渲染全部 200，0 失败 0 重试：5 探针、4 方向预览、3 轮终稿。两方向先各出一版并看 32x32 缩略后选定 A（三道 45 度平行胶囊）。4 轮真实视觉迭代：方向A塌成共线长条、方向B杂点、Transform origin 写成盒子尺寸导致整体平移 (+6.4,+103.4) 并被裁切、海报上边距 214 > 下边距 180。brand-audit.json 29/29 PASS，含四边留白 66px(12.89%)、三带两通道、黑色图标 A>0 处 RGB 全 0、两图标实心覆盖差 0 像素、7 条必需文案逐字、4 份 DSL 无位图嵌入、横幅/海报共用同一 45 度规则。task-metrics.ended_at = ' + $A13End + '（本事件时刻为状态落盘时刻）。'
}
$ev26 = [ordered]@{
  seq  = 26
  ts   = $closeTs
  type = 'task_started'
  task = $NEXT
  note = ''
}
foreach ($e in @($ev25, $ev26)) {
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
  checkpoint_id    = 'state-000014'
  checkpoint_seq   = 14
  event_seq        = 26
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000014.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A13 关闭：四张终图（512x512 透明彩色图标、512x512 透明纯黑图标、1200x400 横幅、1080x1350 海报）+ 四份同名 .snapshot + brand-system.json + rationale.md + brand-audit.json（29/29 PASS）+ snapshot-usage.md + task-metrics.json 共 13 个产物全部落盘，SHA256/尺寸逐个复核一致。20 次渲染全部 200，0 失败 0 重试；3 轮终稿；21 次看图；4 轮真实视觉迭代。suite-state.json 中 A13=completed、A14=in_progress。A14 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000014.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), [Text.UTF8Encoding]::new($false))

Write-Output "A13 -> completed (ended_at $A13End)"
Write-Output "A14 -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 25 (task_completed A13), seq 26 (task_started A14)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000014.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
