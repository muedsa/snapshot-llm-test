# gen-b06-c.ps1 -- build case-08, case-09, case-10
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
# case-08 -- 降水概率怎么读 (1000 x 1000, dark)
# =====================================================================
$c8 = $calc.case08
$W = 1000; $H = 1000; $M = 40
$Wt = Tone6 'dark'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$o = ''
$mh = Masthead6 '08' '降水概率 · 怎么读' $M 32 ($W - 2 * $M) $hair2 $subC $txtC 16 16
$o += $mh[0]
$o += Ts 'c8-t' $M 78 ($W - 2 * $M) 52 '明天 08:00 出门，带伞吗？' 34 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c8-s' $M 136 ($W - 2 * $M) 30 '出门带伞 —— 08:00 这一小时 40%，09:00 升到 70%' 19 $script:SANS $script:UMB 'LEFT' ''

# ---- A: the 100-cell field ----
$o += Ts 'c8-at' $M 186 460 32 '100 个格子，40 个在下雨' 22 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c8-ah' 560 190 400 28 '每格 = 长期看的 1 次' 17 $script:SANS $subC 'RIGHT' ''
$gridSize = 416.0
$cellW = ($gridSize - (9 * 4.0)) / 10.0
$stepW = $cellW + 4.0
$filled = [int]$c8.gridFilled
for ($gi = 0; $gi -lt 100; $gi++) {
    $gcol = '#1B2530'
    if ((($gi * 37) % 100) -lt $filled) { $gcol = $script:RAIN }
    $gxx = $M + (($gi % 10) * $stepW)
    $gyy = 230.0 + ([Math]::Floor($gi / 10) * $stepW)
    $o += (Box $gxx $gyy $cellW $cellW $gcol 6)
}
$o += Ts 'c8-gc' $M 660 416 26 ('青格 ' + $filled + ' 个 · 暗格 60 个 —— 格子是次数，不是地点') 16 $script:SANS $subC 'LEFT' ''

# ---- A right: three readings of the same number ----
# each reading is split at its own first comma so no line ever ends on an orphan glyph;
# the two halves are re-checked against calc so the dataset stays authoritative
$ti = 0
foreach ($tr in $c8.translations) {
    $ty = 230.0 + ($ti * 145.0)
    if ($ti -eq 1) { $ty = 375.0 }
    if ($ti -eq 2) { $ty = 520.0 }
    $ts = [string]$tr
    $sp = $ts.IndexOf([char]0xFF0C)
    if ($sp -lt 0) { $sp = $ts.IndexOf(',') }
    if ($sp -lt 0) { Fail ('case-08 translation ' + $ti + ' has no comma to break on') }
    $la = $ts.Substring(0, $sp + 1)
    $lb = $ts.Substring($sp + 1)
    if (($la + $lb) -ne $ts) { Fail ('case-08 translation ' + $ti + ' split does not rejoin to the calc string') }
    $o += (Card 486 $ty 474 126 $pan 10 ('1 SOLID ' + $hair) '')
    $o += (Step6 510 ($ty + 43) 40 ($ti + 1) $script:RAIN '#0B1B1F')
    $o += Ts ('c8-tra' + $ti) 566 ($ty + 38) 370 26 $la 17 $script:SANS $txtC 'LEFT' ''
    if ($lb.Length -gt 0) {
        $o += Ts ('c8-trb' + $ti) 566 ($ty + 64) 370 26 $lb 17 $script:SANS $txtC 'LEFT' ''
    }
    $ti++
}
Guard 'case-08-a' 686 $H

