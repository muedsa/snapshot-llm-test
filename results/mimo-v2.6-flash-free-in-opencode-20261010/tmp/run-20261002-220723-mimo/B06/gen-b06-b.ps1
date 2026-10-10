# gen-b06-b.ps1 -- build case-05, case-06, case-07
# PS 5.1 traps respected: masthead result is $mh (never $m beside $M), no local may be
# named $L beside a $l parameter, every concatenation passed to a command is
# parenthesised, no inline `if` in argument position, no ?? or ternaries.
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
# case-05 -- 站台到发与换乘 (1920 x 620, dark)
# signage, not an article: no display headline, the countdown is the hero
# =====================================================================
$c5 = $calc.case05
$W = 1920; $H = 620; $M = 56
$Wt = Tone6 'dark'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$o = ''
$mh = Masthead6 '05' '地铁站台 · 到发与换乘' $M 32 ($W - 2 * $M) $hair2 $subC $txtC 18 18
$o += $mh[0]

$CY = [double]$mh[1]; $CH = 430.0
$colLX = 56.0;   $colLW = 590.0
$colMX = 676.0;  $colMW = 660.0
$colRX = 1366.0; $colRW = 498.0

# ---- left: line roundel, direction, hero countdown ----
$o += (Card $colLX $CY $colLW $CH $pan 10 ('1 SOLID ' + $hair) '')
$o += (Box ($colLX + 24) 104 64 64 $script:LINERED 14)
$o += Ts 'c5-num' ($colLX + 24) 110 64 48 '3' 40 $script:DISP '#FFFFFF' 'CENTER' ''
$o += Ts 'c5-dir' ($colLX + 104) 104 340 46 $c5.dir 34 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c5-sub' ($colLX + 104) 152 340 32 ($c5.line + ' · 6 节编组') 20 $script:SANS $subC 'LEFT' ''
$ptTxt = [string]$c5.platform
$ptW = [int](TW $ptTxt 18) + 24
$o += (Tag ($colLX + $colLW - 24 - $ptW) 112 $ptTxt 18 $script:LINERED '#FFFFFF' $script:SANS 12 40)
$o += (HR ($colLX + 24) 200 ($colLW - 48) 1 $hair)
$o += (Box ($colLX + 12) 214 ($colLW - 24) 272 $script:PANELD6b 10)

$o += Kicker 'c5-k' ($colLX + 24) 224 300 '首班车还有' 20 $script:SANS $subC
$o += Ts 'c5-big' ($colLX + 24) 254 130 130 ([string]($c5.trains[0].min)) 112 $script:DISP $script:LINEORG 'LEFT' ''
$o += Ts 'c5-unit' ($colLX + 120) 336 150 46 '分钟' 34 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c5-eta' ($colLX + 24) 396 540 36 (($c5.trains[0].eta + ' 到站 · 现在 ' + $c5.now)) 26 $script:MONO $txtC 'LEFT' ''
$o += Ts 'c5-last' ($colLX + 24) 444 540 32 $c5.nextLast 21 $script:SANS $script:LINEORG 'LEFT' ''
Guard 'case-05-left' 476 508

