$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B02'
$enc  = New-Object System.Text.UTF8Encoding($false)

# append-only guard: never clobber an existing trace file
foreach ($f in @('requests.jsonl', 'iterations.jsonl', 'tool-usage.jsonl')) {
    $p = Join-Path $tmp $f
    if (($f -ne 'requests.jsonl') -and (Test-Path $p)) { throw "refusing to overwrite $p" }
}

function J([object]$o) {
    $s = $o | ConvertTo-Json -Compress -Depth 6
    # PS 5.1 escapes non-ASCII; put readable UTF-8 back
    $s = [regex]::Replace($s, '\\u(?<c>[0-9a-fA-F]{4})', { param($m) [char][int]('0x' + $m.Groups['c'].Value) })
    return $s
}

# ---------------------------------------------------------------- requests.jsonl
# One transport-level failure happened before any HTTP exchange (DNS lookup failed
# inside curl); render.ps1 threw while moving a non-existent error body, so no row
# was written. Record it honestly rather than dropping it.
$dnsRow = @{
    id              = 'B02-c06-r2'
    task            = 'B02'
    type            = 'render_transport_error'
    started_utc     = $null
    ended_utc       = $null
    tz              = 'UTC'
    duration_ms     = $null
    method          = 'POST'
    path            = '/snapshot'
    http_status     = $null
    content_type    = $null
    bytes           = 0
    request_file    = (Join-Path $root 'outputs\run-20261002-220723-mimo\B02\case-06\final.snapshot')
    response_file   = $null
    request_id      = $null
    server_timing   = $null
    ratelimit_remaining = $null
    error_summary   = 'TRANSPORT_ERROR: curl (6) Could not resolve host: open-snapshot.muedsa.com'
    attempt         = 1
    note            = 'DNS failure before any HTTP exchange, so no wall-clock was captured; occurred immediately before B02-c06-r1-retry (2026-10-06T04:55:56.433Z). render.ps1 then threw on Move-Item of a non-existent error body and the batch stopped; the next batch retried all four cases successfully.'
}
$reqLog = Join-Path $tmp 'requests.jsonl'
if (-not (Select-String -Path $reqLog -Pattern '"id":"B02-c06-r2"' -Quiet -ErrorAction SilentlyContinue)) {
    Add-Content -Path $reqLog -Value (J $dnsRow) -Encoding UTF8
}

# ---------------------------------------------------------------- iterations.jsonl
$iters = @()

function I([hashtable]$h) { $script:iters += , $h }

# ---- case-01
I @{ iteration_id='ite-B02-c01-v1-syntaxfix'; case_id='case-01'; version='v1'; parent_version=$null; type='syntax-fix'
    request_id='B02-c01-r1'; http_status=400; duration_ms=1918.3; render_ended_utc='2026-10-05T09:53:15.025Z'
    viewed=$false; view_evidence=$null
    observation='PARSE_ERROR: Attr [fontStyle] value is invalid: Unexpected font style bold（小写 bold 被解析器拒绝）'
    change='生成库中 fontStyle 全部改为大写 BOLD（合法值 NORMAL/BOLD/ITALIC/BOLD_ITALIC）'
    result='语法修复，待下次渲染' }
I @{ iteration_id='ite-B02-c01-v2-baseline'; case_id='case-01'; version='v2'; parent_version='v1'; type='baseline'
    request_id='B02-c01-r2'; http_status=200; duration_ms=4390.1; render_ended_utc='2026-10-05T09:56:36.943Z'
    viewed=$true; view_evidence='读图工具打开 outputs/run-20261002-220723-mimo/B02/case-01/final.png（r2 版本，已被 r5 取代）'
    observation='版式、层级、页脚、演示标识均成立；但「迁徙季进度环」的亮弧起点不在 12 点方向，与声明的 gradientStartAngle=-π/2 不符'
    change='计划改用分段圆弧替代 SWEEP 渐变环'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c01-v3-syntaxfix'; case_id='case-01'; version='v3'; parent_version='v2'; type='syntax-fix'
    request_id='B02-c01-r3'; http_status=400; duration_ms=1864.1; render_ended_utc='2026-10-05T10:07:11.835Z'
    viewed=$false; view_evidence=$null
    observation='PARSE_ERROR: Unexpected character ''"'' in input state [AFTER_ATTR_VALUE_QUOTED]，gradientEndAngle 属性值后多出一个引号（补丁脚本写坏）'
    change='去掉多余引号后重新生成'
    result='语法修复，待下次渲染' }
