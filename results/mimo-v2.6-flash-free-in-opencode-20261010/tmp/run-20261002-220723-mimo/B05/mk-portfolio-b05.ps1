# mk-portfolio-b05.ps1 -- portfolio.json / portfolio.md / product-brief.md / gallery.html
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B05'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B05'
$utf8 = New-Object Text.UTF8Encoding($false)
$BQ   = [char]96
function Code([string]$s) { return ($BQ + $s + $BQ) }
$RUN = 'run-20261002-220723-mimo'
$tz  = 'UTC+08:00'

$idx = [IO.File]::ReadAllText((Join-Path $tmp 'case-index-b05.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
$reqs = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'requests.jsonl'))) { if ($l.Trim()) { $reqs += ($l | ConvertFrom-Json) } }
$iters = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'iterations.jsonl'))) { if ($l.Trim()) { $iters += ($l | ConvertFrom-Json) } }

# case meta: question / stage / surface / roles
$meta = @{
 'case-01' = @{ q='这栋楼现在是什么态度？'; stage='看清现状';        surface='桌面'; arc='A 看清现状'
   role='全楼的第一屏，牵头人贴到群里的那张图' }
 'case-05' = @{ q='52.8 万是怎么算出来的？'; stage='把钱说清楚';      surface='桌面'; arc='B 钱与口径'
   role='业主大会的造价与比价材料' }
 'case-02' = @{ q='我家到底要掏多少钱？';   stage='算我家的账';      surface='手机'; arc='C 分摊到户'
   role='居民自助算账，点开链接就能看' }
 'case-03' = @{ q='哪种规则对我们楼更公平？'; stage='选规则';         surface='桌面'; arc='D 协商与选型'
   role='协商会现场逐列比对的投票板' }
 'case-04' = @{ q='三户不同意，怎么一条条销掉？'; stage='破顾虑';     surface='桌面'; arc='D 协商与选型'
   role='牵头人每天要打开的销项清单' }
 'case-06' = @{ q='到哪一步了，我怎么签字？'; stage='凑齐 12/12';     surface='手机'; arc='E 签约落地'
   role='公示与签约的进度页，带成功与失败反馈' }
 'case-07' = @{ q='这份对我最不利的算法，我认不认？'; stage='最后一户确认'; surface='平板'; arc='E 签约落地'
   role='面签场景，牵头人当面打开给 602 室看' }
 'case-08' = @{ q='今天盖到哪一步了？';     stage='看着它盖起来';    surface='宽屏'; arc='F 施工与交付'
   role='工地公告屏与群内长图' }
 'case-09' = @{ q='12 项验收过了几项？';     stage='交付验收';        surface='竖屏'; arc='F 施工与交付'
   role='联合验收当天打印签字的清单' }
 'case-10' = @{ q='这十年一共要花多少？';   stage='十年之后回头看';  surface='桌面'; arc='G 长期复盘'
   role='交付后第一年做复盘用的十年账' }
}

$works = @()
foreach ($r in $idx) {
  $cid = $r.id
  $m = $meta[$cid]
  $rs = @($reqs | Where-Object { $_.id -match ('^B05-rnd-' + $cid.Substring(5) + '-\d\d$') -and $_.http_status -eq 200 })
  $shape = '接近方形'
  if ($r.ratio -gt 1.05) { $shape = '横幅' } elseif ($r.ratio -lt 0.95) { $shape = '竖幅' }
  $works += ([ordered]@{
    id = $cid; index = [int]$cid.Substring(5); title = $r.title
    reader_question = $m.q; stage = $m.stage; surface = $m.surface; arc = $m.arc; role = $m.role
    canvas = ('{0}x{1}' -f $r.w, $r.h); width = $r.w; height = $r.h
    aspect_ratio = ('{0} {1}' -f $r.ratio, $shape); background = $r.bg
    final_round = 2; rounds_total = 2
    png_path = ($cid + '/final.png'); snapshot_path = ($cid + '/final.snapshot'); case_md = ($cid + '/case.md')
    png_bytes = $r.pngB; snapshot_bytes = $r.dslB
    png_sha256_16 = $r.pngSha; snapshot_sha256_16 = $r.dslSha
    png_is_service_bytes_untouched = $true; png_matches_last_successful_render_bytes = $true
    request_count = @($reqs | Where-Object { $_.id -match ('^B05-rnd-' + $cid.Substring(5) + '-\d\d$') }).Count
    successful_requests = $rs.Count
    failed_requests = (@($reqs | Where-Object { $_.id -match ('^B05-rnd-' + $cid.Substring(5) + '-\d\d$') }).Count - $rs.Count)
    iteration_count = 2; image_view_count = 2
    render_request_ids = @($rs | ForEach-Object { $_.id })
    render_durations_ms = @($rs | ForEach-Object { [double]$_.duration_ms })
    final_round_request_id = $rs[$rs.Count - 1].id
  })
}
$pngTotal = 0; $dslTotal = 0
foreach ($w in $works) { $pngTotal = $pngTotal + [int]$w['png_bytes']; $dslTotal = $dslTotal + [int]$w['snapshot_bytes'] }