# ---- middle: three upcoming trains, wait bars on one shared scale ----
$o += (Card $colMX $CY $colMW $CH $pan 10 ('1 SOLID ' + $hair) '')
$o += Ts 'c5-mt' ($colMX + 24) 100 300 34 '接下来三班' 22 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c5-mh' ($colMX + 300) 104 336 28 ('横条长度 = 等待分钟数 · 现在 ' + $c5.now) 17 $script:SANS $subC 'RIGHT' ''
$mxMax = 0
foreach ($tn in $c5.trains) { if ([int]$tn.min -gt $mxMax) { $mxMax = [int]$tn.min } }
if ($mxMax -le 0) { $mxMax = 1 }
$rowIdx = 0
foreach ($tn in $c5.trains) {
    $ry = 142.0 + ($rowIdx * 116.0)
    $isFirst = ($rowIdx -eq 0)
    $dotC = $script:PANELD6b
    $dotFg = $txtC
    if ($isFirst) { $dotC = $script:LINEORG; $dotFg = '#0E1319' }
    $barC = $subC
    if ($isFirst) { $barC = $script:LINEORG }
    $o += (Circ ($colMX + 24) ($ry + 16) 46 $dotC '')
    $o += Ts ('c5-rn' + $rowIdx) ($colMX + 24) ($ry + 26) 46 30 ([string]$tn.no) 20 $script:DISP $dotFg 'CENTER' ''
    $o += Ts ('c5-re' + $rowIdx) ($colMX + 88) ($ry + 8) 200 50 ([string]$tn.eta) 38 $script:MONO $txtC 'LEFT' ''
    $o += Ts ('c5-rs' + $rowIdx) ($colMX + 88) ($ry + 58) 230 30 ('6 节编组 · ' + $tn.load) 20 $script:SANS $subC 'LEFT' ''
    $o += (Box ($colMX + 330) ($ry + 34) 156 14 $script:PANELD6b 7)
    $fillW = 156.0 * ([int]$tn.min / [double]$mxMax)
    if ($fillW -lt 6) { $fillW = 6.0 }
    $o += (Box ($colMX + 330) ($ry + 34) $fillW 14 $barC 7)
    $minTxt = ([string]$tn.min + ' 分钟')
    $o += Ts ('c5-rm' + $rowIdx) ($colMX + 500) ($ry + 26) 136 30 $minTxt 20 $script:MONO $txtC 'RIGHT' ''
    if ($rowIdx -lt 2) { $o += (HR ($colMX + 24) ($ry + 106) 612 1 $hair) }
    $rowIdx++
}
$o += Ts 'c5-mn' ($colMX + 24) 470 612 30 '横条按 3 / 9 / 16 分钟等比绘制，最长的一班即本次量程' 17 $script:SANS $subC 'LEFT' ''
Guard 'case-05-mid' 500 508

# ---- right: same-platform transfers ----
$o += (Card $colRX $CY $colRW $CH $pan 10 ('1 SOLID ' + $hair) '')
$o += Ts 'c5-rt' ($colRX + 24) 100 300 34 '同站台换乘' 22 $script:SANS $txtC 'LEFT' ''
$tfCols = @($script:LINEGRN, $script:LINEBLU)
$tfChip = @('#FFFFFF', '#FFFFFF')
$tfIdx = 0
foreach ($tf in $c5.transfer) {
    $ty = 146.0 + ($tfIdx * 150.0)
    $tcol = $tfCols[$tfIdx]
    $o += (Card ($colRX + 24) $ty 450 134 $script:PANELD6b 8 ('1 SOLID ' + $hair) '')
    $o += (Box ($colRX + 44) ($ty + 24) 48 48 $tcol 12)
    $lnNum = ([string]($tf.line)) -replace '[^0-9]', ''
    $lnFs = 22
    if ($lnNum.Length -gt 1) { $lnFs = 18 }
    $o += Ts ('c5-cn' + $tfIdx) ($colRX + 44) ($ty + 34) 48 32 $lnNum $lnFs $script:DISP $tfChip[$tfIdx] 'CENTER' ''
    $o += Ts ('c5-ln' + $tfIdx) ($colRX + 104) ($ty + 22) 220 34 $tf.line 26 $script:SANS $txtC 'LEFT' ''
    $opBg = $script:LINEGRN
    $opTxt = '#FFFFFF'
    if ($tf.open -ne '本侧乘车') { $opBg = $script:LINEORG }
    $opW = [int](TW $tf.open 16) + 20
    $o += (Tag ($colRX + 450 - 24 - $opW) ($ty + 24) $tf.open 16 $opBg $opTxt $script:SANS 10 30)
    $o += Ts ('c5-td' + $tfIdx) ($colRX + 104) ($ty + 58) 300 30 $tf.to 21 $script:SANS $subC 'LEFT' ''
    $o += Ts ('c5-tw' + $tfIdx) ($colRX + 44) ($ty + 94) 400 30 $tf.walk 19 $script:SANS $txtC 'LEFT' ''
    $tfIdx++
}
$np5 = PPara 'c5-note' ($colRX + 24) 446 450 '7 号线在本侧、12 号线在对侧；步行距离见每张卡。' 17 26 $script:SANS $subC ''
$o += $np5[0]
Guard 'case-05-right' 500 508

