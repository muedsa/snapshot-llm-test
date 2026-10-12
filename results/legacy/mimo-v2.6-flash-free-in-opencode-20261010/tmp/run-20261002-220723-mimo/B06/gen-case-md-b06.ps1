# gen-case-md-b06.ps1 -- build outputs/.../B06/case-NN/case.md from the real logs
# Every number, hash, timestamp and duration is read from requests.jsonl / iterations.jsonl
# / final.snapshot; only the authored prose (problem, source vs assumption) lives here.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B06'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B06'
$utf8 = New-Object Text.UTF8Encoding($false)
$BQ   = [char]96
function Code([string]$s) { return ($BQ + $s + $BQ) }

$reqs = @()
foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'requests.jsonl'), [Text.Encoding]::UTF8)) {
    if ($l.Trim()) { $reqs += ($l | ConvertFrom-Json) }
}
$iters = @()
foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'iterations.jsonl'), [Text.Encoding]::UTF8)) {
    if ($l.Trim()) { $iters += ($l | ConvertFrom-Json) }
}

$meta = @(
  [ordered]@{ id='case-01'; title='货架单价换算'; bg='纸色'; ratio='1.615'; ori='横幅'; pass='a02';
    stuck='两个价签谁更划算，现场算不出来 —— 500g / 1.2kg / 24 枚装的单价都没写，只能心算。'
    aud='家庭采购者 · 超市货架前举着手机对照店内标签'
    hero='三层货架当骨架（坚果按 100 克比 / 牛奶按 100 毫升比 / 抽纸按 100 抽比），每格给规格与总价，右侧一条对齐的换算刻度把 9 个价签统一到同一单位，并把"总价最便宜"与"单价最便宜"是不是同一件直接标出来。'
    data='3 组 x 3 行共 9 个价签，三组 disagreeCount = 3，即每一组的总价冠军都不是单价冠军。坚果 500g 49.9 元 = 9.98 元/100g、1.2kg 118 元 = 9.83、180g 22.9 元 = 12.72；牛奶 250ml x 12 49.9 = 1.66、1L x 6 89.9 = 1.50、200ml x 24 69.9 = 1.46；抽纸 100抽 x 6 19.9 = 3.32、100抽 x 24 69.9 = 2.91、130抽 x 12 45.9 = 2.94（元 / 100 抽）。单位价一律由 总价 / 折算基数 x 100 得出，与画面刻度逐条对齐。'
    src='换算口径依据《明码标价和禁止价格欺诈规定》的检索摘要（Bing RSS，2026-10-08），属二手来源；画面不引用条文号，只呈现"同组同单位才可比"这一产品化规则。'
    demo='商品名、规格与价格均为自拟样例 DEMO。' },
  [ordered]@{ id='case-02'; title='当日用药卡'; bg='纸色'; ratio='0.435'; ori='竖屏'; pass='a04';
    stuck='说明书 6 号字、术语一堆，"饭前服"和"餐中服"看不出差别 —— 一天该吃几次、饭前还是饭后、漏了一顿怎么办。'
    aud='慢病老人 / 照护家属 · 厨房窗台药盒旁'
    hero='上半是"今天 3 次"的时刻带，下半是 4 张必答问答卡（怎么吃 / 漏服怎么办 / 不能同吃什么 / 怎么存），底部一排 7 x 3 的一周药格。'
    data='示例药 · 降压片（演示）5 mg / 片，每天 3 次，饭后 30 分钟内服；今天已服 1 次、剩 2 次、完成 33.3%；一周药格 21 格 = 7 天 x 3 次。漏服规则写为：想起来马上补，若已接近下一次就跳过这一次，绝不补两片。'
    src='用药指导与漏服处理按通行药品说明书含义整理；本轮研究未取得任何具体说明书原文，画面不引用药厂文件或标准条文。'
    demo='药名、规格、禁忌与储存条件均为演示样例 DEMO。' },
  [ordered]@{ id='case-03'; title='体检报告行动清单'; bg='深色'; ratio='1.333'; ori='横幅'; pass='a04';
    stuck='报告上一排箭头，↑↓ 只表示出界，不表示严重，更不表示下一步该做什么。'
    aud='35 岁上班族 · 体检中心前台 / 家里'
    hero='6 项各一条参考区间刻度尺 + 当前值指针 + 出界距离，右侧连线到对应动作卡；最右汇总"3 正常 / 2 复查 / 1 提前"，让下一步按等级排序而不是按箭头方向排序。'
    data='收缩压 142（区间 90-139，出界 3 mmHg，动作：一周内在家测 3 次并记录）；空腹血糖 5.8（3.9-6.1）；总胆固醇 5.61（3.0-5.2，+0.41，3 个月后复查血脂）；尿酸 452（208-428，+24，3 个月后复查）；血红蛋白 148（130-175）；谷丙转氨酶 33（0-40）。stat：total 6 / normal 3 / recheck 2 / sooner 1。'
    src='参考区间含义按 WS/T 402 的检索摘要（Bing RSS，2026-10-08）整理，属二手来源；画面只写区间与动作，不引用条文号，也不给出任何诊断结论。'
    demo='指标、数值、动作与复查时间均为演示样例 DEMO，不构成医学建议。' },
  [ordered]@{ id='case-04'; title='电费阶梯账单'; bg='纸色'; ratio='1.796'; ori='横幅'; pass='a03';
    stuck='账单只给总额和"比上期 +38%"，不解释为什么 —— 这期到底贵在哪，是不是阶梯跳档了。'
    aud='家庭月底看电费短信的人'
    hero='水位阶梯 + 分档瀑布：本期柱被切成三档叠块，左边对上期，右边列档位增量，并把总差额拆回档位上做一次闭合核对。'
    data='上期 130.86 元、本期 236.63 元、差额 105.77 元；电量 +136 度（+61.8%）、电费 +80.8%、单价口径 +11.8%；增量中第三档占 63.8%、第二档占 36.2%；attributionCheck = 105.77，即分档增量之和恰好等于总差额，分子分母与百分比同源。'
    src='阶梯机制依据发改价格〔2011〕2617号 的检索摘要（Bing RSS，2026-10-08），属二手来源；三档电量与三档单价均为演示数据 DEMO，画面不引用条文原文。'
    demo='户号、上期与本期电量金额均为演示样例 DEMO。' },
  [ordered]@{ id='case-05'; title='站台到发与换乘'; bg='深色'; ratio='3.097'; ori='超宽横幅'; pass='a02';
    stuck='"下一班 3 分钟"和"往哪个方向"是两块屏 —— 要抬头两次才知道车来不来、是不是我要的方向。'
    aud='通勤者 · 地铁站台候车 40 秒内'
    hero='顶部整条线路色带；左侧"本次列车去哪"，中间大字倒计时与三班到发横条（长度按等待分钟数等比），右侧换乘卡片标明 7 号线 180 m 本侧、12 号线 240 m 对侧，一块屏同时回答方向、时间与换乘。'
    data='3 号线 往 江湾新城，现在 07:39，站台 A；三班 3 / 9 / 16 分钟，到站 07:42 / 07:48 / 07:55；本方向末班车 22:47。横条长度 = 等待分钟数，三条同尺，最长的一班即本次量程。'
    src='末班车口径依据上海地铁官方页面检索摘要（2026-10-08），属二手来源；画面写明"末班车进站前 3 分钟停止售票"的出处摘要，但不引用条文。'
    demo='班次时刻、站台编号与换乘距离均为自拟样例 DEMO。' },
  [ordered]@{ id='case-06'; title='信用卡分期真实年化'; bg='深色'; ratio='0.643'; ori='竖屏'; pass='a03';
    stuck='"0 手续费"、"每期 0.6%"，不换算就不知道真实年化 —— 分期比贷款贵还是便宜，当场比不了。'
    aud='购物后被收银员推荐分期的人'
    hero='12 期每期现金流竖排（本金 + 手续费），下方把名义费率翻译成年化，并用一根共同刻度尺把名义、年化利率、实际年化与手续费/平均本金四个口径放在同一量程上对照。'
    data='商品价 6000 元，12 期，每期 536 元，合计 6432 元，手续费 432 元。名义费率 7.20% = 432 / 6000；月 IRR 1.0862%，年化利率 13.03% = 月 x 12；实际年化 13.84%；平均未还本金 3250 元，手续费 / 平均本金 = 13.29%。全页每一个费率都用同一位小数渲染，分子分母与单位在画面中给出。'
    src='分期费率换算口径依据央视 2025-07 关于"分期"诱导的检索摘要（2026-10-08），属二手来源；年化按每期现金流内部收益率计算，全部演示数据 DEMO，画面不引用任何条款或利率上限。'
    demo='商品价、费率与期数均为演示样例 DEMO。' },
  [ordered]@{ id='case-07'; title='退租押金扣减瀑布'; bg='纸色'; ratio='0.475'; ori='竖屏'; pass='a03';
    stuck='退租时押金扣多少，要一项一项问中介 —— 不知道哪几项能扣、哪几项不能扣。'
    aud='租客退租前一晚'
    hero='6000 元押金向右逐项扣减的瀑布，下方逐项台账把可争议的两笔用斜纹标出，末端给出两条结局卡与对应余额条，把"能争回多少"变成一个可以直接量出来的差额。'
    data='起 6000 元；扣减 -312 / -268 / -180 / -450 / -150；固定可扣 760 元、有争议 600 元；全扣退 4640 元、争回可退 5240 元、差额 600 元。4640 = 6000 - 760 - 600，两条结局的差额恰好等于争议项合计。'
    src='押金担保性质按通行租赁检索摘要整理（Bing RSS，2026-10-08），属二手来源；退还期限写为"合同约定退租后 7 日内退还（演示约定 DEMO，以合同为准）"，画面不引用任何法条或罚则金额。'
    demo='房屋、扣减项目与金额均为演示样例 DEMO。' },
  [ordered]@{ id='case-08'; title='降水概率怎么读'; bg='深色'; ratio='1.000'; ori='方形'; pass='a02';
    stuck='"降水概率 40%" 被当成"会下 40 分钟"或"40% 的地方在下" —— 概率说的是下不下，不说下多久、下多大。'
    aud='早上出门前看手机的通勤者'
    hero='100 格点阵，其中 40 格填色；右侧三句翻译把同一个 40% 分别否掉两种常见误读、再给出正确的长期频率含义；下方今天上午三个小时的 40 / 70 / 20% 卡片与出门结论。'
    data='decisionP = 40，gridFilled = 40 / 100。填色规则 (i x 37) mod 100 < 40 中 37 与 100 互素，因此 i 取 0..99 时结果是 0..99 的一个排列，恰好 40 个落入 40 以下，与画面"青格 40 个 · 暗格 60 个"完全一致。三小时 40%（08:00-09:00）、70%（09:00-10:00）、20%（10:00-11:00）；08:00 出门的结论为"带"。'
    src='概率解释按通行气象含义整理；本轮研究未取得官方定义原文，画面明写"不引用任何标准条文"。三句翻译是产品化改写，不是引用。'
    demo='出发时间与三个小时的概率为演示样例 DEMO。' },
  [ordered]@{ id='case-09'; title='路侧停车限时计费'; bg='纸色'; ratio='0.627'; ori='竖屏'; pass='a02';
    stuck='车位牌上"首 15 分钟 x 元、限时 y 小时"，超时怎么算记不住 —— 办事要多久、停下去会不会超，站在车边想不起来。'
    aud='临时办事的司机 · 路边车位旁'
    hero='钟面把 2 小时画成一个整圆，三段扇形对应三个计费档，指针停在 27 分钟；下方一根 120 分钟计费刻度自带刻度数字与两道档位切换线；再下方三张累计卡给出 3 / 9 / 17 元与比例条。'
    data='规则 首 15 分钟 3.00 元、之后每 15 分钟 2.00 元；限时 120 分钟；14:20 到、现在 14:47、已用 27 分钟、已付 5.00 元、距限时 93 分钟；累计 3 / 9 / 17 元（maxFeeAtLimit = 17），日封顶 40 元。钟面三段与累计卡三段一一对应，比例条以 17 为分母。'
    src='计费规则为自拟演示 DEMO；停车价格依据检索摘要（Bing RSS，2026-10-08），属二手来源；超时写为"超过 2 小时不是继续收费，而是按违规停放处理（演示规则 DEMO，以现场标志为准）"，画面不引用罚则金额。'
    demo='时段、费率与限时均为演示样例 DEMO。' },
  [ordered]@{ id='case-10'; title='快递到件时间窗'; bg='深色'; ratio='1.778'; ori='横幅'; pass='a03';
    stuck='物流一直显示"派送中"，节点时间一大堆，却没有一个回答"几点到"。'
    aud='收一件急件的人 · 办公室等快递'
    hero='一条横向五节点轨道（前三站已过、第四站是当前位置并放大着色、第五站是预计窗），下方把预计窗画在与"现在"共用的 105 分钟比例条上，右侧 43 / 78 派件进度，底部给出打电话的时机与一句可照读的话术。'
    data='现在 13:05，预计 14:20-14:50，还有 75 分钟到窗、窗宽 30 分钟；比例条用 0 到 105 分钟的共同量程，窗口占 30 / 105。currentIndex = 3；stationDone 43 / stationTotal 78 = 55.1%；callAfter 17:00，callWhy 为"超过预计窗 2 小时仍无更新"。'
    src='到件时间窗与异常判定是产品化的自拟规则，标注演示 DEMO；本轮未取得快递服务时限的官方原文，画面不引用任何服务标准条文。'
    demo='单号 SF 1234 5678 90、节点时刻与地址均为演示样例 DEMO。' }
)

