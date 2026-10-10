# probe-hatch.ps1 -- prove Hatch6 (ClipRRect > Stack > rotated bars) before any
# case depends on it.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $root 'tmp\run-20261002-220723-mimo\B06\lib-b06.ps1')

$W = 760; $H = 320
$o = ''
$o += Ts 'p-k' 24 20 712 30 'Hatch6 probe -- clipped diagonal fill' 18 $script:MONO '#333333' 'LEFT' ''

# sharp rect, light ground
$o += (Box 24 66 330 90 '#E9E5DC' 0)
$o += (Hatch6 24 66 330 90 0 '#4C5FD5' 16 4)
$o += Ts 'p-l1' 24 164 330 26 'ClipR rad 0  pitch 16  thick 4' 15 $script:SANS '#5C6674' 'LEFT' ''

# rounded rect, other colour / finer pitch
$o += (Box 406 66 330 90 '#E9E5DC' 0)
$o += (Hatch6 406 66 330 90 14 '#E0A33C' 10 3)
$o += Ts 'p-l2' 406 164 330 26 'ClipR rad 14  pitch 10  thick 3' 15 $script:SANS '#5C6674' 'LEFT' ''

# narrow strip (the shape case-07 actually needs)
$o += (Box 24 210 712 44 '#FFFFFF' 0)
$o += (Hatch6 24 210 712 44 6 '#E5484D' 12 3)
$o += Ts 'p-l3' 24 262 712 26 'narrow strip 712x44 rad 6 -- corners must stay covered' 15 $script:SANS '#5C6674' 'LEFT' ''

$body = Page6 $W $H '#F4F2ED' $o
$p = Join-Path $script:B06TMP 'probe-hatch.snapshot'
Write-Dsl6 $p $body
Write-Output ("probe-hatch.snapshot  {0} bytes" -f (Get-Item $p).Length)
Report-Problems6
