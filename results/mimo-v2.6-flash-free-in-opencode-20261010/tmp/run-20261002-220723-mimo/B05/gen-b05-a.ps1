# gen-b05-a.ps1 -- build case-01, case-02, case-03
# PS 5.1 traps respected: $m collides with $M (case-insensitive) so the masthead
# result is $mh; every concatenation passed to a command is fully parenthesised;
# no inline `if` in argument position.
param([int]$Round = 1)
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $root 'tmp\run-20261002-220723-mimo\B05\lib-b05.ps1')

$calc = Get-Calc
$att  = $calc.attitudes
$mdlA = $calc.models.A
$mdlB = $calc.models.B
$mdlC = $calc.models.C

function OutPath([string]$cid) {
    return (Join-Path $script:B05TMP ("{0}\r{1:d2}.snapshot" -f $cid, $Round))
}
function Save([string]$cid, [string]$body, [int]$cw, [int]$ch) {
    Write-Dsl5 (OutPath $cid) $body
    $g = [regex]::Match($body, '<Container width="(\d+)" height="(\d+)"')
    if ($g.Groups[1].Value -ne [string]$cw -or $g.Groups[2].Value -ne [string]$ch) {
        throw "$cid canvas mismatch: expected ${cw}x${ch}, got $($g.Groups[1].Value)x$($g.Groups[2].Value)"
    }
    Write-Output ("  {0} r{1:d2}  {2}x{3}  {4} bytes  problems={5}" -f
        $cid, $Round, $g.Groups[1].Value, $g.Groups[2].Value,
        (Get-Item (OutPath $cid)).Length, $script:PROBLEMS.Count)
}
function Guard([string]$cid, [double]$bottom, [int]$H) {
    if ($bottom -gt $H) { Fail "$cid content bottom $bottom exceeds canvas height $H" }
}

# =====================================================================
# case-01 -- 楼栋剖面总览 (1600 x 1000, dark, 居委会桌面)
# =====================================================================
$W = 1600; $H = 1000; $M = 56
$o = ''
$mh = Masthead5 '01' '梧桐里 3 号楼 · 居委会工作台' $M 40 ($W - 2*$M) $script:HAIRD $script:MUTED $script:PAPERW 20 20
$o += $mh[0]
$o += Ts 'c1-title' $M 100 ($W - 2*$M) 60 '楼栋剖面总览' 46 $script:DISP $script:PAPERW 'LEFT' ''
$sub1 = ('一梯两户 · 6 层 · 12 户 · 总建筑面积 ' + $calc.building.totalArea + ' ㎡ · 方案甲 52.8 万元（演示）')
$o += Ts 'c1-sub' $M 158 940 34 $sub1 21 $script:SANS $script:MUTED 'LEFT' ''
$o += Ts 'c1-date' ($M + $W - 2*$M - 520) 158 520 34 '状态快照 2026-10-08' 21 $script:MONO $script:MUTED 'RIGHT' ''

# ---- left: section panel ----
$PX = $M; $PW = 760; $PY = 196; $PH = 734
$o += (Card $PX $PY $PW $PH $script:PANEL_D 10 ('1 SOLID ' + $script:HAIRD) '')
$o += Ts 'c1-pt' ($PX + 24) ($PY + 18) 520 32 '楼栋剖面 · 一户一格，颜色即态度' 22 $script:SANS $script:PAPERW 'LEFT' ''
$lx = $PX + 24
$o += (Pill $lx ($PY + 58) ('已签约 ' + $att.signed) 18 $script:TEAL $script:WHITE $script:SANS)
$o += (Pill ($lx + 148) ($PY + 58) ('已同意 ' + $att.agreed) 18 $script:AMBER $script:INK $script:SANS)
$o += (Pill ($lx + 296) ($PY + 58) ('顾虑 ' + $att.concern) 18 $script:CORAL $script:WHITE $script:SANS)
$o += (Section5 ($PX + 20) ($PY + 104) ($PW - 40) ($PH - 128) $calc 'dark' 'attitude' '602')
Guard 'case-01-left' ($PY + $PH) $H

