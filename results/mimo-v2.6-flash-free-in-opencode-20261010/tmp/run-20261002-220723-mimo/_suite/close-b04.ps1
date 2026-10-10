# close-b04.ps1 -- B04 -> completed, B05 -> in_progress, append event + checkpoint
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
 "outputs/$run/B04/portfolio.json"
 "outputs/$run/B04/portfolio.md"
 "outputs/$run/B04/gallery.html"
 "outputs/$run/B04/sources.json"
 "outputs/$run/B04/editorial-note.md"
 "outputs/$run/B04/snapshot-usage.md"
 "outputs/$run/B04/task-metrics.json"
)
foreach ($i in 1..10) {
  $c = 'case-{0:d2}' -f $i
  $art += "outputs/$run/B04/$c/final.png"
  $art += "outputs/$run/B04/$c/final.snapshot"
  $art += "outputs/$run/B04/$c/case.md"
}

$evidence = @(
 "outputs/.../B04/case-01/final.png  1080x1528 184223 B（读图工具实际查看，r02）：60 个等高灰刻度 + 第 61 个琥珀刻度单独加高，首版的递增高度（视觉上暗示秒越走越长）已消除；说明文字由生造词「闰接日」改为「6 月 30 日或 12 月 31 日」；统计块 −37 s 使用真减号 U+2212；刊头与编辑部署名带 DEMO",
 "outputs/.../B04/case-02/final.png  1748x760 181385 B（读图工具查看，r02）：卡片 3 小标题由语义错误的「模型频率固定」改为「铯频率固定」；卡片 2/3 正文重排后不再把全角冒号断到行首、句号齐全；五张卡片的年份 1820/1967/2018/2022/2026·2030 与决议 5 原文逐条对上",
 "outputs/.../B04/case-03/final.png  1920x1080 203526 B（读图工具查看，r02）：TAI 线末端的青色实心矩形（原拟作箭头）已换成 → 字形；UT1 波形由 5x4 离散小方块改为跨样本连续平滑曲线，串珠感消失；SCALE FREE 标注与 0.9 秒引述框均在",
 "outputs/.../B04/case-04/final.png  1200x1600 200127 B（读图工具查看 r02 与 r03 两次）：27 行数据逐行复核与日期差一致（184/365/366/547/2557/1096/1277/1095/550），末行 2016-12-31 / MJD 57754 / 37 s 加琥珀底纹与左侧色条；r03 补口径「MJD 为生效首日」消除 MJD 列歧义",
 "outputs/.../B04/case-05/final.png  1100x1500 160657 B（读图工具查看，r02）：按十年图表标题上移、基线下移，9 轴标签与标题不再重叠；年份矩阵补 72-82/83-93/94-04/05-15/16-26 行区间标签并右移让位；图例由两个同色圆点改为绘制的琥珀实心点与灰色空心点两组色块",
 "outputs/.../B04/case-06/final.png  1080x1080 166079 B（读图工具查看，r02）：0.1 秒细梳齿由 2x2 暗点改为 2x14 可见刻度并加轴线，caption 提到的灰色刻度现在读得出来；琥珀整数刻度明显高出，两级刻度关系清楚",
 "outputs/.../B04/case-07/final.png  1920x480 81701 B（读图工具查看，r02）：61 格刻度由递增改为等长，第 61 个琥珀刻度单独加高；新增 :00 :10 :20 :30 :40 :50 刻度标签；与实际位置相差约 320px 的 23:59:59 标签已删除并重写底部说明",
 "outputs/.../B04/case-08/final.png  1400x1050 109040 B（读图工具查看，r02）：平均 625 天标签由图表右端移到左侧空白处，不再压在最高柱体上；2 557 天红柱标签、184/625/2557 三个统计格与 26 根柱的数值逐根核对一致",
 "outputs/.../B04/case-09/final.png  800x2000 234822 B（读图工具查看，r02）：9 个时间节点各补第二行细节，800x2000 竖幅不再大片留白、节奏均匀；节点配色（青=数据事件、琥珀=决议、珊瑚=门槛/待定）与收尾面板完整",
 "outputs/.../B04/case-10/final.png  1600x640 161306 B（读图工具查看，r02）：迷你示意图的「保留 / 跳过（拟议）/ 保留」标签已移入面板内（距底边 >10px），不再掉到卡片描边上；三个方块的竖条与横杠区分清楚；引文与「以下为编辑解释，非引文」分隔明确",
 "outputs/.../B04/case-04/final.png  r03（读图工具查看）：口径行确认为「插入日期 = 生效日期前一天的 23:59:60；MJD 为生效首日（IERS Leap_Second.dat）」，第 27 行琥珀强调仍在",
 "outputs/.../B04/task-metrics.json  程序生成（mk-metrics-b04.ps1 从 JSONL 反查）：84 请求 / 21 渲染全 200 / 0 失败 0 重试 0 条 429（ratelimit_remaining 最低 110）/ 请求耗时之和 643.286s（渲染 74.686s）/ 收到 13114026 字节；迭代 21 行（baseline 10 + visual 11）、tool-usage 11 行、读图 33 次（21 次匹配正确字节 + 12 次串图/重复全部留档）；token/图像用量/费用 null 并注明原因",
 "outputs/.../B04/sources.json  14 个一手来源全部真实访问，sources[].visits 的 url/http_status/bytes/started_at/ended_at/local_file 由 requests.jsonl 反查写入；14 条不可达或 404 请求原样留档；12 条算术检查 AC-01..AC-12 带分子/分母/单位/时间范围/来源编号并逐条 matches_artwork=true",
 "outputs/.../B04/editorial-note.md  选题四条理由、7 个读者问题、10 件叙事弧线、四类事实标注（confirmed_fact / editorial_calculation / editorial_interpretation / editorial_advice / demo_data）、主动放弃的四条措辞、r01 被推翻的六类问题、工具踩坑与边界"
)

