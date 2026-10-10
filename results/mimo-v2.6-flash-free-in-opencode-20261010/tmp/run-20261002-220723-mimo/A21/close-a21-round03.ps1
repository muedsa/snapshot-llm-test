# close-a21-round03.ps1 - archive the final round, update suite-state.json,
# append event seq 43 and write immutable checkpoint state-000024.json.
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
$ROUND     = 'round-03'
$utf8      = [Text.UTF8Encoding]::new($false)
$ts = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

# ------------------------------------------------------------------ verify -------
$R = "outputs\$RUN\A21\round-03"
$r3files = @('launch-portrait.png', 'launch-portrait.snapshot', 'launch-wide.png',
             'launch-wide.snapshot', 'contrast-audit.json', 'contrast-audit-portrait.json',
             'contrast-audit-wide.json', 'design-tokens.json', 'content-map.json',
             'snapshot-usage.md', 'task-metrics.json')
foreach ($f in $r3files) { if (-not (Test-Path "$R\$f")) { throw "round-03 missing $f" } }

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
  $src = "tmp\$RUN\A21\" + ($png -replace '\.png$', '-r03.png')
  if ((Get-FileHash "$R\$png" -Algorithm SHA256).Hash -ne (Get-FileHash $src -Algorithm SHA256).Hash) {
    throw "$png is not byte-identical to the service response"
  }
}
foreach ($f in @('launch-portrait.snapshot', 'launch-wide.snapshot')) {
  $t = [IO.File]::ReadAllText("$R\$f", $utf8)
  if ($t -notmatch '^<Snapshot type="png"') { throw "$f root is not Snapshot" }
  if ($t -match '<Image') { throw "$f contains <Image" }
}

# PNG byte size must equal what requests.jsonl recorded for that render
$reqs = @(Get-Content "tmp\$RUN\A21\requests.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
foreach ($e in @(@{ id = 'A21r3-p01'; f = 'launch-portrait.png' }, @{ id = 'A21r3-w01'; f = 'launch-wide.png' })) {
  $resp = $reqs | Where-Object { $_.id -eq $e.id }
  if (-not $resp -or $resp.http_status -ne 200) { throw "$($e.id) not a 200" }
  if ($resp.bytes -ne (Get-Item "$R\$($e.f)").Length) { throw "$($e.f) differs from the recorded response bytes" }
}

# previous rounds untouched
$oldHashes = @{ 'round-01/launch-portrait.png' = 'A41B1C2954A9C88D6B9102327E000AF4'
                'round-01/launch-wide.png'     = 'BEAEFEB2D03C3AA0D69A6D2F75BAB68A'
                'round-02/launch-portrait.png' = 'F013863FB5E50783164AC44686249378'
                'round-02/launch-wide.png'     = 'A9B8F6D1E035323383DADDD9BAEAFAEC' }
foreach ($rn in @('round-01', 'round-02')) {
  foreach ($f in @('launch-portrait.png','launch-portrait.snapshot','launch-wide.png','launch-wide.snapshot',
                   'design-tokens.json','content-map.json','snapshot-usage.md','task-metrics.json')) {
    if (-not (Test-Path "outputs\$RUN\A21\$rn\$f")) { throw "$rn missing $f" }
  }
}
foreach ($k in $oldHashes.Keys) {
  $h = (Get-FileHash "outputs\$RUN\A21\$k" -Algorithm SHA256).Hash
  if (-not $h.StartsWith($oldHashes[$k])) { throw "$k changed: $h" }
}

# contrast audits
$ca = Get-Content "$R\contrast-audit.json" -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $ca.summary.pass) { throw 'contrast-audit.json summary.pass is not true' }
if (-not $ca.summary.entries_sufficient_per_image) { throw 'fewer than 6 entries for an image' }
if (-not $ca.summary.all_entries_ge_4_5) { throw 'an entry is below 4.5:1' }
foreach ($f in @('contrast-audit-portrait.json','contrast-audit-wide.json')) {
  $a = Get-Content "$R\$f" -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($a.entries.Count -lt 6) { throw "$f has only $($a.entries.Count) entries" }
  if (@($a.entries | Where-Object { $_.contrast_ratio -lt 4.5 }).Count) { throw "$f has an entry below 4.5" }
  if (@($a.problems).Count) { throw "$f reports problems" }
  if (@($a.reserved_band_checks | Where-Object { -not $_.empty }).Count) { throw "$f reserved band not empty" }
}
$met = Get-Content "$R\task-metrics.json" -Raw -Encoding UTF8 | ConvertFrom-Json
if ($met.quality.deliverables_present -ne 11) { throw 'metrics say not all deliverables are present' }

