# A09 delivered-artifact verifier.
#  * re-parses the delivered PNG + .snapshot
#  * recomputes every transform independently from inputs/ (separate code path
#    from gen.ps1) and compares it with the matrix actually stored in the DSL
#  * samples the delivered PNG at analytically predicted points and measures the
#    ink bounding box, so every geometry claim is backed by pixels
#  * writes geometry-audit.json
param()
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$OUT  = "$root\outputs\$RUN\A09"
$IN   = "$root\tasks\A09-transform-atlas\inputs"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$CULT = [System.Globalization.CultureInfo]::InvariantCulture
Add-Type -AssemblyName System.Drawing

$pngPath = "$OUT\transform-atlas.png"
$dslPath = "$OUT\transform-atlas.snapshot"
$stampJ = Get-Content "$IN\stamp.json"      -Raw -Encoding UTF8 | ConvertFrom-Json
$transJ = Get-Content "$IN\transforms.json" -Raw -Encoding UTF8 | ConvertFrom-Json

$SK   = [double]$stampJ.size[0]; $SKH = [double]$stampJ.size[1]
$PVX  = [double]$stampJ.pivot[0]; $PVY = [double]$stampJ.pivot[1]
$COLR = @()
foreach ($r in $stampJ.rectangles) { $COLR += ,@([string]$r.color, [int]$r.xywh[0], [int]$r.xywh[1], [int]$r.xywh[2], [int]$r.xywh[3]) }
$DOTC = [string]$stampJ.dot.color
$DOCR = [double]$stampJ.dot.radius
$DOX  = [double]$stampJ.dot.center[0]; $DOY = [double]$stampJ.dot.center[1]

# ---------------------------------------------------------------- checks ----
$CHK = New-Object System.Collections.ArrayList
function AddChk([string]$cid, [string]$name, [bool]$ok, [string]$detail) {
  [void]$CHK.Add([pscustomobject]@{ id = $cid; check = $name; pass = $ok; detail = $detail })
}

# ------------------------------------------------------ independent math ----
function NN([double]$v) {
  if ([math]::Abs($v) -lt 0.0000005) { return '0' }
  return $v.ToString('0.######', $CULT)
}
function OpM([string]$nm, $a) {
  switch ($nm) {
    'rotate_clockwise_deg' {
      $r = [double]$a * [math]::PI / 180.0
      $co = [math]::Cos($r); $si = [math]::Sin($r)
      # row-major (a,b,c,d) = (cos, -sin, sin, cos)  ->  p' = R.p is clockwise
      # because y points down in pixel space
      return ("{0},{1},{2},{3}" -f (NN $co), (NN (-$si)), (NN $si), (NN $co))
    }
    'mirror_horizontal'    { return '-1,0,0,1' }
    'mirror_vertical'      { return '1,0,0,-1' }
    'scale_uniform'        { return ("{0},0,0,{0}" -f (NN ([double]$a))) }
    'scale_xy'             { return ("{0},0,0,{1}" -f (NN ([double]$a[0])), (NN ([double]$a[1]))) }
    default { throw "unknown op $nm" }
  }
}
function Split4([string]$s) {
  $p = $s.Split(',')
  if ($p.Count -ne 4) { throw "bad matrix '$s'" }
  return ,@([double]$p[0], [double]$p[1], [double]$p[2], [double]$p[3])
}
# p' = M . p,  M stored row-major "m00,m01,m10,m11"  (a,b,c,d)
# returns g applied after f, both given as "a,b,c,d" strings
function MatMul([string]$fstr, [string]$gstr) {
  $fp = $fstr.Split(','); $gp = $gstr.Split(',')
  if ($fp.Count -ne 4 -or $gp.Count -ne 4) { throw "bad matrix '$fstr' '$gstr'" }
  $f0 = [double]$fp[0]; $f1 = [double]$fp[1]; $f2 = [double]$fp[2]; $f3 = [double]$fp[3]
  $g0 = [double]$gp[0]; $g1 = [double]$gp[1]; $g2 = [double]$gp[2]; $g3 = [double]$gp[3]
  $r0 = $g0 * $f0 + $g1 * $f2
  $r1 = $g0 * $f1 + $g1 * $f3
  $r2 = $g2 * $f0 + $g3 * $f2
  $r3 = $g2 * $f1 + $g3 * $f3
  return ("{0},{1},{2},{3}" -f (NN $r0), (NN $r1), (NN $r2), (NN $r3))
}
function MapPt([double[]]$f, [double]$x, [double]$y) {
  $p = @(($f[0] * $x + $f[1] * $y), ($f[2] * $x + $f[3] * $y))
  return ("{0},{1}" -f $p[0], $p[1])
}
function Tuple4([double[]]$f) {
  return ("({0},{1},0,0,{2},{3},0,0,0,0,1,0,0,0,0,1)" -f (NN $f[0]), (NN $f[2]), (NN $f[1]), (NN $f[3]))
}

