# Append-only log writer for the B01 case-08 post-closure ring correction (2026-10-06).
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B01'
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Add-Jsonl([string]$path, [string]$line) {
    $existing = @()
    if (Test-Path $path) { $existing = @(Get-Content $path -Encoding UTF8) }
    foreach ($e in $existing) {
        if ([string]::IsNullOrWhiteSpace($e)) { continue }
        $o = $e | ConvertFrom-Json
        $n = $line | ConvertFrom-Json
        if ($o.iteration_id -and $n.iteration_id -and $o.iteration_id -eq $n.iteration_id) { return 'skip ' + $n.iteration_id }
        if ($o.tool_id -and $n.tool_id -and $o.tool_id -eq $n.tool_id) { return 'skip ' + $n.tool_id }
    }
    [IO.File]::AppendAllText($path, $line + "`n", $utf8)
    return 'ok   ' + (($line | ConvertFrom-Json) | ForEach-Object { if ($_.iteration_id) { $_.iteration_id } else { $_.tool_id } })
}

# ---------------- iterations.jsonl ----------------
$it = Join-Path $tmp 'iterations.jsonl'

$r1 = @'
{"iteration_id":"ite-B01-c08-v1-baseline-erroneous-verdict","case_id":"case-08","version":"v1","parent_version":null,"type":"baseline","request_id":"B01-c08-r1","http_status":200,"duration_ms":3071.8,"render_ended_utc":"2026-10-05T08:55:32.452Z","viewed":true,"view_evidence":"读图工具直接打开 outputs/run-20261002-220723-mimo/B01/case-08/final.png（当时返回的字节与该版本一致）","observation":"当时判定 4 条完成标准全部通过，记为首版即合格；2026-10-06 逐半度取样证明该判定有误——亮弧仅 50.14% 且自 90°（3 点方向）起，而非声明的 75% 自 12 点起","change":null,"result":"原判定已由 ite-B01-c08-v2-visual 撤回并修正"}
'@
Add-Jsonl $it $r1

$r2 = @'
{"iteration_id":"ite-B01-c08-v2-visual","case_id":"case-08","version":"v2","parent_version":"v1","type":"visual-iteration","request_id":"B01-c08-r2","http_status":200,"duration_ms":4580.4,"render_ended_utc":"2026-10-06T05:41:49.132Z","viewed":true,"view_evidence":"读图工具直接打开 outputs/run-20261002-220723-mimo/B01/case-08/final.png（r2 版本，本次内容正确返回）","observation":"橙色亮弧自 12 点起顺时针扫到 9 点方向即止，缺口落在 9 点→12 点的左上象限，即精确 75%；环内 3/4 与「免疫程序完成」仍居中且在白色镂空内；两张接种卡、10-24 预约日期与 2x2 注意事项均无位移；System.Drawing 复测 542/720 = 75.28%、起点样本 716（358°）","change":"case-08 进度环改用确定性 DialArc(156,360,260,0.75,#FF8A5B,#F6E4D6,32,100)：先画白色镂空圆，再用 100 个 Rotate+C 分段先铺暗弧、后覆盖亮弧；gen-b01-b.ps1 中 RingProg 保留为记录并加注说明，lib-b01.ps1 新增 DialArc（同时供 B02 复用）。重新生成后 case-06/07/09/10 的 final.snapshot 哈希与修正前完全一致，仅 case-08 变化","result":"完成 visual iteration #1（关闭后修正），4 条完成标准重新逐条核对通过"}
'@
Add-Jsonl $it $r2

$r3 = @'
{"iteration_id":"ite-B01-c08-v1evidence-reconstruction","case_id":"case-08","version":"v1","parent_version":null,"type":"evidence-reconstruction","request_id":"B01-c08-r1b","http_status":200,"duration_ms":2867.3,"render_ended_utc":"2026-10-06T05:54:54.575Z","viewed":true,"view_evidence":"读图工具打开 tmp/run-20261002-220723-mimo/B01/attempts/pre-ringfix-20261006/case-08.v1-reconstructed.png","observation":"重建图清晰显示橙色亮弧只覆盖 3 点→6 点→9 点的下半圈，上半圈整圈留白，与 50.14% 自 90° 起的量测结论完全吻合，直观复现了原缺陷","change":"用已归档的 v1 DSL（attempts/pre-ringfix-20261006/case-08.final.snapshot）重新渲染出被取代版本的图像证据，响应 179866 B 与 r1 记录的响应字节数完全一致，说明服务渲染是确定性的；不产生新的 DSL 版本，不写入 final.png","result":"被取代尝试的图像证据已归档并实际查看"}
'@
Add-Jsonl $it $r3

# ---------------- tool-usage.jsonl ----------------
$tu = Join-Path $tmp 'tool-usage.jsonl'

$t1 = @'
{"tool_id":"tu-12","tool":"System.Drawing 环形逐角度采样","category":"视觉/度量工具","purpose":"沿进度环圆周每 0.5° 取样一次，按颜色距离把样本分类为亮弧/暗弧/其他，量化实际弧度比例与起止角","input":"outputs/run-20261002-220723-mimo/B01/case-08/final.png（修正前后各一次）","output":"量测报告（直接打印到执行输出）","affected_cases":["case-08"],"http_request_ids":[],"double_counted":false,"note":"修正前：亮 361/720 = 50.14%、ON 起点样本 180（90°）——与 case.md 声明的 75% 自 12 点起不符，据此判定 SWEEP 渐变不遵循 gradientStops/gradientStartAngle；修正后：亮 542/720 = 75.28%、ON 起点样本 716（358°）——达标。B02 复用同一方法复测 case-01（28.19%）、case-09（78.47%）均自 12 点起。该结论同时写入 lib-b01.ps1 DialArc 注释与 B02 lib-b02.ps1。"}
'@
Add-Jsonl $tu $t1

$t2 = @'
{"tool_id":"tu-13","tool":"渲染辅助 render.ps1（关闭后修正批次）","category":"渲染调用","purpose":"把修正版与证据重建版 DSL POST 到 open-snapshot /snapshot，落盘服务原始响应字节","input":"outputs/.../B01/case-08/final.snapshot（v2）、tmp/.../B01/attempts/pre-ringfix-20261006/case-08.final.snapshot（v1 重建）","output":"outputs/.../B01/case-08/final.png、tmp/.../B01/attempts/pre-ringfix-20261006/case-08.v1-reconstructed.png","affected_cases":["case-08"],"http_request_ids":["B01-c08-r2","B01-c08-r1b"],"double_counted":false,"note":"tu-11 是关闭前批次的调用记录（其 http_request_ids 列表为当时的 21 条）；本行为关闭后修正批次的补充记录，2 条请求同样只在 requests.jsonl 计入一次。"}
'@
Add-Jsonl $tu $t2

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