$o += (Src6 '05' ([string]$c5.lastTrain) $M 516 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '05' '第 2 班标了较挤 —— 等多久和挤不挤是两件事，横条只回答前一个问题' $M 560 ($W - 2 * $M) $hair2 $txtC)
Guard 'case-05-foot' 600 $H
Save 'case-05' (Page6 $W $H $shell $o) $W $H

# =====================================================================
# case-06 -- 信用卡分期真实年化 (900 x 1400, dark)
# =====================================================================
$c6 = $calc.case06
$W = 900; $H = 1400; $M = 40
$Wt = Tone6 'dark'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$o = ''
$mh = Masthead6 '06' '信用卡分期 · 真实年化' $M 32 ($W - 2 * $M) $hair2 $subC $txtC 16 16
$o += $mh[0]
$o += Ts 'c6-t' $M 78 ($W - 2 * $M) 52 '分 12 期，年化不是 7.20%' 34 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c6-s' $M 136 ($W - 2 * $M) 30 '每期 536 元，其中手续费 36 元；本金逐期减少，手续费不减' 19 $script:SANS $subC 'LEFT' ''

# ---- KPI strip ----
$kpi6 = @(
    @{ lb = '商品价';    vl = '¥6,000';        sb = '一次付清的原价';  cl = $txtC }
    @{ lb = '每期';      vl = '¥536 x 12';     sb = '共付 ¥6,432';     cl = $txtC }
    @{ lb = '名义费率';  vl = (D2 $c6.nominalPct) + '%'; sb = '432 / 6,000'; cl = $script:MAG }
    @{ lb = '实际年化';  vl = (D2 $c6.aprEff) + '%';     sb = '现金流折算';  cl = $script:WARN }
)
$kx = $M
foreach ($k in $kpi6) {
    $o += (Card $kx 184 196 112 $pan 10 ('1 SOLID ' + $hair) '')
    $o += Ts ('c6-kl' + $k.lb) ($kx + 16) 202 164 26 $k.lb 16 $script:SANS $subC 'LEFT' ''
    $o += Ts ('c6-kv' + $k.lb) ($kx + 16) 228 164 42 $k.vl 28 $script:DISP $k.cl 'LEFT' ''
    $o += Ts ('c6-ks' + $k.lb) ($kx + 16) 272 164 24 $k.sb 13 $script:SANS $subC 'LEFT' ''
    $kx = $kx + 208
}
Guard 'case-06-kpi' 296 1300

# ---- section A: two charts, one shared x-geometry ----
$o += Ts 'c6-at' $M 316 560 32 '每期 536 元，去向是固定的' 22 $script:SANS $txtC 'LEFT' ''

$plotT = 392.0; $plotB = 628.0
$plotH = $plotB - $plotT
$inW = 380.0
$in1 = $M + 10.0
$in2 = 470.0
$slotW = ($inW - (11 * 5.0)) / 12.0

