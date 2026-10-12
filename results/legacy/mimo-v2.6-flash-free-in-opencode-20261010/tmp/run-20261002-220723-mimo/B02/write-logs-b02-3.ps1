# Append-only log writer for B02 round 3 (2026-10-06): r7/r8/r3 visual passes,
# cross-work element audit, archive/reconstruction tool usage.
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

# ---------------------------------------------------------------- iterations
Add-Jsonl $it @'
{"iteration_id":"ite-B02-c01-v7-visual","case_id":"case-01","version":"v7","parent_version":"v6","type":"visual","request_id":"B02-c01-r7","http_status":200,"duration_ms":4786.8,"render_ended_utc":"2026-10-06T05:35:57.672Z","viewed":true,"view_evidence":"读图工具直接打开 outputs/run-20261002-220723-mimo/B02/case-01/final.png（本次内容正确返回）；另存自标注副本 tmp/run-20261002-220723-mimo/B02/view/","observation":"进度环亮弧自 12 点起顺时针扫到约 8 点方向即止，缺口落在左上象限；System.Drawing 逐 0.5 度复测 203/720 = 28.19%、起点样本 716（358 度）与 DialArc 参数 0.28 一致；环内 28% 与下方「迁徙季 · 第 16/57 天」一致（16/57 = 28.07%）。目标物种数已由 132 改为 143，与 case-09 记载的上一季 132 种不再冲突，且 143 = 132 + 11（本届新增 11 种）与 case-09 的「新增 11 种」自洽。三行表头、DN/DM 环志编号、17:30 交表与 case-03/05 一致","change":"进度环 SWEEP 渐变环改为确定性 DialArc（B01 case-08 同源修复）；目标物种 132 -> 143","result":"完成 visual iteration #1，海报类数据与其他 9 件作品对齐"}
'@

Add-Jsonl $it @'
{"iteration_id":"ite-B02-c04-v7-visual","case_id":"case-04","version":"v7","parent_version":"v6","type":"visual","request_id":"B02-c04-r8","http_status":200,"duration_ms":3103.2,"render_ended_utc":"2026-10-06T05:36:00.830Z","viewed":true,"view_evidence":"读图工具直接打开 outputs/run-20261002-220723-mimo/B02/case-04/final.png（本次内容正确返回）","observation":"柱状图横轴为 10 11 12 13 14 15 16 17 八个整点，柱高依次 28 41 37 34 31 28 25 21，峰值 41 落在 11:00；最末一根柱高 21 与右上「在站 21 人」完全一致，逐小时回落到当前值的叙述成立。图注「峰值 11:00 为 41 人，之后逐小时回落至当前 21 人」与图形一致。16 行鸣种表求和 412 只、16 种，与「今日鸟种 16 种 · 累计 412 只」「总记录条数 412」三处一致；借出望远镜 9/12 与 case-03 的 12 台一致","change":"在站趋势图由 12 点起改为 10-17 时八点序列并重算柱高（28/41/37/34/31/28/25/21），重写峰值图注；在站人数 21 与末柱对齐","result":"完成 visual iteration #1，四块看板数值全部自洽"}
'@

Add-Jsonl $it @'
{"iteration_id":"ite-B02-c05-v3-visual","case_id":"case-05","version":"v3","parent_version":"v2","type":"visual","request_id":"B02-c05-r3","http_status":200,"duration_ms":4574,"render_ended_utc":"2026-10-06T06:16:22.217Z","viewed":true,"view_evidence":"读图工具直接打开 outputs/run-20261002-220723-mimo/B02/case-05/final.png（本次内容正确返回）","observation":"第 3 条已变为「记录五要素 / 时间 / 种类 / 数量 / 行为 / 备注 / 五项与野外记录表逐列对应，别记在自己手背上」，与 case-06 野外记录表的副标题「五要素缺一不可：时间 / 种类 / 数量 / 行为 / 备注」及其表格列头（时间/物种/数量/行为/备注）逐项对应；其余四环节、P.2/P.4/P.6/P.8 页码、17:30 交表、四个小组、完成勾选四项均无位移，版面与 v2 相同","change":"第 3 条第五要素由「天气」改为「备注」，副句改为「五项与野外记录表逐列对应」——跨作品一致性核查发现 case-05 与 case-06 对「五要素」的枚举不一致，野外记录表（case-06）才是学员要真正填写的表单，故以表单为准修正文案","result":"完成 visual iteration #1，跨作品元素命名统一"}
'@

