# gen-b05-b.ps1 -- build case-04, case-05, case-06
# PS 5.1: masthead result is $mh (never $m -- collides with margin $M);
# all command-argument concatenations fully parenthesised; no multi-line commands;
# no inline `if` in argument position.
param([int]$Round = 1)
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $root 'tmp\run-20261002-220723-mimo\B05\lib-b05.ps1')

$calc = Get-Calc
$att  = $calc.attitudes
$cost = $calc.cost

function OutPath([string]$cid) {
    return (Join-Path $script:B05TMP ("{0}\r{1:d2}.snapshot" -f $cid, $Round))
}
function Save([string]$cid, [string]$body, [int]$cw, [int]$ch) {
    Write-Dsl5 (OutPath $cid) $body
    $g = [regex]::Match($body, '<Container width="(\d+)" height="(\d+)"')
    if ($g.Groups[1].Value -ne [string]$cw -or $g.Groups[2].Value -ne [string]$ch) {
        throw "$cid canvas mismatch: expected ${cw}x${ch}"
    }
    Write-Output ("  {0} r{1:d2}  {2}x{3}  {4} bytes  problems={5}" -f
        $cid, $Round, $g.Groups[1].Value, $g.Groups[2].Value,
        (Get-Item (OutPath $cid)).Length, $script:PROBLEMS.Count)
}
function Guard([string]$cid, [double]$bottom, [int]$H) {
    if ($bottom -gt $H) { Fail "$cid content bottom $bottom exceeds canvas height $H" }
}

# =====================================================================
# case-04 -- 顾虑台账 (1440 x 1024, dark, 牵头人桌面)
# =====================================================================
$W = 1440; $H = 1024; $M = 48
$o = ''
$mh = Masthead5 '04' '牵头人工作台 · 桌面' $M 40 ($W - 2*$M) $script:HAIRD $script:MUTED $script:PAPERW 20 20
$o += $mh[0]
$t4 = '顾虑台账：把「不同意」变成可销项的条目'
$o += Ts 'c4-title' $M 96 ($W - 2*$M) 56 $t4 42 $script:DISP $script:PAPERW 'LEFT' ''
$s4 = '3 户有顾虑 · 每条都有负责人、应对方案与截止日期 · 全部来自楼栋问卷与上门记录（演示）'
$o += Ts 'c4-sub' $M 152 1140 30 $s4 21 $script:SANS $script:MUTED 'LEFT' ''

# ---- table ----
$tx = $M; $TW = $W - 2*$M
$colX = @($tx, ($tx + 110), ($tx + 410), ($tx + 880), ($tx + 1010), ($tx + 1150))
$colW = @(110, 300, 470, 130, 140, 194)
$colH = @('户号', '顾虑', '应对方案', '负责人', '状态', '截止日期')
$hy = 200
$o += (Box $tx $hy $TW 36 $script:PANEL_D2 0)
for ($i = 0; $i -lt 6; $i++) {
    $o += Ts ('c4-h' + $i) ($colX[$i] + 14) $hy ($colW[$i] - 20) 36 $colH[$i] 17 $script:SANS $script:MUTED 'LEFT' ''
}
$hy += 36

