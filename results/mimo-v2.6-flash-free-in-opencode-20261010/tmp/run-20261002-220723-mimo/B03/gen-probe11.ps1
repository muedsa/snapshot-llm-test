$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$rend = Join-Path $tmp 'render-b03.ps1'
$log  = Join-Path $tmp 'requests.jsonl'
$dsl  = Join-Path $tmp 'probes\p11-linear-tiling.snapshot'
$png  = Join-Path $tmp 'probes\p11-linear-tiling.png'

$body = @'
<Snapshot type="png" background="#000000">
<Container width="800" height="300" color="#000000">
<Stack>
<Positioned left="0" top="0" width="800" height="100">
<Container width="800" height="100" gradientType="LINEAR" gradientColors="#FF0000,#0000FF" gradientStops="0,0.5" gradientTileMode="REPEAT" gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT"/>
</Positioned>
<Positioned left="0" top="100" width="800" height="100">
<Container width="800" height="100" gradientType="LINEAR" gradientColors="#FF0000,#0000FF" gradientStops="0,0.5" gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT"/>
</Positioned>
<Positioned left="0" top="200" width="800" height="100">
<Container width="800" height="100" gradientType="LINEAR" gradientColors="#FF0000,#0000FF" gradientStops="0,1" gradientRotation="1.5707963" gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT"/>
</Positioned>
</Stack>
</Container>
</Snapshot>
'@

[IO.File]::WriteAllText($dsl, $body.Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
& $rend -DslPath $dsl -OutPath $png -TaskId 'B03' -ReqId 'B03-p11-linear-tiling' -CaseId $null -LogPath $log | Out-Null
"bytes=" + (Get-Item $png).Length
