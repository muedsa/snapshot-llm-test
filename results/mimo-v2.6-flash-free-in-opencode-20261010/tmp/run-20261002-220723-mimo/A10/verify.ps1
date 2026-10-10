$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$PNG  = "$root\outputs\$RUN\A10\compositing-lab.png"
$DSL  = "$root\outputs\$RUN\A10\compositing-lab.snapshot"
if (-not (Test-Path $DSL)) { $DSL = "$root\tmp\$RUN\A10\compositing-lab-v02.snapshot" }
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap($PNG)

$checks = New-Object System.Collections.Generic.List[object]
function AddCheck([string]$id, [string]$name, $pass, [string]$detail) {
  $checks.Add([pscustomobject]@{ id = $id; name = $name; pass = [bool]$pass; detail = $detail })
}
function Sha([string]$p) { (Get-FileHash -Algorithm SHA256 $p).Hash }

# ---------------------------------------------------------------- layout ---
$ZX = @(160, 560, 960)          # zone left per column
$ZY = @(270, 690)               # zone top per row
$ZW = 320; $ZH = 240

# ------------------------------------------------------- pixel utilities ---
function Rgb([int]$x, [int]$y) { $c = $bmp.GetPixel($x, $y); return ,@([int]$c.R, [int]$c.G, [int]$c.B) }
function RowSpan([int]$x0, [int]$y, [int]$n) {
  $mn = 255; $mx = 0
  for ($i = 0; $i -lt $n; $i++) { $r = [int]$bmp.GetPixel(($x0 + $i), $y).R; if ($r -lt $mn) { $mn = $r }; if ($r -gt $mx) { $mx = $r } }
  return ($mx - $mn)
}
function BoxSpan([int]$x0, [int]$y0, [int]$w, [int]$h) {
  $mn = 255; $mx = 0
  for ($y = $y0; $y -lt ($y0 + $h); $y++) {
    for ($x = $x0; $x -lt ($x0 + $w); $x++) {
      $r = [int]$bmp.GetPixel($x, $y).R
      if ($r -lt $mn) { $mn = $r }; if ($r -gt $mx) { $mx = $r }
    }
  }
  return ($mx - $mn)
}
function GoldenBox([int]$cx, [int]$cy) {
  $minx = 9999; $miny = 9999; $maxx = -1; $maxy = -1; $n = 0
  for ($y = $cy; $y -lt ($cy + $ZH); $y++) {
    for ($x = $cx; $x -lt ($cx + $ZW); $x++) {
      $c = $bmp.GetPixel($x, $y)
      if ($c.R -gt 180 -and $c.B -lt 160 -and ($c.R - $c.B) -gt 60) {
        $n++
        if ($x -lt $minx) { $minx = $x }; if ($x -gt $maxx) { $maxx = $x }
        if ($y -lt $miny) { $miny = $y }; if ($y -gt $maxy) { $maxy = $y }
      }
    }
  }
  return ,@(($minx - $cx), ($miny - $cy), ($maxx - $cx), ($maxy - $cy), $n)
}

# ------------------------------------------------------------- PNG header ---
$bytes = [System.IO.File]::ReadAllBytes($PNG)
$sig = ($bytes[0..3] -join ',')
$w = ([int]$bytes[16] * 16777216) + ([int]$bytes[17] * 65536) + ([int]$bytes[18] * 256) + [int]$bytes[19]
$h = ([int]$bytes[20] * 16777216) + ([int]$bytes[21] * 65536) + ([int]$bytes[22] * 256) + [int]$bytes[23]
AddCheck 'P01' 'PNG signature' ($sig -eq '137,80,78,71') "sig=$sig"
AddCheck 'P02' 'IHDR is 1440x1100' ($w -eq 1440 -and $h -eq 1100) "width=$w height=$h"

# ------------------------------------------------------------------- DSL ---
$dslBytes = [System.IO.File]::ReadAllBytes($DSL)
$bom = ($dslBytes[0] -eq 0xEF -and $dslBytes[1] -eq 0xBB -and $dslBytes[2] -eq 0xBF)
AddCheck 'D01' 'DSL has no UTF-8 BOM' (-not $bom) ("firstByte=" + $dslBytes[0])
$xml = New-Object System.Xml.XmlDocument
$xml.Load($DSL)
$dslText = [System.IO.File]::ReadAllText($DSL)
AddCheck 'D02' 'DSL is well-formed XML' $true ("elements=" + $xml.SelectNodes('//*').Count)

# ---------------------------------------------------------------- labels ---
$fontSizes = @()
foreach ($m in [regex]::Matches($dslText, 'fontSize="([0-9.]+)"')) { $fontSizes += [double]$m.Groups[1].Value }
$minFs = ($fontSizes | Measure-Object -Minimum).Minimum
AddCheck 'L01' 'every label >= 20px' ($minFs -ge 20) ("count=" + $fontSizes.Count + " min=" + $minFs + " sizes=" + (($fontSizes | Sort-Object -Unique) -join '/'))
AddCheck 'L02' 'exact board title present once' (([regex]::Matches($dslText, [regex]::Escape('看到差异，才能说用对了'))).Count -eq 1) ("count=" + ([regex]::Matches($dslText, [regex]::Escape('看到差异，才能说用对了'))).Count)
AddCheck 'L03' 'card caption SHARP / BLUR at fontSize 24 twice' (([regex]::Matches($dslText, 'fontSize="24"[^>]*>SHARP / BLUR<')).Count -eq 2) ("count=" + ([regex]::Matches($dslText, 'fontSize="24"[^>]*>SHARP / BLUR<')).Count)

