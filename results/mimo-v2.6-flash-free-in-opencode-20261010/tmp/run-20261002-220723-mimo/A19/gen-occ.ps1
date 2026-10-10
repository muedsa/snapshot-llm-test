param(
  [Parameter(Mandatory=$true)][string]$OutA,
  [Parameter(Mandatory=$true)][string]$OutB,
  [Parameter(Mandatory=$true)][string]$OutGeom,
  [switch]$Quiet
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)

# ================================================================================
# 800x800 occlusion scene.  Both variants are emitted by this one script, so the
# shared part is byte-identical by construction.
#
# Draw order is the whole trick:
#   background -> title
#             -> HIDDEN LAYER   (differs between A and B)
#             -> OPAQUE PANEL   (identical)  <- every pixel that may differ lives under it
#             -> VISIBLE LAYER  (identical)
#             -> panel text / bar label / caption (identical)
#
# The panel covers x in [300,700], y in [170,650].  Everything whose pixels may
# differ lies strictly inside that box, so the two PNGs are pixel-identical while
# the two DSLs describe different hidden content.
#
# Two distinct occlusion mechanisms make the case complete:
#   (1) PARTIAL - a blue bar whose left end sticks out of the panel.  The visible
#       run x 200..300 is the same in both; the tail under the panel ends at
#       x=560 in A and x=430 in B.
#   (2) TOTAL   - objects lying entirely under the panel; A hides 3 objects,
#       B hides 4, with different shapes and colours.
#
# Nothing dashed, ghosted, shadowed or labelled is drawn for hidden content.
# ================================================================================

$W = 800; $H = 800
$BG      = '#F8FAFC'
$PANEL   = '#1E293B'
$PANELBD = '#0F172A'
$TXT     = '#0F172A'
$TXT2    = '#475569'
$IDCOL   = '#475569'
$PANTXT  = '#F8FAFC'
$PANSUB  = '#CBD5E1'
$FONT    = 'Noto Sans CJK SC'
$FONTID  = 'Noto Sans Mono CJK SC'

$BLUE = '#3B82F6'; $ORANGE = '#F59E0B'; $GREEN = '#22C55E'; $PURPLE = '#A855F7'

$PX0 = 300; $PY0 = 170; $PW = 400; $PH = 480   # the opaque panel

function F([double]$v) {
  if ($v -eq [Math]::Floor($v)) { return [string][int]$v }
  return $v.ToString([cultureinfo]::InvariantCulture)
}

function AddRect($list, [double]$cx, [double]$cy, [double]$w, [double]$h, [string]$hex, [double]$rad) {
  $list.Add('      <Positioned left="' + (F ($cx - $w/2)) + '" top="' + (F ($cy - $h/2)) + '" width="' + (F $w) + '" height="' + (F $h) + '">')
  $list.Add('        <Container width="' + (F $w) + '" height="' + (F $h) + '" color="' + $hex + '" borderRadius="' + (F $rad) + '"/>')
  $list.Add('      </Positioned>')
}
function AddRing($list, [double]$cx, [double]$cy, [double]$outer, [string]$hex, [string]$bg) {
  $inner = $outer / 2
  AddRect $list $cx $cy $outer $outer $hex ($outer / 2)
  AddRect $list $cx $cy $inner $inner $bg   ($inner / 2)
}
function AddLabel($list, [double]$x, [double]$y, [int]$w, [int]$h, [int]$fs, [string]$col, [string]$text, [string]$align, [string]$fam, [string]$bold) {
  $list.Add('      <Positioned left="' + (F $x) + '" top="' + (F $y) + '" width="' + $w + '" height="' + $h + '">')
  $b = ''
  if ($bold -ne '') { $b = ' fontStyle="BOLD"' }
  $list.Add('        <Text fontSize="' + $fs + '" fontFamily="' + $fam + '"' + $b + ' textAlign="' + $align + '" color="' + $col + '">' + $text + '</Text>')
  $list.Add('      </Positioned>')
}

# ---------------------------------------------------------- shared visible part --
$vis = New-Object System.Collections.Generic.List[string]
AddRect $vis 110 165 72 72 $BLUE    36
AddRect $vis 200 300 64 64 $ORANGE  0
AddRing $vis 110 470 80     $GREEN  $BG
AddRect $vis 215 590 64 64 $PURPLE  16
AddRect $vis 745 250 60 60 $GREEN   30
AddRect $vis 420 710 56 56 $ORANGE  14
AddLabel $vis 74  205 64 22 14 $IDCOL 'V01' 'START' $FONTID ''
AddLabel $vis 168 336 64 22 14 $IDCOL 'V02' 'START' $FONTID ''
AddLabel $vis 70  514 64 22 14 $IDCOL 'V03' 'START' $FONTID ''
AddLabel $vis 183 630 64 22 14 $IDCOL 'V04' 'START' $FONTID ''
AddLabel $vis 715 284 64 22 14 $IDCOL 'V05' 'START' $FONTID ''
AddLabel $vis 392 742 64 22 14 $IDCOL 'V06' 'START' $FONTID ''

