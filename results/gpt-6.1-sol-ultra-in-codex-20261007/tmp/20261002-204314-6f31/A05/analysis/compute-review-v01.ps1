$ErrorActionPreference='Stop'
$suiteRoot='D:\workspaces\gpt-6.1-sol-ultra'
$inputPath=Join-Path $suiteRoot 'tasks\A05-irregular-sensors\inputs\readings.csv'
$outputPath=Join-Path $suiteRoot 'tmp\20261002-204314-6f31\A05\analysis\normalized-review-v01.json'
function Get-Minute([string]$hhmm){$p=$hhmm.Split(':');return [int]$p[0]*60+[int]$p[1]}
$raw=Import-Csv -LiteralPath $inputPath
$fields=@('temperature_c','humidity_pct','pressure_kpa')
$rows=@()
for($i=0;$i -lt $raw.Count;$i++){
    $inputRow=$raw[$i]
    $row=[ordered]@{index=$i;time=$inputRow.time;minute_offset=(Get-Minute $inputRow.time)-480}
    foreach($field in $fields){$value=$inputRow.$field;$row[$field]=if([string]::IsNullOrWhiteSpace($value)){$null}else{[decimal]$value}}
    $row['proposed_x']=144+$row.minute_offset*1248/270
    $rows += [pscustomobject]$row
}
$summaries=[ordered]@{};$connections=[ordered]@{};$forbidden=[ordered]@{}
foreach($field in $fields){
    $observed=@($rows|Where-Object {$null -ne $_.$field})
    $missing=@($rows|Where-Object {$null -eq $_.$field})
    $range=$observed|ForEach-Object {$_.$field}|Measure-Object -Minimum -Maximum
    $summaries[$field]=[ordered]@{valid_count=$observed.Count;missing_count=$missing.Count;observed_min=$range.Minimum;observed_max=$range.Maximum;missing_times=@($missing.time);marker_times=@($observed.time)}
    $edges=@();$gaps=@()
    for($i=0;$i -lt $rows.Count-1;$i++){
        $left=$rows[$i];$right=$rows[$i+1]
        $record=[ordered]@{from_index=$i;to_index=$i+1;from_time=$left.time;to_time=$right.time;from_offset=$left.minute_offset;to_offset=$right.minute_offset;elapsed_minutes=$right.minute_offset-$left.minute_offset;from_value=$left.$field;to_value=$right.$field}
        if($null -ne $left.$field -and $null -ne $right.$field){$edges+=$record}else{$record.reason='Adjacent original pair includes null; no line drawn';$gaps+=$record}
    }
    $connections[$field]=$edges;$forbidden[$field]=$gaps
}
$negative=@($rows|Where-Object {$null -ne $_.pressure_kpa -and $_.pressure_kpa -lt 0}|ForEach-Object {[ordered]@{time=$_.time;minute_offset=$_.minute_offset;pressure_kpa=$_.pressure_kpa}})
$checks=[ordered]@{
    twelve_rows=($rows.Count -eq 12)
    exact_offsets=(@($rows.minute_offset)-join ',' -eq '0,10,35,60,75,100,130,170,180,220,250,270')
    temperature_valid10=($summaries.temperature_c.valid_count -eq 10)
    humidity_valid11=($summaries.humidity_pct.valid_count -eq 11)
    pressure_valid12=($summaries.pressure_kpa.valid_count -eq 12)
    exact_segment_counts=($connections.temperature_c.Count -eq 7 -and $connections.humidity_pct.Count -eq 9 -and $connections.pressure_kpa.Count -eq 11)
    all_edges_original_adjacent=@($fields|ForEach-Object {$field=$_;@($connections[$field]|Where-Object {$_.to_index-$_.from_index -ne 1}).Count -eq 0})
    no_edges_have_null=@($fields|ForEach-Object {$field=$_;@($connections[$field]|Where-Object {$null -eq $_.from_value -or $null -eq $_.to_value}).Count -eq 0})
    negative_count3=($negative.Count -eq 3)
    final_zero_is_valid=($rows[11].pressure_kpa -eq 0 -and $null -ne $rows[11].pressure_kpa)
}
$result=[ordered]@{
    task_id='A05';run_id='20261002-204314-6f31';created_at=[DateTimeOffset]::Now.ToString('o');source=$inputPath
    rows=$rows;summary=$summaries;connections=$connections;forbidden_adjacent_pairs=$forbidden
    negative_pressure_observations=[ordered]@{samples=$negative;label='09:40–10:50区段的3个采样值为负';continuous_interval_claim=$false;unobserved_time_values_unknown=$true}
    proposed_axes=[ordered]@{
        time=[ordered]@{start='08:00';end='12:30';domain_minutes=@(0,270);x_start=144;x_end=1392;width=1248;pixels_per_minute=1248/270;formula='x=144+minute_offset*1248/270';sampling_reference_offsets=@($rows.minute_offset);label_tick_offsets=@(0,60,120,180,240,270);shared_x_for_all_three=$true}
        temperature_c=[ordered]@{unit='°C';domain=@(18,24);ticks=@(18,20,22,24)}
        humidity_pct=[ordered]@{unit='%';domain=@(32,42);ticks=@(32,36,40,42)}
        pressure_kpa=[ordered]@{unit='kPa';domain=@(-1,1.5);ticks=@(-1,-.5,0,.5,1,1.5);zero_line_emphasized=$true}
    }
    requirements=[ordered]@{canvas=@(1440,1000);body_min_px=20;axis_and_table_min_px=18;table_all_12_times=$true;null_display='—';every_observed_value_has_distinct_marker=$true;missing_values_not_zero=$true;missing_break_legend_required=$true;no_line_or_dashed_interpolation_across_missing=$true}
    arithmetic_checks=$checks;rendered=$false;actual_png_viewed=$false;new_http_requests=0
}
$result|ConvertTo-Json -Depth 14|Set-Content -LiteralPath $outputPath -Encoding utf8
$outputPath
