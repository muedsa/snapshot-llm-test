# gen-b06-a.ps1 -- build case-01, case-02, case-03, case-04
# PS 5.1 traps respected: masthead result is $mh (never $m beside $M),
# every concatenation passed to a command is parenthesised, no inline `if`
# in argument position, no ?? or ternaries.
param([int]$Round = 1)
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $root 'tmp\run-20261002-220723-mimo\B06\lib-b06.ps1')

$calc = Get-Calc6

function OutPath([string]$cid) {
    return (Join-Path $script:B06TMP ("{0}\r{1:d2}.snapshot" -f $cid, $Round))
}
function Save([string]$cid, [string]$body, [int]$cw, [int]$ch) {
    Write-Dsl6 (OutPath $cid) $body
    $g = [regex]::Match($body, '<Container width="(\d+)" height="(\d+)"')
    if ($g.Groups[1].Value -ne [string]$cw -or $g.Groups[2].Value -ne [string]$ch) {
        throw "$cid canvas mismatch: expected ${cw}x${ch}, got $($g.Groups[1].Value)x$($g.Groups[2].Value)"
    }
    $pc = $script:PROBLEMS.Count
    $script:B06PROB = $script:B06PROB + $pc
    Write-Output ("  {0} r{1:d2}  {2}x{3}  {4} bytes  problems={5}" -f
        $cid, $Round, $g.Groups[1].Value, $g.Groups[2].Value,
        (Get-Item (OutPath $cid)).Length, $pc)
    if ($pc -gt 0) {
        $script:PROBLEMS | ForEach-Object { Write-Output ('       ! ' + $_) }
        $script:PROBLEMS.Clear()
    }
}
function Guard([string]$cid, [double]$bottom, [int]$HH) {
    if ($bottom -gt $HH) { Fail "$cid content bottom $bottom exceeds canvas height $HH" }
}
$script:B06PROB = 0

# =====================================================================
# case-01 -- 货架单价换算 (1680 x 1040, light)
# =====================================================================
$W = 1680; $H = 1040; $M = 56
$Wt = Tone6 'light'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$o = ''
$mh = Masthead6 '01' '超市货架 · 统一口径比价' $M 40 ($W - 2 * $M) $hair2 $subC $txtC 20 20
$o += $mh[0]
$o += Ts 'c1-t' $M 96 ($W - 2 * $M) 62 '同一格子里，价格不会自己对齐' 44 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c1-s' $M 160 1300 34 '把三种包装换算成同一个口径，最便宜的那一个会自己站出来' 21 $script:SANS $subC 'LEFT' ''
$o += Kicker 'c1-k' $M 206 1300 '三组商品 · 九个包装 · 口径分别是每 100g / 每 100ml / 每 100抽' 17 $script:SANS $subC

