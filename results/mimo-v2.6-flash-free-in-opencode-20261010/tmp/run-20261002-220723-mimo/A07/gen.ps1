param([string]$Ver = '02')
# A07 - emits both deliverable DSLs from routes.json:
#   network-map  1600x1000  schematic transit diagram (16 stations, 3 lines)
#   travel-card   720x1280  three ordinary journeys + accessible verdicts
# Geometry, line segments and route strips are computed here so the two images
# and routes.json can never disagree.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$TMP  = Join-Path $ROOT "tmp\$RUN\A07"
$OUT  = Join-Path $ROOT "outputs\$RUN\A07"
New-Item -ItemType Directory -Force -Path $TMP, $OUT | Out-Null

$routes = Get-Content (Join-Path $OUT 'routes.json') -Raw -Encoding UTF8 | ConvertFrom-Json

# ---------------------------------------------------------------- palette
$FONT  = 'Inter,Noto Sans CJK SC'
$BG    = '#0B1220'
$PANEL = '#111A2B'
$BORD  = '#24304A'
$CHIP  = '#1B2540'
$TXT1  = '#F8FAFC'
$TXT2  = '#A8BCD8'
$TXT3  = '#7288A8'
$CR = '#F43F5E'; $CB = '#3B82F6'; $CG = '#22C55E'   # R red / B blue / G green
$ACC_OK = '#34D399'
$ACC_NO = '#FBBF24'
$LINE_W = 9.0
$DOT_RING = '#0B1220'

$LINE_COLOR = @{ R = $CR; B = $CB; G = $CG }
$LINE_NAME  = @{ R = 'R 红线'; B = 'B 蓝线'; G = 'G 绿线' }