# ------------------------------------------------------------------ hidden A/B --
# BAR: identical from x=200 to the panel edge x=300; only the tail differs.
$BAR_X = 200; $BAR_Y = 400; $BAR_H = 56
$hiddenA = New-Object System.Collections.Generic.List[string]
AddRect $hiddenA (($BAR_X + 560)/2) ($BAR_Y + $BAR_H/2) 360 $BAR_H $BLUE 8
AddRect $hiddenA 500 300 140 140 $GREEN  70
AddRect $hiddenA 560 560 90  90  $PURPLE 0

$hiddenB = New-Object System.Collections.Generic.List[string]
AddRect $hiddenB (($BAR_X + 430)/2) ($BAR_Y + $BAR_H/2) 230 $BAR_H $BLUE 8
AddRing $hiddenB 500 300 160 $ORANGE $BG
AddRect $hiddenB 560 560 90 90 $BLUE 45
AddRect $hiddenB 420 540 70 70 $GREEN 0

# ------------------------------------------------------------------- the panel --
$panelList = New-Object System.Collections.Generic.List[string]
AddRect $panelList ($PX0 + $PW/2) ($PY0 + $PH/2) $PW $PH $PANELBD 0            # outer frame
AddRect $panelList ($PX0 + $PW/2) ($PY0 + $PH/2) ($PW - 6) ($PH - 6) $PANEL 0    # solid face

# ================================================================== builder ======
function Build([System.Collections.Generic.List[string]]$hidden) {
  $L = New-Object System.Collections.Generic.List[string]
  $L.Add('<Snapshot type="png" background="' + $BG + '">')
  $L.Add('  <Container width="' + $W + '" height="' + $H + '" color="' + $BG + '">')
  $L.Add('    <Stack>')
  $L.Add('      <!--TITLE-->')
  AddLabel $L 40 30 720 44 26 $TXT '遮挡场景 · 仅显示可见部分' 'CENTER' $FONT 'BOLD'
  $L.Add('      <!--HIDDEN-DIFFERS-->')
  $L.AddRange($hidden)
  $L.Add('      <!--PANEL-OPAQUE-->')
  $L.AddRange($panelList)
  $L.Add('      <!--VISIBLE-SAME-->')
  $L.AddRange($vis)
  $L.Add('      <!--PANEL-TEXT-->')
  AddLabel $L ($PX0 + 10) 214 ($PW - 20) 40 24 $PANTXT '遮挡面板（不透明前景）' 'CENTER' $FONT 'BOLD'
  AddLabel $L ($PX0 + 16) 264 ($PW - 32) 28 17 $PANSUB '其后内容对观众完全不可见' 'CENTER' $FONT ''
  AddLabel $L ($PX0 + 16) 298 ($PW - 32) 28 17 $PANSUB '未以虚线、轮廓或阴影泄漏' 'CENTER' $FONT ''
  $L.Add('      <!--BAR-LABEL-->')
  AddLabel $L 200 462 100 22 15 $TXT2 '可见部分' 'CENTER' $FONT ''
  $L.Add('      <!--CAPTION-->')
  AddLabel $L 40 772 720 26 16 $TXT2 '两份 DSL 的隐藏内容不同，可见像素完全一致（见 equivalence.json）' 'START' $FONT ''
  $L.Add('    </Stack>')
  $L.Add('  </Container>')
  $L.Add('</Snapshot>')
  return ,$L.ToArray()
}

[IO.File]::WriteAllText($OutA, (((Build $hiddenA) -join "`r`n") + "`r`n"), $utf8)
[IO.File]::WriteAllText($OutB, (((Build $hiddenB) -join "`r`n") + "`r`n"), $utf8)

