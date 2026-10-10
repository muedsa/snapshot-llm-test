# close-a21-round02.ps1 - archive round-02, update suite-state.json (the live pointer),
# append the round_completed event and write immutable checkpoint state-000023.json.
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
$ROUND     = 'round-02'
$NEXT_ROUND = 'round-03'
$utf8      = [Text.UTF8Encoding]::new($false)

$ts = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

# ------------------------------------------------------------------ verify -------
$R  = "outputs\$RUN\A21\round-02"
$R1 = "outputs\$RUN\A21\round-01"
$required = @('launch-portrait.png', 'launch-portrait.snapshot', 'launch-wide.png',
              'launch-wide.snapshot', 'design-tokens.json', 'content-map.json',
              'snapshot-usage.md', 'task-metrics.json')
foreach ($f in $required) { if (-not (Test-Path "$R\$f"))  { throw "round-02 missing $f" } }
foreach ($f in $required) { if (-not (Test-Path "$R1\$f")) { throw "round-01 was disturbed: $f missing" } }

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
  $src = "tmp\$RUN\A21\" + ($png -replace '\.png$', '-r02.png')
  if ((Get-FileHash "$R\$png" -Algorithm SHA256).Hash -ne (Get-FileHash $src -Algorithm SHA256).Hash) {
    throw "$png is not byte-identical to the service response"
  }
}
foreach ($f in @('launch-portrait.snapshot', 'launch-wide.snapshot')) {
  $t = [IO.File]::ReadAllText("$R\$f", $utf8)
  if ($t -notmatch '^<Snapshot type="png"') { throw "$f root is not Snapshot" }
  if ($t -match '<Image') { throw "$f contains <Image" }
}
# round-01 PNGs must still carry the hashes recorded when they were closed
$oldHashes = @{ 'launch-portrait.png' = 'A41B1C2954A9C88D6B9102327E000AF4'
                'launch-wide.png'     = 'BEAEFEB2D03C3AA0D69A6D2F75BAB68A' }
foreach ($k in $oldHashes.Keys) {
  $h = (Get-FileHash "$R1\$k" -Algorithm SHA256).Hash
  if (-not $h.StartsWith($oldHashes[$k])) { throw "round-01 $k changed: $h" }
}

$probeP = Get-Content "tmp\$RUN\A21\probe-r2-portrait.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$probeW = Get-Content "tmp\$RUN\A21\probe-r2-wide.json"     -Raw -Encoding UTF8 | ConvertFrom-Json
if ($probeP.problems.Count -ne 0 -or $probeW.problems.Count -ne 0) { throw 'round-02 probes still report problems' }
if (@($probeP.reserved_band_checks + $probeW.reserved_band_checks | Where-Object { -not $_.empty }).Count) { throw 'a reserved band is not empty' }
$met = Get-Content "$R\task-metrics.json" -Raw -Encoding UTF8 | ConvertFrom-Json
if ($met.quality.deliverables_present -ne 8) { throw 'metrics say not all deliverables are present' }

# ------------------------------------------------------------- source state ------
$sourceJson = [IO.File]::ReadAllText($STATE, $utf8)
$src = $sourceJson | ConvertFrom-Json
$a21 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($a21.status -ne 'in_progress') { throw "A21 expected in_progress, found $($a21.status)" }
if (@($a21.completed_rounds) -notcontains 'round-01') { throw 'round-01 not recorded yet' }
if (@($a21.completed_rounds) -contains $ROUND) { throw "$ROUND already recorded" }