$unresolved = @(
 "无阻塞项：B04 已 completed，10/10 件独立研究型作品经真实 open-snapshot 服务渲染，终版全部用读图工具实际打开查看（21 次正确字节读图覆盖 10 件 r01/r02 与 case-04 r03），7 项顶层交付 + 10 组 case-NN 三件套齐全",
 "requests.jsonl 中 6 条 documentation 404（B04-doc-02..07）是早期按猜测地址抓取的真实失败，按原样保留在 docs/；正确文档自 B04-doc-08 起由 snapshot.muedsa.com 取得",
 "14 条 research 不可达请求（Wikipedia 中英移动版、wikiwand、Britannica 403、USNO、datacenter.iers.org 与 usno.navy.mil DNS 失败、4 个猜错路径）全部留档；相关事实改由 BIPM/IERS/hpiers/IANA/ITU/NIST/NPL/PTB/RFC 一手来源交叉覆盖，未以任何未访问页面充当来源",
 "read 工具按内容哈希缓存，同内容副本与连续读取多次返回错图（最严重时连续四次把 case-06 返回成 case-04）；已用 System.Drawing 独立核验 20 张 PNG 的画布尺寸与 SHA1、outputs 与 tmp 的 SHA256 全部 SAME，确认磁盘字节正确、问题只在读图通道；恢复办法为每次只读一张 + 改 1 个角像素生成唯一字节副本（视觉无损）。33 次读图中 21 次匹配正确字节、12 次串图/重复，全部留档为失败的工具尝试（tu-08/tu-09/tu-10）",
 "browser.preview 不可用（[browser.disconnected] No desktop browser is connected），按失败记录在 tu-10，未重复尝试",
 "mk-cases-b04.ps1 曾因循环变量 $d 与字典 $D 大小写同名互相覆盖，写出了一个字段为空的 case-02；已改名 $caseMeta 并加 null 守卫后全部重跑覆盖",
 "token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明 unknown_fields_reason；排队等待不可测记 null；限流等待 0（本题未出现 429/Retry-After，属实测非未知）",
 "case-01/case-05/case-08 中「至今/当前」的天数以 2026-10-07 为基准日，时间流逝后会过期；来源行已写明抓取日期",
 "看图的精确单次时刻未被工具记录，iterations.jsonl 以 viewed 布尔值 + view_evidence 字段记录，不编造具体时刻"
)

