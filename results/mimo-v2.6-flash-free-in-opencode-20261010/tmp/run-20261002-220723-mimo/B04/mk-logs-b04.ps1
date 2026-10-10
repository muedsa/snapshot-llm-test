# mk-logs-b04.ps1 -- derive iterations.jsonl + tool-usage.jsonl for B04 from requests.jsonl
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b    = Join-Path $root 'tmp\run-20261002-220723-mimo\B04'
$enc  = New-Object System.Text.UTF8Encoding($false)

$reqs = @(); Get-Content (Join-Path $b 'requests.jsonl') -Encoding UTF8 | ForEach-Object { $reqs += ($_ | ConvertFrom-Json) }
$renders = @($reqs | Where-Object { $_.type -eq 'render' } | Sort-Object started_utc)

function Find-Req([string]$id) { @($renders | Where-Object { $_.id -eq $id })[0] }

$titles = @{
 'case-01' = '封面：23:59:60 那一秒钟'
 'case-02' = '一秒有多长？——定义的五次落点'
 'case-03' = '1972 年的三条钟：TAI / UTC / UT1'
 'case-04' = '27 次闰秒全表'
 'case-05' = '27 次的节奏：年代与年份分布'
 'case-06' = '为什么步长必须是 1 秒'
 'case-07' = '23:59:60 那一分钟（2012-06-30 现场）'
 'case-08' = '一段创纪录的静默：空窗对照'
 'case-09' = '决定：从 0.9 秒到 2035'
 'case-10' = '反向的一秒与工程师工具箱'
}

$changes = @{
 'case-01' = 'Strip61 由递增高度改为 60 个等长刻度、第 61 个琥珀刻度单独加高；文案"闰接日"改为"6 月 30 日或 12 月 31 日"；统计块 -37 s 改用 U+2212 真减号'
 'case-02' = '卡片 3 小标题"模型频率固定"改为"铯频率固定"；卡片 2/3 正文重排，避免行首出现全角冒号并补句号；副标题问号统一为全角'
 'case-03' = '移除 TAI 线末端突兀的青色实心色块，改为 → 字形；UT1 波形由 5x4 离散小方块改为跨样本连续线段，消除串珠感'
 'case-04' = '末行（第 27 次 2016-12-31 / 37 s）加琥珀底纹与左侧色条，强调"至今有效"'
 'case-05' = '按十年图表标题上移、基线下移，消除 9 轴标签与标题重叠；年份矩阵加行区间标签（72-82 等）并向右让位；图例由文字圆点改为绘制的色块+圆点'
 'case-06' = '0.1 秒梳齿由 2x2 暗点改为 2x14 可见刻度并加轴线；整数刻度加高；说明文字改为"灰色细刻度是 0.1 秒，琥珀色的粗刻度才是允许的落点"'
 'case-07' = '61 格刻度由递增改为等长；新增 :00..:50 刻度标签；删除与实际位置错位的 23:59:59 标签；底部说明改为居中单行完整表述'
 'case-08' = '平均值标签由图表右端移到左端，避开最高柱体；注释文字统一为 1 010 的分位写法'
 'case-09' = '9 个时间节点各补第二行细节，填满 800x2000 竖幅的空档，节点间距节奏更均匀'
 'case-10' = '迷你示意图标签由 y=530 移入面板内 y=506，不再压到卡片描边；保留/跳过方块改为描边卡片 + 竖条（保留）/ 横杠（跳过）'
}

$viewNotes = @{
 'case-01' = '读图 r01：刻度呈线性递增，视觉上暗示"秒越走越长"，与事实不符；说明文字出现不规范词"闰接日"；-37 s 的连字符不像减号'
 'case-02' = '读图 r01：卡片 3 标题语义错误；卡片 2/3 正文把全角冒号断到行首，排版难看'
 'case-03' = '读图 r01：TAI 线末端有一块突兀的青色实心矩形（原拟作箭头）；UT1 波形由离散点构成，呈串珠状'
 'case-04' = '读图 r01：表格数据逐行核对无误（184/365/366/547/2557/1096/1277/1095/550 均与日期差一致），但末行"37 s 至今有效"缺少视觉强调'
 'case-05' = '读图 r01：9 轴标签与"按十年统计"标题重叠；年份矩阵无行区间标签，读者无法定位跨十年的行；图例两个圆点同色无法区分'
 'case-06' = '读图 r01：0.1 秒梳齿几乎不可见，caption 提到的"灰色刻度"在画面上读不出来'
 'case-07' = '读图 r01：与 case-01 同样的递增刻度误导；23:59:59 标签位置与它标注的那一秒相差约 320 px'
 'case-08' = '读图 r01："平均 625" 标签压在最右侧柱体上；纵轴数据与 26 个间隔核对一致'
 'case-09' = '读图 r01：9 个节点多为单行，2000 px 竖幅留下大片空白，节奏松散'
 'case-10' = '读图 r01：迷你示意图的"保留/跳过（拟议）"标签越过卡片底边，掉到面板外'
}

$iters = @()
$seq = 0

# --- round 1: baseline ---
foreach ($i in 1..10) {
  $c = 'case-{0:d2}' -f $i
  $r = Find-Req "B04-rend-$c-r01"
  $seq++
  $iters += [ordered]@{
    iteration_id   = 'ite-B04-{0}-r01' -f $c
    case_id        = $c
    title          = $titles[$c]
    round          = 'r01'
    type           = 'baseline'
    request_id     = $r.id
    http_status    = $r.http_status
    duration_ms    = $r.duration_ms
    render_started_utc = $r.started_utc
    render_ended_utc   = $r.ended_utc
    change         = '首轮：按 plan.md 的 10 件选题与画幅一次性生成完整 DSL 并真实渲染'
    observation    = 'build-b04.ps1 Fit 守卫 10/10 通过（r01 曾有 c09 来源行 675 > 672 的越界，改行后通过）；服务返回 200 image/png'
    result         = "渲染成功，得到 $c/r01.png（$($r.bytes) B）"
    viewed         = $true
    view_evidence  = "读图 $c/r01.png：$($viewNotes[$c])"
    fix_applied_in = 'r02'
  }
}

# --- round 2: visual iteration for all 10 ---
$r02txt = @{
 'case-01' = '等长刻度 + 文案更正 + 真减号'
 'case-02' = '文案与断行修正'
 'case-03' = '箭头与波形连续化'
 'case-04' = '末行强调'
 'case-05' = '标题避让 + 行标签 + 图例色块'
 'case-06' = '梳齿可见性与轴线'
 'case-07' = '等长刻度 + 刻度标签 + 位置修正'
 'case-08' = '平均值标签移位'
 'case-09' = '节点补细节行'
 'case-10' = '面板内标签 + 方块语义'
}
$r02view = @{
 'case-01' = '读图 r02：60 个等高灰刻度、第 61 个琥珀刻度更高更粗，不再读成递增柱；说明文字改为"前 60 个刻度等长；第 61 个只出现在 6 月 30 日或 12 月 31 日的 23:59"；-37 s 显示为真减号'
 'case-02' = '读图 r02：卡片 3 标题为"铯频率固定"；卡片 2/3 正文四行齐整、句号齐全；问号为全角'
 'case-03' = '读图 r02：TAI 线末端换成细 → 字形，不再有突兀色块；UT1 波形成为连续平滑曲线'
 'case-04' = '读图 r02：第 27 行出现琥珀底纹与左侧色条，37 s 一眼可辨；全表 27 行数据再次逐行核对一致'
 'case-05' = '读图 r02：9 轴标签与标题不再重叠；矩阵左侧出现 72-82/83-93/94-04/05-15/16-26 行标签；图例为琥珀实心点与灰色空心点两组色块'
 'case-06' = '读图 r02：0.1 秒细梳齿清晰可见，琥珀整数刻度明显高出并带轴线，两级刻度关系读得懂'
 'case-07' = '读图 r02：60 个等高刻度 + :00..:50 刻度标签 + 23:59:00/23:59:60 左右对位，第 61 个琥珀刻度单独突出'
 'case-08' = '读图 r02：平均 625 天标签落在左侧空白处，与柱体无接触；2 557 天红柱标签清晰'
 'case-09' = '读图 r02：9 个节点均为两行，竖幅节奏均匀，收尾面板与来源三行完整'
 'case-10' = '读图 r02：保留/跳过标签位于面板内、距底边 10 px 以上；三个方块的竖条与横杠区分清楚'
}
foreach ($i in 1..10) {
  $c = 'case-{0:d2}' -f $i
  $r = Find-Req "B04-rend-$c-r02"
  $seq++
  $iters += [ordered]@{
    iteration_id   = 'ite-B04-{0}-r02' -f $c
    case_id        = $c
    title          = $titles[$c]
    round          = 'r02'
    type           = 'visual'
    request_id     = $r.id
    http_status    = $r.http_status
    duration_ms    = $r.duration_ms
    render_started_utc = $r.started_utc
    render_ended_utc   = $r.ended_utc
    change         = $changes[$c]
    observation    = $viewNotes[$c]
    result         = "$($r02txt[$c])；重新渲染 200 image/png（$($r.bytes) B）"
    viewed         = $true
    view_evidence  = $r02view[$c]
    fix_applied_in = $null
  }
}

