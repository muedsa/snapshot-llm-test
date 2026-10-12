$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$rend = Join-Path $tmp 'render-b03.ps1'
$log  = Join-Path $tmp 'requests.jsonl'
$dsl  = Join-Path $tmp 'probes\p18-backdrop-final.snapshot'
$png  = Join-Path $tmp 'probes\p18-backdrop-final.png'

$body = @'
<Snapshot type="png" background="#FFFFFF">
<Container width="900" height="400" color="#FFFFFF">
<Stack clipBehavior="NONE">
<Positioned left="0" top="0" width="450" height="400"><Container width="450" height="400" color="#000000"/></Positioned>
<Positioned left="380" top="120" width="140" height="140"><ClipRRect borderRadius="24"><BackdropFilter sigmaX="25" sigmaY="25"><Container width="140" height="140" color="#FF000066"/></BackdropFilter></ClipRRect></Positioned>
<Positioned left="600" top="0" width="300" height="400"><Container width="300" height="400" color="#000000"/></Positioned>
<Positioned left="530" top="120" width="140" height="140"><ClipRect><BackdropFilter sigmaX="25" sigmaY="25"><Container width="140" height="140" color="#FF000066"/></BackdropFilter></ClipRect></Positioned>
<Positioned left="60" top="170" width="300" height="40"><Text fontFamily="Inter" fontSize="30" color="#FF0000">P1 ClipRRect first</Text></Positioned>
<Positioned left="640" top="170" width="250" height="40"><Text fontFamily="Inter" fontSize="30" color="#FF0000">P2 second</Text></Positioned>
</Stack>
</Container>
</Snapshot>
'@

[IO.File]::WriteAllText($dsl, $body.Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
& $rend -DslPath $dsl -OutPath $png -TaskId 'B03' -ReqId 'B03-p18-backdrop-final' -CaseId $null -LogPath $log | Out-Null
"bytes=" + (Get-Item $png).Length
