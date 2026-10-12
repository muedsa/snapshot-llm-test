# promote-b05.ps1 -- copy round-02 PNG + DSL verbatim into outputs/.../B05/case-NN
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B05'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B05'
if (!(Test-Path $out)) { New-Item -ItemType Directory -Force -Path $out | Out-Null }

$done = 0
for ($i = 1; $i -le 10; $i++) {
  $cid = 'case-{0:d2}' -f $i
  $d = Join-Path $out $cid
  if (!(Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
  Copy-Item (Join-Path $tmp "$cid\r02.png")        (Join-Path $d 'final.png') -Force
  Copy-Item (Join-Path $tmp "$cid\r02.snapshot")   (Join-Path $d 'final.snapshot') -Force
  [IO.File]::WriteAllText((Join-Path $d '.round'), '2', (New-Object Text.UTF8Encoding($false)))
  $done++
}
"promoted $done cases -> $out"
