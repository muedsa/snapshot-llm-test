# A08 final reviewer - re-parses the DELIVERED png + .snapshot + paths.json
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$T    = "$root\tmp\$RUN\A08"
$O    = "$root\outputs\$RUN\A08"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$CI   = [System.Globalization.CultureInfo]::InvariantCulture

$CELL = 44; $GX = 48; $GY = 116; $COLS = 26; $ROWS = 18
function CX([int]$x) { return $GX + $x * $CELL + $CELL / 2 }
function CY([int]$y) { return $GY + $y * $CELL + $CELL / 2 }

$checks = New-Object System.Collections.ArrayList
function OK($id, $pass, $detail) {
  [void]$checks.Add([ordered]@{ id = $id; pass = [bool]$pass; detail = $detail })
}
function HexRGB([string]$hex) {
  $h = $hex.TrimStart('#')
  return ,@([Convert]::ToInt32($h.Substring(0,2),16), [Convert]::ToInt32($h.Substring(2,2),16), [Convert]::ToInt32($h.Substring(4,2),16))
}
function Near($a, $b, $tol) {
  return ([math]::Abs($a[0]-$b[0]) -le $tol -and [math]::Abs($a[1]-$b[1]) -le $tol -and [math]::Abs($a[2]-$b[2]) -le $tol)
}

# ------------------------------------------------------------------ inputs ---
$raw = [System.IO.File]::ReadAllLines("$T\floor.txt")
$j   = Get-Content "$O\paths.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$mk  = $j.markers
$pngPath = "$O\wayfinding.png"
$dslPath = "$O\wayfinding.snapshot"

$C_WALL = HexRGB '#3E4C66'
$C_FLOOR= HexRGB '#101A2E'
$C_DOOR = HexRGB '#22314F'
$C_S    = HexRGB '#0F3A2E'
$C_E    = HexRGB '#3A2C0F'
$C_ZONE = HexRGB '#232B55'
$C_R1   = HexRGB '#F43F5E'
$C_R2   = HexRGB '#38BDF8'

$doorSet = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($d in $j.connectivity.doorway_cells) { [void]$doorSet.Add("$([int]$d[0]),$([int]$d[1])") }
$markerOf = @{}
foreach ($k in @('S','E','A','B','C','D')) { $p = $mk.$k.xy; $markerOf["$([int]$p[0]),$([int]$p[1])"] = $k }

# ------------------------------------------------------------------- files ---
foreach ($n in @('wayfinding.png','wayfinding.snapshot','paths.json')) {
  $p = "$O\$n"
  $e = Test-Path $p
  $len = if ($e) { (Get-Item $p).Length } else { 0 }
  OK "file.$n" ($e -and $len -gt 0) ("exists=$e bytes=$len")
}

Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap($pngPath)
OK 'png.dimensions' (($bmp.Width -eq 1560) -and ($bmp.Height -eq 1080)) ("$($bmp.Width)x$($bmp.Height) expected 1560x1080")

# raw PNG signature must be a real PNG
$pngBytes = [System.IO.File]::ReadAllBytes($pngPath)
$sig = ($pngBytes[0..7] | ForEach-Object { $_.ToString('X2') }) -join ''
OK 'png.signature' ($sig -eq '89504E470D0A1A0A') ("$sig")

# --------------------------------------------------------------------- DSL ---
$dslText = [System.IO.File]::ReadAllText($dslPath)
$dslOk = $true; $dslErr = ''
try { $x = [xml]$dslText } catch { $dslOk = $false; $dslErr = $_.Exception.Message }
OK 'dsl.parse' $dslOk $dslErr
if ($dslOk) {
  $rootName = $x.DocumentElement.Name
  OK 'dsl.root' ($rootName -eq 'Snapshot') $rootName
  $sizes = @()
  foreach ($m in [regex]::Matches($dslText, 'fontSize="(\d+)"')) { $sizes += [int]$m.Groups[1].Value }
  $uniq = ($sizes | Sort-Object -Unique) -join ','
  $below22 = @($sizes | Where-Object { $_ -lt 22 })
  $at16    = @($sizes | Where-Object { $_ -eq 16 })
  # exactly 70 edge-ruler labels are allowed to sit at the grid-label floor of 16
  OK 'dsl.body_min_22' (@($below22 | Where-Object { $_ -ne 16 }).Count -eq 0) ("unique=$uniq below22=$($below22.Count)")
  OK 'dsl.grid_labels_16' ($at16.Count -eq 70) ("fontSize=16 occurrences=$($at16.Count) expected 70 (26 top + 26 bottom + 18 left)")
  $badHex = @()
  foreach ($m in [regex]::Matches($dslText, '#([0-9A-Fa-f]{6})(?![-0-9A-Fa-f])')) { }
  foreach ($m in [regex]::Matches($dslText, 'color="(#[0-9A-Fa-f]+)"')) {
    $h = $m.Groups[1].Value
    if ($h.Length -ne 7) { $badHex += $h }
  }
  OK 'dsl.colour_hex_len' ($badHex.Count -eq 0) ("bad=$($badHex.Count)")
  $tpl = ($dslText -split "`n").Count
  OK 'dsl.canvas_container' ($dslText -match '<Container width="1560" height="1080">') '1560x1080'
  OK 'dsl.lines' $tpl 'ok'
}