# ---- right column: KPI cards ----
$RX = 856; $KW = 332; $KH = 150; $PY = 196
function Kpi([double]$kx, [double]$ky, [string]$label, [string]$big, [string]$bigC,
             [string]$unit, [string]$note, [string]$um = 'block') {
    $k = Card $kx $ky $KW $KH $script:PANEL_D 10 ('1 SOLID ' + $script:HAIRD) ''
    $k += Ts ('lb' + $label) ($kx + 20) ($ky + 16) ($KW - 40) 28 $label 20 $script:SANS $script:MUTED 'LEFT' ''
    $k += Ts ('bg' + $label) ($kx + 20) ($ky + 44) ($KW - 40) 58 $big 44 $script:DISP $bigC 'LEFT' ''
    if ($unit -ne '' -and $um -eq 'inline') { $k += Ts ('un' + $label) ($kx + $KW - 100) ($ky + 62) 80 36 $unit 22 $script:SANS $script:PAPERW 'RIGHT' '' }
    if ($unit -ne '' -and $um -ne 'inline') { $k += Ts ('un' + $label) ($kx + 20) ($ky + 104) ($KW - 40) 24 $unit 19 $script:SANS $script:PAPERW 'LEFT' '' }
    if ($note -ne '')  { $k += Ts ('nt' + $label) ($kx + 20) ($ky + 128) ($KW - 40) 24 $note 17 $script:SANS $script:MUTED 'LEFT' '' }
    return $k
}
$o += (Kpi $RX $PY '意愿支持' ('{0} / 12' -f $att.support) $script:PAPERW '户' ('支持率 ' + $att.supportPct + '%') 'inline')
$bx1 = $RX + 20; $by1 = $PY + 108
$o += (Stack1 $bx1 $by1 ($KW - 40) 10 @(
        @{ v = $att.signed; c = $script:TEAL },
        @{ v = $att.agreed; c = $script:AMBER },
        @{ v = $att.concern; c = $script:CORAL }) 12)

$sgn = ('签约率 ' + [math]::Round(100.0 * $att.signed / 12, 0) + '% · 目标 12/12')
$o += (Kpi ($RX + $KW + 24) $PY '已签约' ('{0} / 12' -f $att.signed) $script:TEAL '户' $sgn 'inline')
$o += (Prog ($RX + $KW + 44) $by1 ($KW - 40) 10 (7.0/12.0) $script:PANEL_D2 $script:TEAL 999)

$o += (Kpi $RX 362 '每户自付区间' ('0 ' + [char]0x2013 + ' 42,985') $script:ACC2 '元（模型 A · 演示）' '1 层不出钱，顶层最高' 'block')
$u4 = '万元 = 造价 52.8 ' + [char]0x2212 + ' 补贴 24.0'
$o += (Kpi ($RX + $KW + 24) 362 '自付合计' '28.8' $script:ACC2 $u4 '补贴金额以当地政策核定为准' 'block')

# ---- next actions ----
$NY = 536; $NH = 180
$o += (Card $RX $NY 688 $NH $script:PANEL_D2 10 ('1 SOLID ' + $script:HAIRD) '')
$o += Ts 'c1-nt' ($RX + 20) ($NY + 16) 400 30 '下一步建议 · 3 项' 21 $script:SANS $script:PAPERW 'LEFT' ''
$o += Ts 'c1-nn' ($RX + 368) ($NY + 16) 300 30 '按截止日期排序' 17 $script:SANS $script:MUTED 'RIGHT' ''
$acts = @(
  @('1', '约 602 室谈三期付款节点', '顶层 42,985 元最高'),
  @('2', '结构工程师复核 101 室井道外移', '一层采光与通行'),
  @('3', '补齐 202 室夜间噪音复测报告', '运行噪音')
)
$ay = $NY + 56
foreach ($a in $acts) {
    $o += (MarkDot ($RX + 20) $ay 26 $script:ACC $script:PANEL_D2)
    $o += Ts ('an' + $a[0]) ($RX + 20) $ay 26 26 $a[0] 17 $script:MONO $script:ACC 'CENTER' ''
    $o += Ts ('at' + $a[0]) ($RX + 58) ($ay - 1) 340 28 $a[1] 21 $script:SANS $script:PAPERW 'LEFT' ''
    $o += Ts ('as' + $a[0]) ($RX + 410) ($ay + 1) 258 26 $a[2] 18 $script:SANS $script:MUTED 'LEFT' ''
    $ay += 40
}