# ------------------------------------------------------------- source state ------
$sourceJson = [IO.File]::ReadAllText($STATE, $utf8)
$src = $sourceJson | ConvertFrom-Json
$a21 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($a21.status -ne 'in_progress') { throw "A21 expected in_progress, found $($a21.status)" }
if (@($a21.completed_rounds) -join ',' -ne 'round-01,round-02') { throw 'rounds 01+02 not both recorded' }

$b1 = "outputs/run-20261002-220723-mimo/A21/round-01/"
$b2 = "outputs/run-20261002-220723-mimo/A21/round-02/"
$b3 = "outputs/run-20261002-220723-mimo/A21/round-03/"
$f8 = @('launch-portrait.png','launch-portrait.snapshot','launch-wide.png','launch-wide.snapshot',
        'design-tokens.json','content-map.json','snapshot-usage.md','task-metrics.json')

$a21.completed_rounds = @('round-01', 'round-02', 'round-03')
$a21.artifacts = @( @($f8 | ForEach-Object { $b1 + $_ }) + @($f8 | ForEach-Object { $b2 + $_ }) +
                    @($r3files | ForEach-Object { $b3 + $_ }) )
$a21.visual_review_evidence = @($a21.visual_review_evidence) + @(
  "$b3/launch-portrait.png  整图 1080x1350（本地读取）：浅色主题页面 #F4F5FB 生效；bandA(#5B4FE81F) 垫在长标题+副标题下、bandB(#FFB02029) 垫在网址正上方的英语短句与网址下；「Clarity through structure」fs28 落在 layerlight.example.org 正上方；第二轮全部文案（长标题 2 行 fs56、副标题、2026.11.07 19:30、讲者：林川 / 苏言、ONLINE LAUNCH、赞助方 Northstar Research / 云构工具、免费参加 · 无需报名、网址）逐字保留；顶部 0..120 与底部 1180..1350 为空且没写占位文字",
  "$b3/launch-wide.png  整图 1440x810（本地读取）：左栏 bandA 包住长标题（fs52 2 行）与副标题，右栏白色面板内 bandB 包住英文短句与网址，赞助方仍在面板中部未消失；同一 bandB 在白色面板上实测 #FFF2DB、在页面上实测 #F5E9D7，两种不同合成色证明叠层真实参与；顶部 0..100 与底部 710..810 为空",
  "tmp/run-20261002-220723-mimo/A21/v3-mark-portrait-01.png  竖版叠光标记 3x 放大 src[72,104,340,174]（本地读取）：仍是同一套 4 构件、同一相对几何与叠压顺序、同一主色，仅底色由深变浅，品牌形态未变",
  "tmp/run-20261002-220723-mimo/A21/v3-mark-wide-01.png  横版叠光标记 3x 放大 src[82,86,460,140]（本地读取）：scale 仍为 0.8，与竖版同一套构件与叠压顺序",
  "round-03/contrast-audit.json（+ 逐图两份）  GDI+ 实测每个正文 probe 的最终像素，按 WCAG 2.1 用实测背景算比值：竖版 10 处、横版 10 处，各 >=6 处要求，全部 >=4.5:1，最低 5.63:1，problems 0，4 条保留带 non_background=0，最大通道差 1（8-bit 取整容差，对比度结论只用实测像素）；按约定像素扫描不计入看图次数",
  "$b3/snapshot-usage.md + $b3/task-metrics.json  11/11 交付、2 渲染 200 失败 0 重试 0、看图 4 次、本轮迭代 2 行（syntax-fix 1 + requirement-change 1）且完整视觉迭代 0，含 round-03.md 要求的视觉回归说明"
)
$a21.unresolved_issues = @(
  '看图的精确时钟未被采集，iterations.jsonl 以 viewed_at_basis 记录可证明的时间窗，不编造单次看图时刻',
  'token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明原因',
  'requests.jsonl 中 A21-doc-000 是开工时经取文工具读取服务指南的记录，执行环境未暴露其起止时刻与字节数，按约定记 null；A21-doc-001 是同 URL 的带计时 GET，两者去重后仍是同一篇文档',
  '参考合成色与实测像素存在每通道 <=1 的取整差，已在 contrast-audit.json 记录 max_channel_delta 与容差理由；对比度结论只依赖实测像素，不受该容差影响',
  '竖版长标题断行点落在「让复 / 杂信息」中间（CJK 允许任意位置断行），三轮一致；不影响行数与字号要求，也未使用任何变形压窄；如需按词断句需引入分词信息，各轮需求只约束行数与字号，故不处理'
)
$a21.resume_notes = '三轮全部归档（round-01 8 个、round-02 8 个、round-03 11 个，共 27 个产物）。round-03：2 次渲染 200=2、失败 0、重试 0，限流余量 119/118，渲染耗时之和 6143 ms、收到 229184 字节；本轮文档请求 0（复用 round-01 落盘件）。变更：浅色主题 #F4F5FB/#FFFFFF、新增 bandA(#5B4FE81F) 与 bandB(#FFB02029) 两条真半透明背景光带、网址正上方新增英语短句 Clarity through structure（竖 fs28 / 横 fs26，>=24）。未变：主色 #5B4FE8、4 构件叠光标记、1080x1350 与 1440x810、长标题 fs56/52 且 2 行 <=3 行、11 条必含文案、赞助方未消失。质量：每图 10 处正文对比度（>=6 要求）全部 >=4.5:1，最低 5.63:1，按实测像素计算；20/20 probe 命中声明背景，4 条保留带为空，0 个 <Image> 0 个 transform，0 problems。看图 4 次，完整视觉迭代 0。本轮修了 3 个生成器缺陷（PowerShell 逗号优先级高于乘法导致 Composite 的 @() 三元数组误解析、光带层描述缺冒号、自修出的多重开括号）与 1 个 layout-map 真错（title 的 probe 落在 bandA 内却只声明 page），全部留痕 A21r3-it01/it02。三轮墙钟累计见任务根 task-metrics.json。剩余：写任务根累计 snapshot-usage.md 与 task-metrics.json 后即可把 A21 标 completed 并转入 A22。'