$cardW = 500.0; $cardGap = 34.0; $cardY = 248.0; $cardH = 470.0
$rowY = $cardY + 58; $rowH = 116.0
$gi = 0
foreach ($grp in $calc.case01.groups) {
    $cx = $M + ($gi * ($cardW + $cardGap))
    $gi++
    $o += (Card $cx $cardY $cardW $cardH $pan 10 ('1 SOLID ' + $hair) '')
    $o += Ts ('c1-gt' + $grp.key) ($cx + 20) ($cardY + 18) 330 32 $grp.title 21 $script:SANS $txtC 'LEFT' ''
    $uw = [int](TW $grp.unit 16) + 24
    $o += (Tag ($cx + $cardW - 20 - $uw) ($cardY + 16) $grp.unit 16 $script:SHADE6 $subC $script:SANS 12 30)

    $maxUp = 0.0
    foreach ($rw in $grp.rows) { if ([double]$rw.unitPrice -gt $maxUp) { $maxUp = [double]$rw.unitPrice } }
    if ($maxUp -le 0) { $maxUp = 1.0 }

    $ri = 0
    foreach ($rw in $grp.rows) {
        $ry = $rowY + ($ri * $rowH)
        $ri++
        $isBest = ([double]$rw.unitPrice -eq ($grp.rows | ForEach-Object { [double]$_.unitPrice } | Sort-Object | Select-Object -First 1))
        $col = $script:PRICEAMT
        $bestTxt = $subC
        if ($isBest) { $col = $script:PRICELIME; $bestTxt = $script:PRICELIME }
        $o += Ts ('c1-p' + $ri + $grp.key) ($cx + 20) ($ry + 6) 270 30 $rw.pack 20 $script:SANS $txtC 'LEFT' ''
        $prTxt = [string]('¥' + ([double]$rw.price).ToString('0.00'))
        $o += Ts ('c1-v' + $ri + $grp.key) ($cx + 300) ($ry + 2) 180 34 $prTxt 25 $script:DISP $txtC 'RIGHT' ''
        $o += (Box ($cx + 20) ($ry + 52) 460 14 $script:SHADE6 7)
        $bw = 460.0 * ([double]$rw.unitPrice / $maxUp)
        if ($bw -lt 8) { $bw = 8.0 }
        $o += (Box ($cx + 20) ($ry + 52) $bw 14 $col 7)
        $o += Ts ('c1-u' + $ri + $grp.key) ($cx + 20) ($ry + 74) 300 28 $rw.unitPriceText 19 $script:MONO $bestTxt 'LEFT' ''
        $stTxt = ('心算 ' + $rw.mentalSteps + ' 步')
        $o += Ts ('c1-n' + $ri + $grp.key) ($cx + 360) ($ry + 76) 120 26 $stTxt 16 $script:SANS $subC 'RIGHT' ''
        $o += (HR ($cx + 20) ($ry + 106) 460 1 $hair)
    }

    if ($grp.disagree) {
        $o += (Box ($cx + 20) ($cardY + 412) 460 40 $script:SHADE6 8)
        $o += (Box ($cx + 20) ($cardY + 412) 5 40 $script:PRICELIME 0)
        $o += Ts ('c1-b' + $grp.key) ($cx + 36) ($cardY + 418) 430 30 '总价最便宜的，不是单价最便宜的' 17 $script:SANS $txtC 'LEFT' ''
    }
}
Guard 'case-01-cards' ($cardY + $cardH) $H

# ---- bottom: the mental arithmetic, then the verdict ----
$BY = 770.0; $BH = 170.0
$o += (Card $M $BY 1000 $BH $pan 10 ('1 SOLID ' + $hair) '')
$o += Ts 'c1-bt' ($M + 22) ($BY + 16) 600 30 '现场心算要几步 · 以 1.2kg 装为例' 19 $script:SANS $txtC 'LEFT' ''
$steps1 = @(
    @{ n = 1; s = '1.2kg → 1200g' }
    @{ n = 2; s = '118 ÷ 1200 = 0.09833' }
    @{ n = 3; s = '× 100 = 9.83' }
)
$sx = $M + 22
foreach ($st1 in $steps1) {
    $o += (Step6 $sx ($BY + 62) 36 $st1.n $script:PHARM $script:WHITE)
    $o += Ts ('c1-st' + $st1.n) ($sx + 46) ($BY + 66) 250 30 $st1.s 18 $script:MONO $txtC 'LEFT' ''
    $sx += 320
}
$o += Ts 'c1-res' ($M + 22) ($BY + 112) 400 40 '= 9.83 元 / 100g' 27 $script:MONO $script:PRICELIME 'LEFT' ''
$o += Ts 'c1-resn' ($M + 420) ($BY + 118) 560 30 '货架上这一步通常要心算两到三步' 17 $script:SANS $subC 'LEFT' ''

$o += (Card 1090 $BY 534 $BH $pan 10 ('1 SOLID ' + $hair) '')
$o += Ts 'c1-vt' 1112 ($BY + 16) 460 30 '这组货架告诉我们什么' 19 $script:SANS $txtC 'LEFT' ''
$v1 = '九个包装里，三组的"总价冠军"都不是"单价冠军"'
$v2 = '差价最大的一组，贵的比便宜的贵 30.4%'
$v3 = '口径统一之前，货架上的价格没法直接比'
$o += Ts 'c1-v1' 1112 ($BY + 54) 490 28 $v1 17 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c1-v2' 1112 ($BY + 86) 490 28 $v2 17 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c1-v3' 1112 ($BY + 118) 490 28 $v3 17 $script:SANS $subC 'LEFT' ''
Guard 'case-01-bottom' ($BY + $BH) $H