$base1 = "outputs/run-20261002-220723-mimo/A21/round-01/"
$base2 = "outputs/run-20261002-220723-mimo/A21/round-02/"
$a21.completed_rounds = @('round-01', 'round-02')
$a21.artifacts = @( @($required | ForEach-Object { $base1 + $_ }) + @($required | ForEach-Object { $base2 + $_ }) )
$a21.visual_review_evidence = @($a21.visual_review_evidence) + @(
  "$base2/launch-portrait.png  整图 1080x1350（本地读取）：27 字长标题「当所有信息都想成为标题：让复杂信息变得清晰的结构化方法」排成 2 行、fs56>=48 且 <=3 行、不裁切不压窄；副标题独立成行「让复杂信息变得清晰」；赞助方「Northstar Research / 云构工具」与「免费参加 · 无需报名」胶囊落在 880..1006，与标题 370..570 相隔 310 px 不碰撞；日期/讲者/ONLINE LAUNCH/网址四条原内容逐字保留；顶部 0..120 与底部 1092..1350 为空且没写占位文字",
  "$base2/launch-wide.png  整图 1440x810（本地读取）：长标题只占左栏 310..490（2 行 fs52），新增赞助方与胶囊放进右侧信息面板 340..502——两栏水平相隔 48 px、纵向不相交，长标题与新增信息分属不同列物理上不可能碰撞；面板自上而下日期/讲者/赞助方(折 2 行)/胶囊/网址；顶部 0..100 与底部 710..810 为空",
  "tmp/run-20261002-220723-mimo/A21/v2-mark-portrait-01.png  竖版叠光标记 3x 放大 src[72,104,340,174]（本地读取）：与 round-01 同一套 4 构件，相对几何/颜色/叠压顺序一致，仅整体上移 20 px（markY 140->120），形态未变",
  "tmp/run-20261002-220723-mimo/A21/v2-mark-wide-01.png  横版叠光标记 3x 放大 src[82,86,460,140]（本地读取）：scale 仍为 0.8，同一套 4 构件、同一叠压顺序",
  "probe-a21.ps1  GDI+ 逐点实测：两图各 9 个 probe 全部命中声明背景（9/9、9/9），4 条保留带 non_background=0，最低对比度 5.63:1（竖）/ 5.52:1（横）；按约定不计入看图次数",
  "round-02/snapshot-usage.md + round-02/task-metrics.json  8/8 交付、2 渲染 200 失败 0 重试 0、看图 4 次、本轮迭代 1 行（requirement-change）且完整视觉迭代 0，含 round-02.md 要求的「如何避免长标题与新增信息碰撞」四道手段"
)
$a21.unresolved_issues = @(
  '看图的精确时钟未被采集，iterations.jsonl 以 viewed_at_basis 记录可证明的时间窗，不编造单次看图时刻',
  'token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明原因',
  'requests.jsonl 中 A21-doc-000 是开工时经取文工具读取服务指南的记录，执行环境未暴露其起止时刻与字节数，按约定记 null；A21-doc-001 是同 URL 的带计时 GET，两者去重后仍是同一篇文档',
  '竖版长标题的断行点落在「让复 / 杂信息」中间（CJK 允许任意位置断行）。不影响行数与字号要求，也未使用任何变形压窄；如需按词断句需引入分词信息，round-02.md 只约束行数与字号，故不处理'
)
$a21.resume_notes = 'round-01 与 round-02 均已归档（各 8 个产物，共 16）。round-02：2 次渲染 200=2、失败 0、重试 0，限流余量 119/118，渲染耗时之和 5554.6 ms、收到 214035 字节；本轮无文档请求（复用 round-01 已落盘的服务指南与 DSL/字体缓存）。变更：主标题换为 27 字长标题（竖版 fs56 / 横版 fs52，均 >=48、2 行 <=3 行，框高加到 200/180 以容纳多出的行），副标题改为 round-01 核心句使其仍是独立 text 节点，新增赞助方行与「免费参加 · 无需报名」胶囊。未变：主色 #5B4FE8、深色主题、4 构件叠光标记（仅整体上移 20 px）、1080x1350 与 1440x810 两尺寸、11 条必含文案、字体层级。避免碰撞的四道手段：绝对定位固定框（加行不顶开别人）、长标题与新增信息分属不同坐标区间/不同列（竖版相隔 310 px、横版左右两栏隔离）、maxLines=3 + 固定框高封顶、生成器逐块断言 y>=top 且 y+h<=bottom 再由 GDI+ 扫四条保留带。质量：18/18 probe 命中、4 条保留带为空、0 个 <Image>、最小字号 26>=24、0 transform 不压窄、round-01 哈希校验未变。看图 4 次，完整视觉迭代 0（首版合格不制造修改）。墙钟 444703 ms。下一轮读 rounds/round-03.md：改浅色主题、加英文短句「Clarity through structure」于网址正上方，保留 round-02 的全部文案与品牌形态，两尺寸不变。'

# --------------------------------------------------------------- top-level -------
$src.updated_at = $ts
$src.current_round = $NEXT_ROUND
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000023.json"
[IO.File]::WriteAllText($STATE, ($src | ConvertTo-Json -Depth 12), $utf8)