# ---- 12 household grid ----
$GY = 740; $GH = 190
$o += (Card $RX $GY 688 $GH $script:PANEL_D2 10 ('1 SOLID ' + $script:HAIRD) '')
$o += Ts 'c1-gt' ($RX + 20) ($GY + 14) 400 30 '12 户状态' 21 $script:SANS $script:PAPERW 'LEFT' ''
$o += Ts 'c1-gs' ($RX + 328) ($GY + 16) 340 26 '点色 = 态度，可逐户跟进' 17 $script:SANS $script:MUTED 'RIGHT' ''
$gx0 = $RX + 20; $gy0 = $GY + 54; $gcw = 104; $gch = 46; $gdx = 110; $gdy = 54
$order = @('601','602','501','502','401','402','301','302','201','202','101','102')
for ($k = 0; $k -lt 12; $k++) {
    $uid = $order[$k]
    $u = @($calc.households | Where-Object { $_.id -eq $uid })[0]
    $cxi = $gx0 + (($k % 6) * $gdx)
    $cyi = $gy0 + ([math]::Floor($k / 6) * $gdy)
    $o += (Box $cxi $cyi $gcw $gch (AttTint 'dark' $u.attitude) 6)
    $o += (Box $cxi $cyi 5 $gch (AttColor $u.attitude) 0)
    $o += Ts ('g' + $uid) ($cxi + 14) ($cyi + 6) ($gcw - 20) 24 $uid 19 $script:MONO $script:PAPERW 'LEFT' ''
    $o += Ts ('gs' + $uid) ($cxi + 14) ($cyi + 25) ($gcw - 20) 22 $u.attitude 16 $script:SANS (AttColor $u.attitude) 'LEFT' ''
}
Guard 'case-01' ($GY + $GH) $H

$f1 = '演示数据 DEMO：造价、补贴、报价、工期均为样例；补贴金额以当地政策核定为准（本次未取得政策原文）。剖面 = 本产品的主数据结构。'
$o += (Foot5 'c1' '01' $f1 $M 940 ($W - 2*$M) $script:HAIRD $script:MUTED)
Save 'case-01' (Page5 $W $H $script:BG_D $o) $W $H

# =====================================================================
# case-02 -- 我家出多少（分摊试算）(540 x 1180, light, 手机)
# =====================================================================
$W = 540; $H = 1180; $M = 24
$o = ''
$o += (Box 0 0 $W 84 $script:WHITE 0)
$o += Ts 'c2-brand' $M 22 220 32 '同梯 TongTi' 22 $script:DISP $script:ACC 'LEFT' ''
$o += Ts 'c2-hdr' ($W - $M - 260) 24 260 30 '梧桐里 3 号楼' 19 $script:SANS $script:MUTEL 'RIGHT' ''
$o += (HR 0 84 $W 1 $script:HAIRL)

$mh = Masthead5 '02' '居民端 · 手机' $M 104 ($W - 2*$M) $script:HAIRL $script:MUTEL $script:INK 18 18
$o += $mh[0]
$o += Ts 'c2-title' $M 164 ($W - 2*$M) 48 '我家出多少？' 36 $script:DISP $script:INK 'LEFT' ''
$o += Ts 'c2-sub' $M 216 ($W - 2*$M) 30 '切一个分摊模型，结果立刻变' 20 $script:SANS $script:MUTEL 'LEFT' ''

