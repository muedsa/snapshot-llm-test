# A08 route solver.
#  - parses floor.txt (26x18), never writes to tasks/
#  - BFS distance field from the target
#  - greedy reconstruction that prefers (a) not re-tracing cells already used
#    by earlier legs, (b) keeping the current direction, (c) fixed dir order
#  - emits paths.json with cell-centre sequences, per-leg steps/metres and
#    connectivity checks
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$T    = "$root\tmp\$RUN\A08"
$O    = "$root\outputs\$RUN\A08"
$utf8 = New-Object System.Text.UTF8Encoding($false)

$raw = [System.IO.File]::ReadAllLines("$T\floor.txt")
$H = $raw.Count; $W = $raw[0].Length
if ($W -ne 26 -or $H -ne 18) { throw "expected 26x18, got ${W}x${H}" }

$tile   = New-Object 'char[,]' $W, $H
$marker = @{}
$wallCount = 0; $floorCount = 0
for ($y = 0; $y -lt $H; $y++) {
  $row = $raw[$y]
  if ($row.Length -ne $W) { throw "row $y length $($row.Length)" }
  for ($x = 0; $x -lt $W; $x++) {
    $ch = $row[$x]
    $tile[$x, $y] = $ch
    if ($ch -eq '#') { $wallCount++ } else { $floorCount++ }
    if ($ch -notin @('#', '.')) {
      $k = [string]$ch
      if ($marker.ContainsKey($k)) { throw "duplicate marker $k" }
      $marker[$k] = @($x, $y)
    }
  }
}
function Test-Walk([int]$x, [int]$y) {
  if ($x -lt 0 -or $y -lt 0 -or $x -ge $W -or $y -ge $H) { return $false }
  return ($tile[$x, $y] -ne '#')
}
# order matters for tie-breaking: right, down, up, left
$DIR = @( @(1,0), @(0,1), @(0,-1), @(-1,0) )

# BFS distance-to-target field over the 4-connected walkable graph
function Get-DistField($target) {
  $n = $W * $H
  $d = New-Object int[] $n
  for ($i = 0; $i -lt $n; $i++) { $d[$i] = -1 }
  $q = New-Object System.Collections.Queue
  $sid = $target[1] * $W + $target[0]
  $d[$sid] = 0; $q.Enqueue($sid)
  while ($q.Count -gt 0) {
    $id = $q.Dequeue()
    $cx = $id % $W; $cy = [math]::Floor($id / $W)
    for ($k = 0; $k -lt 4; $k++) {
      $nx = $cx + $DIR[$k][0]; $ny = $cy + $DIR[$k][1]
      if (-not (Test-Walk $nx $ny)) { continue }
      $nid = $ny * $W + $nx
      if ($d[$nid] -ge 0) { continue }
      $d[$nid] = $d[$id] + 1
      $q.Enqueue($nid)
    }
  }
  return ,$d
}

# walk from -> to using the field, avoiding cells in $used where possible
function Get-Path($from, $to, $used) {
  $d = Get-DistField $to
  $startId = $from[1] * $W + $from[0]
  if ($d[$startId] -lt 0) { throw "no path $($from -join ',') -> $($to -join ',')" }
  $path = New-Object System.Collections.ArrayList
  [void]$path.Add(@($from[0], $from[1]))
  $cx = $from[0]; $cy = $from[1]; $cd = -1
  $guard = 0
  while ($cx -ne $to[0] -or $cy -ne $to[1]) {
    $guard++; if ($guard -gt 2000) { throw "runaway walk" }
    $cur = $d[$cy * $W + $cx]
    $best = $null; $bestScore = $null
    for ($k = 0; $k -lt 4; $k++) {
      $nx = $cx + $DIR[$k][0]; $ny = $cy + $DIR[$k][1]
      if (-not (Test-Walk $nx $ny)) { continue }
      if ($d[$ny * $W + $nx] -ne ($cur - 1)) { continue }
      $retrace = if ($used.Contains("$nx,$ny")) { 0 } else { 1 }
      $turn    = if ($cd -ge 0 -and $k -ne $cd) { 0 } else { 1 }
      # prefer fresh cells, then straight-on, then DIR order
      $score = @($retrace, $turn, (3 - $k))
      if ($null -eq $bestScore -or
          $score[0] -gt $bestScore[0] -or
          ($score[0] -eq $bestScore[0] -and $score[1] -gt $bestScore[1]) -or
          ($score[0] -eq $bestScore[0] -and $score[1] -eq $bestScore[1] -and $score[2] -gt $bestScore[2])) {
        $best = @($nx, $ny, $k); $bestScore = $score
      }
    }
    if ($null -eq $best) { throw "dead end at $cx,$cy" }
    $cx = $best[0]; $cy = $best[1]; $cd = $best[2]
    [void]$path.Add(@($cx, $cy))
  }
  return ,$path.ToArray()
}

