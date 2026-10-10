# A06 - 1600x1000 dependency map: 14 nodes, 16 solid prerequisite edges, 2 dashed feedback edges
# Emits the complete Snapshot DSL and graph-audit.json from one computed geometry.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$TMP  = Join-Path $ROOT ("tmp\$RUN\A06")
$OUT  = Join-Path $ROOT ("outputs\$RUN\A06")
New-Item -ItemType Directory -Force -Path $TMP,$OUT | Out-Null

$FONT = 'Inter,Noto Sans CJK SC'
$BG   = '#0B1220'
$SOL  = '#7DD3FC'   # prerequisite edges
$FBK  = '#FB923C'   # feedback edges
$BAND = '#111A2B'
$N_FILL = '#141D30'; $N_BORD = '#334155'; $N_ID = '#7DD3FC'; $N_LAB = '#F8FAFC'
$N8_FILL = '#1A1735'; $N8_BORD = '#A78BFA'; $N8_ID = '#C4B5FD'

$sb = New-Object System.Text.StringBuilder

function L([string]$t) { [void]$script:sb.AppendLine($t) }
function F([double]$v) { $v.ToString('0.##', [System.Globalization.CultureInfo]::InvariantCulture) }
function EW([string]$t, [double]$fs) {
  $w = 0.0
  foreach ($ch in $t.ToCharArray()) { if ([int]$ch -ge 0x1100) { $w += $fs } else { $w += $fs * 0.55 } }
  $w
}
function Txt([double]$x, [double]$y, [string]$t, [double]$fs, [string]$col, [string]$extra = '') {
  L ('      <Positioned left="{0}" top="{1}"><Text fontSize="{2}" height="1.0" fontFamily="{3}" color="{4}"{5}>{6}</Text></Positioned>' -f (F $x), (F $y), (F $fs), $FONT, $col, $extra, $t)
}
function TxtC([double]$cx, [double]$y, [string]$t, [double]$fs, [string]$col, [string]$extra = '') {
  $w = EW $t $fs
  Txt ($cx - $w / 2) $y $t $fs $col $extra
}
function Panel([double]$x, [double]$y, [double]$w, [double]$h, [string]$fill, [double]$rad) {
  L ('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Container width="{2}" height="{3}" color="{4}" borderRadius="{5}"/></Positioned>' -f (F $x), (F $y), (F $w), (F $h), $fill, (F $rad))
}
function Box([double]$x, [double]$y, [double]$w, [double]$h, [string]$fill, [string]$bcol, [double]$bw, [double]$rad) {
  L ('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Container width="{2}" height="{3}" color="{4}" border="{5} SOLID {6}" borderRadius="{7}"/></Positioned>' -f (F $x), (F $y), (F $w), (F $h), $fill, (F $bw), $bcol, (F $rad))
}
# Proven A05 primitive: a bar from (x1,y1) to (x2,y2), rotated about its left-edge centre.
function Seg([double]$x1, [double]$y1, [double]$x2, [double]$y2, [double]$th, [string]$col) {
  $dx = $x2 - $x1; $dy = $y2 - $y1
  $len = [Math]::Sqrt($dx * $dx + $dy * $dy)
  if ($len -lt 0.05) { return }
  $c = $dx / $len; $s = $dy / $len
  $top = $y1 - $th / 2
  $m = '({0},{1},0,0,{2},{3},0,0,0,0,1,0,0,0,0,1)' -f (F $c), (F $s), (F (-$s)), (F $c)
  L ('      <Positioned left="{0}" top="{1}">' -f (F $x1), (F $top))
  L ('        <Transform matrix="{0}" origin="(0,{1})">' -f $m, (F ($th / 2)))
  L ('          <Container width="{0}" height="{1}" color="{2}"/>' -f (F $len), (F $th), $col)
  L ('        </Transform>')
  L ('      </Positioned>')
}
# Arrowhead: two bars springing from the tip at +-150 deg of the travel direction (60 deg included angle).
function Arrow([double]$tx, [double]$ty, [double]$ux, [double]$uy, [double]$alen, [double]$th, [string]$col) {
  $a  = [Math]::Atan2($uy, $ux)
  $d1 = $a + 2.617993877991494
  $d2 = $a - 2.617993877991494
  $p1x = $tx + $alen * [Math]::Cos($d1); $p1y = $ty + $alen * [Math]::Sin($d1)
  $p2x = $tx + $alen * [Math]::Cos($d2); $p2y = $ty + $alen * [Math]::Sin($d2)
  Seg $tx $ty $p1x $p1y $th $col
  Seg $tx $ty $p2x $p2y $th $col
}
# Straight run with a travelling direction; emits dashes (or one segment) plus the arrowhead at the tip.
function Run([double]$x1, [double]$y1, [double]$x2, [double]$y2, [double]$th, [string]$col,
             [double]$ux, [double]$uy, [double]$alen, [bool]$dash, [double]$dl, [double]$gp) {
  $dx = $x2 - $x1; $dy = $y2 - $y1
  $len = [Math]::Sqrt($dx * $dx + $dy * $dy)
  if ($len -lt 0.05) { return }
  if ($dash) {
    $vx = $dx / $len; $vy = $dy / $len
    $t = 0.0
    while ($t -lt $len) {
      $t2 = $t + $dl
      if ($t2 -gt $len) { $t2 = $len }
      $ax = $x1 + $vx * $t;  $ay = $y1 + $vy * $t
      $bx = $x1 + $vx * $t2; $by = $y1 + $vy * $t2
      Seg $ax $ay $bx $by $th $col
      $t = $t2 + $gp
    }
  }
  else {
    Seg $x1 $y1 $x2 $y2 $th $col
  }
  Arrow $x2 $y2 $ux $uy $alen $th $col
}