# ---- B: the three hourly windows ----
$o += Ts 'c8-bt' $M 700 460 32 '今天上午的三个小时' 22 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c8-bh' 560 704 400 28 '概率不是雨量，也不是时长' 17 $script:SANS $subC 'RIGHT' ''
$maxP = 0
foreach ($wn in $c8.windows) { if ([int]$wn.p -gt $maxP) { $maxP = [int]$wn.p } }
$wx = $M
foreach ($wn in $c8.windows) {
    $pp = [int]$wn.p
    $o += (Card $wx 748 296 134 $pan 10 ('1 SOLID ' + $hair) '')
    $o += Ts ('c8-wl' + $wn.label) ($wx + 20) 764 200 26 ([string]$wn.label) 18 $script:SANS $txtC 'LEFT' ''
    if ($pp -eq $maxP) {
        $o += (Tag ($wx + 228) 762 '最高' 14 $script:UMB '#0E1319' $script:SANS 10 26)
    }
    $o += Ts ('c8-wh' + $wn.label) ($wx + 20) 792 256 22 ([string]$wn.h) 14 $script:MONO $subC 'LEFT' ''
    $o += Ts ('c8-wv' + $wn.label) ($wx + 20) 818 160 42 ($pp.ToString() + '%') 32 $script:DISP $script:RAIN 'LEFT' ''
    $o += (Box ($wx + 20) 866 256 8 $script:PANELD6b 4)
    $o += (Box ($wx + 20) 866 (256.0 * $pp / 100.0) 8 $script:RAIN 4)
    $wx = $wx + 312
}
Guard 'case-08-b' 882 $H

$o += (Src6 '08' ([string]$c8.caution) $M 894 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '08' '40% = 100 次里 40 次 —— 不是 40 分钟，也不是 40% 的地方' $M 944 ($W - 2 * $M) $hair2 $txtC)
Guard 'case-08-foot' 984 $H
Save 'case-08' (Page6 $W $H $shell $o) $W $H

# =====================================================================
# case-09 -- 路侧停车限时计费 (840 x 1340, light)
# =====================================================================
$c9 = $calc.case09
$W = 840; $H = 1340; $M = 40
$Wt = Tone6 'light'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$o = ''
$mh = Masthead6 '09' '路侧停车 · 限时计费' $M 28 ($W - 2 * $M) $hair2 $subC $txtC 15 15
$o += $mh[0]
$o += Ts 'c9-t' $M 72 ($W - 2 * $M) 44 '停 27 分钟，现在该多少钱？' 30 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c9-s' $M 122 ($W - 2 * $M) 28 $c9.rule 18 $script:SANS $subC 'LEFT' ''

# ---- KPI ----
$kpi9 = @(
    @{ lb = '已用时长'; vl = ([string]$c9.usedMin + ' 分钟'); sb = ($c9.arriveAt + ' 到 · 现在 ' + $c9.nowAt); cl = $script:ASPHALT }
    @{ lb = '当前费用'; vl = ((D2 $c9.usedFee) + ' 元');     sb = '3.00 + 2.00 元，按段计';          cl = $script:LATE }
    @{ lb = '距限时';   vl = ([string](120 - $c9.usedMin) + ' 分钟'); sb = '限 120 分钟';           cl = $script:ASPHALT }
)
$kx = $M
foreach ($k in $kpi9) {
    $o += (Card $kx 168 244 120 $pan 10 ('1 SOLID ' + $hair) '')
    $o += Ts ('c9-kl' + $k.lb) ($kx + 16) 184 212 24 $k.lb 15 $script:SANS $subC 'LEFT' ''
    $o += Ts ('c9-kv' + $k.lb) ($kx + 16) 210 212 44 $k.vl 32 $script:DISP $k.cl 'LEFT' ''
    $o += Ts ('c9-ks' + $k.lb) ($kx + 16) 256 212 22 $k.sb 13 $script:SANS $subC 'LEFT' ''
    $kx = $kx + 258
}
Guard 'case-09-kpi' 288 $H

