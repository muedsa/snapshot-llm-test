# A07 route solver - BFS on (station, current_line) states.
# Cost is lexicographic: (edge_count, transfer_count). Edge = one hop between adjacent stations.
# transfer = changing riding line; first boarding does not count. Stations are undirected, all hops equal.
# With accessibleOnly=$true the origin, the destination AND every station where a line change happens
# must be accessible; plain pass-through of a non-accessible station stays legal.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$IN   = Join-Path $ROOT 'tasks\A07-transit-topology\inputs\network.json'
$OUT  = Join-Path $ROOT "outputs\$RUN\A07"
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

$net = Get-Content $IN -Raw -Encoding UTF8 | ConvertFrom-Json

$acc = @{}; $nm = @{}; $order = @()
foreach ($s in $net.stations) { $acc[$s.id] = [bool]$s.accessible; $nm[$s.id] = $s.name; $order += $s.id }

$adj = @{}
foreach ($s in $net.stations) { $adj[$s.id] = @() }
$edgeLine = @{}
foreach ($l in $net.lines) {
  $st = @($l.stations)
  for ($i = 0; $i -lt $st.Count - 1; $i++) {
    $a = $st[$i]; $b = $st[$i + 1]
    $adj[$a] += @{ to = $b; line = $l.id }
    $adj[$b] += @{ to = $a; line = $l.id }
    $edgeLine["$a>$b"] = $l.id
    $edgeLine["$b>$a"] = $l.id
  }
}
$lineName = @{}; $lineStations = @{}
foreach ($l in $net.lines) { $lineName[$l.id] = $l.name; $lineStations[$l.id] = @($l.stations) }

# ---- transfers + line segments from a plain station path ----
function Segments([array]$path) {
  $segs = @()
  $cur = $null; $buf = @()
  for ($i = 0; $i -lt $path.Count - 1; $i++) {
    $lid = $edgeLine["$($path[$i])>$($path[$i+1])"]
    if ($null -eq $cur) { $cur = $lid; $buf = @($path[$i], $path[$i+1]) }
    elseif ($lid -eq $cur) { $buf += $path[$i + 1] }
    else { $segs += @{ line = $cur; stations = $buf }; $cur = $lid; $buf = @($path[$i], $path[$i+1]) }
  }
  if ($null -ne $cur) { $segs += @{ line = $cur; stations = $buf } }
  return ,$segs
}
function TransferCount([array]$segs) {
  if (@($segs).Count -le 1) { return 0 }
  return (@($segs).Count - 1)
}
function TransferStations([array]$segs) {
  $t = @()
  for ($i = 1; $i -lt @($segs).Count; $i++) { $t += $segs[$i].stations[0] }
  return ,$t
}

# ---- BFS: state = station + current line ('' before first boarding) ----
function Solve([string]$from, [string]$to, [bool]$accessibleOnly) {
  if ($accessibleOnly) {
    if (-not $acc[$from]) { return $null }
    if (-not $acc[$to])   { return $null }
  }
  $startKey = $from + '|'
  $frontier = New-Object System.Collections.Hashtable
  $frontier[$startKey] = @{ station = $from; line = ''; path = @($from); transfers = 0; boardingAt = $null }
  $depth = 0
  $guard = 0
  while ($frontier.Count -gt 0) {
    $guard++; if ($guard -gt 500) { throw 'BFS did not converge' }
    # goal check: any state sitting on $to with minimal depth
    $best = $null
    foreach ($k in @($frontier.Keys)) {
      $st = $frontier[$k]
      if ($st.station -eq $to) {
        if ($null -eq $best -or $st.transfers -lt $best.transfers) { $best = $st }
      }
    }
    if ($null -ne $best) {
      $segs = Segments $best.path
      return @{
        from = $from; to = $to
        station_path = @($best.path)
        edge_count = $depth
        station_count = @($best.path).Count
        line_segments = $segs
        transfer_count = (TransferCount $segs)
        transfer_stations = (TransferStations $segs)
        accessible_only = $accessibleOnly
      }
    }
    # expand
    $next = New-Object System.Collections.Hashtable
    foreach ($k in @($frontier.Keys)) {
      $st = $frontier[$k]
      foreach ($e in $adj[$st.station]) {
        $ns = $e.to; $nl = $e.line
        # first boarding: no transfer. line change happens AT $st.station.
        $t = $st.transfers
        $boardAt = $st.boardingAt
        if ($st.line -ne '' -and $nl -ne $st.line) {
          $t = $t + 1
          $boardAt = $st.station
          if ($accessibleOnly -and -not $acc[$st.station]) { continue }   # cannot transfer here
        }
        $key = $ns + '|' + $nl
        # same depth: keep the representative with the fewest transfers so far. Future cost depends
        # only on (station, current line), so retaining the min-transfer representative is optimal.
        if ($next.ContainsKey($key)) { if ($next[$key].transfers -le $t) { continue } }
        $next[$key] = @{ station = $ns; line = $nl; path = (@($st.path) + $ns); transfers = $t; boardingAt = $boardAt }
      }
    }
    $frontier = $next
    $depth++
  }
  return $null
}