# ----------------------------------------------------------------- events --------
$ev = [ordered]@{
  seq = 42; ts = $ts; type = 'round_completed'; task = $TASK; round = $ROUND
  artifacts = 8; renders = 2; views = 4; visual_iterations = 0
  note = 'A21 round-02 归档：8 个产物落盘，两张 PNG 由 IHDR 实读为 1080x1350 / 1440x810 且与服务响应 SHA-256 逐字节相同（F013863FB5E50783164 / A9B8F6D1E0353233）。2 次渲染 200=2、失败 0、重试 0、限流余量 119/118，渲染耗时之和 5554.6 ms、214035 字节；本轮文档请求 0（复用 round-01 落盘的服务指南与 DSL/字体缓存）。round-02.md 十二条逐条满足：长标题 27 字竖版 fs56 / 横版 fs52 均 >=48 且 2 行 <=3 行，新增赞助方 Northstar Research / 云构工具 与 免费参加 · 无需报名，日期/讲者/ONLINE LAUNCH/网址逐字保留，主色 #5B4FE8 与 4 构件品牌形态不变（仅按允许整体上移 20 px），两尺寸不变，0 个 transform 不压窄文字，round-01 八个文件齐全且哈希前缀 A41B1C2954A9C88D / BEAEFEB2D03C3AA0 未变。避免长标题与新增信息碰撞的四道独立手段：绝对定位固定框、竖版分属 y370..570 与 y880..1006（相隔 310 px）/ 横版分属左右两栏（水平相隔 48 px）、maxLines=3 + 固定框高封顶、生成器逐块断言 + GDI+ 扫四条保留带。质量：18/18 probe 命中声明背景、4 条保留带 non_background=0、最小字号 26>=24、11 条必含文案两图全在、0 problems。看图 4 次（两图整图 + 两个标记 3x 放大）。完整视觉迭代 0：首版即合格，按总约定不制造修改；本轮 requirement-change 1 行（A21r2-it01），任务级 3 行 syntax-fix 均属 round-01 脚本缺陷、不产生图。suite-state 中 A21 completed_rounds=[round-01, round-02]、current_round=round-03。'
}
[IO.File]::AppendAllText($EVENTS, (([pscustomobject]$ev | ConvertTo-Json -Depth 6 -Compress) + "`n"), $utf8)

# ------------------------------------------------------------- checkpoint --------
$counts = @($src.tasks | Group-Object status | ForEach-Object { [pscustomobject]@{ status = $_.Name; count = $_.Count } })
$ckpt = [pscustomobject][ordered]@{
  schema_version = $src.suite_version; run_id = $RUN; profile = $src.profile
  status = $src.status; snapshot_at = $ts
  checkpoint_id = 'state-000023'; checkpoint_seq = 23; event_seq = 42
  current_task = $TASK; current_status = 'in_progress'
  current_round = $NEXT_ROUND
  last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000023.json"
  task_status_counts = $counts
  tasks_completed = @($src.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
  checkpoint_note = 'A21 round-02 关闭：8 个产物，PNG 尺寸经 IHDR 实读且与服务响应 SHA-256 相同，2 次渲染 200 失败 0 重试 0，长标题 27 字 56/52 均 >=48 且 2 行 <=3 行，新增赞助方与免费参加胶囊，11 条必含文案两图全在，0 <Image> 0 transform，主色与 4 构件品牌形态不变（仅上移 20 px），两尺寸不变，round-01 八文件齐全哈希未变，18/18 probe 命中、4 条保留带为空，看图 4 次，完整视觉迭代 0（首版合格不制造修改）。suite-state 中 A21 completed_rounds=[round-01, round-02]，current_round=round-03，状态仍为 in_progress。'
  suite_state = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000023.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), $utf8)

"A21 round-02 -> completed at $ts"
"  artifacts   = 8 (round-01 still 8)   portrait $($p.w)x$($p.h)   wide $($w.w)x$($w.h)"
"  probes      = $($probeP.entries.Count + $probeW.entries.Count) all matched, 4 reserved bands empty"
"  round-01    hashes unchanged (A41B1C2954A9C88D / BEAEFEB2D03C3AA0)"
"  events      + seq 42 (round_completed A21/round-02)"
"  suite-state current_round = $NEXT_ROUND   last_checkpoint = state-000023.json"
"  checkpoint  -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
"  task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', ')
