# close-b05.ps1 -- B05 -> completed, B06 -> in_progress, append event seq 59 + checkpoint state-000035.json
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$run  = 'run-20261002-220723-mimo'
$so   = Join-Path $root "outputs\$run\_suite"
$st   = Join-Path $root "tmp\$run\_suite"
$enc  = New-Object System.Text.UTF8Encoding($false)
$now  = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss+08:00')

$ssPath = Join-Path $so 'suite-state.json'
$ss = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json

$art = @(
 "outputs/$run/B05/portfolio.json"
 "outputs/$run/B05/portfolio.md"
 "outputs/$run/B05/product-brief.md"
 "outputs/$run/B05/journey.json"
 "outputs/$run/B05/gallery.html"
 "outputs/$run/B05/snapshot-usage.md"
 "outputs/$run/B05/task-metrics.json"
)
foreach ($i in 1..10) {
  $c = 'case-{0:d2}' -f $i
  $art += "outputs/$run/B05/$c/final.png"
  $art += "outputs/$run/B05/$c/final.snapshot"
  $art += "outputs/$run/B05/$c/case.md"
}

$ev = @(
 "outputs/.../B05/case-01/final.png  1600x1000 216801 B（读图工具实际查看，r02）：12 户剖面按态度着色，右侧 4 张 KPI 的单位与数字分层排版后不再叠印，进度条与备注行已拉开；9/12=75%、7/12=58%、0-42,985 元区间与剖面 12 户逐户一致"
 "outputs/.../B05/case-02/final.png  540x1180 131872 B（读图工具查看，r02）：滑杆最小值由裸 46.0 改为 46.0 万元、最大值 58.0 万元，与中间的 52.8 万元同一单位；权重 6.70 与 288,000 / 6.70 = 42,985 自洽"
 "outputs/.../B05/case-03/final.png  1500x980 216115 B（读图工具查看 r02 两次）：r02 首看发现模型 A 权重合计渲染成裸浮点 6.699999999999999993、模型 B 单位权重显示 309 元/㎡ 与规则行 309.08 元/㎡ 不一致；改为 ToString('0.00') 后重渲染复看，现在 6.70 / 6.10 / 309.08 三处一致，极差列收在行底阴影内"
 "outputs/.../B05/case-04/final.png  1440x1024 269560 B（读图工具查看，r02）：每行重复的列头 kicker 已删除并重排行距；截止 10-12 / 10-15 / 10-18 与剩余 4 / 7 / 10 天全部以 2026-10-08 为今日，与 case-01 状态快照同日"
 "outputs/.../B05/case-05/final.png  1760x900 241212 B（读图工具查看，r02）：报价列重排后行距拉开、供应商副行改写为同口径差额；三块卡片的空腔补上每户平均造价 44,000 元、566.6 元每平米、补贴后每户 24,000 元与「与最低同口径的差额」条形图，全部贴在 794-800 守卫线以上"
 "outputs/.../B05/case-06/final.png  480x1040 115302 B（读图工具查看，r02）：异议期由「第 3 天 / 共 7 天（=10-10）」改为「第 1 天 / 共 7 天」、受理编号 WT3-20261007-07 改为 WT3-20261008-07，与 case-01/04 的 2026-10-08 快照和「签约 2026-10-08 起」同时自洽；12 户三色格 7 青 / 2 琥珀 / 3 珊瑚与 case-01 逐户一致，成功与失败两条状态反馈完整"
 "outputs/.../B05/case-07/final.png  900x1340 184535 B（读图工具查看 r02 两次）：剖面格子高下不足 60px 时改单行排版，户号与态度不再叠印；下半屏四处零间距（付款卡第 3 行贴核对标题、核对卡第 3 行贴 CTA、CTA 贴脚注）全部拉开并复看确认；12,896+17,194+12,895=42,985 与合计一致"
 "outputs/.../B05/case-08/final.png  1920x760 166943 B（读图工具查看，r02）：现场记录由 2026-10-15（早于开工）改为 2026-11-16、交付由 12-06 改为 12-23；6 段里程碑 10+10+14+15+8+8=65 天、第 28 天进度 43.1%、「井道与玻璃幕墙 第 8 天 / 共 14 天」与三个日期互相自洽"
 "outputs/.../B05/case-09/final.png  1000x1560 257796 B（读图工具查看 r02 两次）：12 项验收日期整批从 10 月移到 12-18 / 12-19、责任期限 12-21 后仍有一处首次运行记录写着 2026-10-12（早于开工 2026-10-20），改回 2026-12-19 09:12 后复看确认；合格 10 / 待检 1 / 整改 1 与清单逐条一致"
 "outputs/.../B05/case-10/final.png  1560x900 128823 B（读图工具查看 r02 三次）：纵轴由 0/11/21/32/43 万改为 0/10/20/30/40/50 万并按 500000 缩放柱高；KPI 标签由「每户年均 35,500 元」改为「每户十年 35,500 元」（426,000/12 才是十年数），复看确认 288,000+138,000=426,000、63,582/120=530、36,071/120=301、69,836/120=582 均正确"
 "outputs/.../B05/task-metrics.json  程序生成（mk-metrics-b05.ps1 从 JSONL 反查）：68 请求（render 38 = 32x200 + 6x400、documentation 9x200、fonts 1x200、research 20 = 18x200 + 1x404 + 1 网络失败），60 成功 / 8 失败，0 条 429（ratelimit_remaining 最低 110），请求耗时之和 180.746s（渲染 138.927s），墙钟 10389.448s；迭代 6 行、tool-usage 12 行、读图 47 次（43 个唯一字节副本为可核验下界，10 件终图全部确认，8 次串图留档）；token/图像用量/费用 null 并注明原因"
 "outputs/.../B05/product-brief.md  B05 指定额外交付：问题、用户与场景、一句话主张、范围内/外、6 条设计决策、4 条设计假设型成功指标、风险与未决问题、数据与声明纪律；首行明写「验证状态：未验证」"
 "outputs/.../B05/journey.json  B05 指定额外交付：10 步旅程，每步带 stage / persona / surface / goal / entry / key_facts / action / exit / next，外加 cross_screen_consistency（共享数字与日期）、state_feedback（成功/失败/进行中/未过项/边界提示）、claims_discipline 与 exit_paths"
)