$reg = @(
  [ordered]@{
    id = '101'; layer = '一层'; area = '76.4 ㎡'; topic = '采光与通行'
    con = @('井道距单元门 2.4 m，', '担心遮挡一楼窗户、影响出入')
    ado = @('井道外移 0.6 m + 超白玻璃；', '结构复核通过后才出施工图；', '预计 3 个工作日给答复')
    who = '王工'; role = '业委会'; st = '待答复'; stC = $script:CORAL; stNote = @('下次上门', '10-11 上午')
    due = '2026-10-12'; left = '剩余 4 天'
  },
  [ordered]@{
    id = '202'; layer = '二层'; area = '78.9 ㎡'; topic = '运行噪音'
    con = @('担心夜间曳引机噪音', '影响休息与二次成交')
    ado = @('减振基座 + 22:00–06:00 静音', '参数（演示值，需厂商书面确认）；', '已安排夜间复测，出报告即答复')
    who = '李老师'; role = '楼组长'; st = '待复测'; stC = $script:AMBER; stNote = @('夜间复测', '10-14 22:00')
    due = '2026-10-15'; left = '剩余 7 天'
  },
  [ordered]@{
    id = '602'; layer = '六层'; area = '78.9 ㎡'; topic = '分摊金额'
    con = @('模型 A 下本户 42,985 元，', '为全楼最高')
    ado = @('给出 A / B / C 三种模型试算', '与十年总账对照；', '可改三期付款 30% / 40% / 30%')
    who = '陈主任'; role = '居委会'; st = '已沟通'; stC = $script:ACC; stNote = @('待本人确认', '签约后再报进度')
    due = '2026-10-18'; left = '剩余 10 天'
  }
)
$rowH = 130
foreach ($rc in $reg) {
    $ry = $hy
    $o += (Box $tx $ry $TW $rowH $script:PANEL_D 0)
    $o += (Box $tx $ry 5 $rowH $script:CORAL 0)
    # 户号
    $o += Ts ('c4-id' + $rc.id) ($colX[0] + 14) ($ry + 16) ($colW[0] - 20) 40 $rc.id 30 $script:MONO $script:PAPERW 'LEFT' ''
    $o += Ts ('c4-ly' + $rc.id) ($colX[0] + 14) ($ry + 58) ($colW[0] - 20) 24 $rc.layer 17 $script:SANS $script:MUTED 'LEFT' ''
    $o += Ts ('c4-ar' + $rc.id) ($colX[0] + 14) ($ry + 80) ($colW[0] - 20) 24 $rc.area 16 $script:MONO $script:MUTED 'LEFT' ''
    $o += Ts ('c4-at' + $rc.id) ($colX[0] + 14) ($ry + 102) ($colW[0] - 20) 24 '顾虑' 16 $script:SANS $script:CORAL 'LEFT' ''
    # 顾虑
    $o += Ts ('c4-tp' + $rc.id) ($colX[1] + 14) ($ry + 16) ($colW[1] - 24) 30 $rc.topic 21 $script:SANS $script:PAPERW 'LEFT' ''
    $o += Ts ('c4-cn1' + $rc.id) ($colX[1] + 14) ($ry + 52) ($colW[1] - 24) 26 $rc.con[0] 17 $script:SANS $script:MUTED 'LEFT' ''
    $o += Ts ('c4-cn2' + $rc.id) ($colX[1] + 14) ($ry + 76) ($colW[1] - 24) 26 $rc.con[1] 17 $script:SANS $script:MUTED 'LEFT' ''
    # 应对
    $o += Ts ('c4-a1' + $rc.id) ($colX[2] + 14) ($ry + 16) ($colW[2] - 24) 26 $rc.ado[0] 17 $script:SANS $script:PAPERW 'LEFT' ''
    $o += Ts ('c4-a2' + $rc.id) ($colX[2] + 14) ($ry + 52) ($colW[2] - 24) 26 $rc.ado[1] 17 $script:SANS $script:PAPERW 'LEFT' ''
    $o += Ts ('c4-a3' + $rc.id) ($colX[2] + 14) ($ry + 88) ($colW[2] - 24) 26 $rc.ado[2] 17 $script:SANS $script:MUTED 'LEFT' ''
    # 负责人
    $o += Ts ('c4-wh' + $rc.id) ($colX[3] + 14) ($ry + 18) ($colW[3] - 20) 30 $rc.who 20 $script:SANS $script:PAPERW 'LEFT' ''
    $o += Ts ('c4-ro' + $rc.id) ($colX[3] + 14) ($ry + 48) ($colW[3] - 20) 26 $rc.role 16 $script:SANS $script:MUTED 'LEFT' ''
    # 状态
    $o += (Pill ($colX[4] + 14) ($ry + 20) $rc.st 16 $rc.stC $script:WHITE $script:SANS 12 32)
    $o += Ts ('c4-sn' + $rc.id) ($colX[4] + 14) ($ry + 58) ($colW[4] - 24) 24 $rc.stNote[0] 15 $script:SANS $script:MUTED 'LEFT' ''
    $o += Ts ('c4-s2' + $rc.id) ($colX[4] + 14) ($ry + 80) ($colW[4] - 24) 24 $rc.stNote[1] 15 $script:SANS $script:MUTED 'LEFT' ''
    # 截止
    $o += Ts ('c4-du' + $rc.id) ($colX[5] + 14) ($ry + 18) ($colW[5] - 24) 30 $rc.due 20 $script:MONO $script:PAPERW 'LEFT' ''
    $o += Ts ('c4-lf' + $rc.id) ($colX[5] + 14) ($ry + 48) ($colW[5] - 24) 26 $rc.left 16 $script:SANS $rc.stC 'LEFT' ''
    $o += (Box $tx ($ry + $rowH - 1) $TW 1 $script:HAIRD 0)
    $hy += $rowH
}
Guard 'case-04-table' $hy $H