# chart 1 -- payment composition
$o += Ts 'c6-c1t' $M 356 200 28 '① 每期构成' 17 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c6-c1a' 240 356 200 28 '手续费 36 元' 16 $script:SANS $script:MAG 'RIGHT' ''
$o += (DashH $in1 $plotT $inW 1 $hair 4 6)
$feeH = $plotH * 36.0 / 536.0
for ($i = 0; $i -lt 12; $i++) {
    $bx = $in1 + ($i * ($slotW + 5.0))
    $o += (Box $bx $plotT $slotW ($plotH - $feeH) $script:HAIRD6b 0)
    $o += (Box $bx $plotT $slotW $feeH $script:MAG 0)
}
$o += (DashH $in1 ($plotT + $feeH - 1.0) $inW 2 $script:MAG 8 6)
$o += (HR $in1 $plotB $inW 1 $hair2)
$o += Ts 'c6-c1v' ($in1 + 4) 414 60 22 '536' 14 $script:MONO '#FFFFFF' 'LEFT' ''
$o += Ts 'c6-c1x1' $in1 634 120 24 '第 1 期' 15 $script:SANS $subC 'LEFT' ''
$o += Ts 'c6-c1x2' ($in1 + $inW - 120) 634 120 24 '第 12 期' 15 $script:SANS $subC 'RIGHT' ''

# chart 2 -- outstanding balance
$o += Ts 'c6-c2t' 460 356 200 28 '② 你还欠多少' 17 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c6-c2a' 660 356 200 28 '6,000 → 500' 16 $script:SANS $subC 'RIGHT' ''
$balMax = [double]$c6.price
foreach ($gv in @(6000, 4000, 2000)) {
    $gy = $plotB - ($plotH * $gv / $balMax)
    $o += (DashH $in2 $gy $inW 1 $hair 4 6)
    $gTxt = ([int]$gv).ToString('N0')
    $o += Ts ('c6-g' + $gv) ($in2 + $inW - 64) ($gy + 2) 64 22 $gTxt 14 $script:MONO $subC 'RIGHT' ''
}
for ($i = 0; $i -lt 12; $i++) {
    $bal = $balMax - (500.0 * $i)
    $bh = $plotH * ($bal / $balMax)
    $bx = $in2 + ($i * ($slotW + 5.0))
    $o += (Box $bx ($plotB - $bh) $slotW $bh $subC 0)
}
$o += (HR $in2 $plotB $inW 1 $hair2)
$o += Ts 'c6-c2x1' $in2 634 120 24 '第 1 期' 15 $script:SANS $subC 'LEFT' ''
$o += Ts 'c6-c2x2' ($in2 + $inW - 120) 634 120 24 '第 12 期' 15 $script:SANS $subC 'RIGHT' ''

$capA = '左边 12 根柱子一样高：手续费每期 36 元，一次不少。'
$capB = '右边欠款从 6,000 掉到 500，平均只占用 3,250 元 —— 432 / 3,250 = 13.29%。'
$o += Ts 'c6-cap' $M 666 ($W - 2 * $M) 24 $capA 16 $script:SANS $subC 'LEFT' ''
$o += Ts 'c6-cap2' $M 690 ($W - 2 * $M) 24 $capB 16 $script:SANS $subC 'LEFT' ''
Guard 'case-06-charts' 714 1300

