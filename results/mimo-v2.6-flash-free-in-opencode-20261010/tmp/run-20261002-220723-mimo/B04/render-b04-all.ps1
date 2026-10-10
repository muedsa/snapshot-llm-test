# render-b04-all.ps1 -- render one round for all 10 B04 cases
param([string]$Round = "r01")
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp = Join-Path $root 'tmp\run-20261002-220723-mimo\B04'
$out = Join-Path $root 'outputs\run-20261002-220723-mimo\B04'
$render = Join-Path $tmp 'render-b04.ps1'

if (!(Test-Path $out)) { New-Item -ItemType Directory -Force -Path $out | Out-Null }

for ($i = 1; $i -le 10; $i++) {
    $cid = 'case-{0:d2}' -f $i
    $dsl = Join-Path (Join-Path $tmp $cid) ($Round + '.snapshot')
    $png = Join-Path (Join-Path $tmp $cid) ($Round + '.png')
    if (!(Test-Path $dsl)) { Write-Output "SKIP $cid (no $Round.snapshot)"; continue }
    & $render -DslPath $dsl -OutPath $png -TaskId B04 -ReqId ('B04-rend-' + $cid + '-' + $Round) -CaseId $cid
    if ($LASTEXITCODE -ne 0) { Write-Output "ERROR $cid" }
}
