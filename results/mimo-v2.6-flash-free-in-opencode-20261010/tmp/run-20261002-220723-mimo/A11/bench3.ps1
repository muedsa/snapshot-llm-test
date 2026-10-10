$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$TMP = "$root\tmp\$RUN\A11"

Write-Host '--- 1. segments-v02.json top level keys ---'
$raw = [IO.File]::ReadAllText("$TMP\segments-v02.json", [Text.Encoding]::UTF8)
Write-Host ('raw length = ' + $raw.Length)
$meta = $raw | ConvertFrom-Json
$names = @($meta.PSObject.Properties | ForEach-Object { $_.Name })
Write-Host ('keys: ' + ($names -join ', '))
foreach ($n in $names) {
  $v = $meta.PSObject.Properties[$n].Value
  $t = if ($null -eq $v) { 'NULL' } else { $v.GetType().FullName }
  $cnt = ''
  if ($v -is [System.Collections.IEnumerable] -and $v -isnot [string]) { $cnt = (' count=' + @($v).Count) }
  Write-Host ('  ' + $n + ' -> ' + $t + $cnt)
}

Write-Host '--- 2. computation sub keys ---'
$g = $meta.computation
if ($null -eq $g) { Write-Host '  computation is NULL' }
else {
  foreach ($n in @($g.PSObject.Properties | ForEach-Object { $_.Name })) {
    $v = $g.PSObject.Properties[$n].Value
    $t = if ($null -eq $v) { 'NULL' } else { $v.GetType().FullName }
    Write-Host ('  ' + $n + ' -> ' + $t)
  }
}

Write-Host '--- 3. fonts file ---'
$famList = @(Get-Content "$TMP\fonts-0001.txt" -Encoding UTF8 | Where-Object { $_.Trim() -ne '' })
Write-Host ('families = ' + $famList.Count)
$sw = [Diagnostics.Stopwatch]::StartNew()
$ja = $famList | ConvertTo-Json -Depth 10 -Compress
Write-Host ('3a string[] json ok ' + $sw.ElapsedMilliseconds + ' ms len=' + $ja.Length)

$fonts = [pscustomobject]@{
  queried_via = 'GET https://open-snapshot.muedsa.com/fonts'
  request_id = 'A11-fonts-0001'
  families_returned = $famList.Count
  families = $famList
  prose_stack = 'Noto Sans CJK SC,Noto Sans CJK JP'
  numeric_stack = 'Noto Sans Mono CJK SC'
  reason = 'Noto Sans CJK SC carries simplified Chinese, kana and Latin in one face so mixed lines keep one metric; Noto Sans CJK JP is listed second for Japanese glyph forms; Noto Sans Mono CJK SC gives equal advance widths, so right-aligning every amount to x=1136 with exactly two decimals puts every decimal point in one column'
}
$sw = [Diagnostics.Stopwatch]::StartNew()
try { $jb = $fonts | ConvertTo-Json -Depth 10 -Compress; Write-Host ('3b fonts object json ok ' + $sw.ElapsedMilliseconds + ' ms len=' + $jb.Length) }
catch { Write-Host ('3b THREW ' + $_.Exception.Message) }
Write-Host 'bench3 done'