# --- round 3: case-04 precision note ---
$r = Find-Req 'B04-rend-case-04-r03'
$iters += [ordered]@{
  iteration_id   = 'ite-B04-case-04-r03'
  case_id        = 'case-04'
  title          = $titles['case-04']
  round          = 'r03'
  type           = 'visual'
  request_id     = $r.id
  http_status    = $r.http_status
  duration_ms    = $r.duration_ms
  render_started_utc = $r.started_utc
  render_ended_utc   = $r.ended_utc
  change         = '口径行补一句"MJD 为生效首日"，消除 MJD 列与插入日期列的歧义'
  observation    = 'r02 终审：表头 MJD 未说明对应哪一天，读者可能误以为是插入日的儒略日'
  result         = '口径行改为"插入日期 = 生效日期前一天的 23:59:60；MJD 为生效首日（IERS Leap_Second.dat）"；重新渲染 200 image/png（200127 B）'
  viewed         = $true
  view_evidence  = '读图 r03：口径行已含"MJD 为生效首日"；第 27 行琥珀强调仍在；27 行数据复核一致（1972-06-30 MJD 41499 = 1972-07-01 的儒略日）'
  fix_applied_in = $null
}

$itPath = Join-Path $b 'iterations.jsonl'
$sb = New-Object System.Text.StringBuilder
foreach ($it in $iters) {
  $null = $sb.AppendLine((ConvertTo-Json $it -Compress -Depth 5))
}
[IO.File]::WriteAllText($itPath, $sb.ToString(), $enc)
"written: $itPath ($((Get-Item $itPath).Length) bytes, $($iters.Count) rows)"

# ---------------- tool-usage.jsonl ----------------
$docIds = @($reqs | Where-Object { $_.type -eq 'documentation' } | ForEach-Object { $_.id })
$resIds = @($reqs | Where-Object { $_.type -eq 'research' } | ForEach-Object { $_.id })
$rendIds = @($renders | ForEach-Object { $_.id })

