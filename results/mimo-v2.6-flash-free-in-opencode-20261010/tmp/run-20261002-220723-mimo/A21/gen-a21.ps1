# gen-a21.ps1 - A21 叠光 Layerlight 三轮双尺寸发布物的 DSL / tokens / content-map / layout-map 生成器
# 用法: -Round 1|2|3 -OutDir <round dir> -MapPath <layout-map.json>
# 主体全部由 DSL 构造，不使用 <Image>，不嵌入外部图片。
param(
  [Parameter(Mandatory = $true)][ValidateSet(1, 2, 3)][int]$Round,
  [Parameter(Mandatory = $true)][string]$OutDir,
  [Parameter(Mandatory = $true)][string]$MapPath
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

# --------------------------------------------------------------------- helpers --
function N([double]$v) {
  if ([double]::IsNaN($v)) { return '0' }
  if ($v -eq [Math]::Truncate($v)) { return ([long]$v).ToString([cultureinfo]::InvariantCulture) }
  return $v.ToString('0.##', [cultureinfo]::InvariantCulture)
}
function Esc([string]$s) { return $s.Replace('&', '&amp;').Replace('<', '&lt;').Replace('>', '&gt;') }

# conservative advance-width estimate: CJK/fullwidth = 1em, latin narrower
function EstW([string]$s, [double]$fs, [double]$ls = 0) {
  $w = 0.0
  foreach ($ch in $s.ToCharArray()) {
    $c = [int]$ch
    if ($c -gt 0x2E7F)      { $w += $fs * 1.00 }
    elseif ($c -eq 0x00B7)  { $w += $fs * 0.35 }
    elseif ($c -eq 0x20)    { $w += $fs * 0.28 }
    elseif ($c -ge 0x30 -and $c -le 0x39) { $w += $fs * 0.58 }
    elseif ($c -ge 0x41 -and $c -le 0x5A) { $w += $fs * 0.68 }
    elseif ($c -ge 0x61 -and $c -le 0x7A) { $w += $fs * 0.54 }
    else { $w += $fs * 0.40 }
  }
  if ($ls -ne 0) { $w += $ls * [Math]::Max(0, $s.Length - 1) }
  return [Math]::Ceiling($w)
}
function Hex2Rgb([string]$h) {
  return @([Convert]::ToInt32($h.Substring(0, 2), 16), [Convert]::ToInt32($h.Substring(2, 2), 16), [Convert]::ToInt32($h.Substring(4, 2), 16))
}
function Rgb2Hex($r, $g, $b) { return ('{0:X2}{1:X2}{2:X2}' -f [int][Math]::Round($r), [int][Math]::Round($g), [int][Math]::Round($b)) }

# source-over composite in 8-bit sRGB; $layers is bottom-up, entries "RRGGBB" or "RRGGBB:AAhex"
function Composite([string[]]$layers) {
  $out = $null
  foreach ($spec in $layers) {
    $parts = $spec.Split(':')
    $rgb = Hex2Rgb $parts[0]
    $a = 1.0
    if ($parts.Count -gt 1) { $a = [Convert]::ToInt32($parts[1], 16) / 255.0 }
    if ($null -eq $out) { $out = $rgb }
    else {
      # NOTE: each term MUST be parenthesised. In PowerShell the comma binds TIGHTER
      # than '*', so `@($a*$b + ..., $c*$d + ...)` parses as `$a * (..., ...) * ...`
      # and dies with "[System.Object[]] does not contain a method named 'op_Multiply'".
      # Empirically `1 * 2, 3` fails; `@(1 * 2, 3)` fails; the parenthesised form works.
      # Rounds 1-2 never hit this because they only ever composites a single layer.
      $out = @(($rgb[0] * $a + $out[0] * (1 - $a)),
               ($rgb[1] * $a + $out[1] * (1 - $a)),
               ($rgb[2] * $a + $out[2] * (1 - $a)))
    }
  }
  return Rgb2Hex $out[0] $out[1] $out[2]
}

# ---------------------------------------------------------------------- tokens --
$PRIMARY    = '5B4FE8'
$PRIMARY_LT = '8B85FF'
$ACCENT     = 'FFB020'
$FAM_CJK    = 'Noto Sans CJK SC'
$FAM_LATIN  = 'Inter,Noto Sans CJK SC'
$BAND_A_ALPHA = '1F'    # 31/255 = 12.16 % primary over the base
$BAND_B_ALPHA = '29'    # 41/255 = 16.08 % accent  over the base

if ($Round -lt 3) {
  $THEME = 'dark'
  $PAGE = '0E1026'; $PANEL = '171A3C'
  $T1 = 'F4F6FF'; $T2 = 'C2C7EE'; $TA = '8B85FF'; $ON_PRIMARY = 'FFFFFF'
  $BAND_A = $null; $BAND_B = $null
  $BAND_A_SPEC = $null; $BAND_B_SPEC = $null
} else {
  $THEME = 'light'
  $PAGE = 'F4F5FB'; $PANEL = 'FFFFFF'
  $T1 = '14173A'; $T2 = '474B77'; $TA = '3730A3'; $ON_PRIMARY = 'FFFFFF'
  # $BAND_* is the DSL colour: 8-digit #RRGGBBAA (CSS order) -> #5B4FE81F
  $BAND_A = "$PRIMARY$BAND_A_ALPHA"
  $BAND_B = "$ACCENT$BAND_B_ALPHA"
  # *_SPEC is the compositing-layer form "RRGGBB:AAhex" that Composite() understands.
  # Without the colon Composite would read the 8-hex digits as R,G,B and treat the band
  # as fully opaque, so the expected background would come out as flat #5B4FE8.
  $BAND_A_SPEC = "$($PRIMARY):$($BAND_A_ALPHA)"
  $BAND_B_SPEC = "$($ACCENT):$($BAND_B_ALPHA)"
}

# ------------------------------------------------------------------- content ----
$TITLE_R1  = '让复杂信息变得清晰'
$TITLE_R23 = '当所有信息都想成为标题：让复杂信息变得清晰的结构化方法'
$DECK_R1   = '叠光 Layerlight 线上发布会'
$DECK_R23  = '让复杂信息变得清晰'
$EYEBROW   = 'ONLINE LAUNCH'
$DATE      = '2026.11.07 19:30'
$SPEAKERS  = '讲者：林川 / 苏言'
$URL       = 'layerlight.example.org'
$WORDMARK  = '叠光 Layerlight'
$SPONSOR   = '赞助方：Northstar Research / 云构工具'
$FREE      = '免费参加 · 无需报名'
$ENGLISH   = 'Clarity through structure'

$TITLE_FS  = @{ 1 = 88; 2 = 56; 3 = 56 }   # portrait: >=56 r1, >=48 r2/r3
$TITLE_FSW = @{ 1 = 72; 2 = 52; 3 = 52 }   # wide
$MIN_TITLE = $(if ($Round -eq 1) { 56 } else { 48 })
$titleText = $(if ($Round -eq 1) { $TITLE_R1 } else { $TITLE_R23 })
$deckText  = $(if ($Round -eq 1) { $DECK_R1 } else { $DECK_R23 })

# --------------------------------------------------------------- emit helpers ---
$DSL   = New-Object System.Collections.Generic.List[string]
$BLOCK = New-Object System.Collections.Generic.List[object]

function AddRect($x, $y, $w, $h, $color, $radius, $border) {
  $a = New-Object System.Collections.Generic.List[string]
  $a.Add('width="' + (N $w) + '"'); $a.Add('height="' + (N $h) + '"'); $a.Add('color="#' + $color + '"')
  if ($radius -gt 0) { $a.Add('borderRadius="' + (N $radius) + '"') }
  if ($border)       { $a.Add('border="' + $border + '"') }
  $DSL.Add('<Positioned left="' + (N $x) + '" top="' + (N $y) + '" width="' + (N $w) + '" height="' + (N $h) +
           '"><Container ' + ($a -join ' ') + '/></Positioned>')
}

function AddText($key, $orient, $x, $y, $w, $h, $fs, $color, $txt, $bold, $family, $align, $maxLines, $ls,
                 [string[]]$bgLayers, $bgName, $probeMinX, $probeX) {
  $a = New-Object System.Collections.Generic.List[string]
  $a.Add('fontSize="' + (N $fs) + '"')
  $a.Add('fontFamily="' + $family + '"')
  $a.Add('color="#' + $color + '"')
  if ($bold)      { $a.Add('fontStyle="BOLD"') }
  if ($align)     { $a.Add('textAlign="' + $align + '"') }
  if ($maxLines -gt 0) { $a.Add('maxLines="' + $maxLines + '"') }
  if ($ls -ne 0)  { $a.Add('letterSpacing="' + (N $ls) + '"') }
  $DSL.Add('<Positioned left="' + (N $x) + '" top="' + (N $y) + '" width="' + (N $w) + '" height="' + (N $h) +
           '"><Text ' + ($a -join ' ') + '>' + (Esc $txt) + '</Text></Positioned>')

  $px = $x - 6
  if ($null -ne $probeX) { $px = $probeX }
  $BLOCK.Add([pscustomobject]@{
    key = $key; orient = $orient; round = $Round; kind = 'text'
    text = $txt; fontSize = $fs; bold = [bool]$bold; color = ('#' + $color); family = $family
    x = $x; y = $y; w = $w; h = $h
    probe = [pscustomobject]@{ x = $px; y = [Math]::Round($y + $h / 2, 1) }
    probe_min_x = $probeMinX
    background_name = $bgName
    background_layers_bottom_up = $bgLayers
    expected_background = (Composite $bgLayers)
  })
}

# pill / chip: text box is inset 12 px so the probe at chip.x+6 always lands on the fill
function AddChip($key, $orient, $x, $y, $h, $fs, $label, $fill, $textColor, $family, $ls) {
  $tw  = (EstW $label $fs $ls)
  $pad = [Math]::Max(24, [Math]::Round($fs * 0.7))
  $cw  = [Math]::Ceiling($tw * 1.10) + 2 * $pad
  AddRect $x $y $cw $h $fill 14 $null
  $th = [Math]::Round($fs * 1.46, 1)
  AddText $key $orient ($x + 12) ([Math]::Round($y + ($h - $th) / 2, 1)) ($cw - 24) $th $fs $textColor $label $true $family 'CENTER' 1 $ls @($fill) 'primary-chip' $x ($x + 6)
  return $cw
}

# 叠光标记 - 4 components, identical relative geometry and colour order in both orientations
function AddMark($orient, $bx, $by, [double]$s) {
  $w1 = [Math]::Round(88 * $s, 1); $r1 = [Math]::Round(24 * $s, 1)
  $p1 = [Math]::Round(44 * $s, 1); $p2 = [Math]::Round(22 * $s, 1); $p3 = [Math]::Round(88 * $s, 1)
  $d4 = [Math]::Round(30 * $s, 1); $c4x = [Math]::Round(51 * $s, 1); $c4y = [Math]::Round(62 * $s, 1)
  AddRect ($bx)       ($by + $p1) $w1 $w1 $PRIMARY    $r1 $null
  AddRect ($bx + $p1) ($by + $p2) $w1 $w1 $PRIMARY_LT $r1 $null
  AddRect ($bx + $p3) ($by)       $w1 $w1 $ACCENT     $r1 $null
  AddRect ($bx + $c4x) ($by + $c4y) $d4 $d4 $ACCENT ([Math]::Round($d4 / 2, 1)) $null
  $BLOCK.Add([pscustomobject]@{
    key = "$orient-brand-mark"; orient = $orient; round = $Round; kind = 'brand-graphic'
    componentCount = 4; scale = $s
    x = $bx; y = $by; w = [Math]::Round(176 * $s, 1); h = [Math]::Round(132 * $s, 1)
    components = @(
      [pscustomobject]@{ id = 'C1-layer'; local = @(0, 44);  size = @(88, 88); radius = 24; color = "#$PRIMARY" },
      [pscustomobject]@{ id = 'C2-plane'; local = @(44, 22); size = @(88, 88); radius = 24; color = "#$PRIMARY_LT" },
      [pscustomobject]@{ id = 'C3-beam';  local = @(88, 0);  size = @(88, 88); radius = 24; color = "#$ACCENT" },
      [pscustomobject]@{ id = 'C4-core';  local = @(51, 62); size = @(30, 30); radius = 15; color = "#$ACCENT"; shape = 'circle (borderRadius = d/2)' }
    )
  })
}

# =============================================================== PORTRAIT =======
function Build-Portrait {
  $o = 'portrait'; $OX = 88; $OW = 904
  $fsT = $TITLE_FS[$Round]
  $markY = $(if ($Round -eq 1) { 140 } else { 120 })

  AddMark $o $OX $markY 1.0
  AddText "$o-wordmark" $o ($OX + 212) ($markY + 36) 600 60 40 $T1 $WORDMARK $true $FAM_CJK 'LEFT' 1 0 @("$PAGE") 'page' 0 $null

  $ebY = $(if ($Round -eq 1) { 340 } else { 290 })
  [void](AddChip "$o-eyebrow" $o $OX $ebY 56 28 $EYEBROW $PRIMARY $ON_PRIMARY $FAM_LATIN 3)

  if ($Round -eq 1) {
    $titleY = 460; $titleH = 170; $titleLines = 1
    $deckY  = 680
    $divY = 790; $dateY = 850; $spkY = 980
    $spY = 0; $frY = 0; $enY = 0; $urlY = 1110; $bottom = 1156
    $dateFs = 42; $spkFs = 34; $urlFs = 30
  } else {
    $titleY = 370; $titleH = 200; $titleLines = 3
    $deckY  = 600
    $divY = 680; $dateY = 712; $spkY = 800
    $spY = 880; $frY = 950; $urlY = 1046; $bottom = 1092
    $dateFs = 40; $spkFs = 34; $urlFs = 30
    if ($Round -eq 3) { $enY = 1046; $urlY = 1120; $bottom = 1180 }
  }

  # background light band A (round 3 only) is painted BEFORE the title it sits under
  if ($Round -eq 3) { AddRect 64 356 944 310 $BAND_A 24 $null }

  $pageBg = @("$PAGE"); $pageMin = 0
  $titleBg = $pageBg; $titleName = 'page'; $titleMin = $pageMin
  if ($Round -eq 3) { $titleBg = @("$PAGE", $BAND_A_SPEC); $titleName = 'bandA'; $titleMin = 64 }
  AddText "$o-title" $o $OX $titleY $OW $titleH $fsT $T1 $titleText $true $FAM_CJK 'LEFT' $titleLines 0 $titleBg $titleName $titleMin $null

  $deckBg = $pageBg; $deckName = 'page'
  if ($Round -eq 3) { $deckBg = @("$PAGE", $BAND_A_SPEC); $deckName = 'bandA'; $deckMin = 64 }
  else { $deckMin = 0 }
  AddText "$o-deck" $o $OX $deckY $OW 46 30 $T2 $deckText $false $FAM_CJK 'LEFT' 1 0 $deckBg $deckName $deckMin $null

  AddRect $OX $divY $OW 3 $PRIMARY 2 $null
  AddText "$o-date"     $o $OX $dateY $OW 64 $dateFs $T1 $DATE     $true  $FAM_LATIN 'LEFT' 1 0 @("$PAGE") 'page' 0 $null
  AddText "$o-speakers" $o $OX $spkY  $OW 54 $spkFs  $T2 $SPEAKERS $false $FAM_CJK   'LEFT' 1 0 @("$PAGE") 'page' 0 $null

  if ($Round -ge 2) {
    AddText "$o-sponsor" $o $OX $spY $OW 46 28 $T2 $SPONSOR $false $FAM_CJK 'LEFT' 1 0 @("$PAGE") 'page' 0 $null
    [void](AddChip "$o-free" $o $OX $frY 56 28 $FREE $PRIMARY $ON_PRIMARY $FAM_CJK 0)
  }
  if ($Round -eq 3) {
    AddRect 64 1030 944 150 $BAND_B 24 $null
    $enBg = @("$PAGE", $BAND_B_SPEC)
    AddText "$o-english" $o $OX $enY 904 46 28 $T1 $ENGLISH $true  $FAM_LATIN 'LEFT' 1 0 $enBg 'bandB' 64 $null
    AddText "$o-url"     $o $OX $urlY $OW 46 $urlFs $TA $URL $true $FAM_LATIN 'LEFT' 1 0 $enBg 'bandB' 64 $null
  } else {
    AddText "$o-url" $o $OX $urlY $OW 46 $urlFs $TA $URL $true $FAM_LATIN 'LEFT' 1 0 @("$PAGE") 'page' 0 $null
  }
  return @{ top = $markY; bottom = $bottom; width = 1080; height = 1350 }
}

# ==================================================================== WIDE =======
function Build-Wide {
  $o = 'wide'
  $LCX = 96; $LCW = 760
  $PX = 904; $PW = 440; $IX = 940; $IW = 368
  $fsT = $TITLE_FSW[$Round]
  $markY = $(if ($Round -eq 1) { 110 } else { 100 })

  AddMark $o $LCX $markY 0.8
  AddText "$o-wordmark" $o ($LCX + 164) ($markY + 27) 500 52 34 $T1 $WORDMARK $true $FAM_CJK 'LEFT' 1 0 @("$PAGE") 'page' 0 $null

  $ebY = $(if ($Round -eq 1) { 250 } else { 230 })
  [void](AddChip "$o-eyebrow" $o $LCX $ebY 52 26 $EYEBROW $PRIMARY $ON_PRIMARY $FAM_LATIN 3)

  if ($Round -eq 1) {
    $titleY = 340; $titleH = 150; $titleLines = 1; $deckY = 530
    $panelY = 110; $panelH = 560
    $dateY = 170; $spkY = 330
    $spY = 0; $frY = 0; $enY = 0; $urlY = 490; $bottom = 670
    $dateFs = 36; $spkFs = 30; $urlFs = 28
  } else {
    $titleY = 310; $titleH = 180; $titleLines = 3; $deckY = 520
    $panelY = 100; $panelH = 610
    $dateY = 150; $spkY = 250; $spY = 340; $frY = 450; $urlY = 560; $bottom = 710
    $dateFs = 34; $spkFs = 28; $urlFs = 26
    if ($Round -eq 3) { $enY = 552; $urlY = 616 }
  }

  if ($Round -eq 3) { AddRect 72 296 808 300 $BAND_A 24 $null }
  $titleLines1 = $(if ($Round -eq 1) { 1 } else { 3 })
  # round-03: bandA is drawn before the title, so the title really sits on it - declare it
  $wTitleBg = @("$PAGE"); $wTitleName = 'page'; $wTitleMin = 0
  if ($Round -eq 3) { $wTitleBg = @("$PAGE", $BAND_A_SPEC); $wTitleName = 'bandA'; $wTitleMin = 72 }
  AddText "$o-title" $o $LCX $titleY $LCW $titleH $fsT $T1 $titleText $true $FAM_CJK 'LEFT' $titleLines1 0 $wTitleBg $wTitleName $wTitleMin $null

  $deckBg = @("$PAGE"); $deckName = 'page'; $deckMin = 0
  if ($Round -eq 3) { $deckBg = @("$PAGE", $BAND_A_SPEC); $deckName = 'bandA'; $deckMin = 72 }
  AddText "$o-deck" $o $LCX $deckY $LCW 44 28 $T2 $deckText $false $FAM_CJK 'LEFT' 1 0 $deckBg $deckName $deckMin $null

  # right-hand details panel
  AddRect $PX $panelY $PW $panelH $PANEL 24 $null
  $pBg = @("$PANEL")
  AddText "$o-date"     $o $IX $dateY $IW 52 $dateFs $T1 $DATE     $true  $FAM_LATIN 'LEFT' 1 0 $pBg 'panel' $PX $null
  AddText "$o-speakers" $o $IX $spkY  $IW 46 $spkFs  $T2 $SPEAKERS $false $FAM_CJK   'LEFT' 1 0 $pBg 'panel' $PX $null
  if ($Round -ge 2) {
    AddText "$o-sponsor" $o $IX $spY $IW 80 26 $T2 $SPONSOR $false $FAM_CJK 'LEFT' 2 0 $pBg 'panel' $PX $null
    [void](AddChip "$o-free" $o $IX $frY 52 26 $FREE $PRIMARY $ON_PRIMARY $FAM_CJK 0)
  }
  if ($Round -eq 3) {
    AddRect 928 536 392 140 $BAND_B 18 $null
    $enBg = @("$PANEL", $BAND_B_SPEC)
    AddText "$o-english" $o $IX $enY $IW 40 26 $T1 $ENGLISH $true  $FAM_LATIN 'LEFT' 1 0 $enBg 'bandB' 928 $null
    AddText "$o-url"     $o $IX $urlY $IW 40 $urlFs $TA $URL $true $FAM_LATIN 'LEFT' 1 0 $enBg 'bandB' 928 $null
  } else {
    AddText "$o-url" $o $IX $urlY $IW 42 $urlFs $TA $URL $true $FAM_LATIN 'LEFT' 1 0 $pBg 'panel' $PX $null
  }
  return @{ top = $markY; bottom = $bottom; width = 1440; height = 810 }
}

function Wrap([string[]]$inner, $w, $h, $bg) {
  return '<Snapshot type="png" background="#' + $bg + '"><Container width="' + (N $w) + '" height="' + (N $h) +
         '" color="#' + $bg + '"><Stack>' + ($inner -join '') + '</Stack></Container></Snapshot>'
}

# ------------------------------------------------------------------ build -------
$GEO_P = $null; $GEO_W = $null

$DSL.Clear()
$GEO_P = Build-Portrait
$dslPortrait = (Wrap $DSL.ToArray() 1080 1350 $PAGE)

$DSL.Clear()
$GEO_W = Build-Wide
$dslWide = (Wrap $DSL.ToArray() 1440 810 $PAGE)

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $MapPath -Parent) | Out-Null
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $OutDir 'launch-portrait.snapshot'), $dslPortrait, $utf8)
[IO.File]::WriteAllText((Join-Path $OutDir 'launch-wide.snapshot'), $dslWide, $utf8)