# ---- section B: one shared annualisation scale, four pins ----
$o += Ts 'c6-bt' $M 734 560 32 '把 7.20% 放到同一根尺上看' 22 $script:SANS $txtC 'LEFT' ''
$scLo = 0.0; $scHi = 20.0; $scX = $M; $scW = [double]($W - 2 * $M)
$bandW = $scW * ($c6.nominalPct - $scLo) / ($scHi - $scLo)
$o += Ts 'c6-bl' 140 768 180 22 '你以为的成本区间' 14 $script:SANS $script:MAG 'LEFT' ''
$o += (Box $scX 798 $scW 20 $script:PANELD6b 0)
$o += (Box $scX 798 $bandW 20 $script:MAG 0)
$pins = @(
    @{ v = 1.65;              c = $subC;   dot = $false }
    @{ v = [double]$c6.nominalPct; c = $script:MAG;  dot = $true }
    @{ v = [double]$c6.aprSimple;  c = '#FFFFFF';    dot = $false }
    @{ v = [double]$c6.aprEff;     c = $script:WARN; dot = $true }
)
foreach ($pn in $pins) {
    $px = $scX + ($scW * ($pn.v - $scLo) / ($scHi - $scLo))
    $o += (Box ($px - 1.5) 784 3 50 $pn.c 0)
    if ($pn.dot) { $o += (Circ ($px - 9) 776 18 $pn.c '') }
}
for ($i = 0; $i -le 4; $i++) {
    $tx = $scX + ($scW * $i / 4.0)
    $o += (Box ($tx - 1) 818 1 14 $hair 0)
    $tv = [int]($scLo + (($scHi - $scLo) * $i / 4.0))
    $tw = 70.0
    $tal = 'CENTER'
    $tlx = $tx - ($tw / 2.0)
    if ($i -eq 0) { $tal = 'LEFT'; $tlx = $scX }
    if ($i -eq 4) { $tal = 'RIGHT'; $tlx = $scX + $scW - $tw }
    $o += Ts ('c6-tk' + $i) $tlx 836 $tw 24 ($tv.ToString() + '%') 14 $script:MONO $subC $tal ''
}
$legend6 = @(
    @{ x = $M;   y = 872.0; c = $subC;   t = '1.65% 同期存款（演示）' }
    @{ x = 450.0; y = 872.0; c = $script:MAG;  t = '7.20% 名义费率 = 432 / 6,000' }
    @{ x = $M;   y = 906.0; c = '#FFFFFF'; t = ('13.03% 年化利率（月 ' + (D4 $c6.monthlyIRR) + '% x 12）') }
    @{ x = 450.0; y = 906.0; c = $script:WARN; t = '13.84% 实际年化（复利）' }
)
foreach ($lg in $legend6) {
    $o += (Box $lg.x ($lg.y + 5) 14 14 $lg.c 3)
    $o += Ts ('c6-lg' + $lg.x + '-' + $lg.y) ($lg.x + 22) $lg.y 388 24 $lg.t 16 $script:SANS $txtC 'LEFT' ''
}
Guard 'case-06-scale' 930 1300

# ---- section C: three ways to spend the same 6,000 ----
$o += Ts 'c6-ct' $M 950 560 32 '同样 6,000 元的三种走法' 22 $script:SANS $txtC 'LEFT' ''
$cCosts = @($c6.compare[0].cost, $c6.compare[1].cost, $c6.compare[2].cost)
$cCostMax = 432.0
$cCols = @($script:MAG, $subC, $script:LINEGRN)
$ci = 0
foreach ($cm in $c6.compare) {
    $ry = 990.0 + ($ci * 74.0)
    $amt = [double]$cm.cost
    $cCol = $cCols[$ci]
    $o += (Card $M $ry ($W - 2 * $M) 64 $pan 8 ('1 SOLID ' + $hair) '')
    $o += (Box 56 ($ry + 14) 6 36 $cCol 3)
    $o += Ts ('c6-cn' + $ci) 74 ($ry + 10) 470 28 $cm.name 19 $script:SANS $txtC 'LEFT' ''
    $o += Ts ('c6-ct' + $ci) 74 ($ry + 38) 300 22 $cm.tag 14 $script:SANS $subC 'LEFT' ''
    $o += (Box 560 ($ry + 26) 170 12 $script:PANELD6b 6)
    if ($amt -ne 0) {
        $mag = [Math]::Abs($amt) / $cCostMax
        $fill6 = 170.0 * $mag
        if ($fill6 -lt 4) { $fill6 = 4.0 }
        $o += (Box 560 ($ry + 26) $fill6 12 $cCol 6)
    }
    $vTxt = ([Math]::Abs([int]$amt)).ToString() + ' 元'
    if ($amt -lt 0) { $vTxt = '+' + $vTxt }
    if ($amt -eq 0) { $vTxt = '0 元' }
    if ($amt -gt 0) { $vTxt = '+' + $vTxt }
    $o += Ts ('c6-cv' + $ci) 742 ($ry + 16) 106 32 $vTxt 24 $script:MONO $cCol 'RIGHT' ''
    $ci++
}
$note6 = '一次付清是基准：分期多付 432 元，占本金 7.20%；折成年化是 13.84%，接近名义费率的两倍。'
$np6b = PPara 'c6-note' $M 1216 ($W - 2 * $M) $note6 16 24 $script:SANS $subC ''
$o += $np6b[0]
Guard 'case-06-note' (1216 + ($np6b[1] * 24)) 1300

