$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$rend = Join-Path $tmp 'render-b03.ps1'
$log  = Join-Path $tmp 'requests.jsonl'
$dsl  = Join-Path $tmp 'probes\p17-backdrop-order.snapshot'
$png  = Join-Path $tmp 'probes\p17-backdrop-order.png'

function Row($top, $tag) {
  return @"
<Positioned left="0" top="$top" width="900" height="160">
<Stack>
<Positioned left="0" top="0" width="450" height="160"><Container width="450" height="160" color="#000000"/></Positioned>
<Positioned left="380" top="10" width="140" height="140"><ClipRect><BackdropFilter sigmaX="25" sigmaY="25"><Container width="140" height="140" color="#FF000066"/></BackdropFilter></ClipRect></Positioned>
<Positioned left="620" top="10" width="140" height="140"><ClipRect><BackdropFilter sigmaX="25" sigmaY="25"><Container width="140" height="140" color="#FF000066"/></BackdropFilter></ClipRect></Positioned>
</Stack>
</Positioned>
"@
}

# declared bottom-first: order test vs position test
$parts = @()
$parts += (Row 560 'first')
$parts += (Row 380 'second')
$parts += (Row 200 'third')
$parts += (Row 20  'fourth')

$body = @"
<Snapshot type="png" background="#FFFFFF">
<Container width="900" height="760" color="#FFFFFF">
<Stack clipBehavior="NONE">
$($parts -join "`r`n")
</Stack>
</Container>
</Snapshot>
"@

[IO.File]::WriteAllText($dsl, $body.Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
& $rend -DslPath $dsl -OutPath $png -TaskId 'B03' -ReqId 'B03-p17-backdrop-order' -CaseId $null -LogPath $log | Out-Null
"bytes=" + (Get-Item $png).Length