# ------------------------------------------------------------ self assertions ---
$problems = New-Object System.Collections.Generic.List[string]

foreach ($d in @($dslPortrait, $dslWide)) {
  if ($d -match '<Image') { $problems.Add('DSL contains <Image - external / whole-image embedding is forbidden') }
  if ($d -notmatch '^<Snapshot type="png"') { $problems.Add('root is not <Snapshot type="png">') }
}
foreach ($b in $BLOCK) {
  if ($b.kind -ne 'text') { continue }
  $need = 24
  if ($b.key -like '*-title') { $need = $MIN_TITLE }
  if ($b.fontSize -lt $need) { $problems.Add(("text '{0}' fontSize {1} < required {2}" -f $b.key, $b.fontSize, $need)) }
}
$must = @($TITLE_R1, $DATE, $EYEBROW, $SPEAKERS, $URL, $WORDMARK, $deckText)
if ($Round -ge 2) { $must += @($TITLE_R23, 'Northstar Research', '云构工具', $FREE) }
if ($Round -eq 3) { $must += @($ENGLISH) }
foreach ($s in $must) {
  if ($dslPortrait -notlike ('*' + (Esc $s) + '*')) { $problems.Add("portrait missing required string: $s") }
  if ($dslWide -notlike ('*' + (Esc $s) + '*'))     { $problems.Add("wide missing required string: $s") }
}
if ($Round -eq 3) {
  foreach ($o in @('portrait', 'wide')) {
    $e = $BLOCK | Where-Object { $_.key -eq "$o-english" }
    $v = $BLOCK | Where-Object { $_.key -eq "$o-url" }
    if ($e.y -ge $v.y) { $problems.Add("$o english line is not above the url") }
  }
}
# reserved top / bottom bands must contain no element at all
$reserved = New-Object System.Collections.Generic.List[object]
foreach ($o in @('portrait', 'wide')) {
  $g = $(if ($o -eq 'portrait') { $GEO_P } else { $GEO_W })
  $reserved.Add([pscustomobject]@{ orient = $o; band = 'top'; rect = @{ x = 0; y = 0; w = $g.width; h = $g.top }; height = $g.top })
  $reserved.Add([pscustomobject]@{ orient = $o; band = 'bottom'; rect = @{ x = 0; y = $g.bottom; w = $g.width; h = ($g.height - $g.bottom) }; height = ($g.height - $g.bottom) })
  foreach ($b in ($BLOCK | Where-Object { $_.orient -eq $o })) {
    if ($b.y -lt $g.top)         { $problems.Add(("{0}: '{1}' y={2} is inside the reserved top band 0..{3}" -f $o, $b.key, $b.y, $g.top)) }
    if (($b.y + $b.h) -gt $g.bottom) { $problems.Add(("{0}: '{1}' bottom={2} is inside the reserved bottom band {3}..{4}" -f $o, $b.key, ($b.y + $b.h), $g.bottom, $g.height)) }
    if ($b.x -lt 0 -or ($b.x + $b.w) -gt $g.width) { $problems.Add(("{0}: '{1}' horizontally out of canvas" -f $o, $b.key)) }
  }
}
foreach ($b in ($BLOCK | Where-Object { $_.kind -eq 'brand-graphic' })) {
  if ($b.componentCount -lt 3 -or $b.componentCount -gt 6) { $problems.Add("$($b.orient) brand mark has $($b.componentCount) components, must be 3..6") }
}
foreach ($b in ($BLOCK | Where-Object { $_.kind -eq 'text' })) {
  if ($b.probe.x -lt $b.probe_min_x) { $problems.Add("$($b.key): probe x=$($b.probe.x) < layer left edge $($b.probe_min_x)") }
  if ($b.probe.x -lt 0 -or $b.probe.x -ge 1600) { $problems.Add("$($b.key): probe off canvas") }
}
if ($problems.Count -gt 0) {
  $i = 0
  foreach ($p in $problems) { $i++; "PROBLEM $i : $p" }
  throw "gen-a21 round $Round produced $($problems.Count) problem(s)"
}

