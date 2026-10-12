# mk-logs-b05.ps1 -- build tmp/.../B05/tool-usage.jsonl and outputs/.../B05/journey.json
# Everything derived from requests.jsonl / iterations.jsonl / case-index-b05.json + explicit stage table.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B05'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B05'
$utf8 = New-Object Text.UTF8Encoding($false)
$tz   = 'UTC+08:00'
$RUN  = 'run-20261002-220723-mimo'

$reqs = @()
foreach ($l in [IO.File]::ReadAllLines((Join-Path $tmp 'requests.jsonl'))) { if ($l.Trim()) { $reqs += ($l | ConvertFrom-Json) } }
$idx  = [IO.File]::ReadAllText((Join-Path $tmp 'case-index-b05.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json

$docIds = @($reqs | Where-Object { $_.type -eq 'documentation' } | ForEach-Object { $_.id })
$fontIds = @($reqs | Where-Object { $_.type -eq 'fonts' } | ForEach-Object { $_.id })
$resIds  = @($reqs | Where-Object { $_.type -eq 'research' } | ForEach-Object { $_.id })
$rendIds = @($reqs | Where-Object { $_.type -eq 'render' } | ForEach-Object { $_.id })

# ---------------------------------------------------------------- tool-usage.jsonl
$tu = @()
$tu += ([ordered]@{ tool_id='tu-01'; tool='plan.md 10 屏选题、画幅与数据口径表（人写综合）'; category='选题与规划'
  when='2026-10-08T09:02:00.000+08:00'; affected_cases='*'; http_request_ids=@(); artifacts=@('tmp/run-20261002-220723-mimo/B05/plan.md')
  note='先定 10 屏的受众/画幅/比例/深浅底，保证 10 个宽高比互不重复，再定数据与不许写的话' })
$tu += ([ordered]@{ tool_id='tu-02'; tool='fetch-b05.ps1 真实抓取政策与行政研究资料'; category='资料研究'
  when='2026-10-08T09:14:43.371+08:00'; affected_cases='*'; http_request_ids=$resIds
  artifacts=@('tmp/run-20261002-220723-mimo/B05/research/')
  note='20 次 research 请求：18 次 200，1 次 404（shanghai.gov.cn 站内搜索），1 次网络失败（duckduckgo html 端点）。最终没有取得任何一条既有住宅加装电梯的费用分摊政策原文，因此画面不写条款、不写法定比例、不写补贴标准' })
$tu += ([ordered]@{ tool_id='tu-03'; tool='fetch-b05.ps1 文档与字体查询'; category='文档查阅'
  when='2026-10-08T09:06:00.000+08:00'; affected_cases='*'; http_request_ids=($docIds + $fontIds)
  artifacts=@('tmp/run-20261002-220723-mimo/B05/docs/')
  note='9 次 documentation（ai-guide.md 与 snapshot.muedsa.com 的 parser-tags/painting/enums/transform/rendering/decorated-box/source-index/faq）+ 1 次 /fonts，全部 200' })
$tu += ([ordered]@{ tool_id='tu-04'; tool='calc-b05.ps1 -> calc-b05.json 权威数据集'; category='计算与数据'
  when='2026-10-08T09:40:00.000+08:00'; affected_cases='*'; http_request_ids=@()
  artifacts=@('tmp/run-20261002-220723-mimo/B05/calc-b05.ps1','tmp/run-20261002-220723-mimo/B05/calc-b05.json')
  note='三种分摊模型的权重和/单位权重/逐户金额、6 项造价与补贴、三段付款、12 项验收日期、65 天工期、十年总账全部由程序算出；weightSum 四舍五入到 2 位后再落盘，避免 6.6999999999999993 这类裸浮点进画面' })
$tu += ([ordered]@{ tool_id='tu-05'; tool='lib-b05.ps1 共享绘图库（刊头/脚注/剖面格/徽标/药丸/写盘与问题汇总）'; category='生成程序'
  when='2026-10-08T10:05:00.000+08:00'; affected_cases='*'; http_request_ids=@()
  artifacts=@('tmp/run-20261002-220723-mimo/B05/lib-b05.ps1')
  note='Section5 楼栋剖面在格高不足 60 时自动改单行排版，避免 case-07 的户号与态度叠印' })
$tu += ([ordered]@{ tool_id='tu-06'; tool='gen-b05-a/b/c.ps1 三段生成器（01-03 / 04-06 / 07-10）'; category='生成程序'
  when='2026-10-08T10:10:00.000+08:00'; affected_cases='*'; http_request_ids=@()
  artifacts=@('tmp/run-20261002-220723-mimo/B05/gen-b05-a.ps1','tmp/run-20261002-220723-mimo/B05/gen-b05-b.ps1','tmp/run-20261002-220723-mimo/B05/gen-b05-c.ps1')
  note='每次 -Round 2 都跑完整生成 + 文本越界守卫 + 属性校验，problems=0 才允许送渲染' })
$tu += ([ordered]@{ tool_id='tu-07'; tool='属性与尺寸校验（border / color / textAlign / boxShadow / fontStyle / 长小数）'; category='质量校验'
  when='2026-10-08T11:20:00.000+08:00'; affected_cases='*'; http_request_ids=@()
  artifacts=@('tmp/run-20261002-220723-mimo/B05/case-01/r02.snapshot','tmp/run-20261002-220723-mimo/B05/case-10/r02.snapshot')
  note='10 份 r02.snapshot 属性问题 0 个；PNG 实际尺寸与首个 Container 的 width/height 逐一对齐，10/10 无偏差' })
$tu += ([ordered]@{ tool_id='tu-08'; tool='render-b05.ps1 POST /snapshot'; category='服务渲染'
  when='2026-10-08T09:58:00.000+08:00'; affected_cases='*'; http_request_ids=$rendIds
  artifacts=@('tmp/run-20261002-220723-mimo/B05/requests.jsonl')
  note='38 次 render：32 次 200、6 次 400 PARSE_ERROR（border 写在圆上、Ts 第 12 个参数落进 bold 导致 fontStyle、color 写成 元），全部当场修好重交；0 次 429，ratelimit_remaining 最低 110' })
$tu += ([ordered]@{ tool_id='tu-09'; tool='read 工具看图（每件最终图都真实打开）'; category='视觉检查'
  when='2026-10-08T10:40:00.000+08:00'; affected_cases='*'; http_request_ids=@()
  artifacts=@('tmp/run-20261002-220723-mimo/B05/view/')
  note='read 工具按内容哈希缓存，连续读会返回上一张的字节；恢复办法是每次用 System.Drawing 生成一个文件名唯一、像素微调（或加边框）的新副本再读，读完核对刊头 NN/10 与画幅' })
$tu += ([ordered]@{ tool_id='tu-10'; tool='System.Drawing 尺寸 / SHA256 / 逐像素核验'; category='视觉检查'
  when='2026-10-08T11:05:00.000+08:00'; affected_cases='*'; http_request_ids=@()
  artifacts=@('tmp/run-20261002-220723-mimo/B05/promote-b05.ps1')
  note='10 件 final.png 与服务原始字节 SHA256 一致、final.snapshot 与 r02.snapshot 一致、PNG 尺寸与 DSL Container 一致，problems=0' })
$tu += ([ordered]@{ tool_id='tu-11'; tool='smoke-b05.ps1 两次真机冒烟渲染'; category='能力探测'
  when='2026-10-08T09:58:00.000+08:00'; affected_cases='shared'; http_request_ids=@('B05-rend-smoke-01','B05-rend-smoke-02')
  artifacts=@('tmp/run-20261002-220723-mimo/B05/smoke/')
  note='先用小图确认服务可达、字体与 8 位色可用，再批量送 10 屏' })
$tu += ([ordered]@{ tool_id='tu-12'; tool='mk-logs-b05 / gen-case-md-b05 / mk-metrics-b05 脚本'; category='日志与指标'
  when='2026-10-08T12:15:00.000+08:00'; affected_cases='*'; http_request_ids=@()
  artifacts=@('tmp/run-20261002-220723-mimo/B05/mk-logs-b05.ps1','tmp/run-20261002-220723-mimo/B05/gen-case-md-b05.ps1','tmp/run-20261002-220723-mimo/B05/mk-metrics-b05.ps1')
  note='从 JSONL 反查生成 tool-usage / case.md / task-metrics，不手写计数' })

$tuLines = @(); foreach ($t in $tu) { $tuLines += ($t | ConvertTo-Json -Compress -Depth 6) }
[IO.File]::WriteAllLines((Join-Path $tmp 'tool-usage.jsonl'), $tuLines, $utf8)
"tool-usage.jsonl rows = $($tuLines.Count)"

# ---------------------------------------------------------------- journey.json
$stages = @(
  [ordered]@{ step=1;  screen='case-01'; stage='看清现状'; persona='全体业主 / 牵头人'; surface='桌面 1600x1000';
    goal='一眼看清这栋楼现在什么态度、我家大概出多少'; entry='第一次打开工作台';
    key_facts=@('支持 9/12（75%）','已签约 7/12（58%）','顾虑 3 户：101、202、602','自付区间 0 - 42,985 元','状态快照 2026-10-08');
    action='点开右侧 KPI 与剖面里的 3 户顾虑'; exit='知道该先解决 3 条顾虑，也知道净自付是 288,000 元'; next='case-05' },
  [ordered]@{ step=2;  screen='case-05'; stage='把钱说清楚'; persona='全体业主（业主大会材料）'; surface='桌面 1760x900';
    goal='52.8 万到底怎么来的，比价是否离谱，补贴能抵多少'; entry='被问“凭什么收这么多”';
    key_facts=@('6 项合计 528,000 元','补贴 240,000 元（演示数据 DEMO）','净自付 288,000 元','三家同口径 528,000 / 556,000 / 535,000 元','工期 65 天');
    action='看同口径差额图与每户三个指标'; exit='预算口径达成一致，净自付 288,000 元被当作后续分摊的分母'; next='case-02' },
  [ordered]@{ step=3;  screen='case-02'; stage='算我家的账'; persona='单户居民（手机）'; surface='手机 540x1180';
    goal='我家这一户要掏多少钱'; entry='在群里收到一条链接';
    key_facts=@('602 室、6 层、78.9 平米','模型 A 42,985 元','模型 B 24,386 元','模型 C 47,213 元','权重和 6.70，单位权重 288,000 / 6.70 = 42,985');
    action='切换 A/B/C，拖动总造价滑杆 46.0 - 58.0 万元看区间'; exit='知道自己在三种规则下的数，也知道自己是最高的那一档'; next='case-03' },
  [ordered]@{ step=4;  screen='case-03'; stage='选规则'; persona='业主协商会'; surface='桌面 1500x980';
    goal='三种分摊规则各自的分布、极差与代价'; entry='拿着上一屏的数字来开会';
    key_facts=@('A 权重和 6.70、零负担 2 户','B 309.08 元每平米、零负担 0 户','C 权重和 6.10、零负担 4 户','最大极差 24,386 元，出现在 102、202','投票 A 7 票、C 3 票、未选 2 户');
    action='逐列比对 12 户在三种规则下的金额与极差'; exit='规则被选定（本套产品默认 A），极差最大的两户被点名优先沟通'; next='case-04' },
  [ordered]@{ step=5;  screen='case-04'; stage='破顾虑'; persona='牵头人工作台'; surface='桌面 1440x1024';
    goal='把“不同意”变成有负责人、有方案、有截止的条目'; entry='从上一屏拿到 101、202、602 三个重点';
    key_facts=@('101 采光与通行 —— 井道外移 0.6 米，截止 10-12（剩余 4 天）','202 运行噪音 —— 夜间复测 10-14 22:00，截止 10-15（剩余 7 天）','602 分摊金额 —— 三模型试算，截止 10-18（剩余 10 天）','三张剖面格子把 3 户标红');
    action='按截止日期逐条销项，先给数字再谈感受'; exit='3 条顾虑都有下一次动作和时间，可以进签约'; next='case-06' },
  [ordered]@{ step=6;  screen='case-06'; stage='凑齐 12/12'; persona='单户居民（手机）'; surface='手机 480x1040';
    goal='现在到哪一步了，我怎么签字'; entry='顾虑答复完成后收到通知';
    key_facts=@('意愿征询 2026-09-12 至 09-30，支持 9/12','方案公示 2026-10-01 至 10-07，公示 7 天','异议期 2026-10-08 至 10-14，第 1 天 / 共 7 天','已签约 7 / 12','备案与开工预计 2026-10-20');
    action='提交签约授权书；成功看到受理编号 WT3-20261008-07，失败看到 7.3 MB 超限提示';
    exit='要么提交成功，要么拿着明确的失败原因重试'; next='case-07' },
  [ordered]@{ step=7;  screen='case-07'; stage='最后一户确认'; persona='602 室（平板，面签场景）'; surface='平板 900x1340';
    goal='把这份对我最不利的算法看清楚再签'; entry='牵头人当面打开这一屏';
    key_facts=@('本户在剖面中的位置高亮','模型 A 自付 42,985 元，全楼最高','三期 30% / 40% / 30% = 12,896 + 17,194 + 12,895','工期 65 天','每年公共支出 13,800 元');
    action='逐条核对三项确认，点“确认并提交签约”；也可返回修改';
    exit='12 / 12 齐，可以进开工倒计时'; next='case-08' },
  [ordered]@{ step=8;  screen='case-08'; stage='看着它盖起来'; persona='全体业主（公告屏 / 群内长图）'; surface='宽屏 1920x760';
    goal='今天到底干到哪一步了'; entry='开工后的每周更新';
    key_facts=@('开工 2026-10-20，总工期 65 天','6 段里程碑 10+10+14+15+8+8','当前第 28 天，进度 43.1%','现场记录 2026-11-16','预计交付 2026-12-23');
    action='对照里程碑看当天三条现场记录'; exit='知道下一段是“井道与玻璃幕墙 第 8 天 / 共 14 天”'; next='case-09' },
  [ordered]@{ step=9;  screen='case-09'; stage='交付验收'; persona='验收组（业委会 + 居委会 + 特检院）'; surface='竖屏 1000x1560';
    goal='12 项逐条打勾，未过项要有负责人和期限'; entry='2026-12-19 联合验收当天';
    key_facts=@('12 项：10 合格 / 1 待检 / 1 整改','待检：电梯监督检验合格证，已预约 12-19','整改：单元门口高差实测 35 mm，要求不大于 15 mm','责任期限 12-21','首次运行记录 2026-12-19 09:12');
    action='打印本页逐项签字，两条未过项带走'; exit='交房钥匙可以发，但两条尾巴要跟到 12-21'; next='case-10' },
  [ordered]@{ step=10; screen='case-10'; stage='十年之后回头看'; persona='全体业主（复盘材料）'; surface='桌面 1560x900';
    goal='这十年一共花多少，选对规则省多少'; entry='交付后第一年做复盘';
    key_facts=@('一次性自付 288,000 元','十年运行支出 138,000 元','十年合计 426,000 元','每户十年 35,500 元','602 室 A 63,582 / B 36,071 / C 69,836，相差 33,765 元');
    action='看第 0 到第 10 年的累计柱与 602 室三模型对照'; exit='下次再谈分摊时，有一张十年尺度的账可看'; next=$null }
)

$journey = [ordered]@{
  schema_version = 1
  task_id = 'B05'
  task_name = 'product from zero'
  run_id = $RUN
  timezone = $tz
  generated_from = @('tmp/run-20261002-220723-mimo/B05/case-index-b05.json','tmp/run-20261002-220723-mimo/B05/requests.jsonl')
  product = [ordered]@{
    name = '同梯 TongTi'
    tagline = '老旧小区加装电梯的共识与分摊工作台'
    problem = '一栋 6 层 12 户的老楼要加装电梯，卡住的从来不是“装不装”，而是三件事凑不到一起：谁出多少说不清、谁不同意没销项、钱和工期没有一张所有人都认的账。牵头人只能在微信群里贴 Excel 截图，居民只能凭感觉吵架。'
    primary_users = @('牵头人 / 业委会成员（要推进度、销顾虑）','单户居民（要知道我家出多少）','楼组长与居委会（要留痕、要公示）','验收与施工各方（要有清单和节点）')
    promise = '一栋楼一个口径：净自付只有一个数（288,000 元），规则可切换，账可追到十年。'
    validation = '本题为零到一的概念设计，未做任何真实用户访谈或可用性测试；产品判断均为设计假设，不声称已被用户验证。'
  }
  journey_design = [ordered]@{
    scene = '梧桐里小区 3 号楼，一梯两户 6 层共 12 户，西 76.4 平米 / 东 78.9 平米，总建筑面积 931.8 平米'
    today = '2026-10-08（case-01 状态快照、case-04 剩余天数、case-06 异议期第 1 天三者同日）'
    start = '2026-10-08（征询已完成、公示已结束、异议期第 1 天）'
    construction_start = '2026-10-20（开工 = 第 1 天）'
    construction_end = '2026-12-23（第 65 天）'
    acceptance = '2026-12-19（联合验收）'
    screen_count = 10
    stage_order = @('case-01','case-05','case-02','case-03','case-04','case-06','case-07','case-08','case-09','case-10')
    stage_count = 10
    distinct_canvases = 10
    surfaces = @('桌面','手机','平板','宽屏','竖屏')
  }
  stages = $stages
  cross_screen_consistency = [ordered]@{
    shared_numbers = [ordered]@{
      households = 12; floors = 6; total_area_sqm = 931.8
      gross_cost_yuan = 528000; subsidy_demo_yuan = 240000; net_self_pay_yuan = 288000
      annual_recurring_yuan = 13800; ten_year_recurring_yuan = 138000; ten_year_total_yuan = 426000
      ten_year_per_household_yuan = 35500
      model_a_yuan = 42985; model_b_yuan = 24386; model_c_yuan = 47213
      support_9_of_12 = '75%'; signed_7_of_12 = '58%'; schedule_days = 65; progress_day28 = '43.1%'
    }
    shared_attitudes = [ordered]@{ signed = 7; agreed = 2; concerned = 3; concerned_units = @('101','202','602') }
    shared_dates = @('2026-10-08 快照日','2026-10-20 开工','2026-11-16 现场记录','2026-12-19 验收与首次运行','2026-12-21 未过项责任期限','2026-12-23 交付')
    audit = '对 10 份 final.snapshot 的可见文本做过跨屏比对：288,000 出现在 02/03/04/10，42,985 出现在 01/02/03/04/05/07，7 / 12 与 9 / 12 同时出现在 01/06，2026-10-08 同时出现在 01/06，65 天出现在 05/07/08'
  }
  state_feedback = @(
    [ordered]@{ state='提交成功'; screen='case-06'; copy='401 室签约提交成功 · 受理编号 WT3-20261008-07'; color='青绿' }
    [ordered]@{ state='提交失败'; screen='case-06'; copy='602 室提交失败 · 授权书照片 7.3 MB，超过 5 MB 限制 · 请压缩后重试'; color='珊瑚' }
    [ordered]@{ state='进行中'; screen='case-06 / case-08'; copy='异议期 第 1 天 / 共 7 天；施工 第 28 天，进度 43.1%'; color='琥珀' }
    [ordered]@{ state='未通过项'; screen='case-09'; copy='待检（已预约 12-19）与整改（35 mm / 要求不大于 15 mm）各 1 项，责任期限 12-21'; color='琥珀 / 珊瑚' }
    [ordered]@{ state='边界提示'; screen='case-07'; copy='主按钮“确认并提交签约”与次按钮“返回修改”并列，避免误签'; color='橙 / 描边' }
  )
  claims_discipline = [ordered]@{
    no_policy_claims = '研究过程中未取得任何一条既有住宅加装电梯费用分摊的政策原文，因此 10 屏里不出现法条引用、不出现法定分摊比例、不出现任何地区的补贴标准。'
    money_labeling = '所有金额都标注为演示数据 DEMO 或样例价格，未做真实采购询价。'
    weights_are_product_rules = 'A / B / C 三套权重是本产品自定义的分摊规则，画面明写“不是法规要求”。'
    no_user_validation = '未做用户访谈、可用性测试或真实楼栋试点，不声称任何用户结论已被验证。'
    no_endorsements = '三家供应商、报价、工期、质保年限、检验结论、现场记录、负责人与截止日期均为演示样例，不对应任何真实企业或个人。'
    decoration_as_control = '装饰性元素只在能解释时承担控件含义（模型 A/B/C 的选择药丸、剖面中被高亮的本户格子、被点亮的里程碑圆点），并且每个都配文字标签。'
  }
  exit_paths = [ordered]@{
    happy = 'case-06 提交成功 -> case-07 确认 -> case-08 施工 -> case-09 验收 12/12 -> case-10 复盘'
    blocked = 'case-06 提交失败（文件超限）-> 压缩重试 -> 回到 case-06'
    contested = 'case-03 极差 24,386 元的两户优先 -> case-04 三条顾虑销项 -> 回到 case-06'
    pending = 'case-09 两项未过 -> 12-21 前闭环 -> 交付'
  }
}
[IO.File]::WriteAllText((Join-Path $out 'journey.json'), ($journey | ConvertTo-Json -Depth 8), $utf8)
'journey.json written'