# ---- bottom left: talking points ----
$BY = 646; $BH = 300
$o += (Card $M $BY 800 $BH $script:PANEL_D2 10 ('1 SOLID ' + $script:HAIRD) '')
$o += Ts 'c4-pt' ($M + 24) ($BY + 18) 500 30 '回应要点 · 给上门沟通的人' 21 $script:SANS $script:PAPERW 'LEFT' ''
$pts = @(
  @('1', '先给数字，再谈感受', '当场打开 288,000 元的分摊表，允许对方自己切换模型'),
  @('2', '不承诺没核实的事', '补贴以当地政策核定为准；本次未取得政策原文，不引用条款'),
  @('3', '把顾虑写成条目', '有负责人、有应对方案、有截止日期，下次上门先报进度')
)
$py = $BY + 60
foreach ($pt in $pts) {
    $o += (MarkDot ($M + 24) $py 26 $script:ACC $script:PANEL_D2)
    $o += Ts ('c4-pn' + $pt[0]) ($M + 24) $py 26 26 $pt[0] 17 $script:MONO $script:ACC 'CENTER' ''
    $o += Ts ('c4-ph' + $pt[0]) ($M + 62) ($py - 1) 700 28 $pt[1] 20 $script:SANS $script:PAPERW 'LEFT' ''
    $o += Ts ('c4-pd' + $pt[0]) ($M + 62) ($py + 26) 700 26 $pt[2] 17 $script:SANS $script:MUTED 'LEFT' ''
    $py += 78
}

# ---- bottom right: section motif ----
$QX = 872; $QW = 520
$o += (Card $QX $BY $QW $BH $script:PANEL_D2 10 ('1 SOLID ' + $script:HAIRD) '')
$o += Ts 'c4-st' ($QX + 24) ($BY + 18) 472 30 '楼栋剖面 · 仍有顾虑的 3 户' 21 $script:SANS $script:PAPERW 'LEFT' ''
$o += (SectionMini ($QX + 20) ($BY + 52) ($QW - 40) 200 $calc 'dark')
$lgy = $BY + 262
$o += (Pill ($QX + 20) $lgy '101' 16 $script:CORAL $script:WHITE $script:MONO)
$o += (Pill ($QX + 90) $lgy '202' 16 $script:CORAL $script:WHITE $script:MONO)
$o += (Pill ($QX + 160) $lgy '602' 16 $script:CORAL $script:WHITE $script:MONO)
$o += Ts 'c4-lg' ($QX + 240) $lgy 256 30 '其余 9 户已表态支持' 17 $script:SANS $script:MUTED 'LEFT' ''
Guard 'case-04' ($BY + $BH) $H

$f4 = '演示数据 DEMO · 顾虑、负责人与日期均为样例；补贴与政策口径未完成外部核验，画面不引用任何政策条款。'
$o += (Foot5 'c4' '04' $f4 $M 958 ($W - 2*$M) $script:HAIRD $script:MUTED)
Save 'case-04' (Page5 $W $H $script:BG_D $o) $W $H

