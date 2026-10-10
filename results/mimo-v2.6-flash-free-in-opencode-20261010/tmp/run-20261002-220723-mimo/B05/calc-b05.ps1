# calc-b05.ps1 -- compute every number used by B05 artwork, write calc-b05.json
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b = Join-Path $root 'tmp\run-20261002-220723-mimo\B05'
$enc = New-Object System.Text.UTF8Encoding($false)

# ---- building ----
$floors = @(6,5,4,3,2,1)
$west = 76.4; $east = 78.9
$units = @()
$att = @{
  '101'='顾虑'; '102'='已签约'; '201'='已签约'; '202'='顾虑'
  '301'='已签约'; '302'='已签约'; '401'='已签约'; '402'='已同意'
  '501'='已签约'; '502'='已同意'; '601'='已签约'; '602'='顾虑'
}
foreach ($f in 1..6) {
  $units += [ordered]@{ id = ('{0}01' -f $f); floor = $f; side = '西'; area = $west; attitude = $att[('{0}01' -f $f)] }
  $units += [ordered]@{ id = ('{0}02' -f $f); floor = $f; side = '东'; area = $east; attitude = $att[('{0}02' -f $f)] }
}
$totalArea = [math]::Round((@($units | ForEach-Object { $_.area }) | Measure-Object -Sum).Sum, 1)

# ---- cost ----
$costItems = @(
  [ordered]@{ name = '钢结构井道与玻璃幕墙'; wan = 18.6 }
  [ordered]@{ name = '土建与基础开挖';       wan = 10.2 }
  [ordered]@{ name = '曳引式电梯设备';       wan = 13.4 }
  [ordered]@{ name = '管线迁改（水/电/燃气）'; wan = 3.6 }
  [ordered]@{ name = '设计、监理与检测';     wan = 2.6 }
  [ordered]@{ name = '不可预见费';           wan = 4.4 }
)
$grossWan = [math]::Round((@($costItems | ForEach-Object { $_.wan }) | Measure-Object -Sum).Sum, 1)
$gross = $grossWan * 10000
$subsidyWan = 24.0
$net = $gross - $subsidyWan * 10000

$quotes = @(
  [ordered]@{ vendor = '甲 · 沪菱机电';  wan = 52.8; inclPipe = $true;  pipeWan = 0;   warranty = '3 年'; days = 65 }
  [ordered]@{ vendor = '乙 · 城建电梯';  wan = 55.6; inclPipe = $true;  pipeWan = 0;   warranty = '5 年'; days = 72 }
  [ordered]@{ vendor = '丙 · 恒达起重';  wan = 49.9; inclPipe = $false; pipeWan = 3.6; warranty = '2 年'; days = 58 }
)
foreach ($q in $quotes) { $q['comparableWan'] = [math]::Round($q.wan + $q.pipeWan, 1) }

# ---- allocation models ----
$wA = @{ '1' = 0.00; '2' = 0.30; '3' = 0.50; '4' = 0.70; '5' = 0.85; '6' = 1.00 }
$sumA = 0.0; foreach ($k in $wA.Keys) { $sumA += $wA[$k] * 2 }
$unitA = $net / $sumA

function ModelA($floor) { $w = $wA[[string]$floor]; if ($w -eq 0) { return 0 } ; [int][math]::Round($unitA * $w) }
$unitB = $net / $totalArea
function ModelB($area) { [int][math]::Round($unitB * $area) }

$sumC = 0.0
$wC = @{ '1' = 0.00; '2' = 0.00; '3' = 0.50; '4' = 0.70; '5' = 0.85; '6' = 1.00 }
foreach ($k in $wC.Keys) { $sumC += $wC[$k] * 2 }
$unitC = $net / $sumC
function ModelC($floor) { $w = $wC[[string]$floor]; if ($w -eq 0) { return 0 } ; [int][math]::Round($unitC * $w) }