$o += (Src6 '01' '明码标价检索摘要（《明码标价和禁止价格欺诈规定》，二手来源，2026-10-08 抓取）；价格与规格为演示数据 DEMO' $M 952 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '01' '换算口径一致之后，三组商品的"最便宜"没有一个是同一个包装' $M 986 ($W - 2 * $M) $hair $subC)
Guard 'case-01-foot' 1026 $H
Save 'case-01' (Page6 $W $H $shell $o) $W $H

# =====================================================================
# case-02 -- 用药说明卡 (540 x 1240, light)
# =====================================================================
$W = 540; $H = 1240; $M = 32
$Wt = Tone6 'light'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$o = ''
$mh = Masthead6 '02' '说明书重写' $M 28 ($W - 2 * $M) $hair2 $subC $txtC 15 15
$o += $mh[0]
$o += Ts 'c2-t' $M 68 ($W - 2 * $M) 44 '一天三片，什么时候吃' 30 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c2-s' $M 114 ($W - 2 * $M) 26 ('把 ' + $calc.case02.brand + ' 的说明书压成一张看得完的卡') 15 $script:SANS $subC 'LEFT' ''
$o += Kicker 'c2-k' $M 146 ($W - 2 * $M) '一、今天已经吃了几片' 17 $script:SANS $script:PHARM

# ---- timeline ----
$TY = 176.0; $TH = 170.0
$o += (Card $M $TY ($W - 2 * $M) $TH $pan 10 ('1 SOLID ' + $hair) '')
$ax0 = $M + 40; $ax1 = $W - $M - 40; $axY = $TY + 96
$o += (HLine $ax0 $axY ($ax1 - $ax0) 3 $script:SHADE6)
$tks = $calc.case02.times
$nT = @($tks).Count
for ($i = 0; $i -lt $nT; $i++) {
    $f = ($i + 0.5) / $nT
    $cxa = $ax0 + (($ax1 - $ax0) * $f)
    $taken = ($i -lt [int]$calc.case02.todayTaken)
    if ($taken) {
        $o += (Circ ($cxa - 22) ($axY - 22) 44 $script:DOSE '')
    } else {
        $o += (Circ ($cxa - 22) ($axY - 22) 44 $script:PHARM '')
        $o += (Circ ($cxa - 18) ($axY - 18) 36 $pan '')
    }
    $mk = '待服'
    $mkC = $subC
    if ($taken) { $mk = '已服'; $mkC = $script:DOSE }
    $tm = $tks[$i]
    $o += Ts ('c2-h' + $i) ($cxa - 60) ($TY + 40) 120 30 $tm 20 $script:MONO $txtC 'CENTER' ''
    $o += Ts ('c2-m' + $i) ($cxa - 60) ($axY + 32) 120 26 $mk 16 $script:SANS $mkC 'CENTER' ''
}
$o += Ts 'c2-cnt' ($M + 20) ($TY + 14) 240 30 ('今日 ' + $calc.case02.todayTaken + ' / ' + $calc.case02.frequency + ' 已服') 20 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c2-next' ($W - $M - 260) ($TY + 16) 240 28 ('下一次 ' + $tks[1]) 18 $script:MONO $script:PHARM 'RIGHT' ''

# ---- Q&A cards ----
$o += Kicker 'c2-k2' $M 360 ($W - 2 * $M) '二、四个最常被问的问题' 17 $script:SANS $script:PHARM
$qa = @(
    @{ q = '漏服了怎么办？'; a = $calc.case02.missedRule; c = $script:PHARM }
    @{ q = '什么时候吃？';   a = $calc.case02.withMeal;   c = $script:DOSE }
    @{ q = '不能和什么一起吃？'; a = $calc.case02.avoid; c = $script:CORAL6 }
    @{ q = '放在哪里？';     a = $calc.case02.store;      c = $script:PRICELIME }
)
$qy = 386.0; $qh = 118.0; $qg = 8.0
$qi = 0
foreach ($it in $qa) {
    $qy2 = $qy + ($qi * ($qh + $qg))
    $qi++
    $o += (Card $M $qy2 ($W - 2 * $M) $qh $pan 10 ('1 SOLID ' + $hair) '')
    $o += (Box $M $qy2 5 $qh $it.c 0)
    $o += Ts ('c2-q' + $qi) ($M + 20) ($qy2 + 14) 440 30 $it.q 20 $script:SANS $txtC 'LEFT' ''
    $lines2 = WrapTW $it.a 440 15
    $ly = $qy2 + 48
    $li = 0
    foreach ($ln in $lines2) {
        if ($li -ge 3) { break }
        $o += Ts ('c2-a' + $qi + '-' + $li) ($M + 20) ($ly + ($li * 21)) 440 22 $ln 15 $script:SANS $subC 'LEFT' ''
        $li++
    }
}
Guard 'case-02-qa' ($qy + (4 * $qh) + (3 * $qg)) $H

