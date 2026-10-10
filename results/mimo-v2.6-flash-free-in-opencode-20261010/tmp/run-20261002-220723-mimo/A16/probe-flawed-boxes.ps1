# A16 - measure the flawed report's panel boxes and headline text ink boxes so
# every finding can cite an exact image location. Observation only.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$SRC = Join-Path $ROOT 'tasks\A16-visual-data-forensics\inputs\flawed-report.png'
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
$ENC = New-Object Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap($SRC)

function HexOf($c) { return ('#{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B) }

function RunOnRow($b, [int]$y, [string]$hex, [int]$x0, [int]$x1) {
  $c = [System.Drawing.ColorTranslator]::FromHtml($hex)
  $s = -1; $e = -1
  for ($x = $x0; $x -le $x1; $x++) {
    $p = $b.GetPixel($x, $y)
    if ($p.R -eq $c.R -and $p.G -eq $c.G -and $p.B -eq $c.B) { if ($s -lt 0) { $s = $x }; $e = $x }
  }
  if ($s -lt 0) { return $null }
  return [pscustomobject]@{ x0 = $s; x1 = $e; w = ($e - $s + 1) }
}
function RunOnCol($b, [int]$x, [string]$hex, [int]$y0, [int]$y1) {
  $c = [System.Drawing.ColorTranslator]::FromHtml($hex)
  $s = -1; $e = -1
  for ($y = $y0; $y -le $y1; $y++) {
    $p = $b.GetPixel($x, $y)
    if ($p.R -eq $c.R -and $p.G -eq $c.G -and $p.B -eq $c.B) { if ($s -lt 0) { $s = $y }; $e = $y }
  }
  if ($s -lt 0) { return $null }
  return [pscustomobject]@{ y0 = $s; y1 = $e; h = ($e - $s + 1) }
}
function InkBox($b, [int]$x0, [int]$y0, [int]$x1, [int]$y1) {
  $bx = 99999; $by = 99999; $bx1 = -1; $by1 = -1
  for ($y = $y0; $y -le $y1; $y++) {
    for ($x = $x0; $x -le $x1; $x++) {
      $p = $b.GetPixel($x, $y)
      $lum = (0.299 * $p.R) + (0.587 * $p.G) + (0.114 * $p.B)
      if ($lum -lt 170) {
        if ($x -lt $bx) { $bx = $x }; if ($x -gt $bx1) { $bx1 = $x }
        if ($y -lt $by) { $by = $y }; if ($y -gt $by1) { $by1 = $y }
      }
    }
  }
  if ($bx1 -lt 0) { return $null }
  return [pscustomobject]@{ x = $bx; y = $by; w = ($bx1 - $bx + 1); h = ($by1 - $by + 1) }
}

$WHITE = '#FFFFFF'
$res = [ordered]@{}

# panel boxes: white fills on the warm page background
$chartX = RunOnRow $bmp 400 $WHITE 0 1279
$chartY = RunOnCol $bmp 140 $WHITE 150 640
$res.chart_card = [ordered]@{ x = $chartX.x0; y = $chartY.y0; w = $chartX.w; h = $chartY.h }
Write-Output ("chart card  x={0} y={1} w={2} h={3}" -f $chartX.x0, $chartY.y0, $chartX.w, $chartY.h)

$profX = RunOnRow $bmp 760 $WHITE 0 830
$profY = RunOnCol $bmp 400 $WHITE 630 850
$res.profit_card = [ordered]@{ x = $profX.x0; y = $profY.y0; w = $profX.w; h = $profY.h }
Write-Output ("profit card x={0} y={1} w={2} h={3}" -f $profX.x0, $profY.y0, $profX.w, $profY.h)

# callout card: warm cream - discover its exact colour by sampling the middle
$callHex = HexOf $bmp.GetPixel(1000, 730)
Write-Output ("callout fill = {0}" -f $callHex)
$callX = RunOnRow $bmp 730 $callHex 820 1279
$callY = RunOnCol $bmp 1000 $callHex 630 850
$res.callout_card = [ordered]@{ x = $callX.x0; y = $callY.y0; w = $callX.w; h = $callY.h; fill = $callHex }
Write-Output ("callout     x={0} y={1} w={2} h={3} fill={4}" -f $callX.x0, $callY.y0, $callX.w, $callY.h, $callHex)

# legend swatches
$blueSw = $null; $orangeSw = $null
for ($x = 860; $x -le 1220; $x++) {
  $p = $bmp.GetPixel($x, 193)
  if ($p.B -gt 200 -and $p.R -lt 110 -and $p.G -ge 70 -and $p.G -le 150) { if ($null -eq $blueSw) { $blueSw = [ordered]@{ x0 = $x; x1 = $x } } else { $blueSw.x1 = $x } }
  if ($p.R -gt 210 -and $p.G -ge 100 -and $p.G -le 175 -and $p.B -lt 110) { if ($null -eq $orangeSw) { $orangeSw = [ordered]@{ x0 = $x; x1 = $x } } else { $orangeSw.x1 = $x } }
}
Write-Output ("legend blue swatch   x {0}..{1}" -f $blueSw.x0, $blueSw.x1)
Write-Output ("legend orange swatch x {0}..{1}" -f $orangeSw.x0, $orangeSw.x1)
$res.legend = [ordered]@{ blue_swatch = $blueSw; orange_swatch = $orangeSw; y = 193 }

# headline text ink boxes
$res.text = [ordered]@{}
$res.text.title    = (InkBox $bmp 40 30 900 95)
$res.text.subtitle = (InkBox $bmp 40 100 900 145)
$res.text.chart_title = (InkBox $bmp 70 175 700 225)
$res.text.unit     = (InkBox $bmp 70 226 700 260)
$res.text.profit_title = (InkBox $bmp 70 660 700 705)
$res.text.callout_title = (InkBox $bmp 850 665 1210 710)
$res.text.footer   = (InkBox $bmp 40 850 700 895)
foreach ($k in @('title','subtitle','chart_title','unit','profit_title','callout_title','footer')) {
  $t = $res.text.$k
  if ($null -ne $t) { Write-Output ("text {0,-14} x={1} y={2} w={3} h={4}" -f $k, $t.x, $t.y, $t.w, $t.h) }
}

# the four big profit numbers + their quarter captions
$res.profit_numbers = @()
foreach ($i in 0..3) {
  $x0 = 84 + ($i * 178)
  $num = InkBox $bmp $x0 750 ($x0 + 170) 800
  $cap = InkBox $bmp $x0 715 ($x0 + 170) 748
  $res.profit_numbers += [ordered]@{ index = $i; caption_box = $cap; number_box = $num }
  if ($null -ne $num) { Write-Output ("profit[{0}] caption {1},{2} {3}x{4}   number {5},{6} {7}x{8}" -f $i, $cap.x, $cap.y, $cap.w, $cap.h, $num.x, $num.y, $num.w, $num.h) }
}

# bar value labels (dark text just above each bar) - restricted to the bar's own
# x span so the neighbouring bar in the pair cannot bleed into the ink box
$res.bar_labels = @()
$barSpans = @(
  @{ kind = 'blue';   q = 'Q1'; x0 = 224;  x1 = 287;  top = 415; value = 120 },
  @{ kind = 'orange'; q = 'Q1'; x0 = 300;  x1 = 363;  top = 455; value = 90 },
  @{ kind = 'blue';   q = 'Q2'; x0 = 460;  x1 = 523;  top = 393; value = 135 },
  @{ kind = 'orange'; q = 'Q2'; x0 = 536;  x1 = 599;  top = 430; value = 108 },
  @{ kind = 'blue';   q = 'Q3'; x0 = 696;  x1 = 759;  top = 367; value = 128 },
  @{ kind = 'orange'; q = 'Q3'; x0 = 772;  x1 = 835;  top = 437; value = 96 },
  @{ kind = 'blue';   q = 'Q4'; x0 = 932;  x1 = 995;  top = 319; value = 180 },
  @{ kind = 'orange'; q = 'Q4'; x0 = 1008; x1 = 1071; top = 400; value = 126 }
)
foreach ($s in $barSpans) {
  $box = InkBox $bmp ($s.x0 - 10) ($s.top - 42) ($s.x1 + 10) ($s.top - 5)
  $res.bar_labels += [ordered]@{ kind = $s.kind; quarter = $s.q; bar_x0 = $s.x0; bar_x1 = $s.x1; bar_top = $s.top; csv_value = $s.value; label_box = $box }
  if ($null -ne $box) { Write-Output ("barLabel {0} {1} top={2} csv={3} -> label box x={4} y={5} w={6} h={7}" -f $s.kind, $s.q, $s.top, $s.value, $box.x, $box.y, $box.w, $box.h) }
}

[IO.File]::WriteAllText((Join-Path $TMP 'probe-flawed-boxes.json'), ($res | ConvertTo-Json -Depth 8), $ENC)
$bmp.Dispose()
Write-Output ("wrote {0}" -f (Join-Path $TMP 'probe-flawed-boxes.json'))
