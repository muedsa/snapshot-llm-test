$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$s = Get-Content 'outputs\run-20261002-220723-mimo\_suite\suite-state.json' -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Output ("profile={0}  status={1}  current_task={2}  updated_at={3}  last_checkpoint={4}" -f $s.profile, $s.status, $s.current_task, $s.updated_at, $s.last_checkpoint)
$counts = @($s.tasks | Group-Object status | ForEach-Object { "$($_.Name)=$($_.Count)" })
Write-Output ("counts: " + ($counts -join ', '))
foreach ($t in $s.tasks) {
  $props = $t.PSObject.Properties.Name
  $missing = @()
  foreach ($k in @('id','status','started_at','ended_at','output_dir','temp_dir','artifacts','visual_review_evidence','unresolved_issues','resume_notes')) {
    if ($props -notcontains $k) { $missing += $k }
  }
  if ($t.id -in @('A16','A17')) {
    Write-Output ("{0}: status={1}  missing={2}" -f $t.id, $t.status, $(if ($missing.Count) { $missing -join ',' } else { 'none' }))
    Write-Output ("     artifacts={0} evidence={1} issues={2}" -f $t.artifacts.Count, $t.visual_review_evidence.Count, $t.unresolved_issues.Count)
  } elseif ($missing.Count -gt 0) {
    Write-Output ("{0}: MISSING {1}" -f $t.id, ($missing -join ','))
  }
}