# ---------------------------------------------------------------- helpers
$sb = New-Object System.Text.StringBuilder
function L([string]$t) { [void]$script:sb.AppendLine($t) }
function F([double]$v) { $v.ToString('0.##', [System.Globalization.CultureInfo]::InvariantCulture) }
function EW([string]$t, [double]$fs) {
  $w = 0.0
  foreach ($ch in $t.ToCharArray()) {
    $c = [int]$ch
    if ($c -ge 0x1100 -or $c -eq 0x25A0 -or $c -eq 0x25A1) { $w += $fs }
    else { $w += $fs * 0.55 }
  }
  $w
}
function Txt([double]$x, [double]$y, [string]$t, [double]$fs, [string]$col, [string]$extra = '') {
  L ('      <Positioned left="{0}" top="{1}"><Text fontSize="{2}" height="1.0" fontFamily="{3}" color="{4}"{5}>{6}</Text></Positioned>' -f (F $x), (F $y), (F $fs), $FONT, $col, $extra, $t)
}
function TxtC([double]$cx, [double]$y, [string]$t, [double]$fs, [string]$col, [string]$extra = '') {
  $bw = [Math]::Max((EW $t $fs) + 20, 48)
  L ('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Text fontSize="{4}" height="1.0" fontFamily="{5}" color="{6}" textAlign="CENTER"{7}>{8}</Text></Positioned>' -f (F ($cx - $bw / 2)), (F $y), (F $bw), (F $fs), (F $fs), $FONT, $col, $extra, $t)
}
function Rect([double]$x, [double]$y, [double]$w, [double]$h, [string]$fill, [double]$rad) {
  L ('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Container width="{2}" height="{3}" color="{4}" borderRadius="{5}"/></Positioned>' -f (F $x), (F $y), (F $w), (F $h), $fill, (F $rad))
}
function Box([double]$x, [double]$y, [double]$w, [double]$h, [string]$fill, [string]$bcol, [double]$bw, [double]$rad) {
  L ('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Container width="{2}" height="{3}" color="{4}" border="{5} SOLID {6}" borderRadius="{7}"/></Positioned>' -f (F $x), (F $y), (F $w), (F $h), $fill, (F $bw), $bcol, (F $rad))
}
function Circle([double]$cx, [double]$cy, [double]$d, [string]$fill, [string]$ring, [double]$rw) {
  $x = $cx - $d / 2; $y = $cy - $d / 2
  if ($rw -gt 0) {
    L ('      <Positioned left="{0}" top="{1}" width="{2}" height="{2}"><Container width="{2}" height="{2}" shape="CIRCLE" color="{3}" border="{4} SOLID {5}"/></Positioned>' -f (F $x), (F $y), (F $d), $fill, (F $rw), $ring)
  } else {
    L ('      <Positioned left="{0}" top="{1}" width="{2}" height="{2}"><Container width="{2}" height="{2}" shape="CIRCLE" color="{3}"/></Positioned>' -f (F $x), (F $y), (F $d), $fill)
  }
}
# proven primitive: bar from (x1,y1) to (x2,y2) rotated about its left-edge centre
function Seg([double]$x1, [double]$y1, [double]$x2, [double]$y2, [double]$th, [string]$col) {
  $dx = $x2 - $x1; $dy = $y2 - $y1
  $len = [Math]::Sqrt($dx * $dx + $dy * $dy)
  if ($len -lt 0.05) { return }
  $c = $dx / $len; $s = $dy / $len
  $m = '({0},{1},0,0,{2},{3},0,0,0,0,1,0,0,0,0,1)' -f (F $c), (F $s), (F (-$s)), (F $c)
  L ('      <Positioned left="{0}" top="{1}">' -f (F $x1), (F ($y1 - $th / 2)))
  L ('        <Transform matrix="{0}" origin="(0,{1})">' -f $m, (F ($th / 2)))
  L ('          <Container width="{0}" height="{1}" color="{2}"/>' -f (F $len), (F $th), $col)
  L ('        </Transform>')
  L ('      </Positioned>')
}
function Chip([double]$x, [double]$y, [string]$t, [double]$fs, [string]$fill, [string]$tcol, [string]$bcol, [double]$h, [double]$pad) {
  $w = (EW $t $fs) + 2 * $pad
  Box $x $y $w $h $fill $bcol 1 8
  Txt ($x + $pad) ($y + ($h - $fs) / 2) $t $fs $tcol
  $w
}
function OpenDoc([string]$w, [string]$h) {
  $script:sb = New-Object System.Text.StringBuilder
  L '<Snapshot type="png" background="#0B1220">'
  L ('  <Container width="{0}" height="{1}">' -f $w, $h)
  L '    <Stack>'
}
function SaveDoc([string]$path) {
  L '    </Stack>'
  L '  </Container>'
  L '</Snapshot>'
  [System.IO.File]::WriteAllText($path, $script:sb.ToString(), (New-Object System.Text.UTF8Encoding($false)))
}

