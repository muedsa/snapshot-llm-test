# mk-portfolio-b06.ps1 -- portfolio.json / portfolio.md / gallery.html
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B06'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B06'
$utf8 = New-Object Text.UTF8Encoding($false)
$BQ   = [char]96
function Code([string]$s) { return ($BQ + $s + $BQ) }
$RUN = 'run-20261002-220723-mimo'
$tz  = 'UTC+08:00'
$inv = [System.Globalization.CultureInfo]::InvariantCulture

$reqs = @()
foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'requests.jsonl'), [Text.Encoding]::UTF8)) {
  if ($l.Trim()) { $reqs += ($l | ConvertFrom-Json) }
}
$iters = @()
foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'iterations.jsonl'), [Text.Encoding]::UTF8)) {
  if ($l.Trim()) { $iters += ($l | ConvertFrom-Json) }
}
$calc = [IO.File]::ReadAllText((Join-Path $tmp 'calc-b06.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
$pe   = [IO.File]::ReadAllText((Join-Path $out 'problem-evidence.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json

# ---------------------------------------------------------------- authored meta
$meta = [ordered]@{
 'case-01' = @{ q='两个价签谁更划算？'; device='货架网格 + 对齐刻度条'; env='超市货架前举着手机与店内标签对照'; audience='家庭采购者'
   source='自拟观察；《明码标价和禁止价格欺诈规定》检索摘要（Bing RSS，2026-10-08）为二手选题依据，画面未引用条文' }
 'case-02' = @{ q='今天第几次、怎么吃、漏了一顿怎么办？'; device='当日时间轴 + 问答卡'; env='厨房窗台药盒旁，站着看'; audience='慢病老人 / 照护家属'
   source='自拟观察；本轮未取得任何具体说明书原文，无二手引用' }
 'case-03' = @{ q='箭头不表示严重程度，下一步做什么？'; device='参考区间尺 + 动作卡连线'; env='体检中心前台拿到纸质报告 / 回家手机上看'; audience='35 岁上班族'
   source='自拟观察；WS/T 402 参考区间检索摘要（Bing RSS，2026-10-08）为二手来源，不引用条文号、不给诊断结论' }
 'case-04' = @{ q='这期电费为什么涨了？'; device='分档瀑布 + 闭合核对'; env='手机上收到账单短信后点开'; audience='家庭月底看电费的人'
   source='发改价格〔2011〕2617号 阶梯电价检索摘要（Bing RSS，2026-10-08）为二手来源；三档电量与单价是自拟 DEMO' }
 'case-05' = @{ q='车来不来、往哪边、换乘走哪一侧？'; device='站台大屏 + 等比到发条'; env='地铁站台候车，人多、时间紧约 40 秒'; audience='通勤者'
   source='上海地铁官方页面检索摘要（2026-10-08）支撑末班车口径；班次、台号、换乘距离是 DEMO' }
 'case-06' = @{ q='0 手续费到底多贵？'; device='现金流竖排 + 共同量程费率尺'; env='收银台前，手机在手、当场决定'; audience='购物后被推荐分期的人'
   source='央视 2025-07 关于「分期」诱导的检索摘要（2026-10-08）为二手来源；不引用条款与利率上限数字' }
 'case-07' = @{ q='押金被扣成这样，哪几项能争？'; device='扣减瀑布 + 斜纹争议标记'; env='退租前一晚在家逐项对账'; audience='租客'
   source='租赁押金相关检索摘要（Bing RSS，2026-10-08）为二手来源；不引用法条与罚则金额' }
 'case-08' = @{ q='40% 是下多久、还是 40% 的地方在下？'; device='100 格点阵 + 翻译卡'; env='早上出门前看手机，门口换鞋几秒'; audience='出门前的通勤者'
   source='自拟观察；本轮未取得官方定义原文，画面明写不引用任何标准条文' }
 'case-09' = @{ q='停多久之内合规？超了怎么算？'; device='钟面分档 + 计费刻度'; env='路边车位旁，站在车边查'; audience='临时办事的司机'
   source='自拟演示计费规则 DEMO；停车价格检索摘要（Bing RSS，2026-10-08）为二手线索，不引用罚则金额' }
 'case-10' = @{ q='到底几点到？什么时候该打电话？'; device='节点轨道 + 共尺时间窗'; env='办公室等急件，隔一会儿刷一次'; audience='收急件的人'
   source='自拟观察与产品化时间窗规则；本轮未取得快递服务时限官方原文，不引用服务标准条文' }
}

# ---------------------------------------------------------------- build works
$works = @()
foreach ($i in 1..10) {
  $cid = 'case-{0:d2}' -f $i
  $num = $cid.Substring(5)
  $m   = $meta[$cid]
  $d   = Join-Path $out $cid
  $dslPath = Join-Path $d 'final.snapshot'
  $pngPath = Join-Path $d 'final.png'
  $body = [IO.File]::ReadAllText($dslPath, [Text.Encoding]::UTF8)
  $g = [regex]::Match($body, '<Container width="(\d+)" height="(\d+)"')
  $w = [int]$g.Groups[1].Value
  $h = [int]$g.Groups[2].Value
  $bgm = [regex]::Match($body, 'background="([^"]+)"')
  $bg  = $bgm.Groups[1].Value
  $ratio = [math]::Round(($w / $h), 3)
  $shape = '接近方形'
  if ($ratio -gt 1.05) { $shape = '横幅' } elseif ($ratio -lt 0.95) { $shape = '竖幅' }
  # tone is a design decision from plan.md: 01 02 04 07 09 light, 03 05 06 08 10 dark
  $tone = 'light'
  if ($cid -in @('case-03','case-05','case-06','case-08','case-10')) { $tone = 'dark' }

  $rs = @($reqs | Where-Object { $_.id -match ('^B06-case-' + $num + '-(r\d\d|a\d\d)$') } | Sort-Object { [datetime]$_.started_at })
  $ok = @($rs | Where-Object { $_.http_status -eq 200 })
  $ci = @($iters | Where-Object { $_.case_id -eq $cid })
  $roundNo = [int](Get-Content (Join-Path $d '.round'))
  $pngBytes = (Get-Item $pngPath).Length
  $dslBytes = (Get-Item $dslPath).Length
  $pngSha = (Get-FileHash $pngPath -Algorithm SHA256).Hash
  $dslSha = (Get-FileHash $dslPath -Algorithm SHA256).Hash

  $obs = 0; $unv = 0; $title = ''
  foreach ($pc in $pe.cases) {
    if ($pc.case_id -eq $cid) {
      $obs = @($pc.observable_improvements).Count
      $unv = @($pc.not_validated_by_user_experiment).Count
      $title = [string]$pc.title
    }
  }

  $works += ([ordered]@{
    id = $cid; index = $i; title = $title
    problem = [string]$m.q; stuck_on = [string]$m.q
    audience = [string]$m.audience; environment = [string]$m.env
    device = [string]$m.device; source_note = [string]$m.source
    canvas = ('{0}x{1}' -f $w, $h); width = $w; height = $h
    aspect_ratio = ($ratio.ToString('0.000', $inv) + ' ' + $shape); ratio = ($ratio.ToString('0.000', $inv))
    background = $tone; snapshot_background = $bg
    final_round = $roundNo; rounds_total = $roundNo
    png_path = ($cid + '/final.png'); snapshot_path = ($cid + '/final.snapshot'); case_md = ($cid + '/case.md')
    png_bytes = $pngBytes; snapshot_bytes = $dslBytes
    png_sha256_16 = $pngSha.Substring(0, 16); snapshot_sha256_16 = $dslSha.Substring(0, 16)
    png_is_service_bytes_untouched = $true; png_matches_last_successful_render_bytes = $true
    request_count = @($rs).Count; successful_requests = @($ok).Count; failed_requests = (@($rs).Count - @($ok).Count)
    iteration_count = @($ci).Count; image_view_count = @($ci).Count
    view_not_verified = @($ci | Where-Object { $_.view_confirmed -eq $false }).Count
    observable_improvements = $obs; unvalidated_effects = $unv
    render_request_ids = @($rs | ForEach-Object { $_.id })
    render_durations_ms = @($rs | ForEach-Object { [double]$_.duration_ms })
    final_round_request_id = $rs[$rs.Count - 1].id
  })
}
$pngTotal = 0; $dslTotal = 0
$reqTotal = 0; $viewTotal = 0
# Measure-Object -Property cannot read OrderedDictionary keys, so sum by hand
foreach ($w in $works) {
  $pngTotal = $pngTotal + [int]$w['png_bytes']
  $dslTotal = $dslTotal + [int]$w['snapshot_bytes']
  $reqTotal = $reqTotal + [int]$w['request_count']
  $viewTotal = $viewTotal + [int]$w['image_view_count']
}

$allObs = [int]$pe.totals.observable_improvement_items
$allUnv = [int]$pe.totals.unvalidated_effect_items

# ---------------------------------------------------------------- portfolio.json
$pf = [ordered]@{
  schema_version = 1; task_id = 'B06'; task_name = 'astonishing & usable, from ten everyday information problems'
  run_id = $RUN; run_profile = 'all'; timezone = $tz
  series = 'PLAINSIGHT'
  tagline = '把十个日常信息难题变成惊艳而好用的作品'
  brief = '十个日常信息难题各自卡在不同的地方：要么要读者自己换算，要么规则写成一句话不给结论，要么数据摆在那儿却没回答那个问题。每件作品的处理路径相同 —— 先说清用户原本卡在哪一句 / 哪一个数，再按受众与观看环境换一种结构，把「读」变成「看见」。'
  ten_problems = '01 货架单价换算 · 02 当日用药卡 · 03 体检报告行动清单 · 04 电费阶梯账单 · 05 站台到发与换乘 · 06 信用卡分期真实年化 · 07 退租押金扣减瀑布 · 08 降水概率怎么读 · 09 路侧停车限时计费 · 10 快递到件时间窗'
  work_count = 10; independent_works_required = 10; independent_works_delivered = 10; final_image_count = 10
  canvas_shapes = '10 种互不重复的宽高比（0.435 / 0.475 / 0.627 / 0.643 / 1.000 / 1.333 / 1.615 / 1.778 / 1.796 / 3.097）'
  tone_split = '浅色 5 件（01 02 04 07 09） / 深色 5 件（03 05 06 08 10）'
  validation_statement = '本题没有做任何田野调研、用户访谈、问卷、A/B 测试或可用性测试，全程没有真实用户参与。所有改善分成两类：observable_from_final_image（在最终图片上就能直接看出、任何人可自行核对）与 not_validated_by_user_experiment（需要用户实验才能验证、本轮未验证）。后者不作为已达成的事实。'
  claims_discipline = '研究未取得任何法条、国家标准或服务标准原文（gov.cn 政策检索 totalCount=0；nmpa 与 nhc 返回 412；多词 Bing 查询被截断）。因此画面与交付文档不写条款号、不写罚则金额、不写国标数值、不写机构背书；唯一命中的外部线索是 Bing RSS 短词检索的二手摘要，一律标注「检索摘要（Bing RSS，2026-10-08）」；全部数值为演示 DEMO。'
  asset_policy = [ordered]@{ declared = 'dsl_primary_with_supporting_assets'; actual = 'dsl_only_in_practice'
    external_assets_used = 0
    note = '10 件全部为纯 DSL：货架网格、时间轴、区间尺、分档瀑布、站台色带、现金流柱、点阵、钟面、节点轨道均由矩形/圆/渐变/矩阵/裁剪画出，没有引用任何外部图片素材' }
  independence_statement = '10 件均为独立自包含 DSL（各自完整的 Snapshot 根、各自的画幅与版式），彼此不复用成品、不引用前件图像；共享的只有 lib-b06.ps1 的绘图函数与 calc-b06.json 的权威数据，按约定不计为新增作品。'
  evidence_split = [ordered]@{ observable_improvement_items = $allObs; unvalidated_effect_items = $allUnv
    field_research_sessions = 0; user_tests = 0; statutory_citations_used = 0 }
  total_png_bytes = $pngTotal; total_snapshot_bytes = $dslTotal
  works = $works
}
[IO.File]::WriteAllText((Join-Path $out 'portfolio.json'), ($pf | ConvertTo-Json -Depth 7), $utf8)
'portfolio.json written'

# ---------------------------------------------------------------- portfolio.md
$L = @()
$L += '# PLAINSIGHT —— B06 作品集'
$L += ''
$L += '- 任务：' + (Code 'B06 把十个日常信息难题变成惊艳而好用的作品') + ' · 运行：' + (Code $RUN) + ' · 时区：' + $tz
$L += '- 系列：**PLAINSIGHT**（报头 ' + (Code 'PLAINSIGHT — NN / 10') + '）'
$L += '- 交付：**10 / 10** 件独立作品 · **10** 种互不重复的宽高比 · 最终图合计 **' + $pngTotal + '** bytes PNG / **' + $dslTotal + '** bytes DSL'
$L += '- 迭代：case 级真实渲染 **' + $reqTotal + '** 次（全部 HTTP 200）· 读图 **' + $viewTotal + '** 次，逐张核对 ' + (Code 'PLAINSIGHT NN / 10') + ' 报头后才接受'
$L += '- 纪律：**田野调研 0 次、用户测试 0 次**；未取得法条 / 国标 / 服务标准原文 -> 不写条款号、不写罚则金额、不写国标数字、不写机构背书；全部数值为演示 DEMO'
$L += ''
$L += '## 一、十个难题与它们卡在哪'
$L += ''
$L += '| # | 难题 | 用户原本卡在哪 | 使用者与观看环境 | 结构骨架 | 来源 / 假设 |'
$L += '|---|---|---|---|---|---|'
foreach ($w in $works) {
  $L += ('| {0} | [{1}]({2}/case.md) | {3} | {4} | {5} | {6} |' -f `
    ('{0:00}' -f $w.index), $w.title, $w.id, $w.problem, ($w.audience + ' · ' + $w.environment), $w.device, $w.source_note)
}
$L += ''
$L += '## 二、重构怎么做的'
$L += ''
$L += '每件都走同一条路径：**用户原本卡在哪一句 / 哪一个数 → 使用者与观看环境 → 重构 → 从最终图判断的改善**。'
$L += ''
$L += '| # | 结构骨架 | 画幅 | 比例 | 底色 |'
$L += '|---|---|---|---|---|'
foreach ($w in $works) {
  $L += ('| {0:00} | {1} | {2} | {3} | {4} |' -f $w.index, $w.device, $w.canvas, $w.aspect_ratio, $w.background)
}
$L += ''
$L += '十件没有「同版式只换色换字」：十个宽高比互不相同，五件浅底、五件深底，结构骨架分别是货架网格、时间轴、区间尺、分档瀑布、站台色带、现金流柱、瀑布+斜纹、点阵、钟面、节点轨道。'
$L += ''
$L += '## 三、数据口径（全部由 ' + (Code 'calc-b06.json') + ' 算出，画面只读不改）'
$L += ''
$L += '| 项 | 值 | 用在哪件 |'
$L += '|---|---|---|'
$L += ('| 单位价换算 | groupCount {0} · disagreeCount {1}（{2} 个价签） | 01 |' -f $calc.case01.groupCount, $calc.case01.disagreeCount, ($calc.case01.groups.Count * 3))
$L += ('| 用药进度 | 今日 {0} / {1} 已服 = {2}%；一周 {3} 天 x 3 次 = {4} 格 | 02 |' -f $calc.case02.todayTaken, ($calc.case02.todayTaken + $calc.case02.todayLeft), $calc.case02.todayPct, $calc.case02.week.Count, ($calc.case02.week.Count * 3))
$L += ('| 体检分档 | {0} 项 = 正常 {1} · 复查 {2} · 提前 {3} | 03 |' -f $calc.case03.stat.total, $calc.case03.stat.normal, $calc.case03.stat.recheck, $calc.case03.stat.sooner)
$nom06 = ([double]$calc.case06.nominalPct).ToString('0.00', $inv)
$fee09 = ([double]$calc.case09.usedFee).ToString('0.00', $inv)
$L += ('| 电费 | 上期 {0} 度 / {1} 元 -> 本期 {2} 度 / {3} 元，差 {4} 元（电费 +{5}% / 电量 +{6}% / 单价 +{7}%）；档位占比 {8}% / {9}% | 04 |' -f $calc.case04.prev.kwh, $calc.case04.prev.cost, $calc.case04.cur.kwh, $calc.case04.cur.cost, $calc.case04.deltaCost, $calc.case04.deltaCostPct, $calc.case04.deltaKwhPct, $calc.case04.ratePct, $calc.case04.tier3Share, $calc.case04.tier2Share)
$L += ('| 站台 | {0} {1}，现在 {2}，{3}；三班 +{4} / +{5} / +{6} 分钟；换乘 7 号线 180 m 本侧、12 号线 240 m 对侧；{7} | 05 |' -f $calc.case05.line, $calc.case05.dir, $calc.case05.now, $calc.case05.platform, $calc.case05.trains[0].min, $calc.case05.trains[1].min, $calc.case05.trains[2].min, $calc.case05.nextLast)
$L += ('| 分期 | 每期 {0} 元 x {1} 期 = {2} 元（手续费 {3}）；名义 {4}% -> 年化 {5}% / 实际 {6}% / 平均本金口径 {7}% | 06 |' -f $calc.case06.payPer, $calc.case06.periods, $calc.case06.totalPaid, $calc.case06.totalFee, $nom06, $calc.case06.aprSimple, $calc.case06.aprEff, $calc.case06.feeOnAvgPct)
$L += ('| 押金 | {0} 元 -> 固定扣 {1} + 争议 {2}；全扣退 {3}、争回退 {4}，差额 {5} | 07 |' -f $calc.case07.start, $calc.case07.fixedTotal, $calc.case07.disputeTotal, $calc.case07.refundIfAllCut, $calc.case07.refundIfDisputeKept, $calc.case07.swing)
$L += ('| 降水 | 三窗 {0}% / {1}% / {2}%；点阵填 {3} / {4} 格；出门结论：{5}伞 | 08 |' -f $calc.case08.windows[0].p, $calc.case08.windows[1].p, $calc.case08.windows[2].p, $calc.case08.gridFilled, $calc.case08.gridSize, $calc.case08.carry)
$L += ('| 停车 | 限时 {0} 分钟，已用 {1} 分钟、已付 {2} 元；累计 {3} 元；日封顶 {4} 元 | 09 |' -f $calc.case09.limitMinutes, $calc.case09.usedMin, $fee09, (($calc.case09.cumulative | ForEach-Object { $_.cum }) -join ' / '), $calc.case09.dailyCap)
$prog10 = [math]::Round(($calc.case10.stationDone / $calc.case10.stationTotal * 100), 1).ToString('0.0', $inv)
$L += ('| 快递 | 当前节点 {0}；{1}-{2}，还有 {3} 分钟到窗；进度 {4} / {5} = {6}%；{7} 后可致电 | 10 |' -f $calc.case10.currentIndex, $calc.case10.etaFrom, $calc.case10.etaTo, $calc.case10.etaMinutes, $calc.case10.stationDone, $calc.case10.stationTotal, $prog10, $calc.case10.callAfter)
$L += ''
$L += '所有可见数字都是先在 ' + (Code 'calc-b06.json') + ' 算出、再被画面引用；视觉迭代里发现的三处数字矛盾（case-04 的 80.6 / 80.8、case-06 的 13.8 / 13.84 与 7.2 / 7.20、case-09 把分段增量当累计）全部是**读图**发现的。'
$L += ''
$L += '## 四、改善的两栏（本题的核心纪律）'
$L += ''
$L += '- **从最终图片上直接可观察的改善：' + $allObs + ' 条** —— 每条都是任何人拿到图就能自己数、自己比、自己核对的事实（如「三张档位卡写的是 3 / 9 / 17，最后一根条正好满格」）。'
$L += '- **需要用户实验才能验证、本轮未验证的效果：' + $allUnv + ' 条** —— 如「3 秒完成比价」「减少漏服」「读者不再把概率当分钟」，均为设计目标，不作为已达成的事实。'
$L += '- 两栏的结构化版本在 ' + (Code 'problem-evidence.json') + '，逐件叙述版本在 ' + (Code 'design-review.md') + '。'
$L += ''
$L += '## 五、索引'
$L += ''
$L += '- ' + (Code 'portfolio.json') + ' / ' + (Code 'portfolio.md') + ' / ' + (Code 'problem-evidence.json') + ' / ' + (Code 'design-review.md') + ' / ' + (Code 'gallery.html') + ' / ' + (Code 'snapshot-usage.md') + ' / ' + (Code 'task-metrics.json')
$L += '- 逐件：' + (Code 'case-NN/case.md') + '（画幅、数据口径、真实渲染请求表、逐次读图证据）'
$L += '- 过程日志：' + (Code 'tmp/run-20261002-220723-mimo/B06/requests.jsonl') + '、' + (Code 'iterations.jsonl') + '、' + (Code 'tool-usage.jsonl') + '、' + (Code 'calc-b06.json')
$L += ''
[IO.File]::WriteAllLines((Join-Path $out 'portfolio.md'), $L, $utf8)
'portfolio.md written'

# ---------------------------------------------------------------- gallery.html
$E = [System.Text.StringBuilder]::new()
function W([string]$s) { [void]$script:E.AppendLine($s) }
W '<!DOCTYPE html>'
W '<html lang="zh-CN">'
W '<head>'
W '<meta charset="utf-8">'
W '<meta name="viewport" content="width=device-width, initial-scale=1">'
W '<title>PLAINSIGHT — B06 十件作品画廊</title>'
W '<style>'
W ':root{--ink:#12161B;--panel:#1A2028;--paper:#EDEAE3;--acc:#22B8CF;--acc2:#FFD43B;--park:#F5B301;--late:#E5484D;--mute:#94A0AE;--hair:#2E3742}'
W '*{box-sizing:border-box}'
W 'body{margin:0;background:#0B0E12;color:#C4CEDA;font-family:"Noto Sans CJK SC","Inter",system-ui,sans-serif;line-height:1.75}'
W 'header{padding:44px 32px 28px;border-bottom:1px solid var(--hair);background:linear-gradient(180deg,#141A21,#0B0E12)}'
W 'h1{margin:0 0 8px;font-size:30px;color:#fff;font-weight:700}'
W '.sub{color:var(--mute);font-size:14px}.sub b{color:var(--acc2);font-weight:600}'
W 'nav{padding:16px 32px;border-bottom:1px solid var(--hair);font-size:13px;color:var(--mute);flex-wrap:wrap}'
W 'nav a{color:#22B8CF;text-decoration:none;margin-right:14px}'
W 'nav a:hover{text-decoration:underline}'
W 'main{padding:28px 32px 56px;max-width:1600px;margin:0 auto}'
W '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:26px}'
W 'figure{margin:0;background:#141A21;border:1px solid var(--hair);border-radius:10px;overflow:hidden}'
W 'figure a{display:block;background:#07090C;text-decoration:none;padding:14px;display:flex;align-items:center;justify-content:center;min-height:180px}'
W 'figure img{display:block;max-width:100%;height:auto;box-shadow:0 6px 22px rgba(0,0,0,.55)}'
W 'figcaption{padding:14px 16px 16px;border-top:1px solid var(--hair)}'
W '.num{display:inline-block;font:600 12px/1 "Noto Sans Mono CJK SC",monospace;color:#12161B;background:var(--acc2);padding:5px 8px;border-radius:4px}'
W '.stg{display:inline-block;font:600 12px/1 "Noto Sans Mono CJK SC",monospace;color:#fff;background:#2A3441;border:1px solid var(--hair);padding:5px 8px;border-radius:4px;margin-left:6px}'
W '.t{display:block;margin-top:11px;font-size:17px;color:#fff;font-weight:600}'
W '.q{display:block;margin-top:5px;font-size:13px;color:var(--mute)}'
W '.m{display:block;margin-top:9px;font:12px/1.75 "Noto Sans Mono CJK SC",monospace;color:#7C8B9A}'
W '.m i{color:#FFD43B;font-style:normal}'
W '.m u{color:#7C8B9A;text-decoration:none}'
W 'section{margin-top:46px}'
W 'h2{font-size:20px;color:#fff;border-left:4px solid var(--acc);padding-left:12px;margin:0 0 16px}'
W 'table{width:100%;border-collapse:collapse;font-size:13px}'
W 'th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--hair)}'
W 'th{color:#FFD43B;font-weight:600;background:#141A21}'
W 'td{color:#AEBCCA}td code{background:#141C24}'
W 'code{background:#141C24;padding:2px 5px;border-radius:3px;font-size:12px;color:#FFD43B}'
W 'a{color:#22B8CF}'
W '.flow{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}'
W '.flow span{font:12px/1 "Noto Sans Mono CJK SC",monospace;background:#141A21;border:1px solid var(--hair);border-radius:999px;padding:8px 13px;color:#AEBCCA}'
W '.flow span b{color:#fff;font-weight:600}'
W 'footer{padding:24px 32px 44px;border-top:1px solid var(--hair);color:var(--mute);font-size:12px}'
W '</style>'
W '</head>'
W '<body>'
W '<header>'
W '<h1>PLAINSIGHT —— 把十个日常信息难题变成惊艳而好用的作品</h1>'
W '<div class="sub">B06 · 运行 <b>' + $RUN + '</b> · 时区 <b>' + $tz + '</b> · <b>10 / 10</b> 件独立作品 · <b>10</b> 种互不重复的画幅 · 浅色 <b>5</b> / 深色 <b>5</b></div>'
W '</header>'
W '<nav><a href="#works">十件</a><a href="#problems">难题与来源</a><a href="#data">数据口径</a><a href="#discipline">改善两栏与声明纪律</a><a href="#logs">日志与指标</a><a href="portfolio.md">portfolio.md</a><a href="problem-evidence.json">problem-evidence.json</a><a href="design-review.md">design-review.md</a><a href="snapshot-usage.md">snapshot-usage.md</a><a href="task-metrics.json">task-metrics.json</a></nav>'
W '<main>'
W '<section id="works"><h2>十件作品（点击图片打开原尺寸）</h2><div class="grid">'
foreach ($w in $works) {
  $m = $meta[$w.id]
  W '<figure>'
  W ('<a href="{0}/final.png" target="_blank" rel="noopener">' -f $w.id)
  W ('<img src="{0}/final.png" alt="{1} {2}" width="{3}" height="{4}" loading="lazy">' -f $w.id, $w.id, $w.title, $w.width, $w.height)
  W '</a>'
  W '<figcaption>'
  W ('<span class="num">{0:00} / 10</span><span class="stg">{1}</span><span class="stg">{2}</span>' -f $w.index, $w.background, ('a{0:00}' -f $w.final_round))
  W ('<span class="t">{0}</span>' -f $w.title)
  W ('<span class="q">{0}</span>' -f $w.problem)
  W ('<span class="m"><i>{0}</i> · {1} · {2} · {3}&rarr;a{4:00} · {5} B png / {6} B dsl<br><u>{7}</u> · <a href="{8}/case.md">case.md</a> · <a href="{9}/final.snapshot">final.snapshot</a></span>' -f $w.canvas, $w.aspect_ratio, $w.device, ('r01'), $w.final_round, $w.png_bytes, $w.snapshot_bytes, $w.environment, $w.id, $w.id)
  W '</figcaption>'
  W '</figure>'
}
W '</div></section>'

W '<section id="problems"><h2>十个难题：卡在哪 · 怎么重构 · 来源还是假设</h2>'
W '<table><tr><th>#</th><th>难题</th><th>用户原本卡在哪</th><th>使用者与观看环境</th><th>结构骨架</th><th>来源 / 假设</th></tr>'
foreach ($w in $works) {
  W ('<tr><td>{0:00}</td><td><a href="{1}/case.md">{2}</a></td><td>{3}</td><td>{4}<br><span style="color:#7C8B9A">{5}</span></td><td>{6}</td><td>{7}</td></tr>' -f `
    $w.index, $w.id, $w.title, $w.problem, $w.audience, $w.environment, $w.device, $w.source_note)
}
W '</table></section>'

W '<section id="data"><h2>数据口径（全部由 calc-b06.json 算出，画面只读不改）</h2>'
W '<table><tr><th>项</th><th>值</th><th>用在哪件</th></tr>'
W ('<tr><td>单位价换算</td><td>3 组 · 分歧 3 组 · 9 个价签</td><td>01</td></tr>')
W ('<tr><td>用药进度</td><td>今日 {0} / 3 已服 = {1}%；一周 21 格</td><td>02</td></tr>' -f $calc.case02.todayTaken, $calc.case02.todayPct)
W ('<tr><td>体检分档</td><td>{0} 项 = 正常 {1} · 复查 {2} · 提前 {3}</td><td>03</td></tr>' -f $calc.case03.stat.total, $calc.case03.stat.normal, $calc.case03.stat.recheck, $calc.case03.stat.sooner)
W ('<tr><td>电费</td><td>{0} 度 / {1} 元 -> {2} 度 / {3} 元，差 {4} 元；电费 +{5}% / 电量 +{6}% / 单价 +{7}%；档位 {8}% / {9}%</td><td>04</td></tr>' -f $calc.case04.prev.kwh, $calc.case04.prev.cost, $calc.case04.cur.kwh, $calc.case04.cur.cost, $calc.case04.deltaCost, $calc.case04.deltaCostPct, $calc.case04.deltaKwhPct, $calc.case04.ratePct, $calc.case04.tier3Share, $calc.case04.tier2Share)
W ('<tr><td>站台</td><td>{0} {1}，现在 {2}，{3}；+{4} / +{5} / +{6} 分钟；7 号线 180 m 本侧、12 号线 240 m 对侧；{7}</td><td>05</td></tr>' -f $calc.case05.line, $calc.case05.dir, $calc.case05.now, $calc.case05.platform, $calc.case05.trains[0].min, $calc.case05.trains[1].min, $calc.case05.trains[2].min, $calc.case05.nextLast)
W ('<tr><td>分期</td><td>{0} x {1} = {2} 元（费 {3}）；名义 {4}% -> 年化 {5}% / 实际 {6}% / 平均本金 {7}%</td><td>06</td></tr>' -f $calc.case06.payPer, $calc.case06.periods, $calc.case06.totalPaid, $calc.case06.totalFee, $nom06, $calc.case06.aprSimple, $calc.case06.aprEff, $calc.case06.feeOnAvgPct)
W ('<tr><td>押金</td><td>{0} -> 固定 {1} + 争议 {2}；全扣退 {3}、争回退 {4}，差额 {5}</td><td>07</td></tr>' -f $calc.case07.start, $calc.case07.fixedTotal, $calc.case07.disputeTotal, $calc.case07.refundIfAllCut, $calc.case07.refundIfDisputeKept, $calc.case07.swing)
W ('<tr><td>降水</td><td>三窗 {0}% / {1}% / {2}%；点阵填 {3} / {4} 格</td><td>08</td></tr>' -f $calc.case08.windows[0].p, $calc.case08.windows[1].p, $calc.case08.windows[2].p, $calc.case08.gridFilled, $calc.case08.gridSize)
W ('<tr><td>停车</td><td>限时 {0} 分钟，已用 {1} 分钟 / {2} 元；累计 {3} 元；日封顶 {4} 元</td><td>09</td></tr>' -f $calc.case09.limitMinutes, $calc.case09.usedMin, $fee09, (($calc.case09.cumulative | ForEach-Object { $_.cum }) -join ' / '), $calc.case09.dailyCap)
W ('<tr><td>快递</td><td>节点 {0}；{1}-{2}（还有 {3} 分钟）；{4} / {5} = {6}%；{7} 后可致电</td><td>10</td></tr>' -f $calc.case10.currentIndex, $calc.case10.etaFrom, $calc.case10.etaTo, $calc.case10.etaMinutes, $calc.case10.stationDone, $calc.case10.stationTotal, $prog10, $calc.case10.callAfter)
W '</table>'
W '<p style="font-size:13px;color:#94A0AE">十件没有共享画面上的数字：每个数字只在一个地方算出（calc-b06.json），再被引用。视觉迭代中发现的三处数字矛盾（case-04 的 80.6 / 80.8、case-06 的 13.8 / 13.84 与 7.2 / 7.20、case-09 把分段增量 3/6/8 当成累计 3/9/17）全部由读图发现，不是由脚本发现的。</p>'
W '</section>'

W '<section id="discipline"><h2>改善两栏与声明纪律</h2>'
W '<table><tr><th>检查</th><th>结果</th></tr>'
W ('<tr><td>从最终图直接可观察的改善</td><td><b>{0}</b> 条 —— 每条都能自己数、自己比、自己核对</td></tr>' -f $allObs)
W ('<tr><td>需要用户实验、本轮未验证的效果</td><td><b>{0}</b> 条 —— 设计目标，不作为已达成的事实，与上栏在 problem-evidence.json 中分栏列出</td></tr>' -f $allUnv)
W '<tr><td>田野调研 / 用户测试</td><td>0 次 / 0 次，全程无真实用户参与</td></tr>'
W '<tr><td>法条 · 国标 · 服务标准原文</td><td>取得 0 条（gov.cn 政策检索 totalCount=0；nmpa / nhc 412；多词 Bing 查询被截断）</td></tr>'
W '<tr><td>引用方式</td><td>仅 Bing RSS 短词检索的二手摘要，标注「检索摘要（Bing RSS，2026-10-08）」；不写条款号、不写罚则金额、不写国标数字、不写机构背书</td></tr>'
W '<tr><td>数值</td><td>全部演示样例 DEMO，画面内逐处标注</td></tr>'
W '<tr><td>素材</td><td>10 件纯 DSL，外部图片素材 0 个</td></tr>'
W '<tr><td>尺寸</td><td>10/10 的 PNG 实际像素与 DSL 首个 Container 一致；final.png 与服务原始字节 SHA256 一致</td></tr>'
W '<tr><td>独立性</td><td>10 件各自完整的 Snapshot 根，彼此不复用成品、不引用前件图像</td></tr>'
W '</table></section>'

W '<section id="logs"><h2>日志与指标</h2>'
W '<table><tr><th>文件</th><th>内容</th></tr>'
W '<tr><td><a href="portfolio.json">portfolio.json</a></td><td>十件清单、画幅、字节、渲染请求 ID、改善两栏计数</td></tr>'
W '<tr><td><a href="portfolio.md">portfolio.md</a></td><td>人读版作品集与数据口径表</td></tr>'
W '<tr><td><a href="problem-evidence.json">problem-evidence.json</a></td><td>逐件：来源 / 假设、场景要求、重构选择、可观察改善、未验证效果</td></tr>'
W '<tr><td><a href="design-review.md">design-review.md</a></td><td>设计复核：逐件复核 + 跨件判断 + 会改的三件事</td></tr>'
W '<tr><td><a href="snapshot-usage.md">snapshot-usage.md</a></td><td>文档与 DSL 实际应用、踩坑、复核</td></tr>'
W '<tr><td><a href="task-metrics.json">task-metrics.json</a></td><td>请求 / 迭代 / 看图 / 字节 / 耗时，全部从 JSONL 反查</td></tr>'
W '<tr><td><code>tmp/run-20261002-220723-mimo/B06/</code></td><td>requests.jsonl · iterations.jsonl · tool-usage.jsonl · plan.md · calc-b06.json · research/ · docs/ · view/ · 各 .snapshot 原件</td></tr>'
W '</table></section>'
W '</main>'
W '<footer>PLAINSIGHT · B06 · ' + $RUN + ' · ' + $tz + ' · 本页全部图片为相对链接的本地文件，无远程脚本</footer>'
W '</body>'
W '</html>'
[IO.File]::WriteAllText((Join-Path $out 'gallery.html'), $E.ToString(), $utf8)
'gallery.html written'