I @{ iteration_id='ite-B02-c01-v4-visual'; case_id='case-01'; version='v4'; parent_version='v3'; type='visual'
    request_id='B02-c01-r4'; http_status=200; duration_ms=4217.6; render_ended_utc='2026-10-05T10:07:54.032Z'
    viewed=$true; view_evidence='读图工具打开 outputs/run-20261002-220723-mimo/B02/case-01/final.png（r4 版本，已被 r5 取代）'
    observation='用 System.Drawing 逐角度采样量得：声明 start=-π/2 / end=3π/2、停点 0,f,f,1 的 SWEEP 环，实际亮弧落在钟面 [f·360°, (f+90)°] 而非 [0°, f·360°]（f=0.62 实测亮段自 138° 起）'
    change='以确定性 DialArc（N=100 个 Rotate+C 分段，先画 OFF 再画 ON 覆盖）替换 SWEEP 渐变环'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c01-v5-visual'; case_id='case-01'; version='v5'; parent_version='v4'; type='visual'
    request_id='B02-c01-r5'; http_status=200; duration_ms=9567.5; render_ended_utc='2026-10-06T04:42:26.020Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/v01-20261006124241010.png（唯一时间戳副本）'
    observation='measure-ring.ps1 量得 ON 占 62.36%、亮段起点钟面 357.5°（即 12 点方向顺时针），与 62% 目标一致（多出的 0.36% 为末段 1.28 倍重叠）；图上亮弧自 12 点顺时针扫到约 7 点位'
    change=$null
    result='完成，通过' }

# ---- case-02
I @{ iteration_id='ite-B02-c02-v1-syntaxfix'; case_id='case-02'; version='v1'; parent_version=$null; type='syntax-fix'
    request_id='B02-c02-r1'; http_status=400; duration_ms=1973.4; render_ended_utc='2026-10-05T09:53:17.087Z'
    viewed=$false; view_evidence=$null
    observation='PARSE_ERROR: Attr [gradientBegin] value format error（传了 ''0,0'' 坐标）'
    change='gradientBegin/gradientEnd 改用 BoxAlignment 枚举常量（TOP_LEFT / BOTTOM_RIGHT 等）'
    result='语法修复，待下次渲染' }
I @{ iteration_id='ite-B02-c02-v2-baseline'; case_id='case-02'; version='v2'; parent_version='v1'; type='baseline'
    request_id='B02-c02-r2'; http_status=200; duration_ms=3707.9; render_ended_utc='2026-10-05T09:56:40.712Z'
    viewed=$true; view_evidence='读图工具打开 outputs/run-20261002-220723-mimo/B02/case-02/final.png（r2 版本，已被 r3 取代）'
    observation='标题「四条路线，四个点」与图上 4 个点/1 条环线不符；北门入口胶囊压在图例面板上；指北针缺少构成；图例只有 2 行、缺少栈道样式；水面缺少浅滩与航道信息；比例尺在深浅底上不可读'
    change='标题改为「一条环线，四个点」；重建指北针（橙点 + N）；入口胶囊移到 x=500 避开面板；图例扩到 3 行并补白色虚线步道；补浅滩色块与航道虚线；比例尺做深浅双段'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c02-v3-visual'; case_id='case-02'; version='v3'; parent_version='v2'; type='visual'
    request_id='B02-c02-r3'; http_status=200; duration_ms=3532.6; render_ended_utc='2026-10-05T10:05:50.717Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk02-20261006124451349.jpg（自标注标签条副本）'
    observation='标题、指北针、入口位置、3 行图例、浅滩、航道与双段比例尺全部到位；4 个观测点与图例色一致；无裁切'
    change=$null
    result='完成，通过' }

# ---- case-03
I @{ iteration_id='ite-B02-c03-v1-syntaxfix'; case_id='case-03'; version='v1'; parent_version=$null; type='syntax-fix'
    request_id='B02-c03-r1'; http_status=400; duration_ms=1675.7; render_ended_utc='2026-10-05T09:53:18.782Z'
    viewed=$false; view_evidence=$null
    observation='PARSE_ERROR: Attr [fontStyle] value is invalid: Unexpected font style bold'
    change='fontStyle 改为 BOLD'
    result='语法修复，待下次渲染' }