# ------------------------------------------------------------ design-tokens -----
$eyebrowFs = 28; $dateFsTok = $(if ($Round -eq 1) { 42 } else { 40 })
$tokens = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/design-tokens/v1'
  task = 'A21'; round = $Round; generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  brand = [pscustomobject]@{ name_zh = '叠光'; name_en = 'Layerlight'; wordmark = $WORDMARK; event = $EYEBROW; url = $URL }
  color = [pscustomobject]@{
    primary = "#$PRIMARY"; primaryLight = "#$PRIMARY_LT"; accent = "#$ACCENT"
    note = 'primary / primaryLight / accent 三轮完全不变（round-02 明确要求主色不变）'
  }
  theme = [pscustomobject]@{
    name = $THEME
    page = "#$PAGE"; panel = "#$PANEL"
    text_primary = "#$T1"; text_secondary = "#$T2"; text_accent = "#$TA"; on_primary = "#$ON_PRIMARY"
    light_bands = $(if ($Round -eq 3) { [pscustomobject]@{ band_a = "#$BAND_A"; band_b = "#$BAND_B"; alpha_a = $BAND_A_ALPHA; alpha_b = $BAND_B_ALPHA; note = '仅第三轮浅色主题的背景光带，带 alpha；正文对比度按 source-over 合成色计算并在 contrast-audit.json 里与实测像素核对' } } else { $null })
  }
  typography = [pscustomobject]@{
    family_cjk = $FAM_CJK; family_latin = $FAM_LATIN; line_height_ratio = 1.46
    scale = [pscustomobject]@{
      title_portrait = $TITLE_FS[$Round]; title_wide = $TITLE_FSW[$Round]
      deck = 30; eyebrow = $eyebrowFs; date = $dateFsTok; body = 28; meta = 24
    }
    min_title = $MIN_TITLE; min_other = 24
    max_title_lines = $(if ($Round -eq 1) { 1 } else { 3 })
    hierarchy = 'title > deck/date > body > meta，两版与三轮一致'
  }
  brand_graphic = [pscustomobject]@{
    name = '叠光标记 / light-stack mark'
    componentCount = 4
    components = @(
      [pscustomobject]@{ id = 'C1-layer'; shape = 'rounded square 88x88 r24'; color = "#$PRIMARY";    local_offset = @(0, 44) },
      [pscustomobject]@{ id = 'C2-plane'; shape = 'rounded square 88x88 r24'; color = "#$PRIMARY_LT"; local_offset = @(44, 22) },
      [pscustomobject]@{ id = 'C3-beam';  shape = 'rounded square 88x88 r24'; color = "#$ACCENT";    local_offset = @(88, 0) },
      [pscustomobject]@{ id = 'C4-core';  shape = 'circle d30 (borderRadius=d/2)'; color = "#$ACCENT"; local_offset = @(51, 62) }
    )
    invariants = '4 个构件的相对几何、叠压顺序与颜色三轮不变；竖版 scale=1.0 (176x132)、横版 scale=0.8 (140.8x105.6)，只整体缩放与改位置；装饰可移动缩放但形态不变'
    used_in = @('round-01', 'round-02', 'round-03', 'portrait', 'wide')
  }
  layout = [pscustomobject]@{
    portrait = [pscustomobject]@{ width = 1080; height = 1350; margin_x = 88; content_width = 904; reserved_top_h = $GEO_P.top; reserved_bottom_from_y = $GEO_P.bottom; reserved_bottom_h = ($GEO_P.height - $GEO_P.bottom) }
    wide     = [pscustomobject]@{ width = 1440; height = 810; margin_x = 96; left_column_w = 760; panel_x = 904; panel_w = 440; reserved_top_h = $GEO_W.top; reserved_bottom_from_y = $GEO_W.bottom; reserved_bottom_h = ($GEO_W.height - $GEO_W.bottom) }
    reserved_note = '顶部与底部条带内不出现任何元素，也不写待添加占位文字；生成器逐块断言'
  }
}
[IO.File]::WriteAllText((Join-Path $OutDir 'design-tokens.json'), (($tokens | ConvertTo-Json -Depth 10) + "`n"), $utf8)

