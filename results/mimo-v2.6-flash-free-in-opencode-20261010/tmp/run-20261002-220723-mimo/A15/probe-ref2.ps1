# Second measurement pass over inputs/reference.png: chart geometry, gridlines,
# text bounding boxes, sidebar and table anchors. Read-only observation.
$ErrorActionPreference = 'Stop'
Set-Location $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Add-Type -AssemblyName System.Drawing

$REF = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tasks\A15-reference-reconstruction\inputs\reference.png')
$bmp = New-Object System.Drawing.Bitmap($REF)
$W = $bmp.Width; $H = $bmp.Height
function Hex($c) { '{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B }
function Lum($c) { (0.299 * $c.R) + (0.587 * $c.G) + (0.114 * $c.B) }

function InkBox($x0, $y0, $x1, $y1, [string]$mode, $thr) {
  $minX = 9999; $minY = 9999; $maxX = -1; $maxY = -1; $n = 0
  for ($y = $y0; $y -lt $y1; $y++) {
    for ($x = $x0; $x -lt $x1; $x++) {
      $c = $bmp.GetPixel($x, $y); $l = Lum $c; $hit = $false
      if ($mode -eq 'dark')  { if ($l -lt $thr) { $hit = $true } }
      elseif ($mode -eq 'light') { if ($l -gt $thr) { $hit = $true } }
      elseif ($mode -eq 'blue')  { if ($c.B -gt 150 -and $c.B -gt ($c.R + 60) -and $c.B -gt ($c.G + 60)) { $hit = $true } }
      elseif ($mode -eq 'notwhite') { if (-not ($c.R -gt 248 -and $c.G -gt 248 -and $c.B -gt 248)) { $hit = $true } }
      if ($hit) { $n++; if ($x -lt $minX) { $minX = $x }; if ($x -gt $maxX) { $maxX = $x }; if ($y -lt $minY) { $minY = $y }; if ($y -gt $maxY) { $maxY = $y } }
    }
  }
  if ($maxX -lt 0) { return $null }
  return [pscustomobject]@{ x = $minX; y = $minY; w = ($maxX - $minX + 1); h = ($maxY - $minY + 1); right = $maxX; bottom = $maxY; ink = $n }
}
function Show($name, $b) {
  if ($null -eq $b) { Write-Output ("  {0,-26} -" -f $name); return }
  Write-Output ("  {0,-26} x={1,-5} y={2,-5} w={3,-4} h={4,-4} right={5} bottom={6}" -f $name, $b.x, $b.y, $b.w, $b.h, $b.right, $b.bottom)
}

Write-Output '=== chart bars (colour #245CE4) ==='
$barX = @(@(357,410),@(458,511),@(559,612),@(660,713),@(761,814),@(862,915))
$months = @('Apr','May','Jun','Jul','Aug','Sep')
for ($i = 0; $i -lt 6; $i++) {
  $cx = [int](($barX[$i][0] + $barX[$i][1]) / 2)
  $top = -1; $bot = -1
  for ($y = 380; $y -lt 600; $y++) {
    $c = $bmp.GetPixel($cx, $y)
    if ($c.B -gt 150 -and $c.B -gt ($c.R + 60) -and $c.B -gt ($c.G + 60)) { if ($top -lt 0) { $top = $y }; $bot = $y }
  }
  Write-Output ("  {0} cx={1} x={2}..{3} top={4} bottom={5} h={6}" -f $months[$i], $cx, $barX[$i][0], $barX[$i][1], $top, $bot, ($bot - $top + 1))
}

Write-Output '=== horizontal lines / gridlines (scan x=640, y 390..610) ==='
for ($y = 390; $y -lt 610; $y++) {
  $c = $bmp.GetPixel(640, $y)
  if (-not ($c.R -gt 248 -and $c.G -gt 248 -and $c.B -gt 248)) {
    Write-Output ("  y={0} #{1} lum={2}" -f $y, (Hex $c), [math]::Round((Lum $c),1))
  }
}

Write-Output '=== chart axis / labels ==='
Show 'y-tick labels (120..0)'   (InkBox 270 400 335 585 'dark' 160)
Show 'unit label Y-thousand'    (InkBox 270 370 360 392 'dark' 175)
Show 'x-month labels'           (InkBox 340 558 940 585 'dark' 160)
Show 'title Net revenue'        (InkBox 270 325 520 365 'dark' 140)
Show 'period Apr-Sep'           (InkBox 840 330 990 360 'dark' 175)

Write-Output '=== header ==='
Show 'title Workspace Overview' (InkBox 250 25 900 78 'dark' 140)
Show 'subtitle date'            (InkBox 250 78 900 108 'dark' 175)
Show 'button label (white)'     (InkBox 1190 46 1396 88 'light' 210)

Write-Output '=== KPI card 1 ==='
Show 'label REVENUE'            (InkBox 270 152 460 180 'dark' 175)
Show 'value yen128,400'         (InkBox 270 182 520 235 'dark' 140)
Show 'change +12.4%'            (InkBox 270 238 460 268 'dark' 175)
Show 'label ORDERS'             (InkBox 654 152 840 180 'dark' 175)
Show 'value 426'                (InkBox 654 182 900 235 'dark' 140)
Show 'label REFUND RATE'        (InkBox 1038 152 1240 180 'dark' 175)

Write-Output '=== section titles / activity ==='
Show 'Team activity title'      (InkBox 1040 325 1260 365 'dark' 140)
Show 'activity text block'      (InkBox 1066 390 1300 560 'dark' 160)
Show 'Recent projects title'    (InkBox 270 635 520 678 'dark' 140)

Write-Output '=== activity dots (saturated colour in x 1045..1070) ==='
$dots = @(); $cur = $null
for ($y = 390; $y -lt 545; $y++) {
  $found = $null
  for ($x = 1044; $x -lt 1072; $x++) {
    $c = $bmp.GetPixel($x, $y)
    $mx = [math]::Max($c.R, [math]::Max($c.G, $c.B)); $mn = [math]::Min($c.R, [math]::Min($c.G, $c.B))
    if (($mx - $mn) -gt 45 -and $mx -gt 90) { $found = @{ x = $x; y = $y; hex = (Hex $c) } ; break }
  }
  if ($null -ne $found -and $null -eq $cur) { $cur = @{ y0 = $y; x0 = $found.x; x1 = $found.x; hex = $found.hex } }
  elseif ($null -ne $found -and $null -ne $cur) { if ($found.x -lt $cur.x0) { $cur.x0 = $found.x }; if ($found.x -gt $cur.x1) { $cur.x1 = $found.x }; $cur.y1 = $y }
  elseif ($null -eq $found -and $null -ne $cur) { $dots += $cur; $cur = $null }
}
if ($null -ne $cur) { $dots += $cur }
foreach ($d in $dots) { Write-Output ("  dot y {0}..{1} x {2}..{3} #{4}" -f $d.y0, $d.y1, $d.x0, $d.x1, $d.hex) }

Write-Output '=== sidebar ==='
Show 'logo mark'                (InkBox 18 24 62 72 'light' 90)
Show 'brand NORTHSTAR'          (InkBox 66 30 210 66 'light' 140)
Show 'nav text block'           (InkBox 52 118 200 345 'light' 140)
Show 'sidebar card text block'  (InkBox 34 760 190 856 'light' 130)
# selected pill (#294467) bbox
$px0=9999;$px1=-1;$py0=9999;$py1=-1
for ($y=100; $y -lt 180; $y++) { for ($x=0; $x -lt 220; $x++) {
  $c=$bmp.GetPixel($x,$y)
  if ([math]::Abs($c.R-0x29) -le 8 -and [math]::Abs($c.G-0x44) -le 8 -and [math]::Abs($c.B-0x67) -le 8) {
    if($x -lt $px0){$px0=$x}; if($x -gt $px1){$px1=$x}; if($y -lt $py0){$py0=$y}; if($y -gt $py1){$py1=$y}
  } } }
Write-Output ("  selected pill x {0}..{1} (w {2}) y {3}..{4} (h {5})" -f $px0,$px1,($px1-$px0+1),$py0,$py1,($py1-$py0+1))
# sidebar card (#233954) bbox
$px0=9999;$px1=-1;$py0=9999;$py1=-1
for ($y=730; $y -lt 880; $y++) { for ($x=0; $x -lt 220; $x++) {
  $c=$bmp.GetPixel($x,$y)
  if ([math]::Abs($c.R-0x23) -le 7 -and [math]::Abs($c.G-0x39) -le 7 -and [math]::Abs($c.B-0x54) -le 7) {
    if($x -lt $px0){$px0=$x}; if($x -gt $px1){$px1=$x}; if($y -lt $py0){$py0=$y}; if($y -gt $py1){$py1=$y}
  } } }
Write-Output ("  sidebar card x {0}..{1} (w {2}) y {3}..{4} (h {5})" -f $px0,$px1,($px1-$px0+1),$py0,$py1,($py1-$py0+1))

Write-Output '=== table ==='
Show 'header band (#F3F6FB)'    (InkBox 262 686 1398 724 'notwhite' 0)
Show 'row1 project text'        (InkBox 275 730 600 755 'dark' 150)
Show 'row2 project text'        (InkBox 275 764 600 792 'dark' 150)
Show 'row3 project text'        (InkBox 275 798 600 826 'dark' 150)
Show 'col OWNER header'         (InkBox 775 692 900 716 'dark' 175)
Show 'col STATUS header'        (InkBox 1040 692 1160 716 'dark' 175)
Show 'col DUE header'           (InkBox 1220 692 1330 716 'dark' 175)
# pill vertical extents at x=1035 (inside pill, left of text)
foreach ($yy in @(741, 775, 809)) {
  $t=-1;$b=-1
  for ($y = $yy-30; $y -lt $yy+30; $y++) { $c=$bmp.GetPixel(1035,$y); if (-not ($c.R -gt 248 -and $c.G -gt 248 -and $c.B -gt 248)) { if($t -lt 0){$t=$y}; $b=$y } }
  Write-Output ("  pill near y={0}: top={1} bottom={2} h={3}" -f $yy,$t,$b,($b-$t+1))
}
# row separator lines (scan x=1300, y 715..845)
Write-Output '--- row separators (x=1300, non-white) ---'
for ($y=715; $y -lt 850; $y++) { $c=$bmp.GetPixel(1300,$y); if(-not ($c.R -gt 248 -and $c.G -gt 248 -and $c.B -gt 248)) { Write-Output ("   y={0} #{1}" -f $y,(Hex $c)) } }

Write-Output '=== footer ==='
Show 'footer text'              (InkBox 255 860 600 885 'dark' 175)

Write-Output '=== title row alignment ==='
Write-Output ("  content left (title ink x) and KPI card left = 260; sidebar width = 220")

$bmp.Dispose()