$resume = "completed；无阻塞，可继续 B05。10 件主作品：case-01 r02 1080x1528 / case-02 r02 1748x760 / case-03 r02 1920x1080 / case-04 r03 1200x1600 / case-05 r02 1100x1500 / case-06 r02 1080x1080 / case-07 r02 1920x480 / case-08 r02 1400x1050 / case-09 r02 800x2000 / case-10 r02 1600x640。请求 84 行串行（render 21 全 200、documentation 15 中 9×200+6×404、fonts 1×200、research 47 中 32×200+4×404+10 网络失败），0 限流 0 排队 0 重试，请求耗时之和 643.286s（渲染 74.686s），收到 13114026 字节，墙钟 57636.86s（2026-10-07T16:51:31 → 2026-10-08T08:46:08，含研究、写稿与生成程序编写等非请求时间）。迭代 21 行（baseline 10 / visual 11）、tool-usage 11 行、读图 33 次（21 次匹配正确字节、12 次串图/重复已留档）。交付 7 项顶层产物 + 10 组 case-NN/{final.png,final.snapshot,case.md}，10 张 PNG 服务原始字节合计 1676970 B 无后处理，10 种画幅比例互不重复（0.40/0.71/0.73/0.75/1.00/1.33/1.78/2.30/2.50/4.00）。B04 专属额外交付 sources.json（14 来源 + 14 失败留档 + 12 算术检查 + 逐件引用）与 editorial-note.md（选题/读者问题/叙事路线/事实纪律/视觉取向/工具踩坑/边界）。\n关键经验（已写入 snapshot-usage.md）：(1) read 工具内容哈希串图时先用 System.Drawing 验磁盘字节、再用改 1 像素的唯一副本绕开缓存，识别图片靠画内烘焙的 NN/10 报头 + 画幅比例而非路径；(2) PowerShell 5.1 中字典与循环变量绝不可大小写不同名（$d/$D 会互相覆盖）；(3) 绝不把辅助函数命名为 H（Get-History 别名）；(4) build 阶段的文本越界 Fit 守卫抓到 case-09 来源行 675>672，3 轮 30/30 全部通过；(5) ConvertTo-Json 哈希字面量内跨行数组需先算好再赋值。可复用：lib-b04.ps1 的 Ts/TBlock/Card/HR/VR/Kicker/Tag/Bar*/Tick*/Strip61/Steps/Masthead/SourceLine/Page4 与 Leap_Second.dat 解析器、render-b04.ps1 全字段请求日志、mk-metrics/mk-sources 从 JSONL 反查生成指标与来源的做法；成品不得重复计数。"

$b04 = @($ss.tasks | Where-Object { $_.id -eq 'B04' })[0]
$b04.status = 'completed'
$b04.ended_at = $now
$b04.output_dir = "outputs/$run/B04/"
$b04.temp_dir = "tmp/$run/B04/"
$b04.completed_rounds = @('r01','r02','r03')
$b04.completed_cases = @(1..10 | ForEach-Object { 'case-{0:d2}' -f $_ })
$b04.artifacts = $art
$b04.visual_review_evidence = $evidence
$b04.unresolved_issues = $unresolved
$b04.resume_notes = $resume

$b05 = @($ss.tasks | Where-Object { $_.id -eq 'B05' })[0]
if ($b05.status -eq 'pending') {
  $b05.status = 'in_progress'
  $b05.started_at = $now
  $b05.output_dir = "outputs/$run/B05/"
  $b05.temp_dir = "tmp/$run/B05/"
}

$ss.current_task = 'B05'
$ss.last_checkpoint = 'state-000034.json'
$ss.updated_at = $now

