# mk-cases-b04.ps1 -- emit outputs/B04/case-NN/case.md
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$o    = Join-Path $root 'outputs\run-20261002-220723-mimo\B04'
$b    = Join-Path $root 'tmp\run-20261002-220723-mimo\B04'
$enc  = New-Object System.Text.UTF8Encoding($false)

$reqs = @(); Get-Content (Join-Path $b 'requests.jsonl') -Encoding UTF8 | ForEach-Object { $reqs += ($_ | ConvertFrom-Json) }
$iters = @(); Get-Content (Join-Path $b 'iterations.jsonl') -Encoding UTF8 | ForEach-Object { $iters += ($_ | ConvertFrom-Json) }

$D = @{}
$D['case-01'] = [ordered]@{
  idx=1; title='封面：23:59:60 那一秒钟'; aspect='1080 x 1528（0.71，竖幅）'
  question='读者第一眼要相信：这一秒真的存在。'
  content='巨号 `23:59:60` + 标题《多出来的那一秒》+ 61 格刻度条（60 个等高灰刻度 + 第 61 个琥珀刻度单独加高）+ 三格统计（27 次 / −37 s / 2035）+ 一段"编辑按"给出 3 567 天的空窗 + 三行来源。'
  data='61 格刻度按"前 60 格等长、第 61 格插入在 6 月 30 日或 12 月 31 日"绘制；统计块 27 来自 Leap_Second.dat（37 − 10），−37 s 来自 Bulletin C 72，2035 来自 CGPM 决议 4；3 567 天 = 2016-12-31 → 2026-10-07 的日历天数（编辑计算）。'
  citations='S1 Leap_Second.dat · S2 Bulletin C 72 · S3 IERS 闰秒页 · S6 CGPM 2022 决议 4 · S7 决议 5'
  demo='刊头《时间的边缘》第 03 期、编辑部署名标注 DEMO。'
}
$D['case-02'] = [ordered]@{
  idx=2; title='一秒有多长？——定义的五次落点'; aspect='1748 x 760（2.30，横幅）'
  question='"一秒"是量出来的，还是约定出来的？'
  content='标题 + 引句「秒不是量出来的，是约定出来的」+ 5 张并排卡片（1820 平太阳日 / 铯-133 原子 / 铯频率固定 / 光学钟超出 100 倍 / 下一次定义），每张带年份、小标题、四行说明与一个色标。'
  data='五次落点的年份与表述逐条对照决议 5 原文：1967 第 13 届 CGPM 定义 9 192 631 770 个周期、2018 第 26 届固定为 9 192 631 770 Hz、2022 第 27 届决议 5 指出光学标准高出最多 100 倍并安排 2026 审定 / 2030 通过。1820 年平太阳日的 1/86400 来自 IERS 闰秒页原文。'
  citations='S7 CGPM 2022 决议 5（DOI 10.59161/CGPM2022RES5E）· S8 BIPM 秒的重定义 · S3 IERS 闰秒页 · S5 TAI−UTC 历史表'
  demo='无 DEMO 元素；五张卡片的色标为版式装饰，不承载数值。'
}
$D['case-03'] = [ordered]@{
  idx=3; title='1972 年的三条钟：TAI / UTC / UT1'; aspect='1920 x 1080（1.78，16:9 横幅）'
  question='为什么要"跳"？因为有两条互不相同的尺在同时量地球。'
  content='三条并置的时间线：TAI 一条平直青线（连续、不跳）→ 琥珀色阶梯（UTC = TAI − 整数秒，每次上一级）→ 珊瑚色波形（UT1 不均匀）+ 右侧三张规则卡 + 一个 `|UT1 − UTC| 必须保持在 0.9 秒以内` 的引述框 + SCALE FREE 标注。'
  data='阶梯每次抬升 1 级对应 1972 年以来的 27 次插入；0.9 秒阈值与 UT1 的 VLBI 观测口径来自 IERS 闰秒页与地球自转页；纵轴标注"未按比例（SCALE FREE）"，不暗示任何数值刻度。'
  citations='S3 IERS 闰秒页 · S4 IERS 常用常数页 · S6 CGPM 2022 决议 4 · S12 IERS 地球自转页'
  demo='阶梯与波形均为编辑绘制的示意图，画面已写"示意图，纵向未按比例"。'
}
$D['case-04'] = [ordered]@{
  idx=4; title='27 次闰秒全表'; aspect='1200 x 1600（0.75，竖幅表格）'
  question='证据要能被读者自己核对——那就把 27 行全摆出来。'
  content='六列表格：序号 / 插入日期 / 生效日期 / MJD / TAI−UTC (s) / 距上次 (天)，共 27 行 + 表头 + 末行琥珀底纹与左侧色条（强调"37 s 至今有效"）+ 汇总条 + 两行口径说明 + 来源行。'
  data='全部字段由脚本从 `Leap_Second.decoded.txt` 程序化解析后写入 DSL，未手抄。第 1 行 1972-06-30 的 MJD 41499 = 生效首日 1972-07-01 的儒略日；"距上次"是相邻两行插入日期的日历天数差（184 / 365 / 366 / 547 / 2 557 / 1 096 / 1 277 / 1 095 / 550 等），逐格与日期差复核一致。'
  citations='S1 IERS Leap_Second.dat · S2 IERS Bulletin C 72（抓取 2026-10-07）'
  demo='口径行注明"插入日期 = 生效日期前一天的 23:59:60；MJD 为生效首日"，并说明 1972-01-01 的 10 s 是初始值、不计入 27 次。'
}
$D['case-05'] = [ordered]@{
  idx=5; title='27 次的节奏：年代与年份分布'; aspect='1100 x 1500（0.73，竖幅）'
  question='加秒的节奏是怎么从"很密"变成"零"的？'
  content='上半：按十年条形图（1970s 9 / 1980s 6 / 1990s 7 / 2000s 2 / 2010s 3 / 2020s 0，含 3/6/9 网格线与图例色块）；下半：1972–2026 年份矩阵，5 行 × 11 列共 55 格，左侧行区间标签 72–82 / 83–93 / 94–04 / 05–15 / 16–26，有闰秒的年份填充；再下：三条观察句 + 一张事实卡 + 来源行。'
  data='按插入年份归组，分子合计 27，分母 1972–2026 共 55 年；有闰秒的年份数 26（1972 计 2 次，26×1 + 1×2 = 27）；6 月 11 次 + 12 月 16 次 = 27；平均 625 天、最长 2 557 天（1998-12-31 → 2005-12-31）。'
  citations='S1 IERS Leap_Second.dat · S2 IERS Bulletin C 72'
  demo='三句观察与事实卡为编辑整理的读法，不冒充来源结论。'
}
$D['case-06'] = [ordered]@{
  idx=6; title='为什么步长必须是 1 秒'; aspect='1080 x 1080（1.00，方形）'
  question='为什么不能加 0.1 秒？'
  content='左右两块对照卡：左"常见的解释"（珊瑚色）讲 0.2 ms/天 × 5 000 天 = 1 秒这个量级演算；右"真正的约束"（琥珀色）引决议 4 的"UTC 与 TAI 只相差一个整数秒"。下方一条整数落点标尺：琥珀粗刻度 0…10 + 灰色 0.1 秒细梳齿 + 说明句。'
  data='0.2 ms/天来自 IERS 常用常数页（平太阳日目前比 86400 s 长约 0.2 ms）；0.9 秒门槛来自 IERS 闰秒页；整数秒约束来自 CGPM 决议 4。0.2 ms/d × 4500 d = 0.9 s 的换算在画面上标注为"本编辑的算术演示"，并补一句"UT1−UTC 的漂移并不匀速"。'
  citations='S4 IERS 常用常数页 · S3 IERS 闰秒页 · S6 CGPM 2022 决议 4'
  demo='0.1 秒梳齿是编辑画的示意刻度；标尺不带数值单位，不暗示真实比例。'
}
$D['case-07'] = [ordered]@{
  idx=7; title='23:59:60 那一分钟（2012-06-30 现场）'; aspect='1920 x 480（4.00，超长条）'
  question='那一分钟具体长什么样？'
  content='左侧标题块（23:59:60 那一分钟 / 2012 年 6 月 30 日 · 星期六 / 英文引句）；中间 61 格刻度条 + `:00 :10 :20 :30 :40 :50` 刻度标签 + 左 `23:59:00`、右 `23:59:60`（琥珀）+ 一行说明；右侧三个事实格（第 34 → 35 秒 / +1 s / Bulletin C）。'
  data='"On 30 June 2012, the last minute of the day has lasted 61 seconds." 为 IERS 闰秒页原文；第 25 次插入、TAI−UTC 34 → 35、生效 2012-07-01 来自 Leap_Second.dat。60 个灰刻度等长，第 61 个琥珀刻度单独加高，位置在 23:59:60。'
  citations='S3 IERS 闰秒页 · S1 IERS Leap_Second.dat · S2 IERS Bulletin C 72（抓取 2026-10-07）'
  demo='英文引句为原文直引；刻度条为编辑绘制的示意，不按真实时间比例。'
}
$D['case-08'] = [ordered]@{
  idx=8; title='一段创纪录的静默：空窗对照'; aspect='1400 x 1050（1.33，横幅）'
  question='现在到底多久没加了？跟以前比呢？'
  content='上半：全部 26 个相邻闰秒间隔的柱状图（最短 184 天 / 最长 2 557 天用珊瑚色高亮 / 平均 625 天用琥珀虚线并把标签放在左侧空白处）；下半：两根对照柱（上一纪录 2 557 天灰、当前 3 567 天琥珀）+ `1 010 天` 差值注释 + 三个统计格（184 / 625 / 2 557）+ 来源行。'
  data='26 个间隔 = 27 行相邻两行插入日期的日历天数差；平均 625 天 = 16255 ÷ 26 = 625.19 → 625；当前空窗 3 567 天 = 2016-12-31 → 2026-10-07（抓取日）；差值 1 010 天 = 3567 − 2557，约合 2 年 9 个月。'
  citations='S1 IERS Leap_Second.dat · S2 IERS Bulletin C 72'
  demo='全部为编辑依据一手数据计算，画面写明"间隔、平均值与比较由本编辑据表计算"。'
}
$D['case-09'] = [ordered]@{
  idx=9; title='决定：从 0.9 秒到 2035'; aspect='800 x 2000（0.40，竖长条）'
  question='谁在什么时候决定？下一次是什么时候？'
  content='一条纵向时间线，9 个节点（1972 / 2012 / 2016 / 2017 / 2018 / 2022 / 2026 / 2030 / 2035），每个节点配一条主行 + 一条细节行；节点圆点按性质着色（青 = 数据事件、琥珀 = 决议、珊瑚 = 门槛/待定）；末尾一个琥珀描边的收尾面板给出下一步；三行来源含 DOI。'
  data='1972 TAI−UTC = 10 s 与 0.9 秒门槛、2012 第 25 次、2016 第 27 次、2017 起 −37 s 来自 Leap_Second.dat 与 Bulletin C 72；2018 决议 4 的"UTC 是唯一推荐的国际参考时标"、2022 决议 4 的"2035 年前提高 |UT1−UTC| 上限"与"可能需要首次负闰秒"、2026 第 28 届 CGPM 审定实施计划、2030 第 29 届 CGPM 通过新定义，均对照决议 4 / 决议 5 原文。'
  citations='S6 CGPM 2022 决议 4 · S7 决议 5 · S3 IERS 闰秒页 · S2 Bulletin C 72 · S5 TAI−UTC 历史表'
  demo='节点的配色分组与两行式摘要为编辑编排；收尾面板属编辑解读。'
}
$D['case-10'] = [ordered]@{
  idx=10; title='反向的一秒与工程师工具箱'; aspect='1600 x 640（2.50，横幅）'
  question='负闰秒是什么？我该注意什么？'
  content='左侧"反向的一秒"面板：CGPM 决议 4 引文 + 用「—— 以下为编辑解释，非引文：」明确分隔的解释段 + 一个 3 格迷你示意图（保留 / 跳过（拟议）/ 保留，含 23:59:58 → 23:59:59 → 00:00:00 时间标注，标签在面板内）；右侧"工程师工具箱"6 条建议 + `编辑建议` 色标；底部来源行。'
  data='决议 4 关于"可能需要首次负闰秒，而它的插入从未被预见或测试过"为原文；删掉 23:59:59 的解释段为编辑解释（画面已分隔）；工具箱 6 条参考 ITU-R TF.460-6、IANA tzdb、RFC 5905 的处理惯例，但画面与来源行均标注"工具箱 6 条为编辑建议，非来源结论"。'
  citations='S6 CGPM 2022 决议 4 · S7 决议 5 · S2 IERS Bulletin C 72 · S9 ITU-R TF.460-6 · S10 IANA tzdb · S11 RFC 5905'
  demo='工具箱 6 条标注为编辑建议；示意图不按时间比例。'
}

