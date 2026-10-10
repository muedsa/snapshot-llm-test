# A08 DSL generator - builds wayfinding-v<Ver>.snapshot from floor.txt + paths.json
param([string]$Ver = '01')
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$T    = "$root\tmp\$RUN\A08"
$O    = "$root\outputs\$RUN\A08"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$CI   = [System.Globalization.CultureInfo]::InvariantCulture

# ------------------------------------------------------------------ layout --
$CELL = 44; $GX = 48; $GY = 116; $COLS = 26; $ROWS = 18
$CW = 1560; $CH = 1080
$GW = $COLS * $CELL          # 1144
$GH = $ROWS * $CELL          # 792
$R1W = 10                    # route 1 stroke
$R2W = 6                     # route 2 stroke (sits inside route 1 on overlap)
$DASH = 16; $GAP = 12; $PERIOD = $DASH + $GAP
$ARML = 10; $ARMT = 4

# ------------------------------------------------------------------ colours --
$BG='#0B1220'; $PANEL='#111A2B'; $PBD='#24304A'
$FLOOR='#101A2E'; $FLINE='#1D2A44'; $WALLC='#3E4C66'
$DOORC='#22314F'; $DOORB='#FBBF24'
$TX='#F8FAFC'; $SUB='#A8BCD8'; $MUTE='#7288A8'
$C1='#F43F5E'; $C2='#38BDF8'
$SFILL='#0F3A2E'; $SF='#34D399'
$EFILL='#3A2C0F'; $EF='#FBBF24'
$ZFILL='#232B55'; $ZF='#818CF8'
$FONT='Inter,Noto Sans CJK SC'