function Get-Segments($path) {
  # collapse the walk into straight runs. Consecutive runs share their end/start
  # cell so the polyline has no gaps.
  $runs = New-Object System.Collections.ArrayList
  $run  = New-Object System.Collections.ArrayList
  [void]$run.Add($path[0])
  for ($i = 1; $i -lt $path.Count; $i++) {
    $curX = $path[$i][0] - $path[$i-1][0]
    $curY = $path[$i][1] - $path[$i-1][1]
    if ($run.Count -ge 2) {
      $pPrev = $run[$run.Count - 2]
      $prevX = $path[$i-1][0] - $pPrev[0]
      $prevY = $path[$i-1][1] - $pPrev[1]
      if ($prevX -eq $curX -and $prevY -eq $curY) {
        [void]$run.Add($path[$i])
        continue
      }
      # direction changed: close the run at path[i-1] and start a new one there
      $finished = [object[]]$run.ToArray()
      [void]$runs.Add($finished)
      $run = New-Object System.Collections.ArrayList
      [void]$run.Add($path[$i-1])
      [void]$run.Add($path[$i])
    } else {
      [void]$run.Add($path[$i])
    }
  }
  $finished = [object[]]$run.ToArray()
  [void]$runs.Add($finished)
  return ,[object[]]$runs.ToArray()
}

function Test-Adjacent($path) {
  for ($i = 1; $i -lt $path.Count; $i++) {
    $dx = [math]::Abs($path[$i][0] - $path[$i-1][0])
    $dy = [math]::Abs($path[$i][1] - $path[$i-1][1])
    if (($dx + $dy) -ne 1) { return $false }
  }
  return $true
}
function Test-AllWalkable($path) {
  foreach ($p in $path) { if (-not (Test-Walk $p[0] $p[1])) { return $false } }
  return $true
}

# ---------------------------------------------------------------- solve ----
$S = $marker['S']; $E = $marker['E']
$ZA = $marker['A']; $ZB = $marker['B']; $ZC = $marker['C']; $ZD = $marker['D']
$CELL_M = 2

# $used tracks ONLY cells already used by route 2 itself, so:
#   - route 2 is allowed to share stretches with route 1 (the brief asks for
#     overlapping segments that stay traceable for both routes)
#   - route 2 never retraces its own earlier leg (ambiguous arrows)
$used = New-Object 'System.Collections.Generic.HashSet[string]'
$route1 = Get-Path $S $E $used

$legA = Get-Path $S $ZB $used
foreach ($p in $legA) { [void]$used.Add("$($p[0]),$($p[1])") }
$legB = Get-Path $ZB $ZD $used
foreach ($p in $legB) { [void]$used.Add("$($p[0]),$($p[1])") }
$legC = Get-Path $ZD $E $used

# route 2 = A + B + C with the shared waypoint cells de-duplicated
$route2 = New-Object System.Collections.ArrayList
foreach ($p in $legA) { [void]$route2.Add($p) }
foreach ($p in ($legB | Select-Object -Skip 1)) { [void]$route2.Add($p) }
foreach ($p in ($legC | Select-Object -Skip 1)) { [void]$route2.Add($p) }
$route2 = [object[]]($route2.ToArray())

# cell-centre pixel coordinates (grid origin + half cell) - cell is filled in
# by gen.ps1 from the same layout constants, here we only store grid coords
# plus a derived centre so paths.json stands alone.
$CELL = 44
$GX = 48; $GY = 116           # grid origin (top-left of cell 0,0) - MUST match gen.ps1
function Centre([int]$x, [int]$y) {
  $cx = $GX + $x * $CELL + $CELL / 2
  $cy = $GY + $y * $CELL + $CELL / 2
  return ,@($cx, $cy)
}

