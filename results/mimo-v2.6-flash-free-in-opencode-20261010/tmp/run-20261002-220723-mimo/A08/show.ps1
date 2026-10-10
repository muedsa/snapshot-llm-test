$root=if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$O="$root\outputs\run-20261002-220723-mimo\A08"
$j = Get-Content "$O\paths.json" -Raw -Encoding UTF8 | ConvertFrom-Json
function Show($name, $cells) {
  $s = ($cells | ForEach-Object { "($($_[0]),$($_[1]))" }) -join ' '
  Write-Host "$name [$($cells.Count) cells]"
  Write-Host "  $s"
}
Show 'route1' $j.routes.route_1.grid_cells
Show 'legA  ' $j.routes.route_2.leg_a.grid_cells
Show 'legB  ' $j.routes.route_2.leg_b.grid_cells
Show 'legC  ' $j.routes.route_2.leg_c.grid_cells
Write-Host "route1 steps=$($j.routes.route_1.steps) m=$($j.routes.route_1.metres) manhattan=$($j.routes.route_1.manhattan) shortest=$($j.routes.route_1.is_shortest_possible)"
Write-Host "r2 steps=$($j.routes.route_2.steps) m=$($j.routes.route_2.metres) selfdup=$($j.routes.route_2.self_retraced_cells)"
foreach ($n in @('leg_a','leg_b','leg_c')) {
  $l = $j.routes.route_2.$n
  Write-Host "$n steps=$($l.steps) m=$($l.metres) manhattan=$($l.manhattan) shortest=$($l.is_shortest_possible) runs=$($l.straight_runs.Count)"
}
Write-Host "overlap count=$($j.connectivity.route_1_vs_route_2_shared_cell_count)"
Write-Host ("overlap: " + (($j.connectivity.route_1_vs_route_2_shared_cells | ForEach-Object { "($($_[0]),$($_[1]))" }) -join ' '))
Write-Host "components=$($j.connectivity.walkable_connected_components) doors=$($j.connectivity.doorway_count)"
Write-Host ("doors: " + (($j.connectivity.doorway_cells | ForEach-Object { "($($_[0]),$($_[1]))" }) -join ' '))
Write-Host ("r1 doors: " + (($j.connectivity.doors_crossed_by_route_1 | ForEach-Object { "($($_[0]),$($_[1]))" }) -join ' '))
Write-Host ("r2 doors: " + (($j.connectivity.doors_crossed_by_route_2 | ForEach-Object { "($($_[0]),$($_[1]))" }) -join ' '))
Write-Host "reach: " + (($j.connectivity.marker_distance_from_S.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ')
