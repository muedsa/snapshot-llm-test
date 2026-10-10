# A16 - PNG dimension/size probe for viewing aids
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
foreach ($n in @('zoom-legend-title-v03.png', 'zoom-chart-axis-v03.png', 'zoom-profit-card-v03.png',
                 'zoom-key-card-v03.png', 'zoom-header-v03.png', 'zoom-chart-right-v03.png',
                 'view-A16-legend-720.png', 'view-A16-axis-720.png',
                 'corrected-report-v03.png')) {
  $p = Join-Path $TMP $n
  if (Test-Path $p) {
    $b = [IO.File]::ReadAllBytes($p)
    $w = ($b[16] * 16777216) + ($b[17] * 65536) + ($b[18] * 256) + $b[19]
    $h = ($b[20] * 16777216) + ($b[21] * 65536) + ($b[22] * 256) + $b[23]
    Write-Output ("{0,-34} {1}x{2,-5} {3} bytes" -f $n, $w, $h, $b.Length)
  } else {
    Write-Output ("{0,-34} MISSING" -f $n)
  }
}
