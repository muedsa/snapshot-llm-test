# close A19 / open A20 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000020.json.
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
$TASK      = 'A19'
$NEXT      = 'A20'
$utf8      = [Text.UTF8Encoding]::new($false)

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')

$metricsPath = "outputs\$RUN\A19\task-metrics.json"
$metrics = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($metricsPath, $utf8))
$A19End = [string]$metrics.ended_at
if ($A19End -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$') { throw "$TASK ended_at is not a timezone-carrying timestamp: $A19End" }
$wallS = [Math]::Round(($metrics.wall_clock_total_ms / 1000.0), 1)

$exDir = "outputs\$RUN\A19"
function HashOf([string]$f) { return (Get-FileHash $f -Algorithm SHA256).Hash }
function SizeOf([string]$f) { return (Get-Item $f).Length }

$gridPng = "$exDir\grid-scene.png"; $gridPngH = HashOf $gridPng; $gridPngB = SizeOf $gridPng
$gridDsl = "$exDir\grid-scene.snapshot"; $gridDslH = HashOf $gridDsl; $gridDslB = SizeOf $gridDsl
$occAPng = "$exDir\occlusion.png"; $occAPngH = HashOf $occAPng; $occAPngB = SizeOf $occAPng
$occADsl = "$exDir\occlusion.snapshot"; $occADslH = HashOf $occADsl; $occADslB = SizeOf $occADsl
$occBPng = "$exDir\occlusion-alternative.png"; $occBPngH = HashOf $occBPng; $occBPngB = SizeOf $occBPng
$occBDsl = "$exDir\occlusion-alternative.snapshot"; $occBDslH = HashOf $occBDsl; $occBDslB = SizeOf $occBDsl

if ($occAPngH -ne $occBPngH) { throw "the two occlusion PNGs are not byte-identical - equivalence claim would be false" }
if ($occADslH -eq $occBDslH) { throw "the two occlusion DSLs are identical - hidden content would not differ" }

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, $utf8)
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A19 close ---
$a19 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a19) { throw "$TASK entry not found in suite-state.json" }
if ($a19.status -ne 'in_progress') { throw "$TASK expected in_progress, found $($a19.status)" }

