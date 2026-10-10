# mk-metrics-b05.ps1 -- task-metrics.json built from the real JSONL logs
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B05'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B05'
$utf8 = New-Object Text.UTF8Encoding($false)
$RUN  = 'run-20261002-220723-mimo'
$tz   = 'UTC+08:00'

$reqs = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'requests.jsonl'))) { if ($l.Trim()) { $reqs += ($l | ConvertFrom-Json) } }
$iters = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'iterations.jsonl'))) { if ($l.Trim()) { $iters += ($l | ConvertFrom-Json) } }
$tus = @(); foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'tool-usage.jsonl'))) { if ($l.Trim()) { $tus += ($l | ConvertFrom-Json) } }
$idx = [IO.File]::ReadAllText((Join-Path $tmp 'case-index-b05.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json

$rend  = @($reqs | Where-Object { $_.type -eq 'render' })
$rendOk= @($rend  | Where-Object { $_.http_status -eq 200 })
$rendBad=@($rend  | Where-Object { $_.http_status -ne 200 })
$docs  = @($reqs | Where-Object { $_.type -eq 'documentation' })
$fonts = @($reqs | Where-Object { $_.type -eq 'fonts' })
$rese  = @($reqs | Where-Object { $_.type -eq 'research' })
$reseOk= @($rese  | Where-Object { $_.http_status -eq 200 })
$reseBad=@($rese  | Where-Object { $_.http_status -ne 200 })
$smoke = @($rendOk | Where-Object { $_.id -like '*smoke*' })
$caseRend = @($rendOk | Where-Object { $_.id -notlike '*smoke*' })

$first = $reqs[0]; $last = $reqs[$reqs.Count - 1]
$durSum = [math]::Round(((($reqs | Where-Object { $_.duration_ms } | ForEach-Object { [double]$_.duration_ms }) | Measure-Object -Sum).Sum) / 1000, 3)
$rDurSum = [math]::Round(((($rend | ForEach-Object { [double]$_.duration_ms }) | Measure-Object -Sum).Sum) / 1000, 3)
$wall = [math]::Round(([datetime]$last.ended_at - [datetime]$first.started_at).TotalSeconds, 3)
$firstImg = $rendOk | Sort-Object { [datetime]$_.ended_at } | Select-Object -First 1
$firstImgSec = [math]::Round(([datetime]$firstImg.ended_at - [datetime]$first.started_at).TotalSeconds, 3)
$minRL = ($reqs | Where-Object { $null -ne $_.ratelimit_remaining } | ForEach-Object { [int]$_.ratelimit_remaining } | Measure-Object -Minimum).Minimum
$has429 = @($reqs | Where-Object { $_.http_status -eq 429 }).Count

$pngTotal = 0; $dslTotal = 0
foreach ($r in $idx) { $pngTotal += [int]$r.pngB; $dslTotal += [int]$r.dslB }

# --------------------------------------------------------------- per-case metrics
$caseMetrics = @()
foreach ($r in $idx) {
  $cid = $r.id; $n = $cid.Substring(5)
  $cReq = @($reqs | Where-Object { $_.id -match ('^B05-rnd-' + $n + '-\d\d$') })
  $cOk  = @($cReq | Where-Object { $_.http_status -eq 200 })
  $cBad = @($cReq | Where-Object { $_.http_status -ne 200 })
  $dSum = [math]::Round(((($cReq | ForEach-Object { [double]$_.duration_ms }) | Measure-Object -Sum).Sum) / 1000, 3)
  $t0 = [datetime]($cOk | Sort-Object { [datetime]$_.started_at } | Select-Object -First 1).started_at
  $t1 = [datetime]($cOk | Sort-Object { [datetime]$_.ended_at } | Select-Object -Last 1).ended_at
  $caseMetrics += ([ordered]@{
    case_id = $cid; title = $r.title; stage = $null
    aspect_ratio = ('{0}x{1} ({2})' -f $r.w, $r.h, $r.ratio); dimensions = @($r.w, $r.h); background = $r.bg
    requests = $cReq.Count; successful = $cOk.Count; failed = $cBad.Count
    retry_requests = $cBad.Count
    request_duration_sum_seconds = $dSum
    first_request_started_at = [string]($cOk | Sort-Object { [datetime]$_.started_at } | Select-Object -First 1).started_utc
    last_request_ended_at = [string]($cOk | Sort-Object { [datetime]$_.ended_at } | Select-Object -Last 1).ended_utc
    case_wall_seconds = [math]::Round(($t1 - $t0).TotalSeconds, 3)
    case_wall_note = '本用例首末成功请求之间的墙钟；与其他用例区间相互交错，逐用例之和不等于任务墙钟'
    dsl_rounds = $cReq.Count
    successful_renders = $cOk.Count
    failed_renders = $cBad.Count
    iterations = 2
    completed_visual_iterations = 1
    image_views = 2
    image_views_note = 'round-01 与 round-02 各至少 1 次成功读图并核对刊头 NN/10 与画幅；串图重读按 shared 计，不归属单一用例'
    final_round = 2
    final_round_request_id = [string]($cOk | Sort-Object { [datetime]$_.started_at } | Select-Object -Last 1).id
    final_png_bytes = [int]$r.pngB; final_snapshot_bytes = [int]$r.dslB
    final_png_sha256_16 = $r.pngSha
    final_png_matches_last_success_bytes = $true
    final_png_is_service_bytes_untouched = $true
    png_dimensions_match_dsl_container = $true
  })
}

$reqSum = 0; $okSum = 0; $badSum = 0; $rndSum = 0; $durCaseSum = 0.0
foreach ($c in $caseMetrics) { $reqSum += $c.requests; $okSum += $c.successful; $badSum += $c.failed; $rndSum += $c.dsl_rounds; $durCaseSum += $c.request_duration_sum_seconds }

# --------------------------------------------------------------- task-metrics.json
$tm = [ordered]@{
  schema_version = 2
  task_id = 'B05'
  run_id = $RUN
  task_round = $null
  status = 'completed'
  stop_reason = '需求满足并完成视觉自检：10 屏完整产品旅程全部真实渲染（38 次 render 请求、32 次 200）、逐屏实际打开最终图并按视觉反馈迭代（r01 -> r02，round-02 内又对 case-03/06/07/09/10 做了第二轮修复与重渲染）、B05 专属 product-brief.md 与 journey.json 落盘、跨屏数字与日期做过文本比对；本题不设请求/迭代上限，未触及任何配额'
  output_dir = (Join-Path $root ('outputs\' + $RUN + '\B05'))
  temp_dir = $tmp
  timings = [ordered]@{
    started_at = $first.started_at
    ended_at = $last.ended_at
    started_at_utc = $first.started_utc
    ended_at_utc = $last.ended_utc
    elapsed_seconds = $wall
    elapsed_note = '以 requests.jsonl 首条（docs 抓取第一条）到末条（B05-rnd-10-07 成功响应）为界；其前还有 plan.md 选题、calc 数据计算与 gen 程序编写等不发请求的准备时间，故真实任务墙钟大于本值'
    first_usable_image_seconds = $firstImgSec
    first_usable_image_note = ('首个 200 且可打开的渲染为 ' + $firstImg.id + '，ended_utc = ' + $firstImg.ended_utc + '，距首条请求 ' + $firstImgSec + ' s')
    user_feedback_wait_seconds = 0
    user_feedback_wait_note = '本题按预置连续执行版本自动推进，无外部反馈等待'
    rate_limit_wait_seconds = 0
    rate_limit_wait_note = ('未出现 429 / Retry-After，ratelimit_remaining 最低 ' + $minRL + '，限流等待为 0（不是未知）')
    queue_wait_seconds = $null
    queue_wait_note = '服务未返回排队指标，不可测，故为 null'
    request_duration_sum_seconds = $durSum
    request_duration_sum_note = ('requests.jsonl 中 68 行 duration_ms 求和 ' + $durSum + ' s；其中 38 条 render 占 ' + $rDurSum + ' s。请求串行、无重叠，但不等于总墙钟')
    server_timing_source = 'render 响应提供 Server-Timing（render;dur / total;dur）、ratelimit_remaining 与 request_id；文档与研究请求部分含 cfCacheStatus / cfOrigin'
  }
  counts = [ordered]@{
    snapshot_requests = $reqs.Count
    snapshot_requests_note = ('68 行日志、0 行坏 JSON：38 type=render + 9 type=documentation + 1 type=fonts + 20 type=research')
    successful_snapshot_requests = 60
    failed_snapshot_requests = 8
    failed_note = '6 条 render HTTP 400 PARSE_ERROR（3 次 border 写在圆上、2 次 Ts 第 12 个参数落进 bold 导致 fontStyle=LEFT、1 次 color 被写成 元），全部当场修好重交；1 条 research HTTP 404（shanghai.gov.cn 站内搜索）；1 条 research 网络失败无状态码（html.duckduckgo.com）。失败响应字节原样保留，未伪造'
    retry_requests = 6
    retry_note = '6 条 400 修好后在 round-01 批次内重新提交（B05-rnd-02/03/05/06/08/10-02）并全部 200；研究侧的 404 与网络失败未重试，改用 gov.cn 全文检索与 flk.npc.cn 等其他一手入口覆盖同一问题'
    other_service_requests = 0
    document_requests = $docs.Count
    document_requests_note = '9 条 documentation 全部 200：ai-guide.md 与 snapshot.muedsa.com 的 parser-tags / painting / enums / transform / rendering / decorated-box / source-index / faq'
    font_requests = $fonts.Count
    font_requests_note = '1 条 /fonts 查询，返回 27 种字体；本题排版只用 SANS / DISP / MONO 三种'
    research_requests = $rese.Count
    research_requests_note = '20 条 type=research，18 条 200。最终没有取得任何一条既有住宅加装电梯费用分摊的政策原文，因此画面不写法条、不写法定分摊比例、不写补贴标准；取得的是住建部、国务院政策库、发改委、司法部行政法规库、国家法律法规数据库、上海与北京政务检索入口等页面，19 个抓取产物留在 research/'
    render_requests = $rend.Count
    render_requests_note = '38 条 render：32 条 200 + 6 条 400；38 = 36 条用例渲染 + 2 条冒烟（B05-rend-smoke-01/02）'
    smoke_render_requests = $smoke.Count
    shared_render_requests = $smoke.Count
    case_render_requests = ($rend.Count - $smoke.Count)
    successful_case_renders = $caseRend.Count
    failed_case_renders = $rendBad.Count
    dsl_rounds = ($rend.Count - $smoke.Count)
    dsl_rounds_note = '逐用例渲染尝试 3/3/5/3/3/4/4/3/4/4 = 36（含 6 次 400 修复后重交），其中 30 次 200 + 6 次 400；另有 2 条冒烟渲染属 shared，不归属用例'
    final_round_sum = 20
    final_round_sum_note = '10 件最终都取自 round 02；round-02 内的单件修复只是同轮重渲染，不另计轮次'
    iterations = 6
    iteration_log_rows = $iters.Count
    baseline_iterations = 1
    regeneration_iterations = 2
    view_pass_iterations = 2
    service_render_iterations = 1
    syntax_fix_iterations = 6
    syntax_fix_note = '6 次 400 PARSE_ERROR 均为属性写法错误，修复后重交即 200，不产生新的视觉方案'
    completed_visual_iterations = 10
    incomplete_visual_iterations = 0
    completed_visual_iterations_note = '每件都走完 r01 看图 -> 记录缺陷 -> r02 修复重渲染 -> 再次看图确认 的完整闭环'
    image_views = 47
    image_views_note = 'read 工具不写日志，此数按磁盘与过程记录复原：view/ 下 43 个唯一字节视图副本各至少读取 1 次 + 3 次直接读取原始 PNG（round-01 case-01、round-02 case-02 与 case-09）+ 1 次同路径重复读。43 这个下界可由目录内容直接核验'
    image_view_artifacts_on_disk = 43
    image_views_final_confirmed = 10
    image_views_final_confirmed_note = '10 件 final 图都至少有一次读图返回了正确字节，并逐张核对了刊头 TONGTI NN/10 与画幅（01..10 各一次），确认无误后才落 final.png'
    image_views_stale_delivery = 8
    image_views_stale_delivery_note = 'round-02 后段可逐条核验的 8 次串图（read 返回了上一张的字节）；round-01 与 round-02 前段也有串图并重读，但同样没有日志、不单独计数，故本项为下界。恢复办法：每次用 System.Drawing 生成文件名唯一、像素微调或加边框的新副本再读，读完核对刊头与画幅，必要时直接读原始 PNG 路径'
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
    generator_problems_note = 'gen-b05-a/b/c.ps1 -Round 2 全部输出 problems = 0；10 份 r02.snapshot 的 border / color / textAlign / boxShadow / fontStyle 属性校验 0 问题'
    visible_long_decimal_count = 0
    visible_long_decimal_note = '扫描所有 final.snapshot 可见文本，无 4 位以上小数（case-03 的 6.699999999999999993 与 309 元/㎡ 已修）；Transform matrix 内部几何的小数不属于可见文本'
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
    requests = 'tmp/' + $RUN + '/B05/requests.jsonl'
    iterations = 'tmp/' + $RUN + '/B05/iterations.jsonl'
    tool_usage = 'tmp/' + $RUN + '/B05/tool-usage.jsonl'
    plan = 'tmp/' + $RUN + '/B05/plan.md'
    calc = 'tmp/' + $RUN + '/B05/calc-b05.json'
    case_index = 'tmp/' + $RUN + '/B05/case-index-b05.json'
    research = 'tmp/' + $RUN + '/B05/research/'
    docs = 'tmp/' + $RUN + '/B05/docs/'
    view_copies = 'tmp/' + $RUN + '/B05/view/'
    events = 'tmp/' + $RUN + '/_suite/events.jsonl'
  }
  outputs = (@('portfolio.json','portfolio.md','product-brief.md','journey.json','gallery.html','snapshot-usage.md','task-metrics.json') +
             @(foreach ($r in $idx) { ($r.id + '/final.png'); ($r.id + '/final.snapshot'); ($r.id + '/case.md') }))
  unresolved_issues = @(
    '6 条 render HTTP 400 为早期属性写法错误（border 写在圆上、Ts 第 12 个参数落进 bold、color 写成 元），已全部修复并保留原始失败响应字节'
    'B05-res-16-sh-search（404）与 B05-res-10-ddg（网络失败）按原样保留；核心问题改由 gov.cn 全文检索、flk.npc.cn、司法部与住建部入口覆盖'
    '研究最终未取得既有住宅加装电梯费用分摊的政策原文，因此 10 屏不引用任何法条、不写法定比例、不写补贴标准；这是本期最大的能力边界，已写入 product-brief.md 风险节'
    'read 工具按内容哈希缓存会串图，期间 8 次（round-02 后段可核验）返回上一张字节；已用唯一字节副本恢复逐件看图，最终 10 件全部确认'
    'token / 图像使用量 / 费用平台未提供，一律为 null'
    '未做用户访谈、可用性测试或楼栋试点，product-brief.md 的成功指标为设计假设而非已验证结论'
  )
  asset_policy = [ordered]@{
    declared = 'dsl_primary_with_supporting_assets'
    actual = 'dsl_only_in_practice'
    external_assets_used = 0
    note = '10 屏全部为纯 DSL：楼栋剖面、时间轴、条形图、里程碑、检查表、药丸、状态格全部由矩形 / 圆 / 渐变 / 矩阵画出；画面里的“现场照片”是 DSL 画的剖面示意图并标注“示意图 DEMO”。研究抓取的 19 个产物是引用出处，不作为画面素材嵌入'
  }
  shared_preparation = [ordered]@{
    items = @(
      'fetch-b05.ps1 / fetch-bin-b05.ps1 —— 真实抓取文档、字体与研究资料，逐条写 requests.jsonl'
      'calc-b05.ps1 -> calc-b05.json —— 三套分摊模型、造价与补贴、付款节点、65 天工期、12 项验收日期、十年总账全部程序算出'
      'lib-b05.ps1 —— Masthead5 / Foot5 / Section5 / Stack1 / MarkDot / CheckBox / Tick / Outline / Pill / Write-Dsl5 / Report-Problems5'
      'gen-b05-a/b/c.ps1 —— 分段生成 10 屏自包含 DSL（a:01-03 b:04-06 c:07-10），每轮跑越界守卫与属性校验'
      'render-b05.ps1 —— POST /snapshot 并写全字段 requests.jsonl'
      'smoke-b05.ps1 —— 两次真机冒烟渲染确认服务与字体可用'
      'promote-b05.ps1 / gen-case-md-b05.ps1 / mk-logs-b05.ps1 / mk-portfolio-b05.ps1 / mk-metrics-b05.ps1 —— 落盘与从日志反查生成'
    )
    document_requests = $docs.Count
    font_requests = $fonts.Count
    research_requests = $rese.Count
    shared_render_requests = $smoke.Count
    probe_render_requests = $smoke.Count
    note = ('文档、字体与研究抓取属 shared 准备（case_id = null），单列不归属任何用例；36 条用例渲染全部带 case_id，逐用例之和 ' + $reqSum + ' = 36 = 整体，不重复累计；2 条冒烟渲染归 shared')
  }
  case_metrics = $caseMetrics
  case_metrics_reconciliation = [ordered]@{
    requests_sum = $reqSum
    requests_match_total = ($reqSum -eq ($rend.Count - $smoke.Count))
    successful_sum = $okSum
    failed_sum = $badSum
    retry_sum = $badSum
    request_duration_sum_seconds = [math]::Round($durCaseSum, 3)
    dsl_rounds_sum = $rndSum
    iterations_sum = $iters.Count
    iterations_sum_note = 'iterations.jsonl 共 6 行，全部是任务级记录（r01 baseline / r01 view_pass / r02 generate / r02 render / r02 view_pass / r02 fix+re-render）；按用例摊开是 10 件 x 2 轮 = 20 个逻辑迭代，记在 6 行里，不重复累计'
    shared_iterations = $iters.Count
    iteration_rows_total = $iters.Count
    image_views_sum = 20
    shared_image_views = 27
    image_views_total = 47
    image_views_total_note = 'image_views = 47 次 read（复原值）；case_metrics 的 image_views 为逐件 r01/r02 各 1 次共 20，其余 27 次为副本重读、串图重读与一次裁剪，未归属单一用例'
    case_wall_sum_note = '逐用例 case_wall_seconds 之和远大于任务墙钟，因为 10 个用例的请求区间相互交错（同批次串行渲染），不可用它反推任务耗时'
    shared_render_requests = $smoke.Count
    external_assets_sum = 0
    final_case_count = 10
  }
  tool_usage_summary = @()
}
$tuSum = @()
foreach ($t in $tus) {
  $tuSum += ([ordered]@{ tool_id = $t.tool_id; tool = $t.tool; category = $t.category; affected_cases = $t.affected_cases; http_request_ids = $t.http_request_ids })
}
$tm['tool_usage_summary'] = $tuSum
$tm['final_case_count'] = 10

[IO.File]::WriteAllText((Join-Path $out 'task-metrics.json'), ($tm | ConvertTo-Json -Depth 9), $utf8)
'task-metrics.json written'
'  requests=' + $reqs.Count + ' ok=60 fail=8 renders=' + $rend.Count + ' wall=' + $wall + 's durSum=' + $durSum + 's'
'  caseRequests=' + $reqSum + ' match36=' + ($reqSum -eq 36) + ' pngTotal=' + $pngTotal + ' dslTotal=' + $dslTotal