I @{ iteration_id='ite-B02-c03-v2-baseline'; case_id='case-03'; version='v2'; parent_version='v1'; type='baseline'
    request_id='B02-c03-r2'; http_status=200; duration_ms=3390.0; render_ended_utc='2026-10-05T09:56:44.119Z'
    viewed=$true; view_evidence='读图工具打开 outputs/run-20261002-220723-mimo/B02/case-03/final.png（r2 版本，已被 r3 取代）'
    observation='双筒望远镜图解结构错误：目镜筒画在物镜筒下方、缺少连接桥与调焦轮、序号 ①②③ 与指示位置对不上'
    change='重建图解：目镜筒置于物镜筒之上、补镜片、连接桥、调焦轮、瞳距箭头，并把 ①②③ 放到真实指示位置，加一行图注'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c03-v3-visual'; case_id='case-03'; version='v3'; parent_version='v2'; type='visual'
    request_id='B02-c03-r3'; http_status=200; duration_ms=3262.1; render_ended_utc='2026-10-05T10:05:54.036Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk03-20261006124451349.jpg'
    observation='双筒轮廓可信，①调焦轮 / ②目镜 / ③瞳距三处标注位置正确；5 条礼仪与图注均未溢出'
    change=$null
    result='完成，通过' }

# ---- case-04
I @{ iteration_id='ite-B02-c04-v1-syntaxfix'; case_id='case-04'; version='v1'; parent_version=$null; type='syntax-fix'
    request_id='B02-c04-r1'; http_status=400; duration_ms=1780.5; render_ended_utc='2026-10-05T09:53:20.582Z'
    viewed=$false; view_evidence=$null
    observation='PARSE_ERROR: Attr [fontStyle] value is invalid: Unexpected font style bold'
    change='fontStyle 改为 BOLD'
    result='语法修复，待下次渲染' }
I @{ iteration_id='ite-B02-c04-v2-baseline'; case_id='case-04'; version='v2'; parent_version='v1'; type='baseline'
    request_id='B02-c04-r2'; http_status=200; duration_ms=3025.9; render_ended_utc='2026-10-05T09:56:47.160Z'
    viewed=$true; view_evidence='读图工具打开 outputs/run-20261002-220723-mimo/B02/case-04/final.png（r2 版本，已被 r3 取代）'
    observation='柱状图 x 轴标签渲染为 010/011/012/013（06..13 被当成 3 位最小宽度补零格式）；左栏「今日潮汐」下方留出约 120px 空白'
    change='小时标签改用 {0:d2} 生成 06..13；左栏重排，补峰值说明与「今日潮汐与下一步」区块到 y=964'
    result='语法修复+视觉修改，待下次渲染' }
I @{ iteration_id='ite-B02-c04-v3-syntaxfix'; case_id='case-04'; version='v3'; parent_version='v2'; type='syntax-fix'
    request_id='B02-c04-r3'; http_status=400; duration_ms=1713.7; render_ended_utc='2026-10-05T10:05:55.765Z'
    viewed=$false; view_evidence=$null
    observation='PARSE_ERROR: Attr [color] unsupported CSS color [System.Object[] System.Object[] System.Object[]] —— PowerShell 变量不区分大小写，循环里的 $tide 数组覆盖了配色常量 $TIDE'
    change='循环变量改名 $trow，配色常量不再被覆盖'
    result='语法修复，待下次渲染' }
I @{ iteration_id='ite-B02-c04-v4-visual'; case_id='case-04'; version='v4'; parent_version='v3'; type='visual'
    request_id='B02-c04-r3'; http_status=200; duration_ms=3332.0; render_ended_utc='2026-10-05T10:07:15.239Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk04-20261006124451349.jpg'
    observation='x 轴为 06..13；「峰值出现在 07:00，之后逐小时回落」与柱高一致；左栏潮汐区块填满到 y=964，落潮转向 17:50 用强调色标出'
    change=$null
    note='该请求 ID 与前一条 400 记录重复（render.ps1 传入同一 ReqId），requests.jsonl 中保留两条原始记录'
    result='完成，通过' }

