# calc-b06.ps1 -> calc-b06.json
# Every number the ten artworks show is computed here first, so the screens can
# only cite one authoritative dataset.  All monetary/unit values are DEMO data.
$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B06')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$R2 = { param($x) [math]::Round([double]$x, 2) }
$R3 = { param($x) [math]::Round([double]$x, 3) }

function Fmt([double]$v, [string]$f) { return $v.ToString($f) }

# ============================ case-01 unit-price shelf ============================
$g1 = @(
  @{ n = '原味核桃仁'; pack = '500g';        base = 500.0;  unit = 'g';   price = 49.90; uom = '每100g' }
  @{ n = '原味核桃仁'; pack = '1.2kg';      base = 1200.0; unit = 'g';   price = 118.00; uom = '每100g' }
  @{ n = '原味核桃仁'; pack = '180g';       base = 180.0;  unit = 'g';   price = 22.90; uom = '每100g' }
)
$g2 = @(
  @{ n = '纯牛奶'; pack = '250ml x 12';    base = 3000.0; unit = 'ml';  price = 49.90; uom = '每100ml' }
  @{ n = '纯牛奶'; pack = '1L x 6';        base = 6000.0; unit = 'ml';  price = 89.90; uom = '每100ml' }
  @{ n = '纯牛奶'; pack = '200ml x 24';    base = 4800.0; unit = 'ml';  price = 69.90; uom = '每100ml' }
)
$g3 = @(
  @{ n = '三层抽纸'; pack = '100抽 x 6';   base = 600.0;  unit = '抽';  price = 19.90; uom = '每100抽' }
  @{ n = '三层抽纸'; pack = '100抽 x 24';  base = 2400.0; unit = '抽';  price = 69.90; uom = '每100抽' }
  @{ n = '四层抽纸'; pack = '130抽 x 12';  base = 1560.0; unit = '抽';  price = 45.90; uom = '每100抽' }
)
$groups = @(
  @{ key = 'g1'; title = '坚果 · 按 100 克比'; unit = '100g'; items = $g1 }
  @{ key = 'g2'; title = '牛奶 · 按 100 毫升比'; unit = '100ml'; items = $g2 }
  @{ key = 'g3'; title = '抽纸 · 按 100 抽比'; unit = '100抽'; items = $g3 }
)
$shelf = @()
foreach ($g in $groups) {
  $rows = @()
  foreach ($it in $g.items) {
    $up = [math]::Round(($it.price / $it.base) * 100.0, 3)
    # on-shelf mental steps: pack -> base quantity, then price / quantity, then x100
    $steps = 2
    if ($it.pack -match 'x') { $steps = 3 }                # piece count must be multiplied out first
    if ($it.pack -match 'kg') { $steps = 3 }               # kg -> g
    if ($it.pack -match '^\d+(\.\d+)?L') { $steps = 3 }    # L -> ml
    $rows += [pscustomobject]@{
      name = $it.n; pack = $it.pack; base = $it.base; unit = $it.unit
      price = $it.price; uom = $it.uom
      unitPrice = $up; unitPriceText = ($up.ToString('0.00') + ' 元 / ' + $g.unit)
      mentalSteps = $steps
    }
  }
  $cheapestTotal = ($rows | Sort-Object price | Select-Object -First 1)
  $cheapestUnit  = ($rows | Sort-Object unitPrice | Select-Object -First 1)
  $dearestUnit   = ($rows | Sort-Object unitPrice | Select-Object -Last 1)
  $shelf += [pscustomobject]@{
    key = $g.key; title = $g.title; unit = $g.unit
    rows = $rows
    cheapestTotalPack = $cheapestTotal.pack
    cheapestUnitPack  = $cheapestUnit.pack
    dearestUnitPack   = $dearestUnit.pack
    upSpread = [math]::Round(($dearestUnit.unitPrice - $cheapestUnit.unitPrice), 3)
    upSpreadPct = [math]::Round((($dearestUnit.unitPrice / $cheapestUnit.unitPrice - 1) * 100.0), 1)
    disagree = ($cheapestTotal.pack -ne $cheapestUnit.pack)
  }
}
$shelfDisagree = @($shelf | Where-Object { $_.disagree }).Count