# household card
$y = 246
$o += (Card $M $y ($W - 2*$M) 86 $script:WHITE 10 ('1 SOLID ' + $script:HAIRL) '')
$o += (Box ($M + 14) ($y + 16) 6 54 $script:CORAL 0)
$o += Ts 'c2-hh' ($M + 32) ($y + 14) 320 30 '602 室 · 顶层东户' 24 $script:DISP $script:INK 'LEFT' ''
$o += Ts 'c2-hs' ($M + 32) ($y + 48) 340 26 '78.9 ㎡ · 当前态度：顾虑' 19 $script:SANS $script:MUTEL 'LEFT' ''
$o += (Pill ($W - $M - 104) ($y + 26) '顶层' 18 $script:SHADE $script:MUTEL $script:SANS)

# model chips
$y = 352
$chips = @(@('A', '按楼层'), @('B', '按面积'), @('C', '低层免摊'))
$cx = $M
foreach ($cp in $chips) {
    $sel = ($cp[0] -eq 'A')
    $lbl = ($cp[0] + ' ' + $cp[1])
    $cw2 = [int][Math]::Ceiling((TW $lbl 20) + 34)
    if ($sel) {
        $o += (Box $cx $y $cw2 46 $script:ACC 10)
        $o += Ts ('ch' + $cp[0]) $cx $y $cw2 46 $lbl 20 $script:SANS $script:WHITE 'CENTER' ''
    } else {
        $o += (Card $cx $y $cw2 46 $script:WHITE 10 ('1 SOLID ' + $script:HAIRL) '')
        $o += Ts ('ch' + $cp[0]) $cx $y $cw2 46 $lbl 20 $script:SANS $script:MUTEL 'CENTER' ''
    }
    $cx += ($cw2 + 12)
}

# result card
$y = 422
$o += (Card $M $y ($W - 2*$M) 214 $script:WHITE 12 ('1 SOLID ' + $script:HAIRL) '0 6 18 #15191F14')
$o += Ts 'c2-rl' ($M + 22) ($y + 18) 400 28 '按模型 A，本户自付' 20 $script:SANS $script:MUTEL 'LEFT' ''
$o += Ts 'c2-big' ($M + 22) ($y + 48) 330 92 '42,985' 74 $script:DISP $script:ACC 'LEFT' ''
$o += Ts 'c2-unit' ($M + 356) ($y + 98) 120 40 '元' 26 $script:SANS $script:INK 'LEFT' ''
$o += (HR ($M + 22) ($y + 148) ($W - 2*$M - 44) 1 $script:HAIRL)
$r2a = '权重 6.70 · 单位权重 = 288,000 ÷ 6.70 = 42,985 元'
$r2b = '各层权重 1.00 / 0.85 / 0.70 / 0.50 / 0.30 / 0.00'
$o += Ts 'c2-rn' ($M + 22) ($y + 156) ($W - 2*$M - 44) 26 $r2a 18 $script:SANS $script:INK 'LEFT' ''
$o += Ts 'c2-rn2' ($M + 22) ($y + 182) ($W - 2*$M - 44) 26 $r2b 18 $script:SANS $script:MUTEL 'LEFT' ''

# three-model compare strip
$y = 654
$o += Ts 'c2-cl' $M $y 400 28 '同一户，三种模型' 20 $script:SANS $script:INK 'LEFT' ''
$y += 32
$cmp = @(@('A 按楼层', 42985), @('B 按面积', 24386), @('C 低层免摊', 47213))
$cx = $M
foreach ($cc in $cmp) {
    $isSel = ($cc[0][0] -eq 'A')
    if ($isSel) {
        $bgc = $script:ACC; $fgc = $script:WHITE; $sbc = '#FFFFFFCC'; $brd = ''
    } else {
        $bgc = $script:WHITE; $fgc = $script:INK; $sbc = $script:MUTEL; $brd = '1 SOLID ' + $script:HAIRL
    }
    $o += (Card $cx $y 156 86 $bgc 10 $brd '')
    $o += Ts ('cm' + $cc[0]) ($cx + 12) ($y + 12) 132 24 $cc[0] 17 $script:SANS $sbc 'LEFT' ''
    $o += Ts ('cv' + $cc[0]) ($cx + 12) ($y + 38) 132 40 (N0 $cc[1]) 28 $script:MONO $fgc 'LEFT' ''
    $cx += 168
}
Guard 'case-02-compare' ($y + 86) $H

