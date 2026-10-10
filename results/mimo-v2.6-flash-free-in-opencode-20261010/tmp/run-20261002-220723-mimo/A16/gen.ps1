# A16 - emit the corrected quarterly-review report DSL from inputs/source.csv.
# source.csv is the single source of truth; every number in the figure and in
# corrected-data.json is computed here, never transcribed by hand.
# The flawed report PNG is never read by this script.
param([int]$V = 1)

$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
$OUT = Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A16'
$CSV = Join-Path $ROOT 'tasks\A16-visual-data-forensics\inputs\source.csv'
New-Item -ItemType Directory -Force -Path $TMP | Out-Null
New-Item -ItemType Directory -Force -Path $OUT | Out-Null
$ENC = New-Object Text.UTF8Encoding($false)

# ============================================================ source.csv ======
$lines = [IO.File]::ReadAllLines($CSV)
$rows = @()
for ($i = 1; $i -lt $lines.Count; $i++) {
  $ln = $lines[$i]
  if ([string]::IsNullOrWhiteSpace($ln)) { continue }
  $p = $ln.Split(',')
  $rev = [double]$p[1]; $cost = [double]$p[2]
  $rows += [pscustomobject]@{
    quarter = $p[0].Trim(); revenue = $rev; cost = $cost
    profit  = [math]::Round($rev - $cost, 10)
    margin  = [math]::Round(($rev - $cost) / $rev * 100, 1)
    costrate= [math]::Round($cost / $rev * 100, 1)
  }
}
if ($rows.Count -ne 4) { throw "expected 4 quarters, got $($rows.Count)" }

$annRev  = [math]::Round(($rows | Measure-Object -Property revenue -Sum).Sum, 10)
$annCost = [math]::Round(($rows | Measure-Object -Property cost   -Sum).Sum, 10)
$annProf = [math]::Round($annRev - $annCost, 10)
$annMarg = [math]::Round($annProf / $annRev * 100, 1)

for ($i = 0; $i -lt $rows.Count; $i++) {
  if ($i -eq 0) {
    $rows[$i] | Add-Member -NotePropertyName rev_qoq -NotePropertyValue $null
    $rows[$i] | Add-Member -NotePropertyName rev_qoq_pct -NotePropertyValue $null
    $rows[$i] | Add-Member -NotePropertyName prof_share -NotePropertyValue ([math]::Round($rows[$i].profit / $annProf * 100, 1))
  } else {
    $d = $rows[$i].revenue - $rows[$i-1].revenue
    $rows[$i] | Add-Member -NotePropertyName rev_qoq -NotePropertyValue ([math]::Round($d, 10))
    $rows[$i] | Add-Member -NotePropertyName rev_qoq_pct -NotePropertyValue ([math]::Round($d / $rows[$i-1].revenue * 100, 1))
    $rows[$i] | Add-Member -NotePropertyName prof_share -NotePropertyValue ([math]::Round($rows[$i].profit / $annProf * 100, 1))
  }
}

$K     = $rows | Sort-Object profit -Descending | Select-Object -First 1     # key quarter by profit
$Kbest = $rows | Sort-Object margin  -Descending | Select-Object -First 1
$Mmin  = $rows | Sort-Object margin   | Select-Object -First 1
$Cmin  = $rows | Sort-Object costrate | Select-Object -First 1
$Q3    = $rows | Where-Object { $_.quarter -eq 'Q3' }
$Q2    = $rows | Where-Object { $_.quarter -eq 'Q2' }

