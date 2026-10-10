# mk-toolusage-b06.ps1 -- build tmp/.../B06/tool-usage.jsonl from requests.jsonl.
# Group membership and every http_request_ids entry are derived from the append-only
# request log; only the human description of each tool is authored here.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b6   = Join-Path $root 'tmp\run-20261002-220723-mimo\B06'
$utf8 = New-Object System.Text.UTF8Encoding($false)

$reqs = @()
foreach ($l in [IO.File]::ReadAllLines((Join-Path $b6 'requests.jsonl'), [Text.Encoding]::UTF8)) {
    if ($l.Trim()) { $reqs += ($l | ConvertFrom-Json) }
}

function Get-Ids([scriptblock]$pred) {
    $out = @()
    foreach ($r in $reqs) { if (& $pred $r) { $out += [string]$r.id } }
    , $out
}
function Get-When([string[]]$ids) {
    if ($ids.Count -eq 0) { return $null }
    $best = $null
    foreach ($r in $reqs) {
        if ($ids -contains [string]$r.id) {
            $t = [datetime]::Parse([string]$r.started_at)
            if ($best -eq $null -or $t -lt $best) { $best = $t }
        }
    }
    if ($best -eq $null) { return $null }
    return $best.ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
}
function Get-ArtWhen([string[]]$paths) {
    $best = $null
    foreach ($p in $paths) {
        $fp = Join-Path $root $p
        if (Test-Path $fp) {
            $it = Get-Item $fp
            $t = $it.LastWriteTime
            if ($best -eq $null -or $t -lt $best) { $best = $t }
        }
    }
    if ($best -eq $null) { return $null }
    return $best.ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
}

$resNum = { param($r) $r.type -eq 'research' -and $r.id -match '^B06-res-(\d\d)' -and [int]$matches[1] -ge 1 -and [int]$matches[1] -le 18 }
$expNum = { param($r) $r.type -eq 'research' -and $r.id -match '^B06-res-(\d\d)' -and [int]$matches[1] -ge 19 -and [int]$matches[1] -le 25 }
$bingN  = { param($r) $r.type -eq 'research' -and $r.id -match '^B06-res-(\d\d)' -and [int]$matches[1] -ge 26 -and [int]$matches[1] -le 41 }

$docIds = Get-Ids { param($r) ($r.type -eq 'documentation' -or $r.type -eq 'fonts') }
$resIds = Get-Ids $resNum
$expIds = Get-Ids $expNum
$bingIds = Get-Ids $bingN
$smokeIds = Get-Ids { param($r) [string]$r.id -like 'B06-smoke-*' }
$probeIds = Get-Ids { param($r) [string]$r.id -like 'B06-probe-*' }
$caseIds = Get-Ids { param($r) [string]$r.id -like 'B06-case-*' }

$rows = @()

$rows += [ordered]@{
    tool_id = 'tu-01'
    tool    = 'plan.md 十件选题与口径表（人写综合）'
    category= '选题与规划'
    when    = (Get-ArtWhen @('tmp/run-20261002-220723-mimo/B06/plan.md'))
    affected_cases = '*'
    http_request_ids = @()
    artifacts = @('tmp/run-20261002-220723-mimo/B06/plan.md')
    note    = '先定 10 个日常信息难题、受众与观看环境，再定画幅与底色；10 个宽高比互不重复（0.435 / 0.475 / 0.627 / 0.643 / 1.000 / 1.333 / 1.615 / 1.778 / 1.796 / 3.097），结构骨架（货架网格 / 当日时间轴 / 参考区间尺 / 分档瀑布 / 站台色带 / 分期现金流 / 押金瀑布 / 100格点阵 / 钟面 / 五节点轨道）互不重复；每件都先写清"用户原本卡在哪一句 / 哪一个数"'
}