# floor-rate ladder
$y = 786
$o += Ts 'c2-ll' $M $y 460 28 '模型 A · 各层费率（顶层 = 100%）' 20 $script:SANS $script:INK 'LEFT' ''
$y += 32
$ladder = @(@('6 层', 1.00, 42985), @('5 层', 0.85, 36537), @('4 层', 0.70, 30090),
            @('3 层', 0.50, 21493), @('2 层', 0.30, 12896), @('1 层', 0.00, 0))
foreach ($ld in $ladder) {
    $isTop = ($ld[1] -eq 1.0)
    $o += Ts ('ll' + $ld[0]) $M $y 64 30 $ld[0] 19 $script:MONO $script:MUTEL 'LEFT' ''
    $o += (Box ($M + 66) ($y + 7) 200 16 $script:SHADE 8)
    $wd = 200 * [double]$ld[1]
    if ($wd -gt 0) {
        if ($isTop) { $barC = $script:ACC } else { $barC = $script:ACC2 }
        $o += (Box ($M + 66) ($y + 7) $wd 16 $barC 8)
    }
    $pctTxt = ([string][int]([double]$ld[1] * 100)) + '%'
    $o += Ts ('lp' + $ld[0]) ($M + 300) $y 84 30 $pctTxt 18 $script:MONO $script:MUTEL 'RIGHT' ''
    $o += Ts ('lv' + $ld[0]) ($M + 390) $y 102 30 ((N0 $ld[2]) + ' 元') 19 $script:MONO $script:INK 'RIGHT' ''
    $y += 32
}

# slider mock
$y = 1028
$o += (Card $M $y ($W - 2*$M) 96 $script:WHITE 10 ('1 SOLID ' + $script:HAIRL) '')
$o += Ts 'c2-sl' ($M + 18) ($y + 12) 240 26 '总造价（可调）' 18 $script:SANS $script:MUTEL 'LEFT' ''
$o += Ts 'c2-sv' ($W - $M - 180) ($y + 10) 162 30 '52.8 万元' 22 $script:MONO $script:INK 'RIGHT' ''
$trkW = $W - 2*$M - 36
$o += (Box ($M + 18) ($y + 50) $trkW 8 $script:SHADE 4)
$o += (Box ($M + 18) ($y + 50) ($trkW * 0.567) 8 $script:ACC 4)
$knx = ($M + 18 + ($trkW * 0.567) - 11)
$o += (Circ $knx ($y + 43) 22 $script:WHITE '')
$o += (Circ ($knx + 5) ($y + 48) 12 $script:ACC '')
$o += Ts 'c2-sl2' ($M + 18) ($y + 66) 200 24 '46.0 万元' 15 $script:MONO $script:MUTEL 'LEFT' ''
$o += Ts 'c2-sl3' ($W - $M - 118) ($y + 66) 100 24 '58.0 万元' 15 $script:MONO $script:MUTEL 'RIGHT' ''

$f2 = '演示数据 DEMO · 四舍五入到元，合计以 288,000 元为准。'
$o += (Foot5 'c2' '02' $f2 $M 1128 ($W - 2*$M) $script:HAIRL $script:MUTEL)
Guard 'case-02' 1168 $H
Save 'case-02' (Page5 $W $H $script:BG_L $o) $W $H