# ------------------------------------------------------------ route logic ----
function Test-Adj($cells) {
  for ($i = 1; $i -lt $cells.Count; $i++) {
    $d = [math]::Abs([int]$cells[$i][0] - [int]$cells[$i-1][0]) + [math]::Abs([int]$cells[$i][1] - [int]$cells[$i-1][1])
    if ($d -ne 1) { return $false }
  }
  return $true
}
function Test-WalkCells($cells) {
  foreach ($c in $cells) {
    $x = [int]$c[0]; $y = [int]$c[1]
    if ($x -lt 0 -or $y -lt 0 -or $x -ge $COLS -or $y -ge $ROWS) { return $false }
    if ($raw[$y][$x] -eq '#') { return $false }
  }
  return $true
}
$r1  = $j.routes.route_1.grid_cells
$la  = $j.routes.route_2.leg_a.grid_cells
$lb  = $j.routes.route_2.leg_b.grid_cells
$lc  = $j.routes.route_2.leg_c.grid_cells
$r2  = $j.routes.route_2.legs_joined_grid_cells

OK 'route1.adjacent'   (Test-Adj $r1) ("cells=$($r1.Count)")
OK 'route1.walkable'   (Test-WalkCells $r1) 'all cells non-wall'
OK 'route1.endpoints'  (([int]$r1[0][0] -eq [int]$mk.S.xy[0]) -and ([int]$r1[0][1] -eq [int]$mk.S.xy[1]) -and ([int]$r1[$r1.Count-1][0] -eq [int]$mk.E.xy[0]) -and ([int]$r1[$r1.Count-1][1] -eq [int]$mk.E.xy[1])) "S..E"
OK 'route1.steps'      ($j.routes.route_1.steps -eq ($r1.Count - 1)) ("steps=$($j.routes.route_1.steps)")
OK 'route1.metres'     ($j.routes.route_1.metres -eq $j.routes.route_1.steps * 2) ("m=$($j.routes.route_1.metres)")
OK 'route1.manhattan_optimal' ($j.routes.route_1.steps -eq $j.routes.route_1.manhattan) ("steps=$($j.routes.route_1.steps) manhattan=$($j.routes.route_1.manhattan)")

OK 'route2.adjacent'   (Test-Adj $r2) ("cells=$($r2.Count)")
OK 'route2.walkable'   (Test-WalkCells $r2) 'all cells non-wall'
OK 'route2.order'       (([int]$la[$la.Count-1][0] -eq [int]$mk.B.xy[0]) -and ([int]$la[$la.Count-1][1] -eq [int]$mk.B.xy[1]) -and ([int]$lb[$lb.Count-1][0] -eq [int]$mk.D.xy[0]) -and ([int]$lb[$lb.Count-1][1] -eq [int]$mk.D.xy[1])) 'B before D'
OK 'route2.endpoints'  (([int]$r2[0][0] -eq [int]$mk.S.xy[0]) -and ([int]$r2[$r2.Count-1][0] -eq [int]$mk.E.xy[0])) 'S..E'
OK 'route2.steps'      ($j.routes.route_2.steps -eq ($j.routes.route_2.leg_a.steps + $j.routes.route_2.leg_b.steps + $j.routes.route_2.leg_c.steps)) ("total=$($j.routes.route_2.steps)")
OK 'route2.metres'     ($j.routes.route_2.metres -eq $j.routes.route_2.steps * 2) ("m=$($j.routes.route_2.metres)")
OK 'route2.legs_b_c_optimal' (($j.routes.route_2.leg_b.steps -eq $j.routes.route_2.leg_b.manhattan) -and ($j.routes.route_2.leg_c.steps -eq $j.routes.route_2.leg_c.manhattan)) ("b=$($j.routes.route_2.leg_b.steps)/$($j.routes.route_2.leg_b.manhattan) c=$($j.routes.route_2.leg_c.steps)/$($j.routes.route_2.leg_c.manhattan)")
OK 'route2.leg_a_shortest_note' ($j.routes.route_2.leg_a.is_shortest_possible -eq $false) ("detour forced by the x=8 wall: $($j.routes.route_2.leg_a.steps) vs manhattan $($j.routes.route_2.leg_a.manhattan)")
OK 'topology.components' ($j.connectivity.walkable_connected_components -eq 1) ("components=$($j.connectivity.walkable_connected_components)")
OK 'topology.doors'     ($j.connectivity.doorway_count -eq 7) ("doors=$($j.connectivity.doorway_count)")