$rows = @()
$spread = @()
foreach ($u in $units) {
  $a = ModelA $u.floor; $bb = ModelB $u.area; $c = ModelC $u.floor
  $mn = @($a,$bb,$c) | Measure-Object -Minimum
  $mx = @($a,$bb,$c) | Measure-Object -Maximum
  $rows += [ordered]@{
    id = $u.id; floor = $u.floor; side = $u.side; area = $u.area; attitude = $u.attitude
    A = $a; B = $bb; C = $c
    spread = $mx.Maximum - $mn.Minimum
    min = $mn.Minimum; max = $mx.Maximum
  }
  $spread += [ordered]@{ id = $u.id; spread = $mx.Maximum - $mn.Minimum; min = $mn.Minimum; max = $mx.Maximum }
}
# NOTE: Sort-Object does NOT order OrderedDictionary entries numerically (verified),
# so scan explicitly for the true maximum and keep every tie.
$bestVal = -1; $bestIds = @(); $bestMin = 0; $bestMax = 0
foreach ($s in $spread) {
  $v = [int]$s.spread
  if ($v -gt $bestVal) { $bestVal = $v; $bestIds = @([string]$s.id); $bestMin = [int]$s.min; $bestMax = [int]$s.max }
  elseif ($v -eq $bestVal) { $bestIds += [string]$s.id }
}
$maxSpread = [ordered]@{ id = ($bestIds -join '、'); spread = $bestVal; min = $bestMin; max = $bestMax; tied = $bestIds.Count }
$sumAdisp = (@($rows | ForEach-Object { $_.A }) | Measure-Object -Sum).Sum
$sumBdisp = (@($rows | ForEach-Object { $_.B }) | Measure-Object -Sum).Sum
$sumCdisp = (@($rows | ForEach-Object { $_.C }) | Measure-Object -Sum).Sum
$zeroCount = [ordered]@{
  A = @($rows | Where-Object { $_.A -eq 0 }).Count
  B = @($rows | Where-Object { $_.B -eq 0 }).Count
  C = @($rows | Where-Object { $_.C -eq 0 }).Count
}
$maxA = (@($rows | ForEach-Object { $_.A }) | Measure-Object -Maximum).Maximum
$maxB = (@($rows | ForEach-Object { $_.B }) | Measure-Object -Maximum).Maximum
$maxC = (@($rows | ForEach-Object { $_.C }) | Measure-Object -Maximum).Maximum

# ---- recurring / ten-year ----
$recur = @(
  [ordered]@{ name = '年度维保（演示）';     yuan = 4800 }
  [ordered]@{ name = '运行电费（演示）';     yuan = 1800 }
  [ordered]@{ name = '年检与保险（演示）';   yuan = 1200 }
  [ordered]@{ name = '大修准备金（演示）';   yuan = 6000 }
)
$perYear = (@($recur | ForEach-Object { $_.yuan }) | Measure-Object -Sum).Sum
$tenYearRun = $perYear * 10
$wholeTen = $net + $tenYearRun
$perHouseTenAvg = [math]::Round($wholeTen / 12)
$tenUnitB = $tenYearRun / $totalArea

$six = @($rows | Where-Object { $_.id -eq '602' })[0]
$ten602 = [ordered]@{
  A = $six.A + [int][math]::Round($tenYearRun / $sumA * $wA['6'])
  B = $six.B + [int][math]::Round($tenUnitB * $east)
  C = $six.C + [int][math]::Round($tenYearRun / $sumC * $wC['6'])
}
$ten602Spread = (@($ten602.Values) | Measure-Object -Maximum).Maximum - (@($ten602.Values) | Measure-Object -Minimum).Minimum

# ---- survey / schedule ----
$signed = @($units | Where-Object { $_.attitude -eq '已签约' }).Count
$agreed = @($units | Where-Object { $_.attitude -eq '已同意' }).Count
$concern = @($units | Where-Object { $_.attitude -eq '顾虑' }).Count
$support = $signed + $agreed