# --------------------------------------------------------------- top-level -------
$src.updated_at = $ts
$src.current_round = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000024.json"
[IO.File]::WriteAllText($STATE, ($src | ConvertTo-Json -Depth 12), $utf8)

# ----------------------------------------------------------------- events --------
$ev = [ordered]@{
  seq = 43; ts = $ts; type = 'round_completed'; task = $TASK; round = $ROUND
  artifacts = 11; renders = 2; views = 4; visual_iterations = 0
  note = 'A21 round-03（末轮）归档：11 个产物落盘，PNG 经 IHDR 实读为 1080x1350 / 1440x810、字节数与 requests.jsonl 记录的响应一致（120058 / 109126，SHA-256 7F9497E8B17C04F9 / 9C626F24FB851980），.snapshot 根合法且 0 个 <Image>。2 次渲染 200=2、失败 0、重试 0、限流余量 119/118，渲染耗时之和 6143 ms、229184 字节；本轮文档请求 0。round-03.md 十三条逐条满足：浅色主题 #F4F5FB/#FFFFFF；新增 bandA 与 bandB 真半透明背景光带（同一 bandB 在页面实测 #F5E9D7、在白色面板实测 #FFF2DB，两种不同合成色证明叠层真实参与计算，不是只改两种颜色）；网址正上方新增 Clarity through structure（竖 y1046 在 url y1120 正上方、横 y552 在 y616 正上方，fs28/26 >=24）；第二轮全部文案与 4 构件品牌图形保留、赞助方未消失；两尺寸不变；长标题 56/52 >=48 且 2 行 <=3 行。contrast-audit.json（+ 逐图两份）每图 10 处正文（>=6 要求）全部按 GDI+ 实测像素的 WCAG 2.1 比值 >=4.5:1，最低 5.63:1，problems 0，4 条保留带为空，20/20 probe 命中，最大通道差 1（8-bit 取整容差，已记录理由）。视觉回归：坐标与字号除主题色/光带/新增 english 三处外与 round-02 逐项一致。修了 3 个生成器缺陷与 1 个 layout-map 真错（title 的 probe 落在 bandA 内却只声明 page，由真实像素审计发现），修完重新生成的 .snapshot 与首次 SHA-256 相同，DSL 未变故不重渲染。看图 4 次，完整视觉迭代 0。round-01/round-02 各 8 个文件齐全、四张 PNG 哈希未变。suite-state 中 A21 completed_rounds=[round-01, round-02, round-03]，current_round=null，状态仍为 in_progress（任务根累计报告与指标待写）。'
}
[IO.File]::AppendAllText($EVENTS, (([pscustomobject]$ev | ConvertTo-Json -Depth 6 -Compress) + "`n"), $utf8)