# ---- the dial: full circle = 120 minutes ----
$o += Ts 'c9-dt' $M 310 420 30 '钟面上的 2 小时' 21 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c9-dh' 460 314 340 26 '外圈扇形 = 三段计费' 16 $script:SANS $subC 'RIGHT' ''
$cxD = 420.0; $cyD = 600.0; $rD = 200.0
$shade1 = '#FFD966'; $shade2 = '#FFE9A8'
$o += (Circ ($cxD - $rD) ($cyD - $rD) ($rD * 2.0) $script:SHADE6 '')
$o += (Wedge6 $cxD $cyD $rD (Dial-Map 0 120) (Dial-Map 15 120) $script:PARK 16)
$o += (Wedge6 $cxD $cyD $rD (Dial-Map 15 120) (Dial-Map 60 120) $shade1 42)
$o += (Wedge6 $cxD $cyD $rD (Dial-Map 60 120) (Dial-Map 120 120) $shade2 56)
$o += (Box ($cxD - 3) 386 6 34 $script:LATE 0)
# dial tick labels, outside the ring
$o += Ts 'c9-d0' 370 354 100 26 '0 / 120 分' 15 $script:MONO $subC 'CENTER' ''
$o += Ts 'c9-d15' 550 427 60 26 '15 分' 15 $script:MONO $subC 'CENTER' ''
$o += Ts 'c9-d60' 390 813 60 26 '60 分' 15 $script:MONO $subC 'CENTER' ''
# fee labels sitting inside their own wedge
$o += Ts 'c9-f1' 437 448 80 26 '3 元' 17 $script:SANS $txtC 'CENTER' ''
$o += Ts 'c9-f2' 518 644 80 26 '+6 元' 17 $script:SANS $txtC 'CENTER' ''
$o += Ts 'c9-f3' 274 693 80 26 '+8 元' 17 $script:SANS $txtC 'CENTER' ''
# centre readout, kept left of the hand
$o += Ts 'c9-ck' 230 508 165 24 '已用时长' 16 $script:SANS $script:ASPHALT 'LEFT' ''
$o += Ts 'c9-cv' 230 536 165 56 ([string]$c9.usedMin + ' 分钟') 40 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c9-cc' 230 598 165 28 ('当前 ' + (D2 $c9.usedFee) + ' 元') 19 $script:SANS $txtC 'LEFT' ''
$o += (Hand6 $cxD $cyD 165 7 (Dial-Map $c9.usedMin 120) $script:ASPHALT)
$o += (Circ ($cxD - 16) ($cyD - 16) 32 $script:ASPHALT '')
Guard 'case-09-dial' 839 $H

# ---- the fee ruler ----
$o += Ts 'c9-rt' $M 850 520 28 '计费刻度：每 15 分钟一格' 20 $script:SANS $txtC 'LEFT' ''
$rl = Ruler6 'c9-ruler' 60 914 720 0 120 15 0 27 ([double]$c9.usedMin) $script:SHADE6 $script:PARK $script:HAIRL6 $script:ASPHALT 26 12
$o += $rl[0]
# bracket boundaries, so the ruler and the dial describe the same three segments
$o += (Box 149 914 3 26 $script:ASPHALT 0)
$o += (Box 419 914 3 26 $script:ASPHALT 0)
$o += Ts 'c9-rl0' 60 964 70 24 '0 分' 14 $script:MONO $subC 'LEFT' ''
$o += Ts 'c9-rl15' 115 964 70 24 '15 分' 14 $script:MONO $subC 'CENTER' ''
$o += Ts 'c9-rl27' 187 964 70 24 ([string]$c9.usedMin + ' 分') 14 $script:MONO $script:ASPHALT 'CENTER' ''
$o += Ts 'c9-rl60' 385 964 70 24 '60 分' 14 $script:MONO $subC 'CENTER' ''
$o += Ts 'c9-rl120' 710 964 70 24 '120 分' 14 $script:MONO $subC 'RIGHT' ''
$o += Ts 'c9-rc' 60 996 720 26 '圆点 = 现在；黄段 = 已经产生费用的区间；两道竖线 = 计费档位切换' 15 $script:SANS $subC 'LEFT' ''
Guard 'case-09-ruler' 1022 $H

# ---- cumulative brackets ----
$o += Ts 'c9-ct' $M 1042 520 28 '累计到每一档多少钱' 20 $script:SANS $txtC 'LEFT' ''
$bx9 = $M
foreach ($cm in $c9.cumulative) {
    $o += (Card $bx9 1082 244 120 $pan 10 ('1 SOLID ' + $hair) '')
    $np9 = PPara ('c9-bn' + $cm.at) ($bx9 + 16) 1098 212 ([string]$cm.note) 15 22 $script:SANS $subC ''
    $o += $np9[0]
    $o += Ts ('c9-bv' + $cm.at) ($bx9 + 16) 1148 150 34 ('累计 ' + ([int]$cm.cum) + ' 元') 24 $script:DISP $txtC 'LEFT' ''
    $o += (Box ($bx9 + 16) 1186 212 8 $script:SHADE6 4)
    $o += (Box ($bx9 + 16) 1186 (212.0 * [double]$cm.cum / [double]$c9.maxFeeAtLimit) 8 $script:ASPHALT 4)
    $bx9 = $bx9 + 258
}
Guard 'case-09-brackets' 1202 $H