# =====================================================================
# case-03 -- 三种分摊模型对比 (1500 x 980, light, 协商会桌面)
# =====================================================================
$W = 1500; $H = 980; $M = 48
$o = ''
$mh = Masthead5 '03' '业主协商会 · 桌面' $M 40 ($W - 2*$M) $script:HAIRL $script:MUTEL $script:INK 20 20
$o += $mh[0]
$t3 = ('三种分摊模型，同一户最多差 ' + (N0 $calc.models.maxSpread) + ' 元')
$o += Ts 'c3-title' $M 96 ($W - 2*$M) 56 $t3 42 $script:DISP $script:INK 'LEFT' ''
$s3 = '自付总额恒为 288,000 元（造价 52.8 万 ' + [char]0x2212 + ' 补贴 24.0 万）· 差别只在谁出多少'
$o += Ts 'c3-sub' $M 152 980 30 $s3 21 $script:SANS $script:MUTEL 'LEFT' ''
$o += Ts 'c3-tie' ($M + $W - 2*$M - 470) 158 470 30 ('并列户：' + $calc.models.maxSpreadHousehold + ' 室') 21 $script:MONO $script:CORAL 'RIGHT' ''

# three model cards
$y = 196; $cardW = 456; $cardH = 300
$cards = @(
  @('A', $mdlA.label, ($mdlA.weightSum.ToString('0.00')), ((N0 $mdlA.unitWeight) + ' 元'), $mdlA.zeroHouseholds, $mdlA.maxHousehold, '权重 0 / 0.30 / 0.50 / 0.70 / 0.85 / 1.00'),
  @('B', $mdlB.label, '-', ($mdlB.perSqm.ToString('0.00') + ' 元/㎡'), $mdlB.zeroHouseholds, $mdlB.maxHousehold, '309.08 元/㎡ × 本户面积'),
  @('C', $mdlC.label, ($mdlC.weightSum.ToString('0.00')), ((N0 $mdlC.unitWeight) + ' 元'), $mdlC.zeroHouseholds, $mdlC.maxHousehold, '1、2 层均为 0，3 层起分摊')
)
$accents = @($script:ACC, $script:TEAL, $script:AMBER)
$cx = $M
for ($ci = 0; $ci -lt 3; $ci++) {
    $cd = $cards[$ci]
    $ac = $accents[$ci]
    $o += (Card $cx $y $cardW $cardH $script:WHITE 12 ('1 SOLID ' + $script:HAIRL) '0 8 22 #15191F10')
    $o += (Box $cx $y $cardW 6 $ac 0)
    $o += Ts ('c3-mk' + $cd[0]) ($cx + 24) ($y + 22) 60 56 $cd[0] 46 $script:DISP $ac 'LEFT' ''
    $o += Ts ('c3-mn' + $cd[0]) ($cx + 88) ($y + 32) ($cardW - 112) 34 $cd[1] 22 $script:SANS $script:INK 'LEFT' ''
    $o += (HR ($cx + 24) ($y + 78) ($cardW - 48) 1 $script:HAIRL)
    $rows3 = @(
      @('权重合计', $cd[2]),
      @('单位权重', $cd[3]),
      @('零负担户数', ('' + $cd[4] + ' 户')),
      @('单户最高', ((N0 $cd[5]) + ' 元'))
    )
    $ry = $y + 92
    foreach ($rr in $rows3) {
        $o += Ts ('c3-rl' + $rr[0] + $cd[0]) ($cx + 24) $ry 200 28 $rr[0] 19 $script:SANS $script:MUTEL 'LEFT' ''
        $o += Ts ('c3-rv' + $rr[0] + $cd[0]) ($cx + 200) $ry ($cardW - 224) 28 $rr[1] 20 $script:MONO $script:INK 'RIGHT' ''
        $ry += 34
    }
    $o += (Box ($cx + 24) ($ry + 6) ($cardW - 48) 54 $script:SHADE 8)
    $o += Ts ('c3-rule' + $cd[0]) ($cx + 36) ($ry + 14) ($cardW - 72) 40 $cd[6] 18 $script:SANS $script:MUTEL 'LEFT' ''
    $cx += ($cardW + 18)
}
Guard 'case-03-cards' ($y + $cardH) $H

