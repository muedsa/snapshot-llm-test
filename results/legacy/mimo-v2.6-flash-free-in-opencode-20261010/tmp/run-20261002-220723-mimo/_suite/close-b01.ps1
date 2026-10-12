$root = $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Set-Location $root
$ssPath = "outputs\run-20261002-220723-mimo\_suite\suite-state.json"
$ckDir  = "tmp\run-20261002-220723-mimo\_suite\checkpoints"
$evPath = "tmp\run-20261002-220723-mimo\_suite\events.jsonl"

$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

$old = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
$oldCopy = ($old | ConvertTo-Json -Depth 12) | ConvertFrom-Json

# ---- 1. append events (seq 53, 54) ----
$e1 = [pscustomobject][ordered]@{
  seq = 53
  ts = $now
  type = 'task_completed'
  task = 'B01'
  artifacts = 35
  renders = 22
  views = 24
  visual_iterations = 8
  rounds = 0
  note = 'B01 十张真实场景的炫酷用例完成：10 件独立主作品，每件 final.png + final.snapshot + case.md（30 个文件）+ 根层 portfolio.json / portfolio.md / gallery.html / snapshot-usage.md / task-metrics.json = 35 个产物。10 件画幅 10 种比例无一重复：900x1600 末班地铁到站屏、1920x1080 台风应急指挥板、1080x1440 半马破风配速卡、1200x900 精品咖啡烘焙曲线卡、800x1200 独立乐队霓虹巡演海报、1600x1000 锂电PACK装配工艺指导、1200x1200 围棋棋谱解说图、1080x1080 宠物疫苗接种提醒、1080x1350 潮汐与海泳安全牌、1920x640 社区旧物集市导览横幅；受众、媒介、信息任务与视觉隐喻各不相同，无同版式换色或缩放。全部纯 DSL 经真实服务渲染，PNG 为服务原始字节（签名 89504e470d0a1a0a、colorType=6，IHDR 实读尺寸与声明一致），10 件画面内均标「演示数据 DEMO」。请求 29 行 = 渲染 22（200=20、400=2，两次 400 均为真实 PARSE_ERROR：Transform matrix 缺外层括号）+ 文档 7（200=7），失败 2、重试 2、限流 0（ratelimit_remaining 最低 115），请求耗时之和 101518ms（渲染 91851.4 + 文档 9666.6）。看图 24 次；迭代 22 行（baseline 10 / visual-iteration 8 / visual-iteration-incomplete 1 / syntax-fix 2 / capability-probe 1），完整视觉迭代 8、未完成 1。case-01/06/08 首版即合格不制造无意义迭代；case-08 一次性验证 SWEEP + gradientStops(0/0.75/0.75/1) + startAngle=-pi/2 画出 12 点起顺时针的精确 75% 锥形环。视觉迭代驱动的修复：case-02 风圈不共圆心/路径与 WNW 标注矛盾/标签压线/数值单位粘连/底栏被裁共 5 处；case-03 分段条等分改为按真实里程 0.2378/0.4755/0.7102/0.9460/1.0 累计比例使条尾精确落在终点；case-04 曲线区过矮/标签牌相碰/指标行距不足；case-05 CTA 压二维码；case-07 解说与盘面及结果栏互相矛盾（解说称三三侵角而盘面是小飞挂、黑占D16/Q16非右上右下、白胜1.5目与白中盘胜互斥、41+42.5算不出1.5）后改为自洽数据 黑71/白66+贴6.5=白72.5 白胜1.5 目；case-07 第三轮中文自动换行出现行首标点改 TLines 手动断行，Fit 另报 2 处超宽（448>364、373>364）拆行后 problems=0，用 2x 局部放大图逐行核对；case-09 96 段面积填充抗锯齿接缝用 +1.4px 重叠消除；case-10 中栏右上角说明右边界 1404 超出卡片 1400 被裁，收到 1376。数据一致性自检通过：case-03 分段里程和 = 21.0975km、case-06 扭矩游标落绿带、case-07 19路坐标按 A-T 跳 I 换算且星位 D16/Q16/D4/Q4 与天元 K10 正确、case-09 曲线极值与潮时表一致、case-10 席位 12+14+10+12=48 与统计区一致。环境限制如实记录：browser.preview 不可用（浏览器会话断开）；读图工具对同一路径返回旧缓存字节 5 次，导致 ite-B01-c07-v3 成为 1 次未完成迭代，已用唯一文件名副本与局部放大补看（副本 view-check.png / zoom-07.png / view-171022.png / v09-*.png / v10-*.png 全部留档）。token / 图像用量 / 费用平台未提供，task-metrics.json 记 null。墙钟 6053.804s。'
}
$e2 = [pscustomobject][ordered]@{
  seq = 54
  ts = $now
  type = 'task_started'
  task = 'B02'
  note = 'B02 开始（B 类第 2 题，仍要求 >=10 件独立完整作品，沿用同一 run_id 的 outputs/<run_id>/B02/ 与 tmp/<run_id>/B02/）。可复用 B01 已验证的 lib-b01.ps1 设计构件（Fit 宽度校验、TLines 手动断行、matrix 外层括号、BD border 前缀、SWEEP 停点环、唯一文件名规避读图缓存），但 B01 的成品不得重复计数。'
}