# every superlative that the figure will print is checked against source.csv
# here, so a data change can never leave a false claim standing in the report.
$Rmax  = $rows | Sort-Object revenue -Descending | Select-Object -First 1
if ($K.quarter -ne $Kbest.quarter) { throw "claim invalid: $($K.quarter) is not the max-margin quarter ($($Kbest.quarter))" }
if ($K.quarter -ne $Cmin.quarter)  { throw "claim invalid: $($K.quarter) is not the lowest-cost-rate quarter ($($Cmin.quarter))" }
if ($K.quarter -ne $Rmax.quarter)  { throw "claim invalid: $($K.quarter) is not the max-revenue quarter ($($Rmax.quarter))" }
if ($K.quarter -eq $Q3.quarter)    { throw "claim invalid: Q3 and the key quarter collapsed" }

$spread = [math]::Round($K.margin - $Mmin.margin, 1)
$profGap = [math]::Round($K.profit - $Q3.profit, 10)

# ============================================================ formatting ======
function F0($v) {
  $d = [double]$v; $r = [math]::Round($d, 0)
  if ([math]::Abs($d - $r) -lt 1e-9) { return ([int]$r).ToString([cultureinfo]::InvariantCulture) }
  return $d.ToString('0.#', [cultureinfo]::InvariantCulture)
}
function F1($v) { return ([math]::Round([double]$v, 1)).ToString('0.0', [cultureinfo]::InvariantCulture) }

# ============================================================ typography ======
# approximate advance width in em units, used only to centre / right-align labels
function TW([string]$s, [double]$fs) {
  $u = 0.0
  foreach ($ch in $s.ToCharArray()) {
    $c = [int]$ch
    if     ($c -ge 0x3000 -and $c -le 0x9FFF) { $u += 1.0 }
    elseif ($c -ge 0xFF00 -and $c -le 0xFF60) { $u += 1.0 }
    elseif ($c -ge 0x2000 -and $c -le 0x2FFF) { $u += 0.60 }
    elseif ($c -eq 32)  { $u += 0.30 }
    elseif ($c -eq 46)  { $u += 0.28 }
    elseif ($c -eq 44)  { $u += 0.28 }
    elseif ($c -eq 37)  { $u += 0.86 }
    elseif ($c -eq 43)  { $u += 0.60 }
    elseif ($c -eq 45)  { $u += 0.36 }
    elseif ($c -eq 183) { $u += 0.42 }
    elseif ($c -ge 48 -and $c -le 57)  { $u += 0.60 }
    elseif ($c -ge 65 -and $c -le 90)  { $u += 0.68 }
    elseif ($c -ge 97 -and $c -le 122) { $u += 0.56 }
    else  { $u += 0.50 }
  }
  return [math]::Round($u * $fs, 2)
}
function N([double]$v) { return $v.ToString('0.##', [cultureinfo]::InvariantCulture) }
function Esc([string]$s) {
  $s = $s.Replace('&', '&amp;'); $s = $s.Replace('<', '&lt;'); $s = $s.Replace('>', '&gt;')
  return $s
}

# ============================================================== palette =======
$BG      = '#F4F6FB'; $CARD = '#FFFFFF'; $BORDER = '#E2E8F1'
$INK     = '#18283F'; $MUTED = '#63748F'; $SUB = '#5A6B85'
$REV     = '#245CE4'; $COST = '#E88E35'
$GRID    = '#E9EDF4'; $SEP = '#E9EDF4'
$AMBERBG = '#FFF6E6'; $AMBERB = '#F0DCB6'; $AMBERINK = '#8A5A12'; $AMBERTX = '#4A3A22'
$FOOT    = '#7B8BA3'
$FAM     = 'Inter,Noto Sans CJK SC'
$MINUS   = [string][char]0x2212

# =========================================================== geometry =========
# chart plot: common zero baseline
$PLOT_L = 140; $PLOT_R = 1196; $BASE_Y = 516; $TOP_Y = 236
$Y_MAX = 200.0
$PPU = [math]::Round(($BASE_Y - $TOP_Y) / $Y_MAX, 6)     # 1.4 px per 万元
$TICKS = @(0, 50, 100, 150, 200)

