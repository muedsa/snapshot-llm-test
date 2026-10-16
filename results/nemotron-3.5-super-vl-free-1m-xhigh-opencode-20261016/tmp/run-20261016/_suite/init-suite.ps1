$src='templates/suite-state-template.json'
$dst='outputs/run-20261016/_suite/suite-state.json'
Copy-Item $src $dst
$c=Get-Content $dst -Raw
$c=[regex]::Replace($c, '"run_id": null', '"run_id": "run-20261016"', 1)
$c=[regex]::Replace($c, '"status": "not_started"', '"status": "in_progress"', 1)
$c=[regex]::Replace($c, '"started_at": null', '"started_at": "2026-10-16T09:04:43+08:00"', 1)
$c=[regex]::Replace($c, '"updated_at": null', '"updated_at": "2026-10-16T09:04:43+08:00"', 1)
$c=[regex]::Replace($c, '"current_task": null', '"current_task": "A01"', 1)
Set-Content $dst $c
Write-Output "STATE_WRITTEN"

$src2='templates/suite-metrics-template.json'
$dst2='outputs/run-20261016/_suite/suite-metrics.json'
Copy-Item $src2 $dst2
$c2=Get-Content $dst2 -Raw
$c2=[regex]::Replace($c2, '"run_id": null', '"run_id": "run-20261016"', 1)
$c2=[regex]::Replace($c2, '"profile": null', '"profile": "all"', 1)
$c2=[regex]::Replace($c2, '"status": null', '"status": "in_progress"', 1)
$c2=[regex]::Replace($c2, '"started_at": null', '"started_at": "2026-10-16T09:04:43+08:00"', 1)
Set-Content $dst2 $c2
Write-Output "METRICS_WRITTEN"