Add-Jsonl $it @'
{"iteration_id":"ite-B02-crosswork-elements","case_id":"","version":"","parent_version":null,"type":"requirement-change","request_id":"","http_status":null,"duration_ms":null,"render_ended_utc":null,"viewed":true,"view_evidence":"逐张重开 outputs/run-20261002-220723-mimo/B02/case-02、case-03、case-05、case-06、case-10 的 final.png 并与 case-01/04/07/09 的先前查看记录比对","observation":"逐件核对共享品牌元素与跨作品数字：候鸟湾观鸟站 / MIGRANT BAY BIRD OBSERVATORY / 人字鸟阵 Mark / 深青 #0B3B3A / 落日橙 #E4622C / RuleBand / FooterLine 十件全部在位；北门（case-01/03/05/06/10）、06:00-18:00 免费开放、12 台双筒（case-03/04/09）、17:30 交表（case-03/05）、4 个观测点约 2.4 km（case-01/02）、10/10 周六 06:30 北门（case-01/04）、132 + 11 = 143 种（case-01/09）、341 = 214 + 96 + 31 与约 1.7 万元/月（case-09/10）、62 名志愿者 / MB-V-0062（case-01/07/09）均一致。发现唯一不一致：case-05 第 3 条的「五要素」第五项写天气，case-06 野外记录表写备注","change":"据此发起 B02-c05-r3 修正 case-05 文案（见 ite-B02-c05-v3-visual）；case-01 的目标物种 132 与 case-09 上一季 132 重复，已在 B02-c01-r7 改为 143；case-04 柱状图与在站人数的对齐已在 B02-c04-r8 修正","result":"10 件作品的品牌元素与关键数字全部交叉一致"}
'@

# ---------------------------------------------------------------- tool usage
Add-Jsonl $tu @'
{"tool_id":"tu-11","tool":"版本归档与 DSL 重建（attempts/）","category":"留痕与保留","purpose":"在覆盖前把被取代的 PNG/DSL 复制到临时 attempts 目录；当 DSL 已被生成程序覆盖时，用还原后的生成程序重新生成出被取代版本的 DSL","input":"outputs/run-20261002-220723-mimo/B02/case-05/final.png + final.snapshot；gen-b02-a.ps1 中的第 3 条文案行","output":"tmp/run-20261002-220723-mimo/B02/attempts/case-05.v2-final.png、case-05.v2-final.snapshot、case-05.v3-final.snapshot","affected_cases":["case-05"],"http_request_ids":[],"double_counted":false,"note":"B02 早期的被取代 DSL/PNG 是被生成程序就地覆盖的，没有 attempts 目录（诚实记录的留痕缺口，见 snapshot-usage.md）。本轮起补上：先归档 v2 的 PNG（文件长 165540 B 与 requests.jsonl 中 B02-c05-r2 的响应字节数完全一致，可反证归档件就是 r2 的原始字节），再把生成程序的文案行还原、重新生成得到 c05=14270 的 v2 DSL 存档，最后还原新文案再生成并用 SHA256 校验 final.snapshot 恢复到 v3 哈希，确认没有把交付版覆盖坏。全程 0 次额外渲染请求。"}
'@

Add-Jsonl $tu @'
{"tool_id":"tu-12","tool":"跨作品数值一致性核查","category":"数据/一致性检查","purpose":"对 10 件作品的共享品牌元素、地点/时间/设备/期数等关键数字逐条交叉比对，并对可求和的表列做加法验证","input":"outputs/run-20261002-220723-mimo/B02/case-01..10/final.snapshot 的文案段落 + 各图查看记录","output":"发现 1 处不一致（case-05 与 case-06 的五要素枚举）与 2 处已在前轮修掉的冲突（132 种重复、柱状图与在站人数），随后发起 B02-c05-r3","affected_cases":["case-01","case-03","case-04","case-05","case-06","case-07","case-09","case-10"],"http_request_ids":[],"double_counted":false,"note":"已验证的算式：case-04 十六行 96+12+28+36+18+9+44+27+14+8+3+16+22+4+11+64 = 412（16 种）；case-06 24+2+8+5+3+4 = 46 只（6 种）；case-09 214+96+31 = 341 人、214x30+96x68+31x128 = 16916 元/月 ≈ 1.7 万元；case-10 三档 0.5/1.2/2.5 亩与 341 人对应；case-01 16/57 = 28.07% 与环形进度 28% 对应；132+11 = 143。"}
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