# ------------------------------------------------------------ content-map -------
$reqRows = New-Object System.Collections.Generic.List[object]
function Req($id, $zh, $val, $r1, $r2, $r3, $where) {
  $present = @{}
  $present['round-01'] = [bool]$r1; $present['round-02'] = [bool]$r2; $present['round-03'] = [bool]$r3
  $script:reqRows.Add([pscustomobject]@{
    id = $id; label = $zh; value = $val
    required_from_round = $(if ($r1) { 1 } elseif ($r2) { 2 } else { 3 })
    present_in_rounds = $present
    appears_in = $where
  })
}
Req 'headline'  '主标题/核心句' $TITLE_R1  $true  $true  $true  'round-01 作主标题独立成行；round-02/03 收进长标题，同时以副标题独立成行'
Req 'long-title' '第二轮起的长标题' $TITLE_R23 $false $true $true 'round-02/03 主标题（独立 text 节点，maxLines=3）'
Req 'date-time' '日期时间'      $DATE     $true  $true  $true  '竖版正文区 / 横版右侧面板'
Req 'eyebrow'   '活动形式'      $EYEBROW  $true  $true  $true  '两版左上主色胶囊'
Req 'speakers'  '讲者'          $SPEAKERS $true  $true  $true  '竖版正文区 / 横版右侧面板'
Req 'url'       '网址'          $URL      $true  $true  $true  '竖版底部 / 横版右侧面板底部'
Req 'wordmark'  '品牌字标'      $WORDMARK $true  $true  $true  '叠光标记右侧'
Req 'deck'      '副标题'        $deckText $true  $true  $true  '主标题下方'
if ($Round -ge 2) {
  Req 'sponsors' '赞助方'       $SPONSOR $false $true $true '赞助方行'
  Req 'free'     '参加方式'     $FREE    $false $true $true '赞助方下方主色胶囊'
}
if ($Round -eq 3) { Req 'english' '英文短句' $ENGLISH $false $false $true '网址正上方（第三轮新增）' }

