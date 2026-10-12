$ErrorActionPreference = "Stop"
Write-Host "A: scriptblock-invocation syntax"
$segOut = { param($list) @($list | ForEach-Object { [pscustomobject]@{ id=$_.id; n=$_.n } }) }
$objs = @(1..60 | ForEach-Object { [pscustomobject]@{ id=("s" + $_); page=(($_ % 2) + 1); n=$_ } })
$sw = [Diagnostics.Stopwatch]::StartNew()
try { $r = @(segOut ($objs | Where-Object { $_.page -eq 1 })); Write-Host ("A ok {0} ms count={1}" -f $sw.ElapsedMilliseconds, $r.Count) }
catch { Write-Host ("A THREW: " + $_.Exception.Message) }

Write-Host "B: ConvertTo-Json -Depth 10 over a List of 90 pscustomobjects"
$chk = New-Object System.Collections.Generic.List[object]
for ($i=0; $i -lt 90; $i++) { [void]$chk.Add([pscustomobject]@{ id=("X{0:d2}" -f $i); group="G"; check="c"; expected="e"; actual=("a" + $i); pass=$true }) }
$outer = [pscustomobject]@{ a=1; b="x"; c=[pscustomobject]@{ checks=$chk } }
$sw = [Diagnostics.Stopwatch]::StartNew()
try { $j = $outer | ConvertTo-Json -Depth 10; Write-Host ("B ok {0} ms len={1}" -f $sw.ElapsedMilliseconds, $j.Length) }
catch { Write-Host ("B THREW: " + $_.Exception.Message) }

Write-Host "C: ConvertTo-Json over a hashtable with a scriptblock-typed value and unicode"
$u = [pscustomobject]@{ t="批次：  A  07"; arr=@("a","b"); n=$null; f=[pscustomobject]@{ x=[math]::Round(1.2345,3) } }
$sw = [Diagnostics.Stopwatch]::StartNew()
try { $j2 = $u | ConvertTo-Json -Depth 10; Write-Host ("C ok {0} ms len={1}" -f $sw.ElapsedMilliseconds, $j2.Length) }
catch { Write-Host ("C THREW: " + $_.Exception.Message) }

Write-Host "D: bare-word segOut in hashtable value"
try { $tm = [pscustomobject]@{ pages=@([pscustomobject]@{ page=1; segments=(segOut ($objs | Where-Object { $_.page -eq 1 })) }) }; Write-Host ("D ok " + ($tm.pages[0].segments.Count)) }
catch { Write-Host ("D THREW: " + $_.Exception.Message) }
Write-Host "bench done"