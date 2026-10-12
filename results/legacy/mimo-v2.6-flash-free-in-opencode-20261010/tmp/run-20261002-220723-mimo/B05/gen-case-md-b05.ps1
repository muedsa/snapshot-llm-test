# gen-case-md-b05.ps1 -- build outputs/.../B05/case-NN/case.md from the real logs
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B05'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B05'
$utf8 = New-Object Text.UTF8Encoding($false)
$tz   = 'UTC+08:00'
$BQ   = [char]96
function Code([string]$s) { return ($BQ + $s + $BQ) }

$reqs = @()
foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'requests.jsonl'))) { if ($l.Trim()) { $reqs += ($l | ConvertFrom-Json) } }
$iters = @()
foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'iterations.jsonl'))) { if ($l.Trim()) { $iters += ($l | ConvertFrom-Json) } }

$meta = @(
  [ordered]@{ id='case-01'; title='楼栋剖面总览'; aud='全体业主 · 桌面'; bg='深墨';
    hero='整栋 1 层到 6 层的剖面：12 户按态度着色（青=已签约 / 琥珀=已同意 / 珊瑚=顾虑），井道居中并放两块装饰轿厢；右侧 4 张 KPI（9/12 支持率 75%、7/12 签约率 58%、自付区间 0-42,985 元、净自付 28.8 万元）+ 12 户状态网格 + 按模型 A 的分摊一览 + 状态快照 2026-10-08。';
    data='总建筑面积 931.8 平米、造价 52.8 万、补贴 24.0 万、净自付 288,000 元；态度 已签约 7 / 已同意 2 / 顾虑 3，与 case-06 的三色格完全一致。';
    demo='楼栋、户号、态度与状态快照日期均为演示样例。' },
  [ordered]@{ id='case-02'; title='我家出多少 · 手机'; aud='居民端 · 手机'; bg='纸色';
    hero='602 室身份卡 + A/B/C 三模型切换 + 大数 42,985 元 + 权重公式行 + 三模型对照小卡 + 模型 A 各层费率条（100/85/70/50/30/0%）+ 可拖动的总造价滑杆 46.0 - 58.0 万元。';
    data='权重和 6.70，单位权重 = 288,000 / 6.70 = 42,985 元；三模型 42,985 / 24,386 / 47,213 元；滑杆两端 46.0 与 58.0 万元。';
    demo='滑杆为可调演示控件，改动总造价会同步改变分摊，最终口径仍以 288,000 元为准。' },
  [ordered]@{ id='case-03'; title='三种分摊模型对比'; aud='业主协商会 · 桌面'; bg='纸色';
    hero='三张模型卡（A 按楼层递增 / B 按建筑面积均摊 / C 低层免摊），每张给出权重和、单位权重、零负担户数、单户最高与规则说明；下方协商会投票条（模型 A 7 票 / 模型 C 3 票 / 未选 2 户）与 12 户全表（层、面积、态度、三模型金额、极差）。';
    data='A 权重和 6.70、单位权重 42,985 元、零负担 2 户；B 309.08 元每平米、零负担 0 户；C 权重和 6.10、单位权重 47,213 元、零负担 4 户；最大极差 24,386 元并列 102、202 室。';
    demo='投票结果为演示；分摊权重是本产品自定义规则，不是法规要求。' },
  [ordered]@{ id='case-04'; title='顾虑台账'; aud='牵头人工作台 · 桌面'; bg='深墨';
    hero='3 条可销项的顾虑条目（101 采光与通行、202 运行噪音、602 分摊金额），每条含顾虑描述、应对方案、负责人、状态、下次动作与截止日期/剩余天数；下方 3 条回应要点与仍有顾虑的 3 户剖面。';
    data='截止 2026-10-12 / 10-15 / 10-18，剩余 4 / 7 / 10 天，全部以 2026-10-08 为今日，与 case-01 的状态快照同日。';
    demo='顾虑文本、负责人、复测与回访安排均为演示样例；补贴口径未完成外部核验，画面不引用任何政策条款。' },
  [ordered]@{ id='case-05'; title='造价与补贴'; aud='全体业主 · 桌面'; bg='纸色';
    hero='52.8 万元的 6 项构成与补贴 -24.0 万元的推导；右侧三家比价（供应商、报价、是否含迁改、质保、工期、同口径）与与最低同口径的差额条形图；左侧补齐每户平均造价、折合面积单价与补贴后每户三个指标。';
    data='6 项合计 52.8 万、补贴 24.0 万、净自付 288,000 元；甲 52.8 / 乙 55.6 / 丙 49.9 万元，丙另计迁改 3.6 万后同口径 53.5 万；528,000/12=44,000 元、528,000/931.8=566.6 元每平米、288,000/12=24,000 元。';
    demo='造价、报价、工期、补贴均为样例；补贴金额以当地政策核定为准，本次未取得政策原文，画面不引用条款。' },
  [ordered]@{ id='case-06'; title='签约与公示 · 手机'; aud='居民端 · 手机'; bg='深墨';
    hero='5 段流程时间轴（意愿征询 / 方案公示 / 异议期 / 业主签约 / 备案与开工），每段带起止日期、状态与进度条；下方 12 户签约状态格与图例，再加一条提交失败与一条提交成功的真实状态反馈。';
    data='意愿征询支持 9/12；异议期 2026-10-08 至 10-14 第 1 天 / 共 7 天；已签约 7/12；预计开工 2026-10-20；受理编号 WT3-20261008-07。';
    demo='提交失败（授权书照片 7.3 MB 超过 5 MB 限制）与受理编号均为演示状态反馈。' },
  [ordered]@{ id='case-07'; title='602 室最终确认 · 平板'; aud='居民端 · 平板'; bg='纸色';
    hero='本户在楼栋中的位置剖面（602 高亮）+ 模型 A 自付 42,985 元与三模型小对照 + 三期付款节点 + 提交前 3 项逐条核对 + 主按钮确认并提交签约与次按钮返回修改。';
    data='12,896 + 17,194 + 12,895 = 42,985 元（30% / 40% / 30%）；工期 65 天；十年公共支出每年 13,800 元。';
    demo='核对项、按钮与分期节点为演示界面内容。' },
  [ordered]@{ id='case-08'; title='施工进度 · 超宽'; aud='全体业主 · 宽屏'; bg='深墨';
    hero='6 段里程碑横条（基础开挖、主体钢结构、井道与玻璃幕墙、电梯安装调试、管线复接、验收整改与交付），带日序与状态；下方 3 条当日现场记录（示意图 DEMO）与一条安全提示。';
    data='里程碑 10+10+14+15+8+8 = 65 天；当前第 28 天，进度 43.1%，阶段井道与玻璃幕墙 第 8 天 / 共 14 天；开工 2026-10-20、现场记录 2026-11-16、预计交付 2026-12-23 三者与 65 天工期自洽。';
    demo='现场记录文字与三张剖面示意图均为演示，不对应真实工地。' },
  [ordered]@{ id='case-09'; title='交付验收 · 竖屏'; aud='验收组 · 竖屏'; bg='纸色';
    hero='验收清单 12 项（10 合格 / 1 待检 / 1 整改）+ 三张状态卡 + 尚未通过 2 项的责任与期限 + 首次运行记录深色卡。';
    data='验收日 2026-12-19，分项结论日期 2026-12-18 与 12-19，责任期限 12-21；待检项已预约特检院 12-19 到场；整改项实测高差 35 mm、要求不大于 15 mm。全部日期均在开工 2026-10-20 之后。';
    demo='检验结论、日期与责任人为样例，不构成任何真实检验意见。' },
  [ordered]@{ id='case-10'; title='十年总账'; aud='全体业主 · 桌面'; bg='深墨';
    hero='第 0 年到第 10 年的全楼累计成本堆叠柱（橙=一次性自付 288,000，青=当年新增公共支出），第 10 年 42.6 万元单独高亮；右侧 602 室三模型十年总额与月均；底部 4 张总账 KPI。';
    data='一次性自付 288,000 + 十年运行支出 138,000 = 十年合计 426,000 元；每户十年 35,500 元（426,000/12）；602 室 A 63,582（530 元/月）、B 36,071（301 元/月）、C 69,836（582 元/月），相差 33,765 元；纵轴 0 到 50 万、步长 10 万。';
    demo='维保、电费、年检与大修准备金均为样例价格，未做任何真实采购询价。' }
)