foreach ($i in 1..10) {
  $cid = 'case-{0:d2}' -f $i
  $caseMeta = $D[$cid]
  if ($null -eq $caseMeta) { throw "missing metadata for $cid" }
  $png = Get-Item (Join-Path $o "$cid\final.png")
  $snap = Get-Item (Join-Path $o "$cid\final.snapshot")
  $round = (Get-Content (Join-Path $o "$cid\.round") -Raw).Trim()

  $req = @($reqs | Where-Object { $_.case_id -eq $cid -and $_.http_status -eq 200 } | Sort-Object started_utc)
  $it = @($iters | Where-Object { $_.case_id -eq $cid } | Sort-Object { $_.round })

  $lines = @()
  $lines += '# case-{0:d2} —— {1}' -f $i, $caseMeta.title
  $lines += ''
  $lines += '- 任务：B04（researched visual special）· 运行：`run-20261002-220723-mimo` · 时区：UTC+08:00'
  $lines += '- 成品：`outputs/run-20261002-220723-mimo/B04/{0}/final.png` + 同名 `final.snapshot`（{1} 轮）' -f $cid, $round
  $lines += '- 画幅：{0}；`{1}` bytes PNG / `{2}` bytes DSL' -f $caseMeta.aspect, $png.Length, $snap.Length
  $lines += '- 来源引用：{0}' -f $caseMeta.citations
  $lines += ''
  $lines += '## 这件作品回答什么'
  $lines += ''
  $lines += $caseMeta.question
  $lines += ''
  $lines += '## 画面内容'
  $lines += ''
  $lines += $caseMeta.content
  $lines += ''
  $lines += '## 数据与口径'
  $lines += ''
  $lines += $caseMeta.data
  $lines += ''
  $lines += '## 演示 / 非来源内容'
  $lines += ''
  $lines += $caseMeta.demo
  $lines += ''
  $lines += '## 真实渲染与迭代'
  $lines += ''
  foreach ($r in $req) {
    $lines += '- `{0}`  HTTP {1}  {2} ms  {3} B  {4} → {5}' -f $r.id, $r.http_status, $r.duration_ms, $r.bytes, $r.started_at, $r.ended_at
  }
  $lines += ''
  $lines += '| 轮次 | 类型 | 提交的改动 | 读图看到了什么 | 读图复核结论 |'
  $lines += '|---|---|---|---|---|'
  foreach ($x in $it) {
    $lines += '| {0} | {1} | {2} | {3} | {4} |' -f $x.round, $x.type, $x.change, $x.observation, $x.view_evidence
  }
  $lines += ''
  $lines += '所有 `read` / `render` 调用的 URL、HTTP 状态、耗时、字节数与服务返回的 `request_id` 均在'
  $lines += '`tmp/run-20261002-220723-mimo/B04/requests.jsonl`；迭代与看图证据在同目录 `iterations.jsonl`。'
  $lines += ''

  $path = Join-Path $o "$cid\case.md"
  [IO.File]::WriteAllText($path, (($lines -join "`r`n") + "`r`n"), $enc)
  "  wrote case-{0:d2}\case.md  ({1} bytes)" -f $i, (Get-Item $path).Length
}