# ---- case-05
I @{ iteration_id='ite-B02-c05-v1-syntaxfix'; case_id='case-05'; version='v1'; parent_version=$null; type='syntax-fix'
    request_id='B02-c05-r1'; http_status=400; duration_ms=1721.1; render_ended_utc='2026-10-05T09:53:22.326Z'
    viewed=$false; view_evidence=$null
    observation='PARSE_ERROR: Attr [fontStyle] value is invalid: Unexpected font style bold'
    change='fontStyle 改为 BOLD'
    result='语法修复，待下次渲染' }
I @{ iteration_id='ite-B02-c05-v2-baseline'; case_id='case-05'; version='v2'; parent_version='v1'; type='baseline'
    request_id='B02-c05-r2'; http_status=200; duration_ms=3105.4; render_ended_utc='2026-10-05T09:56:50.279Z'
    viewed=$true; view_evidence='读图工具打开 outputs/run-20261002-220723-mimo/B02/case-05/final.png'
    observation='封面层级、课节表、编号方块与页脚均成立；无溢出无遮挡'
    change=$null
    result='baseline 即合格，不制造无意义迭代' }

# ---- case-06
I @{ iteration_id='ite-B02-c06-v1-baseline'; case_id='case-06'; version='v1'; parent_version=$null; type='baseline'
    request_id='B02-c06-r1'; http_status=200; duration_ms=4446.9; render_ended_utc='2026-10-06T04:52:05.238Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk06-20261006125235094.jpg'
    observation='表头、6 行示例、合计 46 只 / 6 种、备注虚线均正确；但交替底色过浅、行分隔线过淡，14 行表格看起来像 4 个悬浮灰块'
    change='交替底色 0x0A→0x0D，行分隔线 0x22→0x4D'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c06-v2-visual'; case_id='case-06'; version='v2'; parent_version='v1'; type='visual'
    request_id='B02-c06-r1-retry'; http_status=200; duration_ms=2561.4; render_ended_utc='2026-10-06T04:55:59.000Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk06-20261006125616218.jpg，并用 System.Drawing 在 x=400 采样 y=545..865 复核'
    observation='14 行的分隔线全部出现，位置 y=555/593/631/…/859（每 38px 一行，与 rowH 完全一致），线色 (175,187,180) 与 30% 不透明度叠纸面的理论值一致'
    change=$null
    result='完成，通过' }

# ---- case-07
I @{ iteration_id='ite-B02-c07-v1-baseline'; case_id='case-07'; version='v1'; parent_version=$null; type='baseline'
    request_id='B02-c07-r1'; http_status=200; duration_ms=2442.7; render_ended_utc='2026-10-06T04:52:07.742Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk07-20261006125235094.jpg'
    observation='信息栅格、班次、服务时长强调色、三枚权限胶囊均成立；但头像由「圆 + 圆角矩形」两块分离组成，读起来像 8 字/雪人而不是人形'
    change='改为先画肩部圆角块（144×100、r44）再画头部圆（100px），肩宽 > 头宽且两块相接'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c07-v2-visual'; case_id='case-07'; version='v2'; parent_version='v1'; type='visual'
    request_id='B02-c07-r1-retry'; http_status=200; duration_ms=2233.8; render_ended_utc='2026-10-06T04:56:01.291Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk07-20261006125616218.jpg'
    observation='头肩轮廓连成一个正确的人形剪影，居中于照片位；其余信息未受影响'
    change=$null
    result='完成，通过' }

# ---- case-08
I @{ iteration_id='ite-B02-c08-v1-baseline'; case_id='case-08'; version='v1'; parent_version=$null; type='baseline'
    request_id='B02-c08-r1'; http_status=200; duration_ms=4109.3; render_ended_utc='2026-10-06T04:52:11.868Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk08-20261006125235094.jpg'
    observation='9 张日程卡 3×3 网格对齐，日期/星期/时间/标题/集合点/说明/余位七要素齐全；仅首场用强调色左边条表示「下一场」；页脚不出血；星期与 2026-10-05 为周日的日历一致'
    change=$null
    result='baseline 即合格，不制造无意义迭代' }