$o += (Src6 '09' '计费规则为自拟演示 DEMO；停车价格检索摘要（Bing RSS，2026-10-08）' $M 1228 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '09' '超过 2 小时不是继续收费，而是按违规停放处理 —— 演示规则 DEMO，以现场标志为准' $M 1280 ($W - 2 * $M) $hair2 $txtC)
Guard 'case-09-foot' 1320 $H
Save 'case-09' (Page6 $W $H $shell $o) $W $H

# =====================================================================
# case-10 -- 快递到件时间窗 (1600 x 900, dark)
# =====================================================================
$c10 = $calc.case10
$W = 1600; $H = 900; $M = 48
$Wt = Tone6 'dark'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]
$o = ''
$mh = Masthead6 '10' '快递 · 预计送达窗' $M 32 ($W - 2 * $M) $hair2 $subC $txtC 17 17
$o += $mh[0]
$o += Ts 'c10-t' $M 80 ($W - 2 * $M) 50 '13:05，还要等多久才送到？' 32 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c10-s' $M 136 ($W - 2 * $M) 28 ('预计 ' + $c10.etaFrom + '–' + $c10.etaTo + ' 送达 · 单号 ' + $c10.waybill) 19 $script:SANS $subC 'LEFT' ''

# ---- A: the five nodes ----
$o += Ts 'c10-at' $M 180 600 30 '这一单走到哪了' 21 $script:SANS $txtC 'LEFT' ''
$o += Ts 'c10-ah' 1000 184 552 26 '已过 3 个节点，当前是第 4 个，最后一个是预计窗' 17 $script:SANS $subC 'RIGHT' ''
$colW10 = 1504.0 / 5.0
$cx0 = $M + ($colW10 * 0.5)
$cx3 = $M + ($colW10 * 3.5)
$cx4 = $M + ($colW10 * 4.5)
$o += (Box $cx0 272 ($cx4 - $cx0) 6 $script:PANELD6b 3)
$o += (Box $cx0 272 ($cx3 - $cx0) 6 $script:PARCEL 3)
$o += (DashH $cx3 272 ($cx4 - $cx3) 6 $subC 10 8)
$ni = 0
foreach ($nd in $c10.nodes) {
    $ncx = $M + ($colW10 * ($ni + 0.5))
    $stc = $subC
    if ($ni -eq [int]$c10.currentIndex) { $stc = $script:DELIV }
    $o += Ts ('c10-nt' + $ni) ($ncx - 140) 228 280 26 ([string]$nd.t) 18 $script:MONO $subC 'CENTER' ''
    if ($ni -eq 4) {
        $o += (Circ ($ncx - 13) 262 26 $pan ('3 SOLID ' + $script:DELIV))
    } elseif ($ni -eq [int]$c10.currentIndex) {
        $o += (Circ ($ncx - 17) 258 34 $script:DELIV '')
    } else {
        $o += (Circ ($ncx - 13) 262 26 $script:PARCEL '')
    }
    $o += Ts ('c10-np' + $ni) ($ncx - 140) 300 280 28 ([string]$nd.p) 20 $script:SANS $txtC 'CENTER' ''
    $o += Ts ('c10-ns' + $ni) ($ncx - 140) 330 280 26 ([string]$nd.s) 17 $script:SANS $stc 'CENTER' ''
    $ni++
}
Guard 'case-10-a' 356 $H

