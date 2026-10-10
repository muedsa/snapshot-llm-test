# A15 - emit the Snapshot DSL for the dashboard reconstruction.
# The reference PNG is NEVER read here; all geometry comes from measurement
# results recorded in this script's element table (see probe-ref*.ps1).
param([int]$V = 1, [switch]$ResetOnly)

$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A15'
$CONTENT = Join-Path $ROOT 'tasks\A15-reference-reconstruction\inputs\content.json'
$c = [IO.File]::ReadAllText($CONTENT) | ConvertFrom-Json

# ---------------------------------------------------------------- palette --
$SIDEBAR = '#14233C'; $SIDECARD = '#233954'; $PILLNAV = '#294467'
$BG      = '#F3F6FB'; $CARD      = '#FFFFFF'; $BORDER  = '#E2E8F1'
$INK     = '#18283F'; $MUTED     = '#63748F'; $ACCENT  = '#245CE4'
$GREEN   = '#168267'; $MINT      = '#64DBB6'; $DOTIDLE = '#7791B3'
$NAVLBL  = '#BECADD'; $SIDE3     = '#B8CADD'; $FOOT    = '#7B8BA3'
$SEP     = '#EBEFF5'; $GRID      = '#E7EDF5'
$PILLBG0 = '#E7EFFF'; $PILLBG1 = '#FFF3D7'; $PILLBG2 = '#DCF5EC'
$PILLTX0 = '#245CE4'; $PILLTX1 = '#9D6613'; $PILLTX2 = '#168267'
$DOT0    = '#EAAF40'; $DOT1    = '#245CE4'; $DOT2   = '#168267'
$FAM     = 'Inter,Noto Sans CJK SC'

# ---------------------------------------------------------------- helpers --
function N([double]$v) { return $v.ToString('0.##', [cultureinfo]::InvariantCulture) }
function Esc([string]$s) {
  $s = $s.Replace('&', '&amp;'); $s = $s.Replace('<', '&lt;'); $s = $s.Replace('>', '&gt;')
  return $s
}
function RectXml($r) {
  $p = 'left="' + (N $r.x) + '" top="' + (N $r.y) + '" width="' + (N $r.w) + '" height="' + (N $r.h) + '"'
  $d = '<Container color="' + $r.color + '"'
  if ($r.border) { $d += ' border="' + $r.border + '"' }
  if ($r.rTL) { $d += ' borderRadiusTopLeft="' + (N $r.rTL) + '"' }
  if ($r.rTR) { $d += ' borderRadiusTopRight="' + (N $r.rTR) + '"' }
  if ($r.rBL) { $d += ' borderRadiusBottomLeft="' + (N $r.rBL) + '"' }
  if ($r.rBR) { $d += ' borderRadiusBottomRight="' + (N $r.rBR) + '"' }
  if ($r.r)   { $d += ' borderRadius="' + (N $r.r) + '"' }
  $d += '/>'
  return '      <Positioned ' + $p + '>' + $d + '</Positioned>'
}
function Card($id, $x, $y, $w, $h) {
  return [ordered]@{ id = $id; x = $x; y = $y; w = $w; h = $h; color = $CARD; border = '1 SOLID ' + $BORDER; r = 10 }
}

# ------------------------------------------------------------------ rects --
$BARS_X = @(357, 458, 559, 660, 761, 862)
$BARS_T = @(484, 462, 473, 441, 452, 419)
$BARS_H = @(65, 87, 76, 108, 97, 130)