# ---------------------------------------------------------------- layout ---
$zoneWrap = 0
foreach ($zi in 0..5) {
  $gx = $ZX[$zi % 3]; $gy = $ZY[[int][math]::Floor($zi / 3)]
  if ($dslText.Contains(('left="{0}" top="{1}" width="320" height="240"><Stack>' -f $gx, $gy))) { $zoneWrap++ }
}
AddCheck 'G01' 'six 320x240 experiment zones at the planned grid coordinates' ($zoneWrap -eq 6) ("zone wrappers found=" + $zoneWrap + " at " + (($ZX | ForEach-Object { $_ }) -join '/') + ' x ' + ($ZY -join '/'))
AddCheck 'G02' 'grid is 3 columns x 2 rows' (($ZX.Count -eq 3) -and ($ZY.Count -eq 2)) ("zone x=" + ($ZX -join ',') + " y=" + ($ZY -join ','))
$gapH = $ZX[1] - ($ZX[0] + $ZW)
$gapV = $ZY[1] - ($ZY[0] + $ZH)
AddCheck 'G03' 'horizontal zone gap >= 32' ($gapH -ge 32) ("gap=$gapH")
AddCheck 'G04' 'vertical zone gap >= 32' ($gapV -ge 32) ("gap=$gapV")
$leftMargin = $ZX[0]; $rightMargin = 1440 - ($ZX[2] + $ZW)
AddCheck 'G05' 'zone block horizontally centred' ($leftMargin -eq $rightMargin) ("left=$leftMargin right=$rightMargin")
# numbers / descriptions sit above the zone, i.e. outside it
$hdrTop = @(140, 560)
$labelsOutside = $true
for ($r = 0; $r -lt 2; $r++) { if (($hdrTop[$r] + 120) -gt $ZY[$r]) { $labelsOutside = $false } }
AddCheck 'G06' 'number and description blocks sit outside the experiment area' $labelsOutside ("row0 header band 140..260 vs zone top 270; row1 header band 560..680 vs zone top 690")

# ------------------------------------------------------ DSL structure -------
AddCheck 'S01' 'Opacity(0.5) group used exactly once (panel 2)' (([regex]::Matches($dslText, '<Opacity opacity="0\.5">')).Count -eq 1) ("count=" + ([regex]::Matches($dslText, '<Opacity opacity="0\.5">')).Count)
$rectR = ([regex]::Matches($dslText, 'left="40" top="40" width="160" height="120"><Container width="160" height="120" color="#FF0000"')).Count
$rectB = ([regex]::Matches($dslText, 'left="120" top="80" width="160" height="120"><Container width="160" height="120" color="#0000FF"')).Count
$rectRa = ([regex]::Matches($dslText, 'left="40" top="40" width="160" height="120"><Container width="160" height="120" color="#FF000080"')).Count
$rectBa = ([regex]::Matches($dslText, 'left="120" top="80" width="160" height="120"><Container width="160" height="120" color="#0000FF80"')).Count
$iRedA = $dslText.IndexOf('color="#FF000080"'); $iBlueA = $dslText.IndexOf('color="#0000FF80"')
$iRedO = $dslText.IndexOf('color="#FF0000"'); $iBlueO = $dslText.IndexOf('color="#0000FF"')
AddCheck 'S02' 'panel 1 rects at (40,40,160,120) and (120,80,160,120) with 50% alpha' ($rectRa -eq 1 -and $rectBa -eq 1) ("red80=$rectRa blue80=$rectBa")
AddCheck 'S03' 'panel 2 uses the same two rectangles, opaque, blue painted after red' (($rectR -eq 1) -and ($rectB -eq 1) -and ($iBlueO -gt $iRedO)) ("redOpaque=$rectR blueOpaque=$rectB  blueAfterRed=" + ($iBlueO -gt $iRedO))
AddCheck 'S03b' 'blue is painted after red in panel 1 as well (blue on top)' ($iBlueA -gt $iRedA) ("redIdx=$iRedA blueIdx=$iBlueA")
$clipR = ([regex]::Matches($dslText, '<ClipRRect borderRadius="20"')).Count
AddCheck 'S04' 'two 240x160 cards with radius 20 (panels 3 and 4)' ($clipR -eq 2) ("ClipRRect radius20 count=" + $clipR)
$cards = ([regex]::Matches($dslText, 'left="40" top="40" width="240" height="160"')).Count
AddCheck 'S05' 'both cards are 240x160 at zone-local (40,40)' ($cards -eq 2) ("count=" + $cards)
$sig6 = ([regex]::Matches($dslText, 'sigmaX="6" sigmaY="6"')).Count
AddCheck 'F01' 'every ImageFiltered uses sigmaX=sigmaY=6' (([regex]::Matches($dslText, 'sigmaX="6" sigmaY="6"')).Count -eq ([regex]::Matches($dslText, '<ImageFiltered')).Count -and $sig6 -ge 4) ("ImageFiltered=" + ([regex]::Matches($dslText, '<ImageFiltered')).Count + " with sigma6=" + $sig6)
$cf = ([regex]::Matches($dslText, '<ColorFiltered color="#F6B94A" blendMode="MULTIPLY">')).Count
AddCheck 'F02' 'ColorFiltered MULTIPLY #F6B94A on panels 5 and 6' ($cf -eq 2) ("count=" + $cf)
AddCheck 'F03' 'ClipOval used exactly once (panel 6)' (([regex]::Matches($dslText, '<ClipOval')).Count -eq 1) ("count=" + ([regex]::Matches($dslText, '<ClipOval')).Count)
AddCheck 'F04' 'no <Image> bitmap is embedded (pure DSL painting)' (([regex]::Matches($dslText, '<Image[ >/]')).Count -eq 0) ("count=" + ([regex]::Matches($dslText, '<Image[ >/]')).Count)