# ==================================================================== data
$ST = @(
  @{ id = 'S01'; n = '松林';   x = 120.0;  y = 470.0; a = $true;  lm = 'C'; lv = 120.0;  ly = 496.0 },
  @{ id = 'S02'; n = '北门';   x = 290.0;  y = 470.0; a = $true;  lm = 'C'; lv = 290.0;  ly = 496.0 },
  @{ id = 'S03'; n = '书院';   x = 460.0;  y = 470.0; a = $false; lm = 'C'; lv = 460.0;  ly = 496.0 },
  @{ id = 'S04'; n = '中心';   x = 610.0;  y = 470.0; a = $true;  lm = 'L'; lv = 628.0;  ly = 384.0 },
  @{ id = 'S05'; n = '东桥';   x = 610.0;  y = 730.0; a = $false; lm = 'L'; lv = 644.0;  ly = 742.0 },
  @{ id = 'S06'; n = '江湾';   x = 610.0;  y = 860.0; a = $true;  lm = 'C'; lv = 610.0;  ly = 886.0 },
  @{ id = 'S07'; n = '西港';   x = 1040.0; y = 470.0; a = $true;  lm = 'C'; lv = 1040.0; ly = 396.0 },
  @{ id = 'S08'; n = '工坊';   x = 870.0;  y = 470.0; a = $true;  lm = 'L'; lv = 856.0;  ly = 506.0 },
  @{ id = 'S09'; n = '花园';   x = 470.0;  y = 330.0; a = $false; lm = 'C'; lv = 470.0;  ly = 244.0 },
  @{ id = 'S10'; n = '南门';   x = 300.0;  y = 330.0; a = $true;  lm = 'C'; lv = 300.0;  ly = 244.0 },
  @{ id = 'S11'; n = '会展';   x = 130.0;  y = 330.0; a = $true;  lm = 'C'; lv = 130.0;  ly = 244.0 },
  @{ id = 'S12'; n = '机场';   x = 790.0;  y = 860.0; a = $true;  lm = 'C'; lv = 790.0;  ly = 886.0 },
  @{ id = 'S13'; n = '石溪';   x = 870.0;  y = 210.0; a = $true;  lm = 'L'; lv = 896.0;  ly = 188.0 },
  @{ id = 'S14'; n = '公园';   x = 870.0;  y = 340.0; a = $false; lm = 'L'; lv = 896.0;  ly = 318.0 },
  @{ id = 'S15'; n = '剧院';   x = 740.0;  y = 600.0; a = $true;  lm = 'L'; lv = 770.0;  ly = 600.0 },
  @{ id = 'S16'; n = '研究所'; x = 450.0;  y = 890.0; a = $true;  lm = 'C'; lv = 450.0;  ly = 916.0 }
)
$ById = @{}; foreach ($s in $ST) { $ById[$s.id] = $s }
$TRANSFER = @('S04', 'S05', 'S08')

$LINES = @(
  @{ id = 'R'; pts = @(@(120.0, 470.0), @(290.0, 470.0), @(460.0, 470.0), @(610.0, 470.0), @(610.0, 730.0), @(610.0, 860.0), @(790.0, 860.0)) },
  @{ id = 'B'; pts = @(@(1040.0, 470.0), @(870.0, 470.0), @(610.0, 470.0), @(470.0, 330.0), @(300.0, 330.0), @(130.0, 330.0)) },
  @{ id = 'G'; pts = @(@(870.0, 210.0), @(870.0, 340.0), @(870.0, 470.0), @(740.0, 600.0), @(610.0, 730.0), @(450.0, 890.0)) }
)
# letter badges beside their own line (verified clear of every label box)
$BADGES = @(
  @{ l = 'R'; x = 180.0; y = 424.0 },
  @{ l = 'R'; x = 554.0; y = 636.0 },
  @{ l = 'B'; x = 700.0; y = 484.0 },
  @{ l = 'B'; x = 340.0; y = 350.0 },
  @{ l = 'G'; x = 810.0; y = 246.0 },
  @{ l = 'G'; x = 490.0; y = 760.0 }
)

# ==================================================================== map
OpenDoc '1600' '1000'
Txt 60 40 '虚构城市地铁示意图' 44 $TXT1 ' fontStyle="BOLD"'
Txt 60 100 '三线十六站 · 示意图（非地理比例）· 连线只用 0°/45°/90° 走向 · 站号 S01–S16' 24 $TXT2 ''