# ---- week grid ----
$GY = 890.0
$o += Kicker 'c2-k3' $M $GY ($W - 2 * $M) '三、一周服药格 · 7 天 x 3 次 = 21 格' 17 $script:SANS $script:PHARM
$gx0 = $M; $gw = $W - 2 * $M
$cw2 = ($gw - (6 * 8)) / 7.0
$days = @('周一', '周二', '周三', '周四', '周五', '周六', '周日')
for ($k = 0; $k -lt 7; $k++) {
    $xx = $gx0 + ($k * ($cw2 + 8))
    $o += Ts ('c2-d' + $k) $xx 926 $cw2 24 $days[$k] 14 $script:SANS $subC 'CENTER' ''
}
$gy0 = 954.0; $chH = 36.0
$slots = @('早', '中', '晚')
for ($r2 = 0; $r2 -lt 3; $r2++) {
    for ($k = 0; $k -lt 7; $k++) {
        $xx = $gx0 + ($k * ($cw2 + 8))
        $yy = $gy0 + ($r2 * ($chH + 6))
        $cc = $script:SHADE6
        if ($r2 -eq 0 -and $k -eq 0) { $cc = $script:DOSE }
        $o += (Box $xx $yy $cw2 $chH $cc 6)
        $tc = $script:INK6
        if ($r2 -eq 0 -and $k -eq 0) { $tc = $script:WHITE }
        $o += Ts ('c2-s' + $r2 + '-' + $k) $xx ($yy + 8) $cw2 24 $slots[$r2] 15 $script:SANS $tc 'CENTER' ''
    }
}
$note2a = '实心金 = 已服 · 蓝色空心 = 待服；下方药格同色'
$note2b = '用法用量以医生处方与药品说明书为准；演示卡片，不构成用药建议'
$o += Ts 'c2-note' $M 1084 ($W - 2 * $M) 24 $note2a 15 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c2-note2' $M 1108 ($W - 2 * $M) 24 $note2b 14 $script:SANS $subC 'LEFT' ''
Guard 'case-02-note' 1132 $H
$o += (Src6 '02' '见 requests.jsonl res-27 · 自拟演示样例 DEMO' $M 1138 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '02' '把 4 段说明压成 4 张问答卡 + 21 格服药格' $M 1186 ($W - 2 * $M) $hair $subC)
Guard 'case-02-foot' 1226 $H
Save 'case-02' (Page6 $W $H $shell $o) $W $H

# =====================================================================
# case-03 -- 体检报告行动清单 (1440 x 1080, dark)
# =====================================================================
$W = 1440; $H = 1080; $M = 56
$Wt = Tone6 'dark'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$o = ''
$mh = Masthead6 '03' '体检报告 · 参考区间到动作' $M 40 ($W - 2 * $M) $hair2 $subC $txtC 20 20
$o += $mh[0]
$o += Ts 'c3-t' $M 96 ($W - 2 * $M) 62 '箭头要落到一件有截止时间的事' 44 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c3-s' $M 160 1200 34 '六项指标，三项出界；出界的三项各自对应一件事和一个时间' 21 $script:SANS $subC 'LEFT' ''

$lg3 = Legend6 $M 204 @(
    @{ c = $script:JADE; t = '在参考区间内' }
    @{ c = $script:AMBER6; t = '略偏，3 个月后复查' }
    @{ c = $script:CORAL6; t = '要尽快复测' }
) 17 $txtC $script:SANS
$o += $lg3[0]
$o += Ts 'c3-lgn' ($lg3[1] + 34) 204 700 30 '浅色带 = 参考区间 · 竖线圆点 = 本次实测值' 16 $script:SANS $subC 'LEFT' ''

