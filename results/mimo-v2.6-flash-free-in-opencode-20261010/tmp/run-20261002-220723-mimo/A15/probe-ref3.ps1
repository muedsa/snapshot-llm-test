# Third measurement pass: settles the open questions from probe 1 and 2.
$ErrorActionPreference = 'Stop'
Set-Location $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Add-Type -AssemblyName System.Drawing

$REF = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tasks\A15-reference-reconstruction\inputs\reference.png')
$bmp = New-Object System.Drawing.Bitmap($REF)
function Hex($c) { '{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B }
function IsWhite($c) { ($c.R -gt 248 -and $c.G -gt 248 -and $c.B -gt 248) }

Write-Output '=== Q1: KPI card 3 right edge (row y=180, x 1370..1412) ==='
$s = ''
for ($x = 1370; $x -lt 1413; $x++) { $s += "{0}:{1} " -f $x, (Hex $bmp.GetPixel($x, 180)) }
Write-Output "  $s"

Write-Output '=== Q2a: table header row colour at chosen x (y=700) ==='
foreach ($x in @(262, 275, 300, 540, 900, 1300, 1373, 1390, 1397)) {
  Write-Output ("  x={0} y=700  #{1}" -f $x, (Hex $bmp.GetPixel($x, 700)))
}
Write-Output '=== Q2b: column x=540 through header (y 684..726) ==='
$s = ''
for ($y = 684; $y -lt 727; $y++) { $c = $bmp.GetPixel(540, $y); if (-not (IsWhite $c)) { $s += "{0}:{1} " -f $y, (Hex $c) } }
Write-Output "  $s"
Write-Output '=== Q2c: non-white runs along y=695 (header text row) ==='
$st = $null
for ($x = 261; $x -lt 1399; $x++) {
  $hit = -not (IsWhite $bmp.GetPixel($x, 695))
  if ($hit -and $null -eq $st) { $st = $x }
  if ((-not $hit) -and $null -ne $st) { if (($x - $st) -ge 2) { Write-Output ("   x {0}..{1} (w {2})" -f $st, ($x - 1), ($x - $st)) }; $st = $null }
}
Write-Output '=== Q2d: non-white runs along y=718 (band under header text) ==='
$st = $null
for ($x = 261; $x -lt 1399; $x++) {
  $hit = -not (IsWhite $bmp.GetPixel($x, 718))
  if ($hit -and $null -eq $st) { $st = $x }
  if ((-not $hit) -and $null -ne $st) { if (($x - $st) -ge 2) { Write-Output ("   x {0}..{1} (w {2})" -f $st, ($x - 1), ($x - $st)) }; $st = $null }
}
if ($null -ne $st) { Write-Output ("   x {0}..{1} (w {2})" -f $st, 1398, (1399 - $st)) }

Write-Output '=== Q3: gridline horizontal extent (y=405 and y=549) ==='
foreach ($gy in @(405, 549)) {
  $st = $null; $runs = @()
  for ($x = 261; $x -lt 1000; $x++) {
    $c = $bmp.GetPixel($x, $gy)
    $hit = ($c.B -gt 225 -and $c.B -lt 250 -and $c.R -gt 215 -and $c.R -lt 245 -and (IsWhite $c) -eq $false)
    if ($hit -and $null -eq $st) { $st = $x }
    if ((-not $hit) -and $null -ne $st) { $runs += ,@($st, ($x - 1)); $st = $null }
  }
  if ($null -ne $st) { $runs += ,@($st, 999) }
  foreach ($r in $runs) { if (($r[1] - $r[0]) -gt 20) { Write-Output ("   y={0} gridline x {1}..{2} (w {3})" -f $gy, $r[0], $r[1], ($r[1] - $r[0] + 1)) } }
}

Write-Output '=== Q4: sidebar nav rows (light pixels in x 26..60, y 110..350) ==='
$rows = @(); $cur = $null
for ($y = 105; $y -lt 355; $y++) {
  $found = $false
  for ($x = 26; $x -lt 60; $x++) {
    $c = $bmp.GetPixel($x, $y)
    $l = (0.299 * $c.R) + (0.587 * $c.G) + (0.114 * $c.B)
    if ($l -gt 95) { $found = $true; break }
  }
  if ($found -and $null -eq $cur) { $cur = @{ y0 = $y; y1 = $y } }
  elseif ($found) { $cur.y1 = $y }
  elseif (-not $found -and $null -ne $cur) { $rows += $cur; $cur = $null }
}
if ($null -ne $cur) { $rows += $cur }
foreach ($r in $rows) {
  $mid = [int](($r.y0 + $r.y1) / 2)
  $x0 = 999; $x1 = -1
  for ($x = 20; $x -lt 70; $x++) { $c = $bmp.GetPixel($x, $mid); $l = (0.299*$c.R)+(0.587*$c.G)+(0.114*$c.B); if ($l -gt 95) { if ($x -lt $x0) { $x0 = $x }; if ($x -gt $x1) { $x1 = $x } } }
  Write-Output ("   marker y {0}..{1} (h {2}) x {3}..{4} colour #{5}" -f $r.y0, $r.y1, ($r.y1-$r.y0+1), $x0, $x1, (Hex $bmp.GetPixel([int](($x0+$x1)/2), $mid)))
}
Write-Output '--- nav labels (light pixels x 62..205) ---'
$rows = @(); $cur = $null
for ($y = 110; $y -lt 355; $y++) {
  $found = $false
  for ($x = 62; $x -lt 205; $x++) {
    $c = $bmp.GetPixel($x, $y); $l = (0.299*$c.R)+(0.587*$c.G)+(0.114*$c.B)
    if ($l -gt 120) { $found = $true; break }
  }
  if ($found -and $null -eq $cur) { $cur = @{ y0 = $y; y1 = $y } }
  elseif ($found) { $cur.y1 = $y }
  elseif (-not $found -and $null -ne $cur) { $rows += $cur; $cur = $null }
}
if ($null -ne $cur) { $rows += $cur }
foreach ($r in $rows) {
  $mid = [int](($r.y0 + $r.y1) / 2)
  $x0 = 999; $x1 = -1
  for ($x = 60; $x -lt 210; $x++) { $c = $bmp.GetPixel($x, $mid); $l = (0.299*$c.R)+(0.587*$c.G)+(0.114*$c.B); if ($l -gt 120) { if ($x -lt $x0) { $x0 = $x }; if ($x -gt $x1) { $x1 = $x } } }
  Write-Output ("   label y {0}..{1} (h {2}) x {3}..{4} (w {5})" -f $r.y0, $r.y1, ($r.y1-$r.y0+1), $x0, $x1, ($x1-$x0+1))
}

Write-Output '=== Q5: activity dots full bbox + centre colour ==='
foreach ($cy in @(401, 461, 521)) {
  $x0 = 999; $x1 = -1; $y0 = 999; $y1 = -1
  for ($y = $cy - 12; $y -lt $cy + 12; $y++) {
    for ($x = 1044; $x -lt 1076; $x++) {
      $c = $bmp.GetPixel($x, $y)
      $mx = [math]::Max($c.R, [math]::Max($c.G, $c.B)); $mn = [math]::Min($c.R, [math]::Min($c.G, $c.B))
      if (($mx - $mn) -gt 45) { if ($x -lt $x0) { $x0 = $x }; if ($x -gt $x1) { $x1 = $x }; if ($y -lt $y0) { $y0 = $y }; if ($y -gt $y1) { $y1 = $y } }
    }
  }
  $cx = [int](($x0 + $x1) / 2); $ccy = [int](($y0 + $y1) / 2)
  Write-Output ("   dot x {0}..{1} (w {2}) y {3}..{4} (h {5}) centre #{6}" -f $x0, $x1, ($x1-$x0+1), $y0, $y1, ($y1-$y0+1), (Hex $bmp.GetPixel($cx, $ccy)))
}

Write-Output '=== Q6: activity text line bands (x 1078..1230, y 385..560) ==='
$rows = @(); $cur = $null
for ($y = 385; $y -lt 565; $y++) {
  $found = $false
  for ($x = 1078; $x -lt 1230; $x++) { $c = $bmp.GetPixel($x, $y); $l = (0.299*$c.R)+(0.587*$c.G)+(0.114*$c.B); if ($l -lt 170) { $found = $true; break } }
  if ($found -and $null -eq $cur) { $cur = @{ y0 = $y; y1 = $y } }
  elseif ($found) { $cur.y1 = $y }
  elseif (-not $found -and $null -ne $cur) { $rows += $cur; $cur = $null }
}
if ($null -ne $cur) { $rows += $cur }
foreach ($r in $rows) { Write-Output ("   text line y {0}..{1} (h {2})" -f $r.y0, $r.y1, ($r.y1-$r.y0+1)) }

Write-Output '=== Q7: sidebar card text line bands (x 38..178, y 762..858) ==='
$rows = @(); $cur = $null
for ($y = 762; $y -lt 858; $y++) {
  $found = $false
  for ($x = 38; $x -lt 178; $x++) { $c = $bmp.GetPixel($x, $y); $l = (0.299*$c.R)+(0.587*$c.G)+(0.114*$c.B); if ($l -gt 110) { $found = $true; break } }
  if ($found -and $null -eq $cur) { $cur = @{ y0 = $y; y1 = $y } }
  elseif ($found) { $cur.y1 = $y }
  elseif (-not $found -and $null -ne $cur) { $rows += $cur; $cur = $null }
}
if ($null -ne $cur) { $rows += $cur }
foreach ($r in $rows) {
  $mid = [int](($r.y0 + $r.y1) / 2)
  $x0 = 999; $x1 = -1
  for ($x = 34; $x -lt 190; $x++) { $c = $bmp.GetPixel($x, $mid); $l = (0.299*$c.R)+(0.587*$c.G)+(0.114*$c.B); if ($l -gt 110) { if ($x -lt $x0) { $x0 = $x }; if ($x -gt $x1) { $x1 = $x } } }
  Write-Output ("   line y {0}..{1} (h {2}) x {3}..{4} colour #{5}" -f $r.y0, $r.y1, ($r.y1-$r.y0+1), $x0, $x1, (Hex $bmp.GetPixel([int](($x0+$x1)/2), $mid)))
}

Write-Output '=== Q8: KPI cards 2 and 3 text bboxes ==='
function InkBox($x0, $y0, $x1, $y1, $thr) {
  $a=9999;$b=9999;$c1=-1;$d1=-1
  for ($y=$y0;$y -lt $y1;$y++){ for ($x=$x0;$x -lt $x1;$x++){
    $p=$bmp.GetPixel($x,$y); $l=(0.299*$p.R)+(0.587*$p.G)+(0.114*$p.B)
    if($l -lt $thr){ if($x -lt $a){$a=$x}; if($x -gt $c1){$c1=$x}; if($y -lt $b){$b=$y}; if($y -gt $d1){$d1=$y} } } }
  if($c1 -lt 0){return $null}
  [pscustomobject]@{x=$a;y=$b;w=($c1-$a+1);h=($d1-$b+1);right=$c1;bottom=$d1}
}
$sets = @(
  @{ n='K2 value 426'; x0=654;y0=182;x1=950;y1=235;thr=140 },
  @{ n='K2 change +8.1%'; x0=654;y0=238;x1=900;y1=268;thr=175 },
  @{ n='K3 value 3.2%'; x0=1038;y0=182;x1=1350;y1=235;thr=140 },
  @{ n='K3 change -0.8pp'; x0=1038;y0=238;x1=1350;y1=268;thr=175 },
  @{ n='table PROJECT hdr'; x0=275;y0=692;x1=700;y1=716;thr=175 },
  @{ n='row1 OWNER'; x0=775;y0=730;x1=1000;y1=756;thr=175 },
  @{ n='row1 STATUS pill'; x0=1010;y0=725;x1=1215;y1=760;thr=250 },
  @{ n='row1 DUE'; x0=1215;y0=730;x1=1350;y1=756;thr=175 },
  @{ n='sidebar PRO WORKSPACE'; x0=34;y0=762;x1=190;y1=792;thr=110 },
  @{ n='sidebar 12 team members'; x0=34;y0=793;x1=190;y1=824;thr=110 },
  @{ n='sidebar Manage access'; x0=34;y0=825;x1=190;y1=856;thr=110 }
)
foreach ($s2 in $sets) {
  $r = InkBox $s2.x0 $s2.y0 $s2.x1 $s2.y1 $s2.thr
  if ($null -eq $r) { Write-Output ("  {0,-24} -" -f $s2.n) }
  else { Write-Output ("  {0,-24} x={1,-5} y={2,-5} w={3,-4} h={4,-4} right={5} bottom={6}" -f $s2.n, $r.x, $r.y, $r.w, $r.h, $r.right, $r.bottom) }
}

Write-Output '=== Q9: row separator / pill vertical (x=1101, y 715..835) ==='
$st=$null
for ($y=715;$y -lt 838;$y++){
  $hit = -not (IsWhite $bmp.GetPixel(1101,$y))
  if($hit -and $null -eq $st){$st=$y}
  if((-not $hit) -and $null -ne $st){ Write-Output ("   band y {0}..{1} (h {2}) colour #{3}" -f $st,($y-1),($y-$st),(Hex $bmp.GetPixel(1101,$st))); $st=$null }
}
if($null -ne $st){ Write-Output ("   band y {0}..{1} (h {2})" -f $st,837,(838-$st)) }

Write-Output '=== Q10: pill horizontal (y=733 row 1) ==='
$st=$null
for ($x=1010;$x -lt 1220;$x++){
  $hit = -not (IsWhite $bmp.GetPixel($x,733))
  if($hit -and $null -eq $st){$st=$x}
  if((-not $hit) -and $null -ne $st){ if(($x-$st) -gt 5){ Write-Output ("   band x {0}..{1} (w {2})" -f $st,($x-1),($x-$st)) }; $st=$null }
}

Write-Output '=== Q11: card borders colour ==='
Write-Output ("  KPI card1 top border (260,138) #{0}; left (260,180) #{1}" -f (Hex $bmp.GetPixel(300,138)), (Hex $bmp.GetPixel(260,180)))
Write-Output ("  chart card top (600,310) #{0}; table card top (600,624) #{1}" -f (Hex $bmp.GetPixel(600,310)), (Hex $bmp.GetPixel(600,624)))
Write-Output ("  card corner probe (261,139) #{0}" -f (Hex $bmp.GetPixel(261,139)))

$bmp.Dispose()
