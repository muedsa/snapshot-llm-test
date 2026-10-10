# close-a21-round01.ps1 - archive round-01, update suite-state.json (the live pointer),
# append the round_completed event and write immutable checkpoint state-000022.json.
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
$TASK      = 'A21'
$ROUND     = 'round-01'
$NEXT_ROUND = 'round-02'
$utf8      = [Text.UTF8Encoding]::new($false)

$ts = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

# ------------------------------------------------------------------ verify -------
$R = "outputs\$RUN\A21\round-01"
$required = @('launch-portrait.png', 'launch-portrait.snapshot', 'launch-wide.png',
              'launch-wide.snapshot', 'design-tokens.json', 'content-map.json',
              'snapshot-usage.md', 'task-metrics.json')
foreach ($f in $required) { if (-not (Test-Path "$R\$f")) { throw "round-01 missing $f" } }

function IhdrOf([string]$p) {
  $fs = [IO.File]::OpenRead((Resolve-Path $p).Path); $buf = New-Object byte[] 24
  [void]$fs.Read($buf, 0, 24); $fs.Close()
  return @{ w = [BitConverter]::ToUInt32(@($buf[19], $buf[18], $buf[17], $buf[16]), 0)
            h = [BitConverter]::ToUInt32(@($buf[23], $buf[22], $buf[21], $buf[20]), 0) }
}
$p = IhdrOf "$R\launch-portrait.png"; $w = IhdrOf "$R\launch-wide.png"
if ($p.w -ne 1080 -or $p.h -ne 1350) { throw "portrait is $($p.w)x$($p.h)" }
if ($w.w -ne 1440 -or $w.h -ne 810)  { throw "wide is $($w.w)x$($w.h)" }
foreach ($png in @('launch-portrait.png', 'launch-wide.png')) {
  $src = "tmp\$RUN\A21\" + ($png -replace '\.png$', '-r01.png')
  if ((Get-FileHash "$R\$png" -Algorithm SHA256).Hash -ne (Get-FileHash $src -Algorithm SHA256).Hash) {
    throw "$png is not byte-identical to the service response"
  }
}
foreach ($f in @('launch-portrait.snapshot', 'launch-wide.snapshot')) {
  $t = [IO.File]::ReadAllText("$R\$f", $utf8)
  if ($t -notmatch '^<Snapshot type="png"') { throw "$f root is not Snapshot" }
  if ($t -match '<Image') { throw "$f contains <Image" }
}
$probeP = Get-Content "tmp\$RUN\A21\probe-r1-portrait.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$probeW = Get-Content "tmp\$RUN\A21\probe-r1-wide.json"     -Raw -Encoding UTF8 | ConvertFrom-Json
if ($probeP.problems.Count -ne 0 -or $probeW.problems.Count -ne 0) { throw 'round-01 probes still report problems' }
if (@($probeP.reserved_band_checks + $probeW.reserved_band_checks | Where-Object { -not $_.empty }).Count) { throw 'a reserved band is not empty' }
$met = Get-Content "$R\task-metrics.json" -Raw -Encoding UTF8 | ConvertFrom-Json
if ($met.quality.deliverables_present -ne 8) { throw 'metrics say not all deliverables are present' }

# ------------------------------------------------------------- source state ------
$sourceJson = [IO.File]::ReadAllText($STATE, $utf8)
$src = $sourceJson | ConvertFrom-Json
$a21 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($a21.status -ne 'in_progress') { throw "A21 expected in_progress, found $($a21.status)" }
if (@($a21.completed_rounds).Count -ne 0) { throw 'round-01 already recorded' }

$base = "outputs/run-20261002-220723-mimo/A21/round-01/"
$a21.completed_rounds = @($ROUND)
$a21.artifacts = @($required | ForEach-Object { $base + $_ })
$a21.visual_review_evidence = @(
  ('{0}launch-portrait.png  整图 1080x1350（本地读取）：4 构件叠光标记、叠光 Layerlight 字标、ONLINE LAUNCH 主色胶囊、主标题「让复杂信息变得清晰」fs88 单行不裁切、副标题、分隔线、2026.11.07 19:30、讲者：林川 / 苏言、layerlight.example.org 全部到位；顶部 0..140 与底部 1156..1350 两条扩展带为空且没写占位文字' -f $base),
  "$base/launch-wide.png  整图 1440x810（本地读取）：左右双栏——左栏品牌与主张、右栏圆角信息面板三行信息，与竖版是两种不同构图（分别构图），顶部 0..110 与底部 670..810 为空",
  "tmp/run-20261002-220723-mimo/A21/v1-mark-portrait-01.png  竖版叠光标记 3x 放大 src[72,124,340,174]（本地读取）：靛蓝/淡紫/琥珀三个圆角方沿对角叠压、琥珀核心圆落在双层叠加区，4 构件可辨、重叠处亮度叠加可见",
  "tmp/run-20261002-220723-mimo/A21/v1-mark-wide-01.png  横版叠光标记 3x 放大 src[82,96,460,140]（本地读取）：与竖版同一套 4 构件、同一叠压顺序与颜色，仅整体 scale=0.8",
  "probe-a21.ps1  GDI+ 逐点实测：两图各 7 个 probe 全部命中声明背景（7/7、7/7），4 条保留带 non_background=0，最低对比度 5.63:1（竖）/ 5.52:1（横）；按约定不计入看图次数",
  "round-01/snapshot-usage.md + round-01/task-metrics.json  8/8 交付、2 渲染 200 失败 0 重试 0、看图 4 次、迭代 2 行（baseline 1 + syntax-fix 1），完整视觉迭代 0 次并说明原因"
)
$a21.unresolved_issues = @(
  '看图的精确时钟未被采集，iterations.jsonl 以 viewed_at_basis 记录可证明的时间窗，不编造单次看图时刻',
  'token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明原因',
  'requests.jsonl 中 A21-doc-000 是开工时经取文工具读取服务指南的记录，执行环境未暴露其起止时刻与字节数，按约定记 null；A21-doc-001 是同 URL 的带计时 GET，两者去重后仍是同一篇文档'
)
$a21.resume_notes = 'round-01 已归档（8 个产物）。2 次渲染 200=2、失败 0、重试 0，限流余量 119/118，渲染耗时之和 4148.6 ms、收到 144395 字节；另有 2 次文档 GET（同一 URL，1 次带计时 846.4 ms/3718 B，1 次时刻不可得记 null）。设计：主色 #5B4FE8、深色主题 #0E1026/#171A3C、字阶 title>date>deck>body>meta；品牌图形为 4 构件叠光标记（C1 靛蓝 / C2 淡紫 / C3 琥珀三个 88x88 r24 圆角方 + C4 琥珀核心圆），竖版 scale=1.0、横版 scale=0.8，相对几何与叠压顺序一致。竖版 1080x1350 单列纵向（x=88 宽 904），横版 1440x810 左右双栏（左 96 宽 760 / 右面板 904 宽 440），分别构图。主标题 fs88/72 均 >=56，其余最小 26 >=24；0 个 <Image>；顶部/底部 4 条扩展带经生成器逐块断言 + GDI+ 逐像素扫描双重确认为空。看图 4 次，完整视觉迭代 0（首版即合格，按约定不制造修改）。墙钟 1810387 ms。下一轮读 rounds/round-02.md：换长标题（<=3 行、>=48）、加赞助方与免费参加，保留日期/讲者/ONLINE LAUNCH/网址，主色与品牌形态不变，两尺寸不变，不许变形压窄文字。'

