# gen-a22.ps1 - A22 真实数据更正与局部回归 三轮 dashboard 的 DSL / computed-data / layout-map / change-audit 生成器
# 用法: -Round 1|2|3 -OutDir <round dir> -MapPath <layout-map.json>
# 主体全部由 DSL 构造，不使用 <Image>，不嵌入外部图片，不做任何位图后处理。
param(
  [Parameter(Mandatory = $true)][ValidateSet(1, 2, 3)][int]$Round,
  [Parameter(Mandatory = $true)][string]$OutDir,
  [Parameter(Mandatory = $true)][string]$MapPath
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

# --------------------------------------------------------------------- helpers --
function N([double]$v) {
  if ([double]::IsNaN($v)) { return '0' }
  if ($v -eq [Math]::Truncate($v)) { return ([long]$v).ToString([cultureinfo]::InvariantCulture) }
  return $v.ToString('0.##', [cultureinfo]::InvariantCulture)
}
function Esc([string]$s) { return $s.Replace('&', '&amp;').Replace('<', '&lt;').Replace('>', '&gt;') }

function EstW([string]$s, [double]$fs) {
  $w = 0.0
  foreach ($ch in $s.ToCharArray()) {
    $c = [int]$ch
    if ($c -gt 0x2E7F)      { $w += $fs * 1.00 }
    elseif ($c -eq 0x00B7)  { $w += $fs * 0.35 }
    elseif ($c -eq 0x20)    { $w += $fs * 0.28 }
    elseif ($c -ge 0x30 -and $c -le 0x39) { $w += $fs * 0.58 }
    elseif ($c -ge 0x41 -and $c -le 0x5A) { $w += $fs * 0.68 }
    elseif ($c -ge 0x61 -and $c -le 0x7A) { $w += $fs * 0.54 }
    else { $w += $fs * 0.40 }
  }
  return [Math]::Ceiling($w)
}
function FmtInt([long]$v) { return $v.ToString('N0', [cultureinfo]::InvariantCulture) }
function FmtPct([double]$v) { return ($v * 100).ToString('0.00', [cultureinfo]::InvariantCulture) + '%' }

# ================================================================ 1. DATA =======
$PAGE = 'EDEFF7'; $PANEL = 'FFFFFF'
$INK = '10142E'; $INK2 = '3A3F63'; $MUTED = '5B6180'
$NET = '5B4FE8'      # 净收入柱 - 主色，三轮不变
$PRF = 'FFB020'      # 利润柱   - 琥珀，三轮不变（含负值柱，颜色不随轮次改）
$NEG = 'DC2626'      # 仅用于负利润的数值/标注文字
$GRID = 'E4E7F3'; $BASE = 'A8ADC9'; $STRIP = 'EEF0FA'; $SEP = 'ECEDF6'
$FAM_CJK  = 'Noto Sans CJK SC'
$FAM_MIX  = 'Inter,Noto Sans CJK SC'

# raw inputs/monthly.csv, untouched
$SRC = @(
  @{ m = '2026-04'; o = 420; g = 126000; r = 6300;   c = 82000;  s = 3500 },
  @{ m = '2026-05'; o = 460; g = 142600; r = 7130;   c = 93500;  s = 4100 },
  @{ m = '2026-06'; o = 445; g = 137950; r = 11036;  c = 99000;  s = 4200 },
  @{ m = '2026-07'; o = 530; g = 169600; r = 8480;   c = 112000; s = 4700 },
  @{ m = '2026-08'; o = 570; g = 188100; r = 15048;  c = 132000; s = 5200 },
  @{ m = '2026-09'; o = 620; g = 210800; r = 8432;   c = 138000; s = 5600 }
)
# round-03 appends 2026-10 from rounds/round-03.md
$ROW10 = @{ m = '2026-10'; o = 640; g = 224000; r = 11200; c = 142000; s = 5900 }

# NOTE: loop variable is $sr, never $src - PowerShell variables are case-insensitive, so
# `foreach ($src in $SRC)` would overwrite the $SRC collection itself on the first pass and
# break the second Compute() call (round-02/03 comparison against the previous round).
function Compute([int]$rnd) {
  $rows = New-Object System.Collections.Generic.List[object]
  foreach ($sr in $SRC) {
    $rr = $sr.r; $cc = $sr.c
    if ($rnd -ge 2) {
      if ($sr.m -eq '2026-08') { $rr = 25048 }   # rounds/round-02.md correction
      if ($sr.m -eq '2026-09') { $cc = 208000 }  # rounds/round-02.md correction
    }
    $nrev = $sr.g - $rr
    $rows.Add([pscustomobject][ordered]@{
      month = $sr.m; orders = $sr.o; gross_revenue = $sr.g
      refund_amount = $rr; operating_cost = $cc; sessions = $sr.s
      net_revenue = $nrev; profit = ($nrev - $cc)
      refund_rate = [Math]::Round($rr / $sr.g, 6)
      conversion_rate = [Math]::Round($sr.o / $sr.s, 6)
      csv_refund_amount = $sr.r; csv_operating_cost = $sr.c
      corrected = ($rnd -ge 2 -and ($sr.m -eq '2026-08' -or $sr.m -eq '2026-09'))
    })
  }
  if ($rnd -ge 3) {
    $add = $ROW10
    $nrev = $add.g - $add.r
    $rows.Add([pscustomobject][ordered]@{
      month = $add.m; orders = $add.o; gross_revenue = $add.g
      refund_amount = $add.r; operating_cost = $add.c; sessions = $add.s
      net_revenue = $nrev; profit = ($nrev - $add.c)
      refund_rate = [Math]::Round($add.r / $add.g, 6)
      conversion_rate = [Math]::Round($add.o / $add.s, 6)
      csv_refund_amount = $add.r; csv_operating_cost = $add.c
      corrected = $false
    })
  }
  $tOrders = 0; $tGross = 0; $tRefund = 0; $tCost = 0; $tSess = 0; $tNet = 0; $tProfit = 0
  foreach ($x in $rows) {
    $tOrders += $x.orders; $tGross += $x.gross_revenue; $tRefund += $x.refund_amount
    $tCost += $x.operating_cost; $tSess += $x.sessions; $tNet += $x.net_revenue; $tProfit += $x.profit
  }
  $totals = [pscustomobject][ordered]@{
    months = $rows.Count
    orders = $tOrders; gross_revenue = $tGross; refund_amount = $tRefund
    operating_cost = $tCost; sessions = $tSess
    net_revenue = $tNet; profit = $tProfit
    refund_rate = [Math]::Round($tRefund / $tGross, 6)
    overall_conversion_rate = [Math]::Round($tOrders / $tSess, 6)
  }
  return @{ rows = $rows; totals = $totals }
}

$CUR = Compute $Round
$ROWS = $CUR.rows
$T = $CUR.totals
$PREV = $null
if ($Round -ge 2) { $PREV = Compute ($Round - 1) }

$n = $ROWS.Count
$netVals = @($ROWS | ForEach-Object { [double]$_.net_revenue })
$prfVals = @($ROWS | ForEach-Object { [double]$_.profit })
$maxV = ($netVals + $prfVals | Measure-Object -Maximum).Maximum
$minV = ($netVals + $prfVals | Measure-Object -Minimum).Minimum

# nice zero-based shared axis; round-02/03 add a negative range because 2026-09 profit is negative
$YMIN = 0.0; $YMAX = 250000.0; $YSTEP = 50000.0
if ($minV -lt 0) { $YMIN = -50000.0 }
if ($minV -lt $YMIN -or $maxV -gt $YMAX) { throw "axis does not cover data: min=$minV max=$maxV range=$YMIN..$YMAX" }

$MONTH_FIRST = $ROWS[0].month
$MONTH_LAST  = $ROWS[$n - 1].month

# ================================================================ 2. GEOMETRY ===
# All region bounds are identical in all three rounds (round-02/03 spec keeps them within +/-2px).
$TITLE  = @{ x = 40;  y = 34;  w = 1520; h = 100 }
$KPIR   = @{ x = 40;  y = 146; w = 1520; h = 160 }
$CHART  = @{ x = 40;  y = 316; w = 900;  h = 410 }
$TABLE  = @{ x = 960; y = 316; w = 600;  h = 410 }
$CONC   = @{ x = 40;  y = 746; w = 1520; h = 218 }
$KPI_W = 365.0; $KPI_GAP = 20.0
$KPI_X = @(40.0, 425.0, 810.0, 1195.0)

$PX0 = 160.0; $PX1 = 910.0; $PY0 = 396.0; $PY1 = 666.0
$PW = $PX1 - $PX0; $PH = $PY1 - $PY0
$GW = $PW / $n
$BAR_PAD = 0.10 * $GW; $BAR_GAP = 0.06 * $GW
$BARW = ($PW - (2 * $BAR_PAD * $n) - ($BAR_GAP * $n)) / (2 * $n)
$BARW = [Math]::Floor($BARW * 100) / 100

$TBL_IN_X = 976.0; $TBL_IN_W = 568.0
$COLS = @(
  @{ name = '月份';   x = 986.0;  w = 110.0; align = 'LEFT';  val = 'month'          },
  @{ name = '净收入'; x = 1096.0; w = 126.0; align = 'RIGHT'; val = 'net_revenue'    },
  @{ name = '利润';   x = 1222.0; w = 118.0; align = 'RIGHT'; val = 'profit'         },
  @{ name = '退款率'; x = 1340.0; w = 92.0;  align = 'RIGHT'; val = 'refund_rate'    },
  @{ name = '转化率'; x = 1432.0; w = 102.0; align = 'RIGHT'; val = 'conversion_rate' }
)
$HDR_Y = 378.0; $HDR_H = 34.0
$ROW_Y = 414.0; $ROW_H = 44.0

$KPI_DEFS = @(
  @{ label = '总净收入';    value = (FmtInt $T.net_revenue); sub = '收入 - 退款' },
  @{ label = '总经营利润';  value = (FmtInt $T.profit);      sub = '净收入 - operating_cost' },
  @{ label = '总订单';      value = (FmtInt $T.orders);      sub = ('{0} 个月合计' -f $n) },
  @{ label = '总体转化率';  value = (FmtPct $T.overall_conversion_rate); sub = '总订单 / 总 sessions' }
)

function Y([double]$v) { return [Math]::Round($PY0 + (($YMAX - $v) / ($YMAX - $YMIN)) * $PH, 2) }

# ---------------------------------------------------------- headline conclusion --
$FORMULAS = '净收入 = 收入 - 退款 ｜ 利润 = 净收入 - operating_cost ｜ 总体转化率 = 总订单 / 总 sessions ｜ 数据来源 inputs/monthly.csv'
if ($Round -eq 1) {
  $TITLE_TXT  = '经营驾驶舱 · ' + $MONTH_FIRST + ' – ' + $MONTH_LAST
  $SUBTITLE   = $FORMULAS
  $BADGE      = ('{0} 个月 · 原始数据' -f $n)
  $CONCLUSION = ('{0} 至 {1} 六个月总净收入 {2}、总经营利润 {3}、总订单 {4}，净收入自 {5} 升至 {6}（+69.1%），' +
                 '{7} 净收入与利润（{8}）均为最高、{9} 利润（{10}）最低；总体转化率 = {11} / {12} = {13}，' +
                 '月度区间 {14}（{15}）- {16}（{17}）。') -f `
    $MONTH_FIRST, $MONTH_LAST, (FmtInt $T.net_revenue), (FmtInt $T.profit), (FmtInt $T.orders),
    (FmtInt $ROWS[0].net_revenue), (FmtInt $ROWS[$n - 1].net_revenue), $MONTH_LAST,
    (FmtInt $ROWS[$n - 1].profit), '2026-06', (FmtInt $ROWS[2].profit),
    (FmtInt $T.orders), (FmtInt $T.sessions), (FmtPct $T.overall_conversion_rate),
    (FmtPct $ROWS[2].conversion_rate), '2026-06', (FmtPct $ROWS[0].conversion_rate), '2026-04'
} elseif ($Round -eq 2) {
  $TITLE_TXT  = '经营驾驶舱 · ' + $MONTH_FIRST + ' – ' + $MONTH_LAST
  $SUBTITLE   = $FORMULAS
  $BADGE      = ('{0} 个月 · 财务更正后' -f $n)
  $CONCLUSION = ('更正后六个月总净收入 {0}、总经营利润 {1}（较更正前少 {2}）：2026-08 refund_amount 15,048 改为 25,048，' +
                 '该月退款率由 8.00% 升至 {3}（六个月最高）；2026-09 operating_cost 138,000 改为 208,000，' +
                 '该月利润由 64,368 转为 {4}，是唯一负值。总订单 {5} 与总 sessions {6} 未变，' +
                 '总体转化率仍 = {5} / {6} = {7}。') -f `
    (FmtInt $T.net_revenue), (FmtInt $T.profit), (FmtInt 80000),
    (FmtPct $ROWS[4].refund_rate), (FmtInt $ROWS[5].profit),
    (FmtInt $T.orders), (FmtInt $T.sessions), (FmtPct $T.overall_conversion_rate)
} else {
  $TITLE_TXT  = '经营驾驶舱 · ' + $MONTH_FIRST + ' – ' + $MONTH_LAST
  $SUBTITLE   = $FORMULAS
  $BADGE      = ('{0} 个月 · 含新增与更正' -f $n)
  $CONCLUSION = ('七个月总净收入 {0}、总经营利润 {1}、总订单 {2}；新增 2026-10 净收入 {3}、利润 {4}，两项均为七个月最高；' +
                 '2026-09 仍是唯一负利润（{5}），2026-08 退款率 {6} 仍为最高。' +
                 '总体转化率 = {2} / {7} = {8}，低于 2026-04 的 {9}，2026-06 的 {10} 仍是月度最低。') -f `
    (FmtInt $T.net_revenue), (FmtInt $T.profit), (FmtInt $T.orders),
    (FmtInt $ROWS[6].net_revenue), (FmtInt $ROWS[6].profit), (FmtInt $ROWS[5].profit),
    (FmtPct $ROWS[4].refund_rate), (FmtInt $T.sessions),
    (FmtPct $T.overall_conversion_rate), (FmtPct $ROWS[0].conversion_rate), (FmtPct $ROWS[2].conversion_rate)
}

# ================================================================ 3. EMITTERS ===
$DSL = New-Object System.Collections.Generic.List[string]
$BLOCK = New-Object System.Collections.Generic.List[object]

function AddRect($x, $y, $w, $h, $color, $radius) {
  $a = New-Object System.Collections.Generic.List[string]
  $a.Add('width="' + (N $w) + '"'); $a.Add('height="' + (N $h) + '"'); $a.Add('color="#' + $color + '"')
  if ($radius -gt 0) { $a.Add('borderRadius="' + (N $radius) + '"') }
  $DSL.Add('<Positioned left="' + (N $x) + '" top="' + (N $y) + '" width="' + (N $w) + '" height="' + (N $h) +
           '"><Container ' + ($a -join ' ') + '/></Positioned>')
}

function AddText($key, $x, $y, $w, $h, $fs, $color, $txt, $bold, $family, $align, $maxLines,
                 [string[]]$bgLayers, $bgName, $probeMinX, $probeX) {
  $a = New-Object System.Collections.Generic.List[string]
  $a.Add('fontSize="' + (N $fs) + '"')
  $a.Add('fontFamily="' + $family + '"')
  $a.Add('color="#' + $color + '"')
  if ($bold)           { $a.Add('fontStyle="BOLD"') }
  if ($align)          { $a.Add('textAlign="' + $align + '"') }
  if ($maxLines -gt 0) { $a.Add('maxLines="' + $maxLines + '"') }
  $DSL.Add('<Positioned left="' + (N $x) + '" top="' + (N $y) + '" width="' + (N $w) + '" height="' + (N $h) +
           '"><Text ' + ($a -join ' ') + '>' + (Esc $txt) + '</Text></Positioned>')

  $px = [Math]::Round($x - 6, 2)
  if ($null -ne $probeX) { $px = $probeX }
  $BLOCK.Add([pscustomobject][ordered]@{
    key = $key; round = $Round; kind = 'text'
    text = $txt; fontSize = $fs; bold = [bool]$bold; color = ('#' + $color); family = $family
    x = $x; y = $y; w = $w; h = $h
    align = $align
    probe = [pscustomobject]@{ x = $px; y = [Math]::Round($y + $h / 2, 1) }
    probe_min_x = $probeMinX
    background_name = $bgName
    background_layers_bottom_up = $bgLayers
    expected_background = $bgLayers[0]
  })
}

# ================================================================= 4. BUILD =====
$problems = New-Object System.Collections.Generic.List[string]

# ---- title region -------------------------------------------------------------
$BADGE_W = [Math]::Ceiling((EstW $BADGE 24) * 1.10) + 40
$BADGE_X = 1560 - $BADGE_W
AddText 'title'   $TITLE.x $TITLE.y 1200 62 42 $INK $TITLE_TXT $true $FAM_CJK 'LEFT' 1 @($PAGE) 'page' 0
AddRect $BADGE_X 44 $BADGE_W 42 $NET 12
AddText 'title-badge' ($BADGE_X + 20) 48 ($BADGE_W - 40) 34 24 $PANEL $BADGE $true $FAM_CJK 'CENTER' 1 @($NET) 'primary-chip' $BADGE_X ($BADGE_X + 6)
AddText 'subtitle' $TITLE.x 98 1520 36 24 $MUTED $SUBTITLE $false $FAM_MIX 'LEFT' 1 @($PAGE) 'page' 0

# ---- KPI row ------------------------------------------------------------------
for ($i = 0; $i -lt 4; $i++) {
  $kx = $KPI_X[$i]; $kd = $KPI_DEFS[$i]
  AddRect $kx $KPIR.y $KPI_W $KPIR.h $PANEL 16
  AddRect ($kx + 24) 158 56 4 $NET 2
  AddText "kpi$($i + 1)-label" ($kx + 24) 170 317 35 24 $MUTED $kd.label $false $FAM_CJK 'LEFT' 1 @($PANEL) 'panel' $kx
  AddText "kpi$($i + 1)-value" ($kx + 24) 207 317 64 44 $INK $kd.value $true $FAM_MIX 'LEFT' 1 @($PANEL) 'panel' $kx
  AddText "kpi$($i + 1)-sub"   ($kx + 24) 273 317 28 22 $MUTED $kd.sub $false $FAM_CJK 'LEFT' 1 @($PANEL) 'panel' $kx
  $subEnd = 273 + 28
  if ($subEnd -gt ($KPIR.y + $KPIR.h)) { $problems.Add(('kpi {0} sub text overflows the card: {1} > {2}' -f ($i + 1), $subEnd, ($KPIR.y + $KPIR.h))) }
}

# ---- chart panel --------------------------------------------------------------
AddRect $CHART.x $CHART.y $CHART.w $CHART.h $PANEL 20
AddText 'chart-title' 64 334 470 38 26 $INK '净收入 / 利润（共用零起点柱图）' $true $FAM_CJK 'LEFT' 1 @($PANEL) 'panel' $CHART.x
AddRect 650 346 26 18 $NET 3
AddText 'legend-net' 690 338 90 34 22 $INK2 '净收入' $false $FAM_CJK 'LEFT' 1 @($PANEL) 'panel' $CHART.x 684
AddRect 790 346 26 18 $PRF 3
AddText 'legend-profit' 830 338 74 34 22 $INK2 '利润' $false $FAM_CJK 'LEFT' 1 @($PANEL) 'panel' $CHART.x 824

# gridlines + y axis labels
$tv = $YMIN
while ($tv -le ($YMAX + 0.5)) {
  $gy = Y $tv
  $isZero = ([Math]::Abs($tv) -lt 0.5)
  AddRect $PX0 $gy $PW $(if ($isZero) { 2 } else { 1 }) $(if ($isZero) { $BASE } else { $GRID }) 0
  AddText ('ygrid-' + (N $tv)) 56 ($gy - 16) 96 32 22 $MUTED (FmtInt $tv) $false $FAM_MIX 'RIGHT' 1 @($PANEL) 'panel' $CHART.x 50
  $tv += $YSTEP
}

# bars + x labels
$negCallout = $null
for ($i = 0; $i -lt $n; $i++) {
  $gx = $PX0 + ($i * $GW)
  $netX = $gx + $BAR_PAD
  $prfX = $netX + $BARW + $BAR_GAP
  $row = $ROWS[$i]
  $z = Y 0

  # net revenue bar (always >= 0 here)
  $ny = Y $row.net_revenue
  AddRect $netX $ny $BARW ([Math]::Round($z - $ny, 2)) $NET 4

  # profit bar - drawn from the shared zero line; negative goes BELOW zero
  $py = Y $row.profit
  if ($row.profit -ge 0) {
    AddRect $prfX $py $BARW ([Math]::Round($z - $py, 2)) $PRF 4
  } else {
    AddRect $prfX $z $BARW ([Math]::Round($py - $z, 2)) $PRF 4
    $negCallout = @{ v = $row.profit; month = $row.month; cx = ($prfX + ($BARW / 2)) }
  }

  $cx = $gx + ($GW / 2)
  AddText ('xlabel-' + $row.month) ([Math]::Round($cx - 55, 2)) 676 110 32 22 $INK2 $row.month $false $FAM_MIX 'CENTER' 1 @($PANEL) 'panel' $CHART.x ([Math]::Round($cx - 61, 2))
}

if ($null -ne $negCallout) {
  $cwx = [Math]::Round($PX1 - 230, 2)
  AddText 'neg-callout' $cwx 632 230 32 22 $NEG ('{0} 利润 {1}（唯一负值）' -f $negCallout.month, (FmtInt $negCallout.v)) $true $FAM_MIX 'RIGHT' 1 @($PANEL) 'panel' $CHART.x ($cwx - 6)
}

# ---- table panel --------------------------------------------------------------
AddRect $TABLE.x $TABLE.y $TABLE.w $TABLE.h $PANEL 20
AddText 'table-title' 976 334 400 38 26 $INK '月度明细' $true $FAM_CJK 'LEFT' 1 @($PANEL) 'panel' $TABLE.x
AddRect $TBL_IN_X $HDR_Y $TBL_IN_W $HDR_H $STRIP 8
foreach ($c in $COLS) {
  $tx = $c.x; $tw = $c.w
  # sample 6px away from the glyphs: left of the box for LEFT-aligned text,
  # 6px inside the box for RIGHT-aligned text (text ends at the box's right edge).
  $px = $(if ($c.align -eq 'RIGHT') { $tx + 6 } else { $tx - 6 })
  if ($px -lt $TBL_IN_X) { $px = $TBL_IN_X }
  AddText ('th-' + $c.name) $tx 381 $tw 28 22 $INK2 $c.name $true $FAM_CJK $c.align 1 @($STRIP) 'table-header-strip' 976 $px
}
for ($i = 0; $i -lt $n; $i++) {
  $row = $ROWS[$i]
  $ry = $ROW_Y + ($i * $ROW_H)
  if ($ry + $ROW_H -gt 726) { $problems.Add(('table row {0} overflows the table panel (ends at {1})' -f $row.month, ($ry + $ROW_H))) }
  AddRect $TBL_IN_X ($ry + $ROW_H - 1) $TBL_IN_W 1 $SEP 0
  $cellBg = @($PANEL)
  foreach ($c in $COLS) {
    $col = $INK
    $val = ''
    switch ($c.val) {
      'month'          { $val = $row.month }
      'net_revenue'    { $val = (FmtInt $row.net_revenue) }
      'profit'         { $val = (FmtInt $row.profit); if ($row.profit -lt 0) { $col = $NEG } }
      'refund_rate'    { $val = (FmtPct $row.refund_rate); $col = $MUTED }
      'conversion_rate'{ $val = (FmtPct $row.conversion_rate); $col = $MUTED }
    }
    $px = $(if ($c.align -eq 'RIGHT') { $c.x + 6 } else { $c.x - 6 })
    AddText ('td-' + $row.month + '-' + $c.name) $c.x ($ry + 6) $c.w 32 22 $col $val ($c.val -eq 'month') $FAM_MIX $c.align 1 $cellBg 'panel' $TABLE.x $px
  }
}

# ---- conclusion panel ---------------------------------------------------------
AddRect $CONC.x $CONC.y $CONC.w $CONC.h $PANEL 20
AddText 'conclusion-title' 64 766 300 38 26 $INK '主结论' $true $FAM_CJK 'LEFT' 1 @($PANEL) 'panel' $CONC.x
AddText 'conclusion-body' 64 810 1472 140 24 $INK2 $CONCLUSION $false $FAM_CJK 'LEFT' 4 @($PANEL) 'panel' $CONC.x

# ================================================================ 5. ASSERT =====
$BODY_LINES = [Math]::Ceiling((EstW $CONCLUSION 24) / 1472.0)
if (($BODY_LINES + 1) -gt 4) { $problems.Add(('conclusion needs about {0} lines, box allows 4' -f $BODY_LINES)) }
foreach ($b in $BLOCK) {
  if ($b.fontSize -lt 22) { $problems.Add(('{0}: fontSize {1} < 22' -f $b.key, $b.fontSize)) }
}
foreach ($d in @($DSL -join '')) {
  if ($d -match '<Image') { $problems.Add('DSL contains <Image - forbidden') }
  if ($d -match 'transform') { $problems.Add('DSL contains transform - forbidden') }
}
if ($n -ne $ROWS.Count) { $problems.Add('month count mismatch') }
if ($MONTH_LAST -ne ($ROWS[$n - 1].month)) { $problems.Add('last month is not the newest row') }
if ($Round -eq 3 -and $MONTH_LAST -ne '2026-10') { $problems.Add('round-03 last month must be 2026-10') }
if ($Round -lt 3 -and $MONTH_LAST -ne '2026-09') { $problems.Add('round-01/02 last month must be 2026-09') }
foreach ($mm in @('2026-04','2026-05','2026-06','2026-07','2026-08','2026-09')) {
  if (-not ($ROWS | Where-Object { $_.month -eq $mm })) { $problems.Add(('month {0} is missing' -f $mm)) }
}
if ($Round -eq 1 -and $YMIN -ne 0) { $problems.Add('round-01 must be zero-based (no negative data exists)') }
if ($minV -lt 0 -and $YMIN -ge 0) { $problems.Add('negative profit exists but the axis has no negative range') }
# bar geometry must equal the value it claims
$barMaxErr = 0.0
for ($i = 0; $i -lt $n; $i++) {
  $row = $ROWS[$i]
  $want = [Math]::Abs($row.profit) / ($YMAX - $YMIN) * $PH
  $gx = $PX0 + ($i * $GW); $prfX = $gx + $BAR_PAD + $BARW + $BAR_GAP
  if ($row.profit -lt 0) { $h = (Y $row.profit) - (Y 0) } else { $h = (Y 0) - (Y $row.profit) }
  $err = [Math]::Abs($h - $want)
  if ($err -gt $barMaxErr) { $barMaxErr = $err }
  if ($row.profit -lt 0) {
    $pz = Y 0; $py = Y $row.profit
    if ($py -le $pz) { $problems.Add(('{0}: negative profit bar is not below the zero line' -f $row.month)) }
  }
}
if ($barMaxErr -gt 0.05) { $problems.Add(('bar height deviates from value by up to {0}px' -f $barMaxErr)) }

# ================================================================ 6. OUTPUT =====
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $MapPath -Parent) | Out-Null
$utf8 = New-Object System.Text.UTF8Encoding($false)

$dsl = '<Snapshot type="png" background="#' + $PAGE + '"><Container width="1600" height="1000" color="#' + $PAGE +
       '"><Stack>' + ($DSL -join '') + '</Stack></Container></Snapshot>'
[IO.File]::WriteAllText((Join-Path $OutDir 'dashboard.snapshot'), $dsl, $utf8)

$computed = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/a22-computed-data/v1'
  task = 'A22'; round = $Round; generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone = 'UTC+08:00'
  source = 'inputs/monthly.csv (unmodified - 任务输入不改写)'
  formulas = [pscustomobject]@{
    net_revenue = 'gross_revenue - refund_amount'
    profit = 'net_revenue - operating_cost'
    refund_rate = 'refund_amount / gross_revenue'
    conversion_rate = 'orders / sessions'
    overall_conversion_rate = 'total_orders / total_sessions'
  }
  corrections_applied = $(if ($Round -ge 2) {
    @(
      [pscustomobject]@{ month = '2026-08'; field = 'refund_amount'; old = 15048; new = 25048; delta = 10000 },
      [pscustomobject]@{ month = '2026-09'; field = 'operating_cost'; old = 138000; new = 208000; delta = 70000 }
    ) } else { @() })
  rows_added = $(if ($Round -ge 3) { @([pscustomobject]$ROW10) } else { @() })
  month_count = $n
  months = @($ROWS | ForEach-Object { $_.month })
  last_month = $MONTH_LAST
  rows = $ROWS
  totals = $T
  previous_round_totals = $(if ($null -ne $PREV) { $PREV.totals } else { $null })
  kpis = $KPI_DEFS
  axis = [pscustomobject]@{
    type = 'shared zero-based grouped bars'; unit = 'currency'
    ymin = $YMIN; ymax = $YMAX; step = $YSTEP
    zero_line_y = (Y 0); plot = [pscustomobject]@{ x = $PX0; y = $PY0; width = $PW; height = $PH }
    data_min = $minV; data_max = $maxV
    covers_data = ($minV -ge $YMIN -and $maxV -le $YMAX)
    negative_range_added = ($YMIN -lt 0)
    negative_range_reason = $(if ($YMIN -lt 0) { '2026-09 profit 为负，round-02 允许在原图表区域内增加负轴范围；柱高仍按同一比例尺绘制，负值画在零线以下' } else { $null })
  }
  conclusion = $CONCLUSION
  conclusion_estimated_lines = $BODY_LINES
}
[IO.File]::WriteAllText((Join-Path $OutDir 'computed-data.json'), (($computed | ConvertTo-Json -Depth 10) + "`n"), $utf8)

$regions = [pscustomobject][ordered]@{
  title = [pscustomobject][ordered]@{
    x = $TITLE.x; y = $TITLE.y; width = $TITLE.w; height = $TITLE.h
    main_style = @{ role = 'title-area'; background = '#' + $PAGE; title_fs = 42; title_bold = $true
                    title_color = '#' + $INK; title_box = @{ x = 40; y = 34; width = 1200; height = 62 }
                    subtitle_fs = 24; subtitle_color = '#' + $MUTED
                    subtitle_box = @{ x = 40; y = 98; width = 1520; height = 36 }
                    badge = @{ fill = '#' + $NET; radius = 12; fs = 24; text_color = '#' + $PANEL; x = $BADGE_X; y = 44; width = $BADGE_W; height = 42 }
                    title_text = $TITLE_TXT; subtitle_text = $SUBTITLE; badge_text = $BADGE }
  }
  kpi_row = [pscustomobject][ordered]@{
    x = $KPIR.x; y = $KPIR.y; width = $KPIR.w; height = $KPIR.h
    main_style = @{ background = '#' + $PANEL; radius = 16; count = 4; card_width = $KPI_W; gap = $KPI_GAP
                    label_fs = 24; label_color = '#' + $MUTED; value_fs = 44; value_bold = $true
                    value_color = '#' + $INK; sub_fs = 22; sub_color = '#' + $MUTED
                    accent_bar = @{ x_offset = 24; y = 158; width = 56; height = 4; color = '#' + $NET; radius = 2 } }
    cards = @(foreach ($i in 0..3) {
      [pscustomobject][ordered]@{
        index = $i + 1; x = $KPI_X[$i]; y = $KPIR.y; width = $KPI_W; height = $KPIR.h
        label = $KPI_DEFS[$i].label; value = $KPI_DEFS[$i].value; sub = $KPI_DEFS[$i].sub
        label_box = @{ x = ($KPI_X[$i] + 24); y = 170; width = 317; height = 35 }
        value_box = @{ x = ($KPI_X[$i] + 24); y = 207; width = 317; height = 64 }
        sub_box   = @{ x = ($KPI_X[$i] + 24); y = 273; width = 317; height = 28 }
      } })
  }
  chart = [pscustomobject][ordered]@{
    x = $CHART.x; y = $CHART.y; width = $CHART.w; height = $CHART.h
    main_style = @{ background = '#' + $PANEL; radius = 20; title_fs = 26; title_color = '#' + $INK
                    legend_fs = 22; net_color = '#' + $NET; profit_color = '#' + $PRF
                    grid_color = '#' + $GRID; baseline_color = '#' + $BASE
                    x_label_fs = 22; x_label_color = '#' + $INK2; y_label_fs = 22; y_label_color = '#' + $MUTED }
    plot = @{ x = $PX0; y = $PY0; width = $PW; height = $PH }
    scale = @{ ymin = $YMIN; ymax = $YMAX; step = $YSTEP; zero_line_y = (Y 0); negative_range_added = ($YMIN -lt 0) }
    groups = $n; group_width = [Math]::Round($GW, 4); bar_width = $BARW
    bars = @(foreach ($row in $ROWS) {
      [pscustomobject]@{
        month = $row.month
        net_x = [Math]::Round($PX0 + ($ROWS.IndexOf($row) * $GW) + $BAR_PAD, 2)
        net_y = (Y $row.net_revenue); net_w = $BARW; net_h = [Math]::Round((Y 0) - (Y $row.net_revenue), 2)
        profit_x = [Math]::Round($PX0 + ($ROWS.IndexOf($row) * $GW) + $BAR_PAD + $BARW + $BAR_GAP, 2)
        profit_y = $(if ($row.profit -ge 0) { Y $row.profit } else { Y 0 })
        profit_w = $BARW
        profit_h = $(if ($row.profit -ge 0) { [Math]::Round((Y 0) - (Y $row.profit), 2) } else { [Math]::Round((Y $row.profit) - (Y 0), 2) })
        profit_below_zero = ($row.profit -lt 0)
        net_value = $row.net_revenue; profit_value = $row.profit
      } })
    zero_based = ($YMIN -eq 0)
    callout = $(if ($null -ne $negCallout) { [pscustomobject]@{ month = $negCallout.month; value = $negCallout.v; x = ($PX1 - 230); y = 632; width = 230; height = 32; color = '#' + $NEG } } else { $null })
  }
  table = [pscustomobject][ordered]@{
    x = $TABLE.x; y = $TABLE.y; width = $TABLE.w; height = $TABLE.h
    main_style = @{ background = '#' + $PANEL; radius = 20; title_fs = 26; title_color = '#' + $INK
                    header_fs = 22; header_bold = $true; header_color = '#' + $INK2
                    header_strip = @{ x = $TBL_IN_X; y = $HDR_Y; width = $TBL_IN_W; height = $HDR_H; color = '#' + $STRIP; radius = 8 }
                    cell_fs = 22; cell_color = '#' + $INK; muted_cell_color = '#' + $MUTED
                    negative_color = '#' + $NEG; separator_color = '#' + $SEP }
    columns = @(foreach ($c in $COLS) { [pscustomobject]@{ name = $c.name; x = $c.x; width = $c.w; align = $c.align; value = $c.val } })
    header_y = $HDR_Y; row_y = $ROW_Y; row_height = $ROW_H
    row_count = $n; total_height_used = [Math]::Round(($ROW_Y + ($n * $ROW_H)) - $TABLE.y, 2)
    panel_bottom = ($TABLE.y + $TABLE.h)
    fits = (($ROW_Y + ($n * $ROW_H)) -le ($TABLE.y + $TABLE.h))
  }
  conclusion = [pscustomobject][ordered]@{
    x = $CONC.x; y = $CONC.y; width = $CONC.w; height = $CONC.h
    main_style = @{ background = '#' + $PANEL; radius = 20; title_fs = 26; title_color = '#' + $INK
                    body_fs = 24; body_color = '#' + $INK2; body_max_lines = 4
                    body_box = @{ x = 64; y = 810; width = 1472; height = 140 } }
    text = $CONCLUSION; estimated_lines = $BODY_LINES
  }
}

$lmap = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/a22-layout-map/v1'
  task = 'A22'; round = $Round
  canvas = [pscustomobject]@{ width = 1600; height = 1000; background = '#' + $PAGE }
  regions = $regions
  probe_note = 'probe 取离字形 6px 的位置、且垂直居中：LEFT 对齐取文本框左缘外 6px（x-6），RIGHT 对齐取文本框左缘内 6px（x+6，因为右对齐的字形结束于框右缘、左邻列的右对齐字形恰好结束于本框左缘，x+6 两侧都够不到任何字形）。probe 必须落在与文字同层的实际背景上，不采到字形；probe_min_x 是该文本所处最上层底面的左边界（页面 0、面板 40/960、表头色条 976、KPI 卡各自左缘），保证采样点确实落在声明的背景上。'
  blocks = $BLOCK
  problems = $problems
  generator = 'tmp/run-20261002-220723-mimo/A22/gen-a22.ps1'
}
[IO.File]::WriteAllText($MapPath, (($lmap | ConvertTo-Json -Depth 12) + "`n"), $utf8)

# ---- change-audit.json (round 02 / 03) ---------------------------------------
if ($Round -ge 2) {
  $prevRows = $PREV.rows; $prevT = $PREV.totals
  $srcChanges = @(
    [pscustomobject]@{ month = '2026-08'; field = 'refund_amount'; old = 15048; new = 25048; delta = 10000; source = 'rounds/round-02.md' },
    [pscustomobject]@{ month = '2026-09'; field = 'operating_cost'; old = 138000; new = 208000; delta = 70000; source = 'rounds/round-02.md' }
  )
  $added = @()
  if ($Round -ge 3) {
    $added = @([pscustomobject][ordered]@{
      month = '2026-10'; orders = 640; gross_revenue = 224000; refund_amount = 11200
      operating_cost = 142000; sessions = 5900; source = 'rounds/round-03.md'
      net_revenue = $ROWS[$n - 1].net_revenue; profit = $ROWS[$n - 1].profit
      refund_rate = $ROWS[$n - 1].refund_rate; conversion_rate = $ROWS[$n - 1].conversion_rate
    })
  }
  $propagation = New-Object System.Collections.Generic.List[object]
  foreach ($row in $ROWS) {
    $before = @($prevRows | Where-Object { $_.month -eq $row.month })
    if ($before.Count -eq 0) {
      $propagation.Add([pscustomobject][ordered]@{
        month = $row.month; status = 'new-row'
        before = $null; after = $row
        changed_fields = @('orders','gross_revenue','refund_amount','operating_cost','sessions','net_revenue','profit','refund_rate','conversion_rate')
      })
      continue
    }
    $b = $before[0]
    $changed = @()
    foreach ($f in @('orders','gross_revenue','refund_amount','operating_cost','sessions','net_revenue','profit','refund_rate','conversion_rate')) {
      if ($b.$f -ne $row.$f) { $changed += $f }
    }
    if ($changed.Count -eq 0) { continue }
    $propagation.Add([pscustomobject][ordered]@{
      month = $row.month; status = 'recomputed'
      before = [pscustomobject]@{ refund_amount = $b.refund_amount; operating_cost = $b.operating_cost
                                  net_revenue = $b.net_revenue; profit = $b.profit
                                  refund_rate = $b.refund_rate; conversion_rate = $b.conversion_rate }
      after  = [pscustomobject]@{ refund_amount = $row.refund_amount; operating_cost = $row.operating_cost
                                  net_revenue = $row.net_revenue; profit = $row.profit
                                  refund_rate = $row.refund_rate; conversion_rate = $row.conversion_rate }
      changed_fields = $changed
    })
  }

  $unchanged = @(
    '画布仍为 1600x1000',
    ('主区域边界：title ({0},{1},{2},{3})、kpi-row ({4},{5},{6},{7})、chart ({8},{9},{10},{11})、table ({12},{13},{14},{15})、conclusion ({16},{17},{18},{19}) —— 三轮完全一致（差 0px，在 ±2px 内）' -f `
      $TITLE.x, $TITLE.y, $TITLE.w, $TITLE.h, $KPIR.x, $KPIR.y, $KPIR.w, $KPIR.h, `
      $CHART.x, $CHART.y, $CHART.w, $CHART.h, $TABLE.x, $TABLE.y, $TABLE.w, $TABLE.h, `
      $CONC.x, $CONC.y, $CONC.w, $CONC.h),
    '主字体 Noto Sans CJK SC / Inter 混排栈，正文最小 22',
    '配色视觉系统：页面 #EDEFF7、面板 #FFFFFF、正文 #10142E、次要 #3A3F63/#5B6180、净收入柱 #5B4FE8、利润柱 #FFB020（含负值柱，颜色不随轮次改变）、网格 #E4E7F3、零线 #A8ADC9',
    '柱图仍为净收入/利润共用零起点的分组柱图，比例尺 y=-50000..250000 步长 50000',
    '四 KPI 标签与口径：总净收入=收入-退款、总经营利润=净收入-operating_cost、总订单、总体转化率=总订单/总sessions',
    '表格仍为 月份/净收入/利润/退款率/转化率 五列',
    '2026-04..2026-09 六个月未被删改；原始 csv 字段 orders/gross_revenue/sessions 三轮完全不变',
    '0 个 <Image>、0 个 transform，全部文字 fontSize >= 22'
  )
  if ($Round -eq 3) { $unchanged += 'round-02 的两项财务更正继续有效：2026-08 refund_amount=25048、2026-09 operating_cost=208000' }

  # ===== round-03 题面逐条证据 + 每项累计值/轴/结论的机器校验 ==========================
  # 题面：「两项第二轮更正继续有效」「不能省略 2026-04 或偷偷恢复旧数据」
  #       「核对每项累计值/轴/结论」。以下全部由真实数据算出并断言，不写死 true。
  $r04 = $ROWS | Where-Object { $_.month -eq '2026-04' }
  $r08 = $ROWS | Where-Object { $_.month -eq '2026-08' }
  $r09 = $ROWS | Where-Object { $_.month -eq '2026-09' }

  $corr = @()
  if ($Round -ge 2) {
    $corr1ok = ($null -ne $r08 -and [int]$r08.refund_amount -eq 25048)
    $corr2ok = ($null -ne $r09 -and [int]$r09.operating_cost -eq 208000)
    $corr = @(
      [pscustomobject][ordered]@{
        month = '2026-08'; field = 'refund_amount'
        round_01_value = 15048; round_02_corrected_value = 25048
        actual_value = $(if ($null -ne $r08) { [int]$r08.refund_amount } else { $null })
        still_effective = $corr1ok
        restored_to_round_01_value = ($null -ne $r08 -and [int]$r08.refund_amount -eq 15048)
        derived_now = $(if ($null -ne $r08) { [pscustomobject]@{ gross_revenue = [int]$r08.gross_revenue; net_revenue = [int]$r08.net_revenue; profit = [int]$r08.profit; refund_rate = [double]$r08.refund_rate } } else { $null })
        round_01_derived = @{ net_revenue = 173052; profit = 41052; refund_rate = 0.08 }
      }
      [pscustomobject][ordered]@{
        month = '2026-09'; field = 'operating_cost'
        round_01_value = 138000; round_02_corrected_value = 208000
        actual_value = $(if ($null -ne $r09) { [int]$r09.operating_cost } else { $null })
        still_effective = $corr2ok
        restored_to_round_01_value = ($null -ne $r09 -and [int]$r09.operating_cost -eq 138000)
        derived_now = $(if ($null -ne $r09) { [pscustomobject]@{ net_revenue = [int]$r09.net_revenue; profit = [int]$r09.profit } } else { $null })
        round_01_derived = @{ net_revenue = 202368; profit = 64368 }
      }
    )
    if (-not $corr1ok) { $problems.Add('两轮更正失效：2026-08 refund_amount 不是 25048') }
    if (-not $corr2ok) { $problems.Add('两轮更正失效：2026-09 operating_cost 不是 208000') }
    if ($null -ne $r08 -and [int]$r08.net_revenue -eq 173052) { $problems.Add('偷偷恢复旧数据：2026-08 net_revenue 回到 173052') }
    if ($null -ne $r08 -and [Math]::Abs([double]$r08.refund_rate - 0.08) -lt 0.000001) { $problems.Add('偷偷恢复旧数据：2026-08 refund_rate 回到 8%') }
    if ($null -ne $r09 -and [int]$r09.profit -eq 64368) { $problems.Add('偷偷恢复旧数据：2026-09 profit 回到 64368') }
  }

  $chk = New-Object System.Collections.Generic.List[object]
  $addChk = {
    param([string]$name, $expected, $actual, [bool]$pass)
    $chk.Add([pscustomobject][ordered]@{ check = $name; expected = $expected; actual = $actual; pass = $pass })
    if (-not $pass) { $problems.Add(('check failed: {0} | expected {1} | actual {2}' -f $name, $expected, $actual)) }
  }

  $expMonths = @('2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09')
  if ($Round -ge 3) { $expMonths += '2026-10' }
  $actMonths = @($ROWS | ForEach-Object { [string]$_.month })

  # --- 月份：不得省略 2026-04，不得缺行，最后一月必须是最新月 ---
  & $addChk 'month_count' $expMonths.Count $actMonths.Count ($actMonths.Count -eq $expMonths.Count)
  & $addChk 'months_present_and_in_order' ($expMonths -join ',') ($actMonths -join ',') ((($actMonths -join ',') -eq ($expMonths -join ',')))
  & $addChk 'month_2026_04_not_omitted' $true ($null -ne $r04) ($null -ne $r04)
  & $addChk 'last_month_is_newest' $expMonths[($expMonths.Count - 1)] $MONTH_LAST ($MONTH_LAST -eq $expMonths[($expMonths.Count - 1)])

  # --- 每月公式自洽 ---
  foreach ($row in $ROWS) {
    $eNet = [int]$row.gross_revenue - [int]$row.refund_amount
    & $addChk ("{0}.net_revenue = gross - refund" -f $row.month) $eNet ([int]$row.net_revenue) ($eNet -eq [int]$row.net_revenue)
    $ePro = [int]$row.net_revenue - [int]$row.operating_cost
    & $addChk ("{0}.profit = net - operating_cost" -f $row.month) $ePro ([int]$row.profit) ($ePro -eq [int]$row.profit)
    $eRr = [double]$row.refund_amount / [double]$row.gross_revenue
    & $addChk ("{0}.refund_rate = refund / gross" -f $row.month) ([Math]::Round($eRr, 6)) ([Math]::Round([double]$row.refund_rate, 6)) (([Math]::Abs([double]$row.refund_rate - $eRr) -lt 0.000001))
    $eCr = [double]$row.orders / [double]$row.sessions
    & $addChk ("{0}.conversion_rate = orders / sessions" -f $row.month) ([Math]::Round($eCr, 6)) ([Math]::Round([double]$row.conversion_rate, 6)) (([Math]::Abs([double]$row.conversion_rate - $eCr) -lt 0.000001))
  }

  # --- 每项累计值：KPI 与汇总必须等于逐行之和 ---
  $sumNet = 0; foreach ($row in $ROWS) { $sumNet += [int]$row.net_revenue }
  $sumPro = 0; foreach ($row in $ROWS) { $sumPro += [int]$row.profit }
  $sumOrd = 0; foreach ($row in $ROWS) { $sumOrd += [int]$row.orders }
  $sumSes = 0; foreach ($row in $ROWS) { $sumSes += [int]$row.sessions }
  & $addChk 'totals.net_revenue = sum(rows)' $sumNet ([int]$T.net_revenue) ($sumNet -eq [int]$T.net_revenue)
  & $addChk 'totals.profit = sum(rows)' $sumPro ([int]$T.profit) ($sumPro -eq [int]$T.profit)
  & $addChk 'totals.orders = sum(rows)' $sumOrd ([int]$T.orders) ($sumOrd -eq [int]$T.orders)
  & $addChk 'totals.sessions = sum(rows)' $sumSes ([int]$T.sessions) ($sumSes -eq [int]$T.sessions)
  $eConv = $sumOrd / [double]$sumSes
  & $addChk 'totals.overall_conversion_rate = total_orders / total_sessions' ([Math]::Round($eConv, 6)) ([Math]::Round([double]$T.overall_conversion_rate, 6)) (([Math]::Abs([double]$T.overall_conversion_rate - $eConv) -lt 0.000001))

  # --- 轴 ---
  & $addChk 'axis_covers_data_min' $true ($minV -ge $YMIN) ($minV -ge $YMIN)
  & $addChk 'axis_covers_data_max' $true ($maxV -le $YMAX) ($maxV -le $YMAX)
  & $addChk 'axis_min_is_a_step_multiple' $true (($YMIN % $YSTEP) -eq 0) (($YMIN % $YSTEP) -eq 0)
  & $addChk 'axis_max_is_a_step_multiple' $true (($YMAX % $YSTEP) -eq 0) (($YMAX % $YSTEP) -eq 0)
  & $addChk 'axis_contains_zero' $true (($YMIN -le 0) -and ($YMAX -ge 0)) (($YMIN -le 0) -and ($YMAX -ge 0))
  if ($minV -lt 0) { & $addChk 'negative_data_has_negative_axis_range' $true ($YMIN -lt 0) ($YMIN -lt 0) }
  if ($Round -eq 1) { & $addChk 'round_01_axis_is_zero_based' 0 $YMIN ($YMIN -eq 0) }

  # --- 结论必须由实际算出的累计值拼成 ---
  $conclBlob = [string]$CONCLUSION
  $kpiBlob = (@($KPI_DEFS | ForEach-Object { $_.label + '=' + $_.value + ' (' + $_.sub + ')' }) -join ' ｜ ')
  & $addChk 'conclusion_contains_total_net_revenue' (FmtInt $T.net_revenue) $(if ($conclBlob -match [regex]::Escape((FmtInt $T.net_revenue))) { (FmtInt $T.net_revenue) } else { 'NOT FOUND' }) ($conclBlob -match [regex]::Escape((FmtInt $T.net_revenue)))
  & $addChk 'conclusion_contains_total_profit' (FmtInt $T.profit) $(if ($conclBlob -match [regex]::Escape((FmtInt $T.profit))) { (FmtInt $T.profit) } else { 'NOT FOUND' }) ($conclBlob -match [regex]::Escape((FmtInt $T.profit)))
  & $addChk 'conclusion_contains_total_orders' (FmtInt $T.orders) $(if ($conclBlob -match [regex]::Escape((FmtInt $T.orders))) { (FmtInt $T.orders) } else { 'NOT FOUND' }) ($conclBlob -match [regex]::Escape((FmtInt $T.orders)))
  & $addChk 'conclusion_contains_overall_conversion_rate' (FmtPct $T.overall_conversion_rate) $(if ($conclBlob -match [regex]::Escape((FmtPct $T.overall_conversion_rate))) { (FmtPct $T.overall_conversion_rate) } else { 'NOT FOUND' }) ($conclBlob -match [regex]::Escape((FmtPct $T.overall_conversion_rate)))
  & $addChk 'conclusion_contains_last_month' $MONTH_LAST $(if ($conclBlob -match [regex]::Escape($MONTH_LAST)) { $MONTH_LAST } else { 'NOT FOUND' }) ($conclBlob -match [regex]::Escape($MONTH_LAST))
  if ($Round -eq 3) {
    & $addChk 'conclusion_states_seven_months' $true (($conclBlob -match '七个月') -or ($conclBlob -match '7 个月')) (($conclBlob -match '七个月') -or ($conclBlob -match '7 个月'))
    & $addChk 'kpi_values_are_current_aggregates' (FmtInt $T.net_revenue) $(if ($kpiBlob -match [regex]::Escape((FmtInt $T.net_revenue))) { (FmtInt $T.net_revenue) } else { 'NOT FOUND' }) ($kpiBlob -match [regex]::Escape((FmtInt $T.net_revenue)))
    & $addChk 'kpi_orders_matches_aggregate' (FmtInt $T.orders) $(if ($kpiBlob -match [regex]::Escape((FmtInt $T.orders))) { (FmtInt $T.orders) } else { 'NOT FOUND' }) ($kpiBlob -match [regex]::Escape((FmtInt $T.orders)))
    & $addChk 'kpi_row_label_says_7_months' $true ($kpiBlob -match '7 个月合计') ($kpiBlob -match '7 个月合计')

    # --- 结论里的比较性断言逐条核对（题面要求「核对…结论」） ---
    $maxNet = ($ROWS | ForEach-Object { [int]$_.net_revenue } | Measure-Object -Maximum).Maximum
    $maxPro = ($ROWS | ForEach-Object { [int]$_.profit } | Measure-Object -Maximum).Maximum
    $maxRr  = ($ROWS | ForEach-Object { [double]$_.refund_rate } | Measure-Object -Maximum).Maximum
    $minCr  = ($ROWS | ForEach-Object { [double]$_.conversion_rate } | Measure-Object -Minimum).Minimum
    $negMonths = @($ROWS | Where-Object { [int]$_.profit -lt 0 } | ForEach-Object { $_.month })
    $claim = $ROWS[($n - 1)]
    & $addChk 'claim_newest_month_net_is_7mo_max' $maxNet ([int]$claim.net_revenue) ([int]$claim.net_revenue -eq $maxNet)
    & $addChk 'claim_newest_month_profit_is_7mo_max' $maxPro ([int]$claim.profit) ([int]$claim.profit -eq $maxPro)
    & $addChk 'claim_2026_09_is_only_negative_profit' '2026-09' ($negMonths -join ',') ((($negMonths -join ',') -eq '2026-09'))
    & $addChk 'claim_2026_08_refund_rate_is_max' ([Math]::Round($maxRr, 6)) ([Math]::Round([double]$r08.refund_rate, 6)) (([Math]::Abs([double]$r08.refund_rate - $maxRr) -lt 0.000001))
    & $addChk 'claim_2026_06_conversion_rate_is_min' ([Math]::Round($minCr, 6)) ([Math]::Round([double]$ROWS[2].conversion_rate, 6)) (([Math]::Abs([double]$ROWS[2].conversion_rate - $minCr) -lt 0.000001))
    & $addChk 'claim_overall_conversion_below_2026_04' $true ([double]$T.overall_conversion_rate -lt [double]$ROWS[0].conversion_rate) ([double]$T.overall_conversion_rate -lt [double]$ROWS[0].conversion_rate)
  }

  $audit = [pscustomobject][ordered]@{
    schema = 'snapshot-suite/a22-change-audit/v1'
    task = 'A22'; round = $Round; generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz'); timezone = 'UTC+08:00'
    execution_mode = 'preloaded_sequential（预置三轮连续执行，rounds/round-0N.md 在执行前已存在，不等待外部反馈）'
    source_file = 'inputs/monthly.csv (unmodified)'
    source_changes = $srcChanges
    rows_added = $added
    propagation = $propagation
    totals = [pscustomobject][ordered]@{
      before = $prevT; after = $T
      net_revenue_delta = ($T.net_revenue - $prevT.net_revenue)
      profit_delta = ($T.profit - $prevT.profit)
      orders_delta = ($T.orders - $prevT.orders)
      sessions_delta = ($T.sessions - $prevT.sessions)
      overall_conversion_rate_before = $prevT.overall_conversion_rate
      overall_conversion_rate_after = $T.overall_conversion_rate
    }
    negative_profit = [pscustomobject][ordered]@{
      exists = ($minV -lt 0)
      months = @(foreach ($row in $ROWS) { if ($row.profit -lt 0) { $row.month } })
      values = @(foreach ($row in $ROWS) { if ($row.profit -lt 0) { $row.profit } })
      axis_min = $YMIN
      rendered_below_zero = ($minV -lt 0 -and (Y $minV) -gt (Y 0))
      clipped = $false
      drawn_as_positive = $false
      note = '负柱按同一比例尺画在零线以下（Y(profit) > Y(0)），未裁剪、未翻正、未只改数字不改柱高'
    }
    corrections_still_effective = $corr
    cumulative_axis_conclusion_checks = [pscustomobject][ordered]@{
      total = $chk.Count
      passed = @($chk | Where-Object { $_.pass }).Count
      failed = @($chk | Where-Object { -not $_.pass }).Count
      covers = @('每月公式自洽（net/profit/refund_rate/conversion_rate）',
                 '每项累计值（net/profit/orders/sessions/overall_conversion_rate 与逐行之和一致）',
                 '轴（覆盖数据、步长对齐零点、含零、负数据必有负范围、round-01 必须零基）',
                 '结论含各累计值与最后月份',
                 'round-03：KPI 为 7 个月聚合、月份集合含 2026-04 且不缺行')
      rows = $chk
    }
    unchanged = $unchanged
    visual_regression = [pscustomobject][ordered]@{
      canvas_unchanged = $true
      region_bounds_unchanged = $true
      region_bounds = [pscustomobject][ordered]@{
        title = '(40,34,1520,100)'; kpi_row = '(40,146,1520,160)'
        chart = '(40,316,900,410)'; table = '(960,316,600,410)'; conclusion = '(40,746,1520,218)'
      }
      max_region_delta_px = 0
      tolerance_px = 2
      fonts_unchanged = $true
      palette_unchanged = $true
      bar_colors_unchanged = $true
      internal_relayout = $(if ($Round -eq 3) { '7 行 7 组：表格行高仍 44px（新增第 7 行后底边 702 <= 面板底 726），柱组宽由 125 收窄到 107.14，柱宽由 46.25 收窄到 39.64 —— 均属题面允许的「内部刻度/行距」重排' } else { '6 行 6 组，与上一轮内部布局一致' })
      checks = @('画布 1600x1000', '五块主区域边界 0px 偏移', '柱色与字体不变', '负柱在零线以下且高度按同一比例尺', 'KPI 口径不变仅数值重算')
    }
    problems = $problems
  }
  [IO.File]::WriteAllText((Join-Path $OutDir 'change-audit.json'), (($audit | ConvertTo-Json -Depth 12) + "`n"), $utf8)
}

# ------------------------------------------------------------------ summary -----
"round $Round"
"  dashboard -> $(Join-Path $OutDir 'dashboard.snapshot')  $((Get-Item (Join-Path $OutDir 'dashboard.snapshot')).Length) bytes"
"  rows      = $n   months = $MONTH_FIRST .. $MONTH_LAST   last = $MONTH_LAST"
"  totals    = net $(FmtInt $T.net_revenue)  profit $(FmtInt $T.profit)  orders $(FmtInt $T.orders)  conv $(FmtPct $T.overall_conversion_rate)  sessions $(FmtInt $T.sessions)"
"  axis      = $YMIN .. $YMAX step $YSTEP   zeroY=$(Y 0)   data $minV .. $maxV   negative-range=$(if($YMIN -lt 0){'yes'}else{'no'})"
"  chart     = plot ${PX0},${PY0} ${PW}x${PH}  groups=$n  groupW=$([Math]::Round($GW,2))  barW=$BARW  barHeightErr=$([Math]::Round($barMaxErr,4))px"
"  table     = $n rows x 5 cols   bottom used = $([Math]::Round($ROW_Y + ($n * $ROW_H),0)) / panel bottom 726"
"  conclusion= $BODY_LINES est lines (box 4)   blocks = $($BLOCK.Count)"
"  regions   = title({0},{1},{2},{3}) kpi({4},{5},{6},{7}) chart({8},{9},{10},{11}) table({12},{13},{14},{15}) conclusion({16},{17},{18},{19})" -f `
    $TITLE.x, $TITLE.y, $TITLE.w, $TITLE.h, $KPIR.x, $KPIR.y, $KPIR.w, $KPIR.h, `
    $CHART.x, $CHART.y, $CHART.w, $CHART.h, $TABLE.x, $TABLE.y, $TABLE.w, $TABLE.h, `
    $CONC.x, $CONC.y, $CONC.w, $CONC.h
"  problems  = $($problems.Count)"
foreach ($p in $problems) { "  !! $p" }