$lineLetters = @{}
foreach ($l in $net.lines) { $lineLetters[$l.id] = $l.id }

$results = @()
foreach ($q in $net.queries) {
  $plain = Solve $q.from $q.to $false
  $plainAccOk = $true
  $why = $null
  # evaluate whether the plain shortest journey is itself a legal accessible journey
  $ts = $plain.transfer_stations
  if (-not $acc[$q.from])  { $plainAccOk = $false; $why = "起点 $($q.from) $($nm[$q.from]) 非无障碍" }
  elseif (-not $acc[$q.to]) { $plainAccOk = $false; $why = "终点 $($q.to) $($nm[$q.to]) 非无障碍" }
  else {
    foreach ($t in $ts) {
      if (-not $acc[$t]) { $plainAccOk = $false; $why = "换乘站 $t $($nm[$t]) 非无障碍" ; break }
    }
  }
  $accRoute = $null
  if ($plainAccOk) { $accRoute = $plain } else { $accRoute = Solve $q.from $q.to $true }

  $results += @{
    from = $q.from; from_name = $nm[$q.from]; to = $q.to; to_name = $nm[$q.to]
    shortest = $plain
    shortest_is_accessible_journey = $plainAccOk
    shortest_blocked_reason = $why
    accessible_journey = $accRoute
    accessible_journey_differs = (-not $plainAccOk)
  }
}

# ---- assemble routes.json ----
$stationObjs = @()
foreach ($id in $order) {
  $lines = @()
  foreach ($l in $net.lines) { if (@($l.stations) -contains $id) { $lines += $l.id } }
  $stationObjs += @{ id = $id; name = $nm[$id]; accessible = $acc[$id]; lines = $lines; is_transfer = (@($lines).Count -gt 1) }
}
$lineObjs = @()
foreach ($l in $net.lines) {
  $lineObjs += @{ id = $l.id; name = $l.name; stations = @($l.stations); station_count = @($l.stations).Count; edge_count = (@($l.stations).Count - 1) }
}

$routeObjs = @()
foreach ($r in $results) {
  $s = $r.shortest
  $a = $r.accessible_journey
  if ($null -ne $a) {
    $accObj = @{
      same_as_shortest_ordinary = (-not $r.accessible_journey_differs)
      station_path = $a.station_path
      station_names = @($a.station_path | ForEach-Object { $nm[$_] })
      edge_count = $a.edge_count
      station_count = $a.station_count
      line_segments = @($a.line_segments | ForEach-Object { @{ line = $_.line; line_name = $lineName[$_.line]; stations = $_.stations } })
      transfer_count = $a.transfer_count
      transfer_stations = $a.transfer_stations
      constraints = '起点/终点/换乘站均 accessible=true；途经非无障碍站允许，仅不得作为起终点或换乘站'
    }
  } else {
    $accObj = $null
  }
  $routeObjs += @{
    query = @{ from = $r.from; from_name = $r.from_name; to = $r.to; to_name = $r.to_name }
    shortest_ordinary = @{
      station_path = $s.station_path
      station_names = @($s.station_path | ForEach-Object { $nm[$_] })
      edge_count = $s.edge_count
      station_count = $s.station_count
      line_segments = @($s.line_segments | ForEach-Object { @{ line = $_.line; line_name = $lineName[$_.line]; stations = $_.stations } })
      transfer_count = $s.transfer_count
      transfer_stations = $s.transfer_stations
      method = 'BFS over undirected equal-weight hops, minimal edge_count first, ties broken by fewest line changes'
    }
    shortest_is_accessible_journey = $r.shortest_is_accessible_journey
    accessible_blocked_reason = $r.shortest_blocked_reason
    shortest_accessible = $accObj
  }
}