# ------------------------------------------------------- layout constants ---
$PngW = 1600; $PngH = 1200
$Cw = 300; $Ch = 250; $Gp = 32
$X0 = 152; $Y0 = 193
$SH = @{}   # short names, independent copy of the labelling rule
function ShortN($ops) {
  $out = @()
  $multi = ($ops.Count -gt 1)
  foreach ($o in $ops) {
    $nm = [string]$o[0]; $a = $o[1]
    if ($nm -eq 'rotate_clockwise_deg') {
      $v = [double]$a
      $vs = $v.ToString('0.######', $CULT)
      if ($multi) { $out += "旋转$vs°" } else { $out += "顺时针 $vs°" }
    }
    elseif ($nm -eq 'mirror_horizontal') { $out += '左右镜像' }
    elseif ($nm -eq 'mirror_vertical')   { $out += '上下镜像' }
    elseif ($nm -eq 'scale_uniform')     { $out += "等比缩放 $(NN ([double]$a))" }
    elseif ($nm -eq 'scale_xy')          { $out += "缩放 $(NN ([double]$a[0]))×$(NN ([double]$a[1]))" }
    else { $out += $nm }
  }
  return ($out -join [string][char]0x2192)
}

# ============================================================ PNG header ====
$pngBytes = [IO.File]::ReadAllBytes($pngPath)
$sigOk = ($pngBytes[0] -eq 137 -and $pngBytes[1] -eq 80 -and $pngBytes[2] -eq 78 -and $pngBytes[3] -eq 71)
$hdrW = ([int]$pngBytes[16] * 16777216) + ([int]$pngBytes[17] * 65536) + ([int]$pngBytes[18] * 256) + [int]$pngBytes[19]
$hdrH = ([int]$pngBytes[20] * 16777216) + ([int]$pngBytes[21] * 65536) + ([int]$pngBytes[22] * 256) + [int]$pngBytes[23]
AddChk 'P01' 'PNG signature' $sigOk ("first4={0}" -f ($pngBytes[0..3] -join ','))
AddChk 'P02' 'PNG size is 1600x1200' ($hdrW -eq $PngW -and $hdrH -eq $PngH) ("{0}x{1}" -f $hdrW, $hdrH)

# ============================================================ DSL + XML =====
$dslText = [IO.File]::ReadAllText($dslPath)
$firstByte = ([IO.File]::ReadAllBytes($dslPath))[0]
AddChk 'D01' 'DSL is UTF-8 without BOM' ($firstByte -eq 60) ("firstByte={0}" -f $firstByte)
$dslOk = $true; $dslErr = ''
try { [void]([xml]$dslText) } catch { $dslOk = $false; $dslErr = $_.Exception.Message }
AddChk 'D02' 'DSL parses as XML' $dslOk $dslErr

# every <Transform> in the delivered file
$trRe = [regex]'<Transform\s+matrix="(\([^"]*\))"\s+origin="\(60,60\)">'
$trMs = $trRe.Matches($dslText)
AddChk 'D03' 'exactly 12 <Transform matrix origin=(60,60)> elements' ($trMs.Count -eq 12) ("count=$($trMs.Count)")
$dslMatrix = @()
foreach ($m in $trMs) { $dslMatrix += $m.Groups[1].Value }

# cell panels: 12 x 300x250 at the prescribed grid
$cellRe = [regex]'<Positioned left="(\d+)" top="(\d+)" width="300" height="250"><Container width="300" height="250"'
$cellMs = $cellRe.Matches($dslText)
AddChk 'G01' '12 cell panels of 300x250 present' ($cellMs.Count -eq 12) ("count=$($cellMs.Count)")
$dslCell = @()
foreach ($m in $cellMs) { $dslCell += ,@([int]$m.Groups[1].Value, [int]$m.Groups[2].Value) }