# =====================================================================
# case-05 -- 造价与补贴构成 (1760 x 900, light, 居民大会超宽)
# =====================================================================
$W = 1760; $H = 900; $M = 56
$o = ''
$mh = Masthead5 '05' '居民大会 · 超宽' $M 40 ($W - 2*$M) $script:HAIRL $script:MUTEL $script:INK 20 20
$o += $mh[0]
$t5 = ((W1 $cost.grossWan) + ' 万元花在哪')
$o += Ts 'c5-title' $M 96 700 56 $t5 42 $script:DISP $script:INK 'LEFT' ''
$s5 = '方案甲 · 六项构成 · 三家报价同口径比较 · 补贴为演示数据，以当地政策核定为准'
$o += Ts 'c5-sub' $M 150 900 30 $s5 21 $script:SANS $script:MUTEL 'LEFT' ''
$o += Ts 'c5-net' ($M + $W - 2*$M - 560) 150 560 30 ('自付 ' + (W1 ($cost.net / 10000.0)) + ' 万元 = 造价 ' + (W1 $cost.grossWan) + ' ' + [char]0x2212 + ' 补贴 ' + (W1 $cost.subsidyWan)) 21 $script:MONO $script:ACC 'RIGHT' ''

# ---- column A: cost composition ----
$AX = $M; $AW = 700; $AY = 196; $AH = 620
$o += (Card $AX $AY $AW $AH $script:WHITE 12 ('1 SOLID ' + $script:HAIRL) '0 8 22 #15191F10')
$o += Ts 'c5-at' ($AX + 24) ($AY + 20) 500 30 '造价构成 · 方案甲（演示）' 21 $script:SANS $script:INK 'LEFT' ''
$stkC = @($script:ACC, $script:ACC2, $script:TEAL, $script:CORAL, $script:GREY, '#414C5A')
$stk = @()
for ($i = 0; $i -lt $cost.items.Count; $i++) {
    $stk += @{ v = $cost.items[$i].wan; c = $stkC[$i] }
}
$o += (Stack1 ($AX + 24) ($AY + 62) ($AW - 48) 44 $stk $cost.grossWan)
$iy = $AY + 128
for ($i = 0; $i -lt $cost.items.Count; $i++) {
    $it = $cost.items[$i]
    $pctS = ([string][math]::Round(100.0 * $it.wan / $cost.grossWan, 1)) + '%'
    $o += (Box ($AX + 24) ($iy + 6) 16 16 $stkC[$i] 4)
    $o += Ts ('c5-in' + $i) ($AX + 52) ($iy) 380 30 $it.name 19 $script:SANS $script:INK 'LEFT' ''
    $o += Ts ('c5-iv' + $i) ($AX + 436) ($iy) 130 30 ((W1 $it.wan) + ' 万') 20 $script:MONO $script:INK 'RIGHT' ''
    $o += Ts ('c5-ip' + $i) ($AX + 574) ($iy) 102 30 $pctS 19 $script:MONO $script:MUTEL 'RIGHT' ''
    $o += (Box ($AX + 24) ($iy + 36) ($AW - 48) 1 $script:HAIRL 0)
    $iy += 54
}
$o += (Box ($AX + 24) ($iy + 14) ($AW - 48) 62 $script:SHADE 8)
$c5n = '合计 52.8 万元；其中不可预见费 4.4 万元为预留，结算时按实际发生多退少补。'
$o += Ts 'c5-cn' ($AX + 38) ($iy + 26) ($AW - 76) 44 $c5n 17 $script:SANS $script:MUTEL 'LEFT' ''
$mets = @(
  @('每户平均造价', ((W1 ($cost.grossWan / 12.0)) + ' 万元')),
  @('折合每平方米', ((W1 ($cost.grossWan * 10000.0 / $calc.building.totalArea)) + ' 元/㎡')),
  @('补贴后每户', ((W1 ($cost.net / 120000.0)) + ' 万元'))
)
$mx = $AX + 24
foreach ($mt in $mets) {
    $o += Ts ('c5-mm' + $mt[0]) $mx 740 210 26 $mt[0] 16 $script:SANS $script:MUTEL 'LEFT' ''
    $o += Ts ('c5-mv' + $mt[0]) $mx 766 210 34 $mt[1] 22 $script:MONO $script:INK 'LEFT' ''
    $mx += 217
}
Guard 'case-05-a' 800 $H