# 1. line strokes
foreach ($ln in $LINES) {
  $p = $ln.pts
  for ($i = 0; $i -lt $p.Count - 1; $i++) { Seg $p[$i][0] $p[$i][1] $p[$i + 1][0] $p[$i + 1][1] $LINE_W ($LINE_COLOR[$ln.id]) }
  for ($i = 1; $i -lt $p.Count - 1; $i++) { Rect ($p[$i][0] - $LINE_W / 2) ($p[$i][1] - $LINE_W / 2) $LINE_W $LINE_W ($LINE_COLOR[$ln.id]) 0 }
}
# 2. line letter badges
foreach ($b in $BADGES) {
  Box $b.x $b.y 44 32 ($LINE_COLOR[$b.l]) ($LINE_COLOR[$b.l]) 1 8
  TxtC ($b.x + 22) ($b.y + 5) $b.l 22 '#FFFFFF' ' fontStyle="BOLD"'
}
# 3. station dots
foreach ($s in $ST) { if ($TRANSFER -notcontains $s.id) { Circle $s.x $s.y 20 '#FFFFFF' $DOT_RING 3 } }
foreach ($tid in $TRANSFER) { $s = $ById[$tid]; Circle $s.x $s.y 32 '#FFFFFF' $DOT_RING 4 }
# 4. station labels
foreach ($s in $ST) {
  $l1 = $s.id + ' ' + $s.n
  if ($s.a) { $l2 = [string][char]0x25A0 + ' 无障碍'; $c2 = $ACC_OK } else { $l2 = [string][char]0x25A1 + ' 非无障碍'; $c2 = $ACC_NO }
  if ($s.lm -eq 'C') {
    TxtC $s.lv $s.ly $l1 22 $TXT1 ' fontStyle="BOLD"'
    TxtC $s.lv ($s.ly + 26) $l2 20 $c2 ''
  } else {
    Txt $s.lv $s.ly $l1 22 $TXT1 ' fontStyle="BOLD"'
    Txt $s.lv ($s.ly + 26) $l2 20 $c2 ''
  }
}
# 5. legend
$LX = 1150.0; $LY = 170.0; $LW = 410.0; $LH = 786.0
Box $LX $LY $LW $LH $PANEL $BORD 1 16
$cx0 = $LX + 24
$cx1 = $LX + $LW - 24
Txt $cx0 196 '图例' 26 $TXT1 ' fontStyle="BOLD"'
Rect $cx0 238 ($cx1 - $cx0) 1 $BORD 0
Txt $cx0 256 '线路' 22 $TXT2 ' fontStyle="BOLD"'
$legLine = @(@{ l = 'R'; t = 'R 红线 · 松林 → 机场' }, @{ l = 'B'; t = 'B 蓝线 · 西港 → 会展' }, @{ l = 'G'; t = 'G 绿线 · 石溪 → 研究所' })
$ly = 294
foreach ($e in $legLine) {
  Box $cx0 $ly 40 28 ($LINE_COLOR[$e.l]) ($LINE_COLOR[$e.l]) 1 8
  TxtC ($cx0 + 20) ($ly + 4) $e.l 20 '#FFFFFF' ' fontStyle="BOLD"'
  Txt ($cx0 + 52) ($ly + 4) $e.t 20 $TXT1 ''
  $ly += 42
}
Txt $cx0 430 '车站' 22 $TXT2 ' fontStyle="BOLD"'
Circle ($cx0 + 10) 470 20 '#FFFFFF' $DOT_RING 3
Txt ($cx0 + 52) 460 '普通站（只有一条线路经过）' 20 $TXT1 ''
Circle ($cx0 + 16) 526 32 '#FFFFFF' $DOT_RING 4
Txt ($cx0 + 52) 506 '换乘站 S04 / S05 / S08' 20 $TXT1 ''
Txt ($cx0 + 52) 534 '圆点更大，可换乘另一条线路' 20 $TXT2 ''
Txt $cx0 586 '无障碍' 22 $TXT2 ' fontStyle="BOLD"'
Txt $cx0 626 ([string][char]0x25A0 + ' 无障碍') 20 $ACC_OK ' fontStyle="BOLD"'
Txt $cx0 654 '可作为起终点与换乘站' 20 $TXT2 ''
Txt $cx0 690 ([string][char]0x25A1 + ' 非无障碍') 20 $ACC_NO ' fontStyle="BOLD"'
Txt $cx0 718 '可乘车通过，不可作起终点或换乘站' 20 $TXT2 ''
Txt $cx0 754 '非无障碍站：S03 书院 · S05 东桥' 20 $TXT3 ''
Txt $cx0 782 'S09 花园 · S14 公园（共 4 站）' 20 $TXT3 ''
Txt $cx0 830 '须知' 22 $TXT2 ' fontStyle="BOLD"'
Txt $cx0 868 '本图为示意拓扑图，非地理比例' 20 $TXT2 ''
Txt $cx0 896 '线条相交但没有站 = 非换乘' 20 $TXT2 ''
Txt $cx0 924 '三条线两两共站仅 S04 / S05 / S08' 20 $TXT2 ''
SaveDoc (Join-Path $TMP ("map-v$Ver.snapshot"))
$mapPath = Join-Path $TMP ("map-v$Ver.snapshot")
"map dsl : " + $mapPath + "  (" + (Get-Item $mapPath).Length + " bytes)"