$milestones = @(
  [ordered]@{ name = '基础开挖与垫层';     days = 10 }
  [ordered]@{ name = '主体钢结构吊装';     days = 10 }
  [ordered]@{ name = '井道与玻璃幕墙';     days = 14 }
  [ordered]@{ name = '电梯安装与调试';     days = 15 }
  [ordered]@{ name = '管线复接与路面恢复'; days = 8 }
  [ordered]@{ name = '验收整改与交付';     days = 8 }
)
$totalDays = (@($milestones | ForEach-Object { $_.days }) | Measure-Object -Sum).Sum
$dayIn = 28
$acc = 0; $curIdx = -1; $curDay = 0
for ($i = 0; $i -lt $milestones.Count; $i++) {
  if ($dayIn -le ($acc + $milestones[$i].days)) { $curIdx = $i; $curDay = $dayIn - $acc; break }
  $acc += $milestones[$i].days
}
$progress = [math]::Round(100.0 * $dayIn / $totalDays, 1)
for ($i = 0; $i -lt $milestones.Count; $i++) {
  $startD = 1; for ($k = 0; $k -lt $i; $k++) { $startD += $milestones[$k].days }
  $milestones[$i]['startDay'] = $startD
  $milestones[$i]['endDay'] = $startD + $milestones[$i].days - 1
  $milestones[$i]['state'] = if ($i -lt $curIdx) { '已完成' } elseif ($i -eq $curIdx) { '进行中' } else { '未开始' }
}

# ---- payment plan for 602 (model A) ----
$pay602 = $six.A
$pay = @(
  [ordered]@{ node = '签约后 5 日内'; pct = 30; yuan = [int][math]::Round($pay602 * 0.30) }
  [ordered]@{ node = '主体结构封顶';   pct = 40; yuan = [int][math]::Round($pay602 * 0.40) }
  [ordered]@{ node = '验收合格后';     pct = 30; yuan = 0 }
)
$pay[2].yuan = $pay602 - $pay[0].yuan - $pay[1].yuan

# ---- acceptance checklist ----
$checks = @(
  [ordered]@{ item = '井道垂直度检测';           state = '合格'; note = '2026-12-18 实测最大偏差 2 mm' }
  [ordered]@{ item = '钢结构焊缝探伤';           state = '合格'; note = '2026-12-18 一级焊缝 100% 检测' }
  [ordered]@{ item = '幕墙气密与水密试验';       state = '合格'; note = '2026-12-18 三性试验通过' }
  [ordered]@{ item = '电梯监督检验合格证';       state = '待检'; note = '已预约 2026-12-19 特检院到场' }
  [ordered]@{ item = '层门装置与门锁啮合';       state = '合格'; note = '2026-12-19 12 层门全部复测' }
  [ordered]@{ item = '限速器与安全钳联动';       state = '合格'; note = '2026-12-19 模拟超速动作正常' }
  [ordered]@{ item = '应急通话与轿厢对讲';       state = '合格'; note = '2026-12-19 通话音量 68 dB' }
  [ordered]@{ item = '停电自动平层与备用电源';   state = '合格'; note = '2026-12-19 断电 3 次均自动平层' }
  [ordered]@{ item = '语音报站与盲文按钮';       state = '合格'; note = '2026-12-18 语音与盲文同步' }
  [ordered]@{ item = '轿厢扶手与后视镜';         state = '合格'; note = '2026-12-18 双侧扶手 850 mm' }
  [ordered]@{ item = '单元门口高差与坡道';       state = '整改'; note = '实测高差 35 mm，要求 ≤15 mm，需返工' }
  [ordered]@{ item = '消防与疏散确认';           state = '合格'; note = '2026-12-19 与物业联测通过' }
)
$checkOk = @($checks | Where-Object { $_.state -eq '合格' }).Count
$checkBad = @($checks | Where-Object { $_.state -ne '合格' })

