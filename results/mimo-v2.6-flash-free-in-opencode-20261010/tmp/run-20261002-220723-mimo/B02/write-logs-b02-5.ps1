# B02 round 5 (2026-10-06): calendar/weekday cross-work audit + r9/r2 fixes.
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
{"iteration_id":"ite-B02-crosswork-calendar","case_id":"case-04,case-08","version":"","parent_version":null,"type":"requirement-change","request_id":"","http_status":null,"duration_ms":null,"render_ended_utc":null,"viewed":true,"view_evidence":"对两件作品的 DSL 源文本做日历实算，并以 System.Drawing 全图 2px 逐点比对确认改动范围","observation":"前一轮 ite-B02-crosswork-elements 的核查只对了数字，没有核对星期。这次用日历实算：2026-10-06 是周二，因此 2026-10-05 是周一（不是周日），2026-10-10 周六、10-11 周日、10-12 周一、10-15 周四、10-17 周六、10-18 周日、10-19 周一、10-22 周四、10-24 周六、10-25 周日、10-26 周一、10-31 周六。于是发现两处星期错误：case-04 表头写 2026-10-05 · 周日（应为周一）；case-08 的三场标着周日的活动实际落在周一（10-12 / 10-19 / 10-26）。同时 case-08 首场 10-10 周六、case-01 的 10/10 周六 06:30、case-04 的 下次同步 周六 06:30 都是对的，9/20 至 11/15 共 57 天也复算成立（9/20 与 11/15 恰好都是周日）","change":"case-04：表头 周日 → 周一；NEXT UP 第 4 条 10/12 09:00 → 10/11 09:00（对齐 case-08）。case-08：把三场周日活动移到真正的周日 10-12 → 10-11、10-19 → 10-18、10-26 → 10-25，星期标签保持周日不变。相应发起 B02-c04-r9 与 B02-c08-r2","result":"10 件作品的日期与星期全部与 2026 年真实日历一致","supersedes":"ite-B02-crosswork-elements 中「10 件作品的品牌元素与关键数字全部交叉一致」的结论对数字成立，对星期不成立，由本行补正"}
'@

Add-Jsonl $it @'
{"iteration_id":"ite-B02-c04-v8-visual","case_id":"case-04","version":"v8","parent_version":"v7","type":"visual","request_id":"B02-c04-r9","http_status":200,"duration_ms":5193.4,"render_ended_utc":"2026-10-06T06:38:54.717Z","viewed":true,"view_evidence":"读图工具直接打开 outputs/run-20261002-220723-mimo/B02/case-04/final.png（本次内容正确返回，PNG 222559 B = 本次响应字节数）","observation":"表头已变为 2026-10-05 · 周一 · 多云 18°C；NEXT UP 第 4 条已变为 10/11 09:00 · 亲子场 · 余 4 席 · 6-12 岁。与 r8 全图 2px 逐点比对：差异仅 44 个采样点，包围盒 x[1406..1484] × y[52..506]，分成两处——y 50-99 是表头日期里的 周日→周一，y 450-549 是 NEXT UP 第 4 条的 10/12→10/11；其余区域零差异。复核未变部分：16 行合计 412、柱状图 10..17 与峰值 41 @11:00、末柱 = 在站 21、借出 9/12、下次同步 周六 06:30 全部保持","change":"仅两处文案：表头星期、NEXT UP 第 4 条日期","result":"完成 visual iteration #2，case-04 四条完成标准继续全部通过，且与 case-08 日程表逐字一致"}
'@

Add-Jsonl $it @'
{"iteration_id":"ite-B02-c08-v2-visual","case_id":"case-08","version":"v2","parent_version":"v1","type":"visual","request_id":"B02-c08-r2","http_status":200,"duration_ms":5419.4,"render_ended_utc":"2026-10-06T06:39:00.204Z","viewed":true,"view_evidence":"读图工具直接打开 outputs/run-20261002-220723-mimo/B02/case-08/final.png（本次内容正确返回，PNG 159482 B = 本次响应字节数）","observation":"9 张卡的日期与星期依次为 10-10 周六 / 10-11 周日 / 10-15 周四 / 10-17 周六 / 10-18 周日 / 10-22 周四 / 10-24 周六 / 10-25 周日 / 10-31 周六，逐条与 2026 年 10 月真实日历相符；10-11 的芦苇荡亲子场 09:00 余 4 席 6-12 岁与 case-04 的 NEXT UP 一致；10-10 秋季同步调查 06:30 余 6 席与 case-01 的 10/10 周六 06:30 北门、case-04 的 还缺 6 名志愿者 一致。与 r1 全图 2px 逐点比对：差异仅 115 个采样点，包围盒 x[696..710] × y[186..566]，正好是第 2/5/8 张卡的日期格，其余区域零差异。网格 3×3 对齐、首场橙色左边条、七要素齐全、页脚不出血均未受影响","change":"三场周日活动的日期各提前一天：10-12 → 10-11、10-19 → 10-18、10-26 → 10-25","result":"完成 visual iteration #1，case-08 四条完成标准全部通过，星期与日历一致这一条现在是真的"}
'@

Add-Jsonl $tu @'
{"tool_id":"tu-14","tool":"本地静态服务 + 浏览器标签页（尝试）","category":"图像观察","purpose":"读图工具连续返回错误字节时，改用本机 HTTP 服务把 PNG 直接投到浏览器标签页，绕开读图层的缓存","input":"outputs/run-20261002-220723-mimo/B02/case-08/final.png","output":"tmp/run-20261002-220723-mimo/B02/httpsrv.ps1（HttpListener 服务根目录）与 httpsrv.log；Invoke-WebRequest 自测 HTTP 200、159482 字节，与响应字节数一致","affected_cases":["case-08"],"http_request_ids":[],"double_counted":false,"note":"失败的尝试，如实记录：HTTP 服务本身可用，但 browser.tabs.open 返回「No desktop browser is connected to this session」，浏览器通道不可用，未能靠它看图。随后读图工具自行恢复，case-08 / case-04 仍用读图工具直接查看完成。本条不计为成功的能力应用，仅记录排查过程。"}
'@

"iterations total : " + (Get-Content $it).Count
"tool-usage total : " + (Get-Content $tu).Count
foreach ($f in @('requests.jsonl','iterations.jsonl','tool-usage.jsonl')) {
    $p = Join-Path $tmp $f
    $bad = 0; $n = 0
    foreach ($line in [System.IO.File]::ReadAllLines($p)) {
        $n++
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { $null = $line | ConvertFrom-Json } catch { $bad++; "BAD line $n in ${f}: $($_.Exception.Message)" }
    }
    "$f : $n lines, $bad bad"
}