$base = "outputs/run-20261002-220723-mimo/A19/"
$a19.status     = 'completed'
$a19.ended_at   = $A19End
$a19.output_dir = "outputs/$RUN/A19/"
$a19.temp_dir   = "tmp/$RUN/A19/"
$a19.artifacts = @(
  $base + 'grid-scene.png',
  $base + 'grid-scene.snapshot',
  $base + 'occlusion.png',
  $base + 'occlusion.snapshot',
  $base + 'occlusion-alternative.png',
  $base + 'occlusion-alternative.snapshot',
  $base + 'scene-data.json',
  $base + 'questions.json',
  $base + 'answers.json',
  $base + 'equivalence.json',
  $base + 'snapshot-usage.md',
  $base + 'task-metrics.json',
  $base + 'final-audit.md'
)
$a19.visual_review_evidence = @(
  'tmp/run-20261002-220723-mimo/A19/grid-v01.png  基线：8x8=64 格每格恰好一个主体，颜色 16x4、形状 16x4、尺寸 21/21/22，每行 4 色 4 形，圆环孔为背景色且约 0.52x 外径，ID 全在主体外（间距>=27px）；但 ID 字高仅约 10-11px，作为诊断图偏小（委托子代理读取）',
  'tmp/run-20261002-220723-mimo/A19/grid-v02.png  ID 字号 14->16、字框 56x20->64x24：64 个标签墨迹框统一 22x12px、字高约 12px，100% 可读，标签与主体最小间距 39.8px，计数与行分布无回退（委托子代理读取）',
  'tmp/run-20261002-220723-mimo/A19/grid-v03.png  颜色与形状改为两个独立 64 格洗牌 + 拒绝采样：颜色x形状矩阵 blue[5/4/5/2] orange[3/6/2/5] green[5/2/4/5] purple[3/4/5/4]，16 种组合全部非零（v02 每行被锁成周期4配对、呈斜条纹，由实看几何表与矩阵发现），每行最小 3 色 3 形（本地读取）',
  'tmp/run-20261002-220723-mimo/A19/occ-a-v02.png  遮挡场景 A：面板不透明且只有自己的两行字，V01-V06 标签均在对象外，蓝条从面板左缘伸出并标注「可见部分」，底部说明未被裁切，无虚线/轮廓/阴影/半透明泄漏（委托子代理读取）',
  'outputs/run-20261002-220723-mimo/A19/grid-scene.png  交付件 1600x1600 原图（本地读取，逐项核对 64 格、标签、圆环孔、尺寸与行分布）',
  'outputs/run-20261002-220723-mimo/A19/occlusion.png  交付件 800x800 原图（本地读取）',
  'outputs/run-20261002-220723-mimo/A19/occlusion-alternative.png  交付件 800x800 原图（本地读取），与 A 肉眼完全一致',
  'equivalence.json  GDI+ LockBits 取回 RGBA 逐字节比较：640,000 像素 0 不同、0 字节不同、SHA-256 相同 ' + $occAPngH.Substring(0,16) + '...；DSL 共同前缀 7 行与共同后缀 68 行逐字节相同、隐藏块 9/15 行不同；隐藏层对象 A=3/B=4，完全覆盖 A=2/B=3；VERDICT EQUIVALENT',
  'final-audit.md  10 项必需交付物齐备、三张 PNG 的 PNG 魔数与尺寸、交付字节 SHA 与服务响应逐一对过、DSL 根标签且无 <Image> 无虚线构造、64 对象全部硬约束、14 题 5 两步 1 无法确定、每题都有坐标原点与比较标准、答案四要素齐全、编号 84>=18、等价性与隐藏内容交叉核对 —— problems = 0，87 项通过',
  'requests.jsonl  7 次渲染请求（200=5、400=2，两次 400 是真实的 PARSE_ERROR 并保留失败体），限流余量最低 118；iterations.jsonl 6 行（baseline 1 / visual 3 / syntax-fix 2），4 行带图，3 轮完整视觉迭代，7 次看图事件（委托 3 + 本地 4）'
)
$a19.unresolved_issues = @(
  '3 次委托看图的精确时钟未被采集；iterations.jsonl 以 viewed_at_basis 记录可证明的时间窗（渲染结束 -> 下一次渲染开始），不编造具体时刻',
  '1 次 general 子代理读图被提供方限流拒绝（Rate limit exceeded），随即改用本地读图完成同一次查看；这是看图通道的临时故障，不是快照服务故障，未影响任何渲染请求，failed_attempts 如实计 1',
  '「编号>=18」在 TASK.md 与 task.json 中与「12 道网格题 + 2 道遮挡题」同时出现，故不可能指题目数；按「带编号的实体至少 18 个」理解并在 questions.json/answers.json 的 numbering 块逐族给出实数（64+6+14=84），该解释与所有其他一致读法一并满足并已写明供复核',
  'token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明原因，不用字数或账号余量估造',
  '用户反馈等待时长：过程中确有一次用户续跑消息，但其到达时刻未被采集，记 null'
)
$a19.resume_notes = '7 次请求全部 POST /snapshot，200=5、400=2（两次均为真实的 PARSE_ERROR：$PANEL 与 $panel 大小写冲突导致列表内容被拼进 color 属性、以及 (a+b)/2 中点误写，失败响应体保留于 tmp/A19/failures/），0 限流、0 重试，请求耗时之和 22670.8ms，收到 391708 字节。文档类请求 0 次：复用 A17 保留的 ai-guide 与既往 DSL/字体查证结果。交付 13 个产物：grid-scene.png/.snapshot（1600x1600，' + $gridPngB + '/' + $gridDslB + ' 字节）+ occlusion.png/.snapshot（800x800，' + $occAPngB + '/' + $occADslB + ' 字节）+ occlusion-alternative.png/.snapshot（' + $occBPngB + '/' + $occBDslB + ' 字节）+ scene-data.json + questions.json + answers.json + equivalence.json + snapshot-usage.md + task-metrics.json + final-audit.md。三张交付 PNG 均为服务原始字节、无后处理，SHA 与被看的草稿渲染逐一对过。迭代 6 行（baseline 1 / visual 3 / syntax-fix 2），3 轮完整视觉迭代，看图 7 次（委托 3 + 本地 4）。网格 3 版（v01 基线、v02 字号、v03 独立洗牌交叉分布），遮挡 2 版（v01 语法失败、v02 成功）；A/B 两份 DSL 由同一脚本生成，共同部分逐字节相同。14 道题（12 网格 + 2 遮挡、5 道两步、1 道「无法确定」），答案由真实几何计算并对唯一性做断言，任一题多解即失败。equivalence.json 用 LockBits 证明 640000 像素 0 差异且 SHA 相同、而两份 DSL 隐藏块不同。首跑自检报 5 个问题（8 题缺比较标准、编号块被 $q/$Q 大小写冲突读空、equivalence 隐藏数传错几何），逐条定位根因修复后复跑 problems = 0、87 项通过。墙钟 ' + $wallS + 's。'

