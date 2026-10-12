$ErrorActionPreference = 'Stop'
$inputPath = 'D:\workspaces\gpt-6.1-sol-ultra\tasks\A01-operations-dashboard\inputs\monthly.csv'
$reviewPath = 'D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A01\analysis\calculated-review-v01.json'
$raw = Import-Csv -LiteralPath $inputPath
$rows = @($raw | ForEach-Object {
    $g = [decimal]$_.gross_revenue
    $r = [decimal]$_.refund_amount
    $c = [decimal]$_.operating_cost
    $o = [decimal]$_.orders
    $s = [decimal]$_.sessions
    [ordered]@{
        month = $_.month; orders = [int]$o; gross_revenue = [int]$g
        refund_amount = [int]$r; operating_cost = [int]$c; sessions = [int]$s
        net_revenue = [int]($g-$r); operating_profit = [int]($g-$r-$c)
        refund_rate = $r/$g; conversion_rate = $o/$s
        refund_percent_display = ($r/$g*100).ToString('F2') + '%'
        conversion_percent_display = ($o/$s*100).ToString('F2') + '%'
    }
})
$totals = [ordered]@{}
foreach ($field in @('orders','gross_revenue','refund_amount','operating_cost','sessions','net_revenue','operating_profit')) {
    $totals[$field] = [int](($rows | ForEach-Object { $_[$field] } | Measure-Object -Sum).Sum)
}
$totals.conversion_rate = [decimal]$totals.orders/[decimal]$totals.sessions
$totals.refund_rate = [decimal]$totals.refund_amount/[decimal]$totals.gross_revenue
$totals.operating_profit_margin = [decimal]$totals.operating_profit/[decimal]$totals.net_revenue
$totals.conversion_percent_display = ($totals.conversion_rate*100).ToString('F2') + '%'
$checks = [ordered]@{
    monthly_net_identities = @($rows | ForEach-Object { $_.net_revenue -eq ($_.gross_revenue-$_.refund_amount) })
    monthly_profit_identities = @($rows | ForEach-Object { $_.operating_profit -eq ($_.net_revenue-$_.operating_cost) })
    sum_net_equals_sum_gross_minus_refunds = ($totals.net_revenue -eq ($totals.gross_revenue-$totals.refund_amount))
    sum_profit_equals_sum_net_minus_cost = ($totals.operating_profit -eq ($totals.net_revenue-$totals.operating_cost))
    month_count = $rows.Count
    negative_profit_count = @($rows | Where-Object { $_.operating_profit -lt 0 }).Count
    highest_net_month = ($rows | Sort-Object net_revenue -Descending | Select-Object -First 1).month
    highest_profit_month = ($rows | Sort-Object operating_profit -Descending | Select-Object -First 1).month
}
$july = $rows[3]
$august = $rows[4]
$september = $rows[5]
$conclusionNumbers = [ordered]@{
    july_net_revenue = $july.net_revenue; august_net_revenue = $august.net_revenue
    july_operating_profit = $july.operating_profit; august_operating_profit = $august.operating_profit
    august_net_revenue_change_vs_july = [decimal]($august.net_revenue-$july.net_revenue)/[decimal]$july.net_revenue
    august_profit_change_vs_july = [decimal]($august.operating_profit-$july.operating_profit)/[decimal]$july.operating_profit
    july_refund_rate = $july.refund_rate; august_refund_rate = $august.refund_rate
    july_operating_cost = $july.operating_cost; august_operating_cost = $august.operating_cost
    august_cost_change_vs_july = [decimal]($august.operating_cost-$july.operating_cost)/[decimal]$july.operating_cost
    september_net_revenue = $september.net_revenue; september_operating_profit = $september.operating_profit
    august_refund_amount = $august.refund_amount; september_refund_amount = $september.refund_amount
    september_refund_rate = $september.refund_rate
}
$review = [ordered]@{
    task_id = 'A01'; run_id = '20261002-204314-6f31'; reviewer_role = 'independent_data_and_layout_analysis'
    created_at = [DateTimeOffset]::Now.ToString('o')
    source = $inputPath; business_data_is_fictional = $true
    formulas = [ordered]@{net_revenue='gross_revenue - refund_amount';operating_profit='net_revenue - operating_cost';refund_rate='refund_amount / gross_revenue';monthly_conversion='orders / sessions';period_conversion='sum(orders) / sum(sessions)'}
    monthly = $rows; totals = $totals; arithmetic_checks = $checks
    chart_axes = [ordered]@{
        grouped_financial_bars = [ordered]@{type='linear';unit='元';display_unit='万元';domain=@(0,250000);ticks=@(0,50000,100000,150000,200000,250000);same_axis_for=@('net_revenue','operating_profit');zero_baseline=$true;plot=@{x=132;y=338;width=770;height=260};month_centers=@(198,326,454,582,710,838);bar_width=30;bar_inner_gap=8;pixel_height_formula='value / 250000 * 260';pixel_top_formula='598 - value / 250000 * 260'}
        sessions = [ordered]@{type='linear';unit='访问次数';domain=@(0,6000);ticks=@(0,3000,6000);zero_baseline=$true;plot=@{x=1040;y=314;width=492;height=88};month_centers=@(1070,1158,1246,1334,1422,1510)}
        conversion = [ordered]@{type='linear';unit='%';domain=@(0,14);ticks=@(0,7,14);zero_baseline=$true;plot=@{x=1040;y=520;width=492;height=88};month_centers=@(1070,1158,1246,1334,1422,1510);percentage_values_are_separate_from_money=$true}
    }
    conclusion = [ordered]@{
        text='8月净收入环比增7.41%，利润却降16.43%；同期退款率5%→8%、成本增17.86%。优先排查退款与成本扩张。'
        evidence=$conclusionNumbers
        causality_note='数据提供同期相关变化，未证明退款或成本变化的独立因果效应。'
    }
    render_or_visual_inspection_performed = $false
    scope_note='This review checks source calculations and proposes geometry; root agent must inspect actual rendered PNG before completion.'
}
$review | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reviewPath -Encoding utf8
$reviewPath