# ------------------------------------------------------------------ geometry
$NW = 108.0; $NH = 72.0
$COLX = @(40.0, 181.2, 322.4, 463.6, 604.8, 746.0, 887.2, 1028.4, 1169.6, 1310.8, 1452.0)
$ROWY = @(220.0, 480.0, 700.0)

$nodes = @(
  @{ id = 'N01'; label = '需求冻结'; col = 0;  row = 1 },
  @{ id = 'N02'; label = '输入检查'; col = 1;  row = 0 },
  @{ id = 'N03'; label = '字体查询'; col = 1;  row = 2 },
  @{ id = 'N04'; label = '数据计算'; col = 2;  row = 0 },
  @{ id = 'N05'; label = '内容规划'; col = 2;  row = 1 },
  @{ id = 'N06'; label = '版式系统'; col = 3;  row = 2 },
  @{ id = 'N07'; label = '图表生成'; col = 3;  row = 0 },
  @{ id = 'N08'; label = 'DSL构建';  col = 4;  row = 1 },
  @{ id = 'N09'; label = '首轮渲染'; col = 5;  row = 1 },
  @{ id = 'N10'; label = '视觉检查'; col = 6;  row = 1 },
  @{ id = 'N11'; label = '问题修复'; col = 7;  row = 1 },
  @{ id = 'N12'; label = '回归渲染'; col = 8;  row = 1 },
  @{ id = 'N13'; label = '产物校验'; col = 9;  row = 1 },
  @{ id = 'N14'; label = '交付归档'; col = 10; row = 1 }
)
$ids = @(); foreach ($n in $nodes) { $ids += $n.id }

# 16 prerequisite edges (flat strings - PowerShell would flatten nested array literals)
$solid = @(
  'N01>N02', 'N01>N03', 'N02>N04', 'N02>N05',
  'N03>N06', 'N05>N06', 'N04>N07', 'N06>N08',
  'N07>N08', 'N08>N09', 'N09>N10', 'N10>N11',
  'N11>N12', 'N12>N13', 'N13>N14', 'N04>N13'
)
# 2 feedback edges - deliberately NOT in $solid, so they never influence ordering
$feedback = @('N09>N08', 'N10>N08')

$inN = @{}; $outN = @{}
foreach ($id in $ids) { $inN[$id] = @(); $outN[$id] = @() }
foreach ($e in $solid) { $p = $e.Split('>'); $outN[$p[0]] += $p[1]; $inN[$p[1]] += $p[0] }