# ---- column B: three quotes ----
$BX = 780; $BW = 560
$o += (Card $BX $AY $BW $AH $script:WHITE 12 ('1 SOLID ' + $script:HAIRL) '0 8 22 #15191F10')
$o += Ts 'c5-bt' ($BX + 24) ($AY + 20) 500 30 '三家报价 · 同口径比较（演示）' 21 $script:SANS $script:INK 'LEFT' ''
$bqX = @(($BX + 24), ($BX + 188), ($BX + 278), ($BX + 344), ($BX + 406), ($BX + 476))
$bqW = @(156, 84, 60, 56, 60, 60)
$bqH = @('供应商', '报价', '含迁改', '质保', '工期', '同口径')
$by = $AY + 62
$o += (Box ($BX + 24) $by ($BW - 48) 32 $script:SHADE 0)
for ($i = 0; $i -lt 6; $i++) {
    $al = 'LEFT'; if ($i -gt 0) { $al = 'RIGHT' }
    $hx = $bqX[$i]; if ($al -eq 'LEFT') { $hx = $bqX[$i] + 8 }
    $o += Ts ('c5-bh' + $i) $hx $by ($bqW[$i] - 8) 32 $bqH[$i] 16 $script:SANS $script:MUTEL $al ''
}
$by += 32
$qz = $cost.quotes
$qnote = @('同口径最低，已选定', '贵 2.8 万，质保 5 年', '另计迁改 3.6 万')
for ($i = 0; $i -lt 3; $i++) {
    $qq = $qz[$i]
    $best = ($qq.comparableWan -eq 52.8)
    if ($best) { $rb = '#FFF4EE' } else { $rb = $script:WHITE }
    $o += (Box ($BX + 24) $by ($BW - 48) 74 $rb 0)
    if ($best) { $o += (Box ($BX + 24) $by 5 74 $script:ACC 0) }
    $o += Ts ('c5-qv' + $i) ($bqX[0] + 8) ($by + 12) ($bqW[0] - 8) 30 $qq.vendor 19 $script:SANS $script:INK 'LEFT' ''
    $qw2 = $qnote[$i]
    $o += Ts ('c5-qs' + $i) ($bqX[0] + 8) ($by + 42) ($bqW[0] - 8) 26 $qw2 15 $script:SANS $script:MUTEL 'LEFT' ''
    $o += Ts ('c5-qa' + $i) $bqX[1] ($by + 22) $bqW[1] 30 ((W1 $qq.wan) + ' 万') 19 $script:MONO $script:INK 'RIGHT' ''
    if ($qq.inclPipe) { $pTxt = '含' } else { $pTxt = '不含' }
    $o += Ts ('c5-qb' + $i) $bqX[2] ($by + 22) $bqW[2] 30 $pTxt 17 $script:SANS $script:MUTEL 'RIGHT' ''
    $o += Ts ('c5-qc' + $i) $bqX[3] ($by + 22) $bqW[3] 30 $qq.warranty 17 $script:SANS $script:MUTEL 'RIGHT' ''
    $o += Ts ('c5-qd' + $i) $bqX[4] ($by + 22) $bqW[4] 30 ([string]$qq.days + ' 天') 17 $script:MONO $script:MUTEL 'RIGHT' ''
    $cq = (W1 $qq.comparableWan) + ' 万'
    $cqC = $script:INK; if ($best) { $cqC = $script:ACC }
    $o += Ts ('c5-qe' + $i) $bqX[5] ($by + 22) $bqW[5] 30 $cq 16 $script:MONO $cqC 'RIGHT' ''
    $o += (Box ($BX + 24) ($by + 73) ($BW - 48) 1 $script:HAIRL 0)
    $by += 74
}
$by += 22
$o += Ts 'c5-bc' ($BX + 24) $by 60 40 '结论' 20 $script:DISP $script:ACC 'LEFT' ''
$by += 30
$c5c1 = '同口径后甲方案 52.8 万最低；'
$c5c2 = '丙表面 49.9 万，但不含管线迁改'
$c5c3 = '3.6 万，同口径为 53.5 万。'
$o += Ts 'c5-c1' ($BX + 24) $by 512 26 $c5c1 18 $script:SANS $script:INK 'LEFT' ''
$o += Ts 'c5-c2' ($BX + 24) ($by + 26) 512 26 $c5c2 18 $script:SANS $script:INK 'LEFT' ''
$o += Ts 'c5-c3' ($BX + 24) ($by + 52) 512 26 $c5c3 18 $script:SANS $script:INK 'LEFT' ''
# delta chart: how far each quote sits above the lowest comparable price
$gy = 668
$o += Ts 'c5-dt' ($BX + 24) $gy 512 26 '与最低同口径的差额（万元）' 17 $script:SANS $script:MUTEL 'LEFT' ''
$gy += 32
$base5 = [double]$qz[0].comparableWan
for ($di = 0; $di -lt 3; $di++) {
    $dv = [double]$qz[$di].comparableWan - $base5
    $o += Ts ('c5-dn' + $di) ($BX + 24) $gy 160 26 $qz[$di].vendor 16 $script:SANS $script:INK 'LEFT' ''
    $o += (Box ($BX + 194) ($gy + 6) 270 14 $script:SHADE 7)
    if ($dv -gt 0.001) {
        $o += (Box ($BX + 194) ($gy + 6) (270.0 * ($dv / 3.0)) 14 $script:ACC 7)
    }
    $dvs = '0.0'
    if ($dv -gt 0.001) { $dvs = '+' + (W1 $dv) }
    $o += Ts ('c5-dv' + $di) ($BX + 472) $gy 64 26 $dvs 17 $script:MONO $script:ACC 'RIGHT' ''
    $gy += 32
}
Guard 'case-05-b' ($gy + 4) $H

