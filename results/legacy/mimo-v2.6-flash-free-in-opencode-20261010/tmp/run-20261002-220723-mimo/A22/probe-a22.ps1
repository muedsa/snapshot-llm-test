# probe-a22.ps1 - GDI+ sampler for A22 dashboard blocks.
# Samples each block's declared probe point from the REAL rendered PNG, checks the pixel
# against the block's declared background layer, and computes the WCAG 2.1 contrast ratio
# of the text colour against the SAMPLED pixel (never against a declared colour).
# Usage: -Round 1|2|3 -MapPath <layout-map.json> -PngPath <dashboard.png> -OutPath <probe-report.json>
param(
  [Parameter(Mandatory = $true)][ValidateSet(1, 2, 3)][int]$Round,
  [Parameter(Mandatory = $true)][string]$MapPath,
  [Parameter(Mandatory = $true)][string]$PngPath,
  [Parameter(Mandatory = $true)][string]$OutPath
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

Add-Type -AssemblyName System.Drawing

function HexToRgb([string]$h) {
  $h = $h.TrimStart('#')
  return @([Convert]::ToInt32($h.Substring(0, 2), 16),
           [Convert]::ToInt32($h.Substring(2, 2), 16),
           [Convert]::ToInt32($h.Substring(4, 2), 16))
}
function RgbToHex($rgb) { return ('{0:X2}{1:X2}{2:X2}' -f [int]$rgb[0], [int]$rgb[1], [int]$rgb[2]) }
function Lum($rgb) {
  $c = @()
  foreach ($v in $rgb) {
    $s = $v / 255.0
    if ($s -le 0.03928) { $c += ($s / 12.92) } else { $c += [Math]::Pow(($s + 0.055) / 1.055, 2.4) }
  }
  return (0.2126 * $c[0]) + (0.7152 * $c[1]) + (0.0722 * $c[2])
}
function Ratio([string]$fg, [string]$bg) {
  $l1 = Lum (HexToRgb $fg); $l2 = Lum (HexToRgb $bg)
  $hi = [Math]::Max($l1, $l2); $lo = [Math]::Min($l1, $l2)
  return [Math]::Round(($hi + 0.05) / ($lo + 0.05), 2)
}

$utf8 = New-Object System.Text.UTF8Encoding($false)
$map = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Resolve-Path $MapPath).Path, $utf8))
$pngAbs = (Resolve-Path $PngPath).Path

$bmp = [System.Drawing.Bitmap]::FromFile($pngAbs)
$entries = New-Object System.Collections.Generic.List[object]
$matched = 0; $total = 0
$maxDelta = 0
$minContrast = 999.0
$problems = New-Object System.Collections.Generic.List[string]

foreach ($b in $map.blocks) {
  $total++
  $px = [int][Math]::Floor([double]$b.probe.x)
  $py = [int][Math]::Floor([double]$b.probe.y)
  if ($px -lt 0 -or $py -lt 0 -or $px -ge $bmp.Width -or $py -ge $bmp.Height) {
    $problems.Add(("block {0}: probe ({1},{2}) is outside the {3}x{4} image" -f $b.key, $px, $py, $bmp.Width, $bmp.Height))
    continue
  }
  if ($px -lt [int]$b.probe_min_x) {
    $problems.Add(("block {0}: probe x {1} is left of probe_min_x {2} - it would not sample this block's own layer" -f $b.key, $px, $b.probe_min_x))
  }
  $c = $bmp.GetPixel($px, $py)
  $sampled = RgbToHex @($c.R, $c.G, $c.B)
  $expectHex = ([string]($b.background_layers_bottom_up[0])).TrimStart('#')
  # the layer spec may be RRGGBB:AA - for A22 every layer is opaque so RGB is the first 6
  if ($expectHex.Length -gt 6) { $expectHex = $expectHex.Substring(0, 6) }
  $expRgb = HexToRgb $expectHex
  $d = [Math]::Max([Math]::Max([Math]::Abs($c.R - $expRgb[0]), [Math]::Abs($c.G - $expRgb[1])), [Math]::Abs($c.B - $expRgb[2]))
  $ok = ($d -le 1)
  if ($ok) { $matched++ } else {
    $problems.Add(("block {0}: sampled #{1} at ({2},{3}) does not match declared background #{4} (max channel delta {5})" -f $b.key, $sampled, $px, $py, $expectHex, $d))
  }
  if ($d -gt $maxDelta) { $maxDelta = $d }
  $r = Ratio $b.color $sampled
  if ($r -lt $minContrast) { $minContrast = $r }

  $entries.Add([pscustomobject][ordered]@{
    key = $b.key; kind = $b.kind; text = $b.text
    fontSize = $b.fontSize; bold = $b.bold
    probe = @{ x = $b.probe.x; y = $b.probe.y }
    probe_min_x = $b.probe_min_x
    sampled_background_rgb = @{ r = $c.R; g = $c.G; b = $c.B }
    sampled_background_hex = $sampled
    declared_background_hex = $expectHex
    background_matches = $ok
    max_channel_delta = $d
    text_color = $b.color
    contrast_ratio = $r
    contrast_ok_ge_4_5 = ($r -ge 4.5)
    font_size_ok_ge_22 = ($b.fontSize -ge 22)
  })
}
$bmp.Dispose()

$result = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/a22-probe-report/v1'
  task = 'A22'; round = $Round
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz'); timezone = 'UTC+08:00'
  png = $PngPath
  image_size = @{ width = 1600; height = 1000 }
  method = 'System.Drawing.Bitmap.GetPixel on the real service-rendered PNG; background compared against the block declared background layer (tolerance: max channel delta <= 1 for 8-bit rounding); contrast computed with the WCAG 2.1 relative-luminance formula from the sampled pixel, never from a declared colour.'
  summary = [pscustomobject][ordered]@{
    blocks = $total; background_matched = $matched
    background_match_rate = ('{0}/{1}' -f $matched, $total)
    max_channel_delta = $maxDelta
    min_contrast_ratio = $minContrast
    all_contrast_ge_4_5 = ($minContrast -ge 4.5)
    all_font_sizes_ge_22 = -not (@($entries | Where-Object { -not $_.font_size_ok_ge_22 }).Count -gt 0)
    problems = $problems.Count
    pass = ($problems.Count -eq 0)
  }
  entries = $entries
  problems = $problems
}
New-Item -ItemType Directory -Force -Path (Split-Path $OutPath -Parent) | Out-Null
[IO.File]::WriteAllText($OutPath, (($result | ConvertTo-Json -Depth 10) + "`n"), $utf8)

"probe round $Round : $matched/$total backgrounds matched, max delta $maxDelta, min contrast $minContrast, problems $($problems.Count)"
foreach ($p in $problems) { "  !! $p" }