# ============================ case-02 medication card ============================
$medFrequency = 3
$medTodayTaken = 1
$medTodayLeft = $medFrequency - $medTodayTaken
$medTodayPct = [math]::Round($medTodayTaken / $medFrequency * 100.0, 1)
$week = @()
for ($d = 0; $d -lt 7; $d++) {
  $cells = @()
  for ($s = 0; $s -lt 3; $s++) {
    $st = '待服'
    if ($d -eq 0 -and $s -eq 0) { $st = '已服' }
    $cells += $st
  }
  $week += [pscustomobject]@{ day = ('周' + '一二三四五六日'[$d]); cells = $cells }
}
$med = [pscustomobject]@{
  brand       = '示例药 · 降压片（演示）'
  strength    = '5 mg / 片'
  frequency   = $medFrequency
  times       = @('08:00', '14:00', '20:00')
  withMeal    = '饭后 30 分钟内服'
  missedRule  = '想起来马上补；若已接近下一次，跳过这一次，绝不补两片'
  avoid       = '服药期间少吃西柚、少吃腌制品（演示禁忌，以说明书为准）'
  store       = '避光、阴凉、干燥处，不放浴室'
  todayTaken  = $medTodayTaken
  todayLeft   = $medTodayLeft
  todayPct    = $medTodayPct
  weekPlan    = 7 * $medFrequency
  week        = $week
}

# ============================ case-03 checkup rulers ============================
$lab = @(
  @{ k = '收缩压';      unit = 'mmHg';     lo = 90.0;   hi = 139.0;  val = 142.0;  step = 5.0;  scaleLo = 80.0;  scaleHi = 170.0
     act = '一周内在家测 3 次并记录';  when = '本周';  lvl = 2 }
  @{ k = '空腹血糖';    unit = 'mmol/L';   lo = 3.9;    hi = 6.1;    val = 5.8;    step = 0.2;  scaleLo = 3.0;   scaleHi = 8.0
     act = '维持现有作息';            when = '下次年度体检'; lvl = 0 }
  @{ k = '总胆固醇';    unit = 'mmol/L';   lo = 3.0;    hi = 5.2;    val = 5.61;   step = 0.2;  scaleLo = 3.0;   scaleHi = 7.5
     act = '3 个月后复查血脂';        when = '2027-01'; lvl = 1 }
  @{ k = '尿酸';        unit = 'μmol/L';  lo = 208.0;  hi = 428.0;  val = 452.0;  step = 20.0; scaleLo = 150.0; scaleHi = 550.0
     act = '3 个月后复查 + 少喝含糖饮料'; when = '2027-01'; lvl = 1 }
  @{ k = '血红蛋白';    unit = 'g/L';      lo = 130.0;  hi = 175.0;  val = 148.0;  step = 5.0;  scaleLo = 100.0; scaleHi = 200.0
     act = '维持现有作息';            when = '下次年度体检'; lvl = 0 }
  @{ k = '谷丙转氨酶';  unit = 'U/L';      lo = 0.0;    hi = 40.0;   val = 33.0;   step = 5.0;  scaleLo = 0.0;   scaleHi = 80.0
     act = '维持现有作息';            when = '下次年度体检'; lvl = 0 }
)
$labRows = @()
foreach ($x in $lab) {
  $off = ''
  $dist = 0.0
  if ($x.val -gt $x.hi) { $off = '偏高'; $dist = [math]::Round($x.val - $x.hi, 2) }
  elseif ($x.val -lt $x.lo) { $off = '偏低'; $dist = [math]::Round($x.lo - $x.val, 2) }
  else { $off = '在区间内' }
  $loP = [math]::Round(($x.lo - $x.scaleLo) / ($x.scaleHi - $x.scaleLo) * 100.0, 2)
  $hiP = [math]::Round(($x.hi - $x.scaleLo) / ($x.scaleHi - $x.scaleLo) * 100.0, 2)
  $vP  = [math]::Round(($x.val - $x.scaleLo) / ($x.scaleHi - $x.scaleLo) * 100.0, 2)
  $rFmt = '0'
  if ((($x.val % 1) -ne 0) -or (($x.hi % 1) -ne 0)) { $rFmt = '0.0' }
  $rTxt = ($x.lo.ToString($rFmt) + ' – ' + $x.hi.ToString($rFmt))
  $labRows += [pscustomobject]@{
    name = $x.k; unit = $x.unit; lo = $x.lo; hi = $x.hi; val = $x.val
    scaleLo = $x.scaleLo; scaleHi = $x.scaleHi; step = $x.step
    status = $off; distance = $dist
    pctLo = $loP; pctHi = $hiP; pctVal = $vP
    rangeText = $rTxt
    action = $x.act; when = $x.when; level = $x.lvl
    ticks = [int][math]::Round(($x.scaleHi - $x.scaleLo) / $x.step)
  }
}
$labStat = [pscustomobject]@{
  total = $labRows.Count
  normal = @($labRows | Where-Object { $_.level -eq 0 }).Count
  recheck = @($labRows | Where-Object { $_.level -eq 1 }).Count
  sooner = @($labRows | Where-Object { $_.level -eq 2 }).Count
}