$enc = New-Object System.Text.UTF8Encoding($false)
$lines = @()
foreach ($e in @($e1, $e2)) { $lines += ($e | ConvertTo-Json -Compress -Depth 6) }
[IO.File]::AppendAllLines((Join-Path (Get-Location) $evPath), [string[]]$lines, $enc)
"events appended: 2 (seq 53, 54); total = " + (Get-Content $evPath).Count

# ---- 2. update suite-state.json ----
$artifacts = @(
  'outputs/run-20261002-220723-mimo/B01/portfolio.json',
  'outputs/run-20261002-220723-mimo/B01/portfolio.md',
  'outputs/run-20261002-220723-mimo/B01/gallery.html',
  'outputs/run-20261002-220723-mimo/B01/snapshot-usage.md',
  'outputs/run-20261002-220723-mimo/B01/task-metrics.json',
  'outputs/run-20261002-220723-mimo/B01/case-01/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-01/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-01/case.md',
  'outputs/run-20261002-220723-mimo/B01/case-02/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-02/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-02/case.md',
  'outputs/run-20261002-220723-mimo/B01/case-03/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-03/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-03/case.md',
  'outputs/run-20261002-220723-mimo/B01/case-04/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-04/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-04/case.md',
  'outputs/run-20261002-220723-mimo/B01/case-05/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-05/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-05/case.md',
  'outputs/run-20261002-220723-mimo/B01/case-06/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-06/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-06/case.md',
  'outputs/run-20261002-220723-mimo/B01/case-07/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-07/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-07/case.md',
  'outputs/run-20261002-220723-mimo/B01/case-08/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-08/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-08/case.md',
  'outputs/run-20261002-220723-mimo/B01/case-09/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-09/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-09/case.md',
  'outputs/run-20261002-220723-mimo/B01/case-10/final.png',
  'outputs/run-20261002-220723-mimo/B01/case-10/final.snapshot',
  'outputs/run-20261002-220723-mimo/B01/case-10/case.md'
)
$cases = @('case-01','case-02','case-03','case-04','case-05','case-06','case-07','case-08','case-09','case-10')
$evidence = @(
  'outputs/.../B01/case-01/final.png  900x1600（读图工具实际查看，B01-c01-r1，236495 B）：末班 23:47 / 发车 23:52 与站台方向自洽，四级信息层级在缩略图下仍可辨认，底部备注未越界，首版即合格未做修改',
  'outputs/.../B01/case-02/final.png  1920x1080（读图工具查看 r1 与 r3 两次，253946 B）：r1 发现风圈不共圆心、路径与 WNW 标注矛盾、标签牌压线、FORCES 数值与单位粘连、底栏被裁共 5 处；r3 复看 5 处全部消失',
  'outputs/.../B01/case-03/final.png  1080x1440（读图工具查看 r2 与 r3，r1 为 400，220595 B）：r2 发现 5 段进度条等分导致条尾不落轨道终点；r3 按真实累计里程比例 0.2378/0.4755/0.7102/0.9460/1.0 重算后条尾精确落在 x=850',
  'outputs/.../B01/case-04/final.png  1200x900（读图工具查看 r1 与 r3，155756 B）：r1 发现曲线区过矮压住 6:00 刻度、3 个节点标签牌相碰并压曲线、指标行距不足粘连；r3 复看全部解决',
  'outputs/.../B01/case-05/final.png  800x1200（读图工具查看 r2 与 r3，r1 为 400，245259 B）：r2 发现「扫码购票」压住二维码右上角；r3 把 CTA 移到 (520,992) 右对齐后两者各自留白',
  'outputs/.../B01/case-06/final.png  1600x1000（读图工具查看 r1，274436 B）：5 张步骤卡行距一致徽标居中、扭矩白游标落在绿带内且与 6.2-6.8 刻度一致、拧紧顺序 1-2-3-4-5 连线与编号正确、页脚未越界，首版即合格',
  'outputs/.../B01/case-07/final.png  1200x1200（读图工具查看 r1、r2 + 2x 局部放大 zoom-07.png 查看 r4，239177 B）：r1 发现解说与盘面（三三侵角 vs 小飞挂、黑占右上右下 vs 实际 D16/Q16）及结果栏（白胜1.5目 vs 白中盘胜、41+42.5 算不出 1.5）互相矛盾；r2 改为自洽数据 黑71/白66+贴6.5=白72.5 白胜1.5 目、条形 201:187 后内容自洽但出现行首标点；r3 改 TLines 后 Fit 报 2 处超宽 448>364 与 373>364，该版本未能取得有效看图（读图缓存）记为未完成迭代；r4 拆行后 problems=0，2x 放大图逐行核对三段各 3 行、行首无标点、无溢出、结果自洽',
  'outputs/.../B01/case-08/final.png  1080x1080（读图工具查看 r1，179866 B）：75% 弧起于 12 点收于 9 点、gradientStops 分段精确，环内「3/4」与说明居中未越出镂空圆，两张接种卡与 2x2 注意事项对齐无遮挡，首版即合格',
  'outputs/.../B01/case-09/final.png  1080x1350（读图工具查看 r1 与唯一命名副本 v09-171103038.png 查看 r2，191533 B）：r1 发现 96 段独立矩形拼接的面积填充有可见抗锯齿竖缝；r2 填充块 +1.4px 相互重叠后成为连续色块，极值标签、红点红线、轴标签均正确',
  'outputs/.../B01/case-10/final.png  1920x640（读图工具查看 r1 与唯一命名副本 v10-171300210.png 查看 r2，189776 B）：r1 发现中栏右上角「北门在上 · 南门在下」文本框右边界 1404 超出卡片 1400 被裁；r2 改为 (1060,66,316,28) 右边界 1376 后完整，三栏边界清晰、席位 12+14+10+12=48 与统计区一致',
  'portfolio.json.final_collection_review  五项最终审查全过：完整性（10 组 png/snapshot/case.md 齐全、PNG 服务原始字节、IHDR 尺寸与声明一致）、独立性（10 种画幅比例无重复）、数据一致性（里程/坐标/目数/潮位/席位可验算）、可见性（10 件均标演示数据 DEMO）、留痕（22 渲染请求 + 2 个 400 响应体 + attempts 目录 + 三个 jsonl）',
  'tmp/.../B01/iterations.jsonl  22 行（baseline 10 / visual-iteration 8 / visual-iteration-incomplete 1 / syntax-fix 2 / capability-probe 1），完整视觉迭代 8、未完成 1（ite-B01-c07-v3 因读图缓存未取得有效查看），看图 24 次',
  'tmp/.../B01/requests.jsonl  29 行 = 渲染 22（200=20、400=2 真实 PARSE_ERROR：Transform matrix 缺外层括号）+ 文档 7（200=7），重试 2、限流 0（ratelimit_remaining 最低 115），请求耗时之和 101518ms，两次 400 响应体分别留档在 case-03/case-05 的 attempts/v1/failures/'
)
$unresolved = @(
  '无阻塞项：B01 已 completed，10/10 件独立主作品渲染成功、逐件实际查看并复看通过，35 个产物齐全',
  'browser.preview 在本环境不可用（浏览器会话断开），全程用直接打开图片文件的方式查看；此为环境限制，不影响交付',
  '读图工具对已读过的同一路径会返回旧缓存字节（本题 5 次），已用唯一文件名副本与 2x 局部放大补看并全部留档；该问题导致 ite-B01-c07-v3 成为 1 次未完成迭代，已在 iterations.jsonl 如实标注，最终版本 r4 的查看结果有效',
  '逐次看图的精确时间戳未被工具记录（读图调用不产生时间戳），iterations.jsonl 以 viewed 布尔值 + 查看证据文件记录，顺序可由渲染结束时间与 attempts 归档文件推断，不编造具体时刻',
  'token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明原因，不用字数或账号余量估造',
  '排队等待无法测量（服务未返回排队指标），记 null'
)
$resume = 'completed；无阻塞，可继续 B02。请求 29 行串行（渲染 22：200=20、400=2；文档 7：200=7），0 限流 0 排队，请求耗时之和 101518ms（渲染 91851.4 + 文档 9666.6），首张可用图 194.354s、首张用例图 1252.303s。看图 24 次（其中 5 次读图缓存已用唯一文件名副本补看）；迭代 22 行，完整视觉迭代 8、未完成 1、语法修复 2。交付 35 个产物，10 张 PNG 服务原始字节无后处理、10 种画幅比例无重复。数据自检：case-03 里程和 21.0975km、case-06 扭矩游标落绿带、case-07 19 路坐标与 目数+贴目=分差 自洽、case-09 极值与潮时表一致、case-10 席位 12+14+10+12=48。墙钟 6053.804s。可复用 lib-b01.ps1 的 Fit/TLines/matrix 外层括号/BD 前缀/SWEEP 停点环设计构件，但成品不得重复计数。'