# ------------------------------------------------------------- checkpoint --------
$counts = @($src.tasks | Group-Object status | ForEach-Object { [pscustomobject]@{ status = $_.Name; count = $_.Count } })
$ckpt = [pscustomobject][ordered]@{
  schema_version = $src.suite_version; run_id = $RUN; profile = $src.profile
  status = $src.status; snapshot_at = $ts
  checkpoint_id = 'state-000024'; checkpoint_seq = 24; event_seq = 43
  current_task = $TASK; current_status = 'in_progress'
  current_round = $null
  all_rounds_done = $true
  last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000024.json"
  task_status_counts = $counts
  tasks_completed = @($src.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
  checkpoint_note = 'A21 三轮全部关闭（round-01 8 个、round-02 8 个、round-03 11 个 = 27 个产物）。round-03：浅色主题 + 两条真半透明背景光带 + 网址上方英语短句 Clarity through structure；每图 10 处正文对比度按实测像素全部 >=4.5:1（最低 5.63:1），problems 0；20/20 probe 命中、4 条保留带为空、0 <Image> 0 transform；2 渲染 200 失败 0 重试 0、6143 ms / 229184 B；看图 4 次、完整视觉迭代 0；round-01/02 各 8 文件齐全、四张 PNG 哈希未变。suite-state 中 A21 completed_rounds=[round-01, round-02, round-03]，current_round=null，状态仍 in_progress —— 任务根累计 snapshot-usage.md 与 task-metrics.json 尚未写，写完才能把 A21 标 completed 并转入 A22。'
  suite_state = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000024.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), $utf8)

"A21 round-03 -> completed at $ts"
"  artifacts   = 11 (round-01 8 + round-02 8)   portrait $($p.w)x$($p.h)   wide $($w.w)x$($w.h)"
"  contrast    = portrait 10 + wide 10 entries, all >= 4.5:1, min $($ca.summary.overall_min_contrast):1, problems 0"
"  probes      = 20 all matched, 4 reserved bands empty"
"  rounds 01/02 unchanged (A41B1C29 / BEAEFEB2 / F013863F / A9B8F6D1)"
"  events      + seq 43 (round_completed A21/round-03)"
"  suite-state current_round = <null> (all rounds done)   last_checkpoint = state-000024.json"
"  checkpoint  -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
"  task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', ')
