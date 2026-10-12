# build-b04.ps1 -- generate all 10 B04 .snapshot files and report guard problems
$ErrorActionPreference = 'Stop'
$here = Split-Path $MyInvocation.MyCommand.Path -Parent
$utf8 = New-Object System.Text.UTF8Encoding($false)

. (Join-Path $here 'lib-b04.ps1')
. (Join-Path $here 'gen-b04-a.ps1')
. (Join-Path $here 'gen-b04-b.ps1')
. (Join-Path $here 'gen-b04-c.ps1')
. (Join-Path $here 'gen-b04-d.ps1')

$round = 'r01'
if ($args.Count -ge 1) { $round = [string]$args[0] }

$builders = @(
    @{ id = 'case-01'; f = { Get-B04-Case01 } },
    @{ id = 'case-02'; f = { Get-B04-Case02 } },
    @{ id = 'case-03'; f = { Get-B04-Case03 } },
    @{ id = 'case-04'; f = { Get-B04-Case04 } },
    @{ id = 'case-05'; f = { Get-B04-Case05 } },
    @{ id = 'case-06'; f = { Get-B04-Case06 } },
    @{ id = 'case-07'; f = { Get-B04-Case07 } },
    @{ id = 'case-08'; f = { Get-B04-Case08 } },
    @{ id = 'case-09'; f = { Get-B04-Case09 } },
    @{ id = 'case-10'; f = { Get-B04-Case10 } }
)

foreach ($b in $builders) {
    $script:PROBLEMS.Clear()
    $script:CURRENT = $b.id
    $dsl = & $b.f
    $dir = Join-Path $script:B04TMP ($b.id)
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $p = Join-Path $dir ($round + '.snapshot')
    [IO.File]::WriteAllText($p, $dsl.Trim() + "`r`n", $utf8)
    $bytes = (Get-Item $p).Length
    $nprob = $script:PROBLEMS.Count
    $msg = 'OK  '
    if ($nprob -gt 0) { $msg = ('P' + $nprob) }
    Write-Output ('{0}  {1}  {2,9} B  {3}' -f $b.id, $round, $bytes, $msg)
    foreach ($pr in $script:PROBLEMS) { Write-Output ('    ! ' + $pr) }
}
