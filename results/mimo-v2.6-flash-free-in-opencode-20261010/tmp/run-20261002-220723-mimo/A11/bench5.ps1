$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$TMP  = "$root\tmp\$RUN\A11"
$famList = @(Get-Content "$TMP\fonts-0001.txt" -Encoding UTF8 | Where-Object { $_.Trim() -ne '' })
Write-Host ('loaded ' + $famList.Count)

Write-Host 'B1: stopwatch only'
$sw = [Diagnostics.Stopwatch]::StartNew()
Write-Host 'B1 done'

Write-Host 'B2: first 5 elements, plain ConvertTo-Json'
$sl = @($famList[0..4])
Write-Host ('  subset count=' + $sl.Count)
$j = $sl | ConvertTo-Json -Compress
Write-Host ('  B2 ok len=' + $j.Length)

Write-Host 'B3: first 5 with -Depth 10'
$j = $sl | ConvertTo-Json -Depth 10 -Compress
Write-Host ('  B3 ok len=' + $j.Length)

Write-Host 'B4: elements 0..13'
$sl = @($famList[0..13])
$j = $sl | ConvertTo-Json -Depth 10 -Compress
Write-Host ('  B4 ok len=' + $j.Length)

Write-Host 'B5: elements 14..26'
$sl = @($famList[14..26])
$j = $sl | ConvertTo-Json -Depth 10 -Compress
Write-Host ('  B5 ok len=' + $j.Length)

Write-Host 'B6: full 27'
$j = $famList | ConvertTo-Json -Depth 10 -Compress
Write-Host ('  B6 ok len=' + $j.Length)
Write-Host 'bench5 done'
