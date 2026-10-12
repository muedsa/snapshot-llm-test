$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B02'
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Add-Jsonl([string]$path, [string]$line) {
    if (Test-Path $path) {
        foreach ($e in @(Get-Content $path -Encoding UTF8)) {
            if ([string]::IsNullOrWhiteSpace($e)) { continue }
            $o = $e | ConvertFrom-Json
            $n = $line | ConvertFrom-Json
            if ($o.iteration_id -and $n.iteration_id -and $o.iteration_id -eq $n.iteration_id) { return 'skip ' + $n.iteration_id }
            if ($o.tool_id -and $n.tool_id -and $o.tool_id -eq $n.tool_id) { return 'skip ' + $n.tool_id }
        }
    }
    [IO.File]::AppendAllText($path, $line + "`n", $utf8)
    $n = $line | ConvertFrom-Json
    $tag = if ($n.iteration_id) { $n.iteration_id } else { $n.tool_id }
    return 'ok   ' + $tag
}

$it = Join-Path $tmp 'iterations.jsonl'
$tu = Join-Path $tmp 'tool-usage.jsonl'

Add-Jsonl $it @'
{"iteration_id":"ite-B02-read-evidence-correction","case_id":"case-01,case-04","version":"","parent_version":null,"type":"evidence-correction","request_id":"","http_status":null,"duration_ms":null,"render_ended_utc":null,"viewed":true,"view_evidence":"唯一命名副本 tmp/run-20261002-220723-mimo/B02/view/verify-case01-1080x1620-7629d248.png（读图返回正确的 r7 海报）；case-04 的 r8 看板由读图工具在请求 case-01/final.png 时返回；并以 PNG IHDR 实读 + 文件字节数交叉核对","observation":"发现读图工具的一次路径/内容错配：请求 outputs/.../case-01/final.png 返回的是 1920x1080 看板（case-04 的 r8 内容），请求 case-04/final.png 返回的是 1080x1620 海报（case-01 的 r7 内容），两者被互换；其后连续 3 次读取不同路径（verify-case04、verify-case07、v04 jpg）均重复返回同一张 case-01 海报，即读图层进入粘滞状态。用文件侧证据交叉核对：IHDR 实读 case-01=1080x1620/220101 B（与 B02-c01-r7 响应字节数一致）、case-04=1920x1080/222950 B（与 B02-c04-r8 一致），且在 case-01/final.png 上直接逐 0.5 度取样得到 203/720=28.19%、起点 0 度——只有海报在 (154,750) 处存在该进度环，看板同坐标没有环，故量测结果反证 case-01 文件确为海报","change":"不改作品与 DSL，只修正证据口径：ite-B02-c01-v7-visual 与 ite-B02-c04-v7-visual 的 view_evidence 中「本次内容正确返回」不成立，实际是两条路径互换了返回内容；两件作品的当前版本均已通过上述交叉核对确认被看到","result":"case-01 r7 与 case-04 r8 的查看结论有效，但查看路径记述已由本行更正，不再声称单次读取即正确"}
'@

Add-Jsonl $tu @'
{"tool_id":"tu-13","tool":"读图返回内容与路径错配的核查","category":"图像观察","purpose":"当读图工具返回的图像与请求路径不符或连续重复时，用文件侧不可变证据判定真正看到的是哪一件作品","input":"outputs/run-20261002-220723-mimo/B02/case-01/final.png、case-04/final.png 的原始字节；读图返回的位图","output":"IHDR 尺寸与文件字节数比对表；case-01 上的环形逐角度量 203/720=28.19%；唯一命名副本与自标注 JPEG（view/verify-*、view/v04-*）","affected_cases":["case-01","case-04","case-07"],"http_request_ids":[],"double_counted":false,"note":"本轮共出现 4 次错误返回（1 次两条路径内容互换 + 3 次同一张海报重复返回）。核查手段：文件字节数必须等于对应渲染请求的响应字节数；在唯一坐标做像素量测，只有目标图在该坐标有对应图形；再用带标题条的 JPEG 副本尝试重新读取。JPEG 副本本次也未奏效，故以文件侧证据为准并在 ite-B02-read-evidence-correction 中如实更正。"}
'@

"iterations total : " + (Get-Content $it).Count
"tool-usage total : " + (Get-Content $tu).Count
foreach ($f in @('iterations.jsonl','tool-usage.jsonl')) {
    $p = Join-Path $tmp $f
    $bad = 0; $n = 0
    foreach ($line in [System.IO.File]::ReadAllLines($p)) {
        $n++
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { $null = $line | ConvertFrom-Json } catch { $bad++; "BAD line $n in ${f}: $($_.Exception.Message)" }
    }
    "$f : $n lines, $bad bad"
}