# ============================ case-04 tiered electricity ============================
$tiers = @(
  @{ name = '第 1 档'; from = 1;    to = 190;  rate = 0.5880 }
  @{ name = '第 2 档'; from = 191;  to = 280;  rate = 0.6380 }
  @{ name = '第 3 档'; from = 281;  to = 9999; rate = 0.8880 }
)
function Split-Tier([int]$kwh) {
  $left = $kwh; $out = @()
  foreach ($t in $tiers) {
    $cap = $t.to - $t.from + 1
    if ($t.to -ge 9999) { $cap = 99999 }
    $take = [math]::Min($left, $cap)
    $out += @{ name = $t.name; kwh = $take; rate = $t.rate; cost = [math]::Round($take * $t.rate, 2) }
    $left -= $take
    if ($left -le 0) { break }
  }
  return ,$out
}
$prevKwh = 220; $curKwh = 356
$prevSplit = Split-Tier $prevKwh
$curSplit  = Split-Tier $curKwh
$prevCost = [math]::Round((($prevSplit | ForEach-Object { $_.cost }) | Measure-Object -Sum).Sum, 2)
$curCost  = [math]::Round((($curSplit  | ForEach-Object { $_.cost }) | Measure-Object -Sum).Sum, 2)
$deltaCost = [math]::Round($curCost - $prevCost, 2)
$deltaKwh = $curKwh - $prevKwh
$prevRate = [math]::Round($prevCost / $prevKwh, 4)
$curRate  = [math]::Round($curCost / $curKwh, 4)
# per-tier cost attribution: hold tier boundaries fixed, add this period's kwh on top
$attrib = @()
for ($i = 0; $i -lt $tiers.Count; $i++) {
  $pk = 0; if ($i -lt $prevSplit.Count) { $pk = $prevSplit[$i].kwh }
  $ck = 0; if ($i -lt $curSplit.Count) { $ck = $curSplit[$i].kwh }
  $add = $ck - $pk
  $attrib += @{ name = $tiers[$i].name; addKwh = $add; rate = $tiers[$i].rate; addCost = [math]::Round($add * $tiers[$i].rate, 2) }
}
$attrSum = [math]::Round((($attrib | ForEach-Object { $_.addCost }) | Measure-Object -Sum).Sum, 2)
$attrTier3 = @($attrib | Where-Object { $_.name -eq '第 3 档' })[0]
$tier3Share = [math]::Round($attrTier3.addCost / $deltaCost * 100.0, 1)
$elec = [pscustomobject]@{
  tiers = $tiers
  prev = [pscustomobject]@{ kwh = $prevKwh; cost = $prevCost; rate = $prevRate; split = $prevSplit }
  cur  = [pscustomobject]@{ kwh = $curKwh;  cost = $curCost;  rate = $curRate;  split = $curSplit  }
  deltaKwh = $deltaKwh
  deltaCost = $deltaCost
  deltaKwhPct = [math]::Round(($curKwh / $prevKwh - 1) * 100.0, 1)
  deltaCostPct = [math]::Round(($curCost / $prevCost - 1) * 100.0, 1)
  ratePct = [math]::Round(($curRate / $prevRate - 1) * 100.0, 1)
  attribution = $attrib
  attributionCheck = $attrSum
  tier3Share = $tier3Share
  tier2Share = [math]::Round(100.0 - $tier3Share, 1)
  note = '阶梯机制依据检索摘要（发改价格〔2011〕2617号，二手来源）；本图三档电量与单价均为演示数据 DEMO'
}

