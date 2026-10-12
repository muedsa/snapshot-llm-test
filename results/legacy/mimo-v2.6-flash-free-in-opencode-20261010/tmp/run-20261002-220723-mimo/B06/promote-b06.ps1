# promote-b06.ps1 -- copy each accepted attempt's PNG + DSL verbatim into outputs/.../B06/case-NN
# final.png      = the service's raw PNG bytes, never re-encoded or cropped
# final.snapshot = r01.snapshot, proven byte-exact for every final by the dsl_sha256 recorded
#                  in iterations.jsonl plus a determinism re-run of both generators
# .round         = the attempt number that was accepted (B05 convention)
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B06'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B06'
if (!(Test-Path $out)) { New-Item -ItemType Directory -Force -Path $out | Out-Null }

$map = [ordered]@{
    'case-01' = 'a02'
    'case-02' = 'a04'
    'case-03' = 'a04'
    'case-04' = 'a03'
    'case-05' = 'a02'
    'case-06' = 'a03'
    'case-07' = 'a03'
    'case-08' = 'a02'
    'case-09' = 'a02'
    'case-10' = 'a03'
}

$utf8 = New-Object Text.UTF8Encoding($false)
$done = 0
foreach ($cid in $map.Keys) {
    $pass = $map[$cid]
    $srcPng = Join-Path $tmp ($cid + '\' + $pass + '.png')
    $srcDsl = Join-Path $tmp ($cid + '\r01.snapshot')
    if (!(Test-Path $srcPng)) { throw "missing $srcPng" }
    if (!(Test-Path $srcDsl)) { throw "missing $srcDsl" }

    $d = Join-Path $out $cid
    if (!(Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

    # verbatim byte copy, no re-encode
    [IO.File]::Copy($srcPng, (Join-Path $d 'final.png'), $true)
    [IO.File]::Copy($srcDsl, (Join-Path $d 'final.snapshot'), $true)
    $roundNo = [int]$pass.Substring(1)
    [IO.File]::WriteAllText((Join-Path $d '.round'), ([string]$roundNo), $utf8)

    $pngOk = ((Get-FileHash $srcPng -Algorithm SHA256).Hash -eq (Get-FileHash (Join-Path $d 'final.png') -Algorithm SHA256).Hash)
    $dslOk = ((Get-FileHash $srcDsl -Algorithm SHA256).Hash -eq (Get-FileHash (Join-Path $d 'final.snapshot') -Algorithm SHA256).Hash)
    $len = (Get-Item (Join-Path $d 'final.png')).Length
    $dlen = (Get-Item (Join-Path $d 'final.snapshot')).Length
    Write-Output ("{0} <- {1}  png {2} B (exact:{3})  dsl {4} B (exact:{5})" -f $cid, $pass, $len, $pngOk, $dlen, $dslOk)
    if (!($pngOk -and $dslOk)) { throw "$cid byte fidelity check failed" }
    $done++
}
Write-Output ("promoted {0} cases -> {1}" -f $done, $out)