# labels
$fsRe = [regex]'fontSize="(\d+)"'
$fsVals = @()
foreach ($m in $fsRe.Matches($dslText)) { $fsVals += [int]$m.Groups[1].Value }
$minFs = ($fsVals | Measure-Object -Minimum).Minimum
AddChk 'L01' 'every label >= 20pt' ($minFs -ge 20) ("min=$minFs count=$($fsVals.Count)")

# unmodified source shape coordinates - proves the matrix does the work
$shapeChecks = @()
foreach ($r in $stampJ.rectangles) {
  $needle = ('<Positioned left="{0}" top="{1}"><Container width="{2}" height="{3}" color="{4}"/>' -f $r.xywh[0], $r.xywh[1], $r.xywh[2], $r.xywh[3], $r.color)
  $n = [regex]::Matches($dslText, [regex]::Escape($needle)).Count
  $shapeChecks += ,@($needle, $n)
}
$dotNeedle = ('<Positioned left="{0}" top="{1}" width="{2}" height="{2}"><Container width="{2}" height="{2}" color="{3}" shape="CIRCLE"/>' -f ($DOX - $DOCR), ($DOY - $DOCR), ($DOCR * 2), $DOTC)
$dotN = [regex]::Matches($dslText, [regex]::Escape($dotNeedle)).Count
$shapesOk = $true
$shapeDetail = @()
foreach ($sc in $shapeChecks) { if ($sc[1] -ne 12) { $shapesOk = $false }; $shapeDetail += "$($sc[1])" }
if ($dotN -ne 12) { $shapesOk = $false }
$shapeDetail += "$dotN"
AddChk 'S01' 'source shape coordinates byte-identical in all 12 cells (12x each)' $shapesOk ("occurrences=" + ($shapeDetail -join '/'))

# tick guide elements
$nTickV = [regex]::Matches($dslText, '<Container width="8" height="1" color="#A9B2C2"/>').Count
$nTickH = [regex]::Matches($dslText, '<Container width="1" height="8" color="#A9B2C2"/>').Count
$nCrossV = [regex]::Matches($dslText, '<Container width="15" height="1" color="#A9B2C2"/>').Count
$nCrossH = [regex]::Matches($dslText, '<Container width="1" height="15" color="#A9B2C2"/>').Count
AddChk 'K01' '8 horizontal-axis ticks per cell (96 total)' ($nTickV -eq 96) ("count=$nTickV")
AddChk 'K02' '8 vertical-axis ticks per cell (96 total)' ($nTickH -eq 96) ("count=$nTickH")
AddChk 'K03' 'centre cross per cell (12+12)' ($nCrossV -eq 12 -and $nCrossH -eq 12) ("$nCrossV/$nCrossH")

# ================================================= independent transforms ===
$IDS = @(); $MLIST = @(); $OPJ = @(); $SNAME = @()
foreach ($tf in $transJ) {
  $mstr = '1,0,0,1'
  foreach ($o in $tf.operations) {
    $mstr = (MatMul $mstr (OpM ([string]$o[0]) $o[1]))
  }
  $md = $mstr.Split(',')
  $IDS += [string]$tf.id
  $MLIST += ,@([double]$md[0], [double]$md[1], [double]$md[2], [double]$md[3])
  $OPJ += ,@($tf.operations)
  $SNAME += (ShortN $tf.operations)
}
AddChk 'M01' '12 transforms loaded' ($IDS.Count -eq 12) ("count=$($IDS.Count)")

$matOk = $true; $matDiff = @()
for ($i = 0; $i -lt $IDS.Count; $i++) {
  $exp = (Tuple4 ([double[]]$MLIST[$i]))
  if ($exp -ne $dslMatrix[$i]) { $matOk = $false; $matDiff += "$($IDS[$i]):$exp vs $($dslMatrix[$i])" }
}
AddChk 'M02' 'DSL matrix == independently recomposed matrix for all 12' $matOk (($matDiff -join '; '))

$o7 = [array]::IndexOf($IDS, 'T07'); $o8 = [array]::IndexOf($IDS, 'T08')
$ordOk = ($dslMatrix[$o7] -ne $dslMatrix[$o8])
AddChk 'M03' 'T07 and T08 carry different matrices (order matters)' $ordOk ("T07=" + $dslMatrix[$o7] + " T08=" + $dslMatrix[$o8])
$det = ($MLIST[$o7][0] * $MLIST[$o7][3] - $MLIST[$o7][1] * $MLIST[$o7][2])
AddChk 'M04' 'T07 determinant == -1 (mirror+rotation, not a pure rotation)' ([math]::Abs($det - (-1.0)) -lt 1e-9) ("det=$det")

