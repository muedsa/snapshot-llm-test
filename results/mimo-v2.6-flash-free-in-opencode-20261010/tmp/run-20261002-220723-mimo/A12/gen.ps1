param([int]$Ver = 1)

# ---------------------------------------------------------------- A12 gen ----
# One content file + one design-token set -> four complete DSLs
# (360x800 / 768x1024 / 1440x900 / 1920x1080).
#
# Rules enforced here (and re-checked by verify.ps1):
#   * no Image, no transform/scale: each canvas is built from scratch
#   * every input string is emitted verbatim as <Raw><![CDATA[...]]></Raw>
#   * font-size floors: mobile body>=16, mobile card title>=18,
#     other body>=20, main title>=40 (all four canvases)
#   * safe margins: mobile>=16, others>=32
#   * every text box lives inside the safe area and no two boxes overlap
#   * layout is section-based (header / meta / cards / footer); the three
#     inter-section gaps absorb the leftover height, so nothing ever collides

$ErrorActionPreference = 'Stop'
[System.Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$TMP = "$root\tmp\$RUN\A12"
New-Item -ItemType Directory -Force -Path $TMP | Out-Null

# ------------------------------------------------------------------ input ----
$SRC   = "$root\tasks\A12-responsive-system\inputs\content.json"
$CT = [IO.File]::ReadAllText($SRC, [Text.UTF8Encoding]::new($false)) | ConvertFrom-Json

# ----------------------------------------------------------------- palette ----
$BG      = '#0B1220'
$SURFACE = '#132038'
$LINE    = '#23324C'
$INK     = '#F8FAFC'
$MUTED   = '#9FB0CB'
$ACCENT  = '#F6B94A'
$ACCENT2 = '#38BDF8'
$CTA_INK = '#0B1220'
$FAM  = 'Noto Sans CJK SC,Noto Sans CJK JP'
$MONO = 'Noto Sans Mono CJK SC'

# ------------------------------------------------------------- breakpoints ---
$BPS = @(
  [pscustomobject][ordered]@{
    name='mobile';  W=360;  H=800;  M=16; cols=1; rows=6
    titleSize=40; titleLines=2; subSize=16; metaSize=16; chipH=32
    cardT=18; cardD=16; idx=16; ctaSize=16; siteSize=16
    cardH=64; cardPad=14; gapX=8; gapY=8; ctaH=40; cardRadius=10
    edge=3; motifS=6; motifGap=12; ruleGap=12; titleSubGap=10; subHairGap=14
    chipGap=6; chipOuter=16; metaStack=$true;  idxMode='inline'
    siteGap=10; cardTitleGap=4; cardDetailGap=4; chipPad=12
    gapWeight2=1.6
  },
  [pscustomobject][ordered]@{
    name='tablet';  W=768;  H=1024; M=32; cols=2; rows=3
    titleSize=56; titleLines=1; subSize=24; metaSize=22; chipH=44
    cardT=24; cardD=20; idx=20; ctaSize=22; siteSize=20
    cardH=160; cardPad=20; gapX=24; gapY=26; ctaH=56; cardRadius=14
    edge=4; motifS=8; motifGap=16; ruleGap=14; titleSubGap=12; subHairGap=16
    chipGap=6; chipOuter=16; metaStack=$false; idxMode='inline'
    siteGap=12; cardTitleGap=8; cardDetailGap=8; chipPad=16
    gapWeight2=1.2
  },
  [pscustomobject][ordered]@{
    name='desktop'; W=1440; H=900;  M=48; cols=3; rows=2
    titleSize=72; titleLines=1; subSize=30; metaSize=26; chipH=52
    cardT=30; cardD=24; idx=20; ctaSize=26; siteSize=24
    cardH=150; cardPad=24; gapX=32; gapY=28; ctaH=56; cardRadius=16
    edge=6; motifS=10; motifGap=20; ruleGap=16; titleSubGap=14; subHairGap=18
    chipGap=6; chipOuter=16; metaStack=$false; idxMode='inline'
    siteGap=14; cardTitleGap=10; cardDetailGap=10; chipPad=20
    gapWeight2=1.2
  },
  [pscustomobject][ordered]@{
    name='stage';   W=1920; H=1080; M=56; cols=6; rows=1
    titleSize=88; titleLines=1; subSize=36; metaSize=30; chipH=64
    cardT=34; cardD=26; idx=24; ctaSize=30; siteSize=26
    cardH=300; cardPad=22; gapX=24; gapY=24; ctaH=72; cardRadius=18
    edge=6; motifS=12; motifGap=24; ruleGap=18; titleSubGap=16; subHairGap=20
    chipGap=6; chipOuter=16; metaStack=$false; idxMode='top'
    siteGap=16; cardTitleGap=14; cardDetailGap=14; chipPad=24
    gapWeight2=1.3
  }
)

# ------------------------------------------------------------------ guards ----
foreach ($b in $BPS) {
  $minM = 16
  if ($b.name -ne 'mobile') { $minM = 32 }
  if ($b.M -lt $minM) { throw "$($b.name): margin $($b.M) < required $minM" }
  if ($b.titleSize -lt 40) { throw "$($b.name): title $($b.titleSize) < 40" }
  foreach ($pair in @(@('subSize',16),@('metaSize',16),@('cardD',16),@('ctaSize',16),@('siteSize',16))) {
    $v = $b.($pair[0])
    $need = 16
    if ($b.name -ne 'mobile') { $need = 20 }
    if ($v -lt $need) { throw "$($b.name): $($pair[0])=$v < $need" }
  }
  if ($b.cardT -lt 18) { throw "$($b.name): card title $($b.cardT) < 18" }
  if (($b.cols * $b.rows) -lt 6) { throw "$($b.name): grid holds $($b.cols * $b.rows) < 6 cards" }
}

# ------------------------------------------------------------- emit helpers ---
$Cur     = $null
$CurName = ''
$Segs    = New-Object System.Collections.Generic.List[object]

function Guard([string]$s) { if ($s -and $s.Contains(']]>')) { throw "CDATA terminator in input: $s" } }

# Conservative advance-width estimator (used only to size boxes, never to draw).
# CJK/fullwidth = 1.0em; monospace latin = 0.62em; proportional latin per class.
function EstTextW([string]$s, [int]$size, [string]$mode) {
  $em = 0.0
  foreach ($ch in $s.ToCharArray()) {
    $cp = [int][char]$ch
    if ($cp -ge 0x2E80) { $em += 1.0; continue }
    if ($mode -eq 'mono') { $em += 0.62; continue }
    if ($cp -gt 127) { $em += 0.55; continue }
    if ($ch -ge 'A' -and $ch -le 'Z') { $em += 0.74; continue }
    if ($ch -ge 'a' -and $ch -le 'z') { $em += 0.58; continue }
    if ($ch -ge '0' -and $ch -le '9') { $em += 0.58; continue }
    if ($ch -eq ' ') { $em += 0.30; continue }
    $em += 0.40
  }
  return [int][math]::Ceiling($em * $size * 1.08)
}

# Anything that must stay on one line gets checked here before it is emitted.
function AssertFit([string]$what, [string]$s, [int]$size, [string]$mode, [int]$boxW) {
  $e = EstTextW $s $size $mode
  if ($e -gt $boxW) { throw "$($BP): '$what' estimated width $e px > box $boxW px (would wrap or clip): [$s]" }
}

function PutBox([string]$Id,[int]$X,[int]$Y,[int]$W,[int]$H,[string]$Col,[int]$Radius,[string]$Field) {
  $r = ''
  if ($Radius -gt 0) { $r = ' borderRadius="' + $Radius + '"' }
  $node = '<Positioned left="' + $X + '" top="' + $Y + '" width="' + $W + '" height="' + $H + '"><Container width="' + $W + '" height="' + $H + '" color="' + $Col + '"' + $r + '/></Positioned>'
  [void]$Cur.Add($node)
  [void]$Segs.Add([pscustomobject]@{
    bp=$CurName; id=$Id; kind='box'; field=$Field; source=''
    x=$X; y=$Y; width=$W; height=$H; text=''; fontFamily=''
    fontSize=0; fontStyle=''; color=$Col; textAlign=''; encoding='Container'
  })
}

function PutText([string]$Id,[int]$X,[int]$Y,[int]$W,[int]$H,[string]$Text,[string]$Fam,[int]$Fs,
                 [string]$Style,[string]$Col,[string]$Align,[string]$Field,[string]$Source) {
  Guard $Text
  $st = ''
  if ($Style -ne '') { $st = ' fontStyle="' + $Style + '"' }
  $node = '<Positioned left="' + $X + '" top="' + $Y + '" width="' + $W + '"><Text fontFamily="' + $Fam + '" fontSize="' + $Fs + '" color="' + $Col + '"' + $st + ' textAlign="' + $Align + '" height="1.0"><Raw><![CDATA[' + $Text + ']]></Raw></Text></Positioned>'
  [void]$Cur.Add($node)
  [void]$Segs.Add([pscustomobject]@{
    bp=$CurName; id=$Id; kind='text'; field=$Field; source=$Source
    x=$X; y=$Y; width=$W; height=$H; text=$Text; fontFamily=$Fam
    fontSize=$Fs; fontStyle=$Style; color=$Col; textAlign=$Align; encoding='Raw+CDATA'
  })
}

# ---------------------------------------------------------------- layout ------
$CanvasRecs = New-Object System.Collections.Generic.List[object]

foreach ($b in $BPS) {
  $BP = $b.name
  $Cur = New-Object System.Collections.Generic.List[string]
  $CurName = $BP

  $innerX = $b.M
  $innerW = $b.W - (2 * $b.M)
  $innerY = $b.M
  $innerH = $b.H - (2 * $b.M)

  # --- header -------------------------------------------------------------
  $y = $innerY
  PutBox "$BP/rule" $innerX $y $innerW $b.edge $ACCENT 0 'decor:rule'

  $y = $y + $b.edge + $b.ruleGap
  $titleY = $y

  $motifW = 3 * $b.motifS
  $motifX = $innerX + $innerW - $motifW
  $motifY = $titleY + [int][math]::Floor(($b.titleSize - $motifW) / 2)
  if ($motifY -lt $titleY) { $motifY = $titleY }
  # shared decorative component: a 2x2 square mark (same motif on all canvases)
  $mcols = @($ACCENT, $ACCENT2, $ACCENT2, $ACCENT)
  for ($mi = 0; $mi -lt 4; $mi++) {
    $mr = [int][math]::Floor($mi / 2); $mc = $mi % 2
    PutBox "$BP/motif-$mi" ($motifX + $mc * (2 * $b.motifS)) ($motifY + $mr * (2 * $b.motifS)) $b.motifS $b.motifS $mcols[$mi] 0 'decor:motif'
  }

  $titleW = $innerW - $motifW - $b.motifGap
  if ($b.titleLines -eq 2) {
    # 360px cannot hold the whole title at the mandated 40px, so it wraps at the
    # " / " separator; both halves still come verbatim from inputs/content.json.
    $full = [string]$CT.title
    $cut  = $full.IndexOf(' / ')
    if ($cut -lt 1) { throw 'title has no " / " separator to wrap at' }
    $L1 = $full.Substring(0, $cut + 2)
    $L2 = $full.Substring($cut + 3)
    PutText "$BP/title-1" $innerX $titleY $titleW $b.titleSize $L1 $FAM $b.titleSize 'BOLD' $INK 'START' 'title' 'inputs/content.json title (line 1 of 2)'
    PutText "$BP/title-2" $innerX ($titleY + $b.titleSize + 4) $titleW $b.titleSize $L2 $FAM $b.titleSize 'BOLD' $INK 'START' 'title' 'inputs/content.json title (line 2 of 2)'
    AssertFit 'title line 1' $L1 $b.titleSize 'fam' $titleW
    AssertFit 'title line 2' $L2 $b.titleSize 'fam' $titleW
    $y = $titleY + (2 * $b.titleSize) + 4
  } else {
    PutText "$BP/title" $innerX $titleY $titleW $b.titleSize ([string]$CT.title) $FAM $b.titleSize 'BOLD' $INK 'START' 'title' 'inputs/content.json title'
    AssertFit 'title' ([string]$CT.title) $b.titleSize 'fam' $titleW
    $y = $titleY + $b.titleSize
  }

  $y = $y + $b.titleSubGap
  PutText "$BP/subtitle" $innerX $y $innerW $b.subSize ([string]$CT.subtitle) $FAM $b.subSize '' $MUTED 'START' 'subtitle' 'inputs/content.json subtitle'
  AssertFit 'subtitle' ([string]$CT.subtitle) $b.subSize 'fam' $innerW
  $y = $y + $b.subSize + $b.subHairGap
  PutBox "$BP/hair" $innerX $y $innerW 1 $LINE 0 'decor:hairline'
  $y = $y + 1
  $headerEnd = $y
  $headerH   = $headerEnd - $innerY

  # --- meta ---------------------------------------------------------------
  if ($b.metaStack) {
    $metaH = (2 * $b.chipH) + $b.chipGap
  } else {
    $metaH = $b.chipH
  }

  # --- cards --------------------------------------------------------------
  $cardsH = ($b.rows * $b.cardH) + (($b.rows - 1) * $b.gapY)

  # --- footer -------------------------------------------------------------
  $siteInkPad = [int][math]::Ceiling($b.siteSize * 0.3)
  $footerH = $b.ctaH + $b.siteGap + $b.siteSize + $siteInkPad

  # --- distribute the leftover height over the three section gaps ---------
  $fixed = $headerH + $metaH + $cardsH + $footerH
  $gapsT = $innerH - $fixed
  if ($gapsT -lt 0) { throw "$($BP): content does not fit (overflow $(-$gapsT) px)" }
  $sumW = 1.0 + [double]$b.gapWeight2 + 1.0
  $g1 = [int][math]::Round($gapsT * 1.0 / $sumW)
  $g2 = [int][math]::Round($gapsT * [double]$b.gapWeight2 / $sumW)
  $g3 = $gapsT - $g1 - $g2
  if ($g1 -lt 0 -or $g2 -lt 0 -or $g3 -lt 0) { throw "$($BP): negative gap" }

  $metaY   = $headerEnd + $g1
  $cardsY  = $metaY + $metaH + $g2
  $footerY = $cardsY + $cardsH + $g3
  $ctaY    = $footerY
  $siteY   = $ctaY + $b.ctaH + $b.siteGap
  if (($siteY + $b.siteSize) -gt ($innerY + $innerH)) { throw "$($BP): footer overflows" }

  # --- meta chips ---------------------------------------------------------
  $chipTextTop = $metaY + [int][math]::Floor(($b.chipH - $b.metaSize) / 2)
  if ($b.metaStack) {
    $chip1 = ([string]$CT.date) + ' · ' + ([string]$CT.time)
    $c1x = $innerX
    $c1w = $innerW
    PutBox "$BP/chip-date" $c1x $metaY $c1w $b.chipH $SURFACE $b.cardRadius 'decor:chip'
    PutText "$BP/chip-date-t" ($c1x + $b.chipPad) $chipTextTop ($c1w - (2 * $b.chipPad)) $b.metaSize $chip1 $MONO $b.metaSize '' $INK 'START' 'date;time' 'inputs/content.json date + time'

    $c2y = $metaY + $b.chipH + $b.chipGap
    PutBox "$BP/chip-loc" $innerX $c2y $innerW $b.chipH $SURFACE $b.cardRadius 'decor:chip'
    PutText "$BP/chip-loc-t" ($innerX + $b.chipPad) ($c2y + [int][math]::Floor(($b.chipH - $b.metaSize) / 2)) ($innerW - (2 * $b.chipPad)) $b.metaSize ([string]$CT.location) $FAM $b.metaSize '' $INK 'START' 'location' 'inputs/content.json location'
  } else {
    $defs = @(
      @{ n='date';     f='date';     t=[string]$CT.date;     fm=$MONO; mode='mono' },
      @{ n='time';     f='time';     t=[string]$CT.time;     fm=$MONO; mode='mono' },
      @{ n='location'; f='location'; t=[string]$CT.location; fm=$FAM;  mode='fam'  }
    )
    # chips are sized to their content rather than split three ways: on 768px an
    # equal third leaves only 192px for the location string and it wrapped out of
    # the pill onto the background.
    $avail = $innerW - (2 * $b.chipOuter)
    $est = @()
    foreach ($d in $defs) { $est += (EstTextW $d.t $b.metaSize $d.mode) }
    $sumEst = [double](($est | Measure-Object -Sum).Sum)
    $ws = @(); $acc = 0
    for ($k = 0; $k -lt 3; $k++) {
      $w = [int][math]::Floor($avail * $est[$k] / $sumEst)
      $ws += $w
      $acc += $w
    }
    $ws[2] = $ws[2] + ($avail - $acc)
    $cx = $innerX
    for ($ci = 0; $ci -lt 3; $ci++) {
      $d = $defs[$ci]
      $cw2 = $ws[$ci]
      $need = $est[$ci] + (2 * $b.chipPad)
      if ($cw2 -lt $need) { throw "$($BP): chip '$($d.n)' width $cw2 < required $need" }
      PutBox "$BP/chip-$($d.n)" $cx $metaY $cw2 $b.chipH $SURFACE $b.cardRadius 'decor:chip'
      PutText "$BP/chip-$($d.n)-t" ($cx + $b.chipPad) $chipTextTop ($cw2 - (2 * $b.chipPad)) $b.metaSize $d.t $d.fm $b.metaSize '' $INK 'START' $d.f ("inputs/content.json " + $d.f)
      $cx = $cx + $cw2 + $b.chipOuter
    }
    if (($cx - $b.chipOuter) -ne ($innerX + $innerW)) { throw "$($BP): chip row does not fill inner width" }
  }

  # --- cards --------------------------------------------------------------
  $cw    = [int][math]::Floor(($innerW - (($b.cols - 1) * $b.gapX)) / $b.cols)
  $gridW = ($b.cols * $cw) + (($b.cols - 1) * $b.gapX)
  $gridX = $innerX + [int][math]::Floor(($innerW - $gridW) / 2)
  $idxW  = [int][math]::Ceiling(1.4 * $b.idx)

  $cardRecs = @()
  for ($i = 0; $i -lt 6; $i++) {
    $rr = [int][math]::Floor($i / $b.cols)
    $cc = $i % $b.cols
    $cx = $gridX + ($cc * ($cw + $b.gapX))
    $cy = $cardsY + ($rr * ($b.cardH + $b.gapY))
    $cd = $CT.cards[$i]
    $path = 'cards[' + $i + ']'

    PutBox "$BP/card-$($cd.id)/surface" $cx $cy $cw $b.cardH $SURFACE $b.cardRadius 'decor:card'
    # left accent stripe, inset vertically by the corner radius so it never
    # spills outside the rounded rectangle
    PutBox "$BP/card-$($cd.id)/stripe" $cx ($cy + $b.cardRadius) 4 ($b.cardH - (2 * $b.cardRadius)) $ACCENT2 0 'decor:stripe'

    $textX = $cx + $b.cardPad
    $textW = $cw - (2 * $b.cardPad)
    $detH = $b.cardD
    if ($b.idxMode -eq 'top') { $detH = $b.cardD * 2 }
    if ($b.idxMode -eq 'top') {
      AssertFit ("$BP/card-" + $cd.id + "/title") ([string]$cd.title) $b.cardT 'fam' $textW
    } else {
      AssertFit ("$BP/card-" + $cd.id + "/title") ([string]$cd.title) $b.cardT 'fam' ($textW - $idxW - 10)
      AssertFit ("$BP/card-" + $cd.id + "/detail") ([string]$cd.detail) $b.cardD 'fam' $textW
    }

    if ($b.idxMode -eq 'top') {
      $contentH = $b.idx + 24 + $b.cardT + $b.cardDetailGap + $b.cardD
      $padTop = [int][math]::Floor(($b.cardH - $contentH) / 2)
      $idxY  = $cy + $padTop
      $titY  = $idxY + $b.idx + 24
      $detY  = $titY + $b.cardT + $b.cardDetailGap
      PutText "$BP/card-$($cd.id)/index" $textX $idxY $textW $b.idx ([string]$cd.id) $MONO $b.idx '' $ACCENT 'START' ($path + '.id') ("inputs/content.json " + $path + ".id")
      PutText "$BP/card-$($cd.id)/title" $textX $titY $textW $b.cardT ([string]$cd.title) $FAM $b.cardT 'BOLD' $INK 'START' ($path + '.title') ("inputs/content.json " + $path + ".title")
      PutText "$BP/card-$($cd.id)/detail" $textX $detY $textW $detH ([string]$cd.detail) $FAM $b.cardD '' $MUTED 'START' ($path + '.detail') ("inputs/content.json " + $path + ".detail")
    } else {
      $contentH = $b.cardT + $b.cardDetailGap + $b.cardD
      $padTop = [int][math]::Floor(($b.cardH - $contentH) / 2)
      $titY = $cy + $padTop
      $detY = $titY + $b.cardT + $b.cardDetailGap
      $idxY = $titY + ($b.cardT - $b.idx)
      $titW = $textW - $idxW - 10
      PutText "$BP/card-$($cd.id)/title" $textX $titY $titW $b.cardT ([string]$cd.title) $FAM $b.cardT 'BOLD' $INK 'START' ($path + '.title') ("inputs/content.json " + $path + ".title")
      PutText "$BP/card-$($cd.id)/index" ($textX + $textW - $idxW) $idxY $idxW $b.idx ([string]$cd.id) $MONO $b.idx '' $ACCENT 'END' ($path + '.id') ("inputs/content.json " + $path + ".id")
      PutText "$BP/card-$($cd.id)/detail" $textX $detY $textW $detH ([string]$cd.detail) $FAM $b.cardD '' $MUTED 'START' ($path + '.detail') ("inputs/content.json " + $path + ".detail")
    }

    $cardRecs += [pscustomobject]@{
      id=[string]$cd.id; index=$i; x=$cx; y=$cy; width=$cw; height=$b.cardH
      title_x=$textX; title_y=$titY; title_w=$(if ($b.idxMode -eq 'top') { $textW } else { $textW - $idxW - 10 }); title_h=$b.cardT
      index_x=$(if ($b.idxMode -eq 'top') { $textX } else { $textX + $textW - $idxW }); index_y=$idxY; index_w=$(if ($b.idxMode -eq 'top') { $textW } else { $idxW }); index_h=$b.idx
      detail_x=$textX; detail_y=$detY; detail_w=$textW; detail_h=$detH
    }
  }

  # --- footer -------------------------------------------------------------
  PutBox "$BP/cta" $innerX $ctaY $innerW $b.ctaH $ACCENT ([int][math]::Floor($b.ctaH / 4)) 'decor:cta'
  PutText "$BP/cta-t" $innerX ($ctaY + [int][math]::Floor(($b.ctaH - $b.ctaSize) / 2)) $innerW $b.ctaSize ([string]$CT.cta) $FAM $b.ctaSize 'BOLD' $CTA_INK 'CENTER' 'cta' 'inputs/content.json cta'
  AssertFit 'cta' ([string]$CT.cta) $b.ctaSize 'fam' $innerW
  PutText "$BP/site" $innerX $siteY $innerW $b.siteSize ([string]$CT.website) $MONO $b.siteSize '' $ACCENT2 'START' 'website' 'inputs/content.json website'
  AssertFit 'website' ([string]$CT.website) $b.siteSize 'mono' $innerW

  $endY = $siteY + $b.siteSize
  $bottomSlack = ($innerY + $innerH) - $endY
  if ($bottomSlack -lt -2) { throw "$($BP): content past safe area by $(-$bottomSlack)" }

  # --- record -------------------------------------------------------------
  $outPath = "$TMP\$BP-v$Ver.snapshot"
  $doc = '<Snapshot type="png" background="' + $BG + '"><Container width="' + $b.W + '" height="' + $b.H + '" color="' + $BG + '"><Stack>' + ([string]::Join('', $Cur.ToArray())) + '</Stack></Container></Snapshot>'
  [IO.File]::WriteAllText($outPath, $doc, [Text.UTF8Encoding]::new($false))

  $CanvasRecs.Add([pscustomobject][ordered]@{
    name=$BP; width=$b.W; height=$b.H; margin=$b.M
    safe=[pscustomobject]@{ left=$b.M; top=$b.M; right=($b.W - $b.M); bottom=($b.H - $b.M) }
    columns=$b.cols; rows=$b.rows
    section_gaps=[pscustomobject]@{ header_to_meta=$g1; meta_to_cards=$g2; cards_to_footer=$g3; total=$gapsT }
    sections=[pscustomobject]@{
      header=[pscustomobject]@{ top=$innerY; bottom=$headerEnd }
      meta=[pscustomobject]@{ top=$metaY; bottom=($metaY + $metaH) }
      cards=[pscustomobject]@{ top=$cardsY; bottom=($cardsY + $cardsH); grid_x=$gridX; card_w=$cw; card_h=$b.cardH }
      footer=[pscustomobject]@{ top=$ctaY; bottom=$endY; cta=[pscustomobject]@{ x=$innerX; y=$ctaY; w=$innerW; h=$b.ctaH }; site=[pscustomobject]@{ x=$innerX; y=$siteY; w=$innerW; h=$b.siteSize } }
      motif=[pscustomobject]@{ x=$motifX; y=$motifY; size=$motifW }
    }
    cards_list=$cardRecs
    dsl=("tmp/$RUN/A12/$BP-v$Ver.snapshot")
    dsl_bytes=(Get-Item $outPath).Length
    bottom_slack=$bottomSlack
    node_count=$Cur.Count
  })

  Write-Output ("  {0,-8} {1}x{2} margin={3} cols={4} gaps={5}/{6}/{7} bottom_slack={8} nodes={9} bytes={10}" -f `
    $BP, $b.W, $b.H, $b.M, $b.cols, $g1, $g2, $g3, $bottomSlack, $Cur.Count, (Get-Item $outPath).Length)
}

# ------------------------------------------------------------- design tokens ---
function BpToken([string]$n) {
  $x = $BPS | Where-Object { $_.name -eq $n }
  return [pscustomobject][ordered]@{
    breakpoint=$n
    canvas=[pscustomobject]@{ width=$x.W; height=$x.H; safe_margin=$x.M; min_safe_margin_required=$(if ($x.name -eq 'mobile') { 16 } else { 32 }) }
    typography=[pscustomobject]@{
      main_title_px=$x.titleSize
      main_title_min_px=40
      subtitle_px=$x.subSize
      body_min_px=$(if ($x.name -eq 'mobile') { 16 } else { 20 })
      card_title_px=$x.cardT
      card_title_min_px=18
      card_detail_px=$x.cardD
      meta_px=$x.metaSize
      cta_px=$x.ctaSize
      website_px=$x.siteSize
      card_index_px=$x.idx
      line_height=1.0
    }
    spacing=[pscustomobject]@{
      card_gap_x=$x.gapX
      card_gap_y=$x.gapY
      card_padding=$x.cardPad
      chip_height=$x.chipH
      chip_padding=$x.chipPad
      chip_gap=$x.chipGap
      cta_height=$x.ctaH
      section_gap_header_meta=$null
      section_gap_meta_cards=$null
      section_gap_cards_footer=$null
    }
    components=[pscustomobject]@{
      card_columns=$x.cols
      card_rows=$x.rows
      card_radius=$x.cardRadius
      card_stripe_width=4
      index_mode=$x.idxMode
      meta_layout=$(if ($x.metaStack) { 'stacked (date+time share one chip)' } else { 'row of three chips' })
      title_lines=$x.titleLines
    }
  }
}

$designTokens = [pscustomobject][ordered]@{
  schema_version = 1
  task_id = 'A12'
  run_id = $RUN
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone = 'Asia/Shanghai (UTC+08:00)'
  source_content = 'tasks/A12-responsive-system/inputs/content.json'
  generator = "tmp/$RUN/A12/gen.ps1 -Ver $Ver"
  palette = [pscustomobject][ordered]@{
    background=$BG; surface=$SURFACE; hairline=$LINE; text_primary=$INK
    text_secondary=$MUTED; accent_amber=$ACCENT; accent_cyan=$ACCENT2; cta_text=$CTA_INK
    note = 'Identical on all four canvases - only size and arrangement change.'
  }
  fonts = [pscustomobject][ordered]@{
    prose = $FAM
    numeric = $MONO
    source = 'GET /fonts (shared-fonts-0001, 200, 1407 ms); response list stored at tmp/run-20261002-220723-mimo/A11/fonts-0001.txt'
    rule = 'fontFamily lists must not contain a space after the comma (documented).'
  }
  component_rules = @(
    [pscustomobject]@{ name='accent-rule';   role='full-width amber bar opening the header'; present='all four' }
    [pscustomobject]@{ name='square-motif';  role='2x2 amber/cyan square mark, top-right of the title line'; present='all four'; size_by_bp='6/8/10/12 px squares' }
    [pscustomobject]@{ name='hairline';      role='1px divider between subtitle and meta'; present='all four' }
    [pscustomobject]@{ name='meta-chip';     role='surface pill holding date / time / location'; present='all four'; rearranged='stacked on mobile, 3-across elsewhere' }
    [pscustomobject]@{ name='card-tile';     role='surface tile + 4px cyan left stripe + amber id + title + detail'; present='all four'; rearranged='1x6 / 2x3 / 3x2 / 6x1' }
    [pscustomobject]@{ name='cta-pill';      role='amber rounded rectangle with the CTA as plain text (no QR)'; present='all four' }
    [pscustomobject]@{ name='site-line';     role='cyan monospace website line under the CTA'; present='all four' }
  )
  responsive_rules = @(
    'No Image tag and no transform/scale anywhere: each of the four DSLs is generated from scratch at its own pixel size.'
    'Card grid goes 1 column -> 2 -> 3 -> 6 while every card keeps title, detail and id in full.'
    'On 360px the title wraps at the slash so it can stay at the mandated 40px instead of being shrunk.'
    'On 360px date and time share one chip to keep their relationship; the strings themselves are untouched.'
    'Section gaps absorb the leftover height, so the four canvases share structure instead of fixed offsets.'
    'Card detail carries an explicit width and therefore wraps rather than overflowing (stage only).'
  )
  breakpoints = @( (BpToken 'mobile'), (BpToken 'tablet'), (BpToken 'desktop'), (BpToken 'stage') )
}
foreach ($rec in $CanvasRecs) {
  $t = $designTokens.breakpoints | Where-Object { $_.breakpoint -eq $rec.name }
  $t.spacing.section_gap_header_meta   = $rec.section_gaps.header_to_meta
  $t.spacing.section_gap_meta_cards    = $rec.section_gaps.meta_to_cards
  $t.spacing.section_gap_cards_footer  = $rec.section_gaps.cards_to_footer
}
$tokPath = "$TMP\design-tokens-v$Ver.json"
[IO.File]::WriteAllText($tokPath, ($designTokens | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))

# --------------------------------------------------------------- content map ---
$allFields = New-Object System.Collections.Generic.List[string]
foreach ($f in @('title','subtitle','date','time','location','cta','website')) { [void]$allFields.Add($f) }
for ($i = 0; $i -lt 6; $i++) {
  $id = $CT.cards[$i].id
  [void]$allFields.Add(('cards[' + $i + '].id'))
  [void]$allFields.Add(('cards[' + $i + '].title'))
  [void]$allFields.Add(('cards[' + $i + '].detail'))
}
$valueOf = @{}
$valueOf['title'] = [string]$CT.title
$valueOf['subtitle'] = [string]$CT.subtitle
$valueOf['date'] = [string]$CT.date
$valueOf['time'] = [string]$CT.time
$valueOf['location'] = [string]$CT.location
$valueOf['cta'] = [string]$CT.cta
$valueOf['website'] = [string]$CT.website
for ($i = 0; $i -lt 6; $i++) {
  $cd = $CT.cards[$i]
  $valueOf[('cards[' + $i + '].id')] = [string]$cd.id
  $valueOf[('cards[' + $i + '].title')] = [string]$cd.title
  $valueOf[('cards[' + $i + '].detail')] = [string]$cd.detail
}

$fieldRecs = New-Object System.Collections.Generic.List[object]
foreach ($fp in $allFields) {
  $entry = [pscustomobject][ordered]@{
    path = $fp
    value = $valueOf[$fp]
    required = $true
    encoding = 'Raw+CDATA'
    canvases = [ordered]@{}
  }
  foreach ($rec in $CanvasRecs) {
    $matches = @($Segs | Where-Object { ($_.bp -eq $rec.name) -and ($_.field -eq $fp) })
    if ($fp -eq 'date') { $matches = @($Segs | Where-Object { ($_.bp -eq $rec.name) -and ($_.field -eq 'date;time') }) }
    if ($fp -eq 'time') { $matches = @($Segs | Where-Object { ($_.bp -eq $rec.name) -and ($_.field -eq 'date;time') }) }
    $boxes = @()
    foreach ($m in $matches) {
      $boxes += [pscustomobject]@{ x=$m.x; y=$m.y; width=$m.width; height=$m.height; text=$m.text; fontSize=$m.fontSize; id=$m.id }
    }
    $entry.canvases[$rec.name] = [pscustomobject][ordered]@{
      status = 'preserved-full'
      boxes = $boxes
    }
  }
  $fieldRecs.Add($entry)
}

# the split title on mobile is still one complete input field
foreach ($e in $fieldRecs) {
  if ($e.path -eq 'title') {
    foreach ($rec in $CanvasRecs) {
      $c = $e.canvases[$rec.name]
      $bs = @($c.boxes)
      if ($bs.Count -eq 2) {
        $c.status = 'preserved-full-wrapped-2-lines'
        $x0 = ($bs | ForEach-Object { $_.x } | Measure-Object -Minimum).Minimum
        $y0 = ($bs | ForEach-Object { $_.y } | Measure-Object -Minimum).Minimum
        $x1 = ($bs | ForEach-Object { $_.x + $_.width } | Measure-Object -Maximum).Maximum
        $y1 = ($bs | ForEach-Object { $_.y + $_.height } | Measure-Object -Maximum).Maximum
        $c | Add-Member -NotePropertyName union_box -NotePropertyValue ([pscustomobject]@{ x=$x0; y=$y0; width=($x1-$x0); height=($y1-$y0) }) -Force
      }
    }
  }
}

$contentMap = [pscustomobject][ordered]@{
  schema_version = 1
  task_id = 'A12'
  run_id = $RUN
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone = 'Asia/Shanghai (UTC+08:00)'
  source = 'tasks/A12-responsive-system/inputs/content.json'
  generator = "tmp/$RUN/A12/gen.ps1 -Ver $Ver"
  legend = [pscustomobject]@{
    box = 'x/y/width/height are absolute pixels in that canvas, measured from the top-left of the PNG.'
    height_note = 'Text boxes use height = fontSize because every Text node is emitted with height="1.0". Card detail reserves 2 lines so a wrap can never collide with the tile edge.'
    status = 'preserved-full = the input string is present verbatim; preserved-full-wrapped-2-lines = present verbatim but laid out on two lines.'
    encoding = 'Every string is emitted as <Raw><![CDATA[...]]></Raw>; the parser does not decode HTML entities and Text would trim leading/trailing spaces, so Raw is required.'
  }
  canvases = $CanvasRecs
  fields = $fieldRecs
  field_count = $fieldRecs.Count
  summary = [pscustomobject][ordered]@{
    canvases = 4
    fields_total = $fieldRecs.Count
    fields_per_canvas = $fieldRecs.Count
    preserved_all = $true
    abbreviations = 0
    dropped_fields = 0
    image_tags = 0
    transforms = 0
  }
}
$mapPath = "$TMP\content-map-v$Ver.json"
[IO.File]::WriteAllText($mapPath, ($contentMap | ConvertTo-Json -Depth 14), [Text.UTF8Encoding]::new($false))

$segPath = "$TMP\segments-v$Ver.json"
[IO.File]::WriteAllText($segPath, ($Segs | ConvertTo-Json -Depth 6), [Text.UTF8Encoding]::new($false))

Write-Output "written:"
Write-Output ("  " + $tokPath + "  bytes=" + (Get-Item $tokPath).Length)
Write-Output ("  " + $mapPath + "  bytes=" + (Get-Item $mapPath).Length)
Write-Output ("  segments  bytes=" + (Get-Item $segPath).Length)
Write-Output ("fields={0}  segments={1}" -f $fieldRecs.Count, $Segs.Count)
