$root = $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Set-Location $root
$ssPath = "outputs\run-20261002-220723-mimo\_suite\suite-state.json"
$ckDir  = "tmp\run-20261002-220723-mimo\_suite\checkpoints"
$evPath = "tmp\run-20261002-220723-mimo\_suite\events.jsonl"

$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

$old = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
$oldCopy = ($old | ConvertTo-Json -Depth 12) | ConvertFrom-Json   # deep clone BEFORE mutation

# ---- 1. append events (seq 51, 52) ----
$e1 = [pscustomobject][ordered]@{
  seq = 51
  ts = $now
  type = 'task_completed'
  task = 'A24'
  artifacts = 11
  renders = 8
  views = 6
  visual_iterations = 1
  rounds = 0
  note = 'A24 双团队约束下的发布作战计划完成：11 个产物 = 3 组 PNG+DSL（execution-board 1920x1080、decision-brief 1200x1600、action-card 720x1280）+ schedule.json + schedule-audit.json + content-map.json + snapshot-usage.md + task-metrics.json，全部指定交付齐全，生成器 problems = 0。排程由 sched-a24.ps1 自算：总工时 485 分钟、忽略资源的关键路径 255 分钟（R01->R04->R07->R09->R10->R12）、两团队均分下界 243、最佳团队负载下界 245、资源感知下界 260，候选 makespan 260 分钟即下界，故有可核验的完整情形枚举证明（schedule-audit.json optimality.proven = true），完成 13:20、缓冲 160 分钟、窗口 420 分钟；design = R01/R04/R07/R09/R10/R12（忙碌 255）、engineering = R02/R05/R03/R06/R08/R11（忙碌 230），R05/R09/R12 三个 teams 两项的任务均二选一未占用两团队。7 项校验全部 PASS、problems = 0：团队资格、完整时长 12/12 一致、16 条依赖边先后关系、泳道 0 冲突、全部落在 09:00-16:00、无抢占、最优性。三图全部从 schedule.json 读数不各自硬编码，一致性复核：完成 13:20 / 260 分钟 / 缓冲 160 / 总工时 485 / 关键路径 255 与 6 个关键任务 / 12 项团队归属，三处完全一致。执行图时间轴 1884px/420min = 4.485714 px/min 等比绘制，含 3 段斜纹空档（design 12:20-12:25、engineering 09:20-09:25、engineering 12:55-13:20 standby）、绿色 13:20 完成线、红色虚线 16:00 截止线与缓冲带；简报含 5 指标卡、6 层依赖分层 + 显式 16 条依赖边两行、排程依据 5 条、3 条风险与对策，footerY 1516/1538；手机卡 12 项按 (start,id) 排序，含团队胶囊、起止、时长与关键路径标记、3 条风险提醒，footerY 1248/1254。正文最小字号 20/24/20 分别满足 >=20 / >=24 / >=20；三张图 0 个 <Image>、0 个 svg/gif/cmyk。请求 17 行 = 渲染 8（200=6、400=2，两次 400 是真实的 PARSE_ERROR：布尔值 false 拼进 color 产生字面量 False、以及 color 只含空格）+ 文档 9（200=7、403=1、404=1），失败 4、重试 2、限流 0（ratelimit_remaining 117..119），请求耗时之和 53159.1ms，收到渲染 2055748 字节 + 文档 430930 字节。看图 6 次（v02 三张 + v03 三张，全部真实像素）。迭代 3 行（baseline 1 / visual 1 / syntax-fix 1），完整视觉迭代 1：看 v02 发现依赖总览缺显式依赖边、分层内顺序非 id 序、无前驱标注写成「起始」、卡片团队胶囊顶边、以及 TW() 估算器因 PowerShell -match 大小写不敏感把小写字母按 0.70em 计的假阳性 bug，逐条修复后重渲染并再看确认。交付级数据缺陷已修：首版 schedule.json 的 brand 为 null（inputs/release.json 无 brand 字段），补齐为题面品牌并加 brand_source，重新生成后与首版仅 generated_at/brand/brand_source 三行不同、12 任务数据逐字节一致，重生成的三份 DSL 与交付 .snapshot 逐字节相同故未重渲染、PNG 未触碰，首版 JSON 归档 attempts/v1-schedule/。过程偏差如实记录：A24-doc-002(403) 与 A24-doc-004(404) 的响应正文被后续同名成功请求覆盖无法恢复（URL/状态/字节数仍在 requests.jsonl），两次 400 共用 failures/A24-r1-board.body（两次 error_summary 均在日志独立成行）。token / 图像输入 / 费用平台未提供，task-metrics.json 记 null。墙钟 5565s。'
}
$e2 = [pscustomobject][ordered]@{
  seq = 52
  ts = $now
  type = 'task_started'
  task = 'B01'
  note = 'B01 开始（B 类首题，B01-B06 各至少 10 件独立完整作品，可复用已学知识与设计构件，但前题成品不得重复计数）。沿用同一 run_id 的 outputs/<run_id>/B01/ 与 tmp/<run_id>/B01/，按 catalog.json 顺序推进。'
}

