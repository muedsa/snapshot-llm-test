$ErrorActionPreference = 'Stop'
$suiteRoot = 'D:\workspaces\gpt-6.1-sol-ultra'
$taskInput = Join-Path $suiteRoot 'tasks\A02-conference-schedule\inputs'
$auditPath = Join-Path $suiteRoot 'tmp\20261002-204314-6f31\A02\analysis\schedule-review-v01.json'
function Get-Minute([string]$hhmm) { $p=$hhmm.Split(':'); return [int]$p[0]*60+[int]$p[1] }
function Get-Time([int]$minute) { return '{0:00}:{1:00}' -f [math]::Floor($minute/60),($minute%60) }
$raw=Import-Csv -LiteralPath (Join-Path $taskInput 'agenda.csv')
$venues=Get-Content -Raw -LiteralPath (Join-Path $taskInput 'venues.json') | ConvertFrom-Json
$sessions=@($raw | ForEach-Object {
    $start=Get-Minute $_.start; $end=Get-Minute $_.end
    [pscustomobject][ordered]@{
        id=$_.id;venue=$_.venue;start=$_.start;end=$_.end;title=$_.title;speaker=$_.speaker
        category=$_.category;category_label=$venues.categories.($_.category)
        start_minute=$start;end_minute=$end;offset_from_09=$start-540;duration_minutes=$end-$start
        proposed_wide_x=200+($start-540)*1640/420
        proposed_wide_width=($end-$start)*1640/420
    }
})
$gaps=[ordered]@{}; $summary=[ordered]@{}; $venueConflicts=@();$speakerConflicts=@();$lunchConflicts=@()
foreach($venue in @('A','B','C')) {
    $items=@($sessions | Where-Object venue -eq $venue | Sort-Object start_minute)
    $list=@();$cursor=540
    foreach($item in $items) {
        if($item.start_minute -gt $cursor) {
            $gs=$cursor;$ge=$item.start_minute
            $list += [ordered]@{start=Get-Time $gs;end=Get-Time $ge;duration_minutes=$ge-$gs;includes_public_lunch=($gs -lt 780 -and $ge -gt 720)}
        }
        if($item.start_minute -lt $cursor) { $venueConflicts += [ordered]@{venue=$venue;id=$item.id;overlap_start=$item.start;overlap_end=Get-Time ([math]::Min($cursor,$item.end_minute))} }
        $cursor=[math]::Max($cursor,$item.end_minute)
    }
    if($cursor -lt 960) { $list += [ordered]@{start=Get-Time $cursor;end='16:00';duration_minutes=960-$cursor;includes_public_lunch=$false} }
    $gaps[$venue]=$list
    $busy=[int](($items.duration_minutes|Measure-Object -Sum).Sum)
    $summary[$venue]=[ordered]@{capacity=$venues.$venue.capacity;session_count=$items.Count;meeting_minutes=$busy;whole_axis_minutes=420;all_gap_minutes=420-$busy;public_lunch_minutes=60;ordinary_gap_minutes=360-$busy;session_ids=@($items.id)}
}
for($i=0;$i -lt $sessions.Count;$i++) {
    $left=$sessions[$i]
    if($left.start_minute -lt 780 -and $left.end_minute -gt 720) { $lunchConflicts+=$left.id }
    $speakersLeft=@($left.speaker -split '\s*/\s*')
    for($j=$i+1;$j -lt $sessions.Count;$j++) {
        $right=$sessions[$j]
        if($left.start_minute -lt $right.end_minute -and $right.start_minute -lt $left.end_minute) {
            $speakersRight=@($right.speaker -split '\s*/\s*')
            foreach($speaker in $speakersLeft) {
                if($speakersRight -contains $speaker) {$speakerConflicts += [ordered]@{speaker=$speaker;ids=@($left.id,$right.id)}}
            }
        }
    }
}
$mapping=@($sessions | ForEach-Object {[ordered]@{id=$_.id;wide=[ordered]@{swimlane=$_.venue;block_id=$_.id;index_fields=@('id','title','speaker','venue','start','end','category_label')};mobile=[ordered]@{order=[array]::IndexOf($sessions,$_)+1;fields=@('id','title','venue','start','end','category_label');speaker_reference='讲者详见完整日程'}}})
$audit=[ordered]@{
    task_id='A02';run_id='20261002-204314-6f31';created_at=[DateTimeOffset]::Now.ToString('o')
    source_files=@('tasks/A02-conference-schedule/inputs/agenda.csv','tasks/A02-conference-schedule/inputs/venues.json')
    event_name='Structure / Vision 2026';date='2026-11-07';timezone='Asia/Shanghai';location='云构中心 · A / B / C 会场'
    session_count=$sessions.Count;sessions=$sessions;venue_summary=$summary;venue_gaps=$gaps
    public_lunch=[ordered]@{start='12:00';end='13:00';duration_minutes=60;separate_item=$true;applies_to=@('A','B','C')}
    conflict_checks=[ordered]@{interval_convention='[start,end), ending at another start is not a conflict';venue_conflicts=$venueConflicts;speaker_conflicts=$speakerConflicts;public_lunch_conflicts=$lunchConflicts;all_clear=($venueConflicts.Count -eq 0 -and $speakerConflicts.Count -eq 0 -and $lunchConflicts.Count -eq 0)}
    proposed_wide_axis=[ordered]@{start='09:00';end='16:00';total_minutes=420;x_start=200;x_end=1840;width=1640;pixels_per_minute=1640/420;formula='x=200+(minute_of_day-540)*1640/420; width=duration_minutes*1640/420';lunch_x_start=200+180*1640/420;lunch_x_end=200+240*1640/420;capacity_labels=@('A会场 · 320人','B会场 · 80人','C会场 · 160人')}
    content_mapping=$mapping
    review_notes=@('No input times changed.','Concurrent sessions in different venues are intentional parallel schedule, not conflicts.','All15 titles/speakers/categories/start/end appear in wide index; mobile retains all15 IDs/titles/venues/start/end.','Proposed geometry is advisory; final actual positions should be copied into delivered schedule-audit.json by producer.')
    rendered=$false;actual_png_viewed=$false
}
$audit|ConvertTo-Json -Depth 12|Set-Content -LiteralPath $auditPath -Encoding utf8
$auditPath