# ---- column C: subsidy waterfall ----
$CX = 1364; $CW = 340
$o += (Card $CX $AY $CW $AH $script:WHITE 12 ('1 SOLID ' + $script:HAIRL) '0 8 22 #15191F10')
$o += Ts 'c5-ct' ($CX + 24) ($AY + 20) 292 30 '补贴与自付' 21 $script:SANS $script:INK 'LEFT' ''
$wf = @(
  @('总造价', $cost.grossWan, $script:GREY, '52.8'),
  @('补贴（演示）', $cost.subsidyWan, $script:TEAL, '-24.0'),
  @('自付', ($cost.net / 10000.0), $script:ACC, '28.8')
)
$wy = $AY + 66
$barMaxW = 260.0
foreach ($wfI in $wf) {
    $o += Ts ('c5-wl' + $wfI[0]) ($CX + 24) $wy 292 26 $wfI[0] 18 $script:SANS $script:MUTEL 'LEFT' ''
    $wy += 28
    $bwd = $barMaxW * ([double]$wfI[1] / $cost.grossWan)
    $o += (Box ($CX + 24) $wy 260 26 $script:SHADE 6)
    $o += (Box ($CX + 24) $wy $bwd 26 $wfI[2] 6)
    $o += Ts ('c5-wv' + $wfI[0]) ($CX + 24) ($wy + 32) 292 30 ($wfI[3] + ' 万元') 21 $script:MONO $script:INK 'RIGHT' ''
    $wy += 76
}
$o += (HR ($CX + 24) ($wy + 4) 292 1 $script:HAIRL)
$o += Ts 'c5-big' ($CX + 24) ($wy + 18) 292 74 '28.8' 60 $script:DISP $script:ACC 'LEFT' ''
$o += Ts 'c5-bu' ($CX + 176) ($wy + 50) 140 36 '万元' 24 $script:SANS $script:INK 'LEFT' ''
$y5n = $wy + 96
$o += Ts 'c5-n1' ($CX + 24) $y5n 292 26 '12 户自付区间 0 – 42,985 元' 17 $script:SANS $script:MUTEL 'LEFT' ''
$o += Ts 'c5-n2' ($CX + 24) ($y5n + 26) 292 46 '补贴以当地政策核定为准' 17 $script:SANS $script:CORAL 'LEFT' ''
$o += (HR ($CX + 24) 754 292 1 $script:HAIRL)
$o += Ts 'c5-cm' ($CX + 24) 764 292 30 ('每户平均 ' + (W1 ($cost.net / 120000.0)) + ' 万元') 19 $script:MONO $script:ACC 'LEFT' ''
Guard 'case-05-c' 794 $H
Guard 'case-05' ($AY + $AH) $H