$unresolved = @(
 "无阻塞项：B05 已 completed，10 屏完整产品旅程全部经真实 open-snapshot 服务渲染，终版全部用读图工具实际打开并核对刊头 NN/10 与画幅后才落盘，37 个交付文件齐全、gallery.html 36 条相对链接全部有效",
 "研究侧 B05-res-16-sh-search（404）与 B05-res-10-ddg（网络失败）按原样保留；核心问题改由 gov.cn 全文检索、flk.npc.cn、司法部行政法规库与住建部入口覆盖",
 "研究最终未取得任何一条既有住宅加装电梯费用分摊的政策原文：10 屏不引用法条、不写法定分摊比例、不写补贴标准，补贴 240,000 元标演示数据 DEMO，A/B/C 权重明写为产品自定义规则。这是本期最大的能力边界，已写入 product-brief.md 风险节与 snapshot-usage.md 第 2 节",
 "6 条 render HTTP 400（3 次 border 裸色值写在圆上、2 次 Ts 第 12 个参数落进 bold 产生 fontStyle=LEFT、1 次 color 写成中文 元）保留原始失败响应字节，修好后重交全部 200",
 "read 工具按内容哈希缓存串图，round-02 后段可逐条核验 8 次返回上一张字节；已用 System.Drawing 生成文件名唯一、角像素微调或加边框的新副本恢复逐件看图，最终 10 件全部确认正确字节",
 "browser.preview 在本环境不可用（browser.disconnected），看图只能走 read 工具",
 "未做用户访谈、可用性测试或真实楼栋试点：product-brief.md 的成功指标是设计假设而非已验证结论，journey.json 的 validation 字段同样写明",
 "token / 图像使用量 / 费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明 unknown_fields_reason；排队等待不可测记 null；限流等待 0（未出现 429/Retry-After，属实测非未知）",
 "梧桐里 3 号楼、12 个户号、三家供应商、检验结论、现场记录、负责人与受理编号全部为演示样例；接真实数据前必须先清掉 DEMO 标记",
 "读图的精确单次时刻未被工具记录，iterations.jsonl 以 phases + defects 列表记录，不编造具体时刻"
)