$o += (Src6 '06' '名义费率 = 432 / 6,000；年化按每期现金流折算（月 IRR 1.0862%）· 演示 DEMO' $M 1276 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '06' '每期 536 元里的 36 元从不减少，而欠款一直在减少 —— 7.20% 因此变 13.84%' $M 1330 ($W - 2 * $M) $hair2 $txtC)
Guard 'case-06-foot' 1370 $H
Save 'case-06' (Page6 $W $H $shell $o) $W $H

# =====================================================================
# case-07 -- 退租押金瀑布 (560 x 1180, light)
# =====================================================================
$c7 = $calc.case07
$W = 560; $H = 1180; $M = 32
$Wt = Tone6 'light'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$o = ''
$mh = Masthead6 '07' '退租押金 · 逐项扣减' $M 28 ($W - 2 * $M) $hair2 $subC $txtC 15 15
$o += $mh[0]
$o += Ts 'c7-t' $M 72 ($W - 2 * $M) 44 '押金 6,000，最后能退多少' 30 $script:DISP $txtC 'LEFT' ''
$np7s = PPara 'c7-s' $M 122 ($W - 2 * $M) '五笔扣减里三笔有单据可核，另外两笔要看措辞算不算自然磨损。' 16 24 $script:SANS $subC ''
$o += $np7s[0]

# ---- KPI ----
$kpi7 = @(
    @{ lb = '押金原额'; vl = '6,000'; sb = '合同起租时交'; cl = $txtC }
    @{ lb = '固定可扣'; vl = '760';   sb = '三项有单据';   cl = $script:INDIGO }
    @{ lb = '有争议';   vl = '600';   sb = '两项看措辞';   cl = $script:CLAIM }
)
$kx = $M
foreach ($k in $kpi7) {
    $o += (Card $kx 182 157 112 $pan 10 ('1 SOLID ' + $hair) '')
    $o += Ts ('c7-kl' + $k.lb) ($kx + 14) 200 129 24 $k.lb 15 $script:SANS $subC 'LEFT' ''
    $o += Ts ('c7-kv' + $k.lb) ($kx + 14) 226 129 40 $k.vl 26 $script:DISP $k.cl 'LEFT' ''
    $o += Ts ('c7-ks' + $k.lb) ($kx + 14) 268 129 22 $k.sb 13 $script:SANS $subC 'LEFT' ''
    $kx = $kx + 169
}
Guard 'case-07-kpi' 294 1100