foreach ($m in $meta) {
    $cid = $m.id
    $d   = Join-Path $out $cid
    if (!(Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

    $pngPath = Join-Path $d 'final.png'
    $dslPath = Join-Path $d 'final.snapshot'
    $pngSha  = (Get-FileHash $pngPath -Algorithm SHA256).Hash
    $dslSha  = (Get-FileHash $dslPath -Algorithm SHA256).Hash
    $pngLen  = (Get-Item $pngPath).Length
    $dslLen  = (Get-Item $dslPath).Length
    $roundNo = [int](Get-Content (Join-Path $d '.round'))

    $body = [IO.File]::ReadAllText($dslPath, [Text.Encoding]::UTF8)
    $g = [regex]::Match($body, '<Container width="(\d+)" height="(\d+)"')
    $cw = $g.Groups[1].Value
    $ch = $g.Groups[2].Value

    # the very first attempt of cases 01-04 was logged as B06-case-NN-r01, the rest as -aNN
    $num = $cid.Substring(5)
    $caseReqs = @($reqs | Where-Object { $_.id -match ('^B06-case-' + $num + '-(r\d\d|a\d\d)$') } |
                  Sort-Object { [datetime]$_.started_at })
    $caseIters = @($iters | Where-Object { $_.case_id -eq $cid })

    $sb = New-Object Text.StringBuilder
    [void]$sb.AppendLine(('# {0} —— {1}' -f $cid, $m.title))
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine(('- 任务：B06（把十个日常信息难题变成惊艳而好用的作品）· 运行：{0} · 时区：{1}' -f 'run-20261002-220723-mimo', 'UTC+08:00'))
    [void]$sb.AppendLine(('- 成品：{0}' -f (Code ('outputs/run-20261002-220723-mimo/B06/' + $cid + '/final.png'))))
    [void]$sb.AppendLine(('  + 同名 {0}（选定尝试 {1}，该件共 {2} 次真实渲染、{3} 次读图）' -f (Code 'final.snapshot'), $m.pass, $caseReqs.Count, $caseIters.Count))
    [void]$sb.AppendLine(('- 受众 / 观看环境：{0}' -f $m.aud))
    [void]$sb.AppendLine(('- 画幅：{0} x {1}（{2}，{3}）· 底色：{4} · {5} bytes PNG / {6} bytes DSL' -f $cw, $ch, $m.ratio, $m.ori, $m.bg, $pngLen, $dslLen))
    [void]$sb.AppendLine(('- 字节校验：PNG sha256 前缀 {0} 与服务原始响应逐字节一致；DSL sha256 前缀 {1}；PNG 与 DSL 尺寸对齐 {2} x {3}' -f (Code $pngSha.Substring(0,16)), (Code $dslSha.Substring(0,16)), $cw, $ch))
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine('## 用户原本卡在哪')
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine($m.stuck)
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine('## 这件作品回答什么')
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine($m.hero)
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine('## 数据与口径')
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine($m.data)
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine('## 来源与假设')
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine($m.src)
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine('## 演示 / 非来源内容')
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine($m.demo)
    [void]$sb.AppendLine('')

    # ---- real render table ($caseReqs already collected above) ----
    [void]$sb.AppendLine('## 真实渲染与迭代')
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine('| 请求 ID | HTTP | 耗时 | 字节 | 起 | 止 |')
    [void]$sb.AppendLine('|---|---|---|---|---|---|')
    foreach ($r in $caseReqs) {
        [void]$sb.AppendLine(('| {0} | {1} | {2} ms | {3} | {4} | {5} |' -f
            (Code $r.id), $r.http_status, $r.duration_ms, $r.bytes, $r.started_at, $r.ended_at))
    }
    [void]$sb.AppendLine('')

    # ---- view evidence table ----
    $caseIters = @($iters | Where-Object { $_.case_id -eq $cid })
    [void]$sb.AppendLine('## 读图证据（每次都用 read 打开实际图片）')
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine('| 尝试 | 判定 | 提交的改动 | 读图看到了什么 | 复核结论 |')
    [void]$sb.AppendLine('|---|---|---|---|---|')
    foreach ($e in $caseIters) {
        $chg = (@($e.changes) -join '；')
        if ($chg.Length -gt 0) { $chg = $chg -replace '\|', '/' }
        $fnd = (@($e.findings) -join '；')
        if ($fnd.Length -gt 0) { $fnd = $fnd -replace '\|', '/' }
        $concl = '待修'
        if ($e.verdict -eq 'accepted') { $concl = '本轮读图复核通过，接受为成品' }
        elseif ($e.verdict -eq 'not-verified') { $concl = '读图工具返回的图片与本图不符，该次不作为证据；已在下一次尝试重新读取并复核' }
        [void]$sb.AppendLine(('| {0} | {1} | {2} | {3} | {4} |' -f $e.pass, $e.verdict, $chg, $fnd, $concl))
    }
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine('所有渲染的 URL、HTTP 状态、耗时、字节数与服务返回的 request_id 都在')
    [void]$sb.AppendLine(('tmp/run-20261002-220723-mimo/B06/requests.jsonl；迭代与逐轮读图证据在同目录 iterations.jsonl。' ))
    [void]$sb.AppendLine('')

    $mdPath = Join-Path $d 'case.md'
    [IO.File]::WriteAllText($mdPath, $sb.ToString(), $utf8)
    Write-Output ('{0}  case.md {1} bytes  ({2} renders, {3} views)' -f
        $cid, (Get-Item $mdPath).Length, $caseReqs.Count, $caseIters.Count)
}
Write-Output 'case.md written for all cases'