function New-Leg($label, $fromId, $toId, $from, $to, $path) {
  $pts = @(); foreach ($p in $path) { $pts += ,@($p[0], $p[1]) }
  $cpts = @(); foreach ($p in $path) { $c = Centre $p[0] $p[1]; $cpts += ,@($c[0], $c[1]) }
  $steps = $path.Count - 1
  $runs = Get-Segments $path
  $runList = @()
  foreach ($r in $runs) {
    $pts2 = @(); foreach ($p in $r) { $pts2 += ,@($p[0], $p[1]) }
    $runList += [ordered]@{ from = @($r[0][0], $r[0][1]); to = @($r[$r.Count-1][0], $r[$r.Count-1][1]); cells = $pts2; run_steps = $r.Count - 1 }
  }
  return [ordered]@{
    label = $label
    from_id = $fromId; to_id = $toId
    from_xy = @($from[0], $from[1]); to_xy = @($to[0], $to[1])
    grid_cells = $pts
    cell_centres_px = $cpts
    steps = $steps
    metres = $steps * $CELL_M
    manhattan = ([math]::Abs($to[0]-$from[0]) + [math]::Abs($to[1]-$from[1]))
    is_shortest_possible = ($steps -eq ([math]::Abs($to[0]-$from[0]) + [math]::Abs($to[1]-$from[1])))
    straight_runs = $runList
    checks = [ordered]@{
      contiguous_4_neighbour = (Test-Adjacent $path)
      all_cells_walkable = (Test-AllWalkable $path)
      steps_equal_cell_count_minus_1 = ($steps -eq $path.Count - 1)
      endpoints_match = (($path[0][0] -eq $from[0]) -and ($path[0][1] -eq $from[1]) -and ($path[$path.Count-1][0] -eq $to[0]) -and ($path[$path.Count-1][1] -eq $to[1]))
      crosses_no_wall = (Test-AllWalkable $path)
    }
  }
}

$r1 = New-Leg 'route-1' 'S' 'E' $S $E $route1
$la = New-Leg 'route-2-leg-a' 'S' 'B' $S $ZB $legA
$lb = New-Leg 'route-2-leg-b' 'B' 'D' $ZB $ZD $legB
$lc = New-Leg 'route-2-leg-c' 'D' 'E' $ZD $E $legC

$steps2 = $la.steps + $lb.steps + $lc.steps

# self-overlap of route 2 with itself (the D->E leg may retrace leg b)
$r2set = New-Object 'System.Collections.Generic.HashSet[string]'
$r2dup = 0
foreach ($p in $route2) { if (-not $r2set.Add("$($p[0]),$($p[1])")) { $r2dup++ } }

# overlap between route 1 and route 2 (cells used by both)
$r1set = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($p in $route1) { [void]$r1set.Add("$($p[0]),$($p[1])") }
$overlap = @()
$seenOv = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($p in $route2) {
  $k = "$($p[0]),$($p[1])"
  if ($r1set.Contains($k) -and $seenOv.Add($k)) { $overlap += ,@($p[0], $p[1]) }
}

# zone reachability sanity: every marker must be reachable from S
$reach = [ordered]@{ S = 0 }
foreach ($k in @('E','A','B','C','D')) {
  $df = Get-DistField $marker[$k]
  $reach[$k] = $df[$S[1] * $W + $S[0]]
}

# --- topology audit --------------------------------------------------------
# connected components over the walkable graph
$comp = New-Object int[] ($W * $H)
for ($i = 0; $i -lt $comp.Count; $i++) { $comp[$i] = -1 }
$ncomp = 0
for ($y = 0; $y -lt $H; $y++) {
  for ($x = 0; $x -lt $W; $x++) {
    if ((-not (Test-Walk $x $y)) -or ($comp[$y * $W + $x] -ge 0)) { continue }
    $ncomp++
    $q = New-Object System.Collections.Queue
    $q.Enqueue($y * $W + $x); $comp[$y * $W + $x] = $ncomp
    while ($q.Count -gt 0) {
      $id = $q.Dequeue(); $cx = $id % $W; $cy = [math]::Floor($id / $W)
      for ($k = 0; $k -lt 4; $k++) {
        $nx = $cx + $DIR[$k][0]; $ny = $cy + $DIR[$k][1]
        if (-not (Test-Walk $nx $ny)) { continue }
        $nid = $ny * $W + $nx
        if ($comp[$nid] -ge 0) { continue }
        $comp[$nid] = $ncomp; $q.Enqueue($nid)
      }
    }
  }
}
# doorway = walkable cell with exactly two walkable neighbours, and they are
# opposite each other (a one-cell-wide opening through a wall)
$doorList = @()
for ($y = 0; $y -lt $H; $y++) {
  for ($x = 0; $x -lt $W; $x++) {
    if (-not (Test-Walk $x $y)) { continue }
    $ok = @()
    for ($k = 0; $k -lt 4; $k++) { if (Test-Walk ($x + $DIR[$k][0]) ($y + $DIR[$k][1])) { $ok += $k } }
    if ($ok.Count -eq 2 -and (($ok[0] -eq 0 -and $ok[1] -eq 3) -or ($ok[0] -eq 1 -and $ok[1] -eq 2))) {
      $doorList += ,@($x, $y)
    }
  }
}
function Test-IsDoor([int]$x, [int]$y) {
  foreach ($d in $doorList) { if ($d[0] -eq $x -and $d[1] -eq $y) { return $true } }
  return $false
}
$doorsOnR1 = @(); foreach ($p in $route1) { if (Test-IsDoor $p[0] $p[1]) { $doorsOnR1 += ,@($p[0], $p[1]) } }
$doorsOnR2 = @(); foreach ($p in $route2) { if (Test-IsDoor $p[0] $p[1]) { $doorsOnR2 += ,@($p[0], $p[1]) } }