# ---- ledger rows, each carrying the running balance as a bar ----
$o += Ts 'c7-h1' $M 316 200 28 '逐项扣减' 21 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c7-h2' 330 320 198 24 '扣减 / 余额' 15 $script:SANS $subC 'RIGHT' ''
$o += (HR $M 350 ($W - 2 * $M) 1 $hair2)
$startV = [double]$c7.start
$ri = 0
foreach ($fl in $c7.flow) {
    $ry = 358.0 + ($ri * 64.0)
    $kind = [string]$fl.kind
    if ($kind -eq 'dispute') {
        $o += (Box $M ($ry + 2) 496 58 '#FBF4E7' 8)
        $o += (Hatch6 $M ($ry + 2) 496 58 8 '#E0A33C33' 18 3)
    } elseif ($kind -eq 'start') {
        $o += (Box $M ($ry + 2) 496 58 '#EEF1FB' 8)
    } else {
        $o += (Box $M ($ry + 2) 496 58 '#FFFFFF' 8)
    }
    $o += Ts ('c7-nm' + $ri) ($M + 8) ($ry + 4) 200 28 $fl.name 18 $script:SANS $txtC 'LEFT' ''
    if ($kind -eq 'dispute') {
        $o += (Tag 244 ($ry + 5) '可争议' 13 $script:CLAIM '#1B1305' $script:SANS 10 26)
    }
    $amt = [double]$fl.amt
    $aTxt = ''
    if ($kind -eq 'start') { $aTxt = ([int]$amt).ToString('N0') }
    else { $aTxt = '-' + ([int][Math]::Abs($amt)).ToString('N0') }
    $aCol = $txtC
    if ($kind -eq 'fixed') { $aCol = $script:INDIGO }
    if ($kind -eq 'dispute') { $aCol = $script:CLAIM }
    $o += Ts ('c7-am' + $ri) 330 ($ry + 6) 84 28 $aTxt 18 $script:MONO $aCol 'RIGHT' ''
    $runV = [double]$fl.running
    $o += Ts ('c7-rn' + $ri) 430 ($ry + 6) 98 28 ([int]$runV).ToString('N0') 18 $script:MONO $txtC 'RIGHT' ''
    $o += Ts ('c7-wh' + $ri) ($M + 8) ($ry + 32) 300 22 ([string]($fl.why)) 14 $script:SANS $subC 'LEFT' ''
    $barW7 = 480.0 * ($runV / $startV)
    $o += (Box ($M + 8) ($ry + 54) $barW7 5 $script:INDIGO 3)
    if ($ri -lt 5) { $o += (HR $M ($ry + 63) ($W - 2 * $M) 1 $hair) }
    $ri++
}
Guard 'case-07-rows' 742 1100

# ---- two outcomes ----
$o += (HR $M 764 ($W - 2 * $M) 1 $hair2)
$o += Ts 'c7-o1' $M 778 300 28 '两种结局' 21 $script:SANS $txtC 'LEFT' ''
$o += (Card $M 812 241 150 $pan 10 ('1 SOLID ' + $hair) '')
$o += Ts 'c7-a1l' ($M + 20) 834 201 26 '全部扣掉' 17 $script:SANS $subC 'LEFT' ''
$o += Ts 'c7-a1v' ($M + 20) 864 201 52 ('¥' + ([int]$c7.refundIfAllCut).ToString('N0')) 34 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c7-a1s' ($M + 20) 920 201 24 '争议项也算你头上' 14 $script:SANS $subC 'LEFT' ''
$o += (Card 287 812 241 150 $pan 10 ('1 SOLID ' + $hair) '')
$o += Ts 'c7-a2l' 307 834 201 26 '争回争议项' 17 $script:SANS $subC 'LEFT' ''
$o += Ts 'c7-a2v' 307 864 201 52 ('¥' + ([int]$c7.refundIfDisputeKept).ToString('N0')) 34 $script:DISP $script:CLAIM 'LEFT' ''
$o += Ts 'c7-a2s' 307 920 201 24 '差额 600 元' 14 $script:SANS $subC 'LEFT' ''

$o += Ts 'c7-cap' $M 974 ($W - 2 * $M) 23 '两项有争议的扣减合计 600 元，这就是两条路的全部差额。' 15 $script:SANS $subC 'LEFT' ''
$o += Ts 'c7-cap2' $M 997 ($W - 2 * $M) 23 '合同措辞决定它们算不算自然磨损。' 15 $script:SANS $subC 'LEFT' ''
Guard 'case-07-cap' 1020 1100

$o += (Src6 '07' '自拟演示 DEMO · 未引用法条原文（检索摘要 2026-10-08）' $M 1036 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '07' '能扣的要有单据，有争议的看措辞 —— 两条路差 600 元' $M 1090 ($W - 2 * $M) $hair2 $txtC)
Guard 'case-07-foot' 1130 $H
Save 'case-07' (Page6 $W $H $shell $o) $W $H

Write-Output ('total problems = ' + $script:B06PROB)
if ($script:B06PROB -gt 0) { exit 1 }
