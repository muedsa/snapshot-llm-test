# mk-iter-b06.ps1 -- rebuild iterations.jsonl for B06 from requests.jsonl plus the
# observed findings of each real visual iteration.
# Timings, status, byte counts and on-disk paths are read from the append-only request
# log; only the human-observed findings/changes are supplied here (in Chinese, matching
# the B04 / B05 iteration logs of this same run).
# r01.snapshot is the working file and is regenerated between passes, so a DSL hash is
# only emitted for the attempt that the working file currently equals.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b6   = Join-Path $root 'tmp\run-20261002-220723-mimo\B06'
$utf8 = New-Object System.Text.UTF8Encoding($false)

$byId = @{}
foreach ($line in [IO.File]::ReadAllLines((Join-Path $b6 'requests.jsonl'), [Text.Encoding]::UTF8)) {
    if ($line.Trim().Length -eq 0) { continue }
    $e = $line | ConvertFrom-Json
    if ($e.id) { $byId[$e.id] = $e }
}

# view_path  = the file actually opened with the read tool
# dsl_final  = true when r01.snapshot still holds exactly this attempt's DSL
$iters = @(
  @{ id='B06-smoke-01'; case='smoke'; i=0; pass='smoke'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\smoke\smoke.png'
     verdict='accepted'
     findings=@('环形、扇形、刻度尺、百分比格、瀑布、色柱六类装置全部通过服务渲染出来')
     changes=@('在任何一件作品使用之前，先证明 Wedge6 / Arc6 / Hand6 / Ruler6 / Pct100 / Waterfall6 / ColStack6 对服务是安全的') }

  @{ id='B06-case-01-r01'; case='case-01'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-01\r01.png'
     verdict='needs-change'
     findings=@('版式、角标与价格条读起来正确','100抽x6、100抽x24、130抽x12 三行的心算步数记为 2，但这三种要先把抽数乘开再相除，应为 3 步')
     changes=@('calc 规则更新：含 x、kg 或「数字 + L」的包装记为 3 步') }
  @{ id='B06-case-01-a02'; case='case-01'; i=2; pass='a02'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\a01-66a6f0ff531643ab8378f65429407af1.png'
     verdict='accepted'
     findings=@('九行步数全部正确：500g 与 180g 是 2 步，1.2kg 与所有多支装是 3 步','无溢出、无重叠，页脚离画布边缘有余量')
     changes=@('接受为成品') }

  @{ id='B06-case-02-r01'; case='case-02'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-02\r01.png'
     verdict='needs-change'
     findings=@('待服标记是浅灰圆，压在蓝色方框描边之下，看起来像金色圆点旁边的一个方块','「待服」文字用 SHADE6，在白卡上对比度不足')
     changes=@('待服标记改成 PHARM 色的双圆环，已服保留为 DOSE 实心圆','标签分别改用 subC 与 DOSE') }
  @{ id='B06-case-02-a02'; case='case-02'; i=2; pass='a02'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\a02-bae3f369281d4e9d93bbf74e3545fb07.png'
     verdict='needs-change'
     findings=@('标记现在读作「空心环」与「实心圆」两种，两处标签都清晰','图例仍写着「灰色 = 待服」，与新的蓝色圆环互相矛盾','页脚离画布下缘只剩约 4px')
     changes=@('图例改写为「实心金 = 已服 · 蓝色空心 = 待服；下方药格同色」') }
  @{ id='B06-case-02-a03'; case='case-02'; i=3; pass='a03'; final=$false; conf=$false
     view=''
     verdict='not-verified'
     findings=@('图例改写确实已经写进 DSL','这次 read 返回的是串图，报头是 04/10，因此这一版从未在屏幕上被确认过')
     changes=@('同一条图例改动在下一次渲染上得到确认，该次取代本次') }
  @{ id='B06-case-02-a04'; case='case-02'; i=4; pass='a04'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-02\a04.png'
     verdict='accepted'
     findings=@('图例与它所描述的标记一致','一周药格行高由 40 收到 36px，说明、来源与页脚相应上移，页脚留出 14px 边距')
     changes=@('接受为成品') }

  @{ id='B06-case-03-r01'; case='case-03'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\y03-46ce5f1cb367408f9eefc9b5ee76073f.png'
     verdict='needs-change'
     findings=@('参考区间条继承了状态色，出界的指标因此显示红色区间条，让人以为区间本身有问题','整数化验值印成 142.00、452.00、148.00、33.00','右栏底部约 90px 空白')
     changes=@('区间条颜色与状态色分离，改成中性带透明度的白色；指针、数值块与左侧条保留状态色','新增 LabN，整数不再带小数尾零','补一条解释性说明与「这次不用动的 3 项」区块') }
  @{ id='B06-case-03-a02'; case='case-03'; i=2; pass='a02'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\a03-1f7c7df7a9e04189a96fc501554e2fba.png'
     verdict='needs-change'
     findings=@('中性区间条配状态色指针读起来正确，说明文字解释了两者的区别','数值已是 142、5.80、5.61、452、148、33','总胆固醇区间印成 3 - 5.2，丢掉了 .0','尿酸单位印成 ASCII 的 umol/L 而不是 μmol/L')
     changes=@('rangeText 改为：只要该行带小数，区间就统一保留一位小数','单位更正为 μmol/L') }
  @{ id='B06-case-03-a04'; case='case-03'; i=3; pass='a04'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-03\a04.png'
     verdict='accepted'
     findings=@('3.0 - 5.2 mmol/L 与 208 - 428 μmol/L 都正常渲染，希腊字母 μ 正确','无溢出、无重叠，右栏一直填到来源行')
     changes=@('接受为成品') }

  @{ id='B06-case-04-r01'; case='case-04'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\z04-e5d242a932cf4863913f5919b45497f6.png'
     verdict='needs-change'
     findings=@('档位单价只显示两位小数，导致画面上的算式 60 x 0.64 = 38.28 不成立','标题与页脚硬编码 +80.6%，而 KPI 卡由 130.86 到 236.63 算出的是 +80.8%','脚注把电费涨幅写成「电价涨幅」，而单价口径其实只涨 11.8%','两根档位条各自按自身总量归一，于是 220 度与 356 度画成等长，与标题矛盾')
     changes=@('档位单价统一显示 4 位小数','标题与页脚改为由 calc 计算（80.8%）','脚注改写为「电费涨幅」','Tier-Bar 接受共享最大值，两根条同尺') }
  @{ id='B06-case-04-a02'; case='case-04'; i=2; pass='a02'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\a04-bdf9ac13377b4b31abb711f89ebcb49d.png'
     verdict='needs-change'
     findings=@('四位小数修正了画面上的算术：60 x 0.6380 = 38.28、76 x 0.8880 = 67.49','标题仍是 80.6%，与 KPI 的 80.8% 不一致','两根条仍然等长')
     changes=@('标题与页脚绑定到 calc；两期共用同一刻度') }
  @{ id='B06-case-04-a03'; case='case-04'; i=3; pass='a03'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-04\a03.png'
     verdict='accepted'
     findings=@('标题与页脚都是 +80.8%，与 KPI 一致','两根条里一档的蓝色段完全等长，而「本期」延伸更远，这正是本页要讲的论点','无溢出、无重叠')
     changes=@('接受为成品') }

  @{ id='B06-probe-hatch'; case='probe-hatch'; i=1; pass='probe'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\probe-hatch.png'
     verdict='needs-change'
     findings=@('在 y=110 的扫描线上，box1 的斜纹从 x=130 而非 24 开始，box2 的斜纹到 458 而非 736 结束，窄条从 x=65 而非 24 开始','两个 ClipR 框都被输出成 left=130.11，恰好等于条长：一个名为 L 的局部变量因为 PowerShell 变量不区分大小写，悄悄覆盖了 l（left）位置参数','服务照样返回 200 而几何是错的，所以这个缺陷只能靠看图和像素扫描发现')
     changes=@('长度类局部变量改名为 barLen 与 halfSpan，任何局部变量都不可能再撞上位置参数','把这条陷阱写进 lib-b06 的头部注释') }
  @{ id='B06-probe-hatch-a2'; case='probe-hatch'; i=2; pass='probe'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\probe-hatch-a2.png'
     verdict='accepted'
     findings=@('y=110 现在依次是 斜纹 24..354、真正的页面底色空档 354..405、斜纹 406..735，与书写的几何完全一致','y=232 上窄条横跨 24..735，两个圆角都被覆盖，没有任何外溢','圆角裁剪被尊重，斜线一直铺到四个角')
     changes=@('在 case-07 依赖它之前，先证明 Hatch6 对服务是安全的') }

  @{ id='B06-case-05-a01'; case='case-05'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-05\a01.png'
     verdict='needs-change'
     findings=@('三栏站牌、倒计时主视觉、按比例的等待条与换乘卡在 1920x620 内无溢出','第 2、3 班的等待条填充用的是偏暗的细线色调，压在更暗的轨道上，两层灰几乎分不开','左侧没有视觉锚点，倒计时与标题挤在同一块平坦面板上')
     changes=@('非首班的填充改用 sub 色调，与轨道拉开对比','倒计时块背后加一块圆角子面板作为锚点') }
  @{ id='B06-case-05-a02'; case='case-05'; i=2; pass='a02'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-05\a02.png'
     verdict='accepted'
     findings=@('填充现在清晰可辨，并在同一量程上与 3 / 9 / 16 分钟保持比例','倒计时子面板成为左侧锚点，与右侧三栏取得平衡','报头 05/10，无溢出、无重叠')
     changes=@('接受为成品') }

  @{ id='B06-case-06-a01'; case='case-06'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-06\a01.png'
     verdict='needs-change'
     findings=@('两张图、四针刻度与三行对照在 900x1400 内都没有被裁切','KPI 显示 13.8%，而标题、刻度与说明都写 13.84%；名义费率显示 7.2%，别处写 7.20%','白色的 536 标签压在洋红色手续费帽上，而不是压在本金条上')
     changes=@('KPI 数值改为两位小数，读作 7.20% 与 13.84%','536 标签下移到手续费帽之下、灰色本金条之上') }
  @{ id='B06-case-06-a02'; case='case-06'; i=2; pass='a02'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-06\a02.png'
     verdict='needs-change'
     findings=@('KPI 现在是 7.20% 与 13.84%，与刻度、说明、页脚一致','标题仍写 7.2%，而其余各处都是 7.20%','13.03% 的图例印成「月 1.0862 x 12」，没有百分号，读起来像个普通倍数')
     changes=@('标题改为 7.20%','图例改为「月 1.0862% x 12」') }
  @{ id='B06-case-06-a03'; case='case-06'; i=3; pass='a03'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\c06-3c415662e820464c844d7b7ca0b2e550.png'
     verdict='accepted'
     findings=@('全页每个费率现在都以同一精度渲染，论点不再被四舍五入削弱','报头 06/10；说明、来源与页脚都离画布边缘有余量','串图的读取一律作废，本次改用带描边的全新 GUID 副本确认')
     changes=@('接受为成品') }

  @{ id='B06-case-07-a01'; case='case-07'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-07\a01.png'
     verdict='needs-change'
     findings=@('台账、争议斜纹、逐期余额条与两条结局卡都正常渲染，Hatch6 的四角都被覆盖','押金行用的是与扣减相同的靛蓝色，但它其实是一笔进项','560x1180 全部容纳，无溢出')
     changes=@('第 0 行金额改用中性墨色；固定扣减保留靛蓝、争议项保留申领色') }
  @{ id='B06-case-07-a02'; case='case-07'; i=2; pass='a02'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-07\a02.png'
     verdict='needs-change'
     findings=@('金额列现在把押金（墨色）、扣减（靛蓝）与争议（琥珀）分开','30% 的斜纹在 14px 的原因文字背后留下可见斜条，正好在需要阅读的地方增加噪点','说明文字在「合同措辞决定」之后换行，把一个短语拆成两半')
     changes=@('斜纹透明度由 4D 降到 33','说明拆成两行，换行点落在两句之间') }
  @{ id='B06-case-07-a03'; case='case-07'; i=3; pass='a03'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\c07-dd8452869a8641dc996cc25863e00caa.png'
     verdict='accepted'
     findings=@('更淡的斜纹仍标出两笔可争议行，而原因文字已经干净地压在上面','说明在两句之间换行，不再断在短语中间','报头 07/10，已用带描边的全新 GUID 副本确认')
     changes=@('接受为成品') }

  @{ id='B06-case-08-a01'; case='case-08'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-08\a01.png'
     verdict='needs-change'
     findings=@('100 格点阵、三句翻译、三个小时窗与结论行都在 1000x1000 内，无裁切','第 2、3 句换行到第二行时只剩一个字，视线卡在单字行上','第一句一行、后两句两行，三张卡的视觉重量不等')
     changes=@('每句都在自己的第一个逗号处断开，使每张卡恰好两行、断点落在分句之间','断开的两半必须能拼回 calc 原字符串，加断言保证数据集仍是权威来源') }
  @{ id='B06-case-08-a02'; case='case-08'; i=2; pass='a02'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\v8-80586b0417444682b118aa0cd1e25c01.png'
     verdict='accepted'
     findings=@('三句现在都断在分句之间，没有单字行','点阵确实填了 40 / 100 格：(i x 37) mod 100 是 0..99 的一个排列，恰好 40 个落在 40 以下，与画面说明完全一致','报头 08/10，已用带描边的全新 GUID 副本确认；B 区三卡共用一条基线，无溢出')
     changes=@('接受为成品') }

  @{ id='B06-case-09-a01'; case='case-09'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-09\a01.png'
     verdict='needs-change'
     findings=@('钟面、KPI 行、刻度尺与档位卡在 840x1340 内都正常，指针在 27 分钟，三段扇形为 0-15 / 15-60 / 60-120','档位卡标题写「累计」，但显示的是分段增量 3 / 6 / 8 而不是累计 3 / 9 / 17，最后一根条画成 8/17，看上去像还没到顶','刻度尺只有刻度没有数字，读者无从知道整条是 0 到 120 分钟')
     changes=@('档位数值改由 case09.cumulative 取而不是 case09.brackets，比例条分母改用 maxFeeAtLimit','刻度上加 0 / 15 / 27 / 60 / 120 五个数字，并加两道档位切换竖线') }
  @{ id='B06-case-09-a02'; case='case-09'; i=2; pass='a02'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\v9-ea368ab6b0a64d11a0283a5f009ca408.png'
     verdict='accepted'
     findings=@('累计现在是 3 / 9 / 17，最后一根条正好满格，与钟面上的 3 / +6 / +8 相互印证','刻度尺自带量程，不再依赖说明文字才读得懂','报头 09/10，已用带描边的全新 GUID 副本确认；来源与页脚离 1340 边缘还有 20px')
     changes=@('接受为成品') }

  @{ id='B06-case-10-a01'; case='case-10'; i=1; pass='a01'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\case-10\a01.png'
     verdict='needs-change'
     findings=@('五节点轨道、按比例的时间窗条、43/78 进度与打电话条带都在 1600x900 内','每个已完成节点的状态都用线路橙，三个过去状态与当前节点争夺注意力','打电话条带两半之间的分隔线是「细线色压面板色」，实际上看不见')
     changes=@('过去与未来的状态改用弱化色调，只有「派件中」保留强调色','分隔线提到中等明度，真正把两列分开') }
  @{ id='B06-case-10-a02'; case='case-10'; i=2; pass='a02'; final=$false; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\vA-90e39596b25d417eba0606f0533a5f74.png'
     verdict='needs-change'
     findings=@('状态行现在退到后面，只有「派件中」保留强调色，当前位置先被读到','分隔线可见，条带两半明确分开','分区提示写「前 4 个节点已完成」，而第 4 个节点画得更大并用强调色标为当前位置，两者互相矛盾')
     changes=@('提示改写为「已过 3 个节点，当前是第 4 个，最后一个是预计窗」') }
  @{ id='B06-case-10-a03'; case='case-10'; i=3; pass='a03'; final=$true; conf=$true
     view='tmp\run-20261002-220723-mimo\B06\view\vB-ac6ef67a17424e89bc2dbe26aadd3d7c.png'
     verdict='accepted'
     findings=@('提示现在与标记样式一致：三个已过、一个当前、一个预计','报头 10/10，已用带描边的全新 GUID 副本确认；900px 边缘内无溢出','时间窗条在同一条 105 分钟量程上保持比例：等 75 分钟，然后是 30 分钟的窗')
     changes=@('接受为成品') }
)

