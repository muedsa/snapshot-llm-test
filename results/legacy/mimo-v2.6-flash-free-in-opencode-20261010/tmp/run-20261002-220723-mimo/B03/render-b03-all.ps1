param(
    [string[]]$Cases = @(),
    [int]$Round = 1
)
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$out = Join-Path $root 'outputs\run-20261002-220723-mimo\B03'
$tmp = Join-Path $root 'tmp\run-20261002-220723-mimo\B03'
$rend = Join-Path $tmp 'render-b03.ps1'
$log = Join-Path $tmp 'requests.jsonl'
$att = Join-Path $tmp 'attempts'
if (!(Test-Path $att)) { New-Item -ItemType Directory -Force -Path $att | Out-Null }

if ($Cases.Count -eq 0) {
    $Cases = Get-ChildItem $out -Directory | Where-Object { $_.Name -like 'case-*' } | Sort-Object Name | ForEach-Object { $_.Name }
}

foreach ($c in $Cases) {
    $dir = Join-Path $out $c
    $dsl = Join-Path $dir 'final.snapshot'
    $png = Join-Path $dir 'final.png'
    if (!(Test-Path $dsl)) { Write-Output "SKIP $c (no snapshot)"; continue }

    if (Test-Path $png) {
        $prev = 'prev'
        $marker = Join-Path $dir '.round'
        if (Test-Path $marker) { $prev = ([IO.File]::ReadAllText($marker)).Trim() }
        $tag = '{0}-r{1}' -f $c, $prev
        $n = 1
        while ((Test-Path (Join-Path $att ($tag + '.png'))) -or (Test-Path (Join-Path $att ($tag + '.snapshot')))) { $n++; $tag = '{0}-r{1}-{2}' -f $c, $prev, $n }
        Copy-Item $png (Join-Path $att ($tag + '.png')) -Force
        Copy-Item $dsl (Join-Path $att ($tag + '.snapshot')) -Force
        Write-Output "ARCHIVE $tag"
    }

    $rid = 'B03-{0}-r{1}' -f $c, $Round
    $before = (Get-Item $png -ErrorAction SilentlyContinue).Length
    & $rend -DslPath $dsl -OutPath $png -TaskId 'B03' -ReqId $rid -CaseId $c -LogPath $log | Out-Null
    $rc = $LASTEXITCODE
    $after = (Get-Item $png -ErrorAction SilentlyContinue).Length
    if ($rc -eq 0) {
        [IO.File]::WriteAllText((Join-Path $dir '.round'), ([string]$Round), (New-Object Text.UTF8Encoding($false)))
        Write-Output "OK  $c r$Round $after bytes"
    } else {
        Write-Output "FAIL $c r$Round"
    }
}
