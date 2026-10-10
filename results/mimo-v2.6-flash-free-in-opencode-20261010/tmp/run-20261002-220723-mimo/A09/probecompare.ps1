# Compare the three probe variants pixel-for-pixel and check each against the
# analytic transform (this is the pixel method geometry-audit.json will cite).
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$T    = "$root\tmp\$RUN\A09"
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap("$T\probe-atlas-v05.png")

$CY = 268
$cards = @{ A = 390; B = 670; C = 950 }
$HW = 90   # window half-size -> 180x180 window around each stamp centre

function Window($bmp, [int]$cx, [int]$cy, [int]$hw) {
  $a = New-Object 'object[,]' (2*$hw+1), (2*$hw+1)
  for ($i = 0; $i -lt (2*$hw+1); $i++) {
    for ($j = 0; $j -lt (2*$hw+1); $j++) {
      $p = $bmp.GetPixel($cx - $hw + $j, $cy - $hw + $i)
      $a[$i,$j] = ("{0:X2}{1:X2}{2:X2}" -f $p.R, $p.G, $p.B)
    }
  }
  return ,$a
}
function DiffPng($a, $b, [int]$hw) {
  $n = 0; $maxd = 0
  for ($i = 0; $i -lt (2*$hw+1); $i++) {
    for ($j = 0; $j -lt (2*$hw+1); $j++) {
      $va = $a[$i,$j]; $vb = $b[$i,$j]
      if ($va -ne $vb) {
        $n++
        $ra = [Convert]::ToInt32($va.Substring(0,2),16); $ga = [Convert]::ToInt32($va.Substring(2,2),16); $ba = [Convert]::ToInt32($va.Substring(4,2),16)
        $rb = [Convert]::ToInt32($vb.Substring(0,2),16); $gb = [Convert]::ToInt32($vb.Substring(2,2),16); $bb = [Convert]::ToInt32($vb.Substring(4,2),16)
        $d = [math]::Max([math]::Max([math]::Abs($ra-$rb), [math]::Abs($ga-$gb)), [math]::Abs($ba-$bb))
        if ($d -gt $maxd) { $maxd = $d }
      }
    }
  }
  return ,@($n, $maxd)
}

$wa = Window $bmp $cards.A $CY $HW
$wb = Window $bmp $cards.B $CY $HW
$wc = Window $bmp $cards.C $CY $HW
$ab = DiffPng $wa $wb $HW
$ac = DiffPng $wa $wc $HW
$bc = DiffPng $wb $wc $HW
"A vs B : {0} differing px, max channel delta {1}" -f $ab[0], $ab[1]
"A vs C : {0} differing px, max channel delta {1}" -f $ac[0], $ac[1]
"B vs C : {0} differing px, max channel delta {1}" -f $bc[0], $bc[1]

# --- analytic check: expected transformed corners of the identity card ------
# stamp rect 0 = (8,8,28,92) colour #E54B4B; centre of card id = 110
$idc = 110
$sv = @((8), (8))
$px = $idc - 60 + $sv[0]; $py = $CY - 60 + $sv[1]
"identity red rect expected top-left at ($px,$py); measured first red pixel:"
$found = $null
for ($y = $py - 4; $y -le $py + 6 -and $null -eq $found; $y++) {
  for ($x = $px - 4; $x -le $px + 6; $x++) {
    $p = $bmp.GetPixel($x, $y)
    if ([math]::Abs($p.R-229) -lt 12 -and [math]::Abs($p.G-75) -lt 12 -and [math]::Abs($p.B-75) -lt 12) { $found = "($x,$y)"; break }
  }
}
"  $found"
$bmp.Dispose()
