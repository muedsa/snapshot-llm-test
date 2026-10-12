# A07 final-review verification: re-parses the DELIVERED .snapshot files and
# pixel-scans the DELIVERED .png files. Nothing here trusts the generator.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$o    = "$root\outputs\$RUN\A07"
Add-Type -AssemblyName System.Drawing

$report = [ordered]@{}
$checks = New-Object System.Collections.ArrayList

function OK($k, $v, $detail) { [void]$checks.Add([ordered]@{ check = $k; pass = [bool]$v; value = $v; detail = $detail }) }

# ---------- 1. pairing + raw bytes ----------
$mapPng = "$o\network-map.png"; $mapDsl = "$o\network-map.snapshot"
$cardPng = "$o\travel-card.png"; $cardDsl = "$o\travel-card.snapshot"
foreach ($p in @($mapPng, $mapDsl, $cardPng, $cardDsl, "$o\routes.json")) { OK ("exists " + (Split-Path $p -Leaf)) (Test-Path $p) $p }

function PngInfo($path) {
  $b = [System.Drawing.Bitmap]::FromFile($path)
  try { return [ordered]@{ w = $b.Width; h = $b.Height } } finally { $b.Dispose() }
}
$mi = PngInfo $mapPng; $ci = PngInfo $cardPng
OK 'map size = 1600x1000' (($mi.w -eq 1600) -and ($mi.h -eq 1000)) "$($mi.w)x$($mi.h)"
OK 'card size = 720x1280' (($ci.w -eq 720) -and ($ci.h -eq 1280)) "$($ci.w)x$($ci.h)"

# DSL that produced each PNG must be byte-identical to the delivered .snapshot
foreach ($pair in @(@("$root\tmp\$RUN\A07\map-v01.snapshot", $mapDsl), @("$root\tmp\$RUN\A07\card-v02.snapshot", $cardDsl))) {
  $a = (Get-FileHash $pair[0] -Algorithm SHA256).Hash
  $b = (Get-FileHash $pair[1] -Algorithm SHA256).Hash
  OK ("rendered DSL == delivered " + (Split-Path $pair[1] -Leaf)) ($a -eq $b) $a
}
# no BOM
foreach ($p in @($mapDsl, $cardDsl)) {
  $bytes = [System.IO.File]::ReadAllBytes($p)
  $bom = ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
  OK ("no BOM " + (Split-Path $p -Leaf)) (-not $bom) "first=$($bytes[0])"
}

# ---------- 2. map DSL structural checks ----------
$mapXml = Get-Content $mapDsl -Raw -Encoding UTF8
$cardXml = Get-Content $cardDsl -Raw -Encoding UTF8

# every text node fontSize >= 20
foreach ($pair in @(@('map', $mapXml), @('card', $cardXml))) {
  $fs = [regex]::Matches($pair[1], 'fontSize="([\d.]+)"') | ForEach-Object { [double]$_.Groups[1].Value }
  $min = ($fs | Measure-Object -Minimum).Minimum
  OK ("$($pair[0]) min fontSize >= 20") ($min -ge 20) "min=$min count=$($fs.Count)"
}

# 16 station labels, ids + names all present
$want = @(
  @('S01','松林'), @('S02','北门'), @('S03','书院'), @('S04','中心'),
  @('S05','东桥'), @('S06','江湾'), @('S07','西港'), @('S08','工坊'),
  @('S09','花园'), @('S10','南门'), @('S11','会展'), @('S12','机场'),
  @('S13','石溪'), @('S14','公园'), @('S15','剧院'), @('S16','研究所')
)
$miss = @()
foreach ($w in $want) { if ($mapXml -notmatch ('>' + $w[0] + ' ' + $w[1] + '<')) { $miss += $w[0] } }
OK 'all 16 station id+name labels present on map' ($miss.Count -eq 0) ("missing: " + ($miss -join ','))