[IO.File]::WriteAllText($ssPath, ($ss | ConvertTo-Json -Depth 12), $enc)
$chk = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
"  suite-state.json written  ({0} bytes)  tasks={1}  b04={2}  b05={3}  current={4}  ckpt={5}" -f `
  (Get-Item $ssPath).Length, @($chk.tasks).Count, (@($chk.tasks|Where-Object{$_.id -eq 'B04'})[0].status), (@($chk.tasks|Where-Object{$_.id -eq 'B05'})[0].status), $chk.current_task, $chk.last_checkpoint

# ---- event seq 58 ----
$ev = [ordered]@{
  seq = 58; ts = $now; type = 'task_completed'; task = 'B04'
  artifact_scope = "outputs/$run/B04"
  renders_added = 21; views_added = 33; iterations_added = 21; cases_completed = 10
  note = "B04 完成并关闭（researched visual special《多出来的那一秒》）。10 件独立研究型作品全部为纯 DSL、经真实 open-snapshot 服务渲染，终版 PNG 字节数与各自最后一次成功响应的 bytes 逐一相等（184223/181385/203526/200127/160657/166079/81701/109040/234822/161306，合计 1676970 B），IHDR 尺寸与 DSL 首个 Container 宽高逐一相等（1080x1528 / 1748x760 / 1920x1080 / 1200x1600 / 1100x1500 / 1080x1080 / 1920x480 / 1400x1050 / 800x2000 / 1600x640），10 种画幅比例互不重复。请求 84 行（render 21 全 200；documentation 15 = 9×200 + 6×404 猜错地址；fonts 1×200；research 47 = 32×200 + 4×404 + 10 网络失败），0 重试 0 限流 0 条 429（ratelimit_remaining 最低 110），请求耗时之和 643.286s（渲染 74.686s），收到 13114026 字节，墙钟 57636.86s（2026-10-07T16:51:31+08:00 → 2026-10-08T08:46:08+08:00）。迭代 21 行（baseline 10 / visual 11）、tool-usage 11 行、读图 33 次（21 次匹配正确字节：10 件 r01 + 10 件 r02 + case-04 r03；12 次串图或重复全部留档）。交付 7 项顶层产物（portfolio.json / portfolio.md / gallery.html / sources.json / editorial-note.md / snapshot-usage.md / task-metrics.json）+ 10 组 case-NN/{final.png,final.snapshot,case.md}。B04 专属额外交付 sources.json（14 个一手来源全部真实访问、visits 由 requests.jsonl 反查写入、14 条不可达请求留档、12 条算术检查 AC-01..AC-12 逐条 matches_artwork、逐件引用 per_case_citations、demo 标记）与 editorial-note.md。视觉迭代：r01 十件全部读图并推翻六类问题（递增刻度误导、23:59:59 错位 320px、青色色块与串珠波形、9 轴标签与标题重叠、0.1 梳齿不可见、迷你图标签掉出面板）→ r02 十件全部修复并复看确认；case-04 因 MJD 列口径歧义另有 r03。fit 守卫在 r01 抓到 case-09 来源行 675>672，三轮 build 30/30 全部通过。过程缺陷如实记录：read 工具内容哈希串图 12 次（已用 System.Drawing 验字节 + 改 1 像素唯一副本恢复）、mk-cases-b04.ps1 的 $d/$D 大小写同名覆盖、辅助函数 H 撞 Get-History 别名。suite-state B04 -> completed，B05 -> in_progress。"
}
Add-Content -Path (Join-Path $st 'events.jsonl') -Value ($ev | ConvertTo-Json -Compress -Depth 4) -Encoding UTF8
"  events.jsonl appended seq=58"

# ---- checkpoint state-000034.json ----
$ckpt = [ordered]@{
  checkpoint = 'state-000034.json'; created_at = $now; seq = 58
  run_id = $run; run_profile = 'all'
  suite_state = $ss
}
$cpath = Join-Path $st 'checkpoints\state-000034.json'
[IO.File]::WriteAllText($cpath, ($ckpt | ConvertTo-Json -Depth 14), $enc)
"  checkpoint written  ({0} bytes)" -f (Get-Item $cpath).Length