$GROUP_W = 264; $BAR_W = 74; $BAR_GAP = 16
$GROUP_X0 = $PLOT_L
$CENTERS = @(0..3 | ForEach-Object { $GROUP_X0 + ($GROUP_W * $_) + [int]($GROUP_W / 2) })

function GridY([double]$v) { return [math]::Round($BASE_Y - ($v * $PPU), 2) }

$RECTS = @()
$RECTS += [ordered]@{ id = 'chartCard';  x = 48;  y = 130; w = 1184; h = 436; color = $CARD; border = '1 SOLID ' + $BORDER; r = 12 }
$RECTS += [ordered]@{ id = 'profitCard'; x = 48;  y = 582; w = 700;  h = 256; color = $CARD; border = '1 SOLID ' + $BORDER; r = 12 }
$RECTS += [ordered]@{ id = 'keyCard';    x = 767; y = 582; w = 465;  h = 256; color = $AMBERBG; border = '1 SOLID ' + $AMBERB; r = 12 }
$RECTS += [ordered]@{ id = 'legendRev';  x = 1010; y = 156; w = 18; h = 18; color = $REV; r = 4 }
$RECTS += [ordered]@{ id = 'legendCost'; x = 1120; y = 156; w = 18; h = 18; color = $COST; r = 4 }

foreach ($tk in $TICKS) {
  $y = GridY $tk
  $RECTS += [ordered]@{ id = ('grid' + $tk); x = $PLOT_L; y = $y; w = ($PLOT_R - $PLOT_L); h = 1; color = $GRID }
}

$BARS = @()
foreach ($i in 0..3) {
  $cx = $CENTERS[$i]
  $rx  = $cx - $BAR_W - ($BAR_GAP / 2)   # left bar of the pair
  $cx2 = $cx + ($BAR_GAP / 2)            # right bar of the pair
  $r = $rows[$i]
  $rh = [math]::Round($r.revenue * $PPU, 2); $rt = [math]::Round($BASE_Y - $rh, 2)
  $ch = [math]::Round($r.cost   * $PPU, 2); $ct = [math]::Round($BASE_Y - $ch, 2)
  $BARS += [pscustomobject]@{ q = $r.quarter; kind = 'revenue'; x = [int]$rx; y = $rt; w = $BAR_W; h = $rh; cx = [math]::Round($rx + $BAR_W / 2, 2); value = $r.revenue }
  $BARS += [pscustomobject]@{ q = $r.quarter; kind = 'cost';    x = [int]$cx2; y = $ct; w = $BAR_W; h = $ch; cx = [math]::Round($cx2 + $BAR_W / 2, 2); value = $r.cost }
}
foreach ($b in $BARS) {
  $col = $REV; if ($b.kind -eq 'cost') { $col = $COST }
  $RECTS += [ordered]@{ id = ('bar_' + $b.q + '_' + $b.kind); x = $b.x; y = $b.y; w = $b.w; h = $b.h; color = $col; rTL = 4; rTR = 4; rBL = 0; rBR = 0 }
}
# white backplates behind the value labels so no number ever sits on a gridline
foreach ($b in $BARS) {
  $lw = TW (F0 $b.value) 22
  $px_ = [math]::Round($b.cx - ($lw / 2) - 6, 2)
  $py_ = [math]::Round($b.y - 26, 2)
  $RECTS += [ordered]@{ id = ('pill_' + $b.q + '_' + $b.kind); x = $px_; y = $py_; w = [math]::Round($lw + 12, 2); h = 24; color = '#FFFFFF'; r = 4 }
}

# visual marker for the key quarter (the data argument lives in the key card)
$KX = $CENTERS[3]
$RECTS += [ordered]@{ id = 'keyUnderline'; x = ($KX - 34); y = 550; w = 68; h = 4; color = $REV; r = 2 }
$RECTS += [ordered]@{ id = 'profitSep';   x = 76; y = 778; w = 643; h = 1; color = $SEP }