$mustIds = @('headline', 'date-time', 'eyebrow', 'speakers', 'url', 'wordmark', 'deck')
if ($Round -ge 2) { $mustIds += @('long-title', 'sponsors', 'free') }
if ($Round -eq 3) { $mustIds += @('english') }

$cmap = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/content-map/v1'
  task = 'A21'; round = $Round; generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  mode = '连续三轮预置需求自动执行：round-01 为本题首轮需求，rounds/round-02.md 与 rounds/round-03.md 是本题自带的后续轮文件，已在本轮之前实际读取并按顺序执行，不等待外部反馈'
  deliverables = [pscustomobject]@{
    portrait = "round-0$Round/launch-portrait.png + .snapshot (1080x1350)"
    wide     = "round-0$Round/launch-wide.png + .snapshot (1440x810)"
  }
  required_ids_for_this_round = $mustIds
  items = $reqRows.ToArray()
  per_image = [pscustomobject]@{
    'launch-portrait' = [pscustomobject]@{ width = 1080; height = 1350; composition = '单列纵向排版：左对齐，叠光标记在左上，主张自上而下堆叠，底部留白' }
    'launch-wide'     = [pscustomobject]@{ width = 1440; height = 810;   composition = '左右双栏：左栏为品牌与主张，右栏为信息面板，两栏各自纵向排布' }
  }
  shared = [pscustomobject]@{
    primary_color = "#$PRIMARY"
    type_hierarchy = 'title > deck/date > body > meta'
    brand_graphic = '叠光标记 4 构件，两版与三轮相对几何/颜色/叠压顺序一致'
    separate_composition = $true
  }
  forbidden = @('整图嵌入', '外部图片 <Image>', '变形压窄文字', '待添加占位文字')
}
[IO.File]::WriteAllText((Join-Path $OutDir 'content-map.json'), (($cmap | ConvertTo-Json -Depth 8) + "`n"), $utf8)

