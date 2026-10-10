# promote-a21-r02.ps1 - byte-copy the round-02 renders into round-02/, verify they are the
# untouched service responses, and append the round-02 iteration row.
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$out = "outputs\$RUN\A21\round-02"
$utf8 = New-Object System.Text.UTF8Encoding($false)

$pairs = @(
  @{ src = "$tmp\launch-portrait-r02.png"; dst = "$out\launch-portrait.png"; w = 1080; h = 1350 },
  @{ src = "$tmp\launch-wide-r02.png";     dst = "$out\launch-wide.png";     w = 1440; h = 810  }
)
$rows = @()
foreach ($p in $pairs) {
  Copy-Item $p.src $p.dst -Force
  $hSrc = (Get-FileHash $p.src -Algorithm SHA256).Hash
  $hDst = (Get-FileHash $p.dst -Algorithm SHA256).Hash
  if ($hSrc -ne $hDst) { throw "copy differs from source: $($p.dst)" }
  $fs = [IO.File]::OpenRead((Resolve-Path $p.dst).Path); $buf = New-Object byte[] 24
  [void]$fs.Read($buf, 0, 24); $fs.Close()
  $iw = [BitConverter]::ToUInt32(@($buf[19], $buf[18], $buf[17], $buf[16]), 0)
  $ih = [BitConverter]::ToUInt32(@($buf[23], $buf[22], $buf[21], $buf[20]), 0)
  if ($iw -ne $p.w -or $ih -ne $p.h) { throw "$($p.dst) is ${iw}x${ih}, expected $($p.w)x$($p.h)" }
  $rows += [pscustomobject]@{ name = (Split-Path $p.dst -Leaf); w = $iw; h = $ih; bytes = (Get-Item $p.dst).Length; sha256 = $hDst }
}
foreach ($f in @('launch-portrait.snapshot', 'launch-wide.snapshot')) {
  $fp = Join-Path $out $f
  if (-not (Test-Path $fp)) { throw "missing $f" }
  $txt = [IO.File]::ReadAllText($fp, $utf8)
  if ($txt -notmatch '^<Snapshot type="png"') { throw "$f is not a Snapshot root" }
  if ($txt -match '<Image') { throw "$f contains <Image" }
}

$probeP = Get-Content "$tmp\probe-r2-portrait.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$probeW = Get-Content "$tmp\probe-r2-wide.json"     -Raw -Encoding UTF8 | ConvertFrom-Json
if ($probeP.problems.Count -ne 0 -or $probeW.problems.Count -ne 0) { throw 'round-02 probes report problems' }
if (@($probeP.reserved_band_checks + $probeW.reserved_band_checks | Where-Object { -not $_.empty }).Count) { throw 'a reserved band is not empty' }

# ---- round-01 must still be intact -------------------------------------------------
foreach ($f in @('launch-portrait.png', 'launch-wide.png', 'launch-portrait.snapshot',
                 'launch-wide.snapshot', 'design-tokens.json', 'content-map.json',
                 'snapshot-usage.md', 'task-metrics.json')) {
  if (-not (Test-Path "outputs\$RUN\A21\round-01\$f")) { throw "round-01 was disturbed: $f missing" }
}
$before = 'A41B1C2954A9C88D6B9102327E000AF4'   # first 32 hex chars recorded when round-01 was closed
$h01 = (Get-FileHash "outputs\$RUN\A21\round-01\launch-portrait.png" -Algorithm SHA256).Hash
if (-not $h01.StartsWith($before)) { throw "round-01 portrait changed: $h01" }