# ============================================================== texts =========
$T = @()
function AddT($id, $text, $x, $iy, $fs, $color, $style, $align) {
  if ($null -eq $style) { $style = 'NORMAL' }
  if ($null -eq $align) { $align = 'left' }
  $left = $x
  if ($align -eq 'center') { $left = [math]::Round($x - (TW $text $fs) / 2, 2) }
  if ($align -eq 'right')  { $left = [math]::Round($x - (TW $text $fs), 2) }
  $script:T += [ordered]@{ id = $id; text = $text; left = $left; iy = $iy; fs = $fs; color = $color; style = $style }
}

# --- header (body copy, >= 22px) ---
$title = '季度复盘：' + $K.quarter + ' 利润 ' + (F0 $K.profit) + ' 万元领跑，全年利润 ' + (F0 $annProf) + ' 万元'
$dq3 = [math]::Round($Q3.revenue - $Q2.revenue, 10)
$subtitle = '收入 ' + (F0 $annRev) + '、成本 ' + (F0 $annCost) + '、利润 ' + (F0 $annProf) + ' 万元；' +
            $K.quarter + ' 利润率 ' + (F1 $K.margin) + '% 全年最高，' + $Q3.quarter + ' 收入环比回落 ' + (F0 ([math]::Abs($dq3))) + ' 万元'
AddT 'title'    $title    48  40 40 $INK   'BOLD' 'left'
AddT 'subtitle' $subtitle 48  94 24 $SUB   'NORMAL' 'left'

# --- chart card ---
AddT 'cTitle' '收入与成本对比 · 共同零起点' 76 152 26 $INK 'BOLD' 'left'
AddT 'unit'   '单位：万元'                  76 192 22 $MUTED 'NORMAL' 'left'
AddT 'lgRev'  '收入'  1036 157 22 $INK 'BOLD'   'left'
AddT 'lgCost' '成本'  1146 157 22 $INK 'NORMAL' 'left'

# y axis ticks (annotations, 22px)
foreach ($tk in $TICKS) {
  $g = GridY $tk
  AddT ('axis' + $tk) (F0 $tk) 128 ([math]::Round($g - 8, 2)) 22 $MUTED 'NORMAL' 'right'
}
# bar value labels (annotations, 22px)
foreach ($b in $BARS) {
  $col = $REV; if ($b.kind -eq 'cost') { $col = $COST }
  AddT ('val_' + $b.q + '_' + $b.kind) (F0 $b.value) $b.cx ([math]::Round($b.y - 22, 2)) 22 $col 'BOLD' 'center'
}
# category labels (annotations, 22px)
foreach ($i in 0..3) {
  $col = $MUTED; $st = 'NORMAL'
  if ($rows[$i].quarter -eq $K.quarter) { $col = $REV; $st = 'BOLD' }
  AddT ('cat' + $i) $rows[$i].quarter $CENTERS[$i] 530 22 $col $st 'center'
}

# --- profit detail card ---
AddT 'pTitle' '利润明细' 76 606 26 $INK 'BOLD' 'left'
AddT 'pNote'  ('利润 = 收入 ' + $MINUS + ' 成本，取自 source.csv') 719 610 22 $MUTED 'NORMAL' 'right'
$COLX = @(76, 232, 388, 544)
foreach ($i in 0..3) {
  $r = $rows[$i]
  AddT ('pq' + $i) $r.quarter                      $COLX[$i] 654 22 $MUTED  'BOLD'   'left'
  AddT ('pp' + $i) ((F0 $r.profit) + ' 万元')      $COLX[$i] 686 34 $INK    'BOLD'   'left'
  AddT ('pm' + $i) ('利润率 ' + (F1 $r.margin) + '%') $COLX[$i] 736 22 $MUTED 'NORMAL' 'left'
}
$totline = '全年合计：收入 ' + (F0 $annRev) + ' · 成本 ' + (F0 $annCost) + ' · 利润 ' + (F0 $annProf) + ' 万元，利润率 ' + (F1 $annMarg) + '%'
AddT 'ptotal' $totline 76 796 22 $INK 'BOLD' 'left'

