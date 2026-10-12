$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$TMP  = "$root\tmp\$RUN\A11"

Write-Host 'T1: plain string array'
$a = @('Inter', 'DejaVu Sans', 'Noto Sans CJK JP')
$sw = [Diagnostics.Stopwatch]::StartNew()
$ja = $a | ConvertTo-Json -Depth 10 -Compress
Write-Host ('T1 ok ' + $sw.ElapsedMilliseconds + ' ms len=' + $ja.Length)

Write-Host 'T2: fonts file via Get-Content'
$famList = @(Get-Content "$TMP\fonts-0001.txt" -Encoding UTF8 | Where-Object { $_.Trim() -ne '' })
Write-Host ('T2 loaded ' + $famList.Count + ' entries, type=' + $famList.GetType().FullName)
Write-Host ('T2 element0 type=' + $famList[0].GetType().FullName + ' len=' + $famList[0].Length)
$sw = [Diagnostics.Stopwatch]::StartNew()
$ja2 = $famList | ConvertTo-Json -Depth 10 -Compress
Write-Host ('T2 ok ' + $sw.ElapsedMilliseconds + ' ms len=' + $ja2.Length)

Write-Host 'T3: pscustomobject with families property'
$fonts = [pscustomobject]@{
  queried_via = 'GET https://open-snapshot.muedsa.com/fonts'
  request_id = 'A11-fonts-0001'
  families_returned = $famList.Count
  families = $famList
  prose_stack = 'Noto Sans CJK SC,Noto Sans CJK JP'
  numeric_stack = 'Noto Sans Mono CJK SC'
  reason = 'short reason text'
}
$sw = [Diagnostics.Stopwatch]::StartNew()
$jb = $fonts | ConvertTo-Json -Depth 10 -Compress
Write-Host ('T3 ok ' + $sw.ElapsedMilliseconds + ' ms len=' + $jb.Length)
Write-Host 'bench4 done'
