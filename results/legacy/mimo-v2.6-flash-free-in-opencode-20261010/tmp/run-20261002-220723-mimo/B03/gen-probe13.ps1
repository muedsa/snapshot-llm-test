$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$rend = Join-Path $tmp 'render-b03.ps1'
$log  = Join-Path $tmp 'requests.jsonl'
$pdir = Join-Path $tmp 'probes'

$pairs = @(
  @('(-1,0)', '(-0.5,0)'),
  @('(-1, 0)', '(-0.5, 0)'),
  @('BoxAlignment(-1, 0)', 'BoxAlignment(-0.5, 0)'),
  @('ALIGNMENT(-1,0)', 'ALIGNMENT(-0.5,0)'),
  @('-1,0', '-0.5,0')
)

$out = @()
$idx = 0
foreach ($pr in $pairs) {
  $idx++
  $id = 'B03-p13-align{0:d2}' -f $idx
  $dsl = Join-Path $pdir ("p13-align{0:d2}.snapshot" -f $idx)
  $png = Join-Path $pdir ("p13-align{0:d2}.png" -f $idx)
  $b = $pr[0]; $e = $pr[1]
  $body = @"
<Snapshot type="png" background="#000000">
<Container width="800" height="100" color="#000000">
<Container width="800" height="100" gradientType="LINEAR" gradientColors="#FF0000,#0000FF" gradientStops="0,1" gradientTileMode="REPEAT" gradientBegin="$b" gradientEnd="$e"/>
</Container>
</Snapshot>
"@
  [IO.File]::WriteAllText($dsl, $body.Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
  & $rend -DslPath $dsl -OutPath $png -TaskId 'B03' -ReqId $id -CaseId $null -LogPath $log | Out-Null
  $row = (Get-Content $log -Encoding UTF8 | Select-Object -Last 1) | ConvertFrom-Json
  $ok = Test-Path $png
  $es = $row.error_summary
  if ($null -eq $es) { $es = '' }
  $out += ("{0,-24} {1,-24} http={2} ok={3} {4}" -f $b, $e, $row.http_status, $ok, $es)
}
$out