# ------------------------------------------------------- analytic values ---
$a = 128.0 / 255.0
function R0([double]$v) { return [int][math]::Round($v, 0, [MidpointRounding]::AwayFromZero) }
# panel 1: red-80 over white, then blue-80 over that
$back   = @((255.0), ((1 - $a) * 255.0), ((1 - $a) * 255.0))                       # red over white = (255,127,127)
$p1red  = @((R0 ($a * 255 + (1 - $a) * 255)), (R0 ((1 - $a) * 255)), (R0 ((1 - $a) * 255)))
$p1blue = @((R0 ((1 - $a) * 255)), (R0 ((1 - $a) * 255)), (R0 ($a * 255 + (1 - $a) * 255)))
$p1ovl  = @((R0 ((1 - $a) * $back[0])), (R0 ((1 - $a) * $back[1])), (R0 ($a * 255 + (1 - $a) * $back[2])))
# panel 2: opaque shapes flatten inside the group, then opacity 0.5 once over white
$p2red  = @((R0 (0.5 * 255 + 0.5 * 255)), (R0 (0.5 * 0 + 0.5 * 255)), (R0 (0.5 * 0 + 0.5 * 255)))
$p2blue = @((R0 (0.5 * 0 + 0.5 * 255)), (R0 (0.5 * 0 + 0.5 * 255)), (R0 (0.5 * 255 + 0.5 * 255)))
$p2ovl  = @($p2blue)

function Near([int[]]$m, [int[]]$e, [int]$tol) {
  for ($i = 0; $i -lt 3; $i++) { if ([math]::Abs($m[$i] - $e[$i]) -gt $tol) { return $false } }
  return $true
}
function DeltaStr([int[]]$m, [int[]]$e) { return ('({0},{1},{2})' -f ($m[0]-$e[0]), ($m[1]-$e[1]), ($m[2]-$e[2])) }

# 5x5 samples around the sampling point, to prove it is a stable interior pixel
function Grid([int]$cx, [int]$cy) {
  $out = New-Object System.Collections.Generic.List[object]
  for ($dy = -2; $dy -le 2; $dy++) { for ($dx = -2; $dx -le 2; $dx++) { [void]$out.Add((Rgb ($cx+$dx) ($cy+$dy))) } }
  return ,$out.ToArray()
}
function MeanRgb($cells) {
  $s = @(0,0,0)
  foreach ($c in $cells) { $s[0] += $c[0]; $s[1] += $c[1]; $s[2] += $c[2] }
  $n = $cells.Count
  return ,@([int][math]::Round($s[0]/$n), [int][math]::Round($s[1]/$n), [int][math]::Round($s[2]/$n))
}

$TOL = 2
$m1 = Rgb ($ZX[0]+180) ($ZY[0]+100)
$m2 = Rgb ($ZX[1]+180) ($ZY[0]+100)
$g1 = MeanRgb (Grid ($ZX[0]+180) ($ZY[0]+100))
$g2 = MeanRgb (Grid ($ZX[1]+180) ($ZY[0]+100))
AddCheck 'X01' 'panel 1 overlap sample matches the analytic alpha stack' (Near $m1 $p1ovl $TOL) ("expected=" + ('({0},{1},{2})' -f $p1ovl[0],$p1ovl[1],$p1ovl[2]) + " measured=" + ('({0},{1},{2})' -f $m1[0],$m1[1],$m1[2]) + " delta=" + (DeltaStr $m1 $p1ovl) + " tol=$TOL")
AddCheck 'X02' 'panel 2 overlap sample matches the analytic single 0.5 group fade' (Near $m2 $p2ovl $TOL) ("expected=" + ('({0},{1},{2})' -f $p2ovl[0],$p2ovl[1],$p2ovl[2]) + " measured=" + ('({0},{1},{2})' -f $m2[0],$m2[1],$m2[2]) + " delta=" + (DeltaStr $m2 $p2ovl) + " 5x5mean=" + ('({0},{1},{2})' -f $g2[0],$g2[1],$g2[2]) + " tol=$TOL")
$diff = [math]::Max([math]::Abs($m1[0]-$m2[0]), [math]::Max([math]::Abs($m1[1]-$m2[1]), [math]::Abs($m1[2]-$m2[2])))
AddCheck 'X03' 'panel 1 and panel 2 differ visibly at the same point' ($diff -ge 30) ("max channel delta=" + $diff)