# ==================================================================== card
function DrawStrip([double]$T, [array]$pathIds, [array]$segs) {
  $n = $pathIds.Count
  $step = 524.0 / ($n - 1)
  $xs = @()
  for ($i = 0; $i -lt $n; $i++) { $xs += 98.0 + $i * $step }
  $lineTop = $T + 140.0; $lineMid = $lineTop + 3
  $badgeY = $T + 102.0
  Seg $xs[0] $lineMid $xs[$n - 1] $lineMid 6 '#2A3A57'
  foreach ($sg in $segs) {
    $fi = [array]::IndexOf($pathIds, $sg.stations[0])
    $li = [array]::IndexOf($pathIds, $sg.stations[$sg.stations.Count - 1])
    $xa = $xs[$fi]; $xb = $xs[$li]
    $col = $LINE_COLOR[$sg.line]
    Rect $xa $lineTop ($xb - $xa) 6 $col 3
    $bx = ($xa + $xb) / 2 - 22
    Box $bx $badgeY 44 24 $col $col 1 8
    TxtC ($bx + 22) ($badgeY + 3) $sg.line 20 '#FFFFFF' ' fontStyle="BOLD"'
  }
  for ($i = 0; $i -lt $n; $i++) {
    $id = $pathIds[$i]
    if ($TRANSFER -contains $id) { Circle $xs[$i] $lineMid 24 '#FFFFFF' $DOT_RING 4 }
    else { Circle $xs[$i] $lineMid 16 '#FFFFFF' $DOT_RING 3 }
    # same accessibility encoding as the map: filled square = accessible, hollow = not
    if ($ById[$id].a) { $nm = [string][char]0x25A0 + ' ' + $ById[$id].n; $nc = $TXT1 }
    else              { $nm = [string][char]0x25A1 + ' ' + $ById[$id].n; $nc = $ACC_NO }
    TxtC $xs[$i] ($T + 160.0) $nm 20 $nc ''
  }
}
function MetricRow([double]$T, [int]$edges, [int]$transfers, [int]$stations) {
  $y = $T + 60.0
  Chip 68.0 $y ("{0} 区间" -f $edges) 20 $CHIP $TXT1 $BORD 30 16 | Out-Null
  Chip 176.0 $y ("{0} 次换乘" -f $transfers) 20 $CHIP $TXT1 $BORD 30 16 | Out-Null
  Chip 304.0 $y ("{0} 站" -f $stations) 20 $CHIP $TXT2 $BORD 30 16 | Out-Null
}
function SegLineText([array]$segs) {
  $parts = @()
  foreach ($sg in $segs) {
    $parts += ('{0} {1}→{2}' -f $LINE_NAME[$sg.line], $sg.stations[0], $sg.stations[$sg.stations.Count - 1])
  }
  $parts -join '  →  '
}
function CardBox([double]$top, [double]$h) { Box 40.0 $top 640.0 $h $PANEL $BORD 1 16 }
function CardBody([double]$top, [string]$idx, [object]$r) {
  $firstSeg = $r.shortest_ordinary.line_segments[0]
  $accent = $LINE_COLOR[$firstSeg.line]
  Box 68.0 ($top + 16) 38 32 $accent $accent 1 8
  TxtC 87.0 ($top + 22) $idx 22 '#FFFFFF' ' fontStyle="BOLD"'
  $title = '{0} {1} → {2} {3}' -f $r.query.from, $r.query.from_name, $r.query.to, $r.query.to_name
  Txt 118.0 ($top + 17) $title 24 $TXT1 ' fontStyle="BOLD"'
  MetricRow $top $r.shortest_ordinary.edge_count $r.shortest_ordinary.transfer_count $r.shortest_ordinary.station_count
  DrawStrip $top $r.shortest_ordinary.station_path $r.shortest_ordinary.line_segments
  Txt 68.0 ($top + 190.0) (SegLineText $r.shortest_ordinary.line_segments) 20 $TXT2 ''
  # verdict
  $y = $top + 226.0
  if ([bool]$r.shortest_is_accessible_journey) {
    Box 68.0 $y 500 34 '#0C2A22' '#10B981' 1 8
    Txt 84.0 ($y + 7) '无障碍旅程：可以 · 起点/终点/换乘站均无障碍' 20 '#6EE7B7' ' fontStyle="BOLD"'
  } else {
    Box 68.0 $y 566 34 '#2C1F06' '#F59E0B' 1 8
    Txt 84.0 ($y + 7) ('无障碍旅程：不可以 · ' + $r.accessible_blocked_reason) 20 '#FCD34D' ' fontStyle="BOLD"'
  }
}

