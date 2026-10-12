# A16 - final delivered PNG: confirm no text overflows its card.
# Measures the SERVED pixels (not the DSL): locates the two lower cards by
# scanning rows that carry no glyphs, splits each card interior into text lines
# by finding ink rows, and reports every line's ink bbox plus the padding that
# is left inside the card edge.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$PNG = Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A16\corrected-report.png'
Add-Type -AssemblyName System.Drawing
$bmp = [Drawing.Bitmap]::FromFile($PNG)
$W = $bmp.Width; $H = $bmp.Height
$fail = $false

function C($x, $y) {
  $p = $bmp.GetPixel($x, $y)
  return ('#{0:X2}{1:X2}{2:X2}' -f $p.R, $p.G, $p.B)
}

function DiffHex($p, $hex) {
  $r = [Convert]::ToInt32($hex.Substring(1, 2), 16)
  $g = [Convert]::ToInt32($hex.Substring(3, 2), 16)
  $b = [Convert]::ToInt32($hex.Substring(5, 2), 16)
  return [math]::Abs($p.R - $r) + [math]::Abs($p.G - $g) + [math]::Abs($p.B - $b)
}

# widest horizontal span of $colour on any of the candidate rows (glyph pixels
# inside a card are ignored because only first/last/count are used)
function CardSpan($colour) {
  $best = $null; $bestW = -1
  foreach ($y in @(586, 590, 828, 832)) {
    $first = -1; $last = -1; $n = 0
    for ($x = 0; $x -lt $W; $x++) {
      if ((C $x $y) -eq $colour) {
        if ($first -lt 0) { $first = $x }
        $last = $x; $n++
      }
    }
    if ($n -gt 100 -and ($last - $first + 1) -gt 200) {
      if (($last - $first) -gt $bestW) { $bestW = $last - $first; $best = @($first, $last) }
    }
  }
  return ,$best
}

# contiguous vertical run of $colour around y=700 on a column that carries no glyphs
function CardVExtent($x, $colour) {
  $anchor = 700
  if ((C $x $anchor) -ne $colour) {
    for ($y = 590; $y -le 830; $y++) { if ((C $x $y) -eq $colour) { $anchor = $y; break } }
  }
  $y0 = $anchor; $y1 = $anchor
  while ($y0 -gt 560 -and ((C $x ($y0 - 1)) -eq $colour)) { $y0-- }
  while ($y1 -lt ($H - 1) -and ((C $x ($y1 + 1)) -eq $colour)) { $y1++ }
  return , @($y0, $y1)
}

function InkBox($x0, $x1, $y0, $y1, $colour, $thresh) {
  $minX = 99999; $maxX = -1; $minY = 99999; $maxY = -1
  for ($y = $y0; $y -le $y1; $y++) {
    for ($x = $x0; $x -le $x1; $x++) {
      $p = $bmp.GetPixel($x, $y)
      if ((DiffHex $p $colour) -gt $thresh) {
        if ($x -lt $minX) { $minX = $x }
        if ($x -gt $maxX) { $maxX = $x }
        if ($y -lt $minY) { $minY = $y }
        if ($y -gt $maxY) { $maxY = $y }
      }
    }
  }
  if ($maxX -lt 0) { return $null }
  return , @($minX, $minY, $maxX, $maxY)
}

function RowHasInk($x0, $x1, $y, $colour, $thresh) {
  for ($x = $x0; $x -le $x1; $x++) {
    $p = $bmp.GetPixel($x, $y)
    if ((DiffHex $p $colour) -gt $thresh) { return $true }
  }
  return $false
}

Write-Output ('image {0}x{1}   {2}' -f $W, $H, (Split-Path $PNG -Leaf))