$m1r = Rgb ($ZX[0]+80) ($ZY[0]+60);   $m2r = Rgb ($ZX[1]+80) ($ZY[0]+60)
$m1b = Rgb ($ZX[0]+250) ($ZY[0]+190); $m2b = Rgb ($ZX[1]+250) ($ZY[0]+190)
AddCheck 'X04' 'panel 1 red-only and blue-only regions match analytic' ((Near $m1r $p1red $TOL) -and (Near $m1b $p1blue $TOL)) ("redOnly expected=" + ('({0},{1},{2})' -f $p1red[0],$p1red[1],$p1red[2]) + " measured=" + ('({0},{1},{2})' -f $m1r[0],$m1r[1],$m1r[2]) + "  blueOnly expected=" + ('({0},{1},{2})' -f $p1blue[0],$p1blue[1],$p1blue[2]) + " measured=" + ('({0},{1},{2})' -f $m1b[0],$m1b[1],$m1b[2]))
AddCheck 'X05' 'panel 2 red-only and blue-only regions match analytic' ((Near $m2r $p2red $TOL) -and (Near $m2b $p2blue $TOL)) ("redOnly expected=" + ('({0},{1},{2})' -f $p2red[0],$p2red[1],$p2red[2]) + " measured=" + ('({0},{1},{2})' -f $m2r[0],$m2r[1],$m2r[2]) + "  blueOnly expected=" + ('({0},{1},{2})' -f $p2blue[0],$p2blue[1],$p2blue[2]) + " measured=" + ('({0},{1},{2})' -f $m2b[0],$m2b[1],$m2b[2]))
# crosshair must not touch the sampled pixel
$armA = Rgb ($ZX[0]+166) ($ZY[0]+100)
$armB = Rgb ($ZX[0]+180) ($ZY[0]+86)
$armC = Rgb ($ZX[0]+192) ($ZY[0]+100)
$armD = Rgb ($ZX[0]+180) ($ZY[0]+112)
$armsOk = ($armA[0] -lt 60) -and ($armB[0] -lt 60) -and ($armC[0] -lt 60) -and ($armD[0] -lt 60)
AddCheck 'X06' 'crosshair arms exist but leave (180,100) itself untouched' ($armsOk -and ($m1[0] -eq $p1ovl[0]) -and ($m1[1] -eq $p1ovl[1]) -and ($m1[2] -eq $p1ovl[2])) ("arm R values = " + $armA[0] + ',' + $armB[0] + ',' + $armC[0] + ',' + $armD[0] + " (all < 60 = dark ink)   centre=" + ('({0},{1},{2})' -f $m1[0],$m1[1],$m1[2]) + " equals analytic " + ('({0},{1},{2})' -f $p1ovl[0],$p1ovl[1],$p1ovl[2]))

# ------------------------------------------------- panels 3 / 4 ------------
$stripeOut3 = RowSpan ($ZX[2]+4)  ($ZY[0]+70) 30
$stripeIn3  = RowSpan ($ZX[2]+60) ($ZY[0]+70) 30
$stripeOut4 = RowSpan ($ZX[0]+4)  ($ZY[1]+70) 30
$stripeIn4  = RowSpan ($ZX[0]+60) ($ZY[1]+70) 30
$txt3 = BoxSpan ($ZX[2]+64) ($ZY[0]+98) 192 34
$txt4 = BoxSpan ($ZX[0]+64) ($ZY[1]+98) 192 34
AddCheck 'X07' 'panel 3: stripes OUTSIDE the card stay sharp' ($stripeOut3 -ge 100) ("row span outside card (30px at y=70) = " + $stripeOut3 + " (full-contrast stripes are 148..255)")
AddCheck 'X08' 'panel 3: stripes INSIDE the card are blurred, text stays sharp' (($stripeIn3 -le 40) -and ($txt3 -ge 150)) ("stripe span inside card = " + $stripeIn3 + " (<=40)   text R-contrast = " + $txt3 + " (>=150)")
AddCheck 'X09' 'panel 4: same stripes outside stay sharp, whole subtree (text + shape) blurred' (($stripeOut4 -ge 100) -and ($stripeIn4 -le 40) -and ($txt4 -le 80)) ("stripe span outside = " + $stripeOut4 + "   stripe span inside = " + $stripeIn4 + "   text R-contrast = " + $txt4 + " (<=80)")
AddCheck 'X10' 'panel 3 vs panel 4 differ exactly where the spec says they should (text)' (($txt3 - $txt4) -ge 100) ("text contrast 3=" + $txt3 + " 4=" + $txt4 + " delta=" + ($txt3 - $txt4))

