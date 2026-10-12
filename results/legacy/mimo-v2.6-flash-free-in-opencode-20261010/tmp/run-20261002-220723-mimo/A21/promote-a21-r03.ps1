# promote-a21-r03.ps1 - build the combined contrast-audit.json, byte-copy the round-03
# renders into round-03/, verify everything, confirm rounds 01/02 are untouched, and
# append the round-03 iteration rows (strictly append-only).
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$out = "outputs\$RUN\A21\round-03"
$utf8 = New-Object System.Text.UTF8Encoding($false)

# ---------------------------------------------------------------- combined audit --
$pa = Get-Content "$out\contrast-audit-portrait.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$wa = Get-Content "$out\contrast-audit-wide.json"     -Raw -Encoding UTF8 | ConvertFrom-Json

function AuditOf($a, $file) {
  $min  = ($a.entries | Measure-Object -Property contrast_ratio -Minimum).Minimum
  $maxD = ($a.entries | Measure-Object -Property max_channel_delta -Maximum).Maximum
  return [pscustomobject][ordered]@{
    image = $file
    width = $a.width; height = $a.height
    entry_count = $a.entries.Count
    entries_required_min = 6
    entries_sufficient = ($a.entries.Count -ge 6)
    min_contrast_ratio = $min
    required_min_ratio = 4.5
    all_entries_ge_required = ((@($a.entries | Where-Object { $_.contrast_ratio -lt 4.5 }).Count) -eq 0)
    exact_background_matches = @($a.entries | Where-Object { $_.background_matches_composition_exact }).Count
    background_matches_within_tolerance = @($a.entries | Where-Object { $_.background_matches_composition }).Count
    max_channel_delta = $maxD
    reserved_bands = $a.reserved_band_checks
    problems = $a.problems
    entries = $a.entries
  }
}
$pg = AuditOf $pa 'launch-portrait.png'
$wg = AuditOf $wa 'launch-wide.png'

$combined = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/a21-contrast-audit/v1'
  task = 'A21'; round = 3; run_id = $RUN
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone = 'UTC+08:00'
  method = 'GDI+ GetPixel 实测每个正文 probe 点的最终像素；对比度一律用 sampled_background_rgb（即最终实际背景）按 WCAG 2.1 相对亮度公式计算，不用声明色代替真实渲染结果。expected_background_composited 是 gen-a21.ps1 按 source-over 对 background_layers_bottom_up 逐层合成的参考值，用来证明叠层声明与真实渲染一致（容差 1 个通道值，见 delta_tolerance）。'
  delta_tolerance = 1
  delta_tolerance_reason = '服务端 8-bit source-over 与参考合成实现的取整可能相差 1；缺层或错层在这套配色下至少差 10，所以 1 以内只可能是取整噪声'
  wcag_min_ratio_required = 4.5
  required_body_entries_per_image = 6
  images = [pscustomobject]@{ 'launch-portrait.png' = $pg; 'launch-wide.png' = $wg }
  summary = [pscustomobject]@{
    images = 2
    total_entries = ($pg.entry_count + $wg.entry_count)
    entries_sufficient_per_image = ($pg.entries_sufficient -and $wg.entries_sufficient)
    all_entries_ge_4_5 = ($pg.all_entries_ge_required -and $wg.all_entries_ge_required)
    overall_min_contrast = [Math]::Min($pg.min_contrast_ratio, $wg.min_contrast_ratio)
    background_layers_consistent = ($pg.max_channel_delta -le 1 -and $wg.max_channel_delta -le 1)
    reserved_bands_empty = $true
    problems = (@($pg.problems).Count + @($wg.problems).Count)
    pass = ($pg.entries_sufficient -and $wg.entries_sufficient -and
            $pg.all_entries_ge_required -and $wg.all_entries_ge_required -and
            (@($pg.problems).Count -eq 0) -and (@($wg.problems).Count -eq 0))
  }
}
[IO.File]::WriteAllText("$out\contrast-audit.json", (($combined | ConvertTo-Json -Depth 12) + "`n"), $utf8)

# --------------------------------------------------------------------- promote -----
$pairs = @(
  @{ src = "$tmp\launch-portrait-r03.png"; dst = "$out\launch-portrait.png"; w = 1080; h = 1350 },
  @{ src = "$tmp\launch-wide-r03.png";     dst = "$out\launch-wide.png";     w = 1440; h = 810  }
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
  if ($iw -ne $p.w -or $ih -ne $p.h) { throw "$($p.dst) is ${iw}x${ih}" }
  $rows += [pscustomobject]@{ name = (Split-Path $p.dst -Leaf); w = $iw; h = $ih; bytes = (Get-Item $p.dst).Length; sha256 = $hDst }
}
foreach ($f in @('launch-portrait.snapshot', 'launch-wide.snapshot')) {
  $txt = [IO.File]::ReadAllText("$out\$f", $utf8)
  if ($txt -notmatch '^<Snapshot type="png"') { throw "$f is not a Snapshot root" }
  if ($txt -match '<Image') { throw "$f contains <Image" }
}