$RECTS = @(
  [ordered]@{ id = 'sidebar';   x = 0;    y = 0;   w = 220;  h = 900; color = $SIDEBAR },
  [ordered]@{ id = 'logoOut';   x = 30;   y = 33;  w = 28;   h = 28;  color = $MINT;   r = 8 },
  [ordered]@{ id = 'logoIn';    x = 37;   y = 40;  w = 12;   h = 12;  color = $SIDEBAR; r = 3 },
  [ordered]@{ id = 'navPill';   x = 18;   y = 116; w = 184;  h = 48;  color = $PILLNAV; r = 7 },
  [ordered]@{ id = 'navDot0';   x = 34;   y = 128; w = 12;   h = 12;  color = $MINT;    r = 6 },
  [ordered]@{ id = 'navDot1';   x = 34;   y = 192; w = 12;   h = 12;  color = $DOTIDLE; r = 6 },
  [ordered]@{ id = 'navDot2';   x = 34;   y = 256; w = 12;   h = 12;  color = $DOTIDLE; r = 6 },
  [ordered]@{ id = 'navDot3';   x = 34;   y = 320; w = 12;   h = 12;  color = $DOTIDLE; r = 6 },
  [ordered]@{ id = 'sideCard';  x = 22;   y = 752; w = 176;  h = 116; color = $SIDECARD; r = 10 },
  [ordered]@{ id = 'button';    x = 1184; y = 43;  w = 216;  h = 48;  color = $ACCENT;  r = 8 },
  [ordered]@{ id = 'kpi1';      x = 260;  y = 138; w = 356;  h = 144; color = $CARD; border = ('1 SOLID ' + $BORDER); r = 10 },
  [ordered]@{ id = 'kpi2';      x = 644;  y = 138; w = 356;  h = 144; color = $CARD; border = ('1 SOLID ' + $BORDER); r = 10 },
  [ordered]@{ id = 'kpi3';      x = 1028; y = 138; w = 356;  h = 144; color = $CARD; border = ('1 SOLID ' + $BORDER); r = 10 },
  [ordered]@{ id = 'chartCard'; x = 260;  y = 310; w = 742;  h = 286; color = $CARD; border = ('1 SOLID ' + $BORDER); r = 10 },
  [ordered]@{ id = 'actCard';   x = 1030; y = 310; w = 370;  h = 286; color = $CARD; border = ('1 SOLID ' + $BORDER); r = 10 },
  [ordered]@{ id = 'tableCard'; x = 260;  y = 624; w = 1140; h = 218; color = $CARD; border = ('1 SOLID ' + $BORDER); r = 10 }
)
# gridlines (zero line last, same colour as the rest in the reference)
foreach ($gy in @(405, 441, 477, 513, 549)) {
  $RECTS += [ordered]@{ id = ('grid' + $gy); x = 333; y = $gy; w = 637; h = 1; color = $GRID }
}
# bars - heights follow the content values at the measured 1.2 px / unit scale
for ($i = 0; $i -lt 6; $i++) {
  $RECTS += [ordered]@{ id = ('bar' + $i); x = $BARS_X[$i]; y = $BARS_T[$i]; w = 54; h = $BARS_H[$i]; color = $ACCENT; rTL = 4; rTR = 4; rBL = 0; rBR = 0 }
}
$RECTS += [ordered]@{ id = 'headBand'; x = 284; y = 688; w = 1090; h = 34; color = $BG }
$RECTS += [ordered]@{ id = 'sep1'; x = 284; y = 760; w = 1090; h = 1; color = $SEP }
$RECTS += [ordered]@{ id = 'sep2'; x = 284; y = 795; w = 1090; h = 1; color = $SEP }
$RECTS += [ordered]@{ id = 'pill0'; x = 1028; y = 729; w = 148; h = 28; color = $PILLBG0; r = 7 }
$RECTS += [ordered]@{ id = 'pill1'; x = 1028; y = 764; w = 148; h = 28; color = $PILLBG1; r = 7 }
$RECTS += [ordered]@{ id = 'pill2'; x = 1028; y = 799; w = 148; h = 28; color = $PILLBG2; r = 7 }
$RECTS += [ordered]@{ id = 'actDot0'; x = 1054; y = 397; w = 10; h = 10; color = $DOT0; r = 5 }
$RECTS += [ordered]@{ id = 'actDot1'; x = 1054; y = 457; w = 10; h = 10; color = $DOT1; r = 5 }
$RECTS += [ordered]@{ id = 'actDot2'; x = 1054; y = 517; w = 10; h = 10; color = $DOT2; r = 5 }

# ------------------------------------------------------------------ texts --
# id | source | colour | size | style | tracking | reference ink box | mode
$T = @()
function AddT($id, $text, $color, $fs, $style, $ls, $rx, $ry, $rw, $rh, $mode) {
  $script:T += [ordered]@{ id = $id; text = $text; color = $color; fs = $fs; style = $style; ls = $ls; rx = $rx; ry = $ry; rw = $rw; rh = $rh; mode = $mode }
}