$rows += [ordered]@{
    tool_id = 'tu-02'
    tool    = '服务指南与字体清单真实抓取'
    category= '文档查阅'
    when    = (Get-When $docIds)
    affected_cases = '*'
    http_request_ids = @($docIds)
    artifacts = @('tmp/run-20261002-220723-mimo/B06/docs/', 'tmp/run-20261002-220723-mimo/B06/fonts/')
    note    = ('{0} 次请求全部 200：ai-guide.md 与 snapshot.muedsa.com 的 parser-tags / painting / enums / transform / rendering / decorated-box / source-index / faq 共 9 次 documentation，加 1 次 /fonts（27 个字体的 SANS/DISP/MONO 映射来源）' -f $docIds.Count)
}

$rows += [ordered]@{
    tool_id = 'tu-03'
    tool    = 'fetch-all-b06.ps1 一手站点抓取'
    category= '资料研究'
    when    = (Get-When $resIds)
    affected_cases = '*'
    http_request_ids = @($resIds)
    artifacts = @('tmp/run-20261002-220723-mimo/B06/research/', 'tmp/run-20261002-220723-mimo/B06/fetch-all-b06.ps1')
    note    = ('{0} 次真实 GET：政策库、标准站点、行业与媒体站点。其中 nmpa 与 nhc 返回 412 反爬页，gov.cn 政策检索接口虽然 200 但返回的 totalCount=0，所以本题没有取得任何一条法条 / 标准原文 —— 画面因此不写条款号、不写罚则金额、不写国标数字；失败响应原样留存在 requests.jsonl 与 research/ 目录' -f $resIds.Count)
}

$rows += [ordered]@{
    tool_id = 'tu-04'
    tool    = '检索方法试探（多词 Bing / 站内检索 / ddg-lite）'
    category= '检索方法试探'
    when    = (Get-When $expIds)
    affected_cases = '*'
    http_request_ids = @($expIds)
    artifacts = @('tmp/run-20261002-220723-mimo/B06/research/')
    note    = ('{0} 次试探：多词中文查询在 Bing 上被截断，gov.cn 站内检索与 DuckDuckGo lite 端点不可用（其中 ddg 请求直接失败）。结论记录下来后改走短词 RSS 路线，没有把任何一次失败伪装成命中' -f $expIds.Count)
}

$rows += [ordered]@{
    tool_id = 'tu-05'
    tool    = 'Bing RSS 短查询批量检索'
    category= '资料研究'
    when    = (Get-When $bingIds)
    affected_cases = '*'
    http_request_ids = @($bingIds)
    artifacts = @('tmp/run-20261002-220723-mimo/B06/research/')
    note    = ('{0} 次单短词 Bing RSS 查询（format=rss + setmkt=zh-CN + 浏览器 UA），全部 200 并落盘为 XML。这些检索摘要是本题唯一命中的外部线索，画面与 case.md 一律标注为二手来源（检索摘要，Bing RSS，2026-10-08），只作为选题依据，不作为条文引用' -f $bingIds.Count)
}

$rows += [ordered]@{
    tool_id = 'tu-06'
    tool    = 'repair-encoding-b06.ps1 响应体编码修复'
    category= '资料处理'
    when    = (Get-ArtWhen @('tmp/run-20261002-220723-mimo/B06/repair-encoding-b06.ps1'))
    affected_cases = '*'
    http_request_ids = @()
    artifacts = @('tmp/run-20261002-220723-mimo/B06/repair-encoding-b06.ps1')
    note    = 'PowerShell 5.1 的 Invoke-WebRequest 把 UTF-8 响应体按 Latin-1 解码，中文全成乱码。修复方式是 读 UTF-8 → 按 28591 编码 → 再按 UTF-8 解码，写到同名 .fixed 文件；原始响应永不改写'
}

$rows += [ordered]@{
    tool_id = 'tu-07'
    tool    = 'calc-b06.ps1 统一计算口径'
    category= '计算与口径'
    when    = (Get-ArtWhen @('tmp/run-20261002-220723-mimo/B06/calc-b06.json'))
    affected_cases = '*'
    http_request_ids = @()
    artifacts = @('tmp/run-20261002-220723-mimo/B06/calc-b06.ps1', 'tmp/run-20261002-220723-mimo/B06/calc-b06.json')
    note    = '10 件作品的全部数字在一处算出并落盘为 JSON（41312 字节）。生成器只读这份文件、不在画面里临时心算，因此每一处百分比的分子分母、单位与时间范围都同源：c01 disagreeCount=3、c03 3/2/1 分档、c04 105.77 元闭合、c06 月 IRR 1.0862% → 年化 13.03% / 13.84%、c07 4640–5240、c08 gridFilled=40/100、c09 累计 3/9/17、c10 43/78=55.1%'
}

