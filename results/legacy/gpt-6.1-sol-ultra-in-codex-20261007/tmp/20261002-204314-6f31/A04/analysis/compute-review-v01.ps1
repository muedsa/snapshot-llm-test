$ErrorActionPreference='Stop'
$suiteRoot='D:\workspaces\gpt-6.1-sol-ultra'
$inputPath=Join-Path $suiteRoot 'tasks\A04-conversion-paradox\inputs\conversion.csv'
$outputPath=Join-Path $suiteRoot 'tmp\20261002-204314-6f31\A04\analysis\conversion-review-v01.json'
function Get-Gcd([long]$a,[long]$b) {while($b -ne 0){$t=$a%$b;$a=$b;$b=$t};return $a}
function Get-Fraction([long]$n,[long]$d) {$g=Get-Gcd $n $d;return [ordered]@{numerator=$n;denominator=$d;literal="$n/$d";simplified=('{0}/{1}' -f ($n/$g),($d/$g));value=[decimal]$n/[decimal]$d}}
$raw=Import-Csv -LiteralPath $inputPath
$periods=@('前期','后期');$channels=@('直接访问','推广访问')
$rows=@($raw | ForEach-Object {[pscustomobject][ordered]@{period=$_.period;channel=$_.channel;visits=[int]$_.visits;conversions=[int]$_.conversions;rate=Get-Fraction ([int]$_.conversions) ([int]$_.visits);display_percent=(([decimal]$_.conversions/[decimal]$_.visits*100).ToString('F2')+'%')}})
$summary=@()
foreach($period in $periods) {
    $subset=@($rows | Where-Object period -eq $period)
    $visits=[int](($subset.visits|Measure-Object -Sum).Sum)
    $conversions=[int](($subset.conversions|Measure-Object -Sum).Sum)
    $parts=@($subset | ForEach-Object {[ordered]@{channel=$_.channel;visits=$_.visits;share=Get-Fraction $_.visits $visits;display_share=(([decimal]$_.visits/[decimal]$visits*100).ToString('F2')+'%');rate=$_.rate;weighted_term=[decimal]$_.conversions/[decimal]$visits}})
    $weighted=($parts|ForEach-Object {$_.weighted_term}|Measure-Object -Sum).Sum
    $summary += [ordered]@{period=$period;total_visits=$visits;total_conversions=$conversions;overall_rate=Get-Fraction $conversions $visits;display_percent=(([decimal]$conversions/[decimal]$visits*100).ToString('F2')+'%');visit_composition=$parts;weighted_sum=[decimal]$weighted;weighted_formula=if($period -eq '前期'){'(8000/10000)*(2400/8000) + (2000/10000)*(200/2000) = 2600/10000 = 26%'}else{'(2000/10000)*(700/2000) + (8000/10000)*(960/8000) = 1660/10000 = 16.6%'}}
}
$changes=@()
foreach($channel in $channels) {
    $before=$rows|Where-Object {$_.period -eq '前期' -and $_.channel -eq $channel}
    $after=$rows|Where-Object {$_.period -eq '后期' -and $_.channel -eq $channel}
    $delta=$after.rate.value-$before.rate.value
    $changes += [ordered]@{channel=$channel;before=$before.rate;after=$after.rate;rate_delta=$delta;percentage_point_delta=$delta*100;direction='increase';visit_share_before=if($channel -eq '直接访问'){0.8}else{0.2};visit_share_after=if($channel -eq '直接访问'){0.2}else{0.8}}
}
$overallDelta=$summary[1].overall_rate.value-$summary[0].overall_rate.value
$result=[ordered]@{
    task_id='A04';run_id='20261002-204314-6f31';created_at=[DateTimeOffset]::Now.ToString('o');source=$inputPath
    rows=$rows;period_summary=$summary;channel_changes=$changes
    overall_change=[ordered]@{before=$summary[0].overall_rate;after=$summary[1].overall_rate;rate_delta=$overallDelta;percentage_point_delta=$overallDelta*100;relative_change=$overallDelta/$summary[0].overall_rate.value;direction='decrease'}
    arithmetic_checks=[ordered]@{all_four_input_rows_retained=($rows.Count -eq 4);both_period_visits_10000=($summary[0].total_visits -eq 10000 -and $summary[1].total_visits -eq 10000);weighted_equals_totals=@($summary|ForEach-Object {[math]::Abs([double]$_.weighted_sum-[double]$_.overall_rate.value) -lt 1e-12});both_channels_improve=(@($changes|Where-Object {$_.rate_delta -le 0}).Count -eq 0);overall_falls=($overallDelta -lt 0)}
    conclusions=[ordered]@{main='两渠道转化率均上升，但访问构成从直接访问80%、推广访问20%，转为20%、80%；按真实访问权重汇总，总体转化率26.00%→16.60%，下降9.40个百分点。';limitation='不能由该数据证明因果';interpretation='总体与分组方向相反。推广访问转化率始终较低，后期其访问权重更高。此为数据描述和加权恒等式解释，不是渠道效果因果估计。'}
    optional_arithmetic_decomposition=[ordered]@{not_observed_counterfactual=$true;causal_estimate=$false;order='Hold prior visit weights while applying later channel rates, then change weights';prior=.26;later_rates_prior_weights=.304;within_rate_component=.044;composition_component_at_later_rates=-.138;sum_delta=-.094;formula='0.26 -> 0.8*0.35+0.2*0.12=0.304 -> 0.2*0.35+0.8*0.12=0.166; (+4.4pp)+(-13.8pp)=-9.4pp'}
    geometry_constraints=[ordered]@{canvas=@(1600,1000);all_rate_plot_domain=@(0,1);rate_ticks=@(0,.25,.5,.75,1);all_rate_plots_same_scale=$true;composition_periods_equal_total_length=$true;composition_segments=[ordered]@{before=@(.8,.2);after=@(.2,.8)};body_min_px=22;chart_annotation_min_px=18;table_required_raw_fields=@('period','channel','visits','conversions');required_period_names=$periods;required_channel_names=$channels;conclusion_has_noncausal_limit=$true}
    no_render_or_visual_inspection=$true;actual_service_error_claims=@();new_http_requests=0
}
$result|ConvertTo-Json -Depth 16|Set-Content -LiteralPath $outputPath -Encoding utf8
$outputPath