AddT 'brand'   $c.brand                      '#FFFFFF' 18 BOLD 0.75 73 38 116 15 'light'
AddT 'nav0'    $c.navigation[0]              '#FFFFFF' 19 BOLD 0 63 126 87 16 'light'
AddT 'nav1'    $c.navigation[1]              $NAVLBL  19 NORMAL 0 63 191 72 18 'light'
AddT 'nav2'    $c.navigation[2]              $NAVLBL  19 NORMAL 0 63 255 81 18 'light'
AddT 'nav3'    $c.navigation[3]              $NAVLBL  19 NORMAL 0 63 319 73 18 'light'
AddT 'sideL1'  $c.workspace_info[0]          $MINT    13 BOLD   0 39 770 112 10 'light'
AddT 'sideL2'  $c.workspace_info[1]          '#FFFFFF' 16 NORMAL 0 41 804 134 13 'light'
AddT 'sideL3'  $c.workspace_info[2]          $SIDE3   14.2 NORMAL 0 39 836 122 13 'light'

AddT 'title'   $c.title                      $INK     32.1 BOLD   0 261 39 333 30 'dark'
AddT 'subtitle' $c.subtitle                  $MUTED   18 NORMAL 0 261 86 246 17 'dark'
AddT 'btnLbl'  $c.button                     '#FFFFFF' 17 BOLD 0 1237 56 110 15 'light'

$kx = @(285, 669, 1053)
for ($i = 0; $i -lt 3; $i++) {
  AddT ('k' + ($i + 1) + 'lab') $c.kpis[$i].label $MUTED 13.6 BOLD 0 $kx[$i] 161 64 10 'dark'
}
$kvw = @(147, 59, 73); $kvx = @(285, 670, 1054); $kvy = @(200, 200, 199); $kvh = @(28, 23, 25)
for ($i = 0; $i -lt 3; $i++) {
  AddT ('k' + ($i + 1) + 'val') $c.kpis[$i].value $INK 32 BOLD 0 $kvx[$i] $kvy[$i] $kvw[$i] $kvh[$i] 'dark'
}
$kcw = @(56, 45, 59); $kch = @(12, 12, 15)
for ($i = 0; $i -lt 3; $i++) {
  AddT ('k' + ($i + 1) + 'chg') $c.kpis[$i].change $GREEN 16 BOLD 0 $kx[$i] 246 $kcw[$i] $kch[$i] 'dark'
}

AddT 'cTitle'  $c.chart_title                $INK     22 BOLD   0 286 336 128 16 'dark'
AddT 'cPeriod' $c.chart_period               $MUTED   17 NORMAL 0 897 338 76 15 'dark'
AddT 'cUnit'   $c.chart_unit                 $MUTED   13 NORMAL 0 288 376 68 9  'dark'

$tkx = @(300, 306, 306, 306, 314); $tky = @(399, 435, 471, 507, 543); $tkw = @(20, 14, 14, 14, 6)
$tkv = @('120', '90', '60', '30', '0')
for ($i = 0; $i -lt 5; $i++) {
  AddT ('tick' + $i) $tkv[$i] $MUTED 13 NORMAL 0 $tkx[$i] $tky[$i] $tkw[$i] 9 'dark'
}

$mx = @(373, 473, 575, 678, 776, 877); $mw = @(22, 25, 22, 18, 23, 24); $mh = @(13, 13, 10, 10, 13, 13)
for ($i = 0; $i -lt 6; $i++) {
  AddT ('m' + $i) $c.months[$i] $MUTED 14 NORMAL 0 $mx[$i] 561 $mw[$i] $mh[$i] 'dark'
}

AddT 'aTitle'  $c.activity_title             $INK     22 BOLD   0 1055 335 144 21 'dark'
$aw = @(117, 139, 141); $ah = @(17, 15, 15); $ay = @(395, 456, 516); $aty = @(423, 483, 543)
$atw = @(38, 35, 35)
for ($i = 0; $i -lt 3; $i++) {
  AddT ('a' + $i)     $c.activity[$i][0] $INK   17.3 BOLD 0 1078 $ay[$i]  $aw[$i] $ah[$i] 'dark'
  AddT ('a' + $i + 't') $c.activity[$i][1] $MUTED 14 NORMAL 0 1078 $aty[$i] $atw[$i] 10 'dark'
}