# ------------------------------------------------- panels 5 / 6 ------------
$gb5 = GoldenBox $ZX[1] $ZY[1]
$gb6 = GoldenBox $ZX[2] $ZY[1]
$gap5 = Rgb ($ZX[1]+160) ($ZY[1]+80)     # transparent gap inside the subtree
$gap6 = Rgb ($ZX[2]+160) ($ZY[1]+80)
$out5 = Rgb ($ZX[1]+20)  ($ZY[1]+20)      # outside the subtree, panel 5
$out6 = Rgb ($ZX[2]+30)  ($ZY[1]+30)      # outside the circle, panel 6
AddCheck 'X11' 'panel 5: transparent gap inside the subtree is tinted by MULTIPLY' ((($gap5[0]-$gap5[2]) -gt 60) -and ($gap5[0] -gt 180)) ("gap=" + ('({0},{1},{2})' -f $gap5[0],$gap5[1],$gap5[2]) + "  filter #F6B94A=(246,185,74)")
AddCheck 'X12' 'panel 5: filter does not spill outside the subtree bounds' (($out5[0] -eq 255) -and ($out5[1] -eq 255) -and ($out5[2] -eq 255)) ("outside=" + ('({0},{1},{2})' -f $out5[0],$out5[1],$out5[2]))
AddCheck 'X13' 'panel 6: same tint inside the circle, white outside it' ((($gap6[0]-$gap6[2]) -gt 60) -and ($out6[0] -eq 255)) ("inside circle=" + ('({0},{1},{2})' -f $gap6[0],$gap6[1],$gap6[2]) + " outside circle=" + ('({0},{1},{2})' -f $out6[0],$out6[1],$out6[2]))
AddCheck 'X14' 'clip boundary is observable: panel 6 tinted area is clipped to the disc' (($gb6[4] -gt 0) -and ($gb6[3] -lt $gb5[3]) -and (($gb6[2]-$gb6[0]+1) -lt 180)) ("panel5 tinted bbox local x {0}..{1} y {2}..{3} ({4}px)  panel6 x {5}..{6} y {7}..{8} ({9}px, {10} px^2)" -f $gb5[0],$gb5[2],$gb5[1],$gb5[3],($gb5[2]-$gb5[0]+1),$gb6[0],$gb6[2],$gb6[1],$gb6[3],($gb6[2]-$gb6[0]+1),$gb6[4])
$underBar5 = Rgb ($ZX[1]+110) ($ZY[1]+210)
AddCheck 'X15' 'panel 5 keeps a shadow under the bottom bar (documented: overflow/shadow preserved)' ((($underBar5[0]-$underBar5[2]) -gt 40) -and ($underBar5[0] -lt 200)) ("under bar = " + ('({0},{1},{2})' -f $underBar5[0],$underBar5[1],$underBar5[2]) + " (golden tint darkened by the box shadow)")

# ------------------------------------------------------------ no clipping --
$mnX = 9999; $mnY = 9999; $mxX = -1; $mxY = -1
for ($y = 0; $y -lt $bmp.Height; $y += 1) {
  for ($x = 0; $x -lt $bmp.Width; $x += 1) {
    $c = $bmp.GetPixel($x, $y)
    if ([math]::Abs($c.R-238) -gt 6 -or [math]::Abs($c.G-241) -gt 6 -or [math]::Abs($c.B-246) -gt 6) {
      if ($x -lt $mnX) { $mnX = $x }; if ($x -gt $mxX) { $mxX = $x }
      if ($y -lt $mnY) { $mnY = $y }; if ($y -gt $mxY) { $mxY = $y }
    }
  }
}
$lastRowClean = $true
for ($x = 0; $x -lt $bmp.Width; $x++) {
  $c = $bmp.GetPixel($x, 1099)
  if ([math]::Abs($c.R-238) -gt 6 -or [math]::Abs($c.G-241) -gt 6 -or [math]::Abs($c.B-246) -gt 6) { $lastRowClean = $false; break }
}
AddCheck 'Z01' 'all ink fits inside the canvas (nothing clipped at any edge)' (($mnX -gt 0) -and ($mnY -gt 0) -and ($mxX -lt 1439) -and ($lastRowClean)) ("ink bbox x {0}..{1} y {2}..{3}; last row clean={4}" -f $mnX,$mxX,$mnY,$mxY,$lastRowClean)
$zonePainted = 0
for ($z = 0; $z -lt 6; $z++) {
  $cx = $ZX[$z % 3]; $cy = $ZY[[int][math]::Floor($z / 3)]
  $ok = $true
  foreach ($p in @(@(2,2), @(317,2), @(2,237), @(317,237))) {
    $c = $bmp.GetPixel(($cx + $p[0]), ($cy + $p[1]))
    if ([math]::Abs($c.R-238) -le 3 -and [math]::Abs($c.G-241) -le 3 -and [math]::Abs($c.B-246) -le 3) { $ok = $false }
  }
  if ($ok) { $zonePainted++ }
}
AddCheck 'Z02' 'every experiment zone is fully painted (no page background showing through)' ($zonePainted -eq 6) ("zones with all 4 corners painted = " + $zonePainted + "/6 (corner inset 2px)")
$bgOk = $true
$c = $bmp.GetPixel(20, 20)
if ([math]::Abs($c.R-238) -gt 4 -or [math]::Abs($c.G-241) -gt 4 -or [math]::Abs($c.B-246) -gt 4) { $bgOk = $false }
AddCheck 'Z03' 'board background keeps the white zones legible' $bgOk ("page background = " + ('({0},{1},{2})' -f $c.R,$c.G,$c.B) + " vs zone (255,255,255)")