# ============================ case-05 platform display ============================
$metro = [pscustomobject]@{
  line = '3 号线'
  dir = '往 江湾新城'
  now = '07:39'
  trains = @(
    @{ no = 1; eta = '07:42'; min = 3; load = '舒适'; cars = 6 }
    @{ no = 2; eta = '07:48'; min = 9; load = '较挤'; cars = 6 }
    @{ no = 3; eta = '07:55'; min = 16; load = '舒适'; cars = 6 }
  )
  platform = '站台 A'
  transfer = @(
    @{ line = '7 号线'; to = '往 机场东'; walk = '换乘 180 米 · 步行 3 分钟'; open = '本侧乘车' }
    @{ line = '12 号线'; to = '往 芦潮港'; walk = '换乘 240 米 · 步行 4 分钟'; open = '对侧乘车' }
  )
  lastTrain = '末班车进站前 3 分钟停止售票（来源：上海地铁官方页面检索摘要，2026-10-08）'
  nextLast = '本方向末班车 22:47'
}

# ============================ case-06 installment ============================
$prin = 6000.0; $nper = 12; $feeRate = 0.0060
$feePer = [math]::Round($prin * $feeRate, 2)                    # 36.00  (rate applied to the full amount each period)
$payPer = [math]::Round($prin / $nper + $feePer, 2)             # 536.00
$totalPaid = [math]::Round($payPer * $nper, 2)
$totalFee = [math]::Round($totalPaid - $prin, 2)
$nominalPct = [math]::Round($totalFee / $prin * 100.0, 2)
# monthly IRR: 6000 = sum payPer/(1+r)^t
function Get-IRR([double]$pv, [double]$pmt, [int]$n) {
  $lo = -0.05; $hi = 0.30
  for ($i = 0; $i -lt 200; $i++) {
    $mid = ($lo + $hi) / 2.0
    $f = 0.0
    for ($t = 1; $t -le $n; $t++) { $f += $pmt / [math]::Pow((1.0 + $mid), $t) }
    if ($f -gt $pv) { $lo = $mid } else { $hi = $mid }
  }
  return ($lo + $hi) / 2.0
}
$mr = Get-IRR $prin $payPer $nper
$aprSimple = [math]::Round($mr * 12 * 100.0, 2)
$aprEff = [math]::Round(([math]::Pow((1.0 + $mr), 12) - 1) * 100.0, 2)
$avgOutstanding = [math]::Round(($prin + $prin / $nper) / 2.0, 2)
$bal = @(); $b = $prin
for ($t = 1; $t -le $nper; $t++) { $b -= ($prin / $nper); $bal += [math]::Round($b, 2) }
$install = [pscustomobject]@{
  price = $prin; periods = $nper; feeRatePer = $feeRate
  feePer = $feePer; payPer = $payPer; totalPaid = $totalPaid; totalFee = $totalFee
  nominalPct = $nominalPct
  monthlyIRR = [math]::Round($mr * 100.0, 4)
  aprSimple = $aprSimple; aprEff = $aprEff
  avgOutstanding = $avgOutstanding
  feeOnAvgPct = [math]::Round($totalFee / $avgOutstanding * 100.0, 2)
  balances = $bal
  compare = @(
    @{ name = '分期：12 期 x ' + $payPer.ToString('0') + ' 元'; cost = $totalFee; tag = '总多付' }
    @{ name = '一次付清'; cost = 0.0; tag = '基准' }
    @{ name = '同样 6,000 元存 12 个月（年化 1.65% 演示）'; cost = -99.0; tag = '反向收益' }
  )
  note = '名义费率 = 总手续费 / 商品价；年化按每期现金流内部收益率算出（月 ' + ([math]::Round($mr * 100.0, 4)).ToString('0.0000') + '%）；全部演示数据 DEMO'
}