$f5 = '演示数据 DEMO：造价、报价、工期、补贴均为样例，补贴金额以当地政策核定为准（本次未取得政策原文）。'
$o += (Foot5 'c5' '05' $f5 $M 836 ($W - 2*$M) $script:HAIRL $script:MUTEL)
Save 'case-05' (Page5 $W $H $script:BG_L $o) $W $H

# =====================================================================
# case-06 -- 签约与公示进度 (480 x 1040, dark, 手机)
# =====================================================================
$W = 480; $H = 1040; $M = 24
$o = ''
$o += (Box 0 0 $W 72 $script:PANEL_D 0)
$o += Ts 'c6-brand' $M 20 220 32 '同梯 TongTi' 21 $script:DISP $script:ACC 'LEFT' ''
$o += Ts 'c6-hdr' ($W - $M - 240) 22 240 30 '梧桐里 3 号楼' 18 $script:SANS $script:MUTED 'RIGHT' ''
$o += (HR 0 72 $W 1 $script:HAIRD)

$mh = Masthead5 '06' '居民端 · 手机' $M 92 ($W - 2*$M) $script:HAIRD $script:MUTED $script:PAPERW 18 18
$o += $mh[0]
$o += Ts 'c6-title' $M 146 ($W - 2*$M) 44 '流程到哪了' 34 $script:DISP $script:PAPERW 'LEFT' ''
$o += Ts 'c6-sub' $M 192 ($W - 2*$M) 26 '方案公示已完成，异议期进行中' 18 $script:SANS $script:MUTED 'LEFT' ''

# stage timeline
$stages = @(
  @('意愿征询', 'done', '2026-09-12 至 09-30', '支持 9 / 12', -1.0),
  @('方案公示', 'done', '2026-10-01 至 10-07', '公示 7 天，无异议件', -1.0),
  @('异议期',   'active', '2026-10-08 至 10-14', '第 1 天 / 共 7 天', (1.0/7.0)),
  @('业主签约', 'active', '2026-10-08 起', '已签约 7 / 12 户', (7.0/12.0)),
  @('备案与开工', 'todo', '预计 2026-10-20', '需 12 / 12 户签约后启动', -1.0)
)
$sc = @{ 'done' = $script:TEAL; 'active' = $script:ACC; 'todo' = $script:GREY }
$sy = 228; $sh = 76
for ($i = 0; $i -lt $stages.Count; $i++) {
    $sg = $stages[$i]
    $cc2 = $sc[$sg[1]]
    $stTxt = '未开始'; $stC2 = $script:GREY
    if ($sg[1] -eq 'done')   { $stTxt = '已完成'; $stC2 = $script:TEAL }
    if ($sg[1] -eq 'active') { $stTxt = '进行中'; $stC2 = $script:ACC }
    if ($i -lt ($stages.Count - 1)) { $o += (Box 53 ($sy + 24) 2 56 $script:HAIRD 0) }
    if ($sg[1] -eq 'done') {
        $o += (Circ 44 ($sy + 4) 20 $cc2 '')
        $o += (Tick 48 ($sy + 8) 12 $script:BG_D)
    } else {
        $o += (Circ 44 ($sy + 4) 20 $cc2 '')
        $o += (Circ 48 ($sy + 8) 12 $script:PANEL_D '')
        $o += (Circ 51 ($sy + 11) 6 $cc2 '')
    }
    $o += Ts ('c6-sn' + $i) 80 $sy 236 26 $sg[0] 20 $script:SANS $script:PAPERW 'LEFT' ''
    $o += Ts ('c6-ss' + $i) 340 $sy 116 26 $stTxt 17 $script:SANS $stC2 'RIGHT' ''
    $o += Ts ('c6-sd' + $i) 80 ($sy + 26) 376 22 $sg[2] 15 $script:MONO $script:MUTED 'LEFT' ''
    $o += Ts ('c6-se' + $i) 80 ($sy + 48) 376 22 $sg[3] 16 $script:SANS $cc2 'LEFT' ''
    if ($sg[4] -gt 0) { $o += (Prog 80 ($sy + 70) 376 6 $sg[4] $script:PANEL_D2 $cc2 999) }
    $sy += $sh
}

