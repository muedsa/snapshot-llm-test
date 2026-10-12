$root=if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$raw=[System.IO.File]::ReadAllLines("$root\tmp\run-20261002-220723-mimo\A08\floor.txt")
$W=26;$H=18
for ($y=0; $y -lt $H; $y++) {
  $sb = New-Object System.Text.StringBuilder
  [void]$sb.Append(("row{0,2}: " -f $y))
  for ($x=0; $x -lt $W; $x++) {
    $ch = $raw[$y][$x]
    if ($ch -eq '#') { [void]$sb.Append('#') } else { [void]$sb.Append('.') }
  }
  [void]$sb.Append('   |x17=' + $raw[$y][17])
  [void]$sb.Append('   |x8=' + $raw[$y][8])
  Write-Host $sb.ToString()
}
Write-Host "--- special markers ---"
for ($y=0; $y -lt $H; $y++) {
  for ($x=0; $x -lt $W; $x++) {
    $ch = [string]$raw[$y][$x]
    if ($ch -ne '#' -and $ch -ne '.') { Write-Host "$ch at ($x,$y)" }
  }
}