# --- key quarter card: the quarter is argued from data, not asserted ---
AddT 'kTitle' ('重点观察 · ' + $K.quarter + '（数据论证）') 795 606 26 $AMBERINK 'BOLD' 'left'
$bullets = @(
  ('· 利润 ' + (F0 $K.profit) + ' 万元，全年最高'),
  ($Q3.quarter + ' 为 ' + (F0 $Q3.profit) + ' 万元，' + $K.quarter + ' 多 ' + (F0 $profGap) + ' 万元'),
  ('· 利润率 ' + (F1 $K.margin) + '%，全年最高'),
  ('比最低的 ' + $Mmin.quarter + ' 高 ' + (F1 $spread) + ' 个百分点'),
  ('· 收入 ' + (F0 $K.revenue) + ' 万元，环比 +' + (F0 $K.rev_qoq) + ' 万元'),
  ('即 +' + (F1 $K.rev_qoq_pct) + '%，成本率 ' + (F1 $K.costrate) + '% 全年最低')
)
$BY = @(648, 678, 708, 738, 768, 798)
foreach ($i in 0..5) {
  # continuation lines are indented to sit under their bullet, not at the margin
  $bx = 795
  if (($i % 2) -eq 1) { $bx = 811 }
  AddT ('kb' + $i) $bullets[$i] $bx $BY[$i] 22 $AMBERTX 'NORMAL' 'left'
}

# --- footer ---
AddT 'footer' '虚构数据 · 季度复盘报告 · 数据源 source.csv · 纵轴自 0 起，柱高等比对应数值' 48 856 22 $FOOT 'NORMAL' 'left'

# ============================================================== emit ==========
$lines2 = @()
$lines2 += '<Snapshot type="png" background="' + $BG + '">'
$lines2 += '  <Container width="1280" height="900" color="' + $BG + '">'
$lines2 += '    <Stack>'
foreach ($r in $RECTS) {
  $p = 'left="' + (N $r.x) + '" top="' + (N $r.y) + '" width="' + (N $r.w) + '" height="' + (N $r.h) + '"'
  $d = '<Container color="' + $r.color + '"'
  if ($r.border) { $d += ' border="' + $r.border + '"' }
  if ($r.rTL) { $d += ' borderRadiusTopLeft="' + (N $r.rTL) + '"' }
  if ($r.rTR) { $d += ' borderRadiusTopRight="' + (N $r.rTR) + '"' }
  if ($r.rBL) { $d += ' borderRadiusBottomLeft="' + (N $r.rBL) + '"' }
  if ($r.rBR) { $d += ' borderRadiusBottomRight="' + (N $r.rBR) + '"' }
  if ($r.r)   { $d += ' borderRadius="' + (N $r.r) + '"' }
  $d += '/>'
  $lines2 += '      <Positioned ' + $p + '>' + $d + '</Positioned>'
}
foreach ($e in $T) {
  $top = [math]::Round($e.iy - 0.23 * $e.fs, 2)
  $a = 'color="' + $e.color + '" fontSize="' + (N $e.fs) + '" fontFamily="' + $FAM + '"'
  if ($e.style -ne 'NORMAL') { $a += ' fontStyle="' + $e.style + '"' }
  $lines2 += '      <Positioned left="' + (N $e.left) + '" top="' + (N $top) + '"><Text ' + $a + '>' + (Esc $e.text) + '</Text></Positioned>'
}
$lines2 += '    </Stack>'
$lines2 += '  </Container>'
$lines2 += '</Snapshot>'
$xml = ($lines2 -join "`n") + "`n"