# ------------------------------------------------------------------ A20 open -----
$a20 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a20) { throw "$NEXT entry not found" }
if ($a20.status -ne 'pending') { throw "$NEXT expected pending, found $($a20.status)" }
$a20.status      = 'in_progress'
$a20.started_at  = $closeTs
$a20.output_dir  = "outputs/$RUN/$NEXT/"
$a20.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000020.json"
$src.status          = 'in_progress'

# --------------------------------------------------------------- write state ------
[IO.File]::WriteAllText($STATE, ($src | ConvertTo-Json -Depth 12), $utf8)

# ----------------------------------------------------------------- events ---------
$evLines = New-Object System.Collections.Generic.List[string]
$ev37 = [ordered]@{
  seq  = 37
  ts   = $closeTs
  type = 'task_completed'
  task = $TASK
  artifacts = 13
  renders = 7
  views = 7
  visual_iterations = 3
  note = 'A19 视觉题场完成：13 个产物。三张指定 PNG 均为服务真实响应且有同名 .snapshot，字节未做任何后处理（SHA 与草稿渲染逐一对过）。7 次请求 200=5、400=2（两次真实 PARSE_ERROR，失败体保留），限流余量最低 118，请求耗时之和 22670.8ms。网格 1600x1600：64 对象 G01-G64 每格一个，颜色与形状各 16、尺寸 21/21/22，每行至少 3 色 3 形，圆环内径为外径一半，ID 全在主体外；颜色与形状由两个独立 64 格洗牌 + 拒绝采样交叉，16 种组合全部出现。遮挡两张 800x800：同一脚本生成、共同部分逐字节相同，隐藏块 A 3 个/B 4 个对象（完全覆盖 2/3），LockBits 逐字节比较 640000 像素 0 差异、SHA-256 相同，VERDICT EQUIVALENT；面板不透明、无虚线轮廓阴影泄漏。题目 14 道（12 网格 + 2 遮挡），5 道两步、1 道「无法确定」，每题写明坐标原点与比较标准，答案由真实几何计算并断言唯一。编号 84>=18（64 个 G + 6 个 V + 14 个 Q）并在 numbering 块逐族列明。看图 7 次（委托 3 + 本地 4），3 轮完整视觉迭代。首跑自检 problems=5，逐条定位根因（8 题缺比较标准、$q/$Q 大小写冲突、equivalence 传错几何）修复后复跑 problems=0、87 项通过。'
}
$ev38 = [ordered]@{
  seq  = 38
  ts   = $closeTs
  type = 'task_started'
  task = $NEXT
  note = ''
}
foreach ($e in @($ev37, $ev38)) {
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
  checkpoint_id    = 'state-000020'
  checkpoint_seq   = 20
  event_seq        = 38
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000020.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A19 关闭：13 个产物落盘，三张 PNG 为服务原始字节，两张遮挡 PNG SHA-256 相同而两份 DSL 隐藏块不同，像素比较 0/640000 差异。7 次渲染请求（200=5、400=2 均为真实 PARSE_ERROR 并保留失败体），6 行 iterations，7 次看图事件，3 轮完整视觉迭代。14 道题答案由真实几何计算并断言唯一，1 道「无法确定」。首跑自检 problems=5 修复后复跑 problems=0（87 项）。suite-state.json 中 A19=completed、A20=in_progress。A20 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000020.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), $utf8)

Write-Output "$TASK -> completed (ended_at $A19End)"
Write-Output "$NEXT -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 37 (task_completed $TASK), seq 38 (task_started $NEXT)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000020.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
Write-Output ("completed: " + ($completedIds -join ','))