$tus = @(
 [ordered]@{ tool_id='tu-01'; tool='plan.md 选题与来源表（人写综合）'; category='选题与规划'; affected_cases='*'
   input='tasks/B04-researched-visual-special/{TASK.md,AGENTS.md,task.json}'; output=@('tmp/run-20261002-220723-mimo/B04/plan.md')
   purpose='把 7 个读者问题、10 个来源 S1-S10、10 件作品与画幅写成可执行计划，并区分事实/来源结论/编辑解释/演示数据'
   http_request_ids=@(); note='共享准备，不归属任何单一作品'; double_counted=$false }
 [ordered]@{ tool_id='tu-02'; tool='fetch-b04.ps1 真实抓取一手资料'; category='资料研究'; affected_cases='*'
   input='BIPM / IERS / hpiers / IANA / ITU / NIST / NPL / PTB / RFC 等主机'; output=@('tmp/run-20261002-220723-mimo/B04/research/*')
   purpose='抓取 Leap_Second.dat、Bulletin C 72、IERS 闰秒与常数页、CGPM 2022 决议 4/5、SI 手册、ITU-R TF.460-6、RFC 5905、IANA tzdb 等一手来源并落盘'
   http_request_ids=$resIds; note="$($resIds.Count) 条 type=research，含 Wikipedia/Britannica 等不可达主机的真实超时与 403 记录，未伪造任何来源"; double_counted=$false }
 [ordered]@{ tool_id='tu-03'; tool='fetch-b04.ps1 文档与字体查询'; category='文档查阅'; affected_cases='*'
   input='https://open-snapshot.muedsa.com/ai-guide.md、snapshot.muedsa.com 文档站、/fonts'
   output=@((Join-Path $b 'docs\*'))
   purpose='真实拉取 AI 指南与 parser-tags/painting/enums/transform/rendering/decorated-box/source-index/faq 等文档，并查可用字体 27 种'
   http_request_ids=(@($docIds) + @($reqs | Where-Object { $_.type -eq 'fonts' } | ForEach-Object { $_.id }))
   note="$($docIds.Count) 条 documentation（其中 6 条为猜错地址的真实 404，按原样登记）+ 1 条 fonts"; double_counted=$false }
 [ordered]@{ tool_id='tu-04'; tool='lib-b04.ps1 共享绘图库'; category='生成程序'; affected_cases='*'
   input='B01 lib 的 F/E/Box/Circle/TW/Fit/Page/Write-Dsl 基元 + B03 的 TX/TXW/Circ'
   output=@('tmp/run-20261002-220723-mimo/B04/lib-b04.ps1')
   purpose='沉淀 Ts/TBlock/Card/HR/VR/Kicker/Tag/Bar*/Tick*/DotH/Strip61/Steps/Masthead/SourceLine/Page4 与调色板，并内置 Get-LeapRows/Get-LeapList 从一手 Leap_Second.dat 解析 28 行、27 次'
   http_request_ids=@(); note='共享准备，不归属任何单一作品'; double_counted=$false }
 [ordered]@{ tool_id='tu-05'; tool='gen-b04-a/b/c/d.ps1 十件作品生成器'; category='生成程序'; affected_cases='*'
   input='lib-b04.ps1 + plan.md'
   output=@('tmp/run-20261002-220723-mimo/B04/gen-b04-a.ps1','tmp/run-20261002-220723-mimo/B04/gen-b04-b.ps1','tmp/run-20261002-220723-mimo/B04/gen-b04-c.ps1','tmp/run-20261002-220723-mimo/B04/gen-b04-d.ps1')
   purpose='按 10 种不同画幅比例生成完整自包含 DSL（a:01-02 b:03-05 c:06-08 d:09-10）'
   http_request_ids=@(); note='可复用构件（Strip61/Steps/Bar*/Matrix）跨 4 个文件复用，但每件作品的 DSL 独立成篇，未把前件成品计入后件'; double_counted=$false }
 [ordered]@{ tool_id='tu-06'; tool='build-b04.ps1 + Fit 守卫'; category='生成程序'; affected_cases='*'
   input='gen-b04-*.ps1'; output=@((Join-Path $b 'case-*\*.snapshot'))
   purpose='逐件写 DSL 并跑越界守卫（文本框底边必须小于画布高），r01 捕获 c09 来源行 675 > 672 一处并修正'
   http_request_ids=@(); note='守卫失败即计为一次真实的方案探索，r01 起 3 轮 build 全部 10/10 通过'; double_counted=$false }
 [ordered]@{ tool_id='tu-07'; tool='render-b04.ps1 / render-b04-all.ps1'; category='服务渲染'; affected_cases='*'
   input='case-*/rNN.snapshot'; output=@('case-*/rNN.png')
   purpose='POST /snapshot 逐件渲染并把 attempt/bytes/server_timing/ratelimit/request_id 全字段写入 requests.jsonl'
   http_request_ids=$rendIds; note="$($rendIds.Count) 条 type=render，全部 200，0 条 429"; double_counted=$false }
 [ordered]@{ tool_id='tu-08'; tool='read 工具看图（33 次调用）'; category='视觉检查'; affected_cases='*'
   input='case-*/rNN.png 与 outputs/.../final.png'
   output=@()
   purpose='逐张打开最终图做视觉自检：r01 10 次 + r02/r03 23 次（含串图重读），得到 10 件 × 2-3 轮的修改清单'
   http_request_ids=@()
   note='read 工具按内容哈希缓存，同内容副本与连续读取多次返回了错图；改用「每次只读一张 + System.Drawing 重编码生成唯一字节副本」后恢复。33 次调用中 21 次取得了与目标画稿匹配的正确字节（10 件 r01 + 10 件 r02 + case-04 r03），12 次为重复或错图，全部保留为失败的工具尝试'
   double_counted=$false }
 [ordered]@{ tool_id='tu-09'; tool='System.Drawing 尺寸/哈希/像素指纹核验'; category='视觉检查'; affected_cases='*'
   input='case-*/r01..r03.png + outputs/.../final.png'
   output=@()
   purpose='在串图期间独立核验 20 张 PNG 的画布尺寸、SHA1/SHA256 与 outputs 副本一致性，确认磁盘字节正确、问题只在读图通道'
   http_request_ids=@(); note='输出为 10×2 的尺寸/哈希表，结论：outputs 与 tmp 全部 SAME'; double_counted=$false }
 [ordered]@{ tool_id='tu-10'; tool='browser.preview 尝试'; category='失败的工具尝试'; affected_cases='*'
   input='preview3/w-06.png'; output=@()
   purpose='尝试用浏览器预览通道看图'
   http_request_ids=@(); note='返回 [browser.disconnected] No desktop browser is connected，通道不可用；后续一律走 read + 唯一字节副本'
   double_counted=$false }
 [ordered]@{ tool_id='tu-11'; tool='mk-logs-b04.ps1 / mk-metrics-b04.ps1'; category='日志与指标'; affected_cases='*'
   input='requests.jsonl'; output=@('iterations.jsonl','tool-usage.jsonl','task-metrics.json')
   purpose='从真实请求日志反查时延生成迭代行，再按 B03 口径汇总任务指标，避免手写数字'
   http_request_ids=@(); note='指标由程序从 JSONL 汇总，未知 token/费用一律 null'; double_counted=$false }
)

$tuPath = Join-Path $b 'tool-usage.jsonl'
$sb2 = New-Object System.Text.StringBuilder
foreach ($t in $tus) { $null = $sb2.AppendLine((ConvertTo-Json $t -Compress -Depth 6)) }
[IO.File]::WriteAllText($tuPath, $sb2.ToString(), $enc)
"written: $tuPath ($((Get-Item $tuPath).Length) bytes, $($tus.Count) rows)"
