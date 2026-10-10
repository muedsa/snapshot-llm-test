# close-a23.ps1 - finish A23, open A24
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
$enc = New-Object System.Text.UTF8Encoding($false)

$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
$suiteTmp = 'tmp\run-20261002-220723-mimo\_suite'
$ssPath = 'outputs\run-20261002-220723-mimo\_suite\suite-state.json'

# ---------- 1. events.jsonl : 48 completed A23, 49 started A24 ----------
$note48 = 'A23 格式边界动画分镜交付完成：19 个产物 = 7 组 PNG+DSL（cover 1200x800 RGB + frame-01..06 各 600x600 RGBA 透明）+ limitations.md + frame-data.json + timing.json + snapshot-usage.md + task-metrics.json，12/12 指定交付齐全，生成器 problems = 0。'
$note48 += '能力判定全部基于真实取回的文档与真实渲染：渲染指南 element.type 分支只有 png/jpg/webp 且兜底 else -> error("Unsupported image type")；openapi.yaml 全文 (?i)svg/cmyk/icc/gif/animat/keyframe/timeline/duration/frame 命中全部为 0；仅 10 个端点且无多帧接口，故 SVG / CMYK / 单文件 GIF 三项原生不支持，PNG 封面与透明 PNG 原生支持。'
$note48 += '透明性用真实探针 A23p1 证实：Format32bppArgb、#FF000080 得 A=128、#00FF0000 得 A=0、画布空隙 A=0。'
$note48 += '授权替代全部交付：cover.png + 6 张透明关键帧 + timing.json（250ms/帧、6 帧循环、帧序 1->6、seamless=false 明写循环跳变 104.3px vs 步长 30.5px）+ frame-data.json；未合成 GIF、未矢量化、未转换 CMYK、未创建任何假的目标格式文件。'
$note48 += '画面要求：6 帧各恰 12 个 60x60 单元、7 色一致、帧内 0 个 Text 标签；起始布局用 design-a23.ps1 seed 20261005 搜 400000 组、3828 组可行、取 frame-01 最小圆心间距 103.56px 大于单元边长 60px；101 个 t 采样 x 66 单元对 = 6666 样本重叠 0（attempt-01 为 596、交付帧 25 对），杜绝单元压盖消失；末帧关于 x=300 镜像对称、屋檐 300 / 主体 180 / 出挑 60，可读作小屋或人形；五步位移 30.45/30.46px 匀速连续。'
$note48 += '封面标题「从结构到画面」大号可读；页脚 fs26 缺「面」字经查看发现后改 fs24（墨迹 975 小于等于 1056，字形游程 1026..1047 确为「面」），推进标记由占位方块改 Text 箭头，生成器新增 9/9 单行文本宽度护栏。'
$note48 += '请求 23 行全 200 = 渲染 16 次（探针 1 + attempt-01 7 + attempt-02 7 + attempt-03 1，38696.4ms / 301581 字节，最小 1032.1 最大 5452ms）+ 文档 7 次（13746.8ms），合计 52443.2ms；失败 0、重试 0、限流 0（ratelimit_remaining 113..119）。'
$note48 += '看图 26 次 = fresh 13 + 陈旧缓冲 13；查看器故障期间用 GDI+ 逐列字形游程 + ascii-a23.ps1 文本点阵做独立交叉证据，恢复后 cover + 6 帧逐张单独打开 + 接触表均确认真实像素。迭代 4 行：baseline 1 / visual 2 / retry 1，完整视觉迭代 2。'
$note48 += '过程偏差如实记录：attempt-01 的 .snapshot 未先归档即被生成器原地重写（7 张 PNG 字节已归档），且该版本只做程序化解析未看图。'
$note48 += '交付 PNG 全为服务原始响应字节原样保存、无后处理，SHA-256 前缀 cover=2B7D507D16501E70、f01=D3DBA9F0DC71DFD5、f02=EA44A9CE89C1FFE6、f03=321B368436C555E8、f04=2898F7A9C93B9FD3、f05=292D26CF75650D96、f06=2C059DD7C15C2A91。墙钟 5150.4s。'

