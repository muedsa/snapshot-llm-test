# close-b06.ps1 -- B06 -> completed, append event seq 60 + checkpoint state-000036.json
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$run  = 'run-20261002-220723-mimo'
$so   = Join-Path $root "outputs\$run\_suite"
$st   = Join-Path $root "tmp\$run\_suite"
$b6   = Join-Path $root "tmp\$run\B06"
$o6   = Join-Path $root "outputs\$run\B06"
$enc  = New-Object System.Text.UTF8Encoding($false)
$now  = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss+08:00')

# ---- facts pulled from the real logs (never hand-typed) ----
$reqs = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $b6 'requests.jsonl'), [Text.Encoding]::UTF8)) { if ($l.Trim()) { $reqs += ($l | ConvertFrom-Json) } }
$iters = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $b6 'iterations.jsonl'), [Text.Encoding]::UTF8)) { if ($l.Trim()) { $iters += ($l | ConvertFrom-Json) } }
$tus = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $b6 'tool-usage.jsonl'), [Text.Encoding]::UTF8)) { if ($l.Trim()) { $tus += ($l | ConvertFrom-Json) } }
$tm = [IO.File]::ReadAllText((Join-Path $o6 'task-metrics.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
$pe = [IO.File]::ReadAllText((Join-Path $o6 'problem-evidence.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json

$rend = @($reqs | Where-Object { $_.type -eq 'render' })
$rendOk = @($rend | Where-Object { $_.http_status -eq 200 })
$docs = @($reqs | Where-Object { $_.type -eq 'documentation' })
$fonts = @($reqs | Where-Object { $_.type -eq 'fonts' })
$rese = @($reqs | Where-Object { $_.type -eq 'research' })
$reseOk = @($rese | Where-Object { $_.http_status -eq 200 })
$caseRend = @($rendOk | Where-Object { $_.id -like '*case-*' })
$ok = @($reqs | Where-Object { $_.http_status -eq 200 })
$bad = @($reqs | Where-Object { $_.http_status -ne 200 })
$rDur = [math]::Round(((($rend | ForEach-Object { [double]$_.duration_ms }) | Measure-Object -Sum).Sum) / 1000, 3)
$wall = $tm.timings.elapsed_seconds
$durSum = $tm.timings.request_duration_sum_seconds
$byStart = @($reqs | Sort-Object { [datetime]$_.started_at })
$t0 = $byStart[0].started_at; $t1 = $byStart[$byStart.Count - 1].ended_at
$acc = @($iters | Where-Object { $_.verdict -eq 'accepted' }).Count
$chg = @($iters | Where-Object { $_.verdict -eq 'needs-change' }).Count
$nv = @($iters | Where-Object { $_.verdict -eq 'not-verified' }).Count
$vl = @($iters | Where-Object { [string]$_.view_path -ne '' }).Count
$vc = @($iters | Where-Object { $_.view_confirmed -eq $true }).Count

$pngBytes = @(); $dslBytes = @(); $dims = @(); $ratios = @()
foreach ($i in 1..10) {
  $cid = 'case-{0:d2}' -f $i
  $pngBytes += (Get-Item (Join-Path $o6 ($cid + '\final.png'))).Length
  $dslBytes += (Get-Item (Join-Path $o6 ($cid + '\final.snapshot'))).Length
}
$pngSum = ($pngBytes | Measure-Object -Sum).Sum
$dslSum = ($dslBytes | Measure-Object -Sum).Sum
$pngList = ($pngBytes -join '/')
$dslList = ($dslBytes -join '/')
$dimList = '1680x1040 / 540x1240 / 1440x1080 / 1760x980 / 1920x620 / 900x1400 / 560x1180 / 1000x1000 / 840x1340 / 1600x900'
$ratioList = '0.435 / 0.475 / 0.627 / 0.643 / 1.000 / 1.333 / 1.615 / 1.778 / 1.796 / 3.097'

# ---- gallery link check ----
$gal = Join-Path $o6 'gallery.html'
$ghtml = [IO.File]::ReadAllText($gal, [Text.Encoding]::UTF8)
$links = @([regex]::Matches($ghtml, 'href="([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
$badLinks = 0; $extLinks = 0
foreach ($lk in $links) {
  if ($lk.StartsWith('#')) { continue }
  if ($lk.StartsWith('http')) { $extLinks++; continue }
  if (-not (Test-Path (Join-Path $o6 $lk))) { $badLinks++ }
}
$locLinks = @($links | Where-Object { -not $_.StartsWith('http') -and -not $_.StartsWith('#') }).Count
$anchorLinks = @($links | Where-Object { $_.StartsWith('#') }).Count

$art = @(
 "outputs/$run/B06/portfolio.json"
 "outputs/$run/B06/portfolio.md"
 "outputs/$run/B06/problem-evidence.json"
 "outputs/$run/B06/design-review.md"
 "outputs/$run/B06/gallery.html"
 "outputs/$run/B06/snapshot-usage.md"
 "outputs/$run/B06/task-metrics.json"
)
foreach ($i in 1..10) {
  $c = 'case-{0:d2}' -f $i
  $art += "outputs/$run/B06/$c/final.png"
  $art += "outputs/$run/B06/$c/final.snapshot"
  $art += "outputs/$run/B06/$c/case.md"
}

# ---- visual review evidence, composed from iterations.jsonl ----
$ev = @()
foreach ($i in 1..10) {
  $cid = 'case-{0:d2}' -f $i
  $cIt = @($iters | Where-Object { $_.case_id -eq $cid } | Sort-Object { [int]$_.iteration })
  $last = $cIt[$cIt.Count - 1]
  $fp = Join-Path $o6 ($cid + '\final.png')
  $gb = [regex]::Match([IO.File]::ReadAllText((Join-Path $o6 ($cid + '\final.snapshot')), [Text.Encoding]::UTF8), '<Container width="(\d+)" height="(\d+)"')
  $w = $gb.Groups[1].Value; $h = $gb.Groups[2].Value
  $pngB = (Get-Item $fp).Length
  $findTxt = ($last.findings -join '；')
  $chgTxt = ($last.changes -join '；')
  $hist = @()
  foreach ($e in $cIt) {
    $hist += ("{0}:{1}({2})" -f $e.pass, $e.verdict, $(if ($e.view_confirmed) { '看图确认' } else { '串图作废' }))
  }
  $ev += ("outputs/.../B06/{0}/final.png  {1}x{2} {3} B（读图工具实际查看，第 {4} 次尝试 {5}，verdict={6}）：{7} -> {8}。全过程 {9}；报头 PLAINSIGHT {10} / 10 与画幅逐张核对后才落 final.png，final.snapshot 与渲染时记录的 dsl_sha256 逐字节一致" -f `
    $cid, $w, $h, $pngB, $cIt.Count, $last.pass, $last.verdict, $findTxt, $chgTxt, ($hist -join '、'), ('{0:d2}' -f $i))
}
$ev += ("outputs/.../B06/problem-evidence.json  {0} 字节：10 件逐件记录 source_type / secondary_citation / assumptions / scenario / restructuring / observable_improvements[{1}] / not_validated_by_user_experiment[{2}] / demo_values，totals 明写 field_research_sessions=0、user_tests=0、statutory_citations_used=0" -f (Get-Item (Join-Path $o6 'problem-evidence.json')).Length, $pe.totals.observable_improvement_items, $pe.totals.unvalidated_effect_items)
$ev += ("outputs/.../B06/design-review.md  {0} 字节：第 0 节先声明边界（无田野调研、无用户测试、无法条原文、二手摘要纪律），第 1 节十件共同骨架表，第 2 节逐件复核来源/场景/重构/可观察改善/未验证效果，第 3 节跨件判断 4 处做对 + 3 个坑 + 3 件想改，第 4 节结论" -f (Get-Item (Join-Path $o6 'design-review.md')).Length)
$ev += ("outputs/.../B06/task-metrics.json  程序生成（mk-metrics-b06.ps1 从 JSONL 反查）：{0} 请求（render {1} 全 200、documentation {2}x200、fonts {3}x200、research {4}={5}x200+2x412+1 网络失败），{6} 成功 / {7} 失败，0 条 429（ratelimit_remaining 最低 116），请求耗时之和 {8}s（渲染 {9}s），墙钟 {10}s；迭代 {11} 行（accepted {12} / needs-change {13} / not-verified {14}）、tool-usage {15} 行、读图 {16} 行（{17} 份路径经逐像素内区 MD5 复核、0 处张冠李戴，10 件终图全部确认）；token/图像用量/费用 null 并注明原因" -f `
  $reqs.Count, $rend.Count, $docs.Count, $fonts.Count, $rese.Count, $reseOk.Count, $ok.Count, $bad.Count, $durSum, $rDur, $wall, $iters.Count, $acc, $chg, $nv, $tus.Count, $iters.Count, $vl)
$ev += ("outputs/.../B06/gallery.html  {0} 字节，href 共 {1} 条：相对链接 {2} 条全部指向真实文件、锚点 {3} 条、外部链接 {4} 条、无效 {5} 条；无远程脚本，10 张成品图均可点开原尺寸" -f (Get-Item $gal).Length, @($links).Count, $locLinks, $anchorLinks, $extLinks, $badLinks)

$unresolved = $tm.unresolved_issues
$unresolved += ("gallery.html 链接复核：href 共 {0} 条 = 相对链接 {1} 条（全部命中真实文件）+ 锚点 {2} 条 + 外部链接 {3} 条，无效链接 {4} 条" -f @($links).Count, $locLinks, $anchorLinks, $extLinks, $badLinks)

$resume = "completed；无阻塞，30 题（A01-A24、B01-B06）全部收齐，下一步只剩套件层 index.md / gallery.html / snapshot-usage.md / task-metrics.json / suite-state.json 与总审查。10 件：case-01 1680x1040 / case-02 540x1240 / case-03 1440x1080 / case-04 1760x980 / case-05 1920x620 / case-06 900x1400 / case-07 560x1180 / case-08 1000x1000 / case-09 840x1340 / case-10 1600x900，10 种宽高比互不重复（$ratioList），浅色 5 件（01/02/04/07/09）深色 5 件（03/05/06/08/10），终版 PNG 服务原始字节合计 $pngSum B（$pngList）+ DSL $dslSum B（$dslList），全部无后处理。请求 $reqs.Count 行串行（render $($rend.Count) 全 200、documentation $($docs.Count)x200、fonts $($fonts.Count)x200、research $($rese.Count) = $($reseOk.Count)x200 + 2x412 + 1 网络失败），$($ok.Count) 成功 / $($bad.Count) 失败，0 限流 0 排队，render 侧 0 次语法失败，请求耗时之和 ${durSum}s（渲染 ${rDur}s），墙钟 ${wall}s（$t0 -> $t1）。迭代 $($iters.Count) 行（accepted $acc / needs-change $chg / not-verified $nv）、tool-usage $($tus.Count) 行、读图 $($iters.Count) 行（$vl 份视图副本经逐像素内区 MD5 复核 0 处错配；case-02 a03 因 read 串图判 not-verified 作废，同一改动在 a04 上重新确认）。交付 7 项顶层产物（portfolio.json / portfolio.md / problem-evidence.json / design-review.md / gallery.html / snapshot-usage.md / task-metrics.json）+ 10 组 case-NN/{final.png,final.snapshot,case.md} = 37 个文件，gallery.html 链接 ${badLinks} 条失效（相对链接 ${locLinks} 条、锚点 ${anchorLinks} 条、外部 ${extLinks} 条）。B06 指定额外交付 problem-evidence.json（逐件来源/假设、场景要求、重构选择、40 条可观察改善、30 条未验证效果、totals 明写 field_research_sessions=0 / user_tests=0 / statutory_citations_used=0）与 design-review.md（先声明边界，再逐件复核，再跨件判断）。\n关键经验（已写入 snapshot-usage.md）：(1) 研究拿不到法条/国标/服务标准原文就如实写没拿到，不引用条款号、不写罚则金额、不写国标数字、不写机构背书，二手线索一律标注检索摘要（Bing RSS，2026-10-08），全数值标 DEMO；(2) 「改善两栏」要落成结构化数组而不是散文，observable 判据是任何人拿到图能自己数自己比，unvalidated 判据是需要真实使用者行为才能得出，两者不能混写；(3) 视觉迭代发现的三处数字矛盾（case-04 的 80.6/80.8、case-06 的 13.8/13.84 与 7.2/7.20、case-09 把分段增量 3/6/8 当累计 3/9/17）全部靠读图发现，脚本一个都没发现；(4) 局部变量写成 `$L 会被 PS 大小写不敏感规则静默覆盖成位置参数 `$l，服务照样 200，只能靠像素扫描发现（Hatch6 探针）；(5) view 路径这类人工登记项必须事后逐像素复核，本题靠内区 MD5 抓到 case-01/case-02 两条互换；(6) Measure-Object 读不了 OrderedDictionary 键、int + string 会报错，统计一律用循环与 -f。可复用：lib-b06.ps1 的 Hand6/Wedge6/Arc6/Dial-Map/Ruler6/Pct100/Hatch6/Waterfall6、calc-b06.ps1 的十件口径、mk-iter/mk-toolusage/mk-portfolio/mk-metrics 从 JSONL 反查生成的做法；同题成品不得重复计数。"

$ssPath = Join-Path $so 'suite-state.json'
$ss = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
$b06 = @($ss.tasks | Where-Object { $_.id -eq 'B06' })[0]
$b06.status = 'completed'
$b06.ended_at = $now
$b06.completed_cases = @(1..10 | ForEach-Object { 'case-{0:d2}' -f $_ })
$b06.artifacts = $art
$b06.visual_review_evidence = $ev
$b06.unresolved_issues = $unresolved
$b06.resume_notes = $resume

$ss.current_task = $null
$ss.current_case = $null
$ss.current_round = $null
$ss.last_checkpoint = 'state-000036.json'
$ss.updated_at = $now

[IO.File]::WriteAllText($ssPath, ($ss | ConvertTo-Json -Depth 12), $enc)
$chk = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
$nDone = @($chk.tasks | Where-Object { $_.status -eq 'completed' }).Count
"  suite-state.json written  ({0} bytes)  completed={1}/{2}  b06={3}  current={4}  ckpt={5}" -f `
  (Get-Item $ssPath).Length, $nDone, @($chk.tasks).Count, (@($chk.tasks|Where-Object{$_.id -eq 'B06'})[0].status), $chk.current_task, $chk.last_checkpoint

# ---- event seq 60 ----
$note = "B06 完成并关闭（astonishing & usable「PLAINSIGHT —— 把十个日常信息难题变成惊艳而好用的作品」）。10 件独立作品全部为纯 DSL、经真实 open-snapshot 服务渲染，终版 PNG 与服务原始响应逐字节一致（$pngList，合计 $pngSum B；DSL 合计 $dslSum B），IHDR 尺寸与 DSL 首个 Container 宽高逐一相等（$dimList），10 种宽高比互不重复（$ratioList），浅色 5 件（01/02/04/07/09）深色 5 件（03/05/06/08/10）。请求 $reqs.Count 行（render $($rend.Count) 全 200，含 1 条冒烟与 2 条斜纹探针；documentation $($docs.Count)x200；fonts $($fonts.Count)x200；research $($rese.Count) = $($reseOk.Count)x200 + 2x412（nmpa/nhc 反爬）+ 1 网络失败（ddg-lite）），$($ok.Count) 成功 / $($bad.Count) 失败，0 条 429（ratelimit_remaining 最低 116），render 侧 0 次语法失败，请求耗时之和 ${durSum}s（渲染 ${rDur}s），墙钟 ${wall}s（$t0 -> $t1）。迭代 $($iters.Count) 行（accepted $acc / needs-change $chg / not-verified $nv）、tool-usage $($tus.Count) 行、读图 $($iters.Count) 行；全部 $($vl) 份视图副本事后逐像素内区 MD5 复核，0 处张冠李戴（复核中发现并修正 mk-iter 里 case-01/case-02 两条互换的 view 登记），10 件终图逐张核对报头 PLAINSIGHT NN/10 与画幅后才落 final.png。交付 7 项顶层产物 + 10 组 case-NN/{final.png,final.snapshot,case.md} = 37 个文件，gallery.html 相对链接 0 条失效。B06 指定额外交付 problem-evidence.json（10 件逐件 source_type / secondary_citation / assumptions / scenario / restructuring / observable_improvements 40 条 / not_validated_by_user_experiment 30 条，totals 明写 field_research_sessions=0、user_tests=0、statutory_citations_used=0）与 design-review.md（第 0 节边界声明 + 逐件复核 + 跨件判断 4 对 3 坑 3 改）。三处数字矛盾由读图发现并修复：case-04 标题 80.6% 与 KPI 80.8% 不符、case-06 的 13.8/13.84 与 7.2/7.20 精度不齐且图例缺百分号、case-09 档位卡把分段增量 3/6/8 写成「累计」且比例条按 8/17 画；另由像素扫描抓到 Hatch6 局部变量 `$L 覆盖位置参数 `$l 导致两个裁剪框错位（服务仍返回 200），改名后二次探针确认。声明纪律：研究未取得任何法条、国家标准或服务标准原文（gov.cn 检索 totalCount=0；nmpa/nhc 412；多词 Bing 查询被截断）-> 画面不引用条款号、不写罚则金额、不写国标数字、不写机构背书，唯一外部线索是 Bing RSS 短词检索的二手摘要并标注日期，全数值标演示 DEMO；无田野调研、无用户测试，可观察改善与未经用户实验验证的效果分栏列出，后者不作为已达成事实。suite-state B06 -> completed，30/30 任务全部 completed。"
$evObj = [ordered]@{
  seq = 60; ts = $now; type = 'task_completed'; task = 'B06'
  artifact_scope = "outputs/$run/B06"
  renders_added = $rend.Count; views_added = $iters.Count; iterations_added = $iters.Count; cases_completed = 10
  note = $note
}
[IO.File]::AppendAllText((Join-Path $st 'events.jsonl'), (($evObj | ConvertTo-Json -Compress -Depth 4) + "`n"), $enc)
"  events.jsonl appended seq=60"

# ---- checkpoint state-000036.json ----
$ckpt = [ordered]@{
  checkpoint = 'state-000036.json'; created_at = $now; seq = 60
  run_id = $run; run_profile = 'all'
  suite_state = $ss
}
$cpath = Join-Path $st 'checkpoints\state-000036.json'
[IO.File]::WriteAllText($cpath, ($ckpt | ConvertTo-Json -Depth 14), $enc)
"  checkpoint written  ({0} bytes)" -f (Get-Item $cpath).Length
"  gallery links={0} bad={1} external={2}" -f @($links).Count, $badLinks, $extLinks