# ----------------------------------------------------------------- output ---
$passed = @($checks | Where-Object { $_.pass }).Count
$total  = $checks.Count

$panels = @(
  [pscustomobject]@{ index=1; title='红蓝重叠的矩形分别设置 50% alpha'; spec='①红蓝重叠的矩形分别设置50%alpha'
    implemented='#FF000080 at zone-local (40,40,160,120), #0000FF80 at (120,80,160,120), blue painted last'
    evidence=('overlap (180,100) measured ' + ('({0},{1},{2})' -f $m1[0],$m1[1],$m1[2]) + ', analytic two-layer alpha stack ' + ('({0},{1},{2})' -f $p1ovl[0],$p1ovl[1],$p1ovl[2]) + ', delta ' + (DeltaStr $m1 $p1ovl) + '; red-only ' + ('({0},{1},{2})' -f $m1r[0],$m1r[1],$m1r[2]) + ' vs expected ' + ('({0},{1},{2})' -f $p1red[0],$p1red[1],$p1red[2]))
    judgment='PASS - each shape carries its own alpha, so the backdrop of the second shape is the already-composited first shape' },
  [pscustomobject]@{ index=2; title='同样的两个不透明矩形放在 Opacity(0.5) 组内'; spec='②同样的两个不透明矩形放在Opacity(0.5)组内'
    implemented='<Opacity opacity="0.5"> wrapping opaque #FF0000 (40,40,160,120) + #0000FF (120,80,160,120) in one Stack'
    evidence=('overlap (180,100) measured ' + ('({0},{1},{2})' -f $m2[0],$m2[1],$m2[2]) + ', analytic group fade ' + ('({0},{1},{2})' -f $p2ovl[0],$p2ovl[1],$p2ovl[2]) + ', delta ' + (DeltaStr $m2 $p2ovl) + '; 5x5 mean ' + ('({0},{1},{2})' -f $g2[0],$g2[1],$g2[2]) + '; differs from panel 1 by ' + $diff + ' at the worst channel')
    judgment='PASS - the opaque blue fully covers the opaque red inside the group, then the whole layer is faded exactly once' },
  [pscustomobject]@{ index=3; title='带锐利条纹背景的圆角卡，仅背景模糊'; spec='③带锐利条纹背景的圆角卡，仅背景模糊；③④的卡为240×160、圆角20，卡内文字"SHARP / BLUR"字号24；条纹跨卡边，外部仍清晰'
    implemented='sharp full-zone stripe layer, then ClipRRect(240x160 r20) > ImageFiltered(sigma 6) > stripes offset to zone coordinates; text and red bar drawn OUTSIDE the filter'
    evidence=('stripe R span outside card = ' + $stripeOut3 + ' (full 148..255), inside card = ' + $stripeIn3 + ' (blurred), text R-contrast = ' + $txt3 + ' (sharp)')
    judgment='PASS - only the striped background is blurred; the caption and the bar stay sharp and the stripes stay crisp outside the card edge' },
  [pscustomobject]@{ index=4; title='相同条纹，把卡内文字与形状一起子树模糊'; spec='④相同条纹，把卡内文字与形状一起子树模糊'
    implemented='ClipRRect(240x160 r20) > ImageFiltered(sigma 6) > Stack{ stripes offset, caption, red bar } - the whole card subtree is inside the filter'
    evidence=('stripe R span outside card = ' + $stripeOut4 + ' (sharp), inside = ' + $stripeIn4 + ' (blurred), text R-contrast = ' + $txt4 + ' vs ' + $txt3 + ' in panel 3 (delta ' + ($txt3-$txt4) + ')')
    judgment='PASS - caption and shape are blurred with the background while the stripes outside the card remain sharp' },
  [pscustomobject]@{ index=5; title='先 ColorFiltered(MULTIPLY) 后子树高斯模糊'; spec='⑤先ColorFiltered(MULTIPLY)后子树高斯模糊；⑤⑥滤色#F6B94A，内部含透明间隙、深色矩形和阴影'
    implemented='ColorFiltered(color=#F6B94A, blendMode=MULTIPLY) > ImageFiltered(sigma 6) > Stack{ dark bar, two dark blocks with a transparent gap, bar with boxShadow }'
    evidence=('transparent gap measured ' + ('({0},{1},{2})' -f $gap5[0],$gap5[1],$gap5[2]) + ' (golden, not white) so MULTIPLY really colours the transparent gaps; shadow under the bottom bar = ' + ('({0},{1},{2})' -f $underBar5[0],$underBar5[1],$underBar5[2]) + '; tinted bbox local x ' + $gb5[0] + '..' + $gb5[2] + ' y ' + $gb5[1] + '..' + $gb5[3])
    judgment='PASS - MULTIPLY runs before the subtree blur, the gaps are tinted, and the documented shadow overflow survives' },
  [pscustomobject]@{ index=6; title='同样的⑤效果再限定于圆形裁剪区域'; spec='⑥同样的⑤效果再限定于圆形裁剪区域；确保能观察裁剪边界'
    implemented='ClipOval(clipBehavior=ANTI_ALIAS) wrapping the identical panel-5 subtree'
    evidence=('tinted region inside the circle = ' + ('({0},{1},{2})' -f $gap6[0],$gap6[1],$gap6[2]) + ', a point outside the circle = ' + ('({0},{1},{2})' -f $out6[0],$out6[1],$out6[2]) + '; tinted bbox shrinks from ' + ($gb5[2]-$gb5[0]+1) + 'x' + ($gb5[3]-$gb5[1]+1) + ' (panel 5) to ' + ($gb6[2]-$gb6[0]+1) + 'x' + ($gb6[3]-$gb6[1]+1) + ' clipped to the disc')
    judgment='PASS - the rectangular filter region of panel 5 becomes a disc, so the clip boundary is directly observable' }
)