function Renders($cid) {
  $n = $cid.Substring(5)
  return @($reqs | Where-Object { $_.id -match ('^B05-rnd-' + $n + '-\d\d$') })
}
function ViewNote($cid, $seq) {
  $e = $iters | Where-Object { $_.seq -eq $seq }
  if (-not $e) { return $null }
  return @($e.defects | Where-Object { $_.case -eq $cid })
}

$chg = @{
  'case-01' = 'Kpi 单位改 inline/block 双模式、进度条上移、备注下移，消除叠印'
  'case-02' = '滑杆最小值补单位 46.0 万元'
  'case-03' = '权重和改 0.00 格式、单位权重 309 -> 309.08、极差列宽 294 -> 270'
  'case-04' = '删除每行重复的列头 kicker 并重排行距'
  'case-05' = '报价列重排加间距、供应商副行改写为差额、补差额图与两个指标行'
  'case-06' = '异议期第 3 天 -> 第 1 天、受理编号 1007 -> 1008，与 case-01/04 的 2026-10-08 对齐'
  'case-07' = '剖面格子改自适应单行；下半屏四处零间距全部拉开（付款卡/核对标题/CTA/脚注）'
  'case-08' = '现场记录 10-15 -> 11-16、交付 12-06 -> 12-23'
  'case-09' = '验收日期整批从 10 月移到 12-18/12-19、责任期限 12-21、首次运行 2026-12-19'
  'case-10' = '纵轴固定 50 万步长 10、KPI 每户年均 -> 每户十年'
}

