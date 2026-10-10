# overlap-a23.ps1 - pairwise unit-box overlap check across the 6 frames.
param(
  [string]$DataPath = 'outputs\run-20261002-220723-mimo\A23\frame-data.json'
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
$utf8 = New-Object System.Text.UTF8Encoding($false)

$fd = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($DataPath, $utf8))
$U = 60
$bad = 0
Write-Output ('{0,-9} {1,7} {2,10} {3,12}  {4}' -f 'frame', 'pairs', 'overlapPx', 'fullyHidden', 'detail')
foreach ($fr in $fd.frames) {
  $pos = @{}
  foreach ($p in $fr.units) { $pos[$p.id] = $p }
  $ids = @($fd.units | ForEach-Object { $_.id })
  $pairs = 0; $opSum = 0; $hidden = @(); $det = @()
  for ($a = 0; $a -lt $ids.Count; $a++) {
    for ($b = $a + 1; $b -lt $ids.Count; $b++) {
      $p1 = $pos[$ids[$a]]; $p2 = $pos[$ids[$b]]
      $dx = [Math]::Abs($p1.x - $p2.x)
      $dy = [Math]::Abs($p1.y - $p2.y)
      if ($dx -lt $U -and $dy -lt $U) {
        $pairs++
        $ox = $U - $dx; $oy = $U - $dy
        $opSum += ($ox * $oy)
        $det += ('{0}/{1}:{2}x{3}' -f $ids[$a], $ids[$b], [int]$ox, [int]$oy)
      }
    }
  }
  # fully hidden = a unit whose box lies entirely inside the union of others (approx: inside one other)
  foreach ($id in $ids) {
    $p1 = $pos[$id]
    foreach ($oid in $ids) {
      if ($oid -eq $id) { continue }
      $p2 = $pos[$oid]
      $inside = ($p1.x -ge $p2.x -and $p1.y -ge $p2.y -and ($p1.x + $U) -le ($p2.x + $U) -and ($p1.y + $U) -le ($p2.y + $U))
      if ($inside) { $hidden += ('{0} inside {1}' -f $id, $oid); break }
    }
  }
  if ($pairs -gt 0) { $bad++ }
  $d = ''
  if ($det.Count) { $d = ($det -join '  ') }
  if ($hidden.Count) { $d = $d + '   HIDDEN: ' + ($hidden -join ', ') }
  Write-Output ('{0,-9} {1,7} {2,10} {3,12}  {4}' -f ('frame-' + ('{0:D2}' -f $fr.index)), $pairs, $opSum, $hidden.Count, $d)
}
Write-Output ''
Write-Output ('frames with overlap = {0} / 6' -f $bad)