# ----------------------------------------------------------------- helpers --
$sb = New-Object System.Text.StringBuilder
function L([string]$s) { [void]$script:sb.Append($s).Append("`n") }
function F($n) {
  if ($null -eq $n) { return '0' }
  $d = [double]$n
  if ($d -eq [math]::Floor($d)) { return $d.ToString('0', $CI) }
  return $d.ToString('0.##', $CI)
}
function X([string]$s) {
  return $s.Replace('&','&amp;').Replace('<','&lt;').Replace('>','&gt;')
}
# conservative text width estimate (over-estimates rather than under-estimates)
function EW([string]$t, [double]$fs) {
  $w = 0.0
  foreach ($ch in $t.ToCharArray()) {
    $o = [int]$ch
    if ($o -ge 0x1100) { $w += $fs }                                   # CJK / fullwidth / arrows / box drawing
    elseif ($o -ge 0xFF01 -and $o -le 0xFF60) { $w += $fs }            # fullwidth forms
    else { $w += $fs * 0.55 }
  }
  return $w
}
function Txt($left, $top, $fs, $color, [string]$text, [bool]$bold = $false) {
  $b = ''
  if ($bold) { $b = ' fontStyle="BOLD"' }
  L ("      <Positioned left=""$(F $left)"" top=""$(F $top)""><Text fontSize=""$(F $fs)"" height=""1.0"" fontFamily=""$FONT"" color=""$color""$b>" + (X $text) + '</Text></Positioned>')
}
function TxtW($left, $top, $fs, $color, [string]$text, $width, [string]$align, [bool]$bold = $false) {
  $b = ''
  if ($bold) { $b = ' fontStyle="BOLD"' }
  L ("      <Positioned left=""$(F $left)"" top=""$(F $top)"" width=""$(F $width)"" height=""$(F $fs)""><Text fontSize=""$(F $fs)"" height=""1.0"" fontFamily=""$FONT"" color=""$color"" textAlign=""$align""$b>" + (X $text) + '</Text></Positioned>')
}
function Rect($left, $top, $w, $h, $color, [string]$border = '', [string]$radius = '') {
  $a = ''
  if ($border) { $a += " border=`"$border`"" }
  if ($radius) { $a += " borderRadius=`"$radius`"" }
  L ("      <Positioned left=""$(F $left)"" top=""$(F $top)"" width=""$(F $w)"" height=""$(F $h)""><Container width=""$(F $w)"" height=""$(F $h)"" color=""$color""$a/></Positioned>")
}
function SegRot($x1, $y1, $x2, $y2, $th, $color) {
  $dx = [double]$x2 - [double]$x1; $dy = [double]$y2 - [double]$y1
  $len = [math]::Sqrt($dx * $dx + $dy * $dy)
  if ($len -lt 0.5) { return }
  $c  = [math]::Round($dx / $len, 6)
  $s  = [math]::Round($dy / $len, 6)
  $ns = [math]::Round(-$s, 6)
  $m  = "($c,$s,0,0,$ns,$c,0,0,0,0,1,0,0,0,0,1)"
  L ("      <Positioned left=""$(F $x1)"" top=""$(F ($y1 - $th / 2))"">")
  L ("        <Transform matrix=""$m"" origin=""(0,$(F ($th / 2)))"">")
  L ("          <Container width=""$(F $len)"" height=""$(F $th)"" color=""$color""/>")
  L ('        </Transform>')
  L ('      </Positioned>')
}
# chevron arrow head: tip at (px,py) travelling along (ux,uy)
function Arrow($px, $py, $ux, $uy, $color) {
  $bx = -$ux; $by = -$uy
  $nx = -$uy; $ny = $ux
  $k = [math]::Sqrt(0.5)
  $a1x = ($bx + $nx) * $k * $ARML; $a1y = ($by + $ny) * $k * $ARML
  $a2x = ($bx - $nx) * $k * $ARML; $a2y = ($by - $ny) * $k * $ARML
  SegRot $px $py ($px + $a1x) ($py + $a1y) $ARMT $color
  SegRot $px $py ($px + $a2x) ($py + $a2y) $ARMT $color
}
function CX([int]$x) { return $GX + $x * $CELL + $CELL / 2 }
function CY([int]$y) { return $GY + $y * $CELL + $CELL / 2 }

# ------------------------------------------------------------------- inputs --
$raw  = [System.IO.File]::ReadAllLines("$T\floor.txt")
if ($raw.Count -ne $ROWS) { throw "floor rows $($raw.Count)" }
$j    = Get-Content "$O\paths.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$mk   = $j.markers
$doors = @()
foreach ($d in $j.connectivity.doorway_cells) { $doors += ,@([int]$d[0], [int]$d[1]) }
$doorSet = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($d in $doors) { [void]$doorSet.Add("$($d[0]),$($d[1])") }

$wallRuns = @()
for ($y = 0; $y -lt $ROWS; $y++) {
  $x = 0
  while ($x -lt $COLS) {
    if ($raw[$y][$x] -eq '#') {
      $x0 = $x
      while ($x -lt $COLS -and $raw[$y][$x] -eq '#') { $x++ }
      $wallRuns += ,@($x0, $y, ($x - $x0))
    } else { $x++ }
  }
}

# -------------------------------------------------------------------- build --
L ('<Snapshot type="png" background="' + $BG + '">')
L ('  <Container width="' + $CW + '" height="' + $CH + '">')
L ('    <Stack>')

# ---- header
Txt 40 14 40 $TX '展馆网格导览 · 两条最短可走路线' $true
Txt 40 62 22 $SUB '26 × 18 格 · 每格 2 米 · 仅上下左右跨格 · 坐标 (x,y) 从 0 起'

# ---- sidebar
Rect 1214 88 346 992 $PANEL "1 SOLID $PBD" '12'
Txt 1238 110 26 $TX '图例' $true
$lg = @(
  @('wall',  $WALLC, '',                     '墙体 # · 不可走'),
  @('floor', $FLOOR, "1 SOLID $FLINE",       '可走格 . · 每格 2 米'),
  @('door',  $DOORC, "1 SOLID $DOORB",       '门洞 · 单格通行'),
  @('S',     $SFILL, "2 SOLID $SF",          '入口 S (2,2)'),
  @('E',     $EFILL, "2 SOLID $EF",          '出口 E (23,15)'),
  @('zone',  $ZFILL, "2 SOLID $ZF",          '展区 A/B/C/D')
)
$yy = 156
foreach ($r in $lg) {
  Rect 1238 ($yy - 2) 26 26 $r[1] $r[2] '4'
  Txt 1274 $yy 22 $SUB $r[3]
  $yy += 42
}
# route 1 sample: solid bar
Rect 1238 ($yy - 5) 26 8 $C1 '' '3'
Txt 1274 $yy 22 $SUB '路线一 S→E 实线'
$yy += 42
# route 2 sample: two dashes
Rect 1238 ($yy - 5) 11 8 $C2 '' '3'
Rect 1253 ($yy - 5) 11 8 $C2 '' '3'
Txt 1274 $yy 22 $SUB '路线二 S→B→D→E 虚线'
$yy += 42

Txt 1238 500 26 $TX '两条路线' $true
Txt 1238 542 22 $SUB '路线二须先 B 后 D，'
Txt 1238 568 22 $SUB '每一段都取最短路。'
Txt 1238 594 22 $SUB '重合处：虚线叠在实线上'
Txt 1238 620 22 $SUB '两种线型都能追踪。'

Txt 1238 650 26 $TX '移动与计步' $true
Txt 1238 692 22 $SUB '只能上下左右跨格，'
Txt 1238 720 22 $SUB '不能斜穿或穿墙。'
Txt 1238 748 22 $SUB '门洞按原格通行，'
Txt 1238 776 22 $SUB '不加宽、不新增开口。'
Txt 1238 804 22 $SUB '步数 = 格间移动次数；'
Txt 1238 832 22 $SUB '米数 = 步数 × 2。'

Txt 1238 884 26 $TX '尺度' $true
for ($i = 0; $i -lt 5; $i++) {
  $c = if ($i % 2 -eq 0) { $SUB } else { '#3B4A66' }
  Rect (1238 + $i * 44) 928 44 12 $c
}
for ($i = 0; $i -le 5; $i++) {
  $tx0 = 1238 + $i * 44
  if ($i -eq 5) { $tx0 = $tx0 - 1 }
  Rect $tx0 918 1 10 $MUTE
}
Rect 1238 928 220 1 $MUTE
Rect 1238 939 220 1 $MUTE
Rect 1238 928 1 12 $MUTE
Rect 1457 928 1 12 $MUTE
Txt 1238 946 22 $MUTE '0'
TxtW 1338 946 22 $MUTE '10 米' 120 'END'
Txt 1238 1000 22 $MUTE ("可走格 {0} · 墙格 {1}" -f $j.grid.walkable_cells, $j.grid.wall_cells)
Txt 1238 1024 22 $MUTE ("单一连通分量 · {0} 处门洞" -f $j.connectivity.doorway_count)

# ---- grid: floor plate, lattice, walls, doorways, markers
Rect $GX $GY $GW $GH $FLOOR '1 SOLID #2E3E5C'
for ($i = 1; $i -lt $COLS; $i++) { Rect ($GX + $i * $CELL) $GY 1 $GH $FLINE }
for ($j2 = 1; $j2 -lt $ROWS; $j2++) { Rect $GX ($GY + $j2 * $CELL) $GW 1 $FLINE }
foreach ($r in $wallRuns) {
  Rect ($GX + $r[0] * $CELL) ($GY + $r[1] * $CELL) ($r[2] * $CELL) $CELL $WALLC
}
foreach ($d in $doors) {
  Rect ($GX + $d[0] * $CELL) ($GY + $d[1] * $CELL) $CELL $CELL $DOORC "1 SOLID $DOORB"
}
$mdefs = [ordered]@{
  'S' = @($SFILL, "2 SOLID $SF", 'S')
  'E' = @($EFILL, "2 SOLID $EF", 'E')
  'A' = @($ZFILL, "2 SOLID $ZF", 'A')
  'B' = @($ZFILL, "2 SOLID $ZF", 'B')
  'C' = @($ZFILL, "2 SOLID $ZF", 'C')
  'D' = @($ZFILL, "2 SOLID $ZF", 'D')
}
foreach ($k in $mdefs.Keys) {
  $p = $mk.$k.xy
  Rect ($GX + [int]$p[0] * $CELL) ($GY + [int]$p[1] * $CELL) $CELL $CELL $mdefs[$k][0] $mdefs[$k][1]
}

# ---- rulers: x on top + bottom, y on the left (zero based)
for ($i = 0; $i -lt $COLS; $i++) {
  TxtW ($GX + $i * $CELL) 92 16 $MUTE ([string]$i) $CELL 'CENTER'
  TxtW ($GX + $i * $CELL) 914 16 $MUTE ([string]$i) $CELL 'CENTER'
}
for ($i2 = 0; $i2 -lt $ROWS; $i2++) {
  TxtW 6 ($GY + $i2 * $CELL + 12) 16 $MUTE ([string]$i2) 36 'END'
}

# ---- marker labels (placed in cells verified free of both routes)
$labels = @(
  @('S', 'above', (EW '入口 S (2,2)' 22), 0),
  @('E', 'below', (EW '出口 E (23,15)' 22), -22),   # keep the label off the right-hand wall column
  @('A', 'above', (EW 'A 材料实验' 22), 0),
  @('B', 'above', (EW 'B 结构剧场' 22), 0),
  @('C', 'above', (EW 'C 光影工坊' 22), 0),
  @('D', 'left',  (EW 'D 作品巡览' 22), 0)
)
$ltext = [ordered]@{ 'S'='入口 S (2,2)'; 'E'='出口 E (23,15)'; 'A'='A 材料实验'; 'B'='B 结构剧场'; 'C'='C 光影工坊'; 'D'='D 作品巡览' }
$lcol  = [ordered]@{ 'S'=$SF; 'E'=$EF; 'A'=$ZF; 'B'=$ZF; 'C'=$ZF; 'D'=$ZF }
foreach ($g in $labels) {
  $k = $g[0]; $mode = $g[1]; $ew = [double]$g[2]
  $wpx = [math]::Ceiling($ew * 1.4 + 30)
  $p = $mk.$k.xy
  $cx = [double](CX ([int]$p[0])) + [double]$g[3]
  $cy = [double](CY ([int]$p[1]))
  if ($mode -eq 'above') {
    TxtW ($cx - $wpx / 2) ($cy - $CELL / 2 - 28) 22 $lcol[$k] $ltext[$k] $wpx 'CENTER' $true
  } elseif ($mode -eq 'below') {
    TxtW ($cx - $wpx / 2) ($cy + $CELL / 2 + 6) 22 $lcol[$k] $ltext[$k] $wpx 'CENTER' $true
  } else {
    TxtW ($cx - $CELL / 2 - 6 - $wpx) ($cy - 11) 22 $lcol[$k] $ltext[$k] $wpx 'END' $true
  }
}

# ---- route 1 : solid, drawn first so route 2 dashes sit on top of it
function Draw-Route1($runs) {
  foreach ($r in $runs) {
    $x1 = [double](CX ([int]$r.from[0])); $y1 = [double](CY ([int]$r.from[1]))
    $x2 = [double](CX ([int]$r.to[0]));   $y2 = [double](CY ([int]$r.to[1]))
    $len = [math]::Abs($x2 - $x1) + [math]::Abs($y2 - $y1)
    if ($len -lt 1) { continue }
    if ($y1 -eq $y2) { Rect $x1 ($y1 - $R1W / 2) $len $R1W $C1 }
    else             { Rect ($x1 - $R1W / 2) $y1 $R1W $len $C1 }
  }
}
function Draw-Arrows1($runs) {
  foreach ($r in $runs) {
    $x1 = [double](CX ([int]$r.from[0])); $y1 = [double](CY ([int]$r.from[1]))
    $x2 = [double](CX ([int]$r.to[0]));   $y2 = [double](CY ([int]$r.to[1]))
    $len = [math]::Abs($x2 - $x1) + [math]::Abs($y2 - $y1)
    if ($len -lt 1) { continue }
    $ux = if ($x2 -eq $x1) { 0.0 } else { ($x2 - $x1) / $len }
    $uy = if ($y2 -eq $y1) { 0.0 } else { ($y2 - $y1) / $len }
    $t = $len * 0.5
    Arrow ($x1 + $ux * $t) ($y1 + $uy * $t) $ux $uy $C1
  }
}
# ---- route 2 : dashed, narrow enough to stay inside route 1 on shared cells
function Draw-Route2($runs) {
  foreach ($r in $runs) {
    $x1 = [double](CX ([int]$r.from[0])); $y1 = [double](CY ([int]$r.from[1]))
    $x2 = [double](CX ([int]$r.to[0]));   $y2 = [double](CY ([int]$r.to[1]))
    $len = [math]::Abs($x2 - $x1) + [math]::Abs($y2 - $y1)
    if ($len -lt 1) { continue }
    $ux = if ($x2 -eq $x1) { 0.0 } else { ($x2 - $x1) / $len }
    $uy = if ($y2 -eq $y1) { 0.0 } else { ($y2 - $y1) / $len }
    $t = 0.0
    while ($t -lt $len) {
      $e = [math]::Min($t + $DASH, $len)
      if ($e - $t -ge 6) {
        $sx = $x1 + $ux * $t; $sy = $y1 + $uy * $t
        $dl = $e - $t
        if ($uy -eq 0) { Rect $sx ($sy - $R2W / 2) $dl $R2W $C2 '' '2' }
        else           { Rect ($sx - $R2W / 2) $sy $R2W $dl $C2 '' '2' }
      }
      $t += $PERIOD
    }
  }
}
function Draw-Arrows2($runs) {
  foreach ($r in $runs) {
    $x1 = [double](CX ([int]$r.from[0])); $y1 = [double](CY ([int]$r.from[1]))
    $x2 = [double](CX ([int]$r.to[0]));   $y2 = [double](CY ([int]$r.to[1]))
    $len = [math]::Abs($x2 - $x1) + [math]::Abs($y2 - $y1)
    if ($len -lt 1) { continue }
    $ux = if ($x2 -eq $x1) { 0.0 } else { ($x2 - $x1) / $len }
    $uy = if ($y2 -eq $y1) { 0.0 } else { ($y2 - $y1) / $len }
    # quarter points keep route 2 heads clear of route 1 heads on shared runs
    if ($len -ge 2 * $CELL) { $ts = @(0.25, 0.75) } else { $ts = @(0.5) }
    foreach ($f in $ts) {
      $t = $len * $f
      Arrow ($x1 + $ux * $t) ($y1 + $uy * $t) $ux $uy $C2
    }
  }
}

$r1runs = @($j.routes.route_1.straight_runs)
$legA   = @($j.routes.route_2.leg_a.straight_runs)
$legB   = @($j.routes.route_2.leg_b.straight_runs)
$legC   = @($j.routes.route_2.leg_c.straight_runs)

Draw-Route1 $r1runs
Draw-Arrows1 $r1runs
Draw-Route2 ($legA + $legB + $legC)
Draw-Arrows2 ($legA + $legB + $legC)

# ---- bottom stat panels
Rect 40 944 460 124 $PANEL "1 SOLID $PBD" '12'
Txt 56 958 24 $TX '路线一 · S → E 最短' $true
Txt 56 990 22 $SUB 'S(2,2) → E(23,15) · 34 步 68 米'
Txt 56 1016 22 $SUB ('门洞 {0}' -f (($j.connectivity.doors_crossed_by_route_1 | ForEach-Object { '(' + $_[0] + ',' + $_[1] + ')' }) -join ' '))
Txt 56 1042 22 $SUB ('与路线二重合 {0} 格' -f $j.connectivity.route_1_vs_route_2_shared_cell_count)

Rect 520 944 670 124 $PANEL "1 SOLID $PBD" '12'
Txt 536 958 24 $TX ('路线二 · S → B → D → E · 合计 {0} 步 {1} 米' -f $j.routes.route_2.steps, $j.routes.route_2.metres) $true
$legs = @(@($j.routes.route_2.leg_a, '第 1 段', 0), @($j.routes.route_2.leg_b, '第 2 段', 1), @($j.routes.route_2.leg_c, '第 3 段', 2))
$dy = 990
foreach ($lg2 in $legs) {
  $leg = $lg2[0]; $nm = $lg2[1]
  $dr = @($j.connectivity.doors_crossed_by_route_2)[$lg2[2]]
  $dstr = if ($null -ne $dr) { '(' + $dr[0] + ',' + $dr[1] + ')' } else { '无' }
  $line = ('{0} ({1},{2}) → ({3},{4}) · {5} 步 {6} 米 · 门洞 {7}' -f $nm,
      $leg.from_xy[0], $leg.from_xy[1], $leg.to_xy[0], $leg.to_xy[1],
      $leg.steps, $leg.metres, $dstr)
  Txt 536 $dy 22 $SUB $line
  $dy += 26
}

L ('    </Stack>')
L ('  </Container>')
L ('</Snapshot>')

# -------------------------------------------------------------------- save --
$out = $sb.ToString()
$path = "$T\wayfinding-v$Ver.snapshot"
[System.IO.File]::WriteAllText($path, $out, $utf8)
$bytes = [System.IO.File]::ReadAllBytes($path)
$bom = if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { 'BOM!' } else { 'no-bom' }
Write-Host "wayfinding-v$Ver.snapshot  $($bytes.Length) bytes  $bom"