# vote bar
$y = 520
$o += Ts 'c3-vt' $M $y 400 30 '协商会投票结果（演示）' 20 $script:SANS $script:INK 'LEFT' ''
$y += 32
$o += (Stack1 $M $y ($W - 2*$M) 34 @(
        @{ v = 7; c = $script:ACC }, @{ v = 3; c = $script:AMBER }, @{ v = 2; c = $script:SHADE }) 12)
$o += Ts 'c3-v1' ($M + 16) ($y + 4) 300 28 '模型 A · 7 票' 20 $script:SANS $script:WHITE 'LEFT' ''
$o += Ts 'c3-v2' ($M + (($W - 2*$M) * 0.60)) ($y + 4) 240 28 '模型 C · 3 票' 20 $script:SANS $script:INK 'LEFT' ''
$o += Ts 'c3-v3' ($M + (($W - 2*$M) * 0.86)) ($y + 4) 200 28 '未选 · 2 户' 20 $script:SANS $script:MUTEL 'LEFT' ''

# matrix table
$y = 600
$cols = @(
  @('户号', 100, 'LEFT'), @('层', 56, 'CENTER'), @('面积 ㎡', 110, 'RIGHT'), @('态度', 130, 'LEFT'),
  @('模型 A', 238, 'RIGHT'), @('模型 B', 238, 'RIGHT'), @('模型 C', 238, 'RIGHT'), @('极差', 270, 'RIGHT')
)
$o += (Box $M $y ($W - 2*$M) 32 $script:SHADE 0)
$cx2 = $M
foreach ($c2 in $cols) {
    if ($c2[2] -eq 'LEFT') { $hx = $cx2 + 12 } else { $hx = $cx2 }
    $o += Ts ('c3-h' + $c2[0]) $hx $y ($c2[1] - 12) 32 $c2[0] 18 $script:SANS $script:MUTEL $c2[2] ''
    $cx2 += $c2[1]
}
$y += 32
$rowH = 22
foreach ($u in $calc.households) {
    if ($u.attitude -eq '顾虑') { $rbg = '#FBEAE5' } else { $rbg = $script:WHITE }
    $o += (Box $M $y ($W - 2*$M) $rowH $rbg 0)
    $vals = @($u.id, [string]$u.floor, ([string]$u.area), $u.attitude,
              (N0 $u.A), (N0 $u.B), (N0 $u.C), (N0 $u.spread))
    $cx3 = $M
    for ($k = 0; $k -lt $cols.Count; $k++) {
        if ($cols[$k][2] -eq 'LEFT') { $tx = $cx3 + 12 } else { $tx = $cx3 }
        $col = $script:INK
        $fam = $script:SANS
        if ($k -eq 3) { $col = (AttColor $u.attitude) }
        if ($k -ge 4) { $fam = $script:MONO }
        if ($k -eq 7 -and $u.spread -ge 24000) { $col = $script:CORAL }
        $o += Ts ('c3-r' + $u.id + $k) $tx $y ($cols[$k][1] - 12) $rowH $vals[$k] 18 $fam $col $cols[$k][2] ''
        $cx3 += $cols[$k][1]
    }
    $o += (Box $M ($y + $rowH - 1) ($W - 2*$M) 1 $script:HAIRL 0)
    $y += $rowH
}
Guard 'case-03-table' $y $H

$y += 8
$n3 = ('同一户在三种模型下的最高与最低之差，最大为 ' + (N0 $calc.models.maxSpread) + ' 元（' + $calc.models.maxSpreadHousehold + ' 室）。')
$o += Ts 'c3-note' $M $y 1100 26 $n3 19 $script:SANS $script:MUTEL 'LEFT' ''
$f3 = '演示数据 DEMO · 分项四舍五入到元，合计以 288,000 元为准。分摊权重是本产品自定义的规则，不是法规要求。'
$o += (Foot5 'c3' '03' $f3 $M 930 ($W - 2*$M) $script:HAIRL $script:MUTEL)
Save 'case-03' (Page5 $W $H $script:BG_L $o) $W $H

Report-Problems5
