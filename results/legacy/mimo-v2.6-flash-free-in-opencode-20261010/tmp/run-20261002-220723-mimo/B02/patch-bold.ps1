$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$enc = New-Object System.Text.UTF8Encoding($false)
$files = @(
  "$root\tmp\run-20261002-220723-mimo\B02\lib-b02.ps1",
  "$root\tmp\run-20261002-220723-mimo\B02\gen-b02-a.ps1"
)
foreach ($f in $files) {
  $t = [IO.File]::ReadAllText($f)
  $t = $t.Replace("'bold'", "'BOLD'")
  $t = $t.Replace("'0,0'", "'TOP_LEFT'")
  $t = $t.Replace("'1,1'", "'BOTTOM_RIGHT'")
  [IO.File]::WriteAllText($f, $t, $enc)
}
Write-Output '--- remaining bold literals ---'
Select-String -Path "$root\tmp\run-20261002-220723-mimo\B02\*.ps1" -Pattern "'bold'" | ForEach-Object { $_.Filename + ':' + $_.LineNumber }
Write-Output '--- remaining coordinate gradients ---'
Select-String -Path "$root\tmp\run-20261002-220723-mimo\B02\*.ps1" -Pattern "'0,0'|'1,1'" | ForEach-Object { $_.Filename + ':' + $_.LineNumber + ': ' + $_.Line.Trim() }
Write-Output '--- BOLD count ---'
(Select-String -Path "$root\tmp\run-20261002-220723-mimo\B02\*.ps1" -Pattern "'BOLD'").Count