# accessibility: exactly 4 non-accessible, and they are exactly S03/S05/S09/S14
$SQ = [string][char]0x25A0   # filled square   = accessible
$HL = [string][char]0x25A1   # hollow square   = not accessible
$order = @('S01','S02','S03','S04','S05','S06','S07','S08','S09','S10','S11','S12','S13','S14','S15','S16')
$noAcc = @(); $unknown = @(); $marks = 0
for ($n = 0; $n -lt $order.Count; $n++) {
  $id = $order[$n]
  $i = $mapXml.IndexOf(('>' + $id + ' '))
  if ($i -lt 0) { $unknown += "$id=absent"; continue }
  $end = $mapXml.Length
  $leg = $mapXml.IndexOf('>图例<')   # legend repeats station ids; it is not part of any label block
  if ($leg -gt 0) { $end = $leg }
  if ($n + 1 -lt $order.Count) {
    $nxt = $mapXml.IndexOf(('>' + $order[$n + 1] + ' '), $i + 1)
    if ($nxt -gt 0 -and $nxt -lt $end) { $end = $nxt }
  }
  $seg = $mapXml.Substring($i, $end - $i)
  $hasH = $seg.Contains($HL); $hasF = $seg.Contains($SQ)
  if ($hasH -and -not $hasF) { $noAcc += $id; $marks++ }
  elseif ($hasF -and -not $hasH) { $marks++ }
  else { $unknown += "$id=both-or-none" }
}
OK 'every station label carries exactly one accessibility mark' ($marks -eq 16) "marks=$marks odd=$($unknown -join ',')"
OK 'exactly 4 non-accessible stations, = S03/S05/S09/S14' ((($noAcc | Sort-Object) -join ',') -eq 'S03,S05,S09,S14') (($noAcc | Sort-Object) -join ',')
OK '16 station id+name label blocks found' (($order | Where-Object { $mapXml.IndexOf(('>' + $_ + ' ')) -ge 0 }).Count -eq 16) ''

# line letters present (R/B/G) and non-colour encoding stated
OK 'line letter badges present' (($mapXml -match '>R<') -and ($mapXml -match '>B<') -and ($mapXml -match '>G<')) 'R/B/G'
OK 'line names spelled out in legend' (($mapXml -match 'R 红线') -and ($mapXml -match 'B 蓝线') -and ($mapXml -match 'G 绿线')) ''
OK 'non-geographic stated on map' ($mapXml -match '非地理比例') ''
OK '45/90 statement on map' ($mapXml -match '0°/45°/90°') ''
OK 'crossing-without-station note' ($mapXml -match '非换乘') ''
OK 'legend explains accessibility' (($mapXml -match '无障碍') -and ($mapXml -match '非无障碍')) ''

# ---------- 3. map geometry: every drawn segment is 0/45/90 ----------
$segs = [regex]::Matches($mapXml, '<Transform matrix="\(([-\d\.]+),([-\d\.]+),0,0,([-\d\.]+),([-\d\.]+),') |
  ForEach-Object { ,@([double]$_.Groups[1].Value, [double]$_.Groups[2].Value) }
$badAngle = 0; $segCount = 0
$LINE_W = 9.0
foreach ($sg in $segs) {
  $c = $sg[0]; $s = $sg[1]
  $segCount++
  $ang = [Math]::Abs([Math]::Atan2($s, $c) * 180.0 / [Math]::PI)
  $okA = ($ang -lt 0.01) -or ([Math]::Abs($ang - 45) -lt 0.01) -or ([Math]::Abs($ang - 90) -lt 0.01) -or
         ([Math]::Abs($ang - 135) -lt 0.01) -or ([Math]::Abs($ang - 180) -lt 0.01) -or
         ([Math]::Abs($ang + 45) -lt 0.01) -or ([Math]::Abs($ang + 90) -lt 0.01) -or ([Math]::Abs($ang + 135) -lt 0.01)
  if (-not $okA) { $badAngle++ }
}
OK 'every drawn segment is a multiple of 45 deg' ($badAngle -eq 0) "segments=$segCount bad=$badAngle"