OpenDoc '720' '1280'
Txt 40 24 '旅行卡 · 三条最少区间路线' 28 $TXT1 ' fontStyle="BOLD"'
Txt 40 60 '数据 inputs/network.json · ■ 无障碍 / □ 非无障碍' 20 $TXT2 ''
Rect 40 92 640 1 $BORD 0

$q = $routes.queries

# card 1
CardBox 100.0 280.0
CardBody 100.0 '1' $q[0]

# card 2 - adds the separately computed shortest accessible journey
$t2 = 398.0
CardBox $t2 480.0
CardBody $t2 '2' $q[1]
Rect 68.0 ($t2 + 296) 584 1 $BORD 0
Txt 68.0 ($t2 + 306) '最短无障碍旅程（另求：起终点与换乘站均须无障碍）' 20 $ACC_OK ' fontStyle="BOLD"'
$a = $q[1].shortest_accessible
Txt 68.0 ($t2 + 336) ('站序 ' + ($a.station_path -join ' → ')) 20 $TXT1 ''
$aparts = @()
foreach ($sg in $a.line_segments) { $aparts += ('{0} {1}→{2}' -f $LINE_NAME[$sg.line], $sg.stations[0], $sg.stations[$sg.stations.Count - 1]) }
$join = '  →  '
$lineA = '线路段 ' + $aparts[0] + $join + $aparts[1]
$lineB = '→ ' + $aparts[2]
Txt 68.0 ($t2 + 366) $lineA 20 $TXT2 ''
Txt 68.0 ($t2 + 394) $lineB 20 $TXT2 ''
Chip 68.0 ($t2 + 426) ("{0} 区间" -f $a.edge_count) 20 $CHIP $TXT1 $BORD 30 16 | Out-Null
Chip 176.0 ($t2 + 426) ("{0} 次换乘" -f $a.transfer_count) 20 $CHIP $TXT1 $BORD 30 16 | Out-Null
Chip 304.0 ($t2 + 426) 'G → B → R' 20 $CHIP $TXT3 $BORD 30 16 | Out-Null
Txt 470.0 ($t2 + 433) '仍为最小区间数' 20 $ACC_OK ''

# card 3
CardBox 896.0 280.0
CardBody 896.0 '3' $q[2]

# footer
Txt 40 1196 '无障碍判定：起点、终点、每次换乘所在的站须无障碍；' 20 $TXT2 ''
Txt 40 1222 '仅途经（乘车通过）非无障碍站允许，不为此删除任何线路。' 20 $TXT2 ''
Txt 40 1248 '换乘 = 改变乘坐线路，第一次上车不算；站数 = 区间数 + 1。' 20 $TXT3 ''

SaveDoc (Join-Path $TMP ("card-v$Ver.snapshot"))
$cardPath = Join-Path $TMP ("card-v$Ver.snapshot")
"card dsl: " + $cardPath + "  (" + (Get-Item $cardPath).Length + " bytes)"
