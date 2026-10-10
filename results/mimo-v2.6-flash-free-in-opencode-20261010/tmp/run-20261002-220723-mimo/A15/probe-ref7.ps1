# Seventh pass: per-item x positions for the chart tick labels and month labels.
$ErrorActionPreference = 'Stop'
Set-Location $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Add-Type -AssemblyName System.Drawing
$REF = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tasks\A15-reference-reconstruction\inputs\reference.png')
$bmp = New-Object System.Drawing.Bitmap($REF)
function LumOf($c) { return (0.299 * $c.R) + (0.587 * $c.G) + (0.114 * $c.B) }

function Find-Runs($y0, $y1, $x0, $x1, $thr, $gap) {
  $hits = @()
  for ($x = $x0; $x -lt $x1; $x++) {
    $any = $false
    for ($y = $y0; $y -lt $y1; $y++) { if ((LumOf $bmp.GetPixel($x,$y)) -lt $thr) { $any = $true; break } }
    $hits += [bool]$any
  }
  $runs = @(); $st = $null; $blank = 0
  for ($i = 0; $i -lt $hits.Count; $i++) {
    if ($hits[$i]) {
      if ($null -eq $st) { $st = $i }
      $blank = 0
    } else {
      if ($null -ne $st) { $blank++; if ($blank -gt $gap) { $runs += ,@($st, ($i - $blank)); $st = $null } }
    }
  }
  if ($null -ne $st) { $runs += ,@($st, ($hits.Count - 1)) }
  $out = @()
  foreach ($r in $runs) { $out += [pscustomobject]@{ x = ($x0 + $r[0]); right = ($x0 + $r[1]); w = ($r[1] - $r[0] + 1) } }
  return $out
}

Write-Output '=== y tick labels (per gridline band, x 284..332) ==='
$vals = @(120, 90, 60, 30, 0)
$ys = @(405, 441, 477, 513, 549)
for ($i = 0; $i -lt 5; $i++) {
  $runs = Find-Runs ($ys[$i]-12) ($ys[$i]+12) 284 332 175 4
  foreach ($r in $runs) {
    $minY=9999;$maxY=-1
    for ($y=$ys[$i]-14;$y -lt $ys[$i]+14;$y++){ for($x=$r.x;$x -le $r.right;$x++){ if((LumOf $bmp.GetPixel($x,$y)) -lt 175){ if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
    Write-Output ("   {0,3}: x {1}..{2} (w {3}) y {4}..{5} (h {6})" -f $vals[$i], $r.x, $r.right, $r.w, $minY, $maxY, ($maxY-$minY+1))
  }
}

Write-Output '=== month labels (y 558..578, x 336..948) ==='
$runs = Find-Runs 558 578 336 948 175 8
foreach ($r in $runs) {
  $minY=9999;$maxY=-1
  for ($y=556;$y -lt 580;$y++){ for($x=$r.x;$x -le $r.right;$x++){ if((LumOf $bmp.GetPixel($x,$y)) -lt 175){ if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
  Write-Output ("   x {0}..{1} (w {2}) centre {3} y {4}..{5} (h {6})" -f $r.x, $r.right, $r.w, [int](($r.x+$r.right)/2), $minY, $maxY, ($maxY-$minY+1))
}

Write-Output '=== table: per-row text x extents (project / owner / due) ==='
$rows = @( @{nm='r1';y0=731;y1=754}, @{nm='r2';y0=766;y1=789}, @{nm='r3';y0=801;y1=824} )
foreach ($rr in $rows) {
  $p = Find-Runs $rr.y0 $rr.y1 292 700 175 8
  $o = Find-Runs $rr.y0 $rr.y1 775 1000 175 8
  $d = Find-Runs $rr.y0 $rr.y1 1224 1360 175 8
  $ps = ($p | ForEach-Object { "{0}..{1}" -f $_.x, $_.right }) -join ' '
  $os = ($o | ForEach-Object { "{0}..{1}" -f $_.x, $_.right }) -join ' '
  $ds = ($d | ForEach-Object { "{0}..{1}" -f $_.x, $_.right }) -join ' '
  Write-Output ("   {0} project {1} | owner {2} | due {3}" -f $rr.nm, $ps, $os, $ds)
}

Write-Output '=== table header label x extents (y 696..712) ==='
$h = Find-Runs 696 712 292 1370 175 8
foreach ($r in $h) { Write-Output ("   x {0}..{1} (w {2})" -f $r.x, $r.right, $r.w) }

Write-Output '=== KPI: per-card text x extents (label row, value row, change row) ==='
foreach ($card in @( @{nm='k1';x0=278;x1=615}, @{nm='k2';x0=662;x1=999}, @{nm='k3';x0=1046;x1=1383} )) {
  $lab = Find-Runs 158 174 $card.x0 $card.x1 175 8
  $val = Find-Runs 196 230 $card.x0 $card.x1 175 8
  $chg = Find-Runs 243 263 $card.x0 $card.x1 175 8
  $fmt = { param($a) (($a | ForEach-Object { "{0}..{1}" -f $_.x, $_.right }) -join ' ') }
  Write-Output ("   {0} label [{1}] value [{2}] change [{3}]" -f $card.nm, (& $fmt $lab), (& $fmt $val), (& $fmt $chg))
}

Write-Output '=== header: title / subtitle / button label x runs ==='
$t = Find-Runs 30 75 250 700 140 12
$s2 = Find-Runs 82 106 250 700 175 12
$bt = Find-Runs 50 76 1200 1390 999 12
Write-Output ("   title runs: {0}" -f (($t | ForEach-Object { "{0}..{1}" -f $_.x,$_.right }) -join ' '))
Write-Output ("   subtitle runs: {0}" -f (($s2 | ForEach-Object { "{0}..{1}" -f $_.x,$_.right }) -join ' '))
Write-Output ("   button label runs (dark-on-blue inverted test below): {0}" -f (($bt | ForEach-Object { "{0}..{1}" -f $_.x,$_.right }) -join ' '))

$bmp.Dispose()