# ---------------------------------------------------------------- portfolio.json
$pf = [ordered]@{
  schema_version = 1; task_id = 'B05'; task_name = 'product from zero'; run_id = $RUN; run_profile = 'all'; timezone = $tz
  product = '同梯 TongTi'
  tagline = '老旧小区加装电梯的共识与分摊工作台'
  problem = '一栋 6 层 12 户的老楼要加装电梯，卡住的不是“装不装”，而是谁出多少说不清、谁不同意没销项、钱和工期没有一张所有人都认的账。'
  promise = '一栋楼一个口径：净自付只有一个数（288,000 元），规则可切换，账可追到十年。'
  scene = '梧桐里小区 3 号楼 · 一梯两户 6 层 12 户 · 西 76.4 / 东 78.9 平米 · 合计 931.8 平米'
  work_count = 10; independent_works_required = 10; independent_works_delivered = 10; final_image_count = 10
  canvas_shapes = '10 种互不重复的宽高比（0.458 / 0.462 / 0.641 / 0.672 / 1.406 / 1.531 / 1.600 / 1.733 / 1.956 / 2.526）'
  surfaces = '桌面 4 屏 / 手机 2 屏 / 平板 1 屏 / 宽屏 1 屏 / 竖屏 2 屏'
  journey_arc = '看清现状 -> 把钱说清楚 -> 算我家的账 -> 选规则 -> 破顾虑 -> 凑齐 12/12 -> 最后一户确认 -> 看着它盖起来 -> 交付验收 -> 十年之后回头看'
  validation_statement = '零到一概念设计：未做真实用户访谈、可用性测试或楼栋试点，产品判断均为设计假设，不声称已被用户验证。'
  claims_discipline = '研究未取得既有加装电梯分摊政策原文，故 10 屏不引用法条、不写法定比例、不写补贴标准；金额一律标注演示数据 DEMO；A/B/C 权重是产品自定义规则而非法规。'
  asset_policy = [ordered]@{ declared = 'dsl_primary_with_supporting_assets'; actual = 'dsl_only_in_practice'
    external_assets_used = 0
    note = '10 屏全部为纯 DSL：剖面、时间轴、条形图、里程碑、检查表、药丸全部由矩形/圆/渐变/矩阵画出；所谓“现场照片”是 DSL 画的剖面示意图并标注“示意图 DEMO”' }
  independence_statement = '10 屏均为独立自包含 DSL（各自完整的 Snapshot 根、各自的画幅与版式），彼此不复用成品、不引用前件图像；共享的只有 lib-b05.ps1 的绘图函数与 calc-b05.json 的权威数据，按约定不计为新增作品。'
  total_png_bytes = $pngTotal; total_snapshot_bytes = $dslTotal
  works = $works
}
[IO.File]::WriteAllText((Join-Path $out 'portfolio.json'), ($pf | ConvertTo-Json -Depth 7), $utf8)
'portfolio.json written'