# --------------------------------------------------------------- layout map -----
$lmap = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/a21-layout-map/v1'
  task = 'A21'; round = $Round; generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  notes = 'probe 是对比度采样点，位于文本框左缘外 6px（胶囊内则落在胶囊左缘内 6px），落在与文字同层的实际背景上，不会采到字形。background_layers_bottom_up 是自底向上的叠层，expected_background 是按 #RRGGBBAA source-over 合成的预期色；round-03 的 contrast-audit.json 会用渲染像素逐条核对它，任何“只改两个颜色忽略叠层”的偏差都会被判失败。'
  reserved_bands = $reserved.ToArray()
  blocks = $BLOCK.ToArray()
}
[IO.File]::WriteAllText($MapPath, (($lmap | ConvertTo-Json -Depth 10) + "`n"), $utf8)

# -------------------------------------------------------------------- report ----
"round $Round"
"  portrait -> $(Join-Path $OutDir 'launch-portrait.snapshot')  $((Get-Item (Join-Path $OutDir 'launch-portrait.snapshot')).Length) bytes"
"  wide     -> $(Join-Path $OutDir 'launch-wide.snapshot')  $((Get-Item (Join-Path $OutDir 'launch-wide.snapshot')).Length) bytes"
"  blocks   = $($BLOCK.Count)   texts = $(@($BLOCK | Where-Object { $_.kind -eq 'text' }).Count)   marks = $(@($BLOCK | Where-Object { $_.kind -eq 'brand-graphic' }).Count)"
"  theme    = $THEME   page #$PAGE   title fs portrait=$($TITLE_FS[$Round]) wide=$($TITLE_FSW[$Round]) (min $MIN_TITLE)"
"  reserved portrait top=0..$($GEO_P.top) bottom=$($GEO_P.bottom)..1350   wide top=0..$($GEO_W.top) bottom=$($GEO_W.bottom)..810"
"  problems = 0"
foreach ($b in ($BLOCK | Where-Object { $_.kind -eq 'text' })) {
  '  [{0,-9}] {1,-10} fs={2,-3} at ({3},{4}) {5}x{6}  bg={7} (#{8})  probe=({9},{10})' -f `
    $b.orient, $b.key.Replace(($b.orient + '-'), ''), $b.fontSize, $b.x, $b.y, $b.w, $b.h, $b.background_name, $b.expected_background, $b.probe.x, $b.probe.y
}