$enc = New-Object System.Text.UTF8Encoding($false)
$lines = @()
foreach ($e in @($e1, $e2)) { $lines += ($e | ConvertTo-Json -Compress -Depth 6) }
[IO.File]::AppendAllLines((Join-Path (Get-Location) $evPath), [string[]]$lines, $enc)
"events appended: 2 (seq 51, 52); total = " + (Get-Content $evPath).Count

# ---- 2. update suite-state.json ----
$artifacts = @(
  'outputs/run-20261002-220723-mimo/A24/execution-board.png',
  'outputs/run-20261002-220723-mimo/A24/execution-board.snapshot',
  'outputs/run-20261002-220723-mimo/A24/decision-brief.png',
  'outputs/run-20261002-220723-mimo/A24/decision-brief.snapshot',
  'outputs/run-20261002-220723-mimo/A24/action-card.png',
  'outputs/run-20261002-220723-mimo/A24/action-card.snapshot',
  'outputs/run-20261002-220723-mimo/A24/schedule.json',
  'outputs/run-20261002-220723-mimo/A24/schedule-audit.json',
  'outputs/run-20261002-220723-mimo/A24/content-map.json',
  'outputs/run-20261002-220723-mimo/A24/snapshot-usage.md',
  'outputs/run-20261002-220723-mimo/A24/task-metrics.json'
)
$evidence = @(
  'outputs/run-20261002-220723-mimo/A24/execution-board.png  交付件 1920x1080（本地读取）：12 个任务块齐全，design 泳道 R01/R04/R07/R09/R10/R12、engineering 泳道 R02/R05/R03/R06/R08/R11；每块 4 行（编号 fs24 BOLD、标签 fs20、起止 fs20、前驱 fs20）可读，R01/R02 显示「无前驱」；3 段斜纹空档与 engineering 12:55-13:20 待命段可见；绿色 13:20 完成线、红色虚线 16:00 截止线、两条缓冲带、图例 4 行、4 张指标卡、关键路径页脚全部到位；紧凑文本框无竖向裁切；正文最小字号 20',
  'outputs/run-20261002-220723-mimo/A24/decision-brief.png  交付件 1200x1600（本地读取）：5 张指标卡（总工时 485 / 两团队均分下界 243 / 资源感知下界 260 / 关键路径 255 / 完成 13:20 · 260 分钟 · 缓冲 160）；依赖总览 6 层 + 显式 16 条依赖边两行（R03<-R02、R04<-R01、R05<-R01、R06<-R03、R07<-R04,R05 / R08<-R04,R06、R09<-R07、R10<-R07,R08,R09、R11<-R08,R09、R12<-R10,R11）+ 图例；排程依据 5 条含 ceil(485/2)=242.5->243 等算式；K1/K2/K3 三条风险与对策；页脚 1516/1538；正文最小字号 24',
  'outputs/run-20261002-220723-mimo/A24/action-card.png  交付件 720x1280（本地读取）：状态条三段（13:20 · 260 分钟 / 缓冲 160 分钟 -> 16:00 / 485 分钟 · 12 项）；12 行按 (start_min,id) 排序 R01->R02->R04->R05->R03->R07->R06->R08->R09->R10->R11->R12，每行含起止、任务名、团队胶囊（留白约 10px）、时长与「关键路径/普通」标记；3 条风险提醒；页脚 1248/1254；正文最小字号 20',
  'tmp/run-20261002-220723-mimo/A24/attempts/v1/execution-board.png + decision-brief.png + action-card.png  改前的首轮三张图（本地读取）：内容正确，但据此发现 5 个真实问题 —— 简报依赖总览只有分层没有显式依赖边、分层内顺序是结束时间序而非 id 序、执行图无前驱块写「起始」与图例「前驱编号」语义不符、卡片团队胶囊 130px 让 engineering 顶边、以及 TW() 宽度估算器把小写字母按 0.70em 计的假阳性 bug。三张已整体归档未被覆盖',
  'schedule-audit.json  7 项校验全部 PASS、problems = 0：team_eligibility、full_duration（12/12 与 inputs 完全一致、0 缩时 0 删检查）、precedence（16 条边）、no_lane_overlap（conflicts = 0）、inside_window（0..420）、no_preemption、optimality（下界 260 = 候选 260）；duration_checks.all_equal = true',
  'schedule-audit.json optimality  可核验的完整情形枚举证明（proven = true）：枚举全部 8 个可分配任务的团队归属 + 每种归属下工程线相对固定链 R02<R03<R06 的合法排序，解析侧证为 makespan >= max(g+120, max(85,f)+170)，R05-on-design >= 285、R05-on-eng 恰 4 种合法排序最小 260 = 候选，故 260 全局最优；题面不强制证明，因有此可核验证明才在三图写「最优」',
  'schedule.json  首版 brand = null（inputs/release.json 根本没有 brand 键）已按题面补齐为「叠光 · 发布演练」并新增 brand_source；重新生成后与归档首版逐行比对只有 generated_at/brand/brand_source 三行不同、12 任务的起止/团队/依赖/下界/缓冲逐字节一致；用新 schedule.json 重生成的三份 DSL 与交付 .snapshot 逐字节相同（33173 / 19016 / 21740 B），故未重渲染、三张 PNG 未被触碰；首版归档 tmp/.../A24/attempts/v1-schedule/',
  'content-map.json  三图共用事实与 cross_image_rules：所有数字从 schedule.json 读取禁止各自硬编码；完成 13:20 / 260 分钟 / 缓冲 160 分钟三图一致；12 项团队归属三图一致（执行图泳道、简报色条、卡片胶囊）',
  'gen-a24.ps1  参数化生成三份 DSL；problems = 0 的护栏：12/12 块标签与前驱零溢出、依赖边 covered == edgeCount == 16 且恰 2 行每行 TW <= 1104、brief footerY 1516 <= 1538、card footerY 1248 <= 1254、团队胶囊文字宽 + 16 <= 144、三图最小正文字号 20/24/20',
  'iterations.jsonl  3 行（baseline 1 / visual 1 / syntax-fix 1），完整视觉迭代 1（a24-v03：看 v02 三图 -> 改 5 处 -> 重渲染 -> 再看并比较），看图 6 次，v01 两次 400 无图如实记录',
  'requests.jsonl  17 行 = 渲染 8（200=6、400=2）+ 文档 9（200=7、403=1、404=1），重试 2、限流 0（ratelimit_remaining 117..119），请求耗时之和 53159.1ms（渲染 35685.5 + 文档 17473.6），收到 2486678 字节',
  'snapshot-usage.md + task-metrics.json  11/11 指定交付、三图逐张看图通过、正文最小字号 20/24/20、0 个 <Image>、过程偏差（2 个文档错误响应正文被同名请求覆盖）与未解决事项逐条列明'
)
$unresolved = @(
  '无阻塞项：A24 已 completed，generator problems = 0，11/11 指定交付齐全，三张最终 PNG 逐张看图通过',
  '过程偏差：A24-doc-002（403）与 A24-doc-004（404）的响应正文分别被 A24-doc-005 / A24-doc-006 的同名文件覆盖，正文无法恢复；两次访问的 URL、状态码、字节数、耗时仍在 requests.jsonl 完整保留。同类问题：两次 400 渲染共用 failures/A24-r1-board.body，但两次的 error_summary 在日志各自成行，可完整追溯',
  '看图的精确单次时刻未采集，iterations.jsonl 以 viewed_at_basis 记录可证明的时间窗（渲染结束 -> 下一次渲染开始），不编造具体时刻',
  'token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明原因，不用字数或账号余量估造',
  '首版 schedule.json 的 brand 为 null 属交付级数据缺陷，已修复并归档旧版；修复后 DSL 逐字节未变、PNG 未触碰'
)
$resume = 'completed；无阻塞，可继续 B01。17 个请求全串行（渲染 8：200=6、400=2；文档 9：200=7、403=1、404=1），0 限流 0 排队，请求耗时之和 53159.1ms，收到渲染 2055748 字节 + 文档 430930 字节。看图 6 次；迭代 3 行（baseline 1 / visual 1 / syntax-fix 1），完整视觉迭代 1。交付 11 个产物，三张 PNG 服务原始字节无后处理，SHA-256 前缀 98910CC19CFD0E12 / 55C764E3A6965829 / 7510ECEF46BAC7FE。排程 260 分钟、完成 13:20、缓冲 160、关键路径 255，最优性有可核验枚举证明。墙钟 5565s。'