# ---------- 4. pixel scan: station dots present at the designed coordinates ----------
$ST = [ordered]@{
  S01 = @(120,470); S02 = @(290,470); S03 = @(460,470); S04 = @(610,470)
  S05 = @(610,730); S06 = @(610,860); S07 = @(1040,470); S08 = @(870,470)
  S09 = @(470,330); S10 = @(300,330); S11 = @(130,330); S12 = @(790,860)
  S13 = @(870,210); S14 = @(870,340); S15 = @(740,600); S16 = @(450,890)
}
$mb = [System.Drawing.Bitmap]::FromFile($mapPng)
try {
  $absent = @()
  foreach ($k in @($ST.Keys)) {
    $p = $mb.GetPixel([int]$ST[$k][0], [int]$ST[$k][1])
    if (-not ($p.R -gt 235 -and $p.G -gt 235 -and $p.B -gt 235)) { $absent += "$k($($p.R),$($p.G),$($p.B))" }
  }
  OK 'all 16 station dot centres are white in the delivered png' ($absent.Count -eq 0) ($absent -join ' ')

  # label boxes must contain no line-coloured pixel (line colours: R F43F5E, B 3B82F6, G 22C55E)
  $LB = @(
    @('S01',55,496,185,542), @('S02',225,496,355,542), @('S03',395,496,525,542),
    @('S04',628,384,758,430), @('S05',644,742,774,788), @('S06',545,886,675,932),
    @('S07',975,396,1105,442), @('S08',856,506,986,552), @('S09',405,244,535,290),
    @('S10',235,244,365,290), @('S11',65,244,195,290), @('S12',725,886,855,932),
    @('S13',896,188,1026,234), @('S14',896,318,1026,364), @('S15',770,600,900,646),
    @('S16',385,916,515,962)
  )
  $hits = @()
  foreach ($b in $LB) {
    $hit = 0
    for ($y = [int]$b[2]; $y -le [int]$b[4]; $y++) {
      for ($x = [int]$b[1]; $x -le [int]$b[3]; $x++) {
        $p = $mb.GetPixel($x, $y)
        # line colours are #F43F5E / #3B82F6 / #22C55E. Tolerances are deliberately
        # tight: the accessible chip green #34D399 blends into a colour a looser
        # test would mistake for the G line green, which produced false positives.
        $isLine = ([Math]::Abs($p.R - 0xF4) -lt 20 -and [Math]::Abs($p.G - 0x3F) -lt 30 -and [Math]::Abs($p.B - 0x5E) -lt 30) -or
                  ([Math]::Abs($p.R - 0x3B) -lt 25 -and [Math]::Abs($p.G - 0x82) -lt 25 -and [Math]::Abs($p.B - 0xF6) -lt 20) -or
                  ([Math]::Abs($p.R - 0x22) -lt 25 -and [Math]::Abs($p.G - 0xC5) -lt 25 -and [Math]::Abs($p.B - 0x5E) -lt 25)
        if ($isLine) { $hit++ }
      }
    }
    if ($hit -gt 0) { $hits += "$($b[0])=$hit" }
  }
  OK 'no line-coloured pixel inside any station label box' ($hits.Count -eq 0) ($hits -join ' ')

  # all three line colours must actually appear
  $cnt = @{ R = 0; B = 0; G = 0 }
  for ($y = 0; $y -lt 1000; $y += 3) {
    for ($x = 0; $x -lt 1600; $x += 3) {
      $p = $mb.GetPixel($x, $y)
      if ([Math]::Abs($p.R - 0xF4) -lt 20 -and [Math]::Abs($p.G - 0x3F) -lt 30 -and [Math]::Abs($p.B - 0x5E) -lt 30) { $cnt.R++ }
      elseif ([Math]::Abs($p.R - 0x3B) -lt 25 -and [Math]::Abs($p.G - 0x82) -lt 25 -and [Math]::Abs($p.B - 0xF6) -lt 20) { $cnt.B++ }
      elseif ([Math]::Abs($p.R - 0x22) -lt 25 -and [Math]::Abs($p.G - 0xC5) -lt 25 -and [Math]::Abs($p.B - 0x5E) -lt 30) { $cnt.G++ }
    }
  }
  OK 'all three line colours present on map' (($cnt.R -gt 500) -and ($cnt.B -gt 500) -and ($cnt.G -gt 500)) ("R=$($cnt.R) B=$($cnt.B) G=$($cnt.G)")

  # 4 non-accessible stations must show an amber second line, 12 green
  $amb = 0; $grn = 0
  foreach ($b in $LB) {
    for ($y = [int]$b[2]; $y -le [int]$b[4]; $y++) {
      for ($x = [int]$b[1]; $x -le [int]$b[3]; $x++) {
        $p = $mb.GetPixel($x, $y)
        if ($p.R -gt 230 -and $p.G -gt 170 -and $p.G -lt 220 -and $p.B -lt 110) { $amb++ }
        if ($p.R -lt 130 -and $p.G -gt 190 -and $p.B -gt 130 -and $p.B -lt 210) { $grn++ }
      }
    }
  }
  OK 'amber (non-accessible) label pixels present' ($amb -gt 500) "amber=$amb"
  OK 'green (accessible) label pixels present' ($grn -gt 500) "green=$grn"
} finally { $mb.Dispose() }

