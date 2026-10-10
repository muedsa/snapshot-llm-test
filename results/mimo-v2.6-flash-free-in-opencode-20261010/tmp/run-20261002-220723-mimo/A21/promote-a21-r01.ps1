# promote-a21-r01.ps1 - byte-copy the round-01 renders into the output dir, verify they are the
# untouched service responses, and append the round-01 iterations row.
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$out = "outputs\$RUN\A21\round-01"
$utf8 = New-Object System.Text.UTF8Encoding($false)

# ---- copies (never overwrite an attempt: the tmp originals stay untouched) ------
$pairs = @(
  @{ src = "$tmp\launch-portrait-r01.png"; dst = "$out\launch-portrait.png"; w = 1080; h = 1350 },
  @{ src = "$tmp\launch-wide-r01.png";     dst = "$out\launch-wide.png";     w = 1440; h = 810  }
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
# DSL files must still be present and non-empty
foreach ($f in @('launch-portrait.snapshot', 'launch-wide.snapshot')) {
  $fp = Join-Path $out $f
  if (-not (Test-Path $fp)) { throw "missing $f" }
  $txt = [IO.File]::ReadAllText($fp, $utf8)
  if ($txt -notmatch '^<Snapshot type="png"') { throw "$f is not a Snapshot root" }
}

# ---- round-01 verification summary --------------------------------------------
$probeP = Get-Content "$tmp\probe-r1-portrait.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$probeW = Get-Content "$tmp\probe-r1-wide.json"     -Raw -Encoding UTF8 | ConvertFrom-Json
if ($probeP.problems.Count -ne 0 -or $probeW.problems.Count -ne 0) { throw 'probe reported problems' }
if (@($probeP.reserved_band_checks | Where-Object { -not $_.empty }).Count) { throw 'portrait reserved band not empty' }
if (@($probeW.reserved_band_checks | Where-Object { -not $_.empty }).Count) { throw 'wide reserved band not empty' }

# ---- iterations.jsonl ----------------------------------------------------------
$renderRows = @(Get-Content "$tmp\requests.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
$pEnd = ($renderRows | Where-Object { $_.id -eq 'A21r1-p01' }).ended_utc
$wEnd = ($renderRows | Where-Object { $_.id -eq 'A21r1-w01' }).ended_utc
$now  = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')

$it = [ordered]@{
  id = 'A21r1-it01'; task = 'A21'; round = 1; parent = $null; type = 'baseline'
  created_utc = $now; tz = 'UTC'
  image_paths = @("$tmp/launch-portrait-r01.png", "$tmp/launch-wide-r01.png",
                  "$tmp/v1-mark-portrait-01.png", "$tmp/v1-mark-wide-01.png",
                  "outputs/$RUN/A21/round-01/launch-portrait.png", "outputs/$RUN/A21/round-01/launch-wide.png")
  rendered_after = @($pEnd, $wEnd)
  viewed_at_basis = "看图发生在两次渲染完成 ($pEnd / $wEnd) 与本轮归档时刻 ($now) 之间；本执行环境不采集单次看图的精确时钟，按约定以可证明的时间窗记录，不编造时刻"
  viewed_with = 'local image read (whole frame x2, brand-mark zoom x2) + GDI+ pixel probe'
  observed = @(
    '竖版 1080x1350：叠光标记 4 构件在左上，ONLINE LAUNCH 主色胶囊，主标题“让复杂信息变得清晰” fs88 单行，副标题/分隔线/日期/讲者/网址自上而下；顶部 0..140 与底部 1156..1350 两条扩展带内确实没有任何元素，也没写占位文字',
    '横版 1440x810：与竖版完全不同构图——左栏品牌与主张、右栏信息面板，两栏各自纵向排布；顶部 0..110 与底部 670..810 为空',
    '两个叠光标记放大后确认是同一套 4 构件（C1 靛蓝圆角方 / C2 淡紫圆角方 / C3 琥珀圆角方 / C4 琥珀核心圆），相对几何、颜色与叠压顺序一致，只整体缩放到 0.8；重叠处能看到亮度叠加，符合“叠光”读法',
    'GDI+ 逐点采样：两图各 7 个 probe 全部命中声明的背景色（7/7、7/7），保留带采样 non_background=0；最低对比度 5.63:1（竖）/ 5.52:1（横），本轮尚无对比度硬要求'
  )
  changes = @()
  rechecked = $null
  result = 'baseline 一次合格：14 处正文 fontSize 全部 >=24、主标题 88/72 均 >=56，5 条必含文案 + 品牌字标在两图都在，未使用 <Image>，0 problems；按“一次合格时无需制造修改”，本轮不为凑迭代而改版'
  stats = [pscustomobject]@{ renders = 2; images = 2; probes = 14; reserved_bands_verified = 4; problems = 0 }
}
$line = ([pscustomobject]$it | ConvertTo-Json -Depth 8 -Compress)
[IO.File]::AppendAllText("$tmp\iterations.jsonl", $line + "`n", $utf8)

"round-01 promoted:"
foreach ($r in $rows) { "  {0,-22} {1}x{2}  {3,7} bytes  sha256={4}" -f $r.name, $r.w, $r.h, $r.bytes, $r.sha256.Substring(0, 32) }
"  dsl files          launch-portrait.snapshot / launch-wide.snapshot"
"  probes             portrait 7/7, wide 7/7 background match, reserved bands empty (4/4)"
"  iterations.jsonl   + A21r1-it01 (baseline)"
"  requests.jsonl     $((@(Get-Content "$tmp\requests.jsonl" -Encoding UTF8)).Count) render requests"