$b01 = $null
$b02 = $null
foreach ($t in $old.tasks) { if ($t.id -eq 'B01') { $b01 = $t }; if ($t.id -eq 'B02') { $b02 = $t } }
if ($null -eq $b01) { throw 'B01 task entry not found' }
if ($null -eq $b02) { throw 'B02 task entry not found' }

$b01.status = 'completed'
$b01.ended_at = $now
$b01.output_dir = 'outputs/run-20261002-220723-mimo/B01/'
$b01.temp_dir = 'tmp/run-20261002-220723-mimo/B01/'
$b01.completed_cases = $cases
$b01.artifacts = $artifacts
$b01.visual_review_evidence = $evidence
$b01.unresolved_issues = $unresolved
$b01.resume_notes = $resume

$b02.status = 'in_progress'
$b02.started_at = $now
$b02.output_dir = 'outputs/run-20261002-220723-mimo/B02/'
$b02.temp_dir = 'tmp/run-20261002-220723-mimo/B02/'

$ckPathRel = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000030.json'
$old.updated_at = $now
$old.current_task = 'B02'
$old.last_checkpoint = $ckPathRel

$ssJson = $old | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText((Join-Path (Get-Location) $ssPath), $ssJson, $enc)
"suite-state.json updated"

# ---- 3. checkpoint state-000030.json ----
$counts = @()
foreach ($st in @('completed','in_progress','pending','partial','blocked')) {
  $n = @($old.tasks | Where-Object { $_.status -eq $st }).Count
  $counts += [pscustomobject][ordered]@{ status = $st; count = $n }
}
$doneIds = @($old.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
$inProg  = (@($old.tasks | Where-Object { $_.status -eq 'in_progress' } | ForEach-Object { $_.id }) -join ',')
if ([string]::IsNullOrEmpty($inProg)) { $inProg = 'B02' }

$note = 'B01 关闭（events 53），B02 开启（events 54）。B01：35 个产物 = 10 x (final.png + final.snapshot + case.md) + portfolio.json + portfolio.md + gallery.html + snapshot-usage.md + task-metrics.json。10 件画幅 10 种比例无一重复（900x1600 / 1920x1080 / 1080x1440 / 1200x900 / 800x1200 / 1600x1000 / 1200x1200 / 1080x1080 / 1080x1350 / 1920x640），受众、媒介、信息任务与视觉隐喻各不相同，无同版式换色或缩放。全部纯 DSL 真实渲染，PNG 服务原始字节（IHDR 实读尺寸与声明一致、colorType=6），10 件画面内均标「演示数据 DEMO」。请求 29 行 = 渲染 22（200=20、400=2 真实 PARSE_ERROR：Transform matrix 缺外层括号）+ 文档 7（200=7），失败 2、重试 2、限流 0（ratelimit_remaining 最低 115），请求耗时之和 101518ms（渲染 91851.4 + 文档 9666.6）。看图 24 次；迭代 22 行 = baseline 10 / visual-iteration 8 / visual-iteration-incomplete 1 / syntax-fix 2 / capability-probe 1，完整视觉迭代 8、未完成 1。case-01/06/08 首版即合格未制造无意义迭代；case-08 首次验证 SWEEP + gradientStops + startAngle=-pi/2 即画出精确 75% 锥形环。视觉迭代修复要点：case-02 共 5 处（风圈共圆心 510,340 / 路径改 WNW 序列 / 标签牌移位 / FORCES 单位改 1420+TW+10 / 底板 h=326）；case-03 分段条从等分改按真实里程累计比例使条尾精确落 x=850；case-04 曲线区 cy0=200 chh=324、标签牌移位、指标 y=198+i*92；case-05 CTA 移到 (520,992)；case-07 解说与结果栏内容矛盾全部改写为自洽（黑71/白66+贴6.5=白72.5 白胜1.5 目、条形 201:187）、行首标点改 TLines、Fit 报 2 处超宽拆行后 problems=0；case-09 面积填充 +1.4px 重叠消接缝；case-10 文本框右边界 1404->1376。数据自检：case-03 分段里程和 = 21.0975km、case-06 扭矩游标落绿带、case-07 19 路坐标按 A-T 跳 I 换算且星位 D16/Q16/D4/Q4 与天元 K10 正确、case-09 曲线极值与潮时表一致、case-10 席位 12+14+10+12=48 与统计区一致。环境限制：browser.preview 不可用；读图工具同路径旧缓存 5 次，导致 ite-B01-c07-v3 记为未完成迭代，已用唯一文件名副本与 2x 放大补看留档。token / 图像 / 费用记 null。suite-state.json 中 B01=completed、current_task=B02、B02=in_progress。'

$ck = [pscustomobject][ordered]@{
  schema_version = 1
  suite_version = '1.0.0'
  run_id = 'run-20261002-220723-mimo'
  profile = 'all'
  status = 'in_progress'
  snapshot_at = $now
  checkpoint_id = 'state-000030'
  checkpoint_seq = 30
  event_seq = 54
  current_task = 'B02'
  current_status = 'in_progress'
  last_checkpoint = $ckPathRel
  task_status_counts = $counts
  tasks_completed = $doneIds
  tasks_in_progress = $inProg
  checkpoint_note = $note
  suite_state = $old
  source_state_copy = $oldCopy
}
$ckJson = $ck | ConvertTo-Json -Depth 14
$ckPath = Join-Path (Get-Location) "$ckDir\state-000030.json"
[IO.File]::WriteAllText($ckPath, $ckJson, $enc)
"checkpoint written: $ckPath"

# ---- verify ----
$v = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
$sB01 = ($v.tasks | Where-Object { $_.id -eq 'B01' }).status
$sB02 = ($v.tasks | Where-Object { $_.id -eq 'B02' }).status
"verify: B01=$sB01  B02=$sB02  current_task=$($v.current_task)  last_checkpoint=$($v.last_checkpoint)"
$grp = $v.tasks | Group-Object status | ForEach-Object { "$($_.Name)=$($_.Count)" }
"verify counts: " + ($grp -join ' ')
$vc = Get-Content "$ckDir\state-000030.json" -Raw -Encoding UTF8 | ConvertFrom-Json
"verify checkpoint: seq=$($vc.checkpoint_seq) event_seq=$($vc.event_seq) current=$($vc.current_task) completed=$($vc.tasks_completed.Count) inprog=$($vc.tasks_in_progress) artifacts=$($vc.suite_state.tasks | Where-Object {$_.id -eq 'B01'} | ForEach-Object {$_.artifacts.Count})"