$a24 = $null
foreach ($t in $old.tasks) { if ($t.id -eq 'A24') { $a24 = $t } }
if ($null -eq $a24) { throw 'A24 task entry not found' }
$a24.status = 'completed'
$a24.ended_at = $now
$a24.output_dir = 'outputs/run-20261002-220723-mimo/A24/'
$a24.temp_dir = 'tmp/run-20261002-220723-mimo/A24/'
$a24.artifacts = $artifacts
$a24.visual_review_evidence = $evidence
$a24.unresolved_issues = $unresolved
$a24.resume_notes = $resume

$ckPathRel = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000029.json'
$old.last_checkpoint = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000028.json'
$old.updated_at = $now
$old.current_task = 'B01'
$old.last_checkpoint = $ckPathRel

$ssJson = $old | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText((Join-Path (Get-Location) $ssPath), $ssJson, $enc)
"suite-state.json updated"

# ---- 3. checkpoint state-000029.json ----
$counts = @()
foreach ($st in @('completed','in_progress','pending','partial','blocked')) {
  $n = @($old.tasks | Where-Object { $_.status -eq $st }).Count
  $counts += [pscustomobject][ordered]@{ status = $st; count = $n }
}
$doneIds = @($old.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
$inProg  = (@($old.tasks | Where-Object { $_.status -eq 'in_progress' } | ForEach-Object { $_.id }) -join ',')
if ([string]::IsNullOrEmpty($inProg)) { $inProg = 'B01' }

$note = 'A24 关闭（events 51），B01 开启（events 52）。A24：11 个产物 = 3 组 PNG+DSL（execution-board 1920x1080 359450 B、decision-brief 1200x1600 404335 B、action-card 720x1280 270676 B）+ schedule.json + schedule-audit.json + content-map.json + snapshot-usage.md + task-metrics.json，全部指定交付齐全、生成器 problems = 0。排程自算：总工时 485、忽略资源的关键路径 255（R01->R04->R07->R09->R10->R12）、两团队均分下界 243、最佳团队负载下界 245、资源感知下界 260，候选 260 = 下界故有可核验的完整情形枚举证明（optimality.proven = true），完成 13:20、缓冲 160、窗口 420；design = R01/R04/R07/R09/R10/R12（255）、engineering = R02/R05/R03/R06/R08/R11（230），R05/R09/R12 三个 teams 两项的任务二选一未占两团队。7 项校验全 PASS、problems = 0。三图共用 schedule.json 单一数据源，一致性复核完成 13:20 / 260 / 缓冲 160 / 总工时 485 / 关键路径 255 与 6 任务 / 12 项团队归属三处一致。执行图 4.485714 px/min 等比时间轴 + 3 段斜纹空档 + 绿色 13:20 完成线 + 红色虚线 16:00 截止线 + 缓冲带；简报 5 指标卡 + 6 层分层 + 显式 16 条依赖边两行 + 排程依据 5 条 + 3 风险对策（footerY 1516/1538）；手机卡 12 项时间序 + 团队 + 起止 + 风险提醒（footerY 1248/1254）。正文最小字号 20/24/20 满足 >=20/>=24/>=20；0 <Image>、0 svg/gif/cmyk。请求 17 行（渲染 8：200=6、400=2 两次真实 PARSE_ERROR；文档 9：200=7、403=1、404=1），失败 4、重试 2、限流 0（ratelimit_remaining 117..119），请求耗时之和 53159.1ms，收到 2486678 字节。看图 6 次；迭代 3 行（baseline 1 / visual 1 / syntax-fix 1），完整视觉迭代 1。交付级缺陷已修：首版 schedule.json brand = null（inputs 无 brand 键）补齐为题面品牌，重生成后仅 3 行差异、重生成 DSL 与交付 .snapshot 逐字节相同故未重渲染，首版 JSON 归档 attempts/v1-schedule/。过程偏差：2 个文档错误响应正文被同名成功请求覆盖无法恢复（URL/状态/字节数仍在 requests.jsonl）。token / 图像输入 / 费用记 null。suite-state.json 中 A24=completed、current_task=B01。'

$ck = [pscustomobject][ordered]@{
  schema_version = 1
  suite_version = '1.0.0'
  run_id = 'run-20261002-220723-mimo'
  profile = 'all'
  status = 'in_progress'
  snapshot_at = $now
  checkpoint_id = 'state-000029'
  checkpoint_seq = 29
  event_seq = 52
  current_task = 'B01'
  current_status = 'pending'
  last_checkpoint = $ckPathRel
  task_status_counts = $counts
  tasks_completed = $doneIds
  tasks_in_progress = $inProg
  checkpoint_note = $note
  suite_state = $old
  source_state_copy = $oldCopy
}
$ckJson = $ck | ConvertTo-Json -Depth 14
$ckPath = Join-Path (Get-Location) "$ckDir\state-000029.json"
[IO.File]::WriteAllText($ckPath, $ckJson, $enc)
"checkpoint written: $ckPath"

# ---- verify ----
$v = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
$sA24 = ($v.tasks | Where-Object { $_.id -eq 'A24' }).status
$counts2 = @{}
foreach ($t in $v.tasks) { $counts2[$t.status] = 1 + $(if ($counts2.ContainsKey($t.status)) { $counts2[$t.status] } else { 0 }) }
"verify: A24=$sA24  current_task=$($v.current_task)  last_checkpoint=$($v.last_checkpoint)"
"verify counts: " + (($counts2.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ')
$vc = Get-Content "$ckDir\state-000029.json" -Raw -Encoding UTF8 | ConvertFrom-Json
"verify checkpoint keys: " + ($vc.PSObject.Properties.Name -join ', ')
"verify checkpoint: seq=$($vc.checkpoint_seq) event_seq=$($vc.event_seq) current=$($vc.current_task) completed=$($vc.tasks_completed.Count) inprog=$($vc.tasks_in_progress)"