# ---- case-09
I @{ iteration_id='ite-B02-c09-v1-baseline'; case_id='case-09'; version='v1'; parent_version=$null; type='baseline'
    request_id='B02-c09-r1'; http_status=200; duration_ms=3361.4; render_ended_utc='2026-10-06T04:52:15.245Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk09-20261006125235094.jpg'
    observation='标题写「十大记录物种（按条数，前六）」自相矛盾；表头「物种」x=65 与物种名 x=88 不齐、「学名」x=420 与拉丁名 x=411 不齐'
    change='标题改为「记录物种（按条数，前六）」；表头 x 改为 88 / 411，与数据列精确对齐'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c09-v2-visual'; case_id='case-09'; version='v2'; parent_version='v1'; type='visual'
    request_id='B02-c09-r1-retry'; http_status=200; duration_ms=3621.8; render_ended_utc='2026-10-06T04:56:04.929Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk09-20261006125616218.jpg'
    observation='标题与两列表头对齐；78% 进度环的暗段约 22% 且位于左上方（亮段自 12 点顺时针 78%），与 0.78 一致；6 行物种计数 642/517/448/386/214/197 均在右对齐轴上'
    change=$null
    result='完成，通过' }

# ---- case-10
I @{ iteration_id='ite-B02-c10-v1-baseline'; case_id='case-10'; version='v1'; parent_version=$null; type='baseline'
    request_id='B02-c10-r1'; http_status=200; duration_ms=4476.1; render_ended_utc='2026-10-06T04:52:19.735Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk10-20261006125235094.jpg'
    observation='三档价格卡、CTA、免责声明、页脚均成立；但价格列（x≈100..300）与权益列（x=430）之间 130px 空档没有任何分隔，卡片读起来左右脱节'
    change='在 x=385 加一条竖分隔（y+30..y+128）'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c10-v2-visual'; case_id='case-10'; version='v2'; parent_version='v1'; type='visual'
    request_id='B02-c10-r1-retry'; http_status=200; duration_ms=2788.5; render_ended_utc='2026-10-06T04:56:07.733Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk10-20261006125616218.jpg'
    observation='竖线把价格列与权益列分开，结构清楚；但竖线终点 y+128 与横线起点 x=430 之间空 45px，两笔画悬空不相接'
    change='横线起点 x=430→385，长度 555→600，与竖线构成一个完整的 L 角'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c10-v3-visual'; case_id='case-10'; version='v3'; parent_version='v2'; type='visual'
    request_id='B02-c10-r3'; http_status=200; duration_ms=2862.8; render_ended_utc='2026-10-06T04:58:10.907Z'
    viewed=$true; view_evidence='读图工具打开 tmp/run-20261002-220723-mimo/B02/view/chk10-20261006125811007.jpg'
    observation='竖线与横线在 (385, y+128) 正确相交；三张卡结构一致；CTA 与页脚无裁切'
    change=$null
    result='完成，通过' }

# ---- shared: read-tool cache problem (incomplete view round)
I @{ iteration_id='ite-B02-view-cache-v1'; case_id='case-01'; version=$null; parent_version=$null; type='visual-incomplete'
    request_id=$null; http_status=$null; duration_ms=$null; render_ended_utc=$null
    viewed=$false
    view_evidence='tmp/run-20261002-220723-mimo/B02/view/v01..v05-20261006124241010.png 多次 read'
    observation='读图工具对已读路径返回旧的/错位的图像字节（请求 v02 三次都返回 case-01），无法确认看的是哪张；browser.preview 同时不可用（No desktop browser connected）'
    change='改为生成自带标签条的 JPEG 校验副本（顶部 64px 深色条写明 case 编号/名称/尺寸），图自带身份，错位也能自证；同时用 System.Drawing 做尺寸与像素复核'
    result='该轮判为未完成迭代；改用自标注副本后 10 件全部完成真实看图' }

$line = ($iters | ForEach-Object { J $_ }) -join "`n"
[System.IO.File]::WriteAllText((Join-Path $tmp 'iterations.jsonl'), $line + "`n", $enc)

# ---------------------------------------------------------------- tool-usage.jsonl
$tu = @()
function U([hashtable]$h) { $script:tu += , $h }