# ============================ case-07 deposit waterfall ============================
$depositItems = @(
  @{ name = '水电燃气结余'; amt = -312.0;  kind = 'fixed'; why = '按抄表数结算，可核对' }
  @{ name = '物业费欠缴';   amt = -268.0;  kind = 'fixed'; why = '按缴费单核对' }
  @{ name = '家电清洗';     amt = -180.0;  kind = 'fixed'; why = '合同附件约定项' }
  @{ name = '墙面钉孔修复'; amt = -450.0;  kind = 'dispute'; why = '自然磨损还是人为损坏，看合同措辞' }
  @{ name = '退租清洁';     amt = -150.0;  kind = 'dispute'; why = '是否已含在月租里，看合同措辞' }
)
$depStart = 6000.0
$depFixed = [math]::Round((($depositItems | Where-Object { $_.kind -eq 'fixed' } | ForEach-Object { [math]::Abs($_.amt) }) | Measure-Object -Sum).Sum, 2)
$depDisp  = [math]::Round((($depositItems | Where-Object { $_.kind -eq 'dispute' } | ForEach-Object { [math]::Abs($_.amt) }) | Measure-Object -Sum).Sum, 2)
$depLow  = [math]::Round($depStart - $depFixed - $depDisp, 2)
$depHigh = [math]::Round($depStart - $depFixed, 2)
$depFlow = @(); $run = $depStart
$depFlow += @{ name = '押金原额'; amt = $depStart; running = $depStart; kind = 'start' }
foreach ($it in $depositItems) {
  $run = [math]::Round($run + $it.amt, 2)
  $depFlow += @{ name = $it.name; amt = $it.amt; running = $run; kind = $it.kind; why = $it.why }
}
$deposit = [pscustomobject]@{
  start = $depStart; items = $depositItems
  fixedTotal = $depFixed; disputeTotal = $depDisp
  refundIfAllCut = $depLow; refundIfDisputeKept = $depHigh
  swing = $depDisp
  flow = $depFlow
  deadline = '合同约定退租后 7 日内退还（演示约定 DEMO，以合同为准）'
}

# ============================ case-08 precipitation grid ============================
$precip = [pscustomobject]@{
  departAt = '08:00'
  windows = @(
    @{ h = '08:00–09:00'; p = 40; label = '通勤这 1 小时' }
    @{ h = '09:00–10:00'; p = 70; label = '到岗后第一小时' }
    @{ h = '10:00–11:00'; p = 20; label = '上午后段' }
  )
  decisionP = 40
  gridFilled = 40
  gridSize = 100
  carry = '带'
  translations = @(
    '它说的是「下不下」，不是「下多大、下多久」'
    '40% 不等于下 40 分钟，也不等于 40% 的地方在下'
    '同一时刻同一地点，长期看 100 次里有 40 次会下'
  )
  caution = '概率解释按通行气象含义；本轮研究未取得官方定义原文，故不引用任何标准条文'
}