# -------------------------------------------------------------------- geometry --
$geom = [ordered]@{
  schema       = 'snapshot-suite/scene-data/v1'
  task         = 'A19'
  kind         = 'occlusion-scene'
  canvas       = [pscustomobject]@{ width = $W; height = $H }
  origin       = 'top-left (0,0); x grows right, y grows down; unit = pixel'
  occluder     = [pscustomobject]@{ x0 = $PX0; y0 = $PY0; x1 = $PX0 + $PW; y1 = $PY0 + $PH; width = $PW; height = $PH; color = $PANEL; frame_color = $PANELBD; opaque = $true }
  occluded_region = 'x in [300,700], y in [170,650]'
  draw_order   = 'background -> title -> HIDDEN LAYER (differs) -> opaque panel -> VISIBLE LAYER (same) -> panel text -> bar label -> caption'
  visible_objects = @(
    [pscustomobject]@{ id = 'V01'; kind = 'circle';         cx = 110; cy = 165; side = 72; color = $BLUE;   x0 = 74;  y0 = 129; x1 = 146; y1 = 201 },
    [pscustomobject]@{ id = 'V02'; kind = 'square';         cx = 200; cy = 300; side = 64; color = $ORANGE; x0 = 168; y0 = 268; x1 = 232; y1 = 332 },
    [pscustomobject]@{ id = 'V03'; kind = 'ring';           cx = 110; cy = 470; side = 80; inner = 40; color = $GREEN; x0 = 70; y0 = 430; x1 = 150; y1 = 510 },
    [pscustomobject]@{ id = 'V04'; kind = 'rounded-square'; cx = 215; cy = 590; side = 64; color = $PURPLE; x0 = 183; y0 = 558; x1 = 247; y1 = 622 },
    [pscustomobject]@{ id = 'V05'; kind = 'circle';         cx = 745; cy = 250; side = 60; color = $GREEN;  x0 = 715; y0 = 220; x1 = 775; y1 = 280 },
    [pscustomobject]@{ id = 'V06'; kind = 'rounded-square'; cx = 420; cy = 710; side = 56; color = $ORANGE; x0 = 392; y0 = 682; x1 = 448; y1 = 738 }
  )
  hidden_A = @(
    [pscustomobject]@{ id = 'H-bar'; mechanism = 'partial'; kind = 'bar';    x0 = 200; y0 = 400; x1 = 560; y1 = 456; color = $BLUE;   note = 'x 200..300 visible and identical in both; x 300..560 hidden' },
    [pscustomobject]@{ id = 'H1';    mechanism = 'total';   kind = 'circle'; x0 = 430; y0 = 230; x1 = 570; y1 = 370; color = $GREEN;  note = 'entirely under the panel' },
    [pscustomobject]@{ id = 'H2';    mechanism = 'total';   kind = 'square'; x0 = 515; y0 = 515; x1 = 605; y1 = 605; color = $PURPLE; note = 'entirely under the panel' }
  )
  hidden_B = @(
    [pscustomobject]@{ id = 'H-bar'; mechanism = 'partial'; kind = 'bar';  x0 = 200; y0 = 400; x1 = 430; y1 = 456; color = $BLUE;   note = 'x 200..300 visible and identical in both; x 300..430 hidden' },
    [pscustomobject]@{ id = 'H1';    mechanism = 'total';   kind = 'ring'; x0 = 420; y0 = 220; x1 = 580; y1 = 380; color = $ORANGE; note = 'entirely under the panel; outer 160, inner 80' },
    [pscustomobject]@{ id = 'H2';    mechanism = 'total';   kind = 'circle'; x0 = 515; y0 = 515; x1 = 605; y1 = 605; color = $BLUE;  note = 'entirely under the panel' },
    [pscustomobject]@{ id = 'H3';    mechanism = 'total';   kind = 'square'; x0 = 385; y0 = 505; x1 = 455; y1 = 575; color = $GREEN;  note = 'entirely under the panel' }
  )
  equivalence_note = 'every pixel that may differ lies strictly inside the occluded region, so both renders are pixel-identical while the hidden content differs in count, shape and colour'
  checks = [pscustomobject]@{
    problems = @()
    notes = @(
      'partial occlusion: the blue bar is visible for x 200..300 in both variants and hidden from x 300 rightwards; its tail ends at 560 in A and 430 in B',
      'total occlusion: A hides 3 objects (bar + circle + square), B hides 4 objects (bar + ring + circle + square)',
      'no dashed outline, no ghost, no shadow and no label is drawn for any hidden object',
      'the title, the six visible objects, the panel and all panel text are byte-identical between the two DSLs'
    )
  }
}
[IO.File]::WriteAllText($OutGeom, (($geom | ConvertTo-Json -Depth 8) + "`n"), $utf8)

if (-not $Quiet) {
  # The two DSLs must be identical everywhere except between the two markers.
  # A plain line-by-line diff would be useless because the hidden blocks differ
  # in length, which shifts every following line; so compare prefix and suffix.
  $la = @(Get-Content $OutA)
  $lb = @(Get-Content $OutB)
  $hiA = [Array]::IndexOf($la, '      <!--HIDDEN-DIFFERS-->')
  $hiB = [Array]::IndexOf($lb, '      <!--HIDDEN-DIFFERS-->')
  $paA = [Array]::IndexOf($la, '      <!--PANEL-OPAQUE-->')
  $paB = [Array]::IndexOf($lb, '      <!--PANEL-OPAQUE-->')
  $preOk = ($la[0..($hiA-1)] -join '|') -eq ($lb[0..($hiB-1)] -join '|')
  $sufOk = ($la[$paA..($la.Count-1)] -join '|') -eq ($lb[$paB..($lb.Count-1)] -join '|')
  $hidA = $la[($hiA+1)..($paA-1)]
  $hidB = $lb[($hiB+1)..($paB-1)]
  Write-Output ("A: {0} lines, B: {1} lines" -f $la.Count, $lb.Count)
  Write-Output ("shared prefix identical : {0}  ({1} lines, up to the hidden marker)" -f $preOk, $hiA)
  Write-Output ("shared suffix identical : {0}  ({1} lines, panel + visible + text)" -f $sufOk, ($la.Count - $paA))
  Write-Output ("hidden block A = {0} lines, B = {1} lines -> differs: {2}" -f $hidA.Count, $hidB.Count, (($hidA -join '|') -ne ($hidB -join '|')))
  Write-Output ("-> {0}" -f $OutGeom)
}