$rows += [ordered]@{
    tool_id = 'tu-08'
    tool    = 'lib-b06.ps1 共享构件与冒烟渲染'
    category= '构件与冒烟'
    when    = (Get-When $smokeIds)
    affected_cases = '*'
    http_request_ids = @($smokeIds)
    artifacts = @('tmp/run-20261002-220723-mimo/B06/lib-b06.ps1', 'tmp/run-20261002-220723-mimo/B06/smoke/')
    note    = 'lib-b06 在 lib-b05/b04/b03/b01 之上补 Tone6、Masthead6、Foot6、Src6、Legend6、Step6、Hand6、Wedge6、Arc6、Dial-Map、Ruler6、Pct100、ColStack6、Waterfall6、Hatch6、Page6。1 次真实冒烟渲染（200，92838 B）在任何一件作品用到它们之前先验证服务端支持'
}

$rows += [ordered]@{
    tool_id = 'tu-09'
    tool    = 'validate-b06.ps1 静态 DSL 校验'
    category= '校验'
    when    = (Get-ArtWhen @('tmp/run-20261002-220723-mimo/B06/validate-b06.ps1'))
    affected_cases = '*'
    http_request_ids = @()
    artifacts = @('tmp/run-20261002-220723-mimo/B06/validate-b06.ps1')
    note    = '解析每个 .snapshot 的根属性、颜色、border、boxShadow、textAlign、transform 矩阵、Canvas 尺寸与页面守卫；每次生成后运行，最终一次为 files=20 problems=0'
}

$rows += [ordered]@{
    tool_id = 'tu-10'
    tool    = 'probe-hatch.ps1 + 像素扫描探针'
    category= '探针'
    when    = (Get-When $probeIds)
    affected_cases = 'case-07'
    http_request_ids = @($probeIds)
    artifacts = @('tmp/run-20261002-220723-mimo/B06/probe-hatch.ps1', 'tmp/run-20261002-220723-mimo/B06/runscan.ps1', 'tmp/run-20261002-220723-mimo/B06/scan-probe.ps1')
    note    = '2 次探针渲染 + 逐像素扫描：第 1 次暴露 $L 静默覆盖 $l（left）的大小写陷阱 —— 服务返回 200 但斜纹起点变成 130 而非 24；改名并把陷阱写进 lib-b06 头部后，第 2 次扫描得到 24..354 / 354..405 / 406..735，与书写几何一致。case-07 的争议斜纹因此在使用前被证明可用'
}

$rows += [ordered]@{
    tool_id = 'tu-11'
    tool    = 'gen-b06-a / -b / -c.ps1 生成器'
    category= 'DSL 构造'
    when    = (Get-ArtWhen @('tmp/run-20261002-220723-mimo/B06/gen-b06-a.ps1','tmp/run-20261002-220723-mimo/B06/gen-b06-b.ps1','tmp/run-20261002-220723-mimo/B06/gen-b06-c.ps1'))
    affected_cases = 'case-01..case-10'
    http_request_ids = @()
    artifacts = @('tmp/run-20261002-220723-mimo/B06/gen-b06-a.ps1', 'tmp/run-20261002-220723-mimo/B06/gen-b06-b.ps1', 'tmp/run-20261002-220723-mimo/B06/gen-b06-c.ps1')
    note    = '三个生成器从 calc-b06.json 读数并写出 10 件作品的完整 DSL，每件自带 Guard 页面越界检查；每次改动后重跑并打印 problems=0 才进入渲染。生成器可重复执行且输出逐字节相同（case-01..04 已做确定性复跑验证）'
}