Write-Host "route1 steps=$($r1.steps)  route2 steps=$steps2"
Write-Host "legA=$($la.steps) legB=$($lb.steps) legC=$($lc.steps)"
Write-Host "overlap cells r1/r2=$($overlap.Count)  r2 self-dup=$r2dup"

$doc = [ordered]@{
  task_id = 'A08'
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone = 'Asia/Shanghai (UTC+08:00)'
  source = [ordered]@{ floor = 'tasks/A08-accessible-wayfinding/inputs/floor.txt'; legend = 'tasks/A08-accessible-wayfinding/inputs/legend.json'; copied_to = 'tmp/run-20261002-220723-mimo/A08/' }
  grid = [ordered]@{
    columns = $W; rows = $H; origin = 'top-left'; cell_metres = $CELL_M
    movement = '4-neighbour only (up/down/left/right); no diagonals; walls block'
    wall_cells = $wallCount; walkable_cells = $floorCount
    coordinates = 'zero-based (x,y)'
    canvas = [ordered]@{ width = 1560; height = 1080; cell_px = $CELL; grid_origin_px = @($GX, $GY) }
  }
  markers = [ordered]@{}
  zone_names = [ordered]@{ A = '材料实验'; B = '结构剧场'; C = '光影工坊'; D = '作品巡览'; S = '入口'; E = '出口' }
  routes = [ordered]@{
    route_1 = $r1
    route_2 = [ordered]@{
      label = 'route-2'; constraint = 'S -> B -> D -> E, B strictly before D, each leg shortest'
      leg_a = $la; leg_b = $lb; leg_c = $lc
      legs_joined_grid_cells = $route2 | ForEach-Object { ,@($_[0], $_[1]) }
      steps = $steps2
      metres = $steps2 * $CELL_M
      self_retraced_cells = $r2dup
    }
  }
  connectivity = [ordered]@{
    marker_distance_from_S = $reach
    walkable_connected_components = $ncomp
    walkable_cells_all_one_component = ($ncomp -eq 1)
    doorway_cells = $doorList
    doorway_count = $doorList.Count
    doors_crossed_by_route_1 = $doorsOnR1
    doors_crossed_by_route_2 = $doorsOnR2
    route_1_vs_route_2_shared_cells = $overlap
    route_1_vs_route_2_shared_cell_count = $overlap.Count
    route_2_self_retraced_cells = $r2dup
    all_markers_reachable_from_S = (@($reach.Values | Where-Object { $_ -lt 0 }).Count -eq 0)
  }
}
$mk = $doc.markers
foreach ($k in @('S','E','A','B','C','D')) { $mk[$k] = [ordered]@{ id = $k; xy = @($marker[$k][0], $marker[$k][1]); centre_px = (Centre $marker[$k][0] $marker[$k][1]) } }

$json = $doc | ConvertTo-Json -Depth 12
$json = [regex]::Replace($json, '\\u([0-9a-fA-F]{4})', { param($m) [char][int]::Parse($m.Groups[1].Value, 'HexNumber') })
[IO.File]::WriteAllText("$O\paths.json", $json, $utf8)
Write-Host "paths.json -> $O\paths.json ($([System.IO.File]::ReadAllBytes("$O\paths.json").Length) bytes)"