$BANDC = '#F1EEE740'
$LX = $M; $LW = 860.0; $RY = 250.0; $RH = 116.0; $RG = 6.0
$ri3 = 0
foreach ($row in $calc.case03.rows) {
    $ry3 = $RY + ($ri3 * ($RH + $RG))
    $ri3++
    $cc = $script:JADE
    if ($row.level -eq 1) { $cc = $script:AMBER6 }
    if ($row.level -eq 2) { $cc = $script:CORAL6 }
    $o += (Card $LX $ry3 $LW $RH $pan 8 ('1 SOLID ' + $hair) '')
    $o += (Box $LX $ry3 5 $RH $cc 0)
    $o += Ts ('c3-n' + $ri3) ($LX + 18) ($ry3 + 6) 190 30 $row.name 20 $script:SANS $txtC 'LEFT' ''
    $rt = ($row.rangeText + ' ' + $row.unit)
    $o += Ts ('c3-r' + $ri3) ($LX + 18) ($ry3 + 38) 190 24 $rt 15 $script:MONO $subC 'LEFT' ''
    $o += Ts ('c3-v' + $ri3) ($LX + 18) ($ry3 + 66) 190 34 (LabN $row.val) 24 $script:MONO $cc 'LEFT' ''
    $rl = Ruler6 ('c3-rl' + $ri3) ($LX + 226) ($ry3 + 56) 560 ([double]$row.scaleLo) ([double]$row.scaleHi) ([double]$row.step) ([double]$row.lo) ([double]$row.hi) ([double]$row.val) $script:PANELD6b $BANDC $script:HAIRD6b $cc 14 14
    $o += $rl[0]
    $stTxt = $row.status
    $sw = [int](TW $stTxt 15) + 24
    $o += (Tag ($LX + $LW - 18 - $sw) ($ry3 + 14) $stTxt 15 $cc $script:DARK6 $script:SANS 12 28)
}
Guard 'case-03-rows' ($RY + (6 * ($RH + $RG))) $H

# ---- right: the actions ----
$AX = 950.0; $AW = 434.0
$o += (Card $AX $RY $AW (6 * ($RH + $RG)) $pan 8 ('1 SOLID ' + $hair) '')
$o += Ts 'c3-at' ($AX + 22) ($RY + 18) 380 30 '把三个箭头翻译成三件事' 20 $script:SANS $txtC 'LEFT' ''
$acts = @()
foreach ($row in $calc.case03.rows) { if ($row.level -gt 0) { $acts += $row } }
$ay = $RY + 66.0; $ah = 158.0; $ag = 16.0
$ai = 0
foreach ($ac in $acts) {
    $ay2 = $ay + ($ai * ($ah + $ag))
    $ai++
    $cc = $script:AMBER6
    if ($ac.level -eq 2) { $cc = $script:CORAL6 }
    $o += (Box ($AX + 22) $ay2 390 $ah $script:PANELD6b 8)
    $o += (Box ($AX + 22) $ay2 5 $ah $cc 0)
    $o += (Step6 ($AX + 42) ($ay2 + 18) 40 $ai $cc $script:DARK6)
    $o += Ts ('c3-an' + $ai) ($AX + 94) ($ay2 + 22) 300 30 $ac.name 20 $script:SANS $txtC 'LEFT' ''
    $o += Ts ('c3-av' + $ai) ($AX + 42) ($ay2 + 70) 350 26 ((LabN $ac.val) + ' / ' + $ac.rangeText + ' ' + $ac.unit) 16 $script:MONO $subC 'LEFT' ''
    $o += Ts ('c3-aa' + $ai) ($AX + 42) ($ay2 + 98) 350 26 $ac.action 16 $script:SANS $txtC 'LEFT' ''
    $awTxt = ('时间 ' + $ac.when)
    $o += Ts ('c3-atm' + $ai) ($AX + 42) ($ay2 + 126) 350 24 $awTxt 15 $script:MONO $cc 'LEFT' ''
}
$np3 = PPara 'c3-note' ($AX + 22) ($ay + (3 * ($ah + $ag)) + 10) 390 '把报告标记翻译成动作只是演示；复查时间与项目以医生意见为准。' 14 21 $script:SANS $subC ''
$o += $np3[0]
# the three that need nothing now -- keeps the right column from ending in dead air
$okRows = @()
foreach ($row in $calc.case03.rows) { if ($row.level -eq 0) { $okRows += $row.name } }
$o += (HR ($AX + 22) 900 390 1 $hair)
$o += Ts 'c3-okt' ($AX + 22) 914 390 26 '这次不用动的 3 项' 16 $script:SANS $subC 'LEFT' ''
$o += Ts 'c3-okv' ($AX + 22) 942 390 30 ([string]::Join('  ·  ', $okRows)) 17 $script:SANS $script:JADE 'LEFT' ''
Guard 'case-03-right' 974 $H