U @{ tool_id='tu-01'; tool='共享 DSL 组件库 lib-b02.ps1'; category='生成程序'
    purpose='dot-source lib-b01 复用 Fit/TW/TLines/Seg/Box/Rotate 等基础设施，并登记本题真实用到的设计系统组件 Mark/Eyebrow/RuleBand/StatChip/SpeciesRow/NumChip/FooterLine/Chip/DialArc/SectionTitle'
    input='tmp/run-20261002-220723-mimo/B01/lib-b01.ps1 与 outputs/.../B02/design-system.json'
    output='tmp/run-20261002-220723-mimo/B02/lib-b02.ps1'
    affected_cases=@('case-01','case-02','case-03','case-04','case-05','case-06','case-07','case-08','case-09','case-10')
    http_request_ids=@(); double_counted=$false
    note='共享准备，不归属任何单一用例；输出根被重指到 outputs/run-20261002-220723-mimo/B02' }

U @{ tool_id='tu-02'; tool='生成程序 gen-b02-a.ps1'; category='生成程序'
    purpose='生成 case-01…case-05 的完整自包含 DSL 并写出 final.snapshot，生成期用 Fit 做文本溢出校验'
    input='lib-b02.ps1'; output=@('outputs/run-20261002-220723-mimo/B02/case-01/final.snapshot','outputs/run-20261002-220723-mimo/B02/case-02/final.snapshot','outputs/run-20261002-220723-mimo/B02/case-03/final.snapshot','outputs/run-20261002-220723-mimo/B02/case-04/final.snapshot','outputs/run-20261002-220723-mimo/B02/case-05/final.snapshot')
    affected_cases=@('case-01','case-02','case-03','case-04','case-05')
    http_request_ids=@(); double_counted=$false; note='最终一次运行 problems = 0' }

U @{ tool_id='tu-03'; tool='生成程序 gen-b02-b.ps1'; category='生成程序'
    purpose='生成 case-06…case-10 的完整自包含 DSL 并写出 final.snapshot'
    input='lib-b02.ps1'; output=@('outputs/run-20261002-220723-mimo/B02/case-06/final.snapshot','outputs/run-20261002-220723-mimo/B02/case-07/final.snapshot','outputs/run-20261002-220723-mimo/B02/case-08/final.snapshot','outputs/run-20261002-220723-mimo/B02/case-09/final.snapshot','outputs/run-20261002-220723-mimo/B02/case-10/final.snapshot')
    affected_cases=@('case-06','case-07','case-08','case-09','case-10')
    http_request_ids=@(); double_counted=$false; note='最终一次运行 problems = 0' }

U @{ tool_id='tu-04'; tool='补丁脚本 patch-bold.ps1'; category='代码修复'
    purpose='把生成库中所有小写 fontStyle="bold" 批量替换为大写 BOLD（解析器只接受枚举大写）'
    input='tmp/run-20261002-220723-mimo/B02/lib-b02.ps1 与 gen 脚本'
    output=@('tmp/run-20261002-220723-mimo/B02/patch-bold.ps1')
    affected_cases=@('case-01','case-03','case-04','case-05')
    http_request_ids=@('B02-c01-r1','B02-c03-r1','B02-c04-r1','B02-c05-r1'); double_counted=$false
    note='对应 requests.jsonl 中 4 条 400；HTTP 事件已在 requests 计入，此处不重复累计' }

U @{ tool_id='tu-05'; tool='像素量测 measure-arc.ps1 / measure-ring.ps1 / show-ring.ps1'; category='图像量测'
    purpose='用 System.Drawing 沿圆周逐角度采样，量化 SWEEP 渐变环与 DialArc 分段环的亮/暗弧起止角，验证进度比例是否与声明一致'
    input=@('outputs/run-20261002-220723-mimo/B02/case-01/final.png','outputs/run-20261002-220723-mimo/B01/case-08/final.png')
    output=@('tmp/run-20261002-220723-mimo/B02/measure-arc.ps1','tmp/run-20261002-220723-mimo/B02/measure-ring.ps1','tmp/run-20261002-220723-mimo/B02/show-ring.ps1')
    affected_cases=@('case-01','case-09'); http_request_ids=@(); double_counted=$false
    note='量测结论直接导致 case-01 用 DialArc 替换 SWEEP 渐变（见 ite-B02-c01/v4）' }

U @{ tool_id='tu-06'; tool='局部放大 zoom.ps1'; category='图像观察'
    purpose='按矩形区域裁出 2x 放大图，核对小字号与细节'
    input='各 case 的 final.png'; output='tmp/run-20261002-220723-mimo/B02/zoom.ps1'
    affected_cases=@('case-03','case-06'); http_request_ids=@(); double_counted=$false; note=$null }