$doc = [ordered]@{
  task_id = 'A07'
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone = 'Asia/Shanghai (UTC+08:00)'
  source = 'tasks/A07-transit-topology/inputs/network.json'
  definitions = @{
    edge = '相邻站之间的一段区间（两个相邻站 = 1 条边）。站数 = 边数 + 1，两者不可混用。'
    transfer = '改变乘坐线路；第一次上车不算换乘。换乘次数 = 线路段数 - 1。'
    walkable = '所有线路无向、可双向乘坐，相邻站耗时相同，因此最少站间边数用等权 BFS 求解。'
    accessible_journey = '起点、终点、以及每一次换乘所在的站都必须 accessible=true。仅作为途经站通过非无障碍站是允许的（可乘车通过）。'
    non_geographic = '本图为示意拓扑图，不按地理比例；站间连线只使用 0°/45°/90° 三种走向。'
  }
  topology = @{
    station_count = @($net.stations).Count
    line_count = @($net.lines).Count
    edge_count = (@($net.lines) | ForEach-Object { @($_.stations).Count - 1 } | Measure-Object -Sum).Sum
    transfer_stations = @($stationObjs | Where-Object { $_.is_transfer } | ForEach-Object { $_.id })
    non_accessible_stations = @($stationObjs | Where-Object { -not $_.accessible } | ForEach-Object { $_.id })
    crossing_rule = '三条线两两的共站集合：R∩B={S04}, R∩G={S05}, B∩G={S08}，全部是有站名的换乘站；不存在"两线相交但无共站"的情况。布局上也刻意让线路之间不发生无站交叉——所有线条交汇点都是换乘站。'
  }
  stations = $stationObjs
  lines = $lineObjs
  queries = $routeObjs
}

$json = $doc | ConvertTo-Json -Depth 16
$json = [System.Text.RegularExpressions.Regex]::Replace($json, '\\u([0-9a-fA-F]{4})', { param($m) [char][System.Convert]::ToInt32($m.Groups[1].Value, 16) })
$p = Join-Path $OUT 'routes.json'
[System.IO.File]::WriteAllText($p, $json + "`r`n", (New-Object System.Text.UTF8Encoding($false)))
"wrote $p (" + (Get-Item $p).Length + " bytes)"

foreach ($r in $results) {
  $s = $r.shortest; $a = $r.accessible_journey
  ""
  "Q  $($r.from) $($r.from_name) -> $($r.to) $($r.to_name)"
  "   ordinary : " + ($s.station_path -join ' > ') + "   edges=" + $s.edge_count + "  transfers=" + $s.transfer_count + "  via " + (($s.line_segments | ForEach-Object { $_.line }) -join ',')
  $blk = ''
  if ($r.shortest_blocked_reason) { $blk = '  (' + $r.shortest_blocked_reason + ')' }
  "   accessible-journey? " + $r.shortest_is_accessible_journey + $blk
  if ($null -eq $a) { "   accessible alternative: NONE" }
  else { "   accessible : " + ($a.station_path -join ' > ') + "   edges=" + $a.edge_count + "  transfers=" + $a.transfer_count + "  same=" + (-not $r.accessible_journey_differs) }
}