$resume = "completed；无阻塞，可继续 B06（最后一题）。10 屏：case-01 1600x1000 / case-02 540x1180 / case-03 1500x980 / case-04 1440x1024 / case-05 1760x900 / case-06 480x1040 / case-07 900x1340 / case-08 1920x760 / case-09 1000x1560 / case-10 1560x900，10 种宽高比互不重复（0.458/0.462/0.641/0.672/1.406/1.531/1.600/1.733/1.956/2.526），终版 PNG 服务原始字节合计 1928959 B + DSL 226862 B，全部无后处理。请求 68 行串行（render 38 中 32x200 + 6x400、documentation 9x200、fonts 1x200、research 20 中 18x200 + 1x404 + 1 网络失败），0 限流 0 排队，6 次 400 修好后重交，请求耗时之和 180.746s（渲染 138.927s），墙钟 10389.448s（2026-10-08T09:14:43 -> 12:07:52）。迭代 6 行（baseline / view_pass / generate / render / view_pass / fix+re-render）、tool-usage 12 行、读图 47 次（43 个唯一字节副本为可核验下界，10 件终图全部确认，8 次串图已留档）。交付 7 项顶层产物（portfolio.json / portfolio.md / product-brief.md / journey.json / gallery.html / snapshot-usage.md / task-metrics.json）+ 10 组 case-NN/{final.png,final.snapshot,case.md}。B05 专属额外交付 product-brief.md（问题/用户/主张/范围/决策/假设型指标/风险/声明纪律）与 journey.json（10 步入口-动作-出口 + 跨屏一致性 + 状态反馈 + 声明纪律 + 出口路径）。\n关键经验（已写入 snapshot-usage.md）：(1) 零到一产品题必须先有 calc 数据集再画，所有数字从 calc-b05.json 引用，跨屏才可能一致；(2) 跨屏一致性要靠脚本文本比对而不是肉眼——本题靠它抓到 case-09 的 2026-10-12、case-06 的第 3 天与 WT3-20261007、case-10 的每户年均标签、case-03 的 309 元/㎡、case-08 的 10-15/12-06 五处真问题；(3) 可见文本绝不允许 4 位以上小数，权重和要先 Round(x,2) 再 ToString('0.00')；(4) read 工具串图用「新 GUID 文件名 + 改 1 个角像素或加边框 + shell 后 sleep 再读 + 核对刊头」恢复；(5) markdown 反引号不能进 PowerShell 双引号字符串（会被当成转义符产生 TAB/CR），要用 [char]96 拼；(6) Measure-Object 读不了 OrderedDictionary 的键，求和用循环；(7) 研究拿不到政策原文就如实写「没拿到」并全面收紧措辞，而不是换个说法绕过去。可复用：lib-b05.ps1 的 Masthead5/Foot5/Section5（剖面格自适应）/Stack1/Pill/Write-Dsl5、calc-b05.ps1 的分摊与工期算法、render-b05.ps1 全字段请求日志、mk-logs/mk-portfolio/mk-metrics 从 JSONL 反查生成的做法；成品不得重复计数。"

$b05 = @($ss.tasks | Where-Object { $_.id -eq 'B05' })[0]
$b05.status = 'completed'
$b05.ended_at = $now
$b05.completed_rounds = @('r01','r02')
$b05.completed_cases = @(1..10 | ForEach-Object { 'case-{0:d2}' -f $_ })
$b05.artifacts = $art
$b05.visual_review_evidence = $ev
$b05.unresolved_issues = $unresolved
$b05.resume_notes = $resume

$b06 = @($ss.tasks | Where-Object { $_.id -eq 'B06' })[0]
if ($b06.status -eq 'pending') {
  $b06.status = 'in_progress'
  $b06.started_at = $now
  $b06.output_dir = "outputs/$run/B06/"
  $b06.temp_dir = "tmp/$run/B06/"
}

$ss.current_task = 'B06'
$ss.current_case = $null
$ss.current_round = $null
$ss.last_checkpoint = 'state-000035.json'
$ss.updated_at = $now