$ev48 = [pscustomobject][ordered]@{
  seq = 48
  ts = $now
  type = 'task_completed'
  task = 'A23'
  artifacts = 19
  renders = 16
  views = 26
  visual_iterations = 2
  rounds = 0
  note = $note48
}

$ev49 = [pscustomobject][ordered]@{
  seq = 49
  ts = $now
  type = 'task_started'
  task = 'A24'
  note = 'A24 双团队约束下的发布作战计划：读取 tasks/A24-release-plan-capstone 的 TASK.md / AGENTS.md / task.json 与 inputs 后按题面推进，沿用同一 run_id 的 outputs/<run_id>/A24/ 与 tmp/<run_id>/A24/，最低 3 张最终 PNG。'
}

[string[]]$lines = @((ConvertTo-Json $ev48 -Depth 5 -Compress), (ConvertTo-Json $ev49 -Depth 5 -Compress))
[IO.File]::AppendAllLines((Join-Path $suiteTmp 'events.jsonl'), $lines, $enc)
'events.jsonl now ' + (Get-Content (Join-Path $suiteTmp 'events.jsonl')).Count + ' lines'

# ---------- 2. suite-state.json : A23 -> completed, current -> A24 ----------
$ss = Get-Content $ssPath -Raw | ConvertFrom-Json
$a23 = $ss.tasks | Where-Object { $_.id -eq 'A23' }
$a23.status = 'completed'
$a23.ended_at = $now
$a23.artifacts = @(
  'A23/cover.png', 'A23/cover.snapshot',
  'A23/frame-01.png', 'A23/frame-01.snapshot',
  'A23/frame-02.png', 'A23/frame-02.snapshot',
  'A23/frame-03.png', 'A23/frame-03.snapshot',
  'A23/frame-04.png', 'A23/frame-04.snapshot',
  'A23/frame-05.png', 'A23/frame-05.snapshot',
  'A23/frame-06.png', 'A23/frame-06.snapshot',
  'A23/limitations.md', 'A23/frame-data.json', 'A23/timing.json',
  'A23/snapshot-usage.md', 'A23/task-metrics.json'
)
$a23.visual_review_evidence = @(
  'tmp/run-20261002-220723-mimo/A23/contact-sheet.png viewed 2026-10-05T13:31:40+08:00 (6 关键帧全览，棋盘格透出即真实透明)',
  'outputs/run-20261002-220723-mimo/A23/cover.png viewed 2026-10-05T13:33:30+08:00 (attempt-02，发现页脚缺「面」字)',
  'tmp/run-20261002-220723-mimo/A23/crop-footer-end.png viewed 2026-10-05T13:35:10+08:00 (放大确认页脚截断)',
  'outputs/run-20261002-220723-mimo/A23/frame-01.png viewed 2026-10-05T13:36:20+08:00 (最分散帧 12 块不接触)',
  'tmp/run-20261002-220723-mimo/A23/finalcover-135845239.png viewed 2026-10-05T13:58:46+08:00 (最终封面，两行页脚与箭头全部完整)',
  'tmp/run-20261002-220723-mimo/A23/contact-sheet.png re-viewed 2026-10-05T14:00:00+08:00 (最终 6 帧全览)',
  'outputs/run-20261002-220723-mimo/A23/frame-01.png viewed 2026-10-05T14:02:00+08:00 (最终版)',
  'outputs/run-20261002-220723-mimo/A23/frame-02.png viewed 2026-10-05T14:03:00+08:00 (最终版)',
  'outputs/run-20261002-220723-mimo/A23/frame-03.png viewed 2026-10-05T14:03:30+08:00 (最终版)',
  'outputs/run-20261002-220723-mimo/A23/frame-04.png viewed 2026-10-05T14:04:00+08:00 (最终版)',
  'outputs/run-20261002-220723-mimo/A23/frame-05.png viewed 2026-10-05T14:04:30+08:00 (最终版)',
  'outputs/run-20261002-220723-mimo/A23/frame-06.png viewed 2026-10-05T14:05:00+08:00 (最终版，12 块拼成对称可识别图形)'
)
$a23.unresolved_issues = @(
  'SVG / CMYK 印刷稿 / 单文件 GIF 三项服务原生不支持，已按授权交付替代物，外部后续工作见 A23/limitations.md',
  '循环不无缝：timing.json seamless=false，frame-06 到 frame-01 跳变 104.3px vs 正常步长 30.5px，如实声明未宣称无缝',
  '过程偏差：attempt-01 的 .snapshot 未先归档即被生成器原地重写，该版 DSL 文本未保留（7 张 PNG 字节已归档到 tmp/run-20261002-220723-mimo/A23/attempt-01-ring/）',
  'attempt-01 版本只做程序化解析未看图（非交付版），已记入 iterations.jsonl 的 a23-v01.observed_problems',
  'token / 图像输入 / 费用平台未提供，task-metrics.json 记 null'
)
$a23.resume_notes = 'completed；无阻塞，可继续 A24。'

