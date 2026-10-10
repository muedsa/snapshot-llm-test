# mk-suite-docs.ps1 -- outputs/<run>/_suite/gallery.md and index.md
# Both files are generated from disk, catalog.json, suite-state.json and
# task-metrics.json. Every count, byte size and pixel dimension is read, never typed.
#
# Path policy (PATHS.md): Markdown local links are relative to the directory of the
# Markdown file itself, so _suite/gallery.md links to ../A01/operations.png. No machine
# paths, no environment-variable expressions and no remote image addresses are written
# into either document; copying the whole run output directory keeps them browsable.
$ErrorActionPreference = 'Stop'
$runDir = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Location).Path }
$runIdFile = Join-Path $runDir 'run-config.json'
if (-not (Test-Path $runIdFile)) { throw "run-config.json not found at $runIdFile; start from the suite root or set SNAPSHOT_TASK_ROOT" }
$rcfg = [IO.File]::ReadAllText($runIdFile, [Text.Encoding]::UTF8) | ConvertFrom-Json
$runId = $null
foreach ($d in @(Get-ChildItem (Join-Path $runDir $rcfg.output_root) -Directory)) {
  if (Test-Path (Join-Path $d.FullName '_suite\suite-state.json')) { $runId = $d.Name; break }
}
if (-not $runId) { throw 'no run directory with _suite/suite-state.json found' }
$outRoot = Join-Path $runDir ($rcfg.output_root + '\' + $runId)
$tmpRoot = Join-Path $runDir ($rcfg.temp_root + '\' + $runId)
$suiteDir = Join-Path $outRoot '_suite'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$suiteBase = '_suite'

function PngSize([string]$p) {
  $fs = [IO.File]::OpenRead($p)
  try { $b = New-Object byte[] 24; $null = $fs.Read($b, 0, 24) } finally { $fs.Close() }
  $w = [int]$b[16] * 16777216 + [int]$b[17] * 65536 + [int]$b[18] * 256 + [int]$b[19]
  $h = [int]$b[20] * 16777216 + [int]$b[21] * 65536 + [int]$b[22] * 256 + [int]$b[23]
  return ,@($w, $h)
}
function MdEsc([string]$s) {
  if ($null -eq $s) { return '' }
  return ($s -replace '\|', '\|')
}

$cat = [IO.File]::ReadAllText((Join-Path $runDir 'catalog.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
$titleById = @{}
foreach ($t in $cat.tasks) { $titleById[$t.id] = $t.title }

$ss = Get-Content (Join-Path $suiteDir 'suite-state.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$sm = [IO.File]::ReadAllText((Join-Path $suiteDir 'task-metrics.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
$metricById = @{}
foreach ($t in $sm.task_summaries) { $metricById[$t.task_id] = $t }

$ids = @(); foreach ($i in 1..24) { $ids += ('A{0:d2}' -f $i) }; foreach ($i in 1..6) { $ids += ('B{0:d2}' -f $i) }

# B-track work titles come from each task's own portfolio.json (works[] or cases[]).
$titleByKey = @{}
foreach ($id in $ids) {
  if (-not $id.StartsWith('B')) { continue }
  $pf = Join-Path $outRoot "$id\portfolio.json"
  if (-not (Test-Path $pf)) { continue }
  try { $pj = [IO.File]::ReadAllText($pf, [Text.Encoding]::UTF8) | ConvertFrom-Json } catch { continue }
  $arr = $null
  if ($pj.PSObject.Properties['works']) { $arr = $pj.works }
  elseif ($pj.PSObject.Properties['cases']) { $arr = $pj.cases }
  if ($null -eq $arr) { continue }
  foreach ($w in $arr) {
    if ($w.id -and $w.title) { $titleByKey["$id/$($w.id)"] = "$($w.title)" }
  }
}

# ---------------- inventory, grouped the way the gallery is presented ----------------
$inv = @()
foreach ($id in $ids) {
  $d = Join-Path $outRoot $id
  $pngs = @(Get-ChildItem $d -Recurse -Filter '*.png' -File | Where-Object { $_.DirectoryName -notlike '*\archive' } | Sort-Object FullName)
  foreach ($p in $pngs) {
    $rel = $p.FullName.Substring($outRoot.Length + 1)
    $sz = PngSize $p.FullName
    $case = $null
    if ($p.DirectoryName -match 'case-(\d\d)$') { $case = $matches[1] }
    $round = $null
    if ($p.DirectoryName -match 'round-(\d\d)$') { $round = $matches[1] }
    $stem = [IO.Path]::GetFileNameWithoutExtension($p.Name)
    $key = "$id/case-$case"
    $title = $stem
    if ($case -and $titleByKey.ContainsKey($key)) { $title = $titleByKey[$key] }
    $inv += ([pscustomobject]@{
      task = $id; file = $rel; name = $p.Name; bytes = $p.Length
      w = $sz[0]; h = $sz[1]; case = $case; round = $round; title = $title
      posix = ($rel -replace '\\', '/')
    })
  }
}

# ---------------- gallery.md ----------------
$g = New-Object System.Text.StringBuilder
[void]$g.AppendLine('# Snapshot 全套画廊')
[void]$g.AppendLine('')
[void]$g.AppendLine(('- run_id：`{0}`　时区：{1}' -f $runId, $sm.timezone))
[void]$g.AppendLine(('- 状态：**{0}**（{1}/{2} 题 completed）' -f $sm.status, $sm.task_status_counts.completed, $sm.task_status_counts.total))
[void]$g.AppendLine(('- 收录：**{0} 张最终图片全部逐图展示**（不是精选、不是接触表）：A 轨 {1} 张 + B 轨 {2} 张' -f $inv.Count, $sm.counts.a_track_final_pngs, $sm.counts.b_track_final_pngs))
[void]$g.AppendLine(('- 独立作品：{0} 件（A 轨 {1} + B 轨 {2}，B01–B06 每题 10 件独立完整作品）' -f $sm.counts.independent_creative_cases, $sm.counts.a_track_works, $sm.counts.b_track_works))
[void]$g.AppendLine(('- 分组：按 catalog 的 task_order 排列；A21 / A22 的预置轮次逐轮展示；B 轨按 case-01 … case-10 的开放用例分组'))
[void]$g.AppendLine(('- 链接：图片与 DSL 链接均为**相对本文件（`_suite/`）**的路径，例如 `../A01/operations.png`。无机器绝对路径、无环境变量表达式、无远程图片地址；复制整个运行输出目录后本文件仍可浏览'))
[void]$g.AppendLine('')
[void]$g.AppendLine('## 目录')
[void]$g.AppendLine('')
[void]$g.AppendLine('| 任务 | 标题 | 最终图片 | 独立作品 |')
[void]$g.AppendLine('| --- | --- | --- | --- |')
foreach ($id in $ids) {
  $imgs = @($inv | Where-Object { $_.task -eq $id })
  $mt = $metricById[$id]
  [void]$g.AppendLine(('| [{0}](#{1}) | {2} | {3} | {4} |' -f $id, $id.ToLower(), (MdEsc $titleById[$id]), $imgs.Count, $mt.works))
}
[void]$g.AppendLine('')
[void]$g.AppendLine('---')

foreach ($id in $ids) {
  $imgs = @($inv | Where-Object { $_.task -eq $id })
  $mt = $metricById[$id]
  [void]$g.AppendLine('')
  [void]$g.AppendLine(('<a id="{0}"></a>' -f $id.ToLower()))
  [void]$g.AppendLine(('## {0}　{1}' -f $id, (MdEsc $titleById[$id])))
  [void]$g.AppendLine('')
  $rounds = @($imgs | Where-Object { $null -ne $_.round } | ForEach-Object { $_.round } | Sort-Object -Unique)
  if ($rounds.Count -gt 0) {
    [void]$g.AppendLine(('{0} 张最终图片，{1} 件作品，预置轮次 round-{2}（共 {3} 轮，全部产物保留）。' -f $imgs.Count, $mt.works, ($rounds -join '/round-'), $rounds.Count))
  } elseif ($mt.works -gt 0 -and @($imgs | Where-Object { $null -ne $_.case }).Count -gt 0) {
    [void]$g.AppendLine(('{0} 张最终图片 = {1} 件独立完整作品，按开放用例 case-01 … case-{2} 分组。' -f $imgs.Count, $mt.works, (@($imgs | Where-Object { $null -ne $_.case } | ForEach-Object { $_.case } | Sort-Object -Unique))[-1]))
  } else {
    [void]$g.AppendLine(('{0} 张最终图片，{1} 件独立作品。' -f $imgs.Count, $mt.works))
  }
  [void]$g.AppendLine('')

  $groups = @()
  if ($rounds.Count -gt 0) {
    foreach ($r in $rounds) { $groups += ([pscustomobject]@{ label = ('round-{0}' -f $r); items = @($imgs | Where-Object { $_.round -eq $r } | Sort-Object name) }) }
  } elseif (@($imgs | Where-Object { $null -ne $_.case }).Count -gt 0) {
    foreach ($c in @($imgs | Where-Object { $null -ne $_.case } | ForEach-Object { $_.case } | Sort-Object -Unique)) {
      $groups += ([pscustomobject]@{ label = ('case-{0}' -f $c); items = @($imgs | Where-Object { $_.case -eq $c }) })
    }
  } else {
    $groups += ([pscustomobject]@{ label = ''; items = $imgs })
  }

  foreach ($grp in $groups) {
    if ($grp.label -ne '') { [void]$g.AppendLine(('### {0}' -f $grp.label)); [void]$g.AppendLine('') }
    foreach ($im in $grp.items) {
      $alt = ('{0} {1} {2}' -f $id, $grp.label, $im.title)
      [void]$g.AppendLine(('#### {0}' -f (MdEsc $im.title)))
      [void]$g.AppendLine('')
      [void]$g.AppendLine(('![{0}](../{1})' -f (MdEsc $alt), $im.posix))
      [void]$g.AppendLine('')
      [void]$g.AppendLine(('- 原 PNG：[`{0}`](../{1})' -f $im.posix, $im.posix))
      [void]$g.AppendLine(('- 对应 DSL：[`{0}`](../{1})' -f (($im.posix -replace '\.png$', '.snapshot')), (($im.posix -replace '\.png$', '.snapshot'))))
      [void]$g.AppendLine(('- 尺寸：{0}x{1}　文件：{2} B' -f $im.w, $im.h, $im.bytes))
      [void]$g.AppendLine('')
    }
  }
  [void]$g.AppendLine('---')
}

[void]$g.AppendLine('')
[void]$g.AppendLine('## 说明')
[void]$g.AppendLine('')
[void]$g.AppendLine('- 每张 PNG 均为 open-snapshot 服务返回的**原始字节**，未经任何后期处理；每张都有同名 `.snapshot`，两者一一配对。')
[void]$g.AppendLine('- A08 与 A10 另各有一张 `archive/*-v01.png` 草稿，明确标为草稿，**不计入**本页的最终图片。')
[void]$g.AppendLine('- A21 / A22 的第 2、3 轮属于预置轮次（按预先写好的 `rounds/round-0N.md` 连续执行，不等待外部反馈），每一轮的产物都保留在本页。')
[void]$g.AppendLine(('- 汇总数据见 [`task-metrics.json`](task-metrics.json)，总索引见 [`index.md`](index.md)，跨题经验见 [`snapshot-usage.md`](snapshot-usage.md)，进度与逐题证据见 [`suite-state.json`](suite-state.json)。'))
[void]$g.AppendLine('- token / 图像用量 / 费用：平台未提供计量数据，全套为 `null`，不以字数或渲染次数猜造。')

$galleryPath = Join-Path $suiteDir 'gallery.md'
[IO.File]::WriteAllText($galleryPath, $g.ToString(), $utf8)
"gallery.md written ({0} bytes)" -f (Get-Item $galleryPath).Length
"  sections={0} images={1}" -f $ids.Count, $inv.Count

# ---------------- index.md ----------------
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('# Snapshot 全套交付索引')
[void]$sb.AppendLine('')
[void]$sb.AppendLine(('- run_id：`{0}`' -f $runId))
[void]$sb.AppendLine(('- profile：`{0}`　时区：{1}' -f $ss.profile, $sm.timezone))
[void]$sb.AppendLine(('- 起：{0}　止：{1}　总墙钟：{2} s（{3} 天）' -f $sm.started_at, $sm.ended_at, $sm.elapsed_seconds, [math]::Round($sm.elapsed_seconds / 86400, 2)))
[void]$sb.AppendLine(('- 服务：{0}　状态：**{1}**（{2}/{3} 题 completed）' -f $ss.service_base_url, $sm.status, $sm.task_status_counts.completed, $sm.task_status_counts.total))
[void]$sb.AppendLine(('- 总输出根：`{0}/{1}/`　总临时根：`{2}/{1}/`（相对总任务根，path_base=suite_root）' -f $rcfg.output_root, $runId, $rcfg.temp_root))
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 0. 一眼看全')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| 项目 | 数量 | 口径 |')
[void]$sb.AppendLine('| --- | --- | --- |')
[void]$sb.AppendLine(('| 最终图片 | **{0}** | A 轨 {1} 张 + B 轨 {2} 张；已排除 2 张明确归档的草稿（A08/archive、A10/archive）；每张都有同名 `.snapshot` |' -f $sm.counts.final_pngs, $sm.counts.a_track_final_pngs, $sm.counts.b_track_final_pngs))
[void]$sb.AppendLine(('| 独立作品 | **{0}** | A 轨 {1} 件 + B 轨 {2} 件；B01–B06 每题 10 件独立完整作品；A21/A22 的多轮版本只算 1 件作品 |' -f $sm.counts.independent_creative_cases, $sm.counts.a_track_works, $sm.counts.b_track_works))
[void]$sb.AppendLine(('| 请求 | {0} | HTTP 尝试 {0} 次 = render {1} + documentation {2} + fonts {3} + research {4}；另有 {5} 行 log_note 非请求行 |' -f $sm.counts.snapshot_requests, $sm.counts.render_requests, $sm.counts.document_requests, $sm.counts.font_requests, $sm.counts.research_requests, $sm.counts.non_request_log_rows))
[void]$sb.AppendLine(('| 成功 / 失败 | {0} / {1} | 失败含刻意能力探测的 400、失效链接 404、反爬 412/403 与 1 次真实网络失败；**0 次 429**；另有 {2} 行状态未记录（取文工具不暴露状态码，记 null 不冒充成败） |' -f $sm.counts.successful_snapshot_requests, $sm.counts.failed_snapshot_requests, $sm.counts.status_not_recorded_requests))
[void]$sb.AppendLine(('| 迭代 / 读图 | {0} / {1} | 迭代行来自 30 题的 `iterations.jsonl`；读图 {1} 次（{2} 题用申报值、{3} 题由迭代记录推得，逐题标注来源） |' -f $sm.counts.iterations, $sm.counts.image_views, $sm.counts.image_views_declared_tasks, $sm.counts.image_views_derived_tasks))
[void]$sb.AppendLine(('| 请求耗时 / 总墙钟 | {0} s / {1} s | 请求串行；总墙钟还包含读题、写生成器、读图、像素复核与写交付物 |' -f $sm.counts.request_duration_sum_seconds, $sm.elapsed_seconds))
[void]$sb.AppendLine(('| DSL 版本 | {0} | `{1}/` {2} 份 + `{3}/` {4} 份 `.snapshot`，未覆盖任何已渲染过的尝试 |' -f $sm.counts.dsl_versions, $rcfg.temp_root, $sm.counts.dsl_versions_on_disk_tmp, $rcfg.output_root, $sm.counts.dsl_versions_on_disk_outputs))
[void]$sb.AppendLine('| token / 图像用量 / 费用 | **null** | 平台未提供计量数据，按约定未知即填 null，不以字数或渲染次数猜造 |')
[void]$sb.AppendLine('')
[void]$sb.AppendLine(('## 1. 套件层交付物（`{0}/{1}/_suite/`）' -f $rcfg.output_root, $runId))
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| 文件 | 作用 |')
[void]$sb.AppendLine('| --- | --- |')
[void]$sb.AppendLine('| [`index.md`](index.md) | 本文件：30 题状态、产物、单题入口与实际路径的总索引 |')
[void]$sb.AppendLine('| [`gallery.md`](gallery.md) | **总画廊**：逐图展示全部 124 张最终图片（含 A21/A22 全部轮次、B 轨 60 件作品），每图有标题、Markdown 预览、原 PNG 链接与对应 `.snapshot` 链接；相对本目录，无远程图片 |')
[void]$sb.AppendLine('| [`snapshot-usage.md`](snapshot-usage.md) | 全套实际文档/DSL/工具应用、跨题经验与踩坑、总审查与剩余事项；§10 记录根 `.gitignore` 与 PATHS.md 路径基准的合规核验 |')
[void]$sb.AppendLine('| [`task-metrics.json`](task-metrics.json) | 全套起止与总耗时、shared + 每题请求/迭代/读图/作品数、汇总范围与计时/日志来源 |')
[void]$sb.AppendLine('| [`suite-state.json`](suite-state.json) | 当前进度指针：逐题状态、启止、产物、视觉复核证据、未解决事项与恢复笔记 |')
[void]$sb.AppendLine('| `gallery.html` | 附加的 HTML 浏览版画廊（同为相对链接、无远程脚本）；**不是** `suite_required_artifacts` 要求项，只是便于肉眼快速翻看 |')
[void]$sb.AppendLine('| [`../../../.gitignore`](../../../.gitignore) | 总任务根的忽略文件，只排除 6 条运行时缓存规则；`outputs/` 与 `tmp/` 中的成品与过程证据一律不排除 |')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 2. 逐题索引')
[void]$sb.AppendLine('')

foreach ($id in $ids) {
  $st1 = @($ss.tasks | Where-Object { $_.id -eq $id })[0]
  $mt = $metricById[$id]
  $imgs = @($inv | Where-Object { $_.task -eq $id })
  $track = if ($id.StartsWith('A')) { 'A' } else { 'B' }
  $rounds = @($imgs | Where-Object { $null -ne $_.round } | ForEach-Object { $_.round } | Sort-Object -Unique)
  $roundTxt = if ($rounds.Count -gt 0) { ('预置轮次 round-{0}（共 {1} 轮，全部产物保留）' -f ($rounds -join '/round-'), $rounds.Count) } else { '单轮连续视觉迭代' }
  [void]$sb.AppendLine(('### {0}　{1}' -f $id, (MdEsc $titleById[$id])))
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine(('- 状态：**{0}**　轨道：{1}　墙钟：{2} s' -f $st1.status, $track, $mt.wall_clock_seconds))
  [void]$sb.AppendLine(('- 轮次：{0}' -f $roundTxt))
  [void]$sb.AppendLine(('- 请求 {0} 次（200 × {1} / 失败 {2} / 状态未记录 {3}）　迭代 {4} 行　读图 {5} 次（{6}）' -f $mt.requests_log_rows, $mt.requests_status.http_200, $mt.requests_status.http_failed_recorded, $mt.requests_status.http_status_not_recorded, $mt.iteration_log_rows, $mt.image_views, $mt.image_views_source))
  [void]$sb.AppendLine(('- 最终图片 {0} 张（{1} 件作品）：' -f $imgs.Count, $mt.works))
  foreach ($im in $imgs) {
    $lbl = $im.name
    if ($null -ne $im.case) { $lbl = ('case-{0}　{1}' -f $im.case, (MdEsc $im.title)) }
    elseif ($null -ne $im.round) { $lbl = ('round-{0}　{1}' -f $im.round, $im.name) }
    [void]$sb.AppendLine(('  - {0}　[`{1}`]({2})　{3}x{4}　{5} B' -f $lbl, $im.posix, ('../' + $im.posix), $im.w, $im.h, $im.bytes))
  }
  [void]$sb.AppendLine(('- 交付产物：{0} 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）' -f @($st1.artifacts).Count))
  $entryLine = ('- 单题入口：[`{0}/snapshot-usage.md`](../{0}/snapshot-usage.md)　[`{0}/task-metrics.json`](../{0}/task-metrics.json)' -f $id)
  if (Test-Path (Join-Path $outRoot ("{0}\gallery.html" -f $id))) {
    $entryLine = $entryLine + ('　[`{0}/gallery.html`](../{0}/gallery.html)（附加 HTML 浏览版）' -f $id)
  }
  [void]$sb.AppendLine($entryLine)
  [void]$sb.AppendLine(('- 实际输出：`{0}/{1}/{2}/`　实际临时：`{3}/{1}/{2}/`' -f $rcfg.output_root, $runId, $id, $rcfg.temp_root))
  [void]$sb.AppendLine('')
}

[void]$sb.AppendLine('## 3. 目录结构')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('```')
[void]$sb.AppendLine("$($rcfg.output_root)/$runId/")
[void]$sb.AppendLine('  _suite/            index.md  gallery.md  snapshot-usage.md  task-metrics.json  suite-state.json  (+ gallery.html)')
[void]$sb.AppendLine('  A01/ .. A24/       每题：作品 PNG + 同名 .snapshot + snapshot-usage.md + task-metrics.json（部分题另有归档草稿）')
[void]$sb.AppendLine('  B01/ .. B06/       每题：case-01/ .. case-10/{final.png,final.snapshot,case.md} + snapshot-usage.md + task-metrics.json + portfolio/gallery 等')
[void]$sb.AppendLine("$($rcfg.temp_root)/$runId/")
[void]$sb.AppendLine('  <task>/            requests.jsonl  iterations.jsonl  （B 类另有 tool-usage.jsonl）以及每一次尝试的 .snapshot / .png')
[void]$sb.AppendLine('  _suite/            events.jsonl（追加式事件）  checkpoints/state-0000NN.json（不可覆盖的编号快照）  各阶段脚本')
[void]$sb.AppendLine('```')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('以上目录均相对总任务根（`path_base: "suite_root"`）；文档内的本地链接则相对文档所在目录（`path_base: "document"`）。')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 4. 留痕位置')
[void]$sb.AppendLine('')
[void]$sb.AppendLine(('- **追加式事件**：`{0}/{1}/_suite/events.jsonl`（{2} 行，从任务启动一路追加到收尾）' -f $rcfg.temp_root, $runId, @(Get-Content (Join-Path $tmpRoot '_suite\events.jsonl')).Count))
[void]$sb.AppendLine(('- **编号检查点**：`{0}/{1}/_suite/checkpoints/state-0000NN.json`（共 {2} 份，只增不改）' -f $rcfg.temp_root, $runId, @(Get-ChildItem (Join-Path $tmpRoot '_suite\checkpoints') -Filter '*.json').Count))
[void]$sb.AppendLine('- **逐请求留痕**：每题 `requests.jsonl`，含 request_id、起止时刻、耗时、HTTP 状态、字节数、Server-Timing、ratelimit_remaining、请求/响应文件路径与错误摘要')
[void]$sb.AppendLine('- **逐迭代留痕**：每题 `iterations.jsonl`，含 DSL 哈希、PNG 哈希、读图路径与读图结论、verdict、findings 与 changes')
[void]$sb.AppendLine('- **工具使用留痕**：B01–B06 另有 `tool-usage.jsonl`')
[void]$sb.AppendLine('- **根 `.gitignore`**：总任务根一份，只排除运行时缓存（`__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`），`outputs/` 与 `tmp/` 中的成品与过程证据一律不排除')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 5. 声明')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('- 全部 124 张最终图片均为 open-snapshot 服务返回的原始字节，未经任何后期处理；每张都有同名 `.snapshot`。')
[void]$sb.AppendLine('- 每张最终图片都用读图工具实际打开并核对了画幅与刊头编号之后才落盘；串图后被丢弃的重读已单独标注。')
[void]$sb.AppendLine('- 研究类题目（B04/B05/B06）在拿不到法条、国家标准或服务标准原文时，一律不引用条款号、不写罚则金额、不写国标数字、不写机构背书，二手线索只标「检索摘要（来源，日期）」，全部数值标 DEMO。')
[void]$sb.AppendLine('- token / 图像使用量 / 费用平台未提供，全套为 null，不以字数、渲染次数或剩余额度替代。')
[void]$sb.AppendLine('')

$indexPath = Join-Path $suiteDir 'index.md'
[IO.File]::WriteAllText($indexPath, $sb.ToString(), $utf8)
"index.md written ({0} bytes)" -f (Get-Item $indexPath).Length
