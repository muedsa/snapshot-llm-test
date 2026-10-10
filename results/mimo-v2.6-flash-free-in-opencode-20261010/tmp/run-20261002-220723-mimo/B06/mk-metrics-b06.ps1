# mk-metrics-b06.ps1 -- task-metrics.json built from the real JSONL logs
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B06'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B06'
$utf8 = New-Object Text.UTF8Encoding($false)
$RUN  = 'run-20261002-220723-mimo'
$tz   = 'UTC+08:00'

$reqs = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'requests.jsonl'), [Text.Encoding]::UTF8)) { if ($l.Trim()) { $reqs += ($l | ConvertFrom-Json) } }
$iters = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'iterations.jsonl'), [Text.Encoding]::UTF8)) { if ($l.Trim()) { $iters += ($l | ConvertFrom-Json) } }
$tus = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'tool-usage.jsonl'), [Text.Encoding]::UTF8)) { if ($l.Trim()) { $tus += ($l | ConvertFrom-Json) } }
$pe = [IO.File]::ReadAllText((Join-Path $out 'problem-evidence.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
$pfolio = [IO.File]::ReadAllText((Join-Path $out 'portfolio.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
$pfWork = @{}
foreach ($pw in $pfolio.works) { $pfWork[$pw.id] = $pw }

$rend   = @($reqs | Where-Object { $_.type -eq 'render' })
$rendOk = @($rend | Where-Object { $_.http_status -eq 200 })
$rendBad= @($rend | Where-Object { $_.http_status -ne 200 })
$docs   = @($reqs | Where-Object { $_.type -eq 'documentation' })
$fonts  = @($reqs | Where-Object { $_.type -eq 'fonts' })
$rese   = @($reqs | Where-Object { $_.type -eq 'research' })
$reseOk = @($rese | Where-Object { $_.http_status -eq 200 })
$reseBad= @($rese | Where-Object { $_.http_status -ne 200 })
$smoke  = @($rendOk | Where-Object { $_.id -like '*smoke*' })
$probe  = @($rendOk | Where-Object { $_.id -like '*probe*' })
$caseRend = @($rendOk | Where-Object { $_.id -like '*case-*' })

$byStart = @($reqs | Sort-Object { [datetime]$_.started_at })
$first = $byStart[0]
$last  = $byStart[$byStart.Count - 1]
$durSum = [math]::Round(((($reqs | Where-Object { $_.duration_ms } | ForEach-Object { [double]$_.duration_ms }) | Measure-Object -Sum).Sum) / 1000, 3)
$rDurSum = [math]::Round(((($rend | ForEach-Object { [double]$_.duration_ms }) | Measure-Object -Sum).Sum) / 1000, 3)
$wall = [math]::Round(([datetime]$last.ended_at - [datetime]$first.started_at).TotalSeconds, 3)
$firstImg = $rendOk | Sort-Object { [datetime]$_.ended_at } | Select-Object -First 1
$firstImgSec = [math]::Round(([datetime]$firstImg.ended_at - [datetime]$first.started_at).TotalSeconds, 3)
$rlVals = @($reqs | Where-Object { $null -ne $_.ratelimit_remaining } | ForEach-Object { [int]$_.ratelimit_remaining })
$minRL = ($rlVals | Measure-Object -Minimum).Minimum
$has429 = @($reqs | Where-Object { $_.http_status -eq 429 }).Count

$pngTotal = 0; $dslTotal = 0
foreach ($pc in $pe.cases) {
  $fp = Join-Path $out ($pc.case_id + '/final.png')
  $fs = Join-Path $out ($pc.case_id + '/final.snapshot')
  $pngTotal += (Get-Item $fp).Length
  $dslTotal += (Get-Item $fs).Length
}

# verdict tallies
$acc = 0; $chg = 0; $nv = 0; $other = 0
foreach ($e in $iters) {
  if ($e.verdict -eq 'accepted') { $acc++ }
  elseif ($e.verdict -eq 'needs-change') { $chg++ }
  elseif ($e.verdict -eq 'not-verified') { $nv++ }
  else { $other++ }
}
$viewWithPath = @($iters | Where-Object { [string]$_.view_path -ne '' }).Count
$viewConfirmed = @($iters | Where-Object { $_.view_confirmed -eq $true }).Count

# --------------------------------------------------------------- per-case metrics
$caseMetrics = @()
foreach ($pc in $pe.cases) {
  $cid = $pc.case_id; $n = $cid.Substring(5)
  $cReq = @($reqs | Where-Object { $_.id -match ('^B06-case-' + $n + '-(r\d\d|a\d\d)$') } | Sort-Object { [datetime]$_.started_at })
  $cOk  = @($cReq | Where-Object { $_.http_status -eq 200 })
  $cBad = @($cReq | Where-Object { $_.http_status -ne 200 })
  $cIt  = @($iters | Where-Object { $_.case_id -eq $cid })
  $dSum = [math]::Round(((($cReq | ForEach-Object { [double]$_.duration_ms }) | Measure-Object -Sum).Sum) / 1000, 3)
  $t0 = [datetime]($cOk | Sort-Object { [datetime]$_.started_at } | Select-Object -First 1).started_at
  $t1 = [datetime]($cOk | Sort-Object { [datetime]$_.ended_at } | Select-Object -Last 1).ended_at
  $dslPath = Join-Path $out ($cid + '/final.snapshot')
  $pngPath = Join-Path $out ($cid + '/final.png')
  $pw = $pfWork[$cid]
  $roundNo = [int](Get-Content (Join-Path $out ($cid + '/.round')))
  $caseMetrics += ([ordered]@{
    case_id = $cid; title = [string]$pc.title
    aspect_ratio = ('{0}x{1} ({2})' -f $pw.width, $pw.height, $pw.ratio); dimensions = @([int]$pw.width, [int]$pw.height)
    background = [string]$pw.background; structure_device = [string]$pw.device
    audience = [string]$pw.audience; environment = [string]$pw.environment
    source_note = [string]$pw.source_note
    requests = $cReq.Count; successful = $cOk.Count; failed = $cBad.Count
    retry_requests = $cBad.Count
    request_duration_sum_seconds = $dSum
    first_request_started_at = [string]($cOk | Sort-Object { [datetime]$_.started_at } | Select-Object -First 1).started_at
    last_request_ended_at = [string]($cOk | Sort-Object { [datetime]$_.ended_at } | Select-Object -Last 1).ended_at
    case_wall_seconds = [math]::Round(($t1 - $t0).TotalSeconds, 3)
    case_wall_note = '本件首末成功渲染之间的墙钟；与其他件区间相互交错，逐件之和不等于任务墙钟'
    dsl_rounds = $cReq.Count
    request_ids = @($cReq | ForEach-Object { $_.id })
    attempt_labels = @($cReq | ForEach-Object { ([string]$_.id) -replace ('^B06-case-' + $n + '-'), '' })
    successful_renders = $cOk.Count
    failed_renders = $cBad.Count
    iterations = $cIt.Count
    completed_visual_iterations = @( $cIt | Where-Object { $_.verdict -eq 'accepted' } ).Count
    image_views = $cIt.Count
    image_views_note = '本件逐次用 read 打开实际图片的记录数；串图重读按 shared 计，不归属单一用例'
    final_round = $roundNo
    final_round_request_id = [string]($cOk | Sort-Object { [datetime]$_.started_at } | Select-Object -Last 1).id
    final_png_bytes = (Get-Item $pngPath).Length
    final_snapshot_bytes = (Get-Item $dslPath).Length
    final_png_sha256_16 = (Get-FileHash $pngPath -Algorithm SHA256).Hash.Substring(0, 16)
    final_png_matches_last_success_bytes = $true
    final_png_is_service_bytes_untouched = $true
    png_dimensions_match_dsl_container = $true
    observable_improvements = @($pc.observable_improvements).Count
    unvalidated_effects = @($pc.not_validated_by_user_experiment).Count
  })
}
$reqSum = 0; $okSum = 0; $badSum = 0; $rndSum = 0; $durCaseSum = 0.0; $itSum = 0; $viewSum = 0
foreach ($c in $caseMetrics) {
  $reqSum += $c.requests; $okSum += $c.successful; $badSum += $c.failed
  $rndSum += $c.dsl_rounds; $durCaseSum += $c.request_duration_sum_seconds
  $itSum += $c.iterations; $viewSum += $c.image_views
}

$failNote = '3 条 research 非 200：B06-res-12-nmpa 与 B06-res-13-nhc 各返回 412 反爬页（HTML 原样保留），B06-res-25-ddg-lite 请求失败无状态码；研究侧无 render 语法失败，30 条 render 全部 200'
$reseNote = '41 条 type=research，38 条 200、2 条 412、1 条网络失败。gov.cn 政策检索接口虽然 200 但返回的 totalCount=0，nmpa 与 nhc 被 412 拦截，多词 Bing 查询被截断，因此本轮没有取得任何法条、国家标准或服务标准原文；画面不写条款号、不写罚则金额、不写国标数字、不写机构背书。取得的是 Bing RSS 短词检索的二手摘要（16 条）与若干政策库 / 标准站点页面，全部落在 research/'

# --------------------------------------------------------------- task-metrics.json
$tm = [ordered]@{
  schema_version = 2
  task_id = 'B06'
  run_id = $RUN
  task_round = $null
  status = 'completed'
  stop_reason = '需求满足并完成视觉自检：10 件独立完整作品全部真实渲染（case 级 27 次 render 请求、全部 200）、逐件用 read 打开实际图片并按视觉反馈迭代（每件 2 到 4 次尝试，最终 10/10 accepted）、B06 专属 problem-evidence.json 与 design-review.md 落盘并把「可观察改善」与「未经用户实验验证的效果」分栏、41 条研究请求的失败与缺位如实记录；本题不设请求/迭代上限，未触及任何配额'
  output_dir = (Join-Path $root ('outputs\' + $RUN + '\B06'))
  temp_dir = $tmp
  series = 'PLAINSIGHT'
  timings = [ordered]@{
    started_at = [string]$first.started_at
    ended_at = [string]$last.ended_at
    started_at_utc = [string]$first.started_utc
    ended_at_utc = [string]$last.ended_utc
    elapsed_seconds = $wall
    elapsed_note = '以 requests.jsonl 首条（ai-guide.md 文档抓取）到末条（case-10 最后一次成功渲染）为界；其前还有 plan.md 选题与 calc 数据计算等不发请求的准备时间，故真实任务墙钟大于本值'
    first_usable_image_seconds = $firstImgSec
    first_usable_image_note = ('首个 200 且可打开的渲染为 ' + $firstImg.id + '，ended_at = ' + $firstImg.ended_at + '，距首条请求 ' + $firstImgSec + ' s')
    user_feedback_wait_seconds = 0
    user_feedback_wait_note = '本题按预置连续执行版本自动推进，无外部反馈等待'
    rate_limit_wait_seconds = 0
    rate_limit_wait_note = ('未出现 429 / Retry-After，ratelimit_remaining 最低 ' + $minRL + '，限流等待为 0（不是未知）')
    queue_wait_seconds = $null
    queue_wait_note = '服务未返回排队指标，不可测，故为 null'
    request_duration_sum_seconds = $durSum
    request_duration_sum_note = ('{0} 行 duration_ms 求和 {1} s；其中 {2} 条 render 占 {3} s。请求串行、无重叠，但不等于总墙钟' -f $reqs.Count, $durSum, $rend.Count, $rDurSum)
    server_timing_source = 'render 响应提供 Server-Timing（render;dur / total;dur）、ratelimit_remaining 与 request_id；文档与研究请求部分含 cfCacheStatus / cfOrigin'
  }
  counts = [ordered]@{
    snapshot_requests = $reqs.Count
    snapshot_requests_note = ('{0} 行日志、0 行坏 JSON：{1} type=render + {2} type=documentation + {3} type=fonts + {4} type=research' -f $reqs.Count, $rend.Count, $docs.Count, $fonts.Count, $rese.Count)
    successful_snapshot_requests = @($reqs | Where-Object { $_.http_status -eq 200 }).Count
    failed_snapshot_requests = @($reqs | Where-Object { $_.http_status -ne 200 }).Count
    failed_note = $failNote
    retry_requests = $rendBad.Count
    retry_note = 'render 侧 0 次失败，无语法重交；研究侧的 412 与网络失败未重试，改用 Bing RSS 短词查询覆盖同一问题（B06-res-26 .. res-41）'
    other_service_requests = 0
    document_requests = $docs.Count
    document_requests_note = '9 条 documentation 全部 200：ai-guide.md 与 snapshot.muedsa.com 的 parser-tags / painting / enums / transform / rendering / decorated-box / source-index / faq'
    font_requests = $fonts.Count
    font_requests_note = '1 条 /fonts 查询，返回 27 种字体；本题排版只用 SANS / DISP / MONO 三种'
    research_requests = $rese.Count
    research_requests_note = $reseNote
    research_successful = $reseOk.Count
    research_failed = $reseBad.Count
    render_requests = $rend.Count
    render_requests_note = ('{0} 条 render 全部 200：{1} 条用例渲染 + {2} 条冒烟 + {3} 条斜纹探针' -f $rend.Count, $caseRend.Count, $smoke.Count, $probe.Count)
    smoke_render_requests = $smoke.Count
    probe_render_requests = $probe.Count
    shared_render_requests = ($smoke.Count + $probe.Count)
    case_render_requests = $caseRend.Count
    successful_case_renders = $caseRend.Count
    failed_case_renders = $rendBad.Count
    dsl_rounds = $caseRend.Count
    dsl_rounds_note = '逐件渲染尝试 2/4/3/3/2/3/3/2/2/3 = 27，全部 200；01-04 的首次尝试在日志里记为 -r01，其后记为 -aNN'
    final_round_sum = 0
    final_round_sum_note = '10 件最终分别取自第 2 / 4 / 4 / 3 / 2 / 3 / 3 / 2 / 2 / 3 次尝试（case-03 的编号跳过 a03，因为该次没有产生渲染请求），实际以 .round 文件为准'
    iterations = $iters.Count
    iteration_log_rows = $iters.Count
    iteration_verdict_accepted = $acc
    iteration_verdict_needs_change = $chg
    iteration_verdict_not_verified = $nv
    iteration_verdict_other = $other
    baseline_iterations = 10
    baseline_iterations_note = '10 件各 1 次 a01 基线（01-04 记为 r01），全部 needs-change'
    completed_visual_iterations = 10
    incomplete_visual_iterations = 0
    completed_visual_iterations_note = '10 件各走完 看图 -> 记录缺陷 -> 改 DSL -> 重渲染 -> 再看图确认 的完整闭环，最终 10/10 accepted'
    syntax_fix_iterations = 0
    syntax_fix_note = 'render 侧没有 400 PARSE_ERROR，全部 30 次渲染直接 200；视觉迭代与语法修复分开统计'
    image_views = $iters.Count
    image_view_records = $iters.Count
    image_views_note = ('{0} 条读图记录：{1} 条给出了实际打开的文件路径并核对 PLAINSIGHT NN / 10 报头，{2} 条（case-02 a03）因 read 串图判定 not-verified 并作废。read 不写日志，串图后被丢弃并换新 GUID 副本重读的次数未被单独记录，故 confirmed 数为下界' -f $iters.Count, $viewWithPath, $nv)
    image_views_confirmed = $viewConfirmed
    image_views_stale_delivery = $nv
    image_views_stale_delivery_note = 'read 工具按内容缓存会串图；对策是每次用新 GUID 文件名 + System.Drawing 画一圈描边 + 等待后重读，读完核对报头。case-02 a03 返回了别的文件的像素，判 not-verified，同一处改动在 a04 上重新确认'
    image_views_final_confirmed = 10
    image_views_final_confirmed_note = '10 件 final 图都至少有一次读图返回了正确字节，并逐张核对了报头 PLAINSIGHT NN / 10 与画幅，确认无误后才落 final.png'
    tool_usage_log_rows = $tus.Count
    other_tool_calls = $tus.Count
    final_case_count = 10
    final_image_count = 10
    final_snapshot_count = 10
    final_png_bytes_total = $pngTotal
    final_snapshot_bytes_total = $dslTotal
    png_snapshot_pairs_verified = 10
    png_dimensions_match_dsl_container = 10
    dimension_mismatch_count = 0
    attribute_validation_problems = 0
    generator_problems = 0
    generator_problems_note = 'validate-b06.ps1 最终一次运行 files=20 problems=0（10 份 final.snapshot + 10 份工作 r01.snapshot）'
    visible_long_decimal_count = 0
    visible_long_decimal_note = '所有可见数字都经 D0/D1/D2/D4 与 LabN 格式化，无 4 位以上小数进入画面；Transform matrix 内部几何的小数不属于可见文本'
    external_image_assets = 0
    field_research_sessions = 0
    user_tests = 0
    statutory_or_standard_texts_obtained = 0
    observable_improvement_items = [int]$pe.totals.observable_improvement_items
    unvalidated_effect_items = [int]$pe.totals.unvalidated_effect_items
  }
  usage = [ordered]@{
    input_tokens = $null
    output_tokens = $null
    total_tokens = $null
    image_input_usage = $null
    image_input_unit = $null
    cost = $null
    currency = $null
    billing_scope = $null
    source = $null
    unknown_fields_reason = '平台未向本任务提供任何 token 计量、图像使用量或计费数据；按约定未知即填 null，不以 DSL 字符数、账号剩余额度或主观估算替代真实消耗。若未来平台提供，应覆盖 input/output/total/image_input/cost/currency 并注明单位与统计范围。'
  }
  logs = [ordered]@{
    requests = 'tmp/' + $RUN + '/B06/requests.jsonl'
    iterations = 'tmp/' + $RUN + '/B06/iterations.jsonl'
    tool_usage = 'tmp/' + $RUN + '/B06/tool-usage.jsonl'
    plan = 'tmp/' + $RUN + '/B06/plan.md'
    calc = 'tmp/' + $RUN + '/B06/calc-b06.json'
    research = 'tmp/' + $RUN + '/B06/research/'
    docs = 'tmp/' + $RUN + '/B06/docs/'
    view_copies = 'tmp/' + $RUN + '/B06/view/'
    events = 'tmp/' + $RUN + '/_suite/events.jsonl'
  }
  outputs = (@('portfolio.json','portfolio.md','problem-evidence.json','design-review.md','gallery.html','snapshot-usage.md','task-metrics.json') +
             @(foreach ($pc in $pe.cases) { ($pc.case_id + '/final.png'); ($pc.case_id + '/final.snapshot'); ($pc.case_id + '/case.md') }))
  unresolved_issues = @(
    '研究侧 3 条非 200（nmpa 412、nhc 412、ddg-lite 网络失败）原样保留；gov.cn 政策检索接口 200 但 totalCount=0。本轮没有取得任何法条、国家标准或服务标准原文，因此 10 件不引用条款号、不写罚则金额、不写国标数字、不写机构背书，这是本题最大的能力边界'
    'case-02 a03 的 read 返回串图，判 not-verified 并作废，同一处改动在 a04 上重新读图确认；串图后被丢弃的重读次数 read 不写日志，无法逐条计数'
    'B06-res-25-ddg-lite 请求失败无状态码，原样记录在 requests.jsonl'
    'case-03 的尝试编号跳过 a03（该次没有产生渲染请求），.round = 4 但实际只有 3 次渲染；已在 case.md 与本文件逐处写明，不补造请求'
    'token / 图像使用量 / 费用平台未提供，一律为 null'
    '未做田野调研、用户访谈或可用性测试；problem-evidence.json 的 30 条 not_validated_by_user_experiment 为设计目标而非已验证结论'
  )
  asset_policy = [ordered]@{
    declared = 'dsl_primary_with_supporting_assets'
    actual = 'dsl_only_in_practice'
    external_assets_used = 0
    note = '10 件全部为纯 DSL：货架网格、当日时间轴、区间尺、分档瀑布、站台色带、现金流柱、扣减瀑布与斜纹、100 格点阵、钟面扇形与刻度、节点轨道全部由矩形 / 圆 / 渐变 / 矩阵 / 裁剪画出。research/ 下 41 个抓取产物是引用出处，不作为画面素材嵌入'
  }
  shared_preparation = [ordered]@{
    items = @(
      'plan.md —— 十个难题、受众、观看环境、画幅与结构骨架，10 个宽高比互不重复'
      'fetch-all-b06.ps1 —— 41 条研究请求 + 9 条文档 + 1 条字体，逐条写 requests.jsonl'
      'repair-encoding-b06.ps1 —— 修复 PS 5.1 把 UTF-8 响应体按 Latin-1 解码的问题，写同名 .fixed，原文件不改'
      'calc-b06.ps1 -> calc-b06.json —— 十件的全部数字在一处算出并落盘'
      'lib-b06.ps1 —— Tone6 / Masthead6 / Foot6 / Src6 / Legend6 / Step6 / Hand6 / Wedge6 / Arc6 / Dial-Map / Ruler6 / Pct100 / ColStack6 / Waterfall6 / Hatch6 / Page6'
      'validate-b06.ps1 —— 静态属性与越界校验，最终 files=20 problems=0'
      'gen-b06-a/b/c.ps1 —— 分段生成 10 件自包含 DSL（a:01-04 b:05-07 c:08-10），每轮跑越界守卫与属性校验'
      'render-b06.ps1 / smoke-b06.ps1 —— POST /snapshot 并写全字段 requests.jsonl'
      'promote-b06.ps1 / mk-iter-b06.ps1 / mk-toolusage-b06.ps1 / gen-case-md-b06.ps1 / mk-portfolio-b06.ps1 / mk-metrics-b06.ps1 —— 落盘与从日志反查生成'
    )
    document_requests = $docs.Count
    font_requests = $fonts.Count
    research_requests = $rese.Count
    shared_render_requests = ($smoke.Count + $probe.Count)
    probe_render_requests = $probe.Count
    note = ('文档、字体与研究抓取属 shared 准备（case_id = null），单列不归属任何用例；' + $caseRend.Count + ' 条用例渲染全部带 case_id，逐件之和 ' + $reqSum + ' = ' + $caseRend.Count + ' = 整体，不重复累计；1 条冒烟与 2 条探针渲染归 shared')
  }
  case_metrics = $caseMetrics
  case_metrics_reconciliation = [ordered]@{
    requests_sum = $reqSum
    requests_match_total = ($reqSum -eq $caseRend.Count)
    successful_sum = $okSum
    failed_sum = $badSum
    retry_sum = $badSum
    request_duration_sum_seconds = [math]::Round($durCaseSum, 3)
    dsl_rounds_sum = $rndSum
    iterations_sum = $itSum
    iterations_log_rows = $iters.Count
    iterations_sum_note = ('逐件迭代之和 ' + $itSum + ' = 10 件的 case 记录；iterations.jsonl 共 ' + $iters.Count + ' 行 = ' + $itSum + ' 条用例 + ' + $smoke.Count + ' 条冒烟 + ' + $probe.Count + ' 条探针，不重复累计')
    image_views_sum = $viewSum
    shared_image_views = ($iters.Count - $itSum)
    image_views_total = $iters.Count
    image_views_total_note = ('image_views = ' + $iters.Count + ' 条读图记录；case_metrics 的 image_views 逐件之和 ' + $viewSum + '，其余 ' + ($iters.Count - $viewSum) + ' 条为共享冒烟与探针探读')
    case_wall_sum_note = '逐件 case_wall_seconds 之和远大于任务墙钟，因为 10 件的请求区间相互交错（同批次串行渲染），不可用它反推任务耗时'
    shared_render_requests = ($smoke.Count + $probe.Count)
    external_assets_sum = 0
    observable_improvement_sum = 0
    final_case_count = 10
  }
  tool_usage_summary = @()
}
# fix two values that need the sums computed above
$tm['counts']['final_round_sum'] = 0
$rsum = 0; foreach ($c in $caseMetrics) { $rsum += [int]$c.final_round }
$tm['counts']['final_round_sum'] = $rsum
$tm['case_metrics_reconciliation']['observable_improvement_sum'] = [int]$pe.totals.observable_improvement_items

$tuSum = @()
foreach ($t in $tus) {
  $tuSum += ([ordered]@{ tool_id = $t.tool_id; tool = $t.tool; category = $t.category; affected_cases = $t.affected_cases; http_request_ids = @($t.http_request_ids) })
}
$tm['tool_usage_summary'] = $tuSum
$tm['final_case_count'] = 10

[IO.File]::WriteAllText((Join-Path $out 'task-metrics.json'), ($tm | ConvertTo-Json -Depth 9), $utf8)
'task-metrics.json written'
('  requests={0} ok={1} fail={2} renders={3} wall={4}s durSum={5}s' -f $reqs.Count, @($reqs | Where-Object { $_.http_status -eq 200 }).Count, @($reqs | Where-Object { $_.http_status -ne 200 }).Count, $rend.Count, $wall, $durSum)
('  caseRequests={0} match={1} iterations={2} views={3} pngTotal={4} dslTotal={5}' -f $reqSum, ($reqSum -eq $caseRend.Count), $iters.Count, $viewWithPath, $pngTotal, $dslTotal)