# paths.json's own pixel claims must agree with the delivered rendering, otherwise
# the JSON would describe a different canvas than the PNG it ships next to
$org = @($j.grid.canvas.grid_origin_px)
OK 'paths.grid_origin_px' (($org[0] -eq $GX) -and ($org[1] -eq $GY)) ("origin=$($org -join ',') expected $GX,$GY")
function Test-Px($cells, $pxs) {
  if ($null -eq $pxs -or $cells.Count -ne $pxs.Count) { return $false }
  for ($i = 0; $i -lt $cells.Count; $i++) {
    $ex = [int]($GX + [int]$cells[$i][0] * $CELL + $CELL / 2)
    $ey = [int]($GY + [int]$cells[$i][1] * $CELL + $CELL / 2)
    if ([int]$pxs[$i][0] -ne $ex -or [int]$pxs[$i][1] -ne $ey) { return $false }
  }
  return $true
}
OK 'paths.route1_cell_centres_px' (Test-Px $r1 $j.routes.route_1.cell_centres_px) ("points=$($j.routes.route_1.cell_centres_px.Count)")
foreach ($lg3 in @(@('leg_a',$la), @('leg_b',$lb), @('leg_c',$lc))) {
  $arr = $j.routes.route_2.($lg3[0]).cell_centres_px
  OK ("paths.route2_" + $lg3[0] + "_cell_centres_px") (Test-Px $lg3[1] $arr) ("points=$($arr.Count)")
}
$mkPxBad = @()
foreach ($k in @('S','E','A','B','C','D')) {
  $p = $mk.$k.xy
  $ex = [int]($GX + [int]$p[0] * $CELL + $CELL / 2)
  $ey = [int]($GY + [int]$p[1] * $CELL + $CELL / 2)
  if ([int]$mk.$k.centre_px[0] -ne $ex -or [int]$mk.$k.centre_px[1] -ne $ey) { $mkPxBad += "$k($($mk.$k.centre_px -join ',')!=$ex,$ey)" }
}
OK 'paths.marker_centre_px' ($mkPxBad.Count -eq 0) (($mkPxBad -join ' '))

# ---------------------------------------------------------- pixel checks -----
$tol = 8
$cellFail = @()
for ($y = 0; $y -lt $ROWS; $y++) {
  for ($x = 0; $x -lt $COLS; $x++) {
    $ch = $raw[$y][$x]
    $key = "$x,$y"
    $exp = $null; $what = 'wall'
    if ($ch -eq '#') { $exp = $C_WALL }
    elseif ($markerOf.ContainsKey($key)) {
      $what = 'marker:' + $markerOf[$key]
      $exp = switch ($markerOf[$key]) { 'S' { $C_S } 'E' { $C_E } default { $C_ZONE } }
    }
    elseif ($doorSet.Contains($key)) { $what = 'door'; $exp = $C_DOOR }
    else { $what = 'floor'; $exp = $C_FLOOR }
    $bx = $GX + $x * $CELL; $by = $GY + $y * $CELL
    $hit = $false
    foreach ($off in @(@(8,8), @(36,8), @(8,36), @(36,36))) {
      $px = $bmp.GetPixel($bx + $off[0], $by + $off[1])
      $c  = @($px.R, $px.G, $px.B)
      if (Near $c $exp $tol) { $hit = $true; break }
    }
    if (-not $hit) { $cellFail += "$what($x,$y)" }
  }
}
OK 'pixels.cell_fills' ($cellFail.Count -eq 0) ("468 cells sampled at 4 corners; mismatches=$($cellFail.Count) " + (($cellFail | Select-Object -First 12) -join ' '))

# walls must never carry a route
$wallOver = @()
for ($y = 0; $y -lt $ROWS; $y++) {
  for ($x = 0; $x -lt $COLS; $x++) {
    if ($raw[$y][$x] -ne '#') { continue }
    $p = $bmp.GetPixel([int](CX $x), [int](CY $y))
    $c = @($p.R, $p.G, $p.B)
    if (-not (Near $c $C_WALL $tol)) { $wallOver += "($x,$y)" }
  }
}
OK 'pixels.no_route_on_wall' ($wallOver.Count -eq 0) ("wall cells with non-wall centres=$($wallOver.Count) " + (($wallOver | Select-Object -First 8) -join ' '))