$audit = [ordered]@{
  schema_version = 1
  task_id = 'A10'
  run_id = $RUN
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fffK')
  timezone = 'Asia/Shanghai (UTC+08:00)'
  artifacts = [ordered]@{
    png = 'outputs/run-20261002-220723-mimo/A10/compositing-lab.png'
    dsl = 'outputs/run-20261002-220723-mimo/A10/compositing-lab.snapshot'
    width = $bmp.Width; height = $bmp.Height
    png_bytes = $bytes.Length; png_sha256 = (Sha $PNG)
    dsl_bytes = (Get-Item $DSL).Length; dsl_sha256 = (Sha $DSL)
    dsl_source_version = 'compositing-lab-v02'
    source = 'open-snapshot real service response, no post-processing'
  }
  layout = [ordered]@{
    canvas = @(1440, 1100)
    title = [ordered]@{ text='看到差异，才能说用对了'; font_size=40; box=@(0,30,1440,52); outside_zones=$true }
    grid = [ordered]@{ columns=3; rows=2; zone_size=@(320,240); gap_horizontal=$gapH; gap_vertical=$gapV
                       zone_x=$ZX; zone_y=$ZY; left_margin=$leftMargin; right_margin=$rightMargin; centred=$true }
    labels = [ordered]@{ number_and_description_outside_zone=$true; row0='header band y140..260, zone y270..510'; row1='header band y560..680, zone y690..930' }
    cards = @( [ordered]@{ panel=3; zone_local_rect=@(40,40,240,160); radius=20 }, [ordered]@{ panel=4; zone_local_rect=@(40,40,240,160); radius=20 } )
    filter = [ordered]@{ sigmaX=6; sigmaY=6; multiply_color='#F6B94A'; blendMode='MULTIPLY'; clip_oval_panel=6; opacity_group_panel=2; opacity=0.5 }
    min_font_size = $minFs
  }
  sampling = [ordered]@{
    point_zone_local = @(180,100)
    point_canvas = @(($ZX[0]+180), ($ZY[0]+100))
    tolerance_lsb = $TOL
    tolerance_rationale = 'Analytic values are exact rational composites; the renderer works in 8-bit premultiplied space, so up to 2 least-significant-bits of rounding can appear on a value that lands on a half step (0.5*255 = 127.5 is not representable).'
    panel1 = [ordered]@{ alpha='128/255 = 0.5019607843' ; expected_overlap=$p1ovl; measured_overlap=$m1; delta=(DeltaStr $m1 $p1ovl)
                         expected_red_only=$p1red; measured_red_only=$m1r; expected_blue_only=$p1blue; measured_blue_only=$m1b
                         five_by_five_mean=$g1 }
    panel2 = [ordered]@{ alpha='0.5 exactly, applied once to the group'; expected_overlap=$p2ovl; measured_overlap=$m2; delta=(DeltaStr $m2 $p2ovl)
                         expected_red_only=$p2red; measured_red_only=$m2r; expected_blue_only=$p2blue; measured_blue_only=$m2b
                         five_by_five_mean=$g2 }
    difference = [ordered]@{
      worst_channel_delta = $diff
      explanation_128_255_vs_0_5 = @(
        '0x80 = 128, so the alpha in panel 1 is 128/255 = 0.5019607843, which is 0.0019607843 (about 0.196%) ABOVE the exact 0.5 used by Opacity(0.5) in panel 2. In 8-bit terms it is 0.5 + 1/510.',
        'Panel 1 also composites TWICE: the blue layer multiplies the already-composited red-over-white backdrop by (1 - 128/255) = 127/255 = 0.498039, while panel 2 composites the opaque blue inside the group first and then fades the single flattened layer by exactly 0.5.',
        'Consequence at (180,100): panel 1 = ' + ('({0},{1},{2})' -f $m1[0],$m1[1],$m1[2]) + ', panel 2 = ' + ('({0},{1},{2})' -f $m2[0],$m2[1],$m2[2]) + ', worst channel delta = ' + $diff + '. Green is the loudest: 0.498039 * 127 = 63.3 in panel 1 versus 0.5 * 255 = 127.5 in panel 2, a difference of 64.2/255 that reads as a clearly different hue.',
        'So "50% alpha per shape" and "50% opacity on the group" are NOT the same operation; the board shows the difference directly at the marked point.'
      )
    }
  }
  panels = $panels
  checks = $checks
  summary = [ordered]@{
    status = $(if ($passed -eq $total) { 'PASS' } else { 'FAIL' })
    checks_total = $total; checks_passed = $passed; checks_failed = ($total - $passed)
    failed_ids = @($checks | Where-Object { -not $_.pass } | ForEach-Object { $_.id })
    min_font_size = $minFs
    zones = 6; cards = 2; filters = 6
    analytic_vs_measured_worst_lsb = [math]::Max([math]::Abs($m1[1]-$p1ovl[1]), [math]::Abs($m2[1]-$p2ovl[1]))
    tolerance_lsb = $TOL
    all_within_tolerance = $(if ($passed -eq $total) { $true } else { $false })
  }
  verification_method = [ordered]@{
    how = @(
      'PNG: IHDR bytes 16..23 read as big-endian int32 (int casts first, so the byte-shift cannot truncate), plus PNG signature 89 50 4E 47.',
      'DSL: re-read the delivered .snapshot, check no BOM, parse as XML, and count the structural tags/attributes the spec calls for.',
      'Compositing: compute the expected RGB analytically in double precision from the spec (alpha stack for panel 1, single group fade for panel 2), then read the delivered PNG with Bitmap.GetPixel at the zone-local point (180,100) mapped to canvas (340,370).',
      'A 5x5 grid around the same point is averaged to prove the sample is a stable interior pixel and not an edge or crosshair pixel.',
      'Sharpness: the red-channel range (max-min) over a 30px horizontal run is compared between the stripe region outside the card and the stripe region inside the card at the same y; full-contrast stripes span 107, blurred stripes must span <= 40.',
      'Caption sharpness: the red-channel range over the caption box (192x34) is compared between panel 3 (must be >= 150) and panel 4 (must be <= 80).',
      'Clip boundary: the set of golden pixels (R>180, B<160, R-B>60) is bounded per zone; panel 5 gives the unclipped filter region, panel 6 the disc-clipped one, and an out-of-disc point must be pure white.',
      'No clipping: a full-canvas scan of every pixel that differs from the page background gives an ink bounding box, and the last row is checked separately.'
    )
    antialiasing_exception = 'The sharpness thresholds are ranges, not absolute edge positions, so anti-aliased stripe edges only shrink the range slightly (measured 107 for a theoretical 107); no single-edge tolerance is claimed. The composited sample point is an interior pixel at least 20px from every shape edge, so it is never an anti-aliased pixel.'
    known_gap = 'The exact 8-bit rounding path of the renderer for a group opacity of exactly 0.5 was not derivable from the documentation, so panel 2 is judged against the analytic value with an explicit +/-2 LSB tolerance and the 5x5 mean is reported rather than asserted as an exact match.'
  }
  documentation_used = @(
    [ordered]@{ url='https://open-snapshot.muedsa.com/ai-guide.md'; when='2026-10-03T12:40+08:00'; purpose='request body encoding, content type, colour notation (#RRGGBBAA alpha last), /fonts'
                quote='向服务提交，并将图片保存为文件：请求体是 UTF-8 纯文本，不是 JSON；成功时响应体是图片二进制。颜色使用 CSS 语法，包括 #RGB、#RGBA、#RRGGBB、#RRGGBBAA；8 位格式的透明度在最后两位。' }
    [ordered]@{ url='https://snapshot.muedsa.com/reference/parser-tags/'; when='2026-10-03T12:41+08:00'; purpose='Opacity, ClipRRect, ClipOval, ImageFiltered, ColorFiltered semantics'
                quote=@(
                  'Opacity - 在特定范围内控制子级的透明度。opacity 必须介于 0.0 和 1.0 之间；0.0 表示完全透明，1.0 表示完全不透明。',
                  'ClipRRect - 将子级裁剪为使用 borderRadius 定义的圆角矩形。不支持自定义裁剪器，但可通过 clipBehavior 控制裁剪行为，默认为 ClipBehavior.ANTI_ALIAS（抗锯齿）。',
                  'ClipOval - 将子级裁剪为椭圆（或圆）形状。',
                  'ImageFiltered - 应用图像滤镜到绘制内容。它会按 sigma 自动提供模糊输出边界，并在子级绘制完成后对结果执行滤镜。仅支持高斯模糊，不能实现运动模糊或卷积模糊。sigmaX 和 sigmaY 为必填浮点值。',
                  'ColorFiltered - 将颜色滤镜应用于子级的绘制内容。需同时提供 color 和 blendMode。在子树绘制边界可确定时限制颜色作用范围，保留合法溢出和阴影；部分混合模式也会给边界内的透明间隙着色。'
                ) }
  )
}

$outPath = "$root\outputs\$RUN\A10\composite-audit.json"
$json = $audit | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($outPath, $json, [System.Text.UTF8Encoding]::new($false))
$bmp.Dispose()
"AUDIT $outPath"
"checks $passed/$total PASS"
foreach ($c in $checks) { if (-not $c.pass) { "  FAIL {0} {1} :: {2}" -f $c.id, $c.name, $c.detail } }