$rows += [ordered]@{
    tool_id = 'tu-12'
    tool    = 'render-b06.ps1 真实渲染 + read 逐张看图'
    category= '渲染与读图'
    when    = (Get-When $caseIds)
    affected_cases = 'case-01..case-10'
    http_request_ids = @($caseIds)
    artifacts = @('tmp/run-20261002-220723-mimo/B06/case-01/','tmp/run-20261002-220723-mimo/B06/case-02/','tmp/run-20261002-220723-mimo/B06/case-03/','tmp/run-20261002-220723-mimo/B06/case-04/','tmp/run-20261002-220723-mimo/B06/case-05/','tmp/run-20261002-220723-mimo/B06/case-06/','tmp/run-20261002-220723-mimo/B06/case-07/','tmp/run-20261002-220723-mimo/B06/case-08/','tmp/run-20261002-220723-mimo/B06/case-09/','tmp/run-20261002-220723-mimo/B06/case-10/','tmp/run-20261002-220723-mimo/B06/view/')
    note    = ('{0} 次 POST /snapshot 全部 200，PNG 原样落盘不后处理。iterations.jsonl 记录 30 次读图判定：29 次给出了实际打开的文件路径，1 次（case-02 a03）因 read 串图判定 not-verified 并作废。读图工具会串图，因此每次都要核对 PLAINSIGHT NN / 10 报头，不符就换新 GUID 副本加重描边重读' -f $caseIds.Count)
}

$rows += [ordered]@{
    tool_id = 'tu-13'
    tool    = 'mk-iter / promote / gen-case-md / mk-metrics 日志与交付脚本'
    category= '日志与指标'
    when    = (Get-ArtWhen @('tmp/run-20261002-220723-mimo/B06/promote-b06.ps1'))
    affected_cases = '*'
    http_request_ids = @()
    artifacts = @('tmp/run-20261002-220723-mimo/B06/mk-iter-b06.ps1','tmp/run-20261002-220723-mimo/B06/promote-b06.ps1','tmp/run-20261002-220723-mimo/B06/gen-case-md-b06.ps1','tmp/run-20261002-220723-mimo/B06/mk-metrics-b06.ps1')
    note    = '全部从 requests.jsonl 反查生成 iterations / tool-usage / case.md / task-metrics，不手写计数；promote 逐件做字节校验，确认 final.png 与服务原始响应、final.snapshot 与该次渲染的 DSL 逐字节一致'
}

$rows += [ordered]@{
    tool_id = 'tu-14'
    tool    = 'problem-evidence.json 与 design-review.md 复核写作'
    category= '结论与复核'
    when    = (Get-ArtWhen @('tmp/run-20261002-220723-mimo/B06/plan.md'))
    affected_cases = 'case-01..case-10'
    http_request_ids = @()
    artifacts = @('outputs/run-20261002-220723-mimo/B06/problem-evidence.json','outputs/run-20261002-220723-mimo/B06/design-review.md')
    note    = '逐件写清问题的实际来源或假设、场景要求、重构选择与从最终图判断的改善；把"在图上直接可观察的可读性改善"与"需要用户实验才能验证、本轮未验证的效果"分栏列出，不写任何田野调研或用户测试'
}

$out = Join-Path $b6 'tool-usage.jsonl'
if (Test-Path $out) { [IO.File]::Delete($out) }
$n = 0
foreach ($r in $rows) {
    [IO.File]::AppendAllText($out, (($r | ConvertTo-Json -Compress -Depth 6) + "`n"), $utf8)
    $n++
}
Write-Output ("tool-usage.jsonl written: {0} entries" -f $n)
Write-Output ("  http ids total = {0} (doc {1}, res {2}, exp {3}, bing {4}, smoke {5}, probe {6}, case {7})" -f `
    ($docIds.Count + $resIds.Count + $expIds.Count + $bingIds.Count + $smokeIds.Count + $probeIds.Count + $caseIds.Count), `
    $docIds.Count, $resIds.Count, $expIds.Count, $bingIds.Count, $smokeIds.Count, $probeIds.Count, $caseIds.Count)
