# Fifth pass: remaining details - separators, pill shape/text, bar caps, logo, nav pill.
$ErrorActionPreference = 'Stop'
Set-Location $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Add-Type -AssemblyName System.Drawing
$REF = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tasks\A15-reference-reconstruction\inputs\reference.png')
$bmp = New-Object System.Drawing.Bitmap($REF)
function Hex($c) { '{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B }
function IsWhite($c) { ($c.R -gt 248 -and $c.G -gt 248 -and $c.B -gt 248) }

Write-Output '=== 1. row separator extent (y=760) ==='
$st = $null
for ($x = 261; $x -lt 1399; $x++) {
  $hit = -not (IsWhite $bmp.GetPixel($x, 760))
  if ($hit -and $null -eq $st) { $st = $x }
  if ((-not $hit) -and $null -ne $st) { if (($x - $st) -gt 5) { Write-Output ("   x {0}..{1} (w {2}) colour {3}" -f $st, ($x-1), ($x-$st), (Hex $bmp.GetPixel($st,760))) }; $st = $null }
}
if ($null -ne $st) { Write-Output ("   x {0}..1398" -f $st) }

Write-Output '=== 2. pill1 top-left corner (first non-white x per row 729..742) ==='
$s = ''
for ($y = 729; $y -lt 743; $y++) {
  for ($x = 1020; $x -lt 1070; $x++) {
    $c = $bmp.GetPixel($x, $y)
    if (-not (IsWhite $c)) { $s += "{0}:{1} " -f $y, $x; break }
  }
}
Write-Output "  $s"

Write-Output '=== 3. pill text ink bbox (pixels differing from pill bg) ==='
$bgs = @( @{n='p1';hex='E7EFFF';x0=1028;y0=729}, @{n='p2';hex='FFF3D7';x0=1028;y0=764}, @{n='p3';hex='DCF5EC';x0=1028;y0=799} )
foreach ($p in $bgs) {
  $br = [Convert]::ToInt32($p.hex.Substring(0,2),16); $bg = [Convert]::ToInt32($p.hex.Substring(2,2),16); $bb = [Convert]::ToInt32($p.hex.Substring(4,2),16)
  $a=9999;$b=9999;$c1=-1;$d1=-1
  for ($y=$p.y0; $y -lt $p.y0+28; $y++) { for ($x=$p.x0; $x -lt $p.x0+148; $x++) {
    $c=$bmp.GetPixel($x,$y)
    if ([math]::Abs($c.R-$br) -gt 40 -or [math]::Abs($c.G-$bg) -gt 40 -or [math]::Abs($c.B-$bb) -gt 40) {
      if($x -lt $a){$a=$x}; if($x -gt $c1){$c1=$x}; if($y -lt $b){$b=$y}; if($y -gt $d1){$d1=$y} } } }
  Write-Output ("   {0} text x {1}..{2} (w {3}) y {4}..{5} (h {6})" -f $p.n,$a,$c1,($c1-$a+1),$b,$d1,($d1-$b+1))
}

Write-Output '=== 4. Apr bar top row run (y=484..490) ==='
for ($y = 484; $y -lt 491; $y++) {
  $st=$null; $seg=@()
  for ($x=350;$x -lt 420;$x++){ $c=$bmp.GetPixel($x,$y); $hit = ($c.B -gt 150 -and $c.B -gt ($c.R+60) -and $c.B -gt ($c.G+60))
    if($hit -and $null -eq $st){$st=$x}; if((-not $hit) -and $null -ne $st){$seg+=("{0}..{1}" -f $st,($x-1));$st=$null} }
  if($null -ne $st){$seg+=("{0}..419" -f $st)}
  Write-Output ("   y={0} {1}" -f $y, ($seg -join ', '))
}

Write-Output '=== 5. logo interior grid (x 29..59, y 32..62 step 3) ==='
for ($y = 32; $y -lt 62; $y += 3) {
  $line = "   y={0,-3} " -f $y
  for ($x = 29; $x -lt 60; $x += 3) { $line += (Hex $bmp.GetPixel($x,$y)) + ' ' }
  Write-Output $line
}

Write-Output '=== 6. nav selected pill column scan (x=100, y 100..180) ==='
$st=$null
for ($y=100;$y -lt 180;$y++){
  $c=$bmp.GetPixel(100,$y)
  $hit = ([math]::Abs($c.R-0x29) -le 6 -and [math]::Abs($c.G-0x44) -le 6 -and [math]::Abs($c.B-0x67) -le 6)
  if($hit -and $null -eq $st){$st=$y}
  if((-not $hit) -and $null -ne $st){ Write-Output ("   pill y {0}..{1} (h {2})" -f $st,($y-1),($y-$st)); $st=$null }
}

Write-Output '=== 7. nav dot bboxes (x 28..52) ==='
foreach ($cy in @(133,197,261,325)) {
  $a=9999;$b=9999;$c1=-1;$d1=-1
  for ($y=$cy-12;$y -lt $cy+12;$y++){ for($x=28;$x -lt 52;$x++){
    $c=$bmp.GetPixel($x,$y)
    $mx=[math]::Max($c.R,[math]::Max($c.G,$c.B)); $mn=[math]::Min($c.R,[math]::Min($c.G,$c.B))
    if(($mx-$mn) -gt 30 -or (0.299*$c.R+0.587*$c.G+0.114*$c.B) -gt 95){
      if($x -lt $a){$a=$x}; if($x -gt $c1){$c1=$x}; if($y -lt $b){$b=$y}; if($y -gt $d1){$d1=$y} } } }
  Write-Output ("   dot y~{0}: x {1}..{2} (w {3}) y {4}..{5} (h {6})" -f $cy,$a,$c1,($c1-$a+1),$b,$d1,($d1-$b+1))
}

Write-Output '=== 8. activity text x extents per line ==='
$lines = @( @{n='item1 title';y0=395;y1=412}, @{n='item1 time';y0=423;y1=433}, @{n='item2 title';y0=456;y1=471}, @{n='item3 title';y0=516;y1=531} )
foreach ($l in $lines) {
  $a=9999;$c1=-1
  for ($y=$l.y0;$y -lt $l.y1;$y++){ for($x=1070;$x -lt 1380;$x++){
    $c=$bmp.GetPixel($x,$y); $L=(0.299*$c.R)+(0.587*$c.G)+(0.114*$c.B)
    if($L -lt 170){ if($x -lt $a){$a=$x}; if($x -gt $c1){$c1=$x} } } }
  Write-Output ("   {0,-14} x {1}..{2} (w {3})" -f $l.n,$a,$c1,($c1-$a+1))
}

Write-Output '=== 9. table card / activity card top-left corner (first non-bg x, y 310..324 at x0=258) ==='
$s=''
for ($y=310;$y -lt 325;$y++){ for($x=256;$x -lt 300;$x++){ $c=$bmp.GetPixel($x,$y)
  if(-not ($c.R -eq 0xF3 -and $c.G -eq 0xF6 -and $c.B -eq 0xFB)) { $s += "{0}:{1} " -f $y,$x; break } } }
Write-Output "  chart card: $s"
$s=''
for ($y=310;$y -lt 325;$y++){ for($x=1026;$x -lt 1070;$x++){ $c=$bmp.GetPixel($x,$y)
  if(-not ($c.R -eq 0xF3 -and $c.G -eq 0xF6 -and $c.B -eq 0xFB)) { $s += "{0}:{1} " -f $y,$x; break } } }
Write-Output "  activity card: $s"

Write-Output '=== 10. header band corner (first non-white x, y 688..698 at x0=280) ==='
$s=''
for ($y=688;$y -lt 699;$y++){ for($x=278;$x -lt 320;$x++){ $c=$bmp.GetPixel($x,$y)
  if(-not (IsWhite $c)) { $s += "{0}:{1} " -f $y,$x; break } } }
Write-Output "  header band: $s"

Write-Output '=== 11. nav label ink left edge per row (x 55..90) ==='
foreach ($cy in @(133,197,261,325)) {
  $a=9999
  for ($y=$cy-11;$y -lt $cy+12;$y++){ for($x=55;$x -lt 90;$x++){
    $c=$bmp.GetPixel($x,$y); $L=(0.299*$c.R)+(0.587*$c.G)+(0.114*$c.B)
    if($L -gt 115){ if($x -lt $a){$a=$x}; break } } }
  Write-Output ("   nav y~{0} ink starts x={1}" -f $cy,$a)
}

$bmp.Dispose()