$dslPath = Join-Path $TMP ('corrected-report-v{0:d2}.snapshot' -f $V)
[IO.File]::WriteAllText($dslPath, $xml, $ENC)

# element table for later measurement
$tbl = @{ texts = $T; rects = @($RECTS | ForEach-Object { [pscustomobject]$_ }); bars = $BARS }
[IO.File]::WriteAllText((Join-Path $TMP 'elements.json'), ($tbl | ConvertTo-Json -Depth 8), $ENC)

# ==================================================== corrected-data.json =====
$qout = @()
foreach ($r in $rows) {
  $qout += [ordered]@{
    quarter        = $r.quarter
    revenue_wan    = $r.revenue
    cost_wan       = $r.cost
    profit_wan     = $r.profit
    margin_pct     = $r.margin
    cost_rate_pct  = $r.costrate
    profit_share_of_year_pct = $r.prof_share
    revenue_qoq_wan = $r.rev_qoq
    revenue_qoq_pct = $r.rev_qoq_pct
  }
}
$barout = @()
foreach ($b in $BARS) {
  $barout += [ordered]@{
    quarter = $b.q; series = $b.kind; value_wan = $b.value
    px_height = $b.h; px_top = $b.y; px_left = $b.x; px_width = $b.w
    implied_value_from_axis = [math]::Round(($BASE_Y - $b.y) / $PPU, 2)
    matches_label = ([math]::Abs((($BASE_Y - $b.y) / $PPU) - $b.value) -lt 0.51)
  }
}
$cdd = [ordered]@{
  schema       = 'snapshot-suite/corrected-data/v1'
  task_id      = 'A16'
  run_id       = 'run-20261002-220723-mimo'
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  source       = [ordered]@{
    path  = 'tasks/A16-visual-data-forensics/inputs/source.csv'
    role  = '唯一可信原始数据'
    header = $lines[0]
    rows  = @($lines | Select-Object -Skip 1 | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    note  = '本文件所有派生值均由 gen.ps1 从上述行计算得到，没有手工转录'
  }
  definitions  = [ordered]@{
    unit            = '万元 (10k CNY), all magnitudes in this file are in 万元 unless the key says _pct'
    profit_wan      = 'profit_wan = revenue_wan - cost_wan'
    margin_pct      = 'margin_pct = profit_wan / revenue_wan * 100, rounded to 1 decimal'
    cost_rate_pct   = 'cost_rate_pct = cost_wan / revenue_wan * 100, rounded to 1 decimal'
    profit_share_of_year_pct = 'profit_share_of_year_pct = profit_wan / annual_profit_wan * 100'
    revenue_qoq_wan = 'revenue_qoq_wan[i] = revenue_wan[i] - revenue_wan[i-1]; null for Q1 (no prior quarter in source.csv)'
    revenue_qoq_pct = 'revenue_qoq_pct[i] = revenue_qoq_wan[i] / revenue_wan[i-1] * 100; null for Q1'
    key_quarter_rule = 'key quarter = max(profit_wan); ties broken by margin_pct then revenue_wan. Not chosen by assertion'
  }
  quarters     = $qout
  annual       = [ordered]@{
    revenue_wan = $annRev; cost_wan = $annCost; profit_wan = $annProf; margin_pct = $annMarg
  }
  key_quarter  = [ordered]@{
    quarter          = $K.quarter
    rule             = 'max(profit_wan)'
    profit_wan       = $K.profit
    margin_pct       = $K.margin
    revenue_wan      = $K.revenue
    revenue_qoq_wan  = $K.rev_qoq
    revenue_qoq_pct  = $K.rev_qoq_pct
    cost_rate_pct    = $K.costrate
    profit_share_of_year_pct = $K.prof_share
    evidence = @(
      ('profit_wan ' + $K.profit + ' is the maximum of ' + (($rows | ForEach-Object { $_.profit }) -join '/') + ' for ' + (($rows | ForEach-Object { $_.quarter }) -join '/')),
      ('margin_pct ' + (F1 $K.margin) + ' is the maximum; lowest is ' + $Mmin.quarter + ' at ' + (F1 $Mmin.margin) + ', spread ' + (F1 $spread) + ' pp'),
      ('revenue_wan ' + $K.revenue + ' is the maximum; revenue rose ' + $K.rev_qoq + ' (' + (F1 $K.rev_qoq_pct) + '%) against ' + $Q3.quarter),
      ('cost_rate ' + (F1 $K.costrate) + '% is the lowest of the four quarters'),
      ($Q3.quarter + ' profit is ' + $Q3.profit + ', below ' + $K.quarter + '; ' + $Q3.quarter + ' revenue fell ' + (F0 ([math]::Abs($dq3))) + ' against ' + $Q2.quarter + ' - so ' + $Q3.quarter + ' cannot be the key quarter')
    )
    superseded_claim = 'the flawed report asserted Q3 was the highest-profit quarter (and its profit card showed 42); source.csv gives Q3 = ' + $Q3.profit + ' and Q4 = ' + $K.profit
  }
  axis_definition = [ordered]@{
    chart_type   = 'grouped vertical bar, revenue and cost side by side, common zero baseline'
    x_axis       = [ordered]@{
      type = 'categorical'; categories = @($rows | ForEach-Object { $_.quarter })
      series_order = @('revenue', 'cost')
      group_width_px = $GROUP_W; bars_per_group = 2; bar_width_px = $BAR_W; intra_pair_gap_px = $BAR_GAP
      group_centres_px = $CENTERS
      plot_left_px = $PLOT_L; plot_right_px = $PLOT_R
    }
    y_axis       = [ordered]@{
      type = 'linear'; unit = '万元'
      min = 0; max = $Y_MAX; zero_baseline = $true; truncated = $false
      ticks = $TICKS
      px_per_unit = $PPU
      baseline_px = $BASE_Y; top_px = $TOP_Y; plot_height_px = ($BASE_Y - $TOP_Y)
      gridline_px = @(0..4 | ForEach-Object { GridY $TICKS[$_] })
      common_scale_for_all_bars = $true
      rule = 'bar_px_height = value_wan * px_per_unit, measured from the shared 0 baseline at y = ' + $BASE_Y
    }
  }
  bars = $barout
  verification = [ordered]@{
    bars_match_labels   = (@($barout | Where-Object { -not $_.matches_label }).Count -eq 0)
    all_quarters_plotted = (@($rows | Where-Object { $q = $_.quarter; -not (@($barout | Where-Object { $_.quarter -eq $q }).Count -eq 2) }).Count -eq 0)
    lowest_value_plottable = (@($rows | ForEach-Object { $_.cost; $_.revenue } | Measure-Object -Minimum).Minimum)
    axis_min = 0
    note = 'axis min is 0 and the lowest plotted value is ' + (@($rows | ForEach-Object { $_.cost; $_.revenue } | Measure-Object -Minimum).Minimum) + ' 万元, so every value is representable - unlike the flawed report whose axis started at 100 while cost reached 90'
  }
}
[IO.File]::WriteAllText((Join-Path $OUT 'corrected-data.json'), ($cdd | ConvertTo-Json -Depth 8), $ENC)

Write-Output ("wrote {0}  ({1} rects, {2} texts)" -f $dslPath, $RECTS.Count, $T.Count)
Write-Output ("key quarter = {0}  profit={1} margin={2}  | annual rev={3} cost={4} profit={5} margin={6}" -f $K.quarter, $K.profit, $K.margin, $annRev, $annCost, $annProf, $annMarg)
Write-Output ("ppu={0}  baseline={1} top={2}  bars={3}" -f $PPU, $BASE_Y, $TOP_Y, $BARS.Count)
Write-Output ("wrote {0}" -f (Join-Path $OUT 'corrected-data.json'))