# ---- iteration row -----------------------------------------------------------------
$renderRows = @(Get-Content "$tmp\requests.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
$pEnd = ($renderRows | Where-Object { $_.id -eq 'A21r2-p01' }).ended_utc
$wEnd = ($renderRows | Where-Object { $_.id -eq 'A21r2-w01' }).ended_utc
$now  = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')

$it = [ordered]@{
  id = 'A21r2-it01'; task = 'A21'; round = 2
  parent = 'A21r1-it01'
  type = 'requirement-change'
  created_utc = $now; tz = 'UTC'
  image_paths = @(
    "$tmp/launch-portrait-r02.png", "$tmp/launch-wide-r02.png",
    "$tmp/v2-mark-portrait-01.png", "$tmp/v2-mark-wide-01.png",
    "outputs/$RUN/A21/round-02/launch-portrait.png", "outputs/$RUN/A21/round-02/launch-wide.png")
  rendered_after = @($pEnd, $wEnd)
  viewed_at_basis = "看图发生在两次渲染完成 ($pEnd / $wEnd) 与本轮归档时刻 ($now) 之间；执行环境不采集单次看图的精确时钟，按约定以可证明的时间窗记录，不编造时刻"
  viewed_with = 'local image read (whole frame x2, brand-mark zoom x2) + GDI+ pixel probe'
  observed = @(
    '竖版：长标题「当所有信息都想成为标题：让复杂信息变得清晰的结构化方法」27 字排成 2 行（上限 3 行）、fs56 >=48，未裁切未压窄；下方副标题独立成行「让复杂信息变得清晰」，保证 round-01 的核心句仍是独立 text 节点',
    '竖版：新增的赞助方「Northstar Research / 云构工具」与「免费参加 · 无需报名」主色胶囊落在分隔线以下的 880..1006 区间，与标题 370..570 相距 310 px，完全不碰撞；日期、讲者、ONLINE LAUNCH、网址四条原内容逐字保留',
    '横版：长标题只占左栏 310..490（2 行、fs52 >=48），新增赞助方与胶囊放进右侧信息面板 340..502——两栏空间天然隔离，长标题与新增信息分属不同列，物理上不可能碰撞',
    '两个叠光标记放大后与 round-01 逐项比对：仍是同一套 4 构件（靛蓝 / 淡紫 / 琥珀三个 88x88 r24 圆角方 + 琥珀核心圆），相对几何、颜色、叠压顺序完全一致，只按「允许移动和缩放装饰」整体上移 20 px（竖版 markY 140 -> 120、横版 110 -> 100），形态未变',
    'GDI+ 逐点采样：两图各 9 个 probe 全部命中声明背景（9/9、9/9），4 条保留带 non_background=0；最低对比度 5.63:1（竖）/ 5.52:1（横）；1080x1350 与 1440x810 尺寸由 IHDR 实读确认'
  )
  changes = @(
    '主标题替换为 27 字长标题，maxLines=3、竖版 fs56 / 横版 fs52（均 >=48），并把标题框加高到 200 / 180 px 以容纳 2 行而不挤压后续块',
    '新增赞助方行（竖版 880 / 横版面板 340）与「免费参加 · 无需报名」主色胶囊（竖版 950 / 横版 450）',
    '为给新增信息腾出空间，副标题/分隔线/日期/讲者/网址整体下移（竖版）或改由面板承接（横版），底部保留带上边界相应下移到 1092 / 710，顶部上边界上移到 120 / 100',
    '主色 #5B4FE8、深色主题、4 构件品牌图形、1080x1350 与 1440x810 两尺寸、全部必含文案与字体层级均未改动；未使用任何 transform 或窄框压窄文字'
  )
  rechecked = '再看两图：长标题 2 行不与任何新增信息重叠，四条必含文案原样保留，品牌图形形态不变；GDI+ 复核 18/18 probe 命中、4 条保留带为空、0 problems；round-01 的 8 个产物仍在且 launch-portrait.png 的 SHA-256 与关闭时记录的 A41B1C2954A9C88D… 一致，旧轮未被覆盖'
  result = 'requirement-change 首版即合格：18 处正文字号最小 26 >=24、长标题 56/52 >=48 且 2 行 <=3 行，11 条必含文案两图全在，0 个 <Image>，0 problems；按「一次合格时无需制造修改」，round-02 内不制造第二次渲染'
  stats = [pscustomobject]@{ renders = 2; images = 2; probes = 18; reserved_bands_verified = 4; problems = 0 }
}
[IO.File]::AppendAllText("$tmp\iterations.jsonl", (([pscustomobject]$it | ConvertTo-Json -Depth 8 -Compress) + "`n"), $utf8)

"round-02 promoted:"
foreach ($r in $rows) { "  {0,-22} {1}x{2}  {3,7} bytes  sha256={4}" -f $r.name, $r.w, $r.h, $r.bytes, $r.sha256.Substring(0, 32) }
"  round-01 intact     launch-portrait.png sha256 still $($h01.Substring(0,32))"
"  probes              portrait 9/9, wide 9/9 background match, reserved bands empty (4/4)"
"  iterations.jsonl    + A21r2-it01 (requirement-change)"
"  requests.jsonl      $((@(Get-Content "$tmp\requests.jsonl" -Encoding UTF8)).Count) rows total"
