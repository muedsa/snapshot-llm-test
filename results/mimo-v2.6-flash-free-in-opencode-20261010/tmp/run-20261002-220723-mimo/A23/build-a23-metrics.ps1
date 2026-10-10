# build-a23-metrics.ps1 - writes outputs/<run>/A23/task-metrics.json
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
$t = 'tmp\run-20261002-220723-mimo\A23'
$o = 'outputs\run-20261002-220723-mimo\A23'
$enc = New-Object System.Text.UTF8Encoding($false)

$st = [datetime]::Parse('2026-10-05T12:47:01+08:00')
$en = Get-Date
$enStr = $en.ToString('yyyy-MM-ddTHH:mm:sszzz')
$wall = [int][math]::Round(($en - $st).TotalMilliseconds)

$req = @(Get-Content "$t\requests.jsonl" | ForEach-Object { $_ | ConvertFrom-Json })
$rend = @($req | Where-Object { $_.type -eq 'render' })
$docs = @($req | Where-Object { $_.type -eq 'documentation' })
$reqSum = [math]::Round(($req | Measure-Object duration_ms -Sum).Sum, 1)
$renSum = [math]::Round(($rend | Measure-Object duration_ms -Sum).Sum, 1)
$docSum = [math]::Round(($docs | Measure-Object duration_ms -Sum).Sum, 1)
$pngBytes = ($rend | Measure-Object bytes -Sum).Sum

$probeEnd = [datetime]::Parse($rend[0].ended_utc).ToUniversalTime().AddHours(8)
$firstImg = $probeEnd.ToString('yyyy-MM-ddTHH:mm:ss.fff+08:00')
$firstImgMs = [int][math]::Round(($probeEnd - $st).TotalMilliseconds)
$c1 = $req | Where-Object { $_.id -eq 'A23c1' }
$delivEnd = [datetime]::Parse($c1.ended_utc).ToUniversalTime().AddHours(8)
$delivImg = $delivEnd.ToString('yyyy-MM-ddTHH:mm:ss.fff+08:00')
$delivMs = [int][math]::Round(($delivEnd - $st).TotalMilliseconds)

function Hms($ms) { $ts = New-Object TimeSpan(0,0,0,0,[int]$ms); return $ts.ToString('hh\:mm\:ss\.fff') }

$imgFiles = @(Get-ChildItem $o -Filter *.png | Sort-Object Name)
$imgRows = @()
foreach ($f in $imgFiles) {
  $fs = [IO.File]::OpenRead($f.FullName)
  $b = New-Object byte[] 33
  [void]$fs.Read($b, 0, 33)
  $fs.Close()
  $w = [BitConverter]::ToInt32(@($b[19], $b[18], $b[17], $b[16]), 0)
  $h = [BitConverter]::ToInt32(@($b[23], $b[22], $b[21], $b[20]), 0)
  $snapName = [IO.Path]::ChangeExtension($f.Name, '.snapshot')
  $imgRows += [pscustomobject][ordered]@{
    name      = $f.Name
    width     = $w
    height    = $h
    bytes     = $f.Length
    sha256    = (Get-FileHash $f.FullName -Algorithm SHA256).Hash
    color_type = $b[25]
    bit_depth  = $b[24]
    paired_dsl = $snapName
    paired_dsl_present = (Test-Path (Join-Path $o $snapName))
    bytes_identical_to_service_response = $true
  }
}
$snapBytes = (Get-ChildItem $o -Filter *.snapshot | Measure-Object Length -Sum).Sum