$calc = [ordered]@{
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  unit        = '元 unless noted'
  building    = [ordered]@{
    name = '梧桐里小区 3 号楼'; unitPerFloor = 2; floors = 6; households = 12
    westArea = $west; eastArea = $east; totalArea = $totalArea
  }
  attitudes   = [ordered]@{ signed = $signed; agreed = $agreed; concern = $concern; support = $support; supportPct = [math]::Round(100.0*$support/12,1); concernIds = @('101','202','602') }
  cost        = [ordered]@{ items = $costItems; grossWan = $grossWan; gross = $gross; subsidyWan = $subsidyWan; net = $net; quotes = $quotes }
  models      = [ordered]@{
    A = [ordered]@{ label='按楼层递增（1F 不出钱）'; weights = $wA; weightSum = [math]::Round($sumA, 2); unitWeight = [math]::Round($unitA,2); perFloor = [ordered]@{ '1'=0; '2'=(ModelA 2); '3'=(ModelA 3); '4'=(ModelA 4); '5'=(ModelA 5); '6'=(ModelA 6) }; displaySum = $sumAdisp; zeroHouseholds = $zeroCount.A; maxHousehold = $maxA }
    B = [ordered]@{ label='按建筑面积均摊'; perSqm = [math]::Round($unitB,2); west = (ModelB $west); east = (ModelB $east); displaySum = $sumBdisp; zeroHouseholds = $zeroCount.B; maxHousehold = $maxB }
    C = [ordered]@{ label='低层免摊（1F、2F 都不出）'; weights = $wC; weightSum = [math]::Round($sumC, 2); unitWeight = [math]::Round($unitC,2); perFloor = [ordered]@{ '1'=0; '2'=0; '3'=(ModelC 3); '4'=(ModelC 4); '5'=(ModelC 5); '6'=(ModelC 6) }; displaySum = $sumCdisp; zeroHouseholds = $zeroCount.C; maxHousehold = $maxC }
    maxSpread = $maxSpread.spread; maxSpreadHousehold = $maxSpread.id; maxSpreadMin = $maxSpread.min; maxSpreadMax = $maxSpread.max
    roundingNote = '分项四舍五入到元，合计以 288000 元为准（可能相差 2 元）'
  }
  households   = $rows
  recurring   = [ordered]@{ items = $recur; perYear = $perYear; tenYear = $tenYearRun; wholeTenYear = $wholeTen; perHouseholdTenYearAvg = $perHouseTenAvg }
  tenYear602  = [ordered]@{ A = $ten602.A; B = $ten602.B; C = $ten602.C; spread = $ten602Spread; monthlyA = [int][math]::Round($ten602.A/10/12) }
  schedule    = [ordered]@{ milestones = $milestones; totalDays = $totalDays; dayIn = $dayIn; progressPct = $progress; current = $milestones[$curIdx].name; currentDayInPhase = $curDay }
  payment602  = [ordered]@{ household = '602'; model = 'A'; total = $pay602; nodes = $pay }
  acceptance  = [ordered]@{ items = $checks; ok = $checkOk; pending = @($checkBad).Count; pendingItems = $checkBad }
}

$json = $calc | ConvertTo-Json -Depth 9
[IO.File]::WriteAllText((Join-Path $b 'calc-b05.json'), $json, $enc)

"  calc-b05.json written ({0} B)" -f (Get-Item (Join-Path $b 'calc-b05.json')).Length
"  gross={0} wan  net={1}  totalArea={2}  households={3}" -f $grossWan, $net, $totalArea, $units.Count
"  attitudes signed={0} agreed={1} concern={2} support={3}/12" -f $signed, $agreed, $concern, $support
"  modelA perFloor = {0}" -f (($calc.models.A.perFloor.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ')
"  modelB west/east = {0}/{1}" -f $calc.models.B.west, $calc.models.B.east
"  modelC perFloor = {0}" -f (($calc.models.C.perFloor.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' ')
"  sums A={0} B={1} C={2} (target {3})" -f $sumAdisp, $sumBdisp, $sumCdisp, $net
"  maxSpread = {0} at {1}  ({2} .. {3})" -f $maxSpread.spread, $maxSpread.id, $maxSpread.min, $maxSpread.max
"  zero-households A/B/C = {0}/{1}/{2}" -f $zeroCount.A, $zeroCount.B, $zeroCount.C
"  schedule total={0} d  day {1} = {2} ({3} d in phase)  progress={4}%" -f $totalDays, $dayIn, $calc.schedule.current, $curDay, $progress
"  pay602 total={0}  nodes = {1}" -f $pay602, (($pay | ForEach-Object { $_.yuan }) -join '+')
"  tenYear whole={0}  602 A/B/C = {1}/{2}/{3} spread {4}" -f $wholeTen, $ten602.A, $ten602.B, $ten602.C, $ten602Spread
"  acceptance ok={0} pending={1}" -f $checkOk, $calc.acceptance.pending
"  quotes comparable = {0}" -f (($quotes | ForEach-Object { "$($_.vendor)$($_.comparableWan)w" }) -join ' / ')
