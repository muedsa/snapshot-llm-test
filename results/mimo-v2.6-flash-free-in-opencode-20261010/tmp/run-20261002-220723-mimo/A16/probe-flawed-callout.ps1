# A16 - the callout card box + its body text, plus the exact page/card fills.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$SRC = Join-Path $ROOT 'tasks\A16-visual-data-forensics\inputs\flawed-report.png'
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
$ENC = New-Object Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap($SRC)
function HexOf($c) { return ('#{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B) }

# sample a grid of points to find the callout fill (avoid text)
Write-Output '--- sample grid ---'
$counts = @{}
foreach ($pt in @(
  @{x=1200;y=660}, @{x=1200;y=800}, @{x=860;y=660}, @{x=860;y=800},
  @{x=1150;y=700}, @{x=1150;y=780}, @{x=1000;y=660}, @{x=1210;y=730}
)) {
  $h = HexOf $bmp.GetPixel($pt.x, $pt.y)
  Write-Output ("  ({0},{1}) = {2}" -f $pt.x, $pt.y, $h)
  if ($counts.ContainsKey($h)) { $counts[$h] = $counts[$h] + 1 } else { $counts[$h] = 1 }
}
$fill = ($counts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Name
Write-Output ("callout fill candidate = {0}" -f $fill)

$c = [System.Drawing.ColorTranslator]::FromHtml($fill)
# horizontal extent at y=790 (below the text)
$s = -1; $e = -1
for ($x = 800; $x -le 1279; $x++) {
  $p = $bmp.GetPixel($x, 790)
  if ($p.R -eq $c.R -and $p.G -eq $c.G -and $p.B -eq $c.B) { if ($s -lt 0) { $s = $x }; $e = $x }
}
$w = $e - $s + 1
# vertical extent at x=1200
$t = -1; $b2 = -1
for ($y = 620; $y -le 860; $y++) {
  $p = $bmp.GetPixel(1200, $y)
  if ($p.R -eq $c.R -and $p.G -eq $c.G -and $p.B -eq $c.B) { if ($t -lt 0) { $t = $y }; $b2 = $y }
}
$hgt = $b2 - $t + 1
Write-Output ("callout box x={0} y={1} w={2} h={3} (x {4}..{5}, y {6}..{7})" -f $s, $t, $w, $hgt, $s, $e, $t, $b2)

# callout body text ink box
$bx = 99999; $by = 99999; $bx1 = -1; $by1 = -1
for ($y = 705; $y -le 800; $y++) {
  for ($x = ($s + 6); $x -le ($e - 6); $x++) {
    $p = $bmp.GetPixel($x, $y)
    $lum = (0.299 * $p.R) + (0.587 * $p.G) + (0.114 * $p.B)
    if ($lum -lt 170) { if ($x -lt $bx) { $bx = $x }; if ($x -gt $bx1) { $bx1 = $x }; if ($y -lt $by) { $by = $y }; if ($y -gt $by1) { $by1 = $y } }
  }
}
Write-Output ("callout body ink x={0} y={1} w={2} h={3}" -f $bx, $by, ($bx1 - $bx + 1), ($by1 - $by + 1))

# the two legend text ink boxes (so the legend claim can be located precisely)
function InkBox($b, [int]$x0, [int]$y0, [int]$x1, [int]$y1) {
  $bx = 99999; $by = 99999; $bx1 = -1; $by1 = -1
  for ($y = $y0; $y -le $y1; $y++) {
    for ($x = $x0; $x -le $x1; $x++) {
      $p = $b.GetPixel($x, $y)
      $lum = (0.299 * $p.R) + (0.587 * $p.G) + (0.114 * $p.B)
      if ($lum -lt 170) { if ($x -lt $bx) { $bx = $x }; if ($x -gt $bx1) { $bx1 = $x }; if ($y -lt $by) { $by = $y }; if ($y -gt $by1) { $by1 = $y } }
    }
  }
  if ($bx1 -lt 0) { return $null }
  return [pscustomobject]@{ x = $bx; y = $by; w = ($bx1 - $bx + 1); h = ($by1 - $by + 1) }
}
$lg1 = InkBox $bmp 900 180 1040 210   # 成本
$lg2 = InkBox $bmp 1078 180 1220 210  # 收入
Write-Output ("legend text 1 (成本) x={0} y={1} w={2} h={3}" -f $lg1.x, $lg1.y, $lg1.w, $lg1.h)
Write-Output ("legend text 2 (收入) x={0} y={1} w={2} h={3}" -f $lg2.x, $lg2.y, $lg2.w, $lg2.h)

# category labels under the bars
$qlabels = @()
foreach ($q in @(@{q='Q1';x0=200;x1=320}, @{q='Q2';x0=436;x1=556}, @{q='Q3';x0=672;x1=792}, @{q='Q4';x0=908;x1=1028})) {
  $box = InkBox $bmp $q.x0 575 $q.x1 605
  $qlabels += [ordered]@{ quarter = $q.q; box = $box }
  Write-Output ("cat {0} box x={1} y={2} w={3} h={4}" -f $q.q, $box.x, $box.y, $box.w, $box.h)
}

$out = [ordered]@{
  callout_fill = $fill
  callout_box  = [ordered]@{ x = $s; y = $t; w = $w; h = $hgt }
  callout_body_ink = [ordered]@{ x = $bx; y = $by; w = ($bx1 - $bx + 1); h = ($by1 - $by + 1) }
  legend_text_cost = $lg1
  legend_text_revenue = $lg2
  category_labels = $qlabels
  page_fill = (HexOf $bmp.GetPixel(20, 20))
  card_fill = (HexOf $bmp.GetPixel(640, 600))
}
[IO.File]::WriteAllText((Join-Path $TMP 'probe-flawed-callout.json'), ($out | ConvertTo-Json -Depth 6), $ENC)
$bmp.Dispose()
Write-Output ("wrote {0}" -f (Join-Path $TMP 'probe-flawed-callout.json'))