$m = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/task-metrics/v2'
  task = 'A23'
  task_title = '格式边界下的动画分镜交付'
  execution_mode = 'single_pass（能力判定 -> 参数化生成 -> 渲染 -> 视觉迭代 -> 交付；无预置轮次、无外部反馈回合）'
  started_at = $st.ToString('yyyy-MM-ddTHH:mm:sszzz')
  ended_at = $enStr
  timezone = 'UTC+08:00'
  wall_clock_total_ms = $wall
  wall_clock_total_human = Hms $wall
  first_usable_image_at = $firstImg
  first_usable_image_elapsed_ms = $firstImgMs
  first_usable_image_note = '第一张真实返回的图是透明通道探针 probe-alpha.png（渲染请求 A23p1），用于证实服务原生输出 RGBA；它不是交付物。'
  first_deliverable_image_at = $delivImg
  first_deliverable_image_elapsed_ms = $delivMs
  first_deliverable_image_note = '第一张交付图是 attempt-01 的 cover.png（渲染请求 A23c1）。'
  user_feedback_wait_ms = 0
  user_feedback_wait_reason = 'A23 执行期间没有任何用户回合，无等待。'
  rate_limit_or_queue_wait_ms = 0
  rate_limit_reason = '23 个请求全部一次成功，无 429、无 Retry-After、无排队、无重试；ratelimit_remaining 观测区间 113..119（16 行有值）。确未发生，故记 0 而非 null。'
  request_duration_sum_ms = $reqSum
  request_duration_sum_human = Hms $reqSum
  render_duration_sum_ms = $renSum
  documentation_duration_sum_ms = $docSum
  note_on_wall_clock = ('总墙钟 = A23 起止的真实经过时间（' + $st.ToString('yyyy-MM-ddTHH:mm:sszzz') + ' 起，到 ' + $enStr + '）。request_duration_sum 只是 23 个 HTTP 请求的服务端耗时之和 ' + $reqSum + 'ms，远小于墙钟；墙钟里绝大部分是能力判定、400000 次起始布局搜索、DSL 生成、看图与报告撰写。请求严格串行，无重叠，耗时之和本身也不等于任务总耗时。')

  requests = [pscustomobject][ordered]@{
    total = $req.Count
    render = $rend.Count
    documentation = $docs.Count
    documentation_breakdown = 'ai-guide.md 1 + openapi.yaml 1 + snapshot.muedsa.com 2 + guides/rendering 2 + fonts 1 = 7'
    render_breakdown = '透明探针 A23p1 1 + attempt-01 7 + attempt-02 7 + attempt-03 封面 1 = 16'
    succeeded = @($req | Where-Object { $_.http_status -eq 200 }).Count
    failed = @($req | Where-Object { $_.http_status -ne 200 }).Count
    retried = 0
    rate_limited = 0
    rate_limit_events = 0
    http_status_observed = 200
    ratelimit_remaining_observed = @(113, 119)
    render_response_bytes = $pngBytes
    duration_ms = $reqSum
    render_duration_ms = $renSum
    documentation_duration_ms = $docSum
    min_render_ms = [math]::Round(($rend | Measure-Object duration_ms -Minimum).Minimum, 1)
    max_render_ms = [math]::Round(($rend | Measure-Object duration_ms -Maximum).Maximum, 1)
    request_ids_render = @($rend | ForEach-Object { $_.id })
    log_file = 'tmp/run-20261002-220723-mimo/A23/requests.jsonl'
  }

  dsl = [pscustomobject][ordered]@{
    versions = 3
    version_note = 'v01 环形起始布局 -> v02 径向分散起始布局（+6666 样本重叠硬校验）-> v03 封面字号与箭头字形（+单行文本宽度护栏）。第 4 行迭代 a23-v04 是查看工具重试，不改 DSL；另有一次仅改 frame-data.json 文案的再生成，7 份 .snapshot 与 7 张 PNG 字节全部未变，不计为新版本。'
    snapshot_files = @('cover.snapshot', 'frame-01.snapshot', 'frame-02.snapshot', 'frame-03.snapshot', 'frame-04.snapshot', 'frame-05.snapshot', 'frame-06.snapshot')
    snapshot_bytes_total = $snapBytes
    tags_used = @('Snapshot', 'Container', 'Stack', 'Positioned', 'Text')
    image_tags = 0
    transform_tags = 0
    svg_gif_cmyk_tokens = 0
    forbidden = $false
    text_in_frames = 0
    text_in_cover = 9
    root_container_color_in_frames = 0
    generated_by = 'tmp/run-20261002-220723-mimo/A23/gen-a23.ps1（参数化生成，未嵌入任何预渲染帧）'
  }

  images = [pscustomobject][ordered]@{
    delivered = $imgRows.Count
    files = $imgRows
    all_real_png_signature = $true
    all_paired_dsl = (@($imgRows | Where-Object { -not $_.paired_dsl_present }).Count -eq 0)
    all_bytes_identical_to_service_response = $true
    cover_size = '1200x800'
    frame_size = '600x600'
    color_type = 6
    bit_depth = 8
    post_processing = 'none（服务原始 PNG 字节原样保存，未做任何后处理）'
    note = 'attempt-01 的 7 张与 attempt-02 的封面已归档在 tmp/.../A23/attempt-01-ring/ 与 attempt-02-cover-footer-overflow/，未被覆盖。'
  }

  viewing = [pscustomobject][ordered]@{
    calls_total = 26
    calls_returned_fresh_pixels = 13
    calls_returned_stale_buffer = 13
    final_images_individually_viewed = 7
    contact_sheets_viewed = 1
    view_files = @(
      'tmp/run-20261002-220723-mimo/A23/contact-sheet.png'
      'tmp/run-20261002-220723-mimo/A23/finalcover-135845239.png'
      'outputs/run-20261002-220723-mimo/A23/cover.png'
      'outputs/run-20261002-220723-mimo/A23/frame-01.png'
      'outputs/run-20261002-220723-mimo/A23/frame-02.png'
      'outputs/run-20261002-220723-mimo/A23/frame-03.png'
      'outputs/run-20261002-220723-mimo/A23/frame-04.png'
      'outputs/run-20261002-220723-mimo/A23/frame-05.png'
      'outputs/run-20261002-220723-mimo/A23/frame-06.png'
    )
    pixel_scans_not_counted = $true
    note = '最终 7 张图在 2026-10-05T13:58:46+08:00 至 14:05:00+08:00 之间逐张用图像查看器单独打开确认（cover + 6 帧），另打开接触表 contact-sheet.png 全览 6 帧与真实透明（棋盘格透出）。期间查看器一度返回陈旧缓冲 13 次，已在 iterations.jsonl 的 a23-v04 如实记录，并用 GDI+ 逐列字形游程扫描 + ascii-a23.ps1 文本点阵成像做独立交叉验证；GDI+ / 像素统计本身不计入看图次数。看图精确时钟未全部采集，有文件时间戳的用时间戳，其余按分钟级时间窗记录，不编造单次时刻。'
  }

  iterations = [pscustomobject][ordered]@{
    total = 4
    full_visual = 2
    by_type = [pscustomobject]@{
      baseline = 1
      visual = 2
      'syntax-fix' = 0
      alternative = 0
      retry = 1
      'requirement-change' = 0
    }
    rows_logged = 4
    log_file = 'tmp/run-20261002-220723-mimo/A23/iterations.jsonl'
    note = '完整视觉迭代 2 次：a23-v02（看旧图发现单元互相压盖 -> 改起始布局 -> 重渲染 -> 看图比较）、a23-v03（看旧图发现封面页脚缺「面」字 + 推进标记像占位符 -> 改字号与字形 -> 重渲染 -> 看图比较）。a23-v01 是 baseline；a23-v04 是查看工具重试，不改画面、不计视觉迭代。'
    baseline_note = 'a23-v01 该版本只做了 GDI+ 与几何程序化解析，未用图像查看器打开；这是本任务唯一一次未配看图的版本评估，已如实记入 iterations.jsonl。该版本的 7 张图不是最终交付物。'
  }

  quality = [pscustomobject][ordered]@{
    deliverables_required = 12
    deliverables_present = 12
    deliverables_detail = '7 组 PNG+DSL（cover + frame-01..06）+ limitations.md + frame-data.json + timing.json + snapshot-usage.md + task-metrics.json'
    deliverables_all_present = $true
    generator_problems = 0
    generator_checks = @(
      '12 单元 / 60x60 / 7 种颜色 / 6 帧一致'
      '72 个位置全部在 600x600 内'
      '路径重叠：101 个 t 采样 x 66 单元对 = 6666 样本，命中 0（attempt-01 为 596）'
      '6 张交付帧重叠对 0（attempt-01 为 25 对）'
      'frame-01 最小圆心间距 103.56px > 单元边长 60px'
      '末帧关于 x=300 镜像对称，屋檐 300 / 主体 180 / 出挑 60'
      '五步位移 30.45~30.46px（匀速）'
      '循环跳变 104.3px vs 步长 30.5px -> seamless = false（不宣称无缝）'
      '封面 1200x800、含「从结构到画面」、分镜 01/03/06'
      '封面单行文本宽度护栏 9/9 通过'
      '帧 DSL 无 <Text>、无 transform、根 Container 无 color'
    )
    overlap_samples_checked = 6666
    overlap_samples_hit = 0
    opaque_pixel_sample_range = '4595..4716（attempt-01 为 3441..4731，收敛后差异 <2%）'
    transparency_evidence = '6 帧四角 alpha=0、有 clear 像素、非全不透明；探针 A23p1 实测 #FF000080 -> A=128、#00FF0000 -> A=0、画布空隙 A=0，IHDR colorType=6'
    cover_text_evidence = '页脚第一行墨迹 x[73..1047] 宽 975 <= 容器 1056；末三字形游程 982..994(B) / 1001..1023(封) / 1026..1047(面)'
    arrow_evidence = '逐列墨迹图呈现水平杆 + 向右收口的头部，确认渲染为 → 而非豆腐块'
    report_files = @('outputs/run-20261002-220723-mimo/A23/snapshot-usage.md', 'outputs/run-20261002-220723-mimo/A23/limitations.md')
    unresolved = @(
      '文字可编辑 SVG、CMYK 印刷稿、单文件 GIF 三项原生不支持，需在服务外完成（见 limitations.md）'
      '循环跳变存在，timing.json 中 seamless = false；如需真正无缝需增加回程关键帧并给出证据'
      '过程偏差：attempt-01 的 .snapshot 未先归档即被生成器原地重写，该版 DSL 文本未能保留（7 张 PNG 字节已归档）'
      'token / 图像输入 / 费用平台未提供，记 null'
    )
  }

  capability_findings = [pscustomobject][ordered]@{
    svg = [pscustomobject]@{ supported = $false; evidence = '渲染指南 element.type 分支仅 png/jpg/webp，else -> error("Unsupported image type")；openapi.yaml (?i)svg 命中 0；/snapshot 200 响应仅 image/png|jpeg|webp' }
    cmyk = [pscustomobject]@{ supported = $false; evidence = 'openapi.yaml (?i)cmyk 与 (?i)icc 命中 0；渲染指南「颜色使用 0xAARRGGBB」，无色彩空间/ICC 字段' }
    gif_animation = [pscustomobject]@{ supported = $false; evidence = 'openapi.yaml (?i)gif/animat/keyframe/timeline/duration/frame 命中全部为 0；仅 10 个端点，无多帧接口；/snapshot 为单次单图' }
    transparent_png = [pscustomobject]@{ supported = $true; evidence = '渲染指南「Parser 的 <Snapshot> 默认背景则为透明」+ 探针 A23p1 实测 RGBA' }
    png_cover = [pscustomobject]@{ supported = $true; evidence = '<Snapshot type="png"> 为规范示例；element.type "png" -> ContentType.Image.PNG；实测 cover.png 1200x800 colorType=6' }
    substitutes_delivered = '1200x800 RGB cover.png + 6 张 600x600 透明 frame-0N.png + timing.json（250ms/帧、6 帧循环、帧序）+ frame-data.json；未合成 GIF、未矢量化、未转换 CMYK、未创建任何假的目标格式文件'
  }

  resource_consumption = [pscustomobject][ordered]@{
    tokens = $null
    tokens_unit = $null
    image_inputs = $null
    image_inputs_unit = $null
    cost = $null
    cost_currency = $null
    source = 'not_provided'
    reason = '本执行环境与 open-snapshot 服务均未提供 A23 的 token、图像输入或费用计量指标；按约定记 null，不以字符数、图片字节数或账号余量估算。'
    covered_scope = 'A23 的 23 个 HTTP 请求（16 次渲染 + 7 次文档/字体）与 26 次图像查看调用'
    quality_vs_cost = '质量（generator problems=0、6666 路径样本重叠 0、12/12 交付齐全、7/7 最终图逐张看图）与消耗分开说明；消耗不可得不影响质量结论。'
  }

  unresolved_items = @(
    '无阻塞项：A23 已 completed，problems = 0，12/12 指定交付齐全'
    'SVG / CMYK / 单文件 GIF 三项原生不支持，替代交付已完成，外部后续工作见 limitations.md'
    '循环不无缝已在 timing.json 中显式声明（seamless = false），不宣称无缝'
    'attempt-01 的 .snapshot 未归档即被重写（过程偏差，已记录）'
    'token / 图像输入 / 费用平台未提供，记 null'
  )
}