# ============================ case-09 curbside parking ============================
$parkSteps = @(
  @{ from = 0;  to = 15;  fee = 3.00; label = '首 15 分钟' }
  @{ from = 15; to = 60;  fee = 2.00; label = '之后每 15 分钟' }
  @{ from = 60; to = 120; fee = 2.00; label = '之后每 15 分钟' }
)
$parkDial = @(
  @{ min = 0;   fee = 3.00; note = '0–15 分钟：3.00 元' }
  @{ min = 15;  fee = 6.00; note = '15–60 分钟：3 段 x 2.00 元' }
  @{ min = 60;  fee = 8.00; note = '60–120 分钟：4 段 x 2.00 元' }
)
$parkCum = @()
$cum = 0.0
foreach ($s in $parkDial) { $cum += $s.fee; $parkCum += @{ at = $s.min; cum = [math]::Round($cum, 2); note = $s.note } }
$parkTotal = [math]::Round($cum, 2)
$parking = [pscustomobject]@{
  rule = '首 15 分钟 3.00 元，之后每 15 分钟 2.00 元（演示规则 DEMO）'
  limitMinutes = 120
  windowStart = '08:00'; windowEnd = '20:00'
  arriveAt = '14:20'; leaveBy = '16:20'
  arriveMin = 14 * 60 + 20
  leaveMin  = 16 * 60 + 20
  nowMin    = 14 * 60 + 47
  nowAt = '14:47'
  usedMin = 27
  usedFee = 5.00
  steps = $parkSteps
  brackets = $parkDial
  cumulative = $parkCum
  maxFeeAtLimit = $parkTotal
  dailyCap = 40.00
  overtime = '超过 2 小时不是继续收费，是按违规停放处理（演示规则 DEMO，以现场标志为准）'
}

# ============================ case-10 courier track ============================
$courier = [pscustomobject]@{
  waybill = 'SF 1234 5678 90（演示单号）'
  now = '13:05'
  nodes = @(
    @{ t = '10-07 21:14'; s = '已揽收';     p = '深圳 · 南山' }
    @{ t = '10-08 02:30'; s = '运输中';     p = '东莞 · 转运中心' }
    @{ t = '10-08 07:52'; s = '到达';       p = '上海 · 转运中心' }
    @{ t = '10-08 11:20'; s = '派件中';     p = '静安寺营业点' }
    @{ t = '14:20–14:50'; s = '预计送达';   p = '收件地址' }
  )
  currentIndex = 3
  etaFrom = '14:20'; etaTo = '14:50'
  etaMinutes = 75
  stationDone = 43; stationTotal = 78
  callAfter = '17:00'
  callWhy = '超过预计窗 2 小时仍无更新'
  callScript = '报单号 + 预计窗 + 现在卡在哪一站，问清是今天送还是改派'
}

$calc = [pscustomobject]@{
  schema_version = 1
  task_id = 'B06'
  run_id = 'run-20261002-220723-mimo'
  timezone = 'UTC+08:00'
  data_note = '全部为演示数据 DEMO，除非另注来源；分组、金额、单号、地址、时刻均为自拟样例'
  case01 = [pscustomobject]@{ groups = $shelf; groupCount = $shelf.Count; disagreeCount = $shelfDisagree }
  case02 = $med
  case03 = [pscustomobject]@{ rows = $labRows; stat = $labStat }
  case04 = $elec
  case05 = $metro
  case06 = $install
  case07 = $deposit
  case08 = $precip
  case09 = $parking
  case10 = $courier
}

[IO.File]::WriteAllText((Join-Path $tmp 'calc-b06.json'), ($calc | ConvertTo-Json -Depth 8), $utf8)
"calc-b06.json written  " + (Get-Item (Join-Path $tmp 'calc-b06.json')).Length + " bytes"
"c01 groups=$($shelf.Count) disagree=$shelfDisagree"
"c03 normal=$($labStat.normal) recheck=$($labStat.recheck) sooner=$($labStat.sooner)"
"c04 prev=$prevCost cur=$curCost delta=$deltaCost tier3=$tier3Share% attrSum=$attrSum"
"c06 pay=$payPer total=$totalPaid fee=$totalFee nominal=$nominalPct% monthlyIRR=$([math]::Round($mr*100,4))% apr=$aprSimple% eff=$aprEff%"
"c07 fixed=$depFixed dispute=$depDisp low=$depLow high=$depHigh"
"c09 totalAtLimit=$parkTotal"