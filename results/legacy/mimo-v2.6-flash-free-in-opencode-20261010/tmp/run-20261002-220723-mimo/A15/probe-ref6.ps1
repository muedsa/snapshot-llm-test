# Sixth pass: fixes probe5 section 8 (a $L / $l case-insensitive clobber) and
# re-measures nav dots, the selected pill and the activity lines.
$ErrorActionPreference = 'Stop'
Set-Location $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Add-Type -AssemblyName System.Drawing
$REF = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tasks\A15-reference-reconstruction\inputs\reference.png')
$bmp = New-Object System.Drawing.Bitmap($REF)
function Hex($c) { '{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B }
function LumOf($c) { return (0.299 * $c.R) + (0.587 * $c.G) + (0.114 * $c.B) }
function NearHex($c, $hex, $tol) {
  $r = [Convert]::ToInt32($hex.Substring(0,2),16); $g = [Convert]::ToInt32($hex.Substring(2,2),16); $b = [Convert]::ToInt32($hex.Substring(4,2),16)
  return ([math]::Abs($c.R-$r) -le $tol -and [math]::Abs($c.G-$g) -le $tol -and [math]::Abs($c.B-$b) -le $tol)
}

Write-Output '=== A. activity item lines (proper names, x 1072..1380) ==='
$bands = @(
  @{ nm='item1 title'; y0=392; y1=414 },
  @{ nm='item1 time';  y0=420; y1=436 },
  @{ nm='item2 title'; y0=453; y1=473 },
  @{ nm='item2 time';  y0=480; y1=496 },
  @{ nm='item3 title'; y0=513; y1=533 },
  @{ nm='item3 time';  y0=540; y1=556 }
)
foreach ($bd in $bands) {
  $minX = 9999; $maxX = -1; $minY = 9999; $maxY = -1
  for ($y = $bd.y0; $y -lt $bd.y1; $y++) {
    for ($x = 1072; $x -lt 1380; $x++) {
      $c = $bmp.GetPixel($x, $y)
      if ((LumOf $c) -lt 170) { if ($x -lt $minX) { $minX = $x }; if ($x -gt $maxX) { $maxX = $x }; if ($y -lt $minY) { $minY = $y }; if ($y -gt $maxY) { $maxY = $y } }
    }
  }
  if ($maxX -lt 0) { Write-Output ("   {0,-13} (no ink)" -f $bd.nm) }
  else { Write-Output ("   {0,-13} x {1}..{2} (w {3})  y {4}..{5} (h {6})" -f $bd.nm, $minX, $maxX, ($maxX-$minX+1), $minY, $maxY, ($maxY-$minY+1)) }
}

Write-Output '=== B. activity dots (tight bbox, any saturated pixel x 1048..1072) ==='
foreach ($cy in @(401, 461, 521)) {
  $minX=9999;$maxX=-1;$minY=9999;$maxY=-1
  for ($y=$cy-12; $y -lt $cy+12; $y++) { for ($x=1048; $x -lt 1072; $x++) {
    $c=$bmp.GetPixel($x,$y)
    $mx=[math]::Max($c.R,[math]::Max($c.G,$c.B)); $mn=[math]::Min($c.R,[math]::Min($c.G,$c.B))
    if (($mx-$mn) -gt 45) { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
  Write-Output ("   dot cy~{0}: x {1}..{2} (w {3}) y {4}..{5} (h {6}) centre #{7}" -f $cy,$minX,$maxX,($maxX-$minX+1),$minY,$maxY,($maxY-$minY+1),(Hex $bmp.GetPixel([int](($minX+$maxX)/2),[int](($minY+$maxY)/2))))
}

Write-Output '=== C. nav dots (tight colour match) ==='
$specs = @(
  @{ nm='nav0'; cy=133; hex='64DBB6' },
  @{ nm='nav1'; cy=197; hex='7791B3' },
  @{ nm='nav2'; cy=261; hex='7791B3' },
  @{ nm='nav3'; cy=325; hex='7791B3' }
)
foreach ($sp in $specs) {
  $minX=9999;$maxX=-1;$minY=9999;$maxY=-1
  for ($y=$sp.cy-14; $y -lt $sp.cy+14; $y++) { for ($x=26; $x -lt 58; $x++) {
    if (NearHex $bmp.GetPixel($x,$y) $sp.hex 30) { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
  Write-Output ("   {0}: x {1}..{2} (w {3}) y {4}..{5} (h {6})" -f $sp.nm,$minX,$maxX,($maxX-$minX+1),$minY,$maxY,($maxY-$minY+1))
}

Write-Output '=== D. selected pill extent at x=195 (clear of text) ==='
$st=$null
for ($y=100; $y -lt 185; $y++) {
  $hit = NearHex $bmp.GetPixel(195,$y) '294467' 6
  if ($hit -and $null -eq $st) { $st=$y }
  if ((-not $hit) -and $null -ne $st) { Write-Output ("   pill y {0}..{1} (h {2})" -f $st,($y-1),($y-$st)); $st=$null }
}
if ($null -ne $st) { Write-Output ("   pill y {0}..184" -f $st) }

Write-Output '=== E. selected pill horizontal extent at y=120 (above text) ==='
$st=$null
for ($x=0; $x -lt 220; $x++) {
  $hit = NearHex $bmp.GetPixel($x,120) '294467' 6
  if ($hit -and $null -eq $st) { $st=$x }
  if ((-not $hit) -and $null -ne $st) { if (($x-$st) -gt 5) { Write-Output ("   pill x {0}..{1} (w {2})" -f $st,($x-1),($x-$st)) }; $st=$null }
}

Write-Output '=== F. nav label ink top/bottom per row (x 62..150) ==='
foreach ($cy in @(133,197,261,325)) {
  $minY=9999;$maxY=-1;$minX=9999;$maxX=-1
  for ($y=$cy-20; $y -lt $cy+22; $y++) { for ($x=62; $x -lt 155; $x++) {
    $c=$bmp.GetPixel($x,$y)
    $lum = LumOf $c
    if ($lum -gt 120) { if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y}; if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x} } } }
  Write-Output ("   nav y~{0}: ink x {1}..{2} (w {3}) y {4}..{5} (h {6})" -f $cy,$minX,$maxX,($maxX-$minX+1),$minY,$maxY,($maxY-$minY+1))
}

Write-Output '=== G. sidebar brand + card line ink boxes ==='
foreach ($spec in @(@{nm='brand';x0=66;y0=32;x1=210;y1=58}, @{nm='cardL1';x0=34;y0=764;x1=195;y1=786}, @{nm='cardL2';x0=34;y0=798;x1=195;y1=822}, @{nm='cardL3';x0=34;y0=830;x1=195;y1=854})) {
  $minX=9999;$maxX=-1;$minY=9999;$maxY=-1
  for ($y=$spec.y0; $y -lt $spec.y1; $y++) { for ($x=$spec.x0; $x -lt $spec.x1; $x++) {
    $c=$bmp.GetPixel($x,$y); if ((LumOf $c) -gt 110) { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
  Write-Output ("   {0,-7} x {1}..{2} (w {3}) y {4}..{5} (h {6})" -f $spec.nm,$minX,$maxX,($maxX-$minX+1),$minY,$maxY,($maxY-$minY+1))
}

$bmp.Dispose()