# 12-household grid
$gy = 620
$o += Ts 'c6-gt' $M $gy 240 28 '12 户签约状态' 19 $script:SANS $script:PAPERW 'LEFT' ''
$o += Ts 'c6-gs' ($W - $M - 200) $gy 200 28 ('已签约 ' + $att.signed + ' / 12') 17 $script:MONO $script:TEAL 'RIGHT' ''
$gy = 656
$gorder = @('101','102','201','202','301','302','401','402','501','502','601','602')
$gcw = 66; $gch = 46; $gdx = 72; $gdy = 54
for ($k = 0; $k -lt 12; $k++) {
    $uid = $gorder[$k]
    $u = @($calc.households | Where-Object { $_.id -eq $uid })[0]
    $gx = $M + (($k % 6) * $gdx)
    $gyy = $gy + ([math]::Floor($k / 6) * $gdy)
    $o += (Box $gx $gyy $gcw $gch (AttTint 'dark' $u.attitude) 6)
    $o += (Box $gx $gyy 5 $gch (AttColor $u.attitude) 0)
    $o += Ts ('c6-u' + $uid) ($gx + 13) ($gyy + 13) ($gcw - 18) 24 $uid 17 $script:MONO $script:PAPERW 'LEFT' ''
}
$o += Ts 'c6-lg' $M 762 432 24 '青 = 已签约 · 琥珀 = 已同意 · 珊瑚 = 有顾虑' 15 $script:SANS $script:MUTED 'LEFT' ''

# error state
$ey = 796
$o += (Card $M $ey 432 110 $script:PANEL_D2 10 ('1 SOLID ' + $script:CORAL) '')
$o += (Box ($M + 1) ($ey + 1) 5 108 $script:CORAL 0)
$o += Ts 'c6-et' ($M + 20) ($ey + 14) 300 30 '602 室提交失败' 20 $script:SANS $script:CORAL 'LEFT' ''
$o += Ts 'c6-ed' ($M + 20) ($ey + 44) 392 26 '授权书照片 7.3 MB，超过 5 MB 限制' 17 $script:SANS $script:PAPERW 'LEFT' ''
$o += Ts 'c6-eh' ($M + 20) ($ey + 70) 240 26 '请压缩后重试' 16 $script:SANS $script:MUTED 'LEFT' ''
$o += (Pill ($M + 336) ($ey + 62) '重试' 17 $script:CORAL $script:WHITE $script:SANS 18 34)

# success toast
$ty = 916
$o += (Card $M $ty 432 64 $script:TINTD['已签约'] 10 ('1 SOLID ' + $script:TEAL) '')
$o += (Circ ($M + 18) ($ty + 20) 24 $script:TEAL '')
$o += (Tick ($M + 22) ($ty + 24) 16 $script:WHITE)
$o += Ts 'c6-ot' ($M + 54) ($ty + 10) 350 28 '401 室签约提交成功' 19 $script:SANS $script:PAPERW 'LEFT' ''
$o += Ts 'c6-oc' ($M + 54) ($ty + 36) 350 24 '受理编号 WT3-20261008-07' 16 $script:MONO $script:MUTED 'LEFT' ''

$f6 = '演示数据 DEMO · 状态与编号均为样例。'
$o += (Foot5 'c6' '06' $f6 $M 992 ($W - 2*$M) $script:HAIRD $script:MUTED)
Guard 'case-06' 1032 $H
Save 'case-06' (Page5 $W $H $script:BG_D $o) $W $H

Report-Problems5