[IO.File]::WriteAllText($ssPath, ($ss | ConvertTo-Json -Depth 12), $enc)
$chk = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
"  suite-state.json written  ({0} bytes)  tasks={1}  b05={2}  b06={3}  current={4}  ckpt={5}" -f `
  (Get-Item $ssPath).Length, @($chk.tasks).Count, (@($chk.tasks|Where-Object{$_.id -eq 'B05'})[0].status), (@($chk.tasks|Where-Object{$_.id -eq 'B06'})[0].status), $chk.current_task, $chk.last_checkpoint

# ---- event seq 59 ----
$note = "B05 完成并关闭（product from zero「同梯 TongTi 老旧小区加装电梯的共识与分摊工作台」）。10 屏完整产品旅程全部为纯 DSL、经真实 open-snapshot 服务渲染，终版 PNG 与服务原始响应逐字节一致（216801/131872/216115/269560/241212/115302/184535/166943/257796/128823，合计 1928959 B；DSL 合计 226862 B），IHDR 尺寸与 DSL 首个 Container 宽高逐一相等（1600x1000 / 540x1180 / 1500x980 / 1440x1024 / 1760x900 / 480x1040 / 900x1340 / 1920x760 / 1000x1560 / 1560x900），10 种宽高比互不重复（0.458/0.462/0.641/0.672/1.406/1.531/1.600/1.733/1.956/2.526）。请求 68 行（render 38 = 32x200 + 6x400；documentation 9x200；fonts 1x200；research 20 = 18x200 + 1x404 + 1 网络失败），60 成功 / 8 失败，6 次 400 均为属性写法错误（3 次 border 裸色值写在圆上、2 次 Ts 第 12 参数落进 bold 致 fontStyle=LEFT、1 次 color 写成中文 元），修好重交全部 200，0 条 429（ratelimit_remaining 最低 110），请求耗时之和 180.746s（渲染 138.927s），墙钟 10389.448s（2026-10-08T09:14:43+08:00 -> 12:07:52+08:00）。迭代 6 行（baseline / r01 view_pass / r02 generate / r02 render / r02 view_pass / r02 fix+re-render）、tool-usage 12 行、读图 47 次（43 个唯一字节视图副本为可核验下界，10 件终图全部核对刊头 TONGTI NN/10 与画幅确认，round-02 后段 8 次串图已留档）。交付 7 项顶层产物 + 10 组 case-NN/{final.png,final.snapshot,case.md} = 37 个文件，gallery.html 36 条相对链接全部有效。B05 指定额外交付 product-brief.md（首行明写「验证状态：未验证」）与 journey.json（10 步入口-动作-出口 + 跨屏一致性 + 状态反馈 + 声明纪律 + 出口路径）。跨屏文本比对抓到并修复 5 处真问题：case-09 首次运行记录 2026-10-12 早于开工、case-06 异议期第 3 天与受理编号 WT3-20261007-07 与 2026-10-08 快照矛盾、case-10 KPI「每户年均」配 35,500 元（实为每户十年 426,000/12）、case-03 模型 B 显示 309 元/㎡ 与规则行 309.08 不一致、case-08 现场记录 10-15 早于开工且交付 12-06 与 65 天工期不符；另修复 r01 记录的 10 项视觉缺陷（KPI 单位叠印、滑杆缺单位、极差列出血、重复列头、报价列空腔、case-07 四处零间距与剖面格子叠印等）。声明纪律：研究未取得既有加装电梯分摊政策原文 -> 不引用法条、不写法定比例、不写补贴标准，金额一律演示数据 DEMO，A/B/C 权重明写为产品自定义规则，未做用户验证不声称已被验证。suite-state B05 -> completed，B06 -> in_progress。"
$evObj = [ordered]@{
  seq = 59; ts = $now; type = 'task_completed'; task = 'B05'
  artifact_scope = "outputs/$run/B05"
  renders_added = 38; views_added = 47; iterations_added = 6; cases_completed = 10
  note = $note
}
[IO.File]::AppendAllText((Join-Path $st 'events.jsonl'), (($evObj | ConvertTo-Json -Compress -Depth 4) + "`n"), $enc)
"  events.jsonl appended seq=59"

# ---- checkpoint state-000035.json ----
$ckpt = [ordered]@{
  checkpoint = 'state-000035.json'; created_at = $now; seq = 59
  run_id = $run; run_profile = 'all'
  suite_state = $ss
}
$cpath = Join-Path $st 'checkpoints\state-000035.json'
[IO.File]::WriteAllText($cpath, ($ckpt | ConvertTo-Json -Depth 14), $enc)
"  checkpoint written  ({0} bytes)" -f (Get-Item $cpath).Length