# longest-path layering (Bellman-Ford over a DAG): layer(n) = 1 + max(layer(preds))
$layer = @{}
foreach ($id in $ids) { $layer[$id] = 1 }
$changed = $true
while ($changed) {
  $changed = $false
  foreach ($e in $solid) {
    $p = $e.Split('>')
    if ($layer[$p[1]] -lt ($layer[$p[0]] + 1)) { $layer[$p[1]] = $layer[$p[0]] + 1; $changed = $true }
  }
}
$LAYERS = 0; foreach ($id in $ids) { if ($layer[$id] -gt $LAYERS) { $LAYERS = $layer[$id] } }

# all maximal prerequisite paths
$paths = New-Object System.Collections.ArrayList
function DFS([string]$cur, [array]$path) {
  $ext = $false
  foreach ($nx in $outN[$cur]) { $ext = $true; DFS $nx ($path + $nx) }
  if (-not $ext) { [void]$paths.Add($path) }
}
DFS 'N01' @('N01')
$MAXLEN = 0
foreach ($p in $paths) { if ($p.Count -gt $MAXLEN) { $MAXLEN = $p.Count } }
$longest = @()
foreach ($p in $paths) { if ($p.Count -eq $MAXLEN) { $longest += , @($p) } }

# ------------------------------------------------------------------ emit DSL
L ('<Snapshot type="png" background="' + $BG + '">')
L '  <Container width="1600" height="1000">'
L '    <Stack>'

# 1. per-layer column bands (visual proof that a column == one topological layer)
for ($i = 0; $i -lt 11; $i++) { Panel ($COLX[$i] - 8) 204 124 572 $BAND 14 }

# 2. header
Txt 40 36 '从需求到可复现交付' 40 '#F8FAFC' ' fontStyle="BOLD"'
Txt 40 86 '14 节点 · 16 条实线先决依赖（构成 DAG）· 2 条虚线反馈回路（不参与排序）· 11 个拓扑层 L1–L11：左→右为先后，同列节点并行' 20 '#94A3B8'

# 3. legend
Seg 40 133 76 133 3 $SOL
Arrow 76 133 1 0 9 3 $SOL
Txt 88 124 '实线箭头：先决依赖（DAG 方向，箭头指向后继）' 18 '#CBD5E1'
Run 520 133 556 133 3 $FBK 1 0 9 $true 9 6
Txt 568 124 '虚线箭头：反馈关系（不参与拓扑排序与布局）' 18 '#CBD5E1'
Seg 978 133 1014 133 3 $SOL
Arrow 1014 133 1 0 9 3 $SOL
Txt 1026 124 '同列为并行，长跨层实线同属先决依赖' 18 '#CBD5E1'

# 4. the one long-range prerequisite N04 -> N13, routed above the graph (never leftward)
$LT_Y = 172.0
Seg 376.4 220 376.4 $LT_Y 2.5 $SOL
Seg 376.4 $LT_Y 1364.8 $LT_Y 2.5 $SOL
Run 1364.8 $LT_Y 1364.8 480 2.5 $SOL 0 1 11 $false 0 0
Txt 400 182 '跨层先决：N04 数据计算 → N13 产物校验（计算结果直接用于交付前校验）' 18 '#E2E8F0'

# 5. 15 short prerequisite edges (16 minus the long one above)
Seg 148 506 181.2 256 2.5 $SOL
Arrow 181.2 256 33.2 (-250) 11 2.5 $SOL
Seg 148 526 181.2 736 2.5 $SOL
Arrow 181.2 736 33.2 210 11 2.5 $SOL
Seg 289.2 256 322.4 256 2.5 $SOL
Arrow 322.4 256 1 0 11 2.5 $SOL
Seg 289.2 276 322.4 516 2.5 $SOL
Arrow 322.4 516 33.2 240 11 2.5 $SOL
Seg 289.2 736 463.6 736 2.5 $SOL
Arrow 463.6 736 1 0 11 2.5 $SOL
Seg 430.4 536 490 700 2.5 $SOL
Arrow 490 700 59.6 164 11 2.5 $SOL
Seg 430.4 256 463.6 256 2.5 $SOL
Arrow 463.6 256 1 0 11 2.5 $SOL
Seg 545 700 658.8 552 2.5 $SOL
Arrow 658.8 552 113.8 (-148) 11 2.5 $SOL
Seg 517.6 292 625 480 2.5 $SOL
Arrow 625 480 107.4 188 11 2.5 $SOL
Seg 712.8 516 746 516 2.5 $SOL
Arrow 746 516 1 0 11 2.5 $SOL
Seg 854 516 887.2 516 2.5 $SOL
Arrow 887.2 516 1 0 11 2.5 $SOL
Seg 995.2 516 1028.4 516 2.5 $SOL
Arrow 1028.4 516 1 0 11 2.5 $SOL
Seg 1136.4 516 1169.6 516 2.5 $SOL
Arrow 1169.6 516 1 0 11 2.5 $SOL
Seg 1277.6 516 1310.8 516 2.5 $SOL
Arrow 1310.8 516 1 0 11 2.5 $SOL
Seg 1418.8 516 1452 516 2.5 $SOL
Arrow 1452 516 1 0 11 2.5 $SOL