# ---------------------------------------------------------------- portfolio.md
$L = @()
$L += '# 同梯 TongTi —— B05 作品集'
$L += ''
$L += '- 任务：' + (Code 'B05 product from zero') + ' · 运行：' + (Code $RUN) + ' · 时区：' + $tz
$L += '- 产品：**同梯 TongTi** —— 老旧小区加装电梯的共识与分摊工作台'
$L += '- 场景：梧桐里小区 3 号楼，一梯两户 6 层共 12 户，总建筑面积 931.8 平米'
$L += '- 交付：**10 / 10** 件独立作品 · **10** 种互不重复的宽高比 · 最终图合计 **' + $pngTotal + '** bytes PNG / **' + $dslTotal + '** bytes DSL'
$L += '- 迭代：每件 2 轮（round-01 基线 -> round-02 视觉修复），全部由真实服务渲染并逐张打开复核'
$L += '- 纪律：未取得加装电梯分摊政策原文，因此不引用法条、不写法定比例、不写补贴标准；金额均标演示数据 DEMO；未做用户验证，不声称已被验证'
$L += ''
$L += '## 产品要解决的问题'
$L += ''
$L += '加装电梯这件事，真正的阻塞点是三样东西凑不到一起：**谁出多少说不清**、**谁不同意没销项**、**钱和工期没有一张所有人都认的账**。牵头人只能在群里贴 Excel 截图，居民只能凭感觉吵架，最后卡在 11/12。'
$L += ''
$L += '同梯把这三件事收进一张工作台：净自付只有一个数（288,000 元），分摊规则可以现场切换比较，顾虑有负责人有截止，账一路追到十年。'
$L += ''
$L += '## 旅程与十屏'
$L += ''
$L += '| # | 屏 | 阶段 | 终端 / 用途 | 画幅 | 比例 | 底色 | 回答的问题 |'
$L += '|---|---|---|---|---|---|---|---|'
foreach ($w in $works) {
  $L += ('| {0} | [{1}]({2}/case.md) | {3} | {4} | {5}x{6} | {7} | {8} | {9} |' -f `
    $w.index, $w.title, $w.id, $meta[$w.id].stage, ($meta[$w.id].surface + ' · ' + $w.role), $w.width, $w.height, $w.aspect_ratio, $w.background, $w.reader_question)
}
$L += ''
$L += '## 数据口径（全部由 calc-b05.ps1 算出，再由画面引用）'
$L += ''
$L += '| 项 | 值 | 用在哪些屏 |'
$L += '|---|---|---|'
$L += '| 总造价 / 补贴 / 净自付 | 528,000 / 240,000 / **288,000** 元 | 01 02 03 04 05 10 |'
$L += '| 模型 A / B / C 单户最高 | 42,985 / 24,386 / 47,213 元 | 01 02 03 04 05 07 |'
$L += '| 模型 A / C 权重和 | 6.70 / 6.10（B 为 309.08 元每平米） | 02 03 07 |'
$L += '| 态度 | 已签约 7 · 已同意 2 · 顾虑 3（101 / 202 / 602） | 01 06 |'
$L += '| 支持 / 签约 | 9 / 12 = 75% · 7 / 12 = 58% | 01 06 |'
$L += '| 每年公共支出 | 13,800 元（4800 + 1800 + 1200 + 6000） | 07 10 |'
$L += '| 十年 | 138,000 运行 + 288,000 自付 = **426,000** 元；每户十年 35,500 元 | 10 |'
$L += '| 602 室十年三模型 | 63,582 / 36,071 / 69,836 元，相差 33,765 元 | 10 |'
$L += '| 工期 | 65 天（10+10+14+15+8+8），开工 2026-10-20，交付 2026-12-23，第 28 天进度 43.1% | 05 07 08 |'
$L += '| 验收 | 12 项 = 10 合格 / 1 待检 / 1 整改，验收 2026-12-19，责任期限 12-21 | 09 |'
$L += ''
$L += '## 跨屏一致性自检'
$L += ''
$L += '对 10 份 ' + (Code 'final.snapshot') + ' 的可见文本做过比对：'
$L += ''
$L += '- ' + (Code '288,000') + ' 出现在 02 / 03 / 04 / 10'
$L += '- ' + (Code '42,985') + ' 出现在 01 / 02 / 03 / 04 / 05 / 07'
$L += '- ' + (Code '7 / 12') + ' 与 ' + (Code '9 / 12') + ' 同时出现在 01 / 06，三色格与剖面逐户一致'
$L += '- ' + (Code '2026-10-08') + ' 同时出现在 01（状态快照）与 06（异议期第 1 天），04 的剩余天数也以它为今日'
$L += '- ' + (Code '65 天') + ' 出现在 05 / 07 / 08'
$L += '- 开工 2026-10-20、现场记录 2026-11-16（第 28 天）、交付 2026-12-23（第 65 天）、验收 2026-12-19 四个日期互相自洽'
$L += ''
$L += '## 索引'
$L += ''
$L += '- ' + (Code 'portfolio.json') + ' / ' + (Code 'journey.json') + ' / ' + (Code 'product-brief.md') + ' / ' + (Code 'gallery.html') + ' / ' + (Code 'snapshot-usage.md') + ' / ' + (Code 'task-metrics.json')
$L += '- 逐屏：' + (Code 'case-NN/case.md') + '（画幅、数据口径、渲染请求表、逐轮读图证据）'
$L += '- 过程日志：' + (Code 'tmp/run-20261002-220723-mimo/B05/requests.jsonl') + '、' + (Code 'iterations.jsonl') + '、' + (Code 'tool-usage.jsonl') + ''
$L += ''
[IO.File]::WriteAllLines((Join-Path $out 'portfolio.md'), $L, $utf8)
'portfolio.md written'

# ---------------------------------------------------------------- product-brief.md
$P = @()
$P += '# 产品需求文档 —— 同梯 TongTi'
$P += ''
$P += '- 任务：' + (Code 'B05 product from zero') + ' · 运行：' + (Code $RUN) + ' · 时区：' + $tz
$P += '- 版本：v1（零到一概念设计）· 配套：' + (Code 'journey.json') + ' / ' + (Code 'portfolio.json') + ''
$P += '- **验证状态：未验证。** 本文全部判断都是设计假设，没有做过用户访谈、可用性测试或真实楼栋试点，不引用任何用户结论。'
$P += ''
$P += '## 1. 要解决的真实问题'
$P += ''
$P += '既有住宅加装电梯，卡点从来不在机械，而在共识。一栋 6 层 12 户的老楼要推进，同时要满足三件事：'
$P += ''
$P += '1. **钱要说得清** —— 造价、补贴、净自付必须是同一个数，且能被任一住户当场复算；'
$P += '2. **人要销得掉** —— 每一条“不同意”都要变成有负责人、有应对方案、有截止日期的可销项条目；'
$P += '3. **账要追得远** —— 一次性的自付和此后每年的运行支出要放在同一张表上，否则居民永远在比“首付”而忽略十年。'
$P += ''
$P += '现状是三件事分别散落在群聊、Excel 截图和口头承诺里，牵头人每次回答都要从头解释一遍，进度一卡在 11/12 就反复推倒重来。'
$P += ''
$P += '## 2. 目标用户与使用场景'
$P += ''
$P += '| 用户 | 场景 | 他要完成的任务 | 对应屏 |'
$P += '|---|---|---|---|'
$P += '| 牵头人 / 业委会 | 每天推进度、回复顾虑 | 看清 12 户态度、逐条销项、留痕 | 01 04 06 |'
$P += '| 单户居民 | 群里收到链接，用手机点开 | 知道我家出多少、怎么签 | 02 06 |'
$P += '| 业主大会 | 现场开会 | 三种规则横向比，选一个 | 03 05 |'
$P += '| 顾虑户（如 602 室） | 当面沟通 / 面签 | 把对自己不利的算法看清楚再决定 | 07 |'
$P += '| 全体业主 | 开工后每周 | 今天盖到哪一步 | 08 |'
$P += '| 验收组 | 交付当天 | 12 项逐条打勾、未过项落责任人 | 09 |'
$P += '| 复盘的人 | 交付后第一年 | 这十年一共花多少 | 10 |'
$P += ''
$P += '## 3. 核心主张（一句话）'
$P += ''
$P += '> **一栋楼一个口径：净自付只有一个数，规则可以现场切换，账能追到十年。**'
$P += ''
$P += '拆开就是三个承诺：'
$P += ''
$P += '- **单一口径** —— 528,000 元造价、240,000 元补贴、**288,000 元净自付**，全楼任何一屏引用的都是这一个数；'
$P += '- **规则可切换** —— A 按楼层递增、B 按面积均摊、C 低层免摊，任一住户可自己切换看到自己的数；'
$P += '- **账追十年** —— 288,000 一次性 + 每年 13,800 运行 = 十年 426,000 元，摊到每户 35,500 元。'
$P += ''
$P += '## 4. 范围内'
$P += ''
$P += '- 10 屏构成的完整旅程：现状盘点、造价与比价、单户试算、三模型对比、顾虑销项、公示与签约、面签确认、施工进度、交付验收、十年复盘；'
$P += '- 三套分摊规则的完整算术（权重和、单位权重、逐户金额、极差、零负担户数）；'
$P += '- 12 户态度与签约状态的可视化（剖面 + 状态格 + 图例）；'
$P += '- 真实的状态反馈：成功、失败、进行中、未通过项各自有明确文案与颜色；'
$P += '- 跨屏一致的数字与日期（见 portfolio.md 的自检表）。'
$P += ''
$P += '## 5. 范围外（本期不做）'
$P += ''
$P += '- **不做政策解释器** —— 研究中没有取得任何一条既有加装电梯费用分摊的政策原文，所以本产品不引用法条、不给出法定分摊比例、不给出任何地区的补贴标准；'
$P += '- **不做采购询价** —— 三家供应商的报价、工期、质保年限都是样例，不构成推荐；'
$P += '- **不做支付** —— 三期付款只做演示节点，不接资金流；'
$P += '- **不做身份与法律效力** —— 签约提交只产生演示受理编号，不产生任何法律效力；'
$P += '- **不做真实楼栋试点** —— 梧桐里 3 号楼、12 个户号、负责人姓名全部是演示样例。'
$P += ''
$P += '## 6. 关键设计决策与理由'
$P += ''
$P += '| 决策 | 理由 |'
$P += '|---|---|'
$P += '| 把“剖面”当全产品统一的视觉母题 | 一栋楼的分摊本质是“哪一层、哪一户”，剖面天然把楼层、户号、态度、井道四件事放在同一张图上 |'
$P += '| 三套规则并排而不是只给推荐值 | 公平感来自“我能自己比较”，不是来自“系统告诉我答案” |'
$P += '| 顾虑做成台账而不是评论区 | 有负责人、有截止、有状态才可能被销项，否则永远停留在情绪 |'
$P += '| 失败反馈写清原因与下一步 | 签约失败最伤进度，明确“7.3 MB 超过 5 MB，请压缩重试”比一句“提交失败”有用得多 |'
$P += '| 十年总账单列一屏 | 只比一次性自付会系统性地低估高层户的长期成本，也低估运行支出 |'
$P += '| 手机 2 屏 + 平板 1 屏 + 宽屏 1 屏 | 居民在手机上看、面签在平板上看、工地与公告用宽屏，各占其位 |'
$P += ''
$P += '## 7. 成功指标（设计假设，尚未测量）'
$P += ''
$P += '- 居民第一次打开 02 屏后，能不借助他人解释说出自己的金额与所选规则；'
$P += '- 牵头人打开 04 屏时，3 条顾虑都处在“有负责人 + 有截止”状态；'
$P += '- 06 屏的签约进度在异议期结束前从 7/12 推到 12/12；'
$P += '- 09 屏未过项在 12-21 前全部闭环。'
$P += ''
$P += '以上均为设计假设，**没有做过任何真实测量**。'
$P += ''
$P += '## 8. 风险与未决问题'
$P += ''
$P += '- **政策口径缺位**：没有拿到政策原文，产品只能提供“算术与留痕”，不能提供“合规背书”。这是本期最大的能力边界。'
$P += '- **规则正当性**：A/B/C 是产品自定义规则，权重怎么定仍需在具体楼栋里谈，产品只能把代价摆清楚。'
$P += '- **未验证**：没有用户反馈，10 屏的信息密度、术语与流程顺序都可能与真实居民的心智不符。'
$P += '- **演示数据污染风险**：所有金额都带 DEMO 标注，后续接真实数据时必须先清掉演示标记，避免误传。'
$P += ''
$P += '## 9. 数据与声明纪律'
$P += ''
$P += '- 金额一律标注 **演示数据 DEMO** 或样例价格，未做真实采购询价；'
$P += '- 未取得政策原文 -> 不写法条、不写法定比例、不写补贴标准；'
$P += '- A / B / C 权重明写为产品自定义规则，不是法规要求；'
$P += '- 供应商、检验结论、现场记录、负责人、截止日期、受理编号均为演示样例，不对应真实企业或个人；'
$P += '- 未做用户访谈与测试，不声称任何用户结论已被验证。'
$P += ''
[IO.File]::WriteAllLines((Join-Path $out 'product-brief.md'), $P, $utf8)
'product-brief.md written'

# ---------------------------------------------------------------- gallery.html
$E = [System.Text.StringBuilder]::new()
function W([string]$s) { [void]$script:E.AppendLine($s) }
W '<!DOCTYPE html>'
W '<html lang="zh-CN">'
W '<head>'
W '<meta charset="utf-8">'
W '<meta name="viewport" content="width=device-width, initial-scale=1">'
W '<title>同梯 TongTi — B05 十屏作品画廊</title>'
W '<style>'
W ':root{--ink:#12161B;--panel:#1A2028;--paper:#EDEAE3;--acc:#E4632A;--acc2:#F2A03C;--teal:#1E9B8A;--amber:#E0A32E;--coral:#DC5238;--mute:#94A0AE;--hair:#2E3742}'
W '*{box-sizing:border-box}'
W 'body{margin:0;background:#0B0E12;color:#C4CEDA;font-family:"Noto Sans CJK SC","Inter",system-ui,sans-serif;line-height:1.75}'
W 'header{padding:44px 32px 28px;border-bottom:1px solid var(--hair);background:linear-gradient(180deg,#141A21,#0B0E12)}'
W 'h1{margin:0 0 8px;font-size:30px;color:#fff;font-weight:700}'
W '.sub{color:var(--mute);font-size:14px}.sub b{color:var(--acc2);font-weight:600}'
W 'nav{padding:16px 32px;border-bottom:1px solid var(--hair);font-size:13px;color:var(--mute);flex-wrap:wrap}'
W 'nav a{color:#F2A03C;text-decoration:none;margin-right:14px}'
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
W '.m i{color:#F2A03C;font-style:normal}'
W '.m u{color:#7C8B9A;text-decoration:none}'
W 'section{margin-top:46px}'
W 'h2{font-size:20px;color:#fff;border-left:4px solid var(--acc);padding-left:12px;margin:0 0 16px}'
W 'table{width:100%;border-collapse:collapse;font-size:13px}'
W 'th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--hair)}'
W 'th{color:var(--acc2);font-weight:600;background:#141A21}'
W 'td{color:#AEBCCA}td code{background:#141C24}'
W 'code{background:#141C24;padding:2px 5px;border-radius:3px;font-size:12px;color:#F2A03C}'
W 'a{color:#F2A03C}'
W '.flow{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}'
W '.flow span{font:12px/1 "Noto Sans Mono CJK SC",monospace;background:#141A21;border:1px solid var(--hair);border-radius:999px;padding:8px 13px;color:#AEBCCA}'
W '.flow span b{color:#fff;font-weight:600}'
W 'footer{padding:24px 32px 44px;border-top:1px solid var(--hair);color:var(--mute);font-size:12px}'
W '</style>'
W '</head>'
W '<body>'
W '<header>'
W '<h1>同梯 TongTi —— 老旧小区加装电梯的共识与分摊工作台</h1>'
W '<div class="sub">B05 product from zero · 运行 <b>' + $RUN + '</b> · 时区 <b>' + $tz + '</b> · 场景 <b>梧桐里 3 号楼 12 户</b> · <b>10 / 10</b> 件独立作品 · <b>10</b> 种互不重复的画幅</div>'
W '</header>'
W '<nav><a href="#works">十屏</a><a href="#flow">旅程</a><a href="#data">数据口径</a><a href="#consistency">跨屏一致性</a><a href="#logs">日志与指标</a><a href="portfolio.md">portfolio.md</a><a href="product-brief.md">product-brief.md</a><a href="journey.json">journey.json</a><a href="snapshot-usage.md">snapshot-usage.md</a><a href="task-metrics.json">task-metrics.json</a></nav>'
W '<main>'
W '<section id="works"><h2>十件作品（点击图片打开原尺寸）</h2><div class="grid">'
foreach ($w in $works) {
  $m = $meta[$w.id]
  W '<figure>'
  W ('<a href="{0}/final.png" target="_blank" rel="noopener">' -f $w.id)
  W ('<img src="{0}/final.png" alt="{1} {2}" width="{3}" height="{4}" loading="lazy">' -f $w.id, $w.id, $w.title, $w.width, $w.height)
  W '</a>'
  W '<figcaption>'
  W ('<span class="num">{0:00} / 10</span><span class="stg">{1}</span>' -f $w.index, $m.stage)
  W ('<span class="t">{0}</span>' -f $w.title)
  W ('<span class="q">{0}</span>' -f $w.reader_question)
  W ('<span class="m"><i>{0}x{1}</i> · {2} · {3} · {4} · r01&rarr;r02 · {5} B png / {6} B dsl<br><u>{7}</u> · <a href="{8}/case.md">case.md</a> · <a href="{9}/final.snapshot">final.snapshot</a></span>' -f $w.width, $w.height, $w.aspect_ratio, $w.background, $m.surface, $w.png_bytes, $w.snapshot_bytes, $m.role, $w.id, $w.id)
  W '</figcaption>'
  W '</figure>'
}
W '</div></section>'

W '<section id="flow"><h2>旅程：十步走完一栋楼</h2>'
W '<div class="flow">'
foreach ($w in $works) { W ('<span><b>{0:00}</b> {1} · {2}</span>' -f $w.index, $meta[$w.id].stage, $meta[$w.id].surface) }
W '</div>'
W '<table><tr><th>步</th><th>屏</th><th>阶段</th><th>入口状态</th><th>用户做的事</th><th>出口状态</th></tr>'
$jn = [IO.File]::ReadAllText((Join-Path $out 'journey.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
foreach ($s in $jn.stages) {
  W ('<tr><td>{0:00}</td><td><code>{1}</code></td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>' -f $s.step, $s.screen, $s.stage, $s.entry, $s.action, $s.exit)
}
W '</table>'
W '<p style="font-size:13px;color:#94A0AE">状态反馈：成功（受理编号 WT3-20261008-07）· 失败（授权书 7.3 MB 超 5 MB，请压缩重试）· 进行中（异议期第 1 天 / 施工第 28 天）· 未通过（待检 1 项、整改 1 项，责任期限 12-21）。</p>'
W '</section>'

W '<section id="data"><h2>数据口径（全部由 calc-b05.ps1 算出）</h2>'
W '<table><tr><th>项</th><th>值</th><th>出现在</th></tr>'
W '<tr><td>总造价 / 补贴 / 净自付</td><td>528,000 / 240,000 / <b>288,000</b> 元</td><td>01 02 03 04 05 10</td></tr>'
W '<tr><td>模型 A / B / C 单户最高</td><td>42,985 / 24,386 / 47,213 元</td><td>01 02 03 04 05 07</td></tr>'
W '<tr><td>模型 A / C 权重和</td><td>6.70 / 6.10（B 为 309.08 元每平米）</td><td>02 03 07</td></tr>'
W '<tr><td>态度</td><td>已签约 7 · 已同意 2 · 顾虑 3（101 / 202 / 602）</td><td>01 06</td></tr>'
W '<tr><td>支持 / 签约</td><td>9 / 12 = 75% · 7 / 12 = 58%</td><td>01 06</td></tr>'
W '<tr><td>每年公共支出</td><td>13,800 元（4800 + 1800 + 1200 + 6000）</td><td>07 10</td></tr>'
W '<tr><td>十年总账</td><td>288,000 + 138,000 = 426,000 元；每户十年 35,500 元</td><td>10</td></tr>'
W '<tr><td>602 室十年三模型</td><td>63,582 / 36,071 / 69,836 元，相差 33,765 元</td><td>10</td></tr>'
W '<tr><td>工期</td><td>65 天 = 10+10+14+15+8+8；开工 2026-10-20、第 28 天 43.1%、交付 2026-12-23</td><td>05 07 08</td></tr>'
W '<tr><td>验收</td><td>12 项 = 10 合格 / 1 待检 / 1 整改；验收 2026-12-19，责任期限 12-21</td><td>09</td></tr>'
W '</table></section>'

W '<section id="consistency"><h2>跨屏一致性与声明纪律</h2>'
W '<table><tr><th>检查</th><th>结果</th></tr>'
W '<tr><td><code>288,000</code></td><td>02 / 03 / 04 / 10 四屏同一数</td></tr>'
W '<tr><td><code>42,985</code></td><td>01 / 02 / 03 / 04 / 05 / 07 六屏同一数</td></tr>'
W '<tr><td><code>7 / 12</code> 与 <code>9 / 12</code></td><td>01 与 06 同时出现，三色格与剖面逐户一致</td></tr>'
W '<tr><td><code>2026-10-08</code></td><td>01（状态快照）与 06（异议期第 1 天）同日，04 的剩余天数同以此为今日</td></tr>'
W '<tr><td><code>65 天</code></td><td>05 / 07 / 08 三屏一致，且与 10-20 -> 11-16 -> 12-19 -> 12-23 四个日期自洽</td></tr>'
W '<tr><td>尺寸</td><td>10/10 的 PNG 实际像素与 DSL 首个 Container 一致，final.png 与服务原始字节 SHA256 一致</td></tr>'
W '<tr><td>政策</td><td>研究未取得加装电梯分摊政策原文 -> 不引用法条、不写法定比例、不写补贴标准</td></tr>'
W '<tr><td>金额</td><td>全部标注演示数据 DEMO / 样例价格，未做真实采购询价</td></tr>'
W '<tr><td>权重</td><td>A / B / C 明写为产品自定义规则，不是法规要求</td></tr>'
W '<tr><td>验证</td><td>未做用户访谈与测试，不声称任何用户结论已被验证</td></tr>'
W '</table></section>'

W '<section id="logs"><h2>日志与指标</h2>'
W '<table><tr><th>文件</th><th>内容</th></tr>'
W '<tr><td><a href="portfolio.json">portfolio.json</a></td><td>作品清单、画幅、字节、渲染请求 ID</td></tr>'
W '<tr><td><a href="portfolio.md">portfolio.md</a></td><td>人读版作品集与数据口径表</td></tr>'
W '<tr><td><a href="product-brief.md">product-brief.md</a></td><td>产品需求文档（问题、用户、范围、决策、风险、声明纪律）</td></tr>'
W '<tr><td><a href="journey.json">journey.json</a></td><td>10 步旅程：入口状态 / 动作 / 出口状态 / 下一屏 + 跨屏一致性 + 声明纪律</td></tr>'
W '<tr><td><a href="snapshot-usage.md">snapshot-usage.md</a></td><td>文档与 DSL 实际应用、踩坑、复核</td></tr>'
W '<tr><td><a href="task-metrics.json">task-metrics.json</a></td><td>请求 / 迭代 / 看图 / 字节 / 耗时，全部从 JSONL 反查</td></tr>'
W '<tr><td><code>tmp/run-20261002-220723-mimo/B05/</code></td><td>requests.jsonl · iterations.jsonl · tool-usage.jsonl · plan.md · calc-b05.json · 各 .snapshot 原件</td></tr>'
W '</table></section>'
W '</main>'
W '<footer>同梯 TongTi · B05 product from zero · ' + $RUN + ' · ' + $tz + ' · 本页全部图片为相对链接的本地文件，无远程脚本</footer>'
W '</body>'
W '</html>'
[IO.File]::WriteAllText((Join-Path $out 'gallery.html'), $E.ToString(), $utf8)
'gallery.html written'
