# A16 - inspect a candidate DSL before rendering it.
param([string]$Dsl = 'corrected-report-v01.snapshot')
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
$p = Join-Path $TMP $Dsl
$b = [IO.File]::ReadAllBytes($p)
$head = ($b[0..([math]::Min(5, $b.Length - 1))] -join ',')
$txt = [IO.File]::ReadAllText($p)
Write-Output ("file      : {0}" -f $p)
Write-Output ("bytes     : {0}" -f $b.Length)
Write-Output ("first bytes: {0}  (65,60,60 = '<<S' so no BOM)" -f $head)
Write-Output ("lines     : {0}" -f ((Get-Content $p).Count))
$tags = @('<Snapshot', '<Container', '<Positioned', '<Text ', '<Image', '<Transform', 'fontFamily', 'letterSpacing')
foreach ($t in $tags) {
  $n = ([regex]::Matches($txt, [regex]::Escape($t))).Count
  Write-Output ("  count {0,-14} = {1}" -f $t.Trim(), $n)
}
$bad = @('<Image ', '<Transform')
foreach ($t in $bad) {
  if ($txt.Contains($t)) { Write-Output ("!! forbidden tag present: {0}" -f $t) }
}
if ($txt.Contains([char]0xFEFF)) { Write-Output '!! BOM present' }
# font sizes actually used
$sizes = @()
foreach ($m in [regex]::Matches($txt, 'fontSize="([0-9.]+)"')) { $sizes += [double]$m.Groups[1].Value }
if ($sizes.Count -gt 0) {
  $sizes = $sizes | Sort-Object
  Write-Output ("fontSize count={0} min={1} max={2}" -f $sizes.Count, $sizes[0], ($sizes[$sizes.Count - 1]))
}
Write-Output '--- first 6 lines ---'
(Get-Content $p -TotalCount 6) | ForEach-Object { Write-Output ('  ' + $_) }
