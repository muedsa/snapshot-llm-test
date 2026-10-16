$p='outputs/run-20261016/_suite/suite-state.json'
$c=Get-Content $p -Raw | ConvertFrom-Json
$t=$c.tasks[0]
$t.status='completed'
$t.started_at='2026-10-16T09:04:43+08:00'
$t.ended_at='2026-10-16T09:11:01+08:00'
$t.output_dir='outputs/run-20261016/A01/'
$t.temp_dir='tmp/run-20261016/A01/'
$t.completed_rounds=@()
$t.completed_cases=@()
$t.artifacts=@('operations.png','operations.snapshot','computed-data.json','snapshot-usage.md','task-metrics.json')
$t.visual_review_evidence=@(@{file='operations.png';size=164704;dims=@(1600,1000);viewed='browser.preview 2026-10-16T09:11:00+08:00';note='PNG 头部尺寸校验 1600x1000，HTTP 200 image/png'})
$t.unresolved_issues=@('平台未提供可直接读取的图像像素反馈工具，视觉质量依 DSL 几何自检与尺寸校验；建议人工复查最终图。')
$t.resume_notes=$null
$c.current_task=$null
$c.current_round=$null
$c.current_case=$null
$c.last_checkpoint='2026-10-16T09:11:01+08:00 A01 completed'
$c.updated_at='2026-10-16T09:11:01+08:00'
$c | ConvertTo-Json -Depth 12 | Set-Content $p
Write-Output "SUITE_STATE_UPDATED A01=completed"