# grid placement
$gridOk = $true; $gridBad = @()
for ($i = 0; $i -lt 12; $i++) {
  $cx = $X0 + ($i % 4) * ($Cw + $Gp)
  $cy = $Y0 + [int][math]::Floor($i / 4) * ($Ch + $Gp)
  if ($dslCell[$i][0] -ne $cx -or $dslCell[$i][1] -ne $cy) { $gridOk = $false; $gridBad += "$($IDS[$i])=$($dslCell[$i][0]),$($dslCell[$i][1])!=$cx,$cy" }
}
AddChk 'G02' 'cell origins match 4x3 grid (gap 32, block centred)' $gridOk (($gridBad -join '; '))
$blkW = 4 * $Cw + 3 * $Gp; $blkH = 3 * $Ch + 2 * $Gp
AddChk 'G03' 'grid block is centred in the 1600x1200 canvas' (($X0 -eq ($PngW - $blkW) / 2) -and ($Y0 -eq ($PngH - $blkH) / 2)) ("block=${blkW}x${blkH} origin=$X0,$Y0")

# every cell must carry its id and its operation short name as a label
$idMiss = @(); $nmMiss = @()
for ($i = 0; $i -lt $IDS.Count; $i++) {
  if ($dslText.IndexOf(('>{0}</Text>' -f $IDS[$i])) -lt 0) { $idMiss += $IDS[$i] }
  if ($dslText.IndexOf(('>{0}</Text>' -f $SNAME[$i])) -lt 0) { $nmMiss += "$($IDS[$i])=$($SNAME[$i])" }
}
AddChk 'L02' 'all 12 cell ids present as text labels' ($idMiss.Count -eq 0) (($idMiss -join ', '))
AddChk 'L03' 'all 12 operation short names present as text labels' ($nmMiss.Count -eq 0) (($nmMiss -join ', '))

# ============================================================ pixel work ====
$bmp = [System.Drawing.Bitmap]::new($pngPath)

function RGB([string]$hex) {
  $h = $hex.TrimStart('#')
  return ,@([Convert]::ToInt32($h.Substring(0, 2), 16), [Convert]::ToInt32($h.Substring(2, 2), 16), [Convert]::ToInt32($h.Substring(4, 2), 16))
}
function Near($p, [int]$r, [int]$g, [int]$b, [int]$tol) {
  $d = [math]::Max([math]::Max([math]::Abs($p.R - $r), [math]::Abs($p.G - $g)), [math]::Abs($p.B - $b))
  return $d -le $tol
}
# Ink detection for the bounding-box scan.  Every background element this atlas
# can put under the stamp is a light, low-chroma grey:
#   #FFFFFF #F7F9FC #DCE1EA #D3D9E3 #C9D0DC #A9B2C2  -> chroma <= 25, min >= 169
# while the three rectangle fills are strongly saturated
#   #E54B4B (154)  #2364DB (184)  #EAB53B (175)
# and the dot is near black (min channel 17).  So a pixel belongs to the ink
# when it is visibly coloured (chroma > 35) or clearly dark (min < 120), and no
# background tone or blend of two background tones can qualify.
# No coverage threshold is applied: even a sub-half-coverage anti-aliased
# vertex sliver counts, so the measured edge always falls in
# [floor(edge), ceil(edge)-1] and the residual error stays below 1px.
function StampPx($p) {
  $rp = [int]$p.R; $gp = [int]$p.G; $bp = [int]$p.B
  $mxv = [math]::Max($rp, [math]::Max($gp, $bp))
  $mnv = [math]::Min($rp, [math]::Min($gp, $bp))
  if (($mxv - $mnv) -gt 35) { return $true }
  if ($mnv -lt 120) { return $true }
  return $false
}
function BBoxIn([int]$x0, [int]$y0, [int]$x1, [int]$y1) {
  $mnX = 100000; $mnY = 100000; $mxX = -1; $mxY = -1
  for ($y = $y0; $y -le $y1; $y++) {
    for ($x = $x0; $x -le $x1; $x++) {
      if (StampPx ($bmp.GetPixel($x, $y))) {
        if ($x -lt $mnX) { $mnX = $x }
        if ($x -gt $mxX) { $mxX = $x }
        if ($y -lt $mnY) { $mnY = $y }
        if ($y -gt $mxY) { $mxY = $y }
      }
    }
  }
  return ,@($mnX, $mnY, $mxX, $mxY)
}

