$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$TMP  = "$root\tmp\$RUN\A11"
$famList = @(Get-Content "$TMP\fonts-0001.txt" -Encoding UTF8 | Where-Object { $_.Trim() -ne '' })
$sl = @($famList[0..4])
Write-Host ('subset count=' + $sl.Count + ' totalchars=' + (($sl | Measure-Object -Property Length -Sum).Sum))

Write-Host '--- default depth, see actual output ---'
$j = $sl | ConvertTo-Json -Compress
Write-Host ('type=' + $j.GetType().FullName + ' len=' + $j.Length)
$preview = $j
if ($preview.Length -gt 500) { $preview = $preview.Substring(0, 500) + ' ...TRUNC...' }
Write-Host $preview

Write-Host '--- depth 3 ---'
$sw = [Diagnostics.Stopwatch]::StartNew()
$j3 = $sl | ConvertTo-Json -Depth 3 -Compress
Write-Host ('depth3 ok ' + $sw.ElapsedMilliseconds + ' ms len=' + $j3.Length)

Write-Host '--- depth 5 ---'
$sw = [Diagnostics.Stopwatch]::StartNew()
$j5 = $sl | ConvertTo-Json -Depth 5 -Compress
Write-Host ('depth5 ok ' + $sw.ElapsedMilliseconds + ' ms len=' + $j5.Length)

Write-Host '--- depth 7 ---'
$sw = [Diagnostics.Stopwatch]::StartNew()
$j7 = $sl | ConvertTo-Json -Depth 7 -Compress
Write-Host ('depth7 ok ' + $sw.ElapsedMilliseconds + ' ms len=' + $j7.Length)

Write-Host '--- depth 10 ---'
$sw = [Diagnostics.Stopwatch]::StartNew()
$j10 = $sl | ConvertTo-Json -Depth 10 -Compress
Write-Host ('depth10 ok ' + $sw.ElapsedMilliseconds + ' ms len=' + $j10.Length)
Write-Host 'bench6 done'