# 6. the two feedback loops - dashed, orange, routed above N08, never part of the DAG
Run 800 480 800 424 2.5 $FBK 0 (-1) 0 $true 9 6
Run 800 424 696 424 2.5 $FBK (-1) 0 0 $true 9 6
Run 696 424 696 480 2.5 $FBK 0 1 11 $true 9 6
Run 941.2 480 941.2 344 2.5 $FBK 0 (-1) 0 $true 9 6
Run 941.2 344 660 344 2.5 $FBK (-1) 0 0 $true 9 6
Run 660 344 660 480 2.5 $FBK 0 1 11 $true 9 6
# elbow caps: a dash gap must never open right at a corner (would read as a break in the loop)
Panel 798.5 422.5 3 3 $FBK 0
Panel 694.5 422.5 3 3 $FBK 0
Panel 939.7 342.5 3 3 $FBK 0
Panel 658.5 342.5 3 3 $FBK 0

Txt 680 396 '①失败后回到构建 N09→N08' 18 '#FDE68A'
Txt 600 312 '②检查发现问题后修复 N10→N08' 18 '#FDE68A'

# 7. layer ruler
for ($i = 0; $i -lt 11; $i++) {
  $bx = $COLX[$i] + $NW / 2 - 23
  Box $bx 790 46 24 '#1A2438' '#2E3C54' 1 8
  TxtC ($COLX[$i] + $NW / 2) 794 ('L' + ($i + 1)) 18 '#94A3B8'
}

# 8. nodes on top so every arrow tip stays outside its target box
foreach ($n in $nodes) {
  $x = $COLX[$n.col]; $y = $ROWY[$n.row]
  if ($n.id -eq 'N08') {
    Box $x $y $NW $NH $N8_FILL $N8_BORD 1.5 10
    TxtC ($x + $NW / 2) ($y + 9) $n.id 22 $N8_ID ' fontStyle="BOLD"'
  }
  else {
    Box $x $y $NW $NH $N_FILL $N_BORD 1.5 10
    TxtC ($x + $NW / 2) ($y + 9) $n.id 22 $N_ID ' fontStyle="BOLD"'
  }
  TxtC ($x + $NW / 2) ($y + 37) $n.label 22 $N_LAB ' fontStyle="BOLD"'
}

# 9. in-figure explanation of both feedback relations
Box 40 856 740 96 '#111A2B' '#26334A' 1 12
Txt 60 870 '① 失败后回到构建：反馈边 N09 → N08（虚线）' 18 '#FDE68A'
Txt 60 896 '首轮渲染 N09 判定失败时，沿虚线回到 DSL 构建 N08 改稿，' 18 '#CBD5E1'
Txt 60 922 '再进入 N09 重新渲染。该回边单列虚线图例，不参与 DAG 拓扑排序。' 18 '#CBD5E1'
Box 820 856 740 96 '#111A2B' '#26334A' 1 12
Txt 840 870 '② 检查发现问题后修复：反馈边 N10 → N08（虚线）' 18 '#FDE68A'
Txt 840 896 '视觉检查 N10 发现需改结构的问题时，沿虚线回到 N08 修复，' 18 '#CBD5E1'
Txt 840 922 '改完再走 N09–N12 渲染与回归；局部问题则在 N11 问题修复内闭环。' 18 '#CBD5E1'

L '    </Stack>'
L '  </Container>'
L '</Snapshot>'

$utf8 = New-Object System.Text.UTF8Encoding($false)
$dslPath = Join-Path $TMP 'v01.snapshot'
[System.IO.File]::WriteAllText($dslPath, $sb.ToString(), $utf8)
"wrote $dslPath  (" + (Get-Item $dslPath).Length + " bytes)"