foreach ($colour in @('#FFFFFF', '#FFF6E6')) {
  $sp = CardSpan $colour
  if ($null -eq $sp) { Write-Output ('CARD {0} NOT FOUND' -f $colour); continue }
  $x0 = $sp[0]; $x1 = $sp[1]
  $colProbe = $x0 + 10   # column inside the card's left padding, clear of all glyphs
  $ve = CardVExtent $colProbe $colour
  $cy0 = $ve[0]; $cy1 = $ve[1]
  Write-Output ''
  Write-Output ('CARD {0}  x {1}..{2}   y {3}..{4}   ({5}x{6})' -f $colour, $x0, $x1, $cy0, $cy1, ($x1 - $x0 + 1), ($cy1 - $cy0 + 1))
  if ($cy0 -lt 570 -or $cy1 -gt 845) {
    Write-Output '  <<< card vertical extent looks wrong (anchor column hit text)'
    $fail = $true
  }

  $innerX0 = $x0 + 1; $innerX1 = $x1 - 1
  $bands = @(); $cur = $null; $gap = 0
  for ($y = ($cy0 + 3); $y -le ($cy1 - 3); $y++) {
    $has = RowHasInk $innerX0 $innerX1 $y $colour 60
    if ($has) {
      if ($null -eq $cur) { $cur = @{ a = $y; b = $y } } else { $cur.b = $y }
      $gap = 0
    } else {
      if ($null -ne $cur) {
        $gap++
        if ($gap -ge 4) { $bands += , @($cur.a, $cur.b); $cur = $null; $gap = 0 }
      }
    }
  }
  if ($null -ne $cur) { $bands += , @($cur.a, $cur.b) }

  $idx = 0
  foreach ($bd in $bands) {
    if (($bd[1] - $bd[0] + 1) -le 2) { continue }   # 1-2px card-corner antialiasing row, not text
    $ink = InkBox $innerX0 $innerX1 $bd[0] $bd[1] $colour 60
    if (-not $ink) { continue }
    $idx++
    $padL = $ink[0] - $x0
    $padR = $x1 - $ink[2]
    $padB = $cy1 - $ink[3]
    $flag = ''
    if ($padR -lt 0) { $flag = '   <<< OVERFLOW RIGHT'; $fail = $true }
    elseif ($padR -lt 10) { $flag = '   <<< TIGHT right (<10px)'; $fail = $true }
    if ($padL -lt 0) { $flag = $flag + '   <<< OVERFLOW LEFT'; $fail = $true }
    elseif ($padL -lt 10) { $flag = $flag + '   <<< TIGHT left (<10px)'; $fail = $true }
    if ($padB -lt -1) { $flag = $flag + '   <<< OVERFLOW BOTTOM'; $fail = $true }
    Write-Output ('  line {0,-2} y {1}..{2}  ink x {3}..{4} w={5} h={6}  padL={7} padR={8} padB={9}{10}' -f
      $idx, $ink[1], $ink[3], $ink[0], $ink[2], ($ink[2] - $ink[0] + 1), ($ink[3] - $ink[1] + 1), $padL, $padR, $padB, $flag)
  }
}

Write-Output ''
$hdr = InkBox 0 ($W - 1) 30 140 '#F4F6FB' 60
Write-Output ('header ink  x {0}..{1}  y {2}..{3}   margins L={4} R={5}' -f $hdr[0], $hdr[2], $hdr[1], $hdr[3], $hdr[0], ($W - 1 - $hdr[2]))
if ($hdr[0] -lt 20 -or ($W - 1 - $hdr[2]) -lt 20) { Write-Output '  <<< header outside the page margin'; $fail = $true }

$ftr = InkBox 0 ($W - 1) ($H - 45) ($H - 1) '#F4F6FB' 60
Write-Output ('footer ink  x {0}..{1}  y {2}..{3}   margins L={4} R={5} bottom={6}' -f $ftr[0], $ftr[2], $ftr[1], $ftr[3], $ftr[0], ($W - 1 - $ftr[2]), ($H - 1 - $ftr[3]))
if ($ftr[0] -lt 20 -or ($W - 1 - $ftr[2]) -lt 20 -or ($H - 1 - $ftr[3]) -lt 10) {
  Write-Output '  <<< footer outside the page margin'; $fail = $true
}

Write-Output ''
Write-Output ('OVERALL (no overflow / no tight text box): ' + (-not $fail))
$bmp.Dispose()