$o += (Src6 '03' '参考区间检索摘要（WS/T 参考区间标准与术语，二手来源，2026-10-08 抓取）；数值为演示数据 DEMO' $M 982 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '03' ('正常 ' + $calc.case03.stat.normal + ' 项 · 3 个月复查 ' + $calc.case03.stat.recheck + ' 项 · 尽快复测 ' + $calc.case03.stat.sooner + ' 项') $M 1010 ($W - 2 * $M) $hair $subC)
Guard 'case-03-foot' 1050 $H
Save 'case-03' (Page6 $W $H $shell $o) $W $H

# =====================================================================
# case-04 -- 电费阶梯账单 (1760 x 980, light)
# =====================================================================
$W = 1760; $H = 980; $M = 56
$Wt = Tone6 'light'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$el = $calc.case04
$o = ''
$mh = Masthead6 '04' '电费账单 · 分档与归因' $M 40 ($W - 2 * $M) $hair2 $subC $txtC 20 20
$o += $mh[0]
$o += Ts 'c4-t' $M 96 ($W - 2 * $M) 62 (('多用了 ' + (D1 $el.deltaKwhPct) + '% 的电，多花了 ' + (D1 $el.deltaCostPct) + '% 的钱')) 44 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c4-s' $M 160 1300 34 '差额不是"电变贵了"，是本期有 76 度落在了第三档' 21 $script:SANS $subC 'LEFT' ''

$kpi4 = @(
    @{ lb = '本期用电'; big = ((D0 $el.cur.kwh) + ' 度'); un = ('上期 ' + (D0 $el.prev.kwh) + ' 度 · +' + (D1 $el.deltaKwhPct) + '%'); cc = $script:ELEC }
    @{ lb = '本期电费'; big = ((D2 $el.cur.cost) + ' 元'); un = ('上期 ' + (D2 $el.prev.cost) + ' 元 · +' + (D1 $el.deltaCostPct) + '%'); cc = $script:JUMP }
    @{ lb = '综合均价'; big = (([double]$el.cur.rate).ToString('0.0000') + ' 元'); un = ('上期 ' + ([double]$el.prev.rate).ToString('0.0000') + ' 元 · +' + (D1 $el.ratePct) + '%'); cc = $script:CORAL6 }
    @{ lb = '落在第三档'; big = ((D0 76) + ' 度'); un = ('占多花钱的 ' + (D1 $el.tier3Share) + '%'); cc = $script:CORAL6 }
)
$kx = $M; $kw = 394.0
foreach ($kp in $kpi4) {
    $o += (Card $kx 210 $kw 140 $pan 10 ('1 SOLID ' + $hair) '')
    $o += (Box $kx 210 5 140 $kp.cc 0)
    $o += Ts ('c4-lb' + $kp.lb) ($kx + 20) 228 350 28 $kp.lb 19 $script:SANS $subC 'LEFT' ''
    $o += Ts ('c4-bg' + $kp.lb) ($kx + 20) 258 350 46 $kp.big 36 $script:DISP $kp.cc 'LEFT' ''
    $o += Ts ('c4-un' + $kp.lb) ($kx + 20) 310 350 26 $kp.un 16 $script:SANS $subC 'LEFT' ''
    $kx += ($kw + 24)
}