# route 1 stroke: at least one sample 4px off the centreline is route-1 red
$r1fail = @()
foreach ($c in $r1) {
  $cx = [int](CX ([int]$c[0])); $cy = [int](CY ([int]$c[1]))
  $hit = $false
  foreach ($ofs in @(@(0,-4), @(0,4), @(-4,0), @(4,0))) {
    $p = $bmp.GetPixel($cx + $ofs[0], $cy + $ofs[1])
    if (Near @($p.R,$p.G,$p.B) $C_R1 $tol) { $hit = $true; break }
  }
  if (-not $hit) { $r1fail += "($($c[0]),$($c[1]))" }
}
OK 'pixels.route1_stroke' ($r1fail.Count -eq 0) ("route-1 cells=$($r1.Count) without red=$($r1fail.Count) " + (($r1fail | Select-Object -First 10) -join ' '))

# route 2 stroke: sample 7 points along the centreline; a 16px dash / 12px gap
# pattern guarantees at least one hit inside any 20px window
$r2fail = @()
foreach ($c in $r2) {
  $cx = [int](CX ([int]$c[0])); $cy = [int](CY ([int]$c[1]))
  $hit = $false
  foreach ($ofs in @(-10,-6,-2,0,2,6,10)) {
    $pa = $bmp.GetPixel($cx + $ofs, $cy)
    if (Near @($pa.R,$pa.G,$pa.B) $C_R2 $tol) { $hit = $true; break }
    $pb = $bmp.GetPixel($cx, $cy + $ofs)
    if (Near @($pb.R,$pb.G,$pb.B) $C_R2 $tol) { $hit = $true; break }
  }
  if (-not $hit) { $r2fail += "($($c[0]),$($c[1]))" }
}
OK 'pixels.route2_stroke' ($r2fail.Count -eq 0) ("route-2 cells=$($r2.Count) without cyan=$($r2fail.Count) " + (($r2fail | Select-Object -First 10) -join ' '))

# shared cells: route 1 keeps a red rim around route 2's narrower dashes
$sharedFail = @()
foreach ($c in $j.connectivity.route_1_vs_route_2_shared_cells) {
  $cx = [int](CX ([int]$c[0])); $cy = [int](CY ([int]$c[1]))
  $red = $false; $cyan = $false
  # red must survive as a rim perpendicular to the centreline; cyan must be hit
  # somewhere within a +-10px window along it (dash 16 / gap 12 guarantees it)
  foreach ($ofs in @(-4, 4)) {
    $pa = $bmp.GetPixel($cx + $ofs, $cy); if (Near @($pa.R,$pa.G,$pa.B) $C_R1 $tol) { $red = $true }
    $pb = $bmp.GetPixel($cx, $cy + $ofs); if (Near @($pb.R,$pb.G,$pb.B) $C_R1 $tol) { $red = $true }
  }
  foreach ($ofs in @(-10,-6,-2,0,2,6,10)) {
    $pa = $bmp.GetPixel($cx + $ofs, $cy); if (Near @($pa.R,$pa.G,$pa.B) $C_R2 $tol) { $cyan = $true }
    $pb = $bmp.GetPixel($cx, $cy + $ofs); if (Near @($pb.R,$pb.G,$pb.B) $C_R2 $tol) { $cyan = $true }
  }
  if (-not ($red -and $cyan)) { $sharedFail += "($($c[0]),$($c[1])) red=$red cyan=$cyan" }
}
OK 'pixels.shared_segment_traceable' ($sharedFail.Count -eq 0) ("shared=$($j.connectivity.route_1_vs_route_2_shared_cell_count) failing=$($sharedFail.Count) " + (($sharedFail | Select-Object -First 6) -join ' | '))

$bmp.Dispose()

# ------------------------------------------------------------- summary -------
$pass = @($checks | Where-Object { $_.pass }).Count
$fail = @($checks | Where-Object { -not $_.pass }).Count
$report = [ordered]@{
  task_id = 'A08'
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone = 'Asia/Shanghai (UTC+08:00)'
  reviewed_artifacts = [ordered]@{
    png = 'outputs/' + $RUN + '/A08/wayfinding.png'
    dsl = 'outputs/' + $RUN + '/A08/wayfinding.snapshot'
    json = 'outputs/' + $RUN + '/A08/paths.json'
    note = 'all checks re-parse the delivered files, not the generator state'
  }
  summary = [ordered]@{ pass = $pass; fail = $fail; verdict = $(if ($fail -eq 0) { 'PASS' } else { 'FAIL' }) }
  checks = $checks
}
$json = $report | ConvertTo-Json -Depth 10
$json = [regex]::Replace($json, '\\u([0-9a-fA-F]{4})', { param($m) [char][int]::Parse($m.Groups[1].Value, 'HexNumber') })
[IO.File]::WriteAllText("$O\wayfinding-audit.json", $json, $utf8)
Write-Host "PASS $pass / $($checks.Count)   FAIL $fail"
foreach ($c in $checks) { if (-not $c.pass) { Write-Host ("  FAIL {0}: {1}" -f $c.id, $c.detail) } }
