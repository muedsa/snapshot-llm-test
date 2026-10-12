# probe-a21.ps1 - sample real pixels from a rendered PNG at the probe points recorded in a layout map,
# verify the reserved top/bottom bands are genuinely empty, and report the text/background contrast.
# -Mode sanity   : verify every probe equals its expected composited background (round-01 / round-02)
# -Mode contrast : same, plus enforce >= 4.5:1 and write contrast-audit.json (round-03)
param(
  [Parameter(Mandatory = $true)][string]$PngPath,
  [Parameter(Mandatory = $true)][string]$MapPath,
  [Parameter(Mandatory = $true)][string]$OutPath,
  [Parameter(Mandatory = $true)][string]$Orient,
  [ValidateSet('sanity', 'contrast')][string]$Mode = 'sanity',
  [double]$MinRatio = 4.5
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

Add-Type -AssemblyName System.Drawing
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Luminance([int]$r, [int]$g, [int]$b) {
  $f = @()
  foreach ($v in @($r, $g, $b)) {
    $c = $v / 255.0
    if ($c -le 0.04045) { $f += ($c / 12.92) } else { $f += [Math]::Pow(($c + 0.055) / 1.055, 2.4) }
  }
  return (0.2126 * $f[0] + 0.7152 * $f[1] + 0.0722 * $f[2])
}
function Ratio($r1, $g1, $b1, $r2, $g2, $b2) {
  $l1 = Luminance $r1 $g1 $b1; $l2 = Luminance $r2 $g2 $b2
  $hi = [Math]::Max($l1, $l2); $lo = [Math]::Min($l1, $l2)
  return [Math]::Round(($hi + 0.05) / ($lo + 0.05), 2)
}
function HexToRgb2([string]$h) {
  return @([Convert]::ToInt32($h.Substring(0, 2), 16), [Convert]::ToInt32($h.Substring(2, 2), 16), [Convert]::ToInt32($h.Substring(4, 2), 16))
}

$map  = Get-Content $MapPath -Raw -Encoding UTF8 | ConvertFrom-Json
$bmp  = [System.Drawing.Bitmap]::FromFile((Resolve-Path $PngPath).Path)
$w = $bmp.Width; $h = $bmp.Height

$problems = New-Object System.Collections.Generic.List[string]

# ---- 1. reserved bands must contain nothing but the page colour ----------------
$bandChecks = New-Object System.Collections.Generic.List[object]
foreach ($r in ($map.reserved_bands | Where-Object { $_.orient -eq $Orient })) {
  $x0 = [int]$r.rect.x; $y0 = [int]$r.rect.y
  $bw = [int]$r.rect.w; $bh = [int]$r.rect.h
  $pageHex = $null
  if ($bw -le 0 -or $bh -le 0) { $problems.Add("$Orient $($r.band) band has zero size"); continue }
  $pageHex = '{0:X2}{1:X2}{2:X2}' -f $bmp.GetPixel($x0 + 1, $y0 + 1).R, $bmp.GetPixel($x0 + 1, $y0 + 1).G, $bmp.GetPixel($x0 + 1, $y0 + 1).B
  $dirty = 0; $tested = 0
  for ($yy = $y0; $yy -lt ($y0 + $bh); $yy += 3) {
    for ($xx = $x0; $xx -lt ($x0 + $bw); $xx += 7) {
      $p = $bmp.GetPixel($xx, $yy); $tested++
      $hex = '{0:X2}{1:X2}{2:X2}' -f $p.R, $p.G, $p.B
      if ($hex -ne $pageHex) {
        $dirty++
        if ($dirty -le 3) { $problems.Add(("{0}: reserved {1} band is NOT empty - non-background pixel at ({2},{3}) colour #{4}" -f $Orient, $r.band, $xx, $yy, $hex)) }
      }
    }
  }
  $bandChecks.Add([pscustomobject]@{
    band = $r.band; rect = $r.rect; sampled = $tested; non_background = $dirty
    background = "#$pageHex"; empty = ($dirty -eq 0)
  })
}

# ---- 2. probe points ----------------------------------------------------------
$entries = New-Object System.Collections.Generic.List[object]
foreach ($b in ($map.blocks | Where-Object { $_.orient -eq $Orient -and $_.kind -eq 'text' })) {
  $px = [int][Math]::Floor($b.probe.x); $py = [int][Math]::Floor($b.probe.y)
  if ($px -lt 0 -or $py -lt 0 -or $px -ge $w -or $py -ge $h) { $problems.Add("$($b.key): probe off canvas"); continue }
  $p = $bmp.GetPixel($px, $py)
  $sampled = '{0:X2}{1:X2}{2:X2}' -f $p.R, $p.G, $p.B
  $expected = $b.expected_background
  $bgMatchExact = ($sampled -eq $expected)
  # The service does 8-bit source-over with its own rounding; the reference composite in
  # gen-a21.ps1 may land 1 unit off in a channel (observed: E1E1F9 vs E1E1F8, F6EAD8 vs
  # F5E9D7). A wrong or missing layer is off by >= 10 in these palettes, so accept
  # max_channel_delta <= 1 as "the declared layer stack is correct" and fail above it.
  $ex = HexToRgb2 $expected
  $dR = [Math]::Abs($p.R - $ex[0]); $dG = [Math]::Abs($p.G - $ex[1]); $dB = [Math]::Abs($p.B - $ex[2])
  $maxDelta = [Math]::Max([Math]::Max($dR, $dG), $dB)
  $bgMatch = ($maxDelta -le 1)

  $t = HexToRgb2 ($b.color.Substring(1))
  $bg = HexToRgb2 $sampled
  $ratio = Ratio $t[0] $t[1] $t[2] $bg[0] $bg[1] $bg[2]

  $ctPass = $true
  if ($Mode -eq 'contrast' -and $ratio -lt $MinRatio) { $ctPass = $false }
  if ($maxDelta -gt 1) {
    $problems.Add(("{0}: probe sampled #{1} but the declared layer stack composites to #{2} (max channel delta {3}) - the background layer was ignored or mismeasured" -f $b.key, $sampled, $expected, $maxDelta))
  }
  if (-not $ctPass) {
    $problems.Add(("{0}: contrast {1}:1 < {2}:1 (text #{3} on #{4})" -f $b.key, $ratio, $MinRatio, $b.color, $sampled))
  }
  $entries.Add([pscustomobject]@{
    key = $b.key; orient = $b.orient
    text = $b.text; fontSize = $b.fontSize; bold = $b.bold
    text_color = $b.color
    background_name = $b.background_name
    background_layers_bottom_up = $b.background_layers_bottom_up
    expected_background_composited = "#$expected"
    probe_point = [pscustomobject]@{ x = $px; y = $py }
    sampled_background_rgb = [pscustomobject]@{ r = $p.R; g = $p.G; b = $p.B }
    sampled_background_hex = "#$sampled"
    background_matches_composition = $bgMatch
    background_matches_composition_exact = $bgMatchExact
    max_channel_delta = $maxDelta
    background_delta_tolerance = 1
    background_delta_tolerance_reason = '服务端 8-bit source-over 的取整方式与参考合成实现可能相差 1 个通道值；对比度一律按实测像素 sampled_background_hex 计算，合成值只用于校验叠层是否正确'
    contrast_ratio = $ratio
    required_min = $MinRatio
    passes = ($bgMatch -and $ctPass)
  })
}

$bmp.Dispose()

# ---- 3. write ------------------------------------------------------------------
$result = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/a21-probe/v1'
  task = 'A21'; orient = $Orient; mode = $Mode
  image = $PngPath
  width = $w; height = $h
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  method = 'GDI+ System.Drawing.Bitmap.GetPixel 在 layout-map 记录的 probe 点取真实渲染像素；对比度按 WCAG 2.1 相对亮度公式 (sRGB 分量先做 gamma 解码) 计算，分母用实测背景色而非声明色'
  minimum_ratio = $MinRatio
  entries = $entries.ToArray()
  reserved_band_checks = $bandChecks.ToArray()
  problems = $problems.ToArray()
}
[IO.File]::WriteAllText($OutPath, (($result | ConvertTo-Json -Depth 8) + "`n"), $utf8)

"probe [$Orient] $Mode  ->  $OutPath"
"  image            = ${w}x${h}"
"  probes           = $($entries.Count)   background match = $(@($entries | Where-Object { $_.background_matches_composition }).Count)"
"  min contrast     = $(($entries | Measure-Object -Property contrast_ratio -Minimum).Minimum):1"
"  reserved bands   = $(($bandChecks | ForEach-Object { $_.band + ':' + $_.empty }) -join ', ')"
"  problems         = $($problems.Count)"
foreach ($p in $problems) { "  !! $p" }
if ($problems.Count -gt 0) { exit 1 }