# ---- B: the window and the progress ----
$o += (Card $M 382 940 222 $pan 12 ('1 SOLID ' + $hair) '')
$o += Ts 'c10-wk' 76 406 400 26 '预计送达窗' 18 $script:SANS $subC 'LEFT' ''
$o += Ts 'c10-wv' 76 438 600 62 ($c10.etaFrom + ' – ' + $c10.etaTo) 50 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c10-ws' 76 504 700 28 ('还有 ' + ([string]$c10.etaMinutes) + ' 分钟到窗；窗宽 30 分钟') 19 $script:SANS $subC 'LEFT' ''
$trkW = 884.0
$winX = 76.0 + ($trkW * 75.0 / 105.0)
$winW = $trkW * 30.0 / 105.0
$o += (Box 76 540 $trkW 18 $script:PANELD6b 9)
$o += (Box 74 534 4 30 $txtC 0)
$o += (Box ($winX - 3) 534 6 30 $script:DELIV 0)
$o += (Box $winX 540 $winW 18 $script:DELIV 9)
$o += Ts 'c10-wl1' 76 566 220 24 ('现在 ' + $c10.now) 15 $script:SANS $subC 'LEFT' ''
$o += Ts 'c10-wl2' 667 566 80 24 $c10.etaFrom 15 $script:MONO $script:DELIV 'CENTER' ''
$o += Ts 'c10-wl3' 880 566 80 24 $c10.etaTo 15 $script:MONO $subC 'RIGHT' ''

$o += (Card 1016 382 536 222 $pan 12 ('1 SOLID ' + $hair) '')
$o += Ts 'c10-pk' 1044 406 300 26 '派件进度' 18 $script:SANS $subC 'LEFT' ''
$o += Ts 'c10-pv' 1044 438 400 56 (([string]$c10.stationDone) + ' / ' + ([string]$c10.stationTotal)) 44 $script:DISP $txtC 'LEFT' ''
$o += Ts 'c10-ps' 1044 498 460 26 ('从营业点出发第 ' + ([string]$c10.stationDone) + ' 分钟，共 ' + ([string]$c10.stationTotal) + ' 分钟') 16 $script:SANS $subC 'LEFT' ''
$pct10 = 100.0 * [double]$c10.stationDone / [double]$c10.stationTotal
$o += (Box 1044 538 480 16 $script:PANELD6b 8)
$o += (Box 1044 538 (480.0 * [double]$c10.stationDone / [double]$c10.stationTotal) 16 $script:DELIV 8)
$o += Ts 'c10-pp' 1044 564 480 26 ('已完成 ' + (D1 $pct10) + '%') 16 $script:SANS $subC 'LEFT' ''
Guard 'case-10-b' 604 $H

# ---- C: when the phone call becomes worth making ----
$o += (Box $M 634 ($W - 2 * $M) 140 $script:PANELD6b 12)
$o += Ts 'c10-ck' 76 654 500 26 '什么时候该打电话' 17 $script:SANS $subC 'LEFT' ''
$o += Ts 'c10-cv' 76 688 400 48 ($c10.callAfter + ' 之后') 34 $script:DISP $script:DELIV 'LEFT' ''
$o += Ts 'c10-cy' 76 740 640 26 ([string]$c10.callWhy) 16 $script:SANS $subC 'LEFT' ''
$o += (Box 760 654 2 96 '#3E4A5A' 0)
$o += Ts 'c10-sk' 800 654 500 26 '电话里怎么说' 17 $script:SANS $subC 'LEFT' ''
$np10 = PPara 'c10-sc' 800 688 724 ([string]$c10.callScript) 20 32 $script:SANS $txtC ''
$o += $np10[0]
$o += Ts 'c10-sb' 800 732 724 26 ([string]$c10.waybill) 16 $script:MONO $subC 'LEFT' ''
Guard 'case-10-c' 774 $H

$o += (Src6 '10' '运单数据为自拟演示样例 DEMO（单号、时间、进度均非真实运单）' $M 792 ($W - 2 * $M) $hair $subC)
$o += (Foot6 '10' '预计窗是一段时间：14:20 到 14:50 之内都算在窗内' $M 842 ($W - 2 * $M) $hair2 $txtC)
Guard 'case-10-foot' 882 $H
Save 'case-10' (Page6 $W $H $shell $o) $W $H

Write-Output ('total problems = ' + $script:B06PROB)
if ($script:B06PROB -gt 0) { exit 1 }