# --------------------------------------------------------------- top-level -------
$src.updated_at = $ts
$src.current_round = $NEXT_ROUND
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000022.json"
[IO.File]::WriteAllText($STATE, ($src | ConvertTo-Json -Depth 12), $utf8)

# ----------------------------------------------------------------- events --------
$ev = [ordered]@{
  seq = 41; ts = $ts; type = 'round_completed'; task = $TASK; round = $ROUND
  artifacts = 8; renders = 2; views = 4; visual_iterations = 0
  note = 'A21 round-01 归档：8 个产物落盘，两张 PNG 由 IHDR 实读为 1080x1350 / 1440x810 且与服务响应 SHA-256 逐字节相同（A41B1C2954A9C88D / BEAEFEB2D03C3AA0）。2 次渲染 200=2、失败 0、重试 0、限流余量 119/118，渲染耗时之和 4148.6 ms、144395 字节；文档 GET 2 次同一 URL（1 次带计时 846.4 ms，1 次时刻不可得记 null）。主色 #5B4FE8 深色主题，4 构件叠光标记在两版几何/颜色/叠压顺序一致（竖 1.0、横 0.8），两版分别构图（竖单列纵向、横左右双栏）。主标题 fs88/72 >=56，其余最小 26 >=24，0 个 <Image>，必含 5 条文案 + 品牌字标两图均在。顶部/底部 4 条扩展带由生成器逐块断言 + GDI+ 逐像素扫描双重确认 non_background=0，且未写任何待添加占位文字。两图各 7 个 probe 全部命中声明背景（14/14），最低对比度 5.63:1 / 5.52:1。看图 4 次（两图整图 + 两个标记 3x 放大）。完整视觉迭代 0 次：首版即满足全部要求，按总约定「一次合格时无需制造修改」不为凑迭代而改版；另有 1 行 syntax-fix（生成器汇总打印的 File::GetLength 方法名写错，发生在任何渲染之前、未影响交付）。suite-state 中 A21 completed_rounds=[round-01]、current_round=round-02。'
}
[IO.File]::AppendAllText($EVENTS, (([pscustomobject]$ev | ConvertTo-Json -Depth 6 -Compress) + "`n"), $utf8)

# ------------------------------------------------------------- checkpoint --------
$counts = @($src.tasks | Group-Object status | ForEach-Object { [pscustomobject]@{ status = $_.Name; count = $_.Count } })
$ckpt = [pscustomobject][ordered]@{
  schema_version = $src.suite_version; run_id = $RUN; profile = $src.profile
  status = $src.status; snapshot_at = $ts
  checkpoint_id = 'state-000022'; checkpoint_seq = 22; event_seq = 41
  current_task = $TASK; current_status = 'in_progress'
  current_round = $NEXT_ROUND
  last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000022.json"
  task_status_counts = $counts
  tasks_completed = @($src.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
  checkpoint_note = 'A21 round-01 关闭：8 个产物，PNG 尺寸经 IHDR 实读且与服务响应 SHA-256 相同，2 次渲染 200 失败 0 重试 0，主标题 88/72、正文最小 26、0 <Image>、4 条保留带为空（逐块断言 + 像素扫描）、probe 14/14、看图 4 次、完整视觉迭代 0（首版合格不制造修改）。suite-state 中 A21 completed_rounds=[round-01]，current_round=round-02，状态仍为 in_progress。'
  suite_state = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000022.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), $utf8)

"A21 round-01 -> completed at $ts"
"  artifacts   = 8   portrait $($p.w)x$($p.h)   wide $($w.w)x$($w.h)"
"  probes      = $($probeP.entries.Count + $probeW.entries.Count) all matched, 4 reserved bands empty"
"  events      + seq 41 (round_completed A21/round-01)"
"  suite-state current_round = $NEXT_ROUND   last_checkpoint = state-000022.json"
"  checkpoint  -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
"  task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', ')