# ---- left panel: how 356 kWh splits across the three tiers ----
$LY = 380.0; $LH = 460.0
$o += (Card $M $LY 812 $LH $pan 10 ('1 SOLID ' + $hair) '')
$o += Ts 'c4-lt' ($M + 22) ($LY + 18) 600 30 '两期用电分别落在哪几档' 21 $script:SANS $txtC 'LEFT' ''
$splitBarX = $M + 22; $splitBarW = 768.0
$tcol = @($script:ELEC, $script:JUMP, $script:CORAL6)

function Tier-Bar([double]$bx, [double]$by, [double]$bw, [double]$total, [object]$split, [double]$maxTotal) {
    $out = ''; $xx = $bx
    $scale = $maxTotal
    if ($scale -le 0) { $scale = $total }
    $barLen = $bw * ($total / $scale)
    for ($k = 0; $k -lt @($split).Count; $k++) {
        $segW = $barLen * ([double]$split[$k].kwh / $total)
        if ($segW -gt 0) { $out += (Box $xx $by $segW 40 $script:tcol[$k] 0) }
        $xx += $segW
    }
    $out += (Outline $bx $by $barLen 40 $hair 2)
    return $out
}
$o += Ts 'c4-pp' $splitBarX ($LY + 62) 60 26 '上期' 17 $script:SANS $subC 'LEFT' ''
$o += (Tier-Bar ($splitBarX + 70) ($LY + 58) 500 ([double]$el.prev.kwh) $el.prev.split ([double]$el.cur.kwh))
$o += Ts 'c4-pv' ($splitBarX + 586) ($LY + 62) 182 26 ((D0 $el.prev.kwh) + ' 度 · ' + (D2 $el.prev.cost) + ' 元') 17 $script:MONO $txtC 'RIGHT' ''
$o += Ts 'c4-cp' $splitBarX ($LY + 118) 60 26 '本期' 17 $script:SANS $subC 'LEFT' ''
$o += (Tier-Bar ($splitBarX + 70) ($LY + 114) 500 ([double]$el.cur.kwh) $el.cur.split ([double]$el.cur.kwh))
$o += Ts 'c4-cv' ($splitBarX + 586) ($LY + 118) 182 26 ((D0 $el.cur.kwh) + ' 度 · ' + (D2 $el.cur.cost) + ' 元') 17 $script:MONO $txtC 'RIGHT' ''

$ry4 = $LY + 186.0
$o += (HR $splitBarX $ry4 $splitBarW 1 $hair)
$ry4 += 14
$hdr4 = @(
    @{ a = '档位'; x = 26; w = 124; al = 'LEFT' }
    @{ a = '本期电量'; x = 170; w = 150; al = 'LEFT' }
    @{ a = '单价'; x = 340; w = 150; al = 'LEFT' }
    @{ a = '本期金额'; x = 560; w = 208; al = 'RIGHT' }
)
foreach ($hd in $hdr4) { $o += Ts ('c4-hd' + $hd.a) ($splitBarX + $hd.x) $ry4 $hd.w 24 $hd.a 15 $script:SANS $subC $hd.al '' }
$ry4 += 30
foreach ($row4 in @($el.cur.split)) {
    $col4 = $script:ELEC
    if ($row4.name -eq '第 2 档') { $col4 = $script:JUMP }
    if ($row4.name -eq '第 3 档') { $col4 = $script:CORAL6 }
    $o += (Box $splitBarX ($ry4 + 6) 16 16 $col4 3)
    $o += Ts ('c4-tn' + $row4.name) ($splitBarX + 26) $ry4 144 28 $row4.name 18 $script:SANS $txtC 'LEFT' ''
    $o += Ts ('c4-tk' + $row4.name) ($splitBarX + 170) $ry4 150 28 ((D0 $row4.kwh) + ' 度') 19 $script:MONO $txtC 'LEFT' ''
    $o += Ts ('c4-tr' + $row4.name) ($splitBarX + 340) $ry4 150 28 ((D4 $row4.rate) + ' 元') 17 $script:MONO $subC 'LEFT' ''
    $o += Ts ('c4-tc' + $row4.name) ($splitBarX + 560) $ry4 208 28 ((D2 $row4.cost) + ' 元') 19 $script:MONO $col4 'RIGHT' ''
    $ry4 += 44
}
$o += (HR $splitBarX $ry4 $splitBarW 1 $hair)
$o += Ts 'c4-ln' $splitBarX ($ry4 + 16) $splitBarW 28 '上期 220 度 = 第 1 档 190 度 + 第 2 档 30 度，第三档为 0 度。' 17 $script:SANS $subC 'LEFT' ''
$o += Ts 'c4-ln2' $splitBarX ($ry4 + 46) $splitBarW 28 '本期第 1 档没变，变的是第 2 档，以及凭空多出来的第 3 档。' 17 $script:SANS $subC 'LEFT' ''
Guard 'case-04-left' ($LY + $LH) $H

