$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$rend = Join-Path $tmp 'render-b03.ps1'
$log  = Join-Path $tmp 'requests.jsonl'
$dsl  = Join-Path $tmp 'probes\p15-backdrop-sigma.snapshot'
$png  = Join-Path $tmp 'probes\p15-backdrop-sigma.png'

$body = @'
<Snapshot type="png" background="#FFFFFF">
<Container width="900" height="700" color="#FFFFFF">
<Stack clipBehavior="NONE">
<Positioned left="0" top="0" width="450" height="700"><Container width="450" height="700" color="#000000"/></Positioned>
<Positioned left="380" top="30" width="140" height="140"><ClipRect><BackdropFilter sigmaX="0.1" sigmaY="0.1"><Container width="140" height="140" color="#FF000066"/></BackdropFilter></ClipRect></Positioned>
<Positioned left="380" top="200" width="140" height="140"><ClipRect><BackdropFilter sigmaX="8" sigmaY="8"><Container width="140" height="140" color="#00FF0066"/></BackdropFilter></ClipRect></Positioned>
<Positioned left="380" top="370" width="140" height="140"><ClipRect><BackdropFilter sigmaX="40" sigmaY="40"><Container width="140" height="140" color="#0000FF66"/></BackdropFilter></ClipRect></Positioned>
<Positioned left="380" top="540" width="140" height="140"><ClipRect><BackdropFilter sigmaX="200" sigmaY="200"><Container width="140" height="140" color="#FFFF0066"/></BackdropFilter></ClipRect></Positioned>
</Stack>
</Container>
</Snapshot>
'@

[IO.File]::WriteAllText($dsl, $body.Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
& $rend -DslPath $dsl -OutPath $png -TaskId 'B03' -ReqId 'B03-p15-backdrop-sigma' -CaseId $null -LogPath $log | Out-Null
"bytes=" + (Get-Item $png).Length