$out = Join-Path $b6 'iterations.jsonl'
if (Test-Path $out) { [IO.File]::Delete($out) }

$n = 0
foreach ($it in $iters) {
    if (-not $byId.ContainsKey($it.id)) { throw ("request " + $it.id + " not found in requests.jsonl") }
    $r = $byId[$it.id]

    $dslPath = ''; $dslSha = ''; $dslNote = ''
    if ($r.request_file) {
        $dslPath = $r.request_file
        if ($it.final) {
            if (Test-Path $dslPath) { $dslSha = (Get-FileHash $dslPath -Algorithm SHA256).Hash }
            $dslNote = 'the .snapshot on disk is this attempt byte for byte'
        } else {
            $dslNote = 'the working .snapshot was regenerated after this attempt, so only dsl_chars (exact at render time) is preserved'
        }
    }

    # png_sha256  = the service's raw response bytes; view_sha256 = the file actually opened
    $pngSha = ''
    if ($r.response_file -and (Test-Path $r.response_file)) {
        $pngSha = (Get-FileHash $r.response_file -Algorithm SHA256).Hash
    }
    $viewSha = ''
    if ($it.conf -and $it.view) {
        $vp = Join-Path $root $it.view
        if (Test-Path $vp) { $viewSha = (Get-FileHash $vp -Algorithm SHA256).Hash }
    }

    $obj = [ordered]@{
        task_id        = 'B06'
        case_id        = $it.case
        round          = 1
        iteration      = [int]$it.i
        pass           = [string]$it.pass
        request_key    = [string]$it.id
        request_id     = [string]$r.request_id
        type           = [string]$r.type
        method         = [string]$r.method
        path           = [string]$r.path
        started_at     = [string]$r.started_at
        ended_at       = [string]$r.ended_at
        timezone       = [string]$r.timezone
        http_status    = $r.http_status
        duration_ms    = $r.duration_ms
        response_bytes = $r.bytes
        attempt        = $r.attempt
        ratelimit_remaining = $r.ratelimit_remaining
        dsl_chars      = $r.dsl_chars
        dsl_path       = $dslPath
        dsl_sha256     = $dslSha
        dsl_note       = $dslNote
        png_path       = $r.response_file
        png_sha256     = $pngSha
        view_method    = 'read'
        view_path      = [string]$it.view
        view_sha256    = $viewSha
        view_confirmed = [bool]$it.conf
        view_note      = 'the read tool cross-delivers images; every view was confirmed by matching the PLAINSIGHT NN / 10 masthead in the returned pixels'
        verdict        = $it.verdict
        findings       = @($it.findings)
        changes        = @($it.changes)
        tool           = 'read'
    }
    [IO.File]::AppendAllText($out, ($obj | ConvertTo-Json -Compress -Depth 6) + "`n", $utf8)
    $n++
}
Write-Output ("iterations.jsonl written: {0} entries" -f $n)