# ------------------------------------------------------------------ audit json
$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

$nodeObjs = @()
foreach ($n in $nodes) {
  $id = $n.id
  $role = 'main single-lane'
  if ($n.row -eq 0) { $role = 'upper parallel lane' }
  if ($n.row -eq 2) { $role = 'lower parallel lane' }
  $nodeObjs += @{
    id            = $id
    label         = $n.label
    layer         = $layer[$id]
    column        = $layer[$id]
    row           = $n.row + 1
    in_degree     = @($inN[$id]).Count
    out_degree    = @($outN[$id]).Count
    in_neighbors   = @($inN[$id])
    out_neighbors  = @($outN[$id])
    position      = @{ left = $COLX[$n.col]; top = $ROWY[$n.row]; width = $NW; height = $NH }
    layout_role   = $role
  }
}

$layerObjs = @()
for ($l = 1; $l -le $LAYERS; $l++) {
  $mem = @()
  foreach ($n in $nodes) { if ($layer[$n.id] -eq $l) { $mem += $n.id } }
  $layerObjs += @{
    layer        = $l
    column       = $l
    nodes        = $mem
    node_count   = @($mem).Count
    is_parallel  = (@($mem).Count -gt 1)
    x_range      = @{ left = $COLX[$l - 1]; right = $COLX[$l - 1] + $NW }
    center_y     = @(256, 516, 736)
  }
}

$pathObjs = @()
foreach ($p in $longest) {
  $pathObjs += @{ nodes = @($p); node_count = @($p).Count; edge_count = (@($p).Count - 1) }
}