# ---- right panel: where the extra 105.77 came from ----
$RXX = 892.0
$o += (Card $RXX $LY 812 $LH $pan 10 ('1 SOLID ' + $hair) '')
$o += Ts 'c4-rt' ($RXX + 22) ($LY + 18) 600 30 ('多花的 ' + (D2 $el.deltaCost) + ' 元从哪来') 21 $script:SANS $txtC 'LEFT' ''
$attrBarX = $RXX + 22; $attrBarW = 768.0; $attrBarY = $LY + 66
$w2 = $attrBarW * ([double]$el.attribution[1].addCost / [double]$el.deltaCost)
$w3 = $attrBarW - $w2
$o += (Box $attrBarX $attrBarY $w2 56 $script:JUMP 0)
$o += (Box ($attrBarX + $w2) $attrBarY $w3 56 $script:CORAL6 0)
$o += Ts 'c4-a1' ($attrBarX + 16) ($attrBarY + 14) ($w2 - 32) 32 ((D1 $el.tier2Share) + '%') 26 $script:DISP $script:WHITE 'LEFT' ''
$o += Ts 'c4-a2' ($attrBarX + $w2 + 16) ($attrBarY + 14) ($w3 - 32) 32 ((D1 $el.tier3Share) + '%') 26 $script:DISP $script:WHITE 'LEFT' ''
$ay4 = $attrBarY + 84.0
$o += (Box $attrBarX ($ay4 + 6) 16 16 $script:JUMP 3)
$o += Ts 'c4-ab2' ($attrBarX + 30) $ay4 500 30 (('第 2 档多出 60 度 x ' + (D4 $el.attribution[1].rate) + ' = ' + (D2 $el.attribution[1].addCost) + ' 元')) 18 $script:MONO $txtC 'LEFT' ''
$o += (Box $attrBarX ($ay4 + 52) 16 16 $script:CORAL6 3)
$o += Ts 'c4-ab3' ($attrBarX + 30) ($ay4 + 46) 500 30 (('第 3 档新增 76 度 x ' + (D4 $el.attribution[2].rate) + ' = ' + (D2 $el.attribution[2].addCost) + ' 元')) 18 $script:MONO $txtC 'LEFT' ''
$o += (HR $attrBarX ($ay4 + 100) $attrBarW 1 $hair)
$o += Ts 'c4-sum' $attrBarX ($ay4 + 116) $attrBarW 34 (('合计 ' + (D2 $el.deltaCost) + ' 元 · 归因校验 ' + (D2 $el.attributionCheck) + ' 元')) 20 $script:MONO $txtC 'LEFT' ''
$o += (Box $attrBarX ($ay4 + 166) $attrBarW 96 $script:SHADE6 8)
$o += Ts 'c4-hint' ($attrBarX + 20) ($ay4 + 182) ($attrBarW - 40) 28 '把「多用了多少度」和「跨了几档」分开看，账单才对得上。' 18 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c4-hint2' ($attrBarX + 20) ($ay4 + 212) ($attrBarW - 40) 28 '多用的 136 度里，有 76 度落在单价最高的第三档。' 18 $script:SANS $subC 'LEFT' ''
Guard 'case-04-right' ($LY + $LH) $H

$o += (Src6 '04' $el.note $M 860 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '04' (('电费涨幅（+' + (D1 $el.deltaCostPct) + '%）高于用电涨幅（+' + (D1 $el.deltaKwhPct) + '%），差值全部来自跳档')) $M 896 ($W - 2 * $M) $hair $subC)
Guard 'case-04-foot' 936 $H
Save 'case-04' (Page6 $W $H $shell $o) $W $H

if ($script:B06PROB -eq 0) { Write-Output 'total problems = 0' }
else { Write-Output ('total problems = ' + $script:B06PROB) }