$out = "$o\task-metrics.json"
$json = $m | ConvertTo-Json -Depth 8
[IO.File]::WriteAllText($out, $json + "`n", $enc)

'wrote ' + $out + '  bytes=' + (Get-Item $out).Length
''
'--- round trip ---'
$chk = Get-Content $out -Raw | ConvertFrom-Json
'  task                = ' + $chk.task
'  started/ended       = ' + $chk.started_at + '  ->  ' + $chk.ended_at
'  wall_clock_total_ms = ' + $chk.wall_clock_total_ms + '  (' + $chk.wall_clock_total_human + ')'
'  first img elapsed   = ' + $chk.first_usable_image_elapsed_ms + ' ms'
'  requests            = ' + $chk.requests.total + '  (render ' + $chk.requests.render + ' / doc ' + $chk.requests.documentation + ')  failed=' + $chk.requests.failed
'  request_duration    = ' + $chk.request_duration_sum_ms + ' ms'
'  iterations          = total ' + $chk.iterations.total + '  full_visual ' + $chk.iterations.full_visual
'  views               = ' + $chk.viewing.calls_total + ' (fresh ' + $chk.viewing.calls_returned_fresh_pixels + ')'
'  images delivered    = ' + $chk.images.delivered + '  all paired=' + $chk.images.all_paired_dsl
'  deliverables        = ' + $chk.quality.deliverables_present + '/' + $chk.quality.deliverables_required
'  tokens / cost       = ' + $chk.resource_consumption.tokens + ' / ' + $chk.resource_consumption.cost
'  Chinese round trip  = ' + ($chk.quality.transparency_evidence -match 'A=128')
