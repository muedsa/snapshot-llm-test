$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$png  = "$root\outputs\$RUN\A10\compositing-lab.png"
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap($png)

function Hex([System.Drawing.Color]$c) { '{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B }

# ---- 1. sampling point in zones 1 and 2 ---------------------------------
$ZX = @(160, 560, 960); $ZY = @(270, 690)
'--- sample (180,100) ---'
foreach ($z in 0,1) {
  $p = $bmp.GetPixel($ZX[$z] + 180, $ZY[0] + 100)
  "z{0} (180,100) = ({1},{2},{3})" -f ($z+1), $p.R, $p.G, $p.B
}
# red-only region (80,60) and blue-only region (250,190) in both zones
foreach ($z in 0,1) {
  $cx = $ZX[$z]
  $a = $bmp.GetPixel($cx + 80, $ZY[0] + 60)
  $b = $bmp.GetPixel($cx + 250, $ZY[0] + 190)
  $w = $bmp.GetPixel($cx + 10, $ZY[0] + 10)
  "z{0} red-only=({1},{2},{3})  blue-only=({4},{5},{6})  bg=({7},{8},{9})" -f ($z+1),$a.R,$a.G,$a.B,$b.R,$b.G,$b.B,$w.R,$w.G,$w.B
}

# ---- 2. golden tint bbox in zones 5 and 6 -------------------------------
function GoldenBBox([int]$cx, [int]$cy) {
  $minx = 9999; $miny = 9999; $maxx = -1; $maxy = -1
  for ($y = $cy; $y -lt ($cy + 240); $y++) {
    for ($x = $cx; $x -lt ($cx + 320); $x++) {
      $p = $bmp.GetPixel($x, $y)
      if ($p.R -gt 180 -and $p.B -lt 160 -and ($p.R - $p.B) -gt 60) {
        if ($x -lt $minx) { $minx = $x }; if ($x -gt $maxx) { $maxx = $x }
        if ($y -lt $miny) { $miny = $y }; if ($y -gt $maxy) { $maxy = $y }
      }
    }
  }
  return ,@(($minx - $cx), ($miny - $cy), ($maxx - $cx), ($maxy - $cy))
}
'--- golden bbox (zone-local) ---'
foreach ($z in 4,5) {
  $b = GoldenBBox $ZX[$z % 3] $ZY[[int][math]::Floor($z/3)]
  "z{0} golden local bbox = x {1}..{2}  y {3}..{4}  (size {5} x {6})" -f ($z+1), $b[0], $b[2], $b[1], $b[3], ($b[2]-$b[0]+1), ($b[3]-$b[1]+1)
}

# ---- 3. stripes sharpness: horizontal scan through zone 3 and 4 ----------
function ScanRow([int]$x, [int]$y, [int]$n) {
  $r = @()
  for ($i = 0; $i -lt $n; $i++) { $p = $bmp.GetPixel($x + $i, $y); $r += $p.R }
  return ,$r
}
function Span([int[]]$v) { return (($v | Measure-Object -Minimum).Minimum) .. (($v | Measure-Object -Maximum).Maximum) }
'--- stripe sharpness (row y=100 local, mid-card) ---'
foreach ($z in 2,3) {
  $cx = $ZX[$z % 3]; $cy = $ZY[[int][math]::Floor($z/3)]
  $out = ScanRow ($cx + 4) ($cy + 100) 30       # outside card, sharp
  $inn = ScanRow ($cx + 60) ($cy + 100) 30      # inside card, blurred
  "z{0} outside R range {1}..{2} (span {3})   inside R range {4}..{5} (span {6})" -f ($z+1),
     (($out|Measure-Object -Minimum).Minimum),(($out|Measure-Object -Maximum).Maximum),(($out|Measure-Object -Maximum).Maximum-($out|Measure-Object -Minimum).Minimum),
     (($inn|Measure-Object -Minimum).Minimum),(($inn|Measure-Object -Maximum).Maximum),(($inn|Measure-Object -Maximum).Maximum-($inn|Measure-Object -Minimum).Minimum)
}

# ---- 4. text sharpness in card 3 vs card 4 ------------------------------
function LocalContrast([int]$x0, [int]$y0, [int]$w, [int]$h) {
  $mn = 255; $mx = 0
  for ($y = $y0; $y -lt ($y0+$h); $y++) { for ($x = $x0; $x -lt ($x0+$w); $x++) {
    $p = $bmp.GetPixel($x,$y); if ($p.R -lt $mn) {$mn=$p.R}; if ($p.R -gt $mx) {$mx=$p.R} } }
  return ($mx - $mn)
}
'--- text region R-contrast (card text box zone-local 64..256, 98..132) ---'
foreach ($z in 2,3) {
  $cx = $ZX[$z % 3]; $cy = $ZY[[int][math]::Floor($z/3)]
  "z{0} text contrast = {1}" -f ($z+1), (LocalContrast ($cx+64) ($cy+98) 192 34)
}

# ---- 5. sample the 5/6 interior gap colour -----------------------------
'--- zone5/6 gap points (local) ---'
foreach ($z in 4,5) {
  $cx = $ZX[$z % 3]; $cy = $ZY[[int][math]::Floor($z/3)]
  $g = $bmp.GetPixel($cx + 70 + 90, $cy + 30 + 50)   # gap between blocks
  $s = $bmp.GetPixel($cx + 70 + 40, $cy + 30 + 176)  # below bottom bar
  $o = $bmp.GetPixel($cx + 20, $cy + 20)             # outside subtree
  "z{0} gap=({1},{2},{3}) underBar=({4},{5},{6}) outside=({7},{8},{9})" -f ($z+1),$g.R,$g.G,$g.B,$s.R,$s.G,$s.B,$o.R,$o.G,$o.B
}

# ---- 7. no ink below the last footer line / no clipping at canvas edge ---
function TestNotBg([int]$x, [int]$y) {
  $c = $bmp.GetPixel($x, $y)
  if ([math]::Abs($c.R - 238) -gt 6) { return $true }
  if ([math]::Abs($c.G - 241) -gt 6) { return $true }
  if ([math]::Abs($c.B - 246) -gt 6) { return $true }
  return $false
}
$minx = 9999; $miny = 9999; $maxx = -1; $maxy = -1
for ($y = 0; $y -lt $bmp.Height; $y++) {
  for ($x = 0; $x -lt $bmp.Width; $x++) {
    if (TestNotBg $x $y) {
      if ($x -lt $minx) { $minx = $x }; if ($x -gt $maxx) { $maxx = $x }
      if ($y -lt $miny) { $miny = $y }; if ($y -gt $maxy) { $maxy = $y }
    }
  }
}
'--- non-background ink bbox (whole canvas) ---'
"inbox = x {0}..{1}  y {2}..{3}   (canvas {4} x {5})" -f $minx, $maxx, $miny, $maxy, $bmp.Width, $bmp.Height
$bottomRowClean = $true
for ($x = 0; $x -lt $bmp.Width; $x++) { if (TestNotBg $x ($bmp.Height - 1)) { $bottomRowClean = $false; break } }
"last row clean = $bottomRowClean   (true => nothing clipped at the bottom edge)"
$rightColClean = $true
for ($y = 0; $y -lt $bmp.Height; $y++) { if (TestNotBg ($bmp.Width - 1) $y) { $rightColClean = $false; break } }
"right col clean = $rightColClean"

# ---- 8. footer band: single-line check ---------------------------------
'--- footer band ink rows (canvas y 955..1099) ---'
$rows = @()
for ($y = 955; $y -lt $bmp.Height; $y++) {
  $has = $false
  for ($x = 150; $x -lt 1300; $x++) { if (TestNotBg $x $y) { $has = $true; break } }
  $rows += [pscustomobject]@{ y = $y; ink = $has }
}
$band = @($rows | Where-Object { $_.ink } | ForEach-Object { $_.y })
if ($band.Count -gt 0) { "ink rows {0}..{1} (span {2})" -f (($band | Measure-Object -Minimum).Minimum), (($band | Measure-Object -Maximum).Maximum), ((($band | Measure-Object -Maximum).Maximum - ($band | Measure-Object -Minimum).Minimum + 1)) }

'--- png ---'
"size = $($bmp.Width) x $($bmp.Height)"
$bmp.Dispose()