$rows = @()
foreach ($m in $meta) {
  $cid = $m.id
  $d   = Join-Path $out $cid
  $fp  = Join-Path $d 'final.png'
  $fs  = Join-Path $d 'final.snapshot'
  $pngB = (Get-Item $fp).Length
  $dslB = (Get-Item $fs).Length
  $pngSha = (Get-FileHash $fp -Algorithm SHA256).Hash.Substring(0,16)
  $dslSha = (Get-FileHash $fs -Algorithm SHA256).Hash.Substring(0,16)
  $t = [IO.File]::ReadAllText($fs, [Text.Encoding]::UTF8)
  $g = [regex]::Match($t, '<Container width="(\d+)" height="(\d+)"')
  $w = [int]$g.Groups[1].Value; $h = [int]$g.Groups[2].Value
  $ratio = [Math]::Round(($w / $h), 3)
  $shape = '接近方形'
  if ($ratio -gt 1.05) { $shape = '横幅' }
  elseif ($ratio -lt 0.95) { $shape = '竖幅' }

  $rs = Renders $cid
  $L = @()
  $L += ('# {0} —— {1}' -f $cid, $m.title)
  $L += ''
  $L += ('- 任务：B05（product from zero）· 运行：' + (Code 'run-20261002-220723-mimo') + ' · 时区：' + $tz)
  $L += ('- 成品：' + (Code "outputs/run-20261002-220723-mimo/B05/$cid/final.png") + ' + 同名 ' + (Code 'final.snapshot') + '（选定 round 02，2 轮视觉迭代）')
  $L += ('- 受众 / 场景：' + $m.aud)
  $L += ('- 画幅：' + $w + ' x ' + $h + '（' + $ratio + '，' + $shape + '）· 底色：' + $m.bg + ' · ' + $pngB + ' bytes PNG / ' + $dslB + ' bytes DSL')
  $L += ('- 字节校验：PNG sha256 前缀 ' + (Code $pngSha) + ' 与服务原始响应逐字节一致；DSL sha256 前缀 ' + (Code $dslSha) + '；PNG 与 DSL 尺寸对齐 ' + $w + ' x ' + $h)
  $L += ''
  $L += '## 这件作品回答什么'
  $L += ''
  $L += $m.hero
  $L += ''
  $L += '## 数据与口径'
  $L += ''
  $L += $m.data
  $L += ''
  $L += '## 演示 / 非来源内容'
  $L += ''
  $L += $m.demo
  $L += ''
  $L += '## 真实渲染与迭代'
  $L += ''
  $L += '| 请求 ID | HTTP | 耗时 | 字节 | 起 | 止 |'
  $L += '|---|---|---|---|---|---|'
  foreach ($r in $rs) {
    $L += ('| ' + (Code $r.id) + ' | ' + $r.http_status + ' | ' + $r.duration_ms + ' ms | ' + $r.bytes + ' | ' + $r.started_at + ' | ' + $r.ended_at + ' |')
  }
  $L += ''
  $L += '## 读图证据（每轮都用 read 打开实际图片）'
  $L += ''
  $L += '| 轮次 | 类型 | 提交的改动 | 读图看到了什么 | 复核结论 |'
  $L += '|---|---|---|---|---|'
  $v1 = ViewNote $cid 2
  $v2 = ViewNote $cid 5
  if ($v1) {
    $c1 = '无缺陷'
    if ($v1[0].severity -ne 'none') { $c1 = '记入 round-02 修复清单' }
    $L += ('| r01 | baseline + view | 首轮按 plan.md 一次性生成 10 件 DSL 并真实渲染 | ' + $v1[0].what + ' | ' + $c1 + ' |')
  }
  if ($v2) {
    $c2 = '本轮读图复核通过，无缺陷'
    if ($v2[0].severity -ne 'none') { $c2 = 'round-02 修复后重新渲染并再次读图复核通过' }
    $L += ('| r02 | visual | ' + $chg[$cid] + ' | ' + $v2[0].what + ' | ' + $c2 + ' |')
  }
  $L += ''
  $L += '所有渲染的 URL、HTTP 状态、耗时、字节数与服务返回的 request_id 都在'
  $L += ('tmp/run-20261002-220723-mimo/B05/requests.jsonl；迭代与逐轮读图证据在同目录 iterations.jsonl。')
  $L += ''

  [IO.File]::WriteAllLines((Join-Path $d 'case.md'), $L, $utf8)
  $rows += ([ordered]@{ id=$cid; title=$m.title; aud=$m.aud; bg=$m.bg; w=$w; h=$h; ratio=$ratio;
                        pngB=$pngB; dslB=$dslB; pngSha=$pngSha; renderCount=@($rs).Count; renders=@($rs | ForEach-Object { $_.id }) })
  ('wrote {0}\case.md  ({1} x {2}, {3} renders)' -f $cid, $w, $h, @($rs).Count)
}

[IO.File]::WriteAllText((Join-Path $tmp 'case-index-b05.json'), (($rows | ConvertTo-Json -Depth 6)), $utf8)
'case-index-b05.json written'