# ---------- 5. card content checks ----------
$routes = Get-Content "$o\routes.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$q = $routes.queries
OK '3 queries in routes.json' ($q.Count -eq 3) "$($q.Count)"
$expect = @(
  @{ e = 6; t = 1; ok = $true  },
  @{ e = 6; t = 1; ok = $false },
  @{ e = 4; t = 1; ok = $true  }
)
for ($i = 0; $i -lt 3; $i++) {
  $r = $q[$i]
  $so = $r.shortest_ordinary
  OK ("q{0} ordinary edge_count = {1}" -f ($i + 1), $expect[$i].e) ($so.edge_count -eq $expect[$i].e) "$($so.edge_count)"
  OK ("q{0} ordinary transfer_count = {1}" -f ($i + 1), $expect[$i].t) ($so.transfer_count -eq $expect[$i].t) "$($so.transfer_count)"
  OK ("q{0} station_count = edge_count + 1" -f ($i + 1)) ($so.station_count -eq ($so.edge_count + 1)) "$($so.station_count)"
  # station_path must walk the line_segments exactly, in order, with no gaps
  $flat = @()
  for ($k2 = 0; $k2 -lt $so.line_segments.Count; $k2++) { $flat += ,@($so.line_segments[$k2].stations) }
  $rebuilt = @()
  for ($k2 = 0; $k2 -lt $flat.Count; $k2++) {
    $ss = $flat[$k2]
    if ($k2 -eq 0) { $rebuilt += $ss } else { $rebuilt += $ss[1..($ss.Count - 1)] }
  }
  $contig = (($rebuilt -join '-') -eq ($so.station_path -join '-'))
  $adj = $true
  for ($k2 = 0; $k2 -lt $so.station_path.Count - 1; $k2++) {
    $a = $so.station_path[$k2]; $b = $so.station_path[$k2 + 1]
    $linked = $false
    foreach ($ln in $routes.lines) {
      $ids = @($ln.stations)
      for ($m2 = 0; $m2 -lt $ids.Count - 1; $m2++) {
        if (($ids[$m2] -eq $a -and $ids[$m2 + 1] -eq $b) -or ($ids[$m2] -eq $b -and $ids[$m2 + 1] -eq $a)) { $linked = $true }
      }
    }
    if (-not $linked) { $adj = $false }
  }
  OK ("q{0} line_segments reassemble into station_path" -f ($i + 1)) $contig ($rebuilt -join '-')
  OK ("q{0} every consecutive station pair is a real adjacent edge" -f ($i + 1)) $adj ''
  OK ("q{0} first boarding line is not counted as a transfer" -f ($i + 1)) (($so.transfer_count) -eq ($so.line_segments.Count - 1)) "segments=$($so.line_segments.Count) transfers=$($so.transfer_count)"
  OK ("q{0} accessible verdict" -f ($i + 1)) ([bool]$r.shortest_is_accessible_journey -eq $expect[$i].ok) "$($r.shortest_is_accessible_journey)"
}
# the non-accessible journey must have a computed alternative
OK 'q2 has a separately computed shortest accessible journey' ($null -ne $q[1].shortest_accessible) ''
OK 'q2 accessible journey differs from ordinary' ($q[1].shortest_accessible -and -not $q[1].shortest_accessible.same_as_shortest_ordinary) ''
OK 'q2 accessible journey edge_count still 6' ($q[1].shortest_accessible.edge_count -eq 6) "$($q[1].shortest_accessible.edge_count)"
OK 'q2 accessible journey transfer_count = 2' ($q[1].shortest_accessible.transfer_count -eq 2) "$($q[1].shortest_accessible.transfer_count)"
# every journey REPORTED AS ACCESSIBLE must have accessible transfer stations;
# the ordinary journey of q2 is expected to fail this, and must say so.
$badT = @(); $silent = @()
for ($i = 0; $i -lt $q.Count; $i++) {
  $r = $q[$i]
  $j = $r.shortest_accessible
  if ($null -ne $j) {
    foreach ($ts in $j.transfer_stations) {
      $st = $routes.stations | Where-Object { $_.id -eq $ts }
      if ($st -and -not $st.accessible) { $badT += "q$($i+1)-accessible:$ts" }
    }
  }
  $o2 = $r.shortest_ordinary
  if ($r.shortest_is_accessible_journey) {
    foreach ($ts in $o2.transfer_stations) {
      $st = $routes.stations | Where-Object { $_.id -eq $ts }
      if ($st -and -not $st.accessible) { $badT += "q$($i+1)-ordinary:$ts" }
    }
  } else {
    if (-not $r.accessible_blocked_reason) { $silent += "q$($i+1)-noreason" }
  }
}
OK 'every journey reported accessible has only accessible transfers' ($badT.Count -eq 0) ($badT -join ',')
OK 'every non-accessible verdict carries an explicit reason' ($silent.Count -eq 0) ($silent -join ',')
OK 'q2 ordinary journey is correctly rejected (transfer at a non-accessible station)' ((-not $q[1].shortest_is_accessible_journey) -and ($q[1].accessible_blocked_reason -match 'S05')) "$($q[1].accessible_blocked_reason)"

# card carries the three journeys + verdicts
foreach ($k in @('6 区间', '1 次换乘', '7 站', '4 区间', '5 站', '无障碍旅程：可以', '无障碍旅程：不可以', '最短无障碍旅程')) {
  OK ("card shows '$k'") ($cardXml -match [regex]::Escape($k)) ''
}

$report.checks = $checks
$report.summary = [ordered]@{
  total  = $checks.Count
  passed = @($checks | Where-Object { $_.pass }).Count
  failed = @($checks | Where-Object { -not $_.pass }).Count
}
$json = $report | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText("$o\map-audit.json", $json, (New-Object System.Text.UTF8Encoding($false)))
"PASS $($report.summary.passed) / $($report.summary.total)   FAIL $($report.summary.failed)"
@($checks | Where-Object { -not $_.pass }) | ForEach-Object { "  FAIL $($_.check) -> $($_.detail)" }