$audit = [ordered]@{
  task_id        = 'A06'
  title          = '十四节点依赖图与反馈回路'
  source         = 'tasks/A06-dependency-graph/inputs/graph.json'
  generated_at   = $now
  timezone       = 'Asia/Shanghai (UTC+08:00)'
  canvas         = @{ width = 1600; height = 1000; background = $BG }
  counts         = @{
    node_count        = @($nodes).Count
    solid_edge_count  = @($solid).Count
    feedback_edge_count = @($feedback).Count
    topological_layer_count = $LAYERS
  }
  topological_layers = @{
    method = 'longest-path layering over solid_edges only: layer(n) = 1 + max(layer(p) for p in solid predecessors), sources = 1. Computed by Bellman-Ford relaxation until fixed point.'
    excluded_from_ordering = 'feedback_edges (N09>N08, N10>N08) were never fed into this computation'
    layer_count = $LAYERS
    layers = $layerObjs
    ordering_statement = 'Every solid edge goes from a lower layer to a strictly higher layer, so no prerequisite edge points at a past layer.'
  }
  nodes = $nodeObjs
  longest_prerequisite_path = @{
    metric = 'node count (edge count = node count - 1)'
    max_node_count = $MAXLEN
    solution_count = @($pathObjs).Count
    note = '多解：最高拓扑层为 L11，且存在贯穿全部 11 层的先决路径，因此最长为 11 个节点 / 10 条边。下列为全部等长解。'
    solutions = $pathObjs
  }
  feedback_edges = @(
    @{
      edge = @('N09', 'N08')
      meaning = '失败后回到构建'
      participates_in_dag_ordering = $false
      rendered_as = 'dashed line (dash 9 / gap 6, thickness 2.5) + solid arrowhead, colour #FB923C'
      dedicated_legend_entry = @{ left = 520; text_left = 568; text = '虚线箭头：反馈关系（不参与拓扑排序与布局）' }
      route = @{
        segments = @(
          @{ type = 'vertical';   x = 800;   y_from = 480; y_to = 424 }
          @{ type = 'horizontal'; y = 424;   x_from = 800; x_to = 696 }
          @{ type = 'vertical';   x = 696;   y_from = 424; y_to = 480 }
        )
        arrow_tip = @{ x = 696; y = 480; direction = 'down (0,+1)' }
        enters_node = 'N08 top edge at x=696'
      }
      in_figure_label = @{ text = '①失败后回到构建 N09→N08'; left = 680; top = 396; font_size = 18 }
      in_figure_explanation = @{ card_left = 40; card_top = 856; card_width = 740; card_height = 96; lines = @(
        '① 失败后回到构建：反馈边 N09 → N08（虚线）',
        '首轮渲染 N09 判定失败时，沿虚线回到 DSL 构建 N08 改稿，',
        '再进入 N09 重新渲染。该回边单列虚线图例，不参与 DAG 拓扑排序。') }
    },
    @{
      edge = @('N10', 'N08')
      meaning = '检查发现问题后修复'
      participates_in_dag_ordering = $false
      rendered_as = 'dashed line (dash 9 / gap 6, thickness 2.5) + solid arrowhead, colour #FB923C'
      dedicated_legend_entry = @{ left = 520; text_left = 568; text = '虚线箭头：反馈关系（不参与拓扑排序与布局）' }
      route = @{
        segments = @(
          @{ type = 'vertical';   x = 941.2; y_from = 480; y_to = 344 }
          @{ type = 'horizontal'; y = 344;   x_from = 941.2; x_to = 660 }
          @{ type = 'vertical';   x = 660;   y_from = 344; y_to = 480 }
        )
        arrow_tip = @{ x = 660; y = 480; direction = 'down (0,+1)' }
        enters_node = 'N08 top edge at x=660'
      }
      in_figure_label = @{ text = '②检查发现问题后修复 N10→N08'; left = 600; top = 312; font_size = 18 }
      in_figure_explanation = @{ card_left = 820; card_top = 856; card_width = 740; card_height = 96; lines = @(
        '② 检查发现问题后修复：反馈边 N10 → N08（虚线）',
        '视觉检查 N10 发现需改结构的问题时，沿虚线回到 N08 修复，',
        '改完再走 N09–N12 渲染与回归；局部问题则在 N11 问题修复内闭环。') }
    }
  )
  layout = @{
    column_rule = 'x = 40 + (layer-1) * 141.2, node width 108, gap 33.2 -> 11 columns spanning 40..1560'
    row_rule    = 'y = 220 / 480 / 700, node height 72; row 0 and row 2 are the parallel lanes, row 1 is the single main lane'
    column_bands = @{ left = 32; right = 1568; top = 204; height = 572; color = $BAND }
    long_range_edge = @{
      edge = @('N04', 'N13')
      route = 'up from N04 top (376.4,220) -> y=172 -> right to x=1364.8 -> down into N13 top (1364.8,480)'
      never_runs_leftward = $true
      label = @{ text = '跨层先决：N04 数据计算 → N13 产物校验（计算结果直接用于交付前校验）'; left = 400; top = 182; font_size = 18 }
      why_routed_above = 'Routing above the graph keeps the whole run left-to-right, so the edge cannot be read as pointing back to an earlier layer; the feedback lanes sit below it (y=424 and y=344) so their verticals never cross it.'
    }
    crossing_policy = 'Edges only meet at shared endpoints. Feedback verticals stop at their own lane, so N09/N10 risers never cross a lane they do not own; edge entry x on N08 are 625 (N07), 660 (N10), 696 (N09) so no two arrows share a point.'
    line_pressure_avoidance = 'Long edges are side-routed (elbow above the graph) instead of drawn as a straight diagonal, so no line passes over a node label.'
  }
  verification_targets = @(
    '1600x1000 canvas',
    'all 14 node ids AND labels rendered',
    '16 solid edges all travel to a strictly later layer',
    '2 feedback edges dashed + dedicated legend, absent from the DAG computation',
    'crossing-without-junction never implies a dependency: no two lines cross at all in this layout',
    'node fontSize >= 22, annotation fontSize >= 18'
  )
}

$json = $audit | ConvertTo-Json -Depth 14
$json = [System.Text.RegularExpressions.Regex]::Replace($json, '\\u([0-9a-fA-F]{4})', {
  param($m) [char][System.Convert]::ToInt32($m.Groups[1].Value, 16)
})
$auditPath = Join-Path $OUT 'graph-audit.json'
[System.IO.File]::WriteAllText($auditPath, $json + "`r`n", $utf8)
"wrote $auditPath  (" + (Get-Item $auditPath).Length + " bytes)"
"layers=$LAYERS  longest=$MAXLEN  solutions=" + @($pathObjs).Count
foreach ($p in $pathObjs) { "  " + ($p -join ' -> ') }