U @{ tool_id='tu-07'; tool='自标注校验副本 mkjpegs.ps1 / mkjpegs-b.ps1'; category='图像观察'
    purpose='把每张 final.png 顶部加 64px 标签条（写明 case 编号/名称/尺寸）后转 JPEG，使送入读图工具的图自带身份，规避读图工具返回错位字节导致的张冠李戴'
    input=@('outputs/run-20261002-220723-mimo/B02/case-01/final.png','outputs/run-20261002-220723-mimo/B02/case-10/final.png')
    output=@('tmp/run-20261002-220723-mimo/B02/view/chk*.jpg')
    affected_cases=@('case-01','case-02','case-03','case-04','case-05','case-06','case-07','case-08','case-09','case-10')
    http_request_ids=@(); double_counted=$false
    note='仅用于看图，未参与任何合成；最终 final.png 仍是服务原始响应字节' }

U @{ tool_id='tu-08'; tool='读图工具 read（看图）'; category='看图'
    purpose='逐件打开最终图与迭代图，做视觉判断'
    input=@('outputs/run-20261002-220723-mimo/B02/case-01..case-10/final.png','tmp/run-20261002-220723-mimo/B02/view/*.png','tmp/run-20261002-220723-mimo/B02/view/*.jpg')
    output='iterations.jsonl 中的 view_evidence 字段'
    affected_cases=@('case-01','case-02','case-03','case-04','case-05','case-06','case-07','case-08','case-09','case-10')
    http_request_ids=@(); double_counted=$false
    note='browser.preview 全程不可用（No desktop browser connected）；已读路径会返回旧字节，故一律用唯一时间戳文件名 + 自标注标签条' }

U @{ tool_id='tu-09'; tool='System.Drawing 尺寸与像素复核'; category='像素/对比度检查'
    purpose='读 PNG IHDR 实际尺寸核对画幅；在 x=400 采样表格行分隔线位置与颜色，确认淡线确实渲染出来'
    input=@('outputs/run-20261002-220723-mimo/B02/case-06/final.png', 'outputs/run-20261002-220723-mimo/B02/case-07..case-10/final.png')
    output='命令输出（10 件尺寸 830x1170 / 1040x660 / 1748x760 / 1080x1080 / 1080x1526 等，全部与设计一致；case-06 分隔线 y=555,593,631,669,707,745,783,821,859 色值 (175,187,180)）'
    affected_cases=@('case-01','case-02','case-03','case-04','case-05','case-06','case-07','case-08','case-09','case-10')
    http_request_ids=@(); double_counted=$false; note='像素检查只作辅助证据，不替代视觉判断' }

U @{ tool_id='tu-10'; tool='B01 已缓存的 snapshot 文档'; category='文档检索'
    purpose='复用本 run 内已真实取得的 AI 使用指南与 parser-tags 参考，核对 fontStyle / gradientBegin / BoxAlignment / Positioned 约束'
    input=@('tmp/run-20261002-220723-mimo/B01/doc-ai-guide.md','tmp/run-20261002-220723-mimo/B01/doc-parser-tags.txt')
    output='无新文件（只读复用）'
    affected_cases=@('case-01','case-02','case-03','case-04','case-05','case-06','case-07','case-08','case-09','case-10')
    http_request_ids=@('B01-doc-001','B01-doc-002','B01-doc-003','B01-doc-004','B01-doc-005','B01-doc-006','B01-doc-007')
    double_counted=$false
    note='本题未发起新的文档 HTTP 请求；上述 ID 属于 B01 的共享准备，B02 的 document_requests 计 0，避免重复累计' }

$line2 = ($tu | ForEach-Object { J $_ }) -join "`n"
[System.IO.File]::WriteAllText((Join-Path $tmp 'tool-usage.jsonl'), $line2 + "`n", $enc)

"requests.jsonl rows : " + (Get-Content (Join-Path $tmp 'requests.jsonl')).Count
"iterations.jsonl rows: " + (Get-Content (Join-Path $tmp 'iterations.jsonl')).Count
"tool-usage rows     : " + (Get-Content (Join-Path $tmp 'tool-usage.jsonl')).Count