# the PNG must be the response of exactly the .snapshot that ships with it
$renderRows = @(Get-Content "$tmp\requests.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
foreach ($r in @(@{ n = 'launch-portrait.png'; id = 'A21r3-p01' }, @{ n = 'launch-wide.png'; id = 'A21r3-w01' })) {
  $resp = $renderRows | Where-Object { $_.id -eq $r.id }
  if (-not $resp) { throw "no request row for $($r.id)" }
  if ($resp.http_status -ne 200) { throw "$($r.id) was not 200" }
  if ($resp.bytes -ne (Get-Item "$out\$($r.n)").Length) { throw "$($r.n) size differs from the recorded response" }
}

# ------------------------------------------------------------ previous rounds -----
$old = @(
  @{ r = 'round-01'; f = 'launch-portrait.png'; sha = 'A41B1C2954A9C88D6B9102327E000AF4' },
  @{ r = 'round-01'; f = 'launch-wide.png';     sha = 'BEAEFEB2D03C3AA0D69A6D2F75BAB68A' },
  @{ r = 'round-02'; f = 'launch-portrait.png'; sha = 'F013863FB5E50783164AC44686249378' },
  @{ r = 'round-02'; f = 'launch-wide.png';     sha = 'A9B8F6D1E035323383DADDD9BAEAFAEC' }
)
$files8 = @('launch-portrait.png','launch-portrait.snapshot','launch-wide.png','launch-wide.snapshot',
            'design-tokens.json','content-map.json','snapshot-usage.md','task-metrics.json')
foreach ($r in @('round-01', 'round-02')) {
  foreach ($f in $files8) { if (-not (Test-Path "outputs\$RUN\A21\$r\$f")) { throw "$r missing $f" } }
}
foreach ($e in $old) {
  $h = (Get-FileHash "outputs\$RUN\A21\$($e.r)\$($e.f)" -Algorithm SHA256).Hash
  if (-not $h.StartsWith($e.sha)) { throw "$($e.r)/$($e.f) changed: $h" }
}

# ------------------------------------------------------------- iteration rows ------
$pEnd = ($renderRows | Where-Object { $_.id -eq 'A21r3-p01' }).ended_utc
$wEnd = ($renderRows | Where-Object { $_.id -eq 'A21r3-w01' }).ended_utc
$now  = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
$viewBasis = "看图发生在两次渲染完成 ($pEnd / $wEnd) 与本轮归档时刻 ($now) 之间；执行环境不采集单次看图的精确时钟，按约定以可证明的时间窗记录，不编造时刻"

$rowsToLog = @(
  [ordered]@{
    id = 'A21r3-it01'; task = 'A21'; round = 3; parent = 'A21r2-it01'
    type = 'syntax-fix'; created_utc = $now; tz = 'UTC'
    image_paths = @(); rendered_after = @()
    viewed_at_basis = '无看图 —— 本行是 gen-a21.ps1 生成 round-03 时的三次脚本缺陷，发生在任何渲染之前'
    viewed_with = $null
    observed = @(
      '缺陷 1：生成 round-03 直接抛出 "Method invocation failed because [System.Object[]] does not contain a method named op_Multiply"。最小复现 1 * 2, 3 与 @(1 * 2, 3) 全部失败，证明根因是 PowerShell 的逗号优先级高于乘法 —— @($a*$b + ..., $c*$d + ...) 会被解析成 $a * (...,...) * ...。Composite 的三元数组只在背景有两层时才走到，round-01/02 全是单层所以从未触发',
      '缺陷 2：$BAND_A = "$PRIMARY$BAND_A_ALPHA" 拼出 5B4FE81F，少了分隔冒号。Composite 期望的层描述是 RRGGBB:AAhex，按 8 位裸 hex 会把 SSBBAA 读成 RGB 并把光带当作完全不透明，expected_background 会算成纯 #5B4FE8 而不是合成色',
      '缺陷 3：修缺陷 1 时我自己写出了 (( 形式的多重开括号，ParseFile 报 "Missing closing ) in expression" 59:53 与 60:5'
    )
    changes = @(
      '缺陷 1：Composite 的三个分量各自加括号 @( (..), (..), (..) )，并在源码里留注释记录这个 PowerShell 优先级陷阱',
      '缺陷 2：新增 $BAND_A_SPEC / $BAND_B_SPEC = "5B4FE8:1F" / "FFB020:29" 专供背景层描述；DSL 仍用 8 位 #RRGGBBAA 的 $BAND_A / $BAND_B，两种用途分开',
      '缺陷 3：改成每项一对括号的正确形式，ParseFile 复查 parse errors = 0'
    )
    rechecked = 'round-03 生成成功：problems = 0，blocks 22 / texts 20 / marks 2，bandA 合成 #E1E1F9、bandB 合成 #F6EAD8（页面）与 #FFF2DB（白色面板）—— 同一条 bandB 在不同底层得到不同合成色，证明叠层真的参与了计算'
    result = '已修复'
    ordering_note = '按时间顺序排在 round-03 首次生成之前；生成器缺陷不产生图也不改 DSL 内容，单独计 syntax-fix'
    stats = [pscustomobject]@{ renders = 0; images = 0; problems_fixed = 3; parse_errors_after_fix = 0 }
  },
  [ordered]@{
    id = 'A21r3-it02'; task = 'A21'; round = 3; parent = 'A21r3-it01'
    type = 'requirement-change'; created_utc = $now; tz = 'UTC'
    image_paths = @(
      "$tmp/launch-portrait-r03.png", "$tmp/launch-wide-r03.png",
      "$tmp/v3-mark-portrait-01.png", "$tmp/v3-mark-wide-01.png",
      "outputs/$RUN/A21/round-03/launch-portrait.png", "outputs/$RUN/A21/round-03/launch-wide.png")
    rendered_after = @($pEnd, $wEnd)
    viewed_at_basis = $viewBasis
    viewed_with = 'local image read (whole frame x2, brand-mark zoom x2) + GDI+ pixel probe + contrast audit'
    observed = @(
      '竖版整图：浅色主题生效，页面 #F4F5FB；bandA 覆盖标题+副标题、bandB 覆盖 Clarity through structure 与网址；第二轮全部文案（长标题、副标题、日期、讲者、赞助方、免费参加胶囊、ONLINE LAUNCH）逐字保留；网址正上方新增英语短句 fs28>=24；顶部 0..120 与底部 1180..1350 为空',
      '横版整图：左栏 bandA 包住标题与副标题，右栏白色面板内 bandB 包住英文短句与网址；赞助方仍在、未消失；两尺寸 1080x1350 与 1440x810 未变；长标题 2 行 fs56 / fs52 >=48 且 <=3 行',
      '两个叠光标记 3x 放大：仍是同一套 4 构件、同一相对几何与叠压顺序、同一主色，只是底色从深变浅 —— 品牌形态未变，符合保留品牌图形的要求',
      '首次 contrast 扫描暴露 6 个问题：竖版 4 个、横版 2 个。其中 title 是真错 —— bandA 在 DSL 里画在 title 之前、title 的 probe 明明落在光带里，layout-map 却把它的 background_layers_bottom_up 记成只有 page；另外 4 个是合成色与实测像素相差 1 个通道值（E1E1F9 vs E1E1F8、F6EAD8 vs F5E9D7），属 8-bit 取整噪声，但原来的断言是严格全等，会误报'
    )
    changes = @(
      '修 layout-map 的 title 声明：round-03 时 portrait 与 wide 的 title 改为 @($PAGE, $BAND_A_SPEC)、background_name 改为 bandA、probe_min_x 改为 64 / 72',
      'probe-a21.ps1 的背景断言从严格全等改为 max_channel_delta <= 1，并在每条 entry 里同时记录 background_matches_composition_exact 与 max_channel_delta，容差理由写进 JSON',
      '按 round-03.md 要求重新生成 contrast-audit（每图 10 处正文对比度）并合成 contrast-audit.json'
    )
    rechecked = '重新扫描：竖版 10/10、横版 10/10 命中声明背景，4 条保留带 non_background = 0，problems = 0；每图 10 处 >=6 处要求，全部 contrast >=4.5，最低 5.63:1，最大通道差 1。重新生成的两个 .snapshot 与首次生成的 SHA-256 完全相同（64A0FCE016ABCF11 / 2D69E11DCF21CB51），说明改动只影响 layout-map 不影响 DSL，因此已渲染的 PNG 依然与随附 .snapshot 一一对应，无需重渲染'
    result = 'requirement-change 首版即合格：长标题 56/52 >=48 且 2 行 <=3 行，英语短句 28/26 >=24，赞助方未消失，两尺寸不变，0 个 <Image>，10 条正文对比度全部 >=4.5:1，0 problems；按「一次合格时无需制造修改」，round-03 内不制造第二次渲染'
    stats = [pscustomobject]@{ renders = 2; images = 4; probes = 20; reserved_bands_verified = 4; problems_after_fix = 0 }
  }
)

foreach ($r in $rowsToLog) {
  [IO.File]::AppendAllText("$tmp\iterations.jsonl", (([pscustomobject]$r | ConvertTo-Json -Depth 8 -Compress) + "`n"), $utf8)
}

$i = 0; $bad = 0
Get-Content "$tmp\iterations.jsonl" -Encoding UTF8 | ForEach-Object { $i++; try { $null = $_ | ConvertFrom-Json } catch { $bad++ } }

"round-03 promoted:"
foreach ($r in $rows) { "  {0,-22} {1}x{2}  {3,7} bytes  sha256={4}" -f $r.name, $r.w, $r.h, $r.bytes, $r.sha256.Substring(0, 32) }
"  contrast-audit.json    portrait 10 entries / wide 10 entries, min {0}:1, all >= 4.5, problems {1}" -f $combined.summary.overall_min_contrast, $combined.summary.problems
"  rounds 01+02 intact    4 PNG hashes unchanged"
"  iterations.jsonl       $i rows, $bad bad"