$a24 = $ss.tasks | Where-Object { $_.id -eq 'A24' }
$a24.status = 'in_progress'
$a24.started_at = $now

$ss.current_task = 'A24'
$ss.current_round = $null
$ss.current_case = $null
$ss.updated_at = $now
$ss.last_checkpoint = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000027.json'

$json = ConvertTo-Json $ss -Depth 10
[IO.File]::WriteAllText($ssPath, $json + "`n", $enc)
'updated suite-state.json  bytes=' + (Get-Item $ssPath).Length

# ---------- 3. checkpoint state-000027.json ----------
$ckpt = [pscustomobject][ordered]@{
  schema_version = $ss.schema_version
  suite_version = $ss.suite_version
  run_id = $ss.run_id
  profile = $ss.profile
  status = $ss.status
  snapshot_at = $now
  checkpoint_id = 'state-000027.json'
  checkpoint_seq = 27
  event_seq = 49
  current_task = 'A24'
  current_status = 'in_progress'
  last_checkpoint = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000027.json'
  task_status_counts = $null
  tasks_completed = 23
  tasks_in_progress = 1
  checkpoint_note = 'A23 完成并关闭（events 48），A24 已开启（events 49）。A23：19 个产物、12/12 指定交付、problems=0、请求 23 全 200、看图 26 次、完整视觉迭代 2。'
  suite_state = $ss
  source_state_copy = $ssPath
}
$counts = $ss.tasks | Group-Object status | ForEach-Object { [pscustomobject]@{ status = $_.Name; count = $_.Count } }
$ckpt.task_status_counts = [pscustomobject]@{}
foreach ($c in $counts) { $ckpt.task_status_counts | Add-Member -NotePropertyName $c.status -NotePropertyValue $c.count }

$ckPath = Join-Path $suiteTmp 'checkpoints\state-000027.json'
if (Test-Path $ckPath) { throw "checkpoint already exists, refusing to overwrite: $ckPath" }
$json2 = ConvertTo-Json $ckpt -Depth 12
[IO.File]::WriteAllText($ckPath, $json2 + "`n", $enc)
'wrote ' + $ckPath + '  bytes=' + (Get-Item $ckPath).Length

# ---------- verify ----------
''
'--- verify ---'
$chk = Get-Content $ssPath -Raw | ConvertFrom-Json
$cmpl = @($chk.tasks | Where-Object { $_.status -eq 'completed' }).Count
'  suite status        = ' + $chk.status
'  current_task        = ' + $chk.current_task
'  last_checkpoint     = ' + $chk.last_checkpoint
'  updated_at          = ' + $chk.updated_at
'  completed / total   = ' + $cmpl + ' / ' + $chk.tasks.Count
$chk.tasks | Group-Object status | ForEach-Object { '    ' + $_.Name + ' = ' + $_.Count }
$a = $chk.tasks | Where-Object { $_.id -eq 'A23' }
'  A23 status          = ' + $a.status + '  ended ' + $a.ended_at
'  A23 artifacts       = ' + $a.artifacts.Count
'  A23 review evidence = ' + $a.visual_review_evidence.Count
'  A23 unresolved      = ' + $a.unresolved_issues.Count
$ck = Get-Content $ckPath -Raw | ConvertFrom-Json
'  checkpoint seq      = ' + $ck.checkpoint_seq + '  event_seq=' + $ck.event_seq + '  current=' + $ck.current_task
'  checkpoint counts   = ' + ((ConvertTo-Json $ck.task_status_counts -Compress))