$auditCells = @()
$worstBbox = 0.0; $cornerTotal = 0; $cornerFail = 0; $dotFail = 0
$clipFail = 0; $cellFail = 0

for ($i = 0; $i -lt $IDS.Count; $i++) {
  $id = $IDS[$i]
  $m = [double[]]$MLIST[$i]
  $col = $i % 4; $row = [int][math]::Floor($i / 4)
  $cx0 = $X0 + $col * ($Cw + $Gp); $cy0 = $Y0 + $row * ($Ch + $Gp)
  $mx = $cx0 + 150; $my = $cy0 + 125

  # expected canvas point for a stamp-local point:
  #   display = (cellCentre - pivot) + pivot + L(p - pivot)
  #           = cellCentre + L(p - pivot)
  $expX0 = 1e9; $expY0 = 1e9; $expX1 = -1e9; $expY1 = -1e9
  $rectOut = @()
  for ($ri = 0; $ri -lt $COLR.Count; $ri++) {
    $cc = $COLR[$ri]
    $sxp = [double]$cc[1]; $syp = [double]$cc[2]; $swp = [double]$cc[3]; $shp = [double]$cc[4]
    $rgbv = RGB $cc[0]
    # flat x0,y0  x1,y1  x2,y2  x3,y3  (clockwise from top-left of the source rect)
    $cornersL = @($sxp, $syp, ($sxp + $swp), $syp, ($sxp + $swp), ($syp + $shp), $sxp, ($syp + $shp))
    $rcx = $sxp + $swp / 2.0; $rcy = $syp + $shp / 2.0
    $ccOut = @()
    for ($k = 0; $k -lt 4; $k++) {
      $lx = [double]$cornersL[2 * $k]
      $ly = [double]$cornersL[2 * $k + 1]
      # stamp-local transform about the pivot, then placed on the canvas:
      #   cellCentre + L(p - pivot)
      $tv = (MapPt $m ($lx - $PVX) ($ly - $PVY)) -split ','
      $cxD = [double]$tv[0] + [double]$mx
      $cyD = [double]$tv[1] + [double]$my
      # inward edge directions (local) -> transformed -> unit length
      $ix = $(if ($lx -lt $rcx) { 1.0 } else { -1.0 })
      $iy = $(if ($ly -lt $rcy) { 1.0 } else { -1.0 })
      $u1 = (MapPt $m $ix 0) -split ','
      $n1 = [math]::Sqrt([double]$u1[0] * [double]$u1[0] + [double]$u1[1] * [double]$u1[1])
      $u1x = [double]$u1[0] / $n1; $u1y = [double]$u1[1] / $n1
      $u2 = (MapPt $m 0 $iy) -split ','
      $n2 = [math]::Sqrt([double]$u2[0] * [double]$u2[0] + [double]$u2[1] * [double]$u2[1])
      $u2x = [double]$u2[0] / $n2; $u2y = [double]$u2[1] / $n2
      $sx = [int][math]::Round($cxD + 3.0 * $u1x + 3.0 * $u2x)
      $sy = [int][math]::Round($cyD + 3.0 * $u1y + 3.0 * $u2y)
      $got = $bmp.GetPixel($sx, $sy)
      $okc = Near $got $rgbv[0] $rgbv[1] $rgbv[2] 30
      $cornerTotal++
      if (-not $okc) { $cornerFail++ }
      $ccOut += ,@([math]::Round($cxD, 3), [math]::Round($cyD, 3), $sx, $sy, ("#{0:X2}{1:X2}{2:X2}" -f $got.R, $got.G, $got.B), $okc)
      if ($cxD -lt $expX0) { $expX0 = $cxD }
      if ($cyD -lt $expY0) { $expY0 = $cyD }
      if ($cxD -gt $expX1) { $expX1 = $cxD }
      if ($cyD -gt $expY1) { $expY1 = $cyD }
    }
    $cl = @(); $cv = @(); $pb = @()
    for ($k = 0; $k -lt 4; $k++) {
      $cl += ,@([double]$cornersL[2 * $k], [double]$cornersL[2 * $k + 1])
      $cv += ,@([double]$ccOut[$k][0], [double]$ccOut[$k][1])
      $pb += [pscustomobject]@{
        canvas         = @([int]$ccOut[$k][2], [int]$ccOut[$k][3])
        stepped_from   = @([double]$ccOut[$k][0], [double]$ccOut[$k][1])
        sampled_colour = [string]$ccOut[$k][4]
        match          = [bool]$ccOut[$k][5]
      }
    }
    $rectOut += [pscustomobject]@{
      color          = [string]$cc[0]
      source_xywh    = @([int]$cc[1], [int]$cc[2], [int]$cc[3], [int]$cc[4])
      corners_local  = $cl
      corners_canvas = $cv
      probes         = $pb
    }
  }

  # ---- dot ----
  $dt = MapPt $m ($DOX - $PVX) ($DOY - $PVY)
  $dtv = $dt -split ','
  $dotX = [double]$mx + [double]$dtv[0]; $dotY = [double]$my + [double]$dtv[1]
  $dg = RGB $DOTC
  $dotPx = $bmp.GetPixel([int][math]::Round($dotX), [int][math]::Round($dotY))
  $dotOk = Near $dotPx $dg[0] $dg[1] $dg[2] 30
  if (-not $dotOk) { $dotFail++ }
  # dot ellipse bbox under the linear map
  $hw = $DOCR * [math]::Sqrt($m[0] * $m[0] + $m[1] * $m[1])
  $hh = $DOCR * [math]::Sqrt($m[2] * $m[2] + $m[3] * $m[3])
  $dBx0 = $dotX - $hw; $dBy0 = $dotY - $hh; $dBx1 = $dotX + $hw; $dBy1 = $dotY + $hh
  if ($dBx0 -lt $expX0) { $expX0 = $dBx0 }
  if ($dBy0 -lt $expY0) { $expY0 = $dBy0 }
  if ($dBx1 -gt $expX1) { $expX1 = $dBx1 }
  if ($dBy1 -gt $expY1) { $expY1 = $dBy1 }

  # ---- measured ink bbox ----
  $winX0 = $mx - 100; $winY0 = $cy0 + 40; $winX1 = $mx + 100; $winY1 = $my + 90
  $winOk = ($expX0 -gt ($winX0 + 1)) -and ($expX1 -lt ($winX1 - 1)) -and ($expY0 -gt ($winY0 + 1)) -and ($expY1 -lt ($winY1 - 1))
  $mb = BBoxIn $winX0 $winY0 $winX1 $winY1
  $eX0 = [math]::Abs($mb[0] - $expX0)
  $eY0 = [math]::Abs($mb[1] - $expY0)
  $eX1 = [math]::Abs($mb[2] - $expX1)
  $eY1 = [math]::Abs($mb[3] - $expY1)
  $eMax = [math]::Max([math]::Max($eX0, $eY0), [math]::Max($eX1, $eY1))
  if ($eMax -gt $worstBbox) { $worstBbox = $eMax }

  # ---- clipping: expected ink must stay inside the cell panel ----
  $clip = ($expX0 -ge ($cx0 + 1)) -and ($expX1 -le ($cx0 + $Cw - 1)) -and ($expY0 -ge ($cy0 + 1)) -and ($expY1 -le ($cy0 + $Ch - 1))
  if (-not $clip) { $clipFail++ }
  $cellOk = ($winOk -and $clip)
  if (-not $cellOk) { $cellFail++ }

  $auditCells += [pscustomobject]@{
    id = $id
    operations = $OPJ[$i]
    short_name = $SNAME[$i]
    cell_index = $i
    cell_rect = @($cx0, $cy0, $Cw, $Ch)
    cell_centre = @($mx, $my)
    stamp_positioned_offset = @(($mx - $PVX), ($my - $PVY))
    transform_origin_local = @($PVX, $PVY)
    matrix_row_major_2x2 = @($m[0], $m[1], $m[2], $m[3])
    matrix_column_major_4x4 = @($m[0], $m[2], 0, 0, $m[1], $m[3], 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
    matrix_tuple_dsl = $dslMatrix[$i]
    matrix_matches_recomposition = ($dslMatrix[$i] -eq (Tuple4 $m))
    rectangles = $rectOut
    dot = [pscustomobject]@{
      source_center = @($DOX, $DOY); source_radius = $DOCR
      centre_canvas = @([math]::Round($dotX, 3), [math]::Round($dotY, 3))
      ellipse_halfextents = @([math]::Round($hw, 3), [math]::Round($hh, 3))
      probe_canvas = @([int][math]::Round($dotX), [int][math]::Round($dotY))
      probe_sampled = ("#{0:X2}{1:X2}{2:X2}" -f $dotPx.R, $dotPx.G, $dotPx.B)
      match = $dotOk
    }
    ink_bbox_expected = @([math]::Round($expX0, 3), [math]::Round($expY0, 3), [math]::Round($expX1, 3), [math]::Round($expY1, 3))
    ink_bbox_measured = @($mb[0], $mb[1], $mb[2], $mb[3])
    ink_bbox_error_px = @([math]::Round($eX0, 3), [math]::Round($eY0, 3), [math]::Round($eX1, 3), [math]::Round($eY1, 3))
    ink_bbox_max_error_px = [math]::Round($eMax, 3)
    within_1_5px = ($eMax -le 1.5)
    scan_window = @($winX0, $winY0, $winX1, $winY1)
    scan_window_covers_ink = $winOk
    ink_inside_cell_no_clipping = $clip
  }
}

AddChk 'X01' 'all 48 rectangle corner probes land on the declared colour (<=30 delta)' ($cornerFail -eq 0) ("fail=$cornerFail/$cornerTotal")
AddChk 'X02' 'all 12 dot-centre probes land on the dot colour (<=30 delta)' ($dotFail -eq 0) ("fail=$dotFail/12")
AddChk 'X03' 'every ink bbox within 1.5px of the analytic bbox' ($worstBbox -le 1.5) ("worst=$([math]::Round($worstBbox,3))px")
AddChk 'X04' 'no transformed subject is clipped by its cell' ($clipFail -eq 0) ("fail=$clipFail/12")
AddChk 'X05' 'scan window fully contains the analytic ink' ($cellFail -eq 0) ("fail=$cellFail/12")

# ---- tick guide pixels: cell T09 (index 8) has the smallest stamp, so every
#      tick at +/-80 units is guaranteed to be free of stamp ink ----
$i9 = [array]::IndexOf($IDS, 'T09')
$mx9 = $X0 + 0 * ($Cw + $Gp) + 150; $my9 = $Y0 + 2 * ($Ch + $Gp) + 125
$tkOk = $true; $tkDet = @()
$tkX = @(($mx9 - 80), ($mx9 + 80), ($mx9 + 4), ($mx9 + 4), $mx9)
$tkY = @(($my9 - 3), ($my9 - 3), ($my9 - 80), ($my9 + 80), $my9)
$tkCol = RGB '#A9B2C2'
for ($ti = 0; $ti -lt $tkX.Count; $ti++) {
  $px = $bmp.GetPixel([int]$tkX[$ti], [int]$tkY[$ti])
  $okv = Near $px $tkCol[0] $tkCol[1] $tkCol[2] 45
  if (-not $okv) { $tkOk = $false }
  $tkDet += ("({0},{1})=#{2:X2}{3:X2}{4:X2}" -f [int]$tkX[$ti], [int]$tkY[$ti], $px.R, $px.G, $px.B)
}
AddChk 'K04' 'tick/centre guide pixels actually rendered in cell T09' $tkOk (($tkDet -join ' '))

$bmp.Dispose()

# ============================================================ audit file ====
$failCount = 0
foreach ($c in $CHK) { if (-not $c.pass) { $failCount++ } }

$pngSha = (Get-FileHash -Algorithm SHA256 $pngPath).Hash
$dslSha = (Get-FileHash -Algorithm SHA256 $dslPath).Hash

$audit = [pscustomobject]@{
  task_id       = 'A09'
  generated_at  = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  run_id        = $RUN
  artifacts     = [pscustomobject]@{
    png      = "outputs/$RUN/A09/transform-atlas.png"
    png_bytes = (Get-Item $pngPath).Length
    png_sha256 = $pngSha
    png_size  = @($hdrW, $hdrH)
    dsl      = "outputs/$RUN/A09/transform-atlas.snapshot"
    dsl_bytes = (Get-Item $dslPath).Length
    dsl_sha256 = $dslSha
    dsl_bom   = (-not ($firstByte -eq 60))
    transform_elements = $trMs.Count
    element_count = ([xml]$dslText).SelectNodes('//*').Count
  }
  layout = [pscustomobject]@{
    canvas = @($PngW, $PngH)
    grid = @{ columns = 4; rows = 3; cell = @($Cw, $Ch); gap = $Gp; block = @($blkW, $blkH); origin = @($X0, $Y0); centred = $true }
    stamp_source = [pscustomobject]@{ size = @($SK, $SKH); pivot = @($PVX, $PVY) }
    title_band = 'y 0..193 (title + 2 caption lines)'
    legend_band = 'y 1007..1200 (6 legend keys + 3 explanation lines)'
  }
  labels = [pscustomobject]@{
    min_font_size = $minFs
    used_sizes = (@($fsVals | Sort-Object -Unique) -join ',')
    count = $fsVals.Count
    requirement = '>=20'
    pass = ($minFs -ge 20)
  }
  verification_method = [pscustomobject]@{
    tolerance_px = 1.5
    corner_probe = 'For each of the 4 corners of each source rectangle: map the corner through the independently recomposed linear part about pivot (60,60) and place it on the canvas (cell centre + L*(p-pivot)). Step 3px inward from the corner along BOTH transformed edge directions (unit-normalised) and read the pixel; it must be within a max-channel delta of 30 of the rectangle''s declared colour. Points are interior points, so the anti-aliased edge band is never sampled.'
    dot_probe = 'Map the source dot centre (91,49) the same way, sample the rounded pixel, require max-channel delta <= 30 from #111111.'
    bbox_probe = 'Independently compute the analytic ink bounding box as the union of the 4 transformed corners of every rectangle and the axis-aligned bbox of the transformed dot ellipse (half-axes r*sqrt(a^2+b^2), r*sqrt(c^2+d^2)). Then scan the cell window and take min/max x,y over every pixel the atlas palette can only produce from stamp ink: chroma (max-min channel) > 35 or min channel < 120.'
    antialiasing_exception = 'The palette separation is what excludes anti-aliased edges without ever demanding an exact colour at one: every background tone and every blend of two background tones is a light grey with chroma <= 25 and min channel >= 169, so it can never be counted as ink, while an edge pixel needs only ~0.23 coverage of a rectangle fill (or ~0.56 of the dot) to qualify. Because no coverage threshold is applied to the near side, a sub-half-coverage vertex sliver is still counted and the measured edge always lands in [floor(edge), ceil(edge)-1]; the residual error is therefore below 1px by construction, and the analytic-exclusive-edge convention (an edge at x=346.0 covers through pixel 345) accounts for the remaining 1px on the right/bottom sides. Tolerance 1.5px.'
    clip_check = 'The analytic ink box must lie strictly inside the 300x250 cell panel, and the measured box must equal the analytic box - a clipped subject would shrink the measured box and fail the 1.5px comparison.'
    matrix_check = 'gen.ps1 composes the operations; this verifier composes them again with a separate row-major 2x2 implementation and formats the column-major 4x4 tuple itself, then compares it byte-for-byte with the matrix attribute stored in the delivered .snapshot.'
  }
  checks = @($CHK)
  summary = [pscustomobject]@{
    checks_total = $CHK.Count
    checks_passed = ($CHK.Count - $failCount)
    checks_failed = $failCount
    rectangle_corner_probes = $cornerTotal
    rectangle_corner_probes_failed = $cornerFail
    dot_probes = 12
    dot_probes_failed = $dotFail
    worst_bbox_error_px = [math]::Round($worstBbox, 3)
    t07_matrix = $dslMatrix[$o7]
    t08_matrix = $dslMatrix[$o8]
    t07_t08_differ = $ordOk
    all_within_1_5px = ($worstBbox -le 1.5)
    status = $(if ($failCount -eq 0) { 'PASS' } else { 'FAIL' })
  }
  cells = $auditCells
}

$json = $audit | ConvertTo-Json -Depth 12
$json = [regex]::Replace($json, '\\u([0-9a-fA-F]{4})', { param($mm) [string][char][System.Int32]::Parse($mm.Groups[1].Value, [System.Globalization.NumberStyles]::HexNumber) })
[IO.File]::WriteAllText("$OUT\geometry-audit.json", $json, $utf8)

Write-Host "geometry-audit.json  bytes=$((Get-Item "$OUT\geometry-audit.json").Length)"
foreach ($c in $CHK) {
  $mk = 'PASS'; if (-not $c.pass) { $mk = 'FAIL' }
  Write-Host ("[{0}] {1} {2} :: {3}" -f $mk, $c.id, $c.check, $c.detail)
}
Write-Host ("TOTAL {0}/{1} passed; worst bbox error {2}px" -f ($CHK.Count - $failCount), $CHK.Count, [math]::Round($worstBbox, 3))
if ($failCount -gt 0) { exit 1 }