AddT 'tTitle'  $c.table_title                $INK     22 BOLD   0 286 645 167 21 'dark'
$hx = @(299, 783, 1034, 1231); $hw = @(54, 43, 46, 24)
for ($i = 0; $i -lt 4; $i++) {
  AddT ('h' + $i) $c.table_columns[$i] $MUTED 12 BOLD 0 $hx[$i] 699 $hw[$i] 9 'dark'
}
$rx = @(299, 783, 1231); $py = @(735, 770, 805)
$pw = @(161, 141, 109); $ph = @(15, 14, 14)
$ow = @(73, 62, 50);    $dw = @(54, 47, 50)
for ($i = 0; $i -lt 3; $i++) {
  AddT ('p' + $i) $c.rows[$i][0] $INK   16 BOLD 0 $rx[0] $py[$i] $pw[$i] $ph[$i] 'dark'
  AddT ('o' + $i) $c.rows[$i][1] $MUTED 16 NORMAL 0 $rx[1] $py[$i] $ow[$i] 12 'dark'
  AddT ('d' + $i) $c.rows[$i][3] $MUTED 16 NORMAL 0 $rx[2] $py[$i] $dw[$i] 12 'dark'
}
$sx = @(1067, 1079, 1086); $sy = @(736, 771, 806); $sw = @(70, 47, 32); $sh = @(13, 10, 10)
$sc = @($PILLTX0, $PILLTX1, $PILLTX2)
for ($i = 0; $i -lt 3; $i++) {
  AddT ('s' + $i) $c.rows[$i][2] $sc[$i] 13 BOLD 0 $sx[$i] $sy[$i] $sw[$i] $sh[$i] 'dark'
}

AddT 'footer'  $c.footer                     $FOOT    13 NORMAL 0 261 867 255 13 'dark'

# Per-element font family overrides (the default is $FAM for every run).
$FAMBYID = @{ brand = 'Inter Extra Bold' }
foreach ($e in $T) {
  if ($FAMBYID.ContainsKey($e.id)) { $e['fam'] = $FAMBYID[$e.id] } else { $e['fam'] = $FAM }
}

# -------------------------------------------------------------- placement --
$plPath = Join-Path $TMP 'placement.json'
$created = $false
if (Test-Path $plPath) {
  $PL = [IO.File]::ReadAllText($plPath) | ConvertFrom-Json
} else {
  $PL = New-Object psobject
  foreach ($e in $T) {
    $top = [math]::Round($e.ry - (0.23 * $e.fs), 1)
    $o = [ordered]@{ left = [double]$e.rx; top = $top; fs = [double]$e.fs; lr = 0.0; off = [math]::Round(0.23 * $e.fs, 2) }
    $PL | Add-Member -NotePropertyName $e.id -NotePropertyValue ([pscustomobject]$o)
  }
  $created = $true
}

# ------------------------------------------------------------------- emit --
$lines = @()
$lines += '<Snapshot type="png" background="' + $BG + '">'
$lines += '  <Container width="1440" height="900" color="' + $BG + '">'
$lines += '    <Stack>'
foreach ($r in $RECTS) { $lines += (RectXml $r) }
foreach ($e in $T) {
  $p = $PL.PSObject.Properties[$e.id].Value
  $a = 'color="' + $e.color + '" fontSize="' + (N $p.fs) + '" fontFamily="' + $e.fam + '"'
  if ($e.style -ne 'NORMAL') { $a += ' fontStyle="' + $e.style + '"' }
  if ($e.ls -ne 0) { $a += ' letterSpacing="' + (N $e.ls) + '"' }
  $lines += '      <Positioned left="' + (N $p.left) + '" top="' + (N $p.top) + '"><Text ' + $a + '>' + (Esc $e.text) + '</Text></Positioned>'
}
$lines += '    </Stack>'
$lines += '  </Container>'
$lines += '</Snapshot>'

$xml = ($lines -join "`n") + "`n"
$out = Join-Path $TMP ('reconstructed-v{0:d2}.snapshot' -f $V)
if (-not $ResetOnly) {
  [IO.File]::WriteAllText($out, $xml, (New-Object Text.UTF8Encoding($false)))
}

if ($created) {
  [IO.File]::WriteAllText($plPath, ($PL | ConvertTo-Json -Depth 6), (New-Object Text.UTF8Encoding($false)))
}

# element table kept next to the generator so compare.ps1 can reuse it
$tbl = @{ texts = $T; rects = @($RECTS | ForEach-Object { $_ }) }
[IO.File]::WriteAllText((Join-Path $TMP 'elements.json'), ($tbl | ConvertTo-Json -Depth 8), (New-Object Text.UTF8Encoding($false)))

if ($ResetOnly) {
  Write-Output ("reset placement.json only ({0} texts, no DSL written)" -f $T.Count)
} else {
  Write-Output ("wrote {0}  ({1} rects, {2} texts)" -f $out, $RECTS.Count, $T.Count)
}
