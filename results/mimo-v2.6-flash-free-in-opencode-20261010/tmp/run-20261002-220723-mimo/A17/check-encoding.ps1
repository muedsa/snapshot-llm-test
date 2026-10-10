$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$dir = Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A17'
Get-ChildItem -Path $dir -Filter 'example-0*.snapshot' | Sort-Object Name | ForEach-Object {
  $b = [IO.File]::ReadAllBytes($_.FullName)
  $bom = if ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF) { 'BOM!' } else { 'no-bom' }
  $nullbyte = ($b -contains 0)
  Write-Output ("{0}  bytes={1}  {2}  nullbytes={3}" -f $_.Name, $b.Length, $bom, $nullbyte)
}
