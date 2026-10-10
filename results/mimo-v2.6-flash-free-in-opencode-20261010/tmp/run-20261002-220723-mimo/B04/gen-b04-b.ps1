# gen-b04-b.ps1 -- B04 cases 03..05 (dot-source after lib-b04.ps1)

function Get-B04-Case03 {
    Use-Case 'case-03'
    $W = 1920; $H = 1080; $M = 70
    $IW = $W - 2 * $M
    $o = ''

    $mh = Masthead '03' '机制 / MECHANISM' $M 60 $IW $script:HAIR $script:MUTE $script:NIGHT 18 18
    $o += $mh[0]; $y = $mh[1]

    $o += (Ts 'c3-t1' $M ($y + 26) 780 80 '1972 年的三条钟' 56 $script:SERIF $script:WHITE 'LEFT' '')
    $o += (Ts 'c3-t2' ($M + $IW - 760) ($y + 44) 760 40 'UT1 · TAI · UTC 的分工' 26 $script:MONO $script:MUTE 'RIGHT' '')
    $o += (Ts 'c3-ld' $M ($y + 118) $IW 40 '闰秒不是给原子钟加的，是给地球自转与原子时之间留的余量。' 23 $script:SANS $script:NIGHT 'LEFT' '')

    $labX = $M; $labW = 210; $trkX = 300.0; $trkW = 860.0

    # --- TAI lane ---
    $o += (Ts 'c3-l1' $labX 292 $labW 34 'TAI 国际原子时' 22 $script:MONO $script:CYAN 'LEFT' '')
    $o += (Ts 'c3-s1' $labX 324 $labW 28 '连续、不跳变' 17 $script:SANS $script:MUTE 'LEFT' '')
    $o += (Box $trkX 368 $trkW 3 $script:CYAN 0)
    $o += (Ts 'c3-arr' ($trkX + $trkW + 8) 354 56 34 '→' 28 $script:MONO $script:CYAN 'LEFT' '')
    $o += (Ts 'c3-a1' $trkX 384 $trkW 28 'BIPM 用全球原子钟网络连续计算' 17 $script:SANS $script:MUTE 'LEFT' '')

    # --- UTC lane (staircase) ---
    $o += (Ts 'c3-l2' $labX 428 $labW 34 'UTC 协调世界时' 22 $script:MONO $script:AMBER 'LEFT' '')
    $o += (Ts 'c3-s2' $labX 460 $labW 28 '= TAI − 整数秒' 17 $script:SANS $script:MUTE 'LEFT' '')
    $bx = $trkX; $by = 580.0; $segW = 140.0; $rise = 16.0
    for ($k = 0; $k -lt 6; $k++) {
        $sy2 = $by - $k * $rise
        $o += (Box ($bx + $k * $segW) $sy2 $segW 3 $script:AMBER 0)
        if ($k -lt 5) { $o += (Box ($bx + ($k + 1) * $segW) ($sy2 - $rise) 3 $rise $script:AMBER 0) }
    }
    $o += (Ts 'c3-a2' $trkX 596 $trkW 28 '每次 +1 秒，1972 年以来共 27 次' 17 $script:SANS $script:MUTE 'LEFT' '')

    # --- UT1 lane (schematic wave) ---
    $o += (Ts 'c3-l3' $labX 644 $labW 34 'UT1 世界时' 22 $script:MONO $script:NIGHT 'LEFT' '')
    $o += (Ts 'c3-s3' $labX 676 $labW 28 '地球自转定义' 17 $script:SANS $script:MUTE 'LEFT' '')
    $wy = 736.0; $amp = 36.0
    $prevY = $wy - (-1.0 * [Math]::Sin(0.0) * $amp)
    $prevY = $wy
    $xw = $trkX
    while ($xw -le ($trkX + $trkW - 5)) {
        $frac = ($xw - $trkX) / $trkW
        $off = -1.0 * [Math]::Sin($frac * [Math]::PI * 5.0) * $amp
        $curY = $wy + $off
        $top = [Math]::Min($prevY, $curY)
        $seg = [Math]::Abs($curY - $prevY) + 4
        $o += (Box $xw $top 6 $seg $script:NIGHT 0)
        $prevY = $curY
        $xw += 5
    }
    $o += (Ts 'c3-a3' $trkX 788 $trkW 28 '不均匀：既会走快，也会走慢' 17 $script:SANS $script:MUTE 'LEFT' '')

    # --- the 0.9 s rule ---
    $o += (Card $trkX 836 $trkW 56 '#1A242E' 8 ('1 SOLID ' + $script:AMBER) '')
    $o += (Ts 'c3-cal' $trkX 836 $trkW 56 '规则：|UT1 − UTC| 必须保持在 0.9 秒以内' 22 $script:MONO $script:AMBER 'CENTER' '')
    $o += (Ts 'c3-free' $trkX 908 $trkW 28 '示意图，纵向未按比例（SCALE FREE）' 17 $script:SANS $script:MUTE 'LEFT' '')

    # --- right: three definition cards ---
    $rx = 1230.0; $rw = 620.0
    $cards = @(
        @{ t = 'TAI · 国际原子时'; c = $script:CYAN; l = @(
            'BIPM 用全球原子钟网络连续计算的时标。',
            '不跳变、不调整，是所有时间计量的原始',
            '参考，也是闰秒要对齐的那一端。') },
        @{ t = 'UTC · 协调世界时'; c = $script:AMBER; l = @(
            '与 TAI 保持同一速率，只相差一个整数秒。',
            '1972 年起成为各国民用时间的基础，也是',
            '航空、金融与计算机共用的时间口径。') },
        @{ t = 'UT1 · 世界时'; c = $script:NIGHT; l = @(
            '由地球自转定义，现在用甚长基线干涉测量',
            '（VLBI）观测得到。它并不均匀，因此要靠',
            '闰秒把它拉回 UTC 附近。') }
    )
    for ($k = 0; $k -lt 3; $k++) {
        $cy = 292 + $k * 220
        $o += (Card $rx $cy $rw 200 $script:INK2 10 ('1 SOLID ' + $script:HAIR) '')
        $o += (Ts ('c3-ct' + $k) ($rx + 26) ($cy + 26) ($rw - 52) 40 $cards[$k].t 28 $script:MONO $cards[$k].c 'LEFT' '')
        $o += (Box ($rx + 26) ($cy + 74) 46 3 $cards[$k].c 0)
        $o += (TBlock ('c3-cb' + $k) ($rx + 26) ($cy + 96) ($rw - 52) 19 $cards[$k].l 30 $script:SANS $script:NIGHT 'LEFT' '')
    }

    $o += (HR $M 1000 $IW 1 $script:HAIR)
    $o += (Ts 'c3-src' $M 1012 $IW 30 '来源：IERS 闰秒页与常用常数（hpiers.obspm.fr）· BIPM 第 27 届 CGPM 决议 4（2022）· 示意图由编辑绘制' 17 $script:SANS $script:MUTE 'LEFT' '')

    return (Page4 $W $H $script:INK $o)
}

function Get-B04-Case04 {
    Use-Case 'case-04'
    $W = 1200; $H = 1600; $M = 60
    $o = ''
    $ls = Get-LeapList
    $rowsAll = Get-LeapRows

    $mh = Masthead '04' '数据 / DATA' $M 56 1080 $script:PAPER3 $script:MUTE2 $script:INK 18 18
    $o += $mh[0]; $y = $mh[1]

    $o += (Ts 'c4-t1' $M ($y + 28) 700 76 '27 次闰秒全表' 54 $script:SERIF $script:INK 'LEFT' '')
    $o += (Ts 'c4-t2' $M ($y + 112) 1080 34 '1972-06-30 至 2016-12-31 · 全部 27 次都发生在 6 月或 12 月的最后一天' 21 $script:SANS $script:MUTE2 'LEFT' '')

    # column layout: x, width, align
    $cols = @(
        @{ x = 60;   w = 48;  h = '#';             a = 'CENTER' },
        @{ x = 116;  w = 210; h = '插入日期 (UTC)'; a = 'LEFT'   },
        @{ x = 334;  w = 210; h = '生效起 (UTC)';   a = 'LEFT'   },
        @{ x = 552;  w = 130; h = 'MJD';            a = 'LEFT'   },
        @{ x = 690;  w = 170; h = 'TAI−UTC (s)';    a = 'LEFT'   },
        @{ x = 868;  w = 170; h = '距上次 (天)';     a = 'LEFT'   },
        @{ x = 1046; w = 94;  h = '月';             a = 'CENTER' }
    )

    # header strip
    $o += (Box $M 258 1080 46 $script:INK 0)
    foreach ($c in $cols) {
        $o += (Ts ('c4-h-' + $c.h) $c.x 270 $c.w 26 $c.h 19 $script:SANS $script:WHITE $c.a '' )
    }

    $y0 = 312.0; $rh = 38.0
    $gaps = @(0)
    for ($i = 1; $i -lt $ls.Count; $i++) { $gaps += ($ls[$i].InsertedOn - $ls[$i - 1].InsertedOn).Days }

    for ($i = 0; $i -lt $ls.Count; $i++) {
        $ry = $y0 + $i * $rh
        $rowFg = $script:INK
        if ($i -eq ($ls.Count - 1)) {
            $o += (Box $M $ry 1080 $rh '#F7E7C4' 0)
            $o += (Box $M $ry 6 $rh $script:AMBER 0)
            $rowFg = '#8A5A10'
        } elseif ($i % 2 -eq 1) { $o += (Box $M $ry 1080 $rh '#EAE4D6' 0) }
        $r = $ls[$i]
        $no = ('{0:d2}' -f ($i + 1))
        $gapTxt = if ($i -eq 0) { '—' } else { [string]$gaps[$i] }
        $monTxt = '{0} 月' -f $r.Mon
        $cells = @(
            @{ v = $no;                     a = 'CENTER' },
            @{ v = $r.DateStr;              a = 'LEFT'   },
            @{ v = $r.EffectiveFrom;        a = 'LEFT'   },
            @{ v = [string]$r.MJD;          a = 'LEFT'   },
            @{ v = [string]$r.NewTAI;       a = 'LEFT'   },
            @{ v = $gapTxt;                 a = 'LEFT'   },
            @{ v = $monTxt;                 a = 'CENTER' }
        )
        for ($k = 0; $k -lt 7; $k++) {
            $o += (Ts ('c4-r' + $i + '-' + $k) $cols[$k].x ($ry + 8) $cols[$k].w 26 $cells[$k].v 20 $script:MONO $rowFg $cells[$k].a '')
        }
    }

    # summary strip
    $o += (Box $M 1366 1080 56 $script:INK 0)
    $o += (Ts 'c4-sum' ($M + 24) 1380 1032 32 '合计 27 次 · TAI−UTC 10 s → 37 s · 平均间隔 625 天 · 最长 2 557 天' 21 $script:MONO $script:AMBER 'LEFT' '')

    $o += (TBlock 'c4-note' $M 1440 1080 18 @(
        '口径：插入日期 = 生效日期前一天的 23:59:60；MJD 为生效首日（IERS Leap_Second.dat）。',
        '1972-01-01 的 10 s 是初始值，不计入 27 次；37 − 10 = 27。'
    ) 26 $script:SANS $script:MUTE2 'LEFT' '')

    $o += (HR $M 1516 1080 1 $script:PAPER3)
    $o += (Ts 'c4-src' $M 1528 1080 30 '来源：IERS / 巴黎天文台 hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat（抓取 2026-10-07，Bulletin C 72）' 17 $script:SANS $script:MUTE2 'LEFT' '')

    return (Page4 $W $H $script:PAPER $o)
}

function Get-B04-Case05 {
    Use-Case 'case-05'
    $W = 1100; $H = 1500; $M = 70
    $IW = $W - 2 * $M
    $o = ''
    $ls = Get-LeapList

    $mh = Masthead '05' '分布 / DISTRIBUTION' $M 56 $IW $script:HAIR $script:MUTE $script:NIGHT 18 18
    $o += $mh[0]; $y = $mh[1]

    $o += (Ts 'c5-t1' $M ($y + 26) 700 78 '27 次的节奏' 56 $script:SERIF $script:WHITE 'LEFT' '')
    $o += (Ts 'c5-t2' $M ($y + 112) $IW 34 '按十年与按年份观察闰秒密度的变化（1972 – 2026）' 21 $script:SANS $script:MUTE 'LEFT' '')

    # ---------- chart 1: by decade ----------
    $o += (Ts 'c5-h1' $M 256 $IW 34 '按十年统计（次数）' 20 $script:MONO $script:AMBER 'LEFT' '')
    $px0 = 122.0; $px1 = 1030.0; $base = 646.0
    $unit = 300.0 / 9.0
    $dec = @( @{ n = '1970s'; v = 9 }, @{ n = '1980s'; v = 6 }, @{ n = '1990s'; v = 7 },
              @{ n = '2000s'; v = 2 }, @{ n = '2010s'; v = 3 }, @{ n = '2020s'; v = 0 } )
    $slot = ($px1 - $px0) / 6.0
    # gridlines
    foreach ($g in @(3, 6, 9)) {
        $gy = $base - $g * $unit
        $o += (DotH $px0 $gy ($px1 - $px0) $script:HAIR 10)
        $o += (Ts ('c5-g' + $g) $M ($gy - 12) 44 24 ([string]$g) 17 $script:MONO $script:MUTE 'RIGHT' '')
    }
    $o += (Box $px0 $base ($px1 - $px0) 2 $script:HAIR2 0)
    for ($k = 0; $k -lt 6; $k++) {
        $bx = $px0 + $k * $slot + ($slot - 96) / 2.0
        $hh = $dec[$k].v * $unit
        if ($dec[$k].v -gt 0) {
            $col = if ($dec[$k].v -ge 6) { $script:AMBER } else { '#8A6A2E' }
            $o += (Box $bx ($base - $hh) 96 $hh $col 3)
            $o += (Ts ('c5-v' + $k) $bx ($base - $hh - 36) 96 30 ([string]$dec[$k].v) 24 $script:MONO $script:AMBER 'CENTER' '')
        } else {
            $o += (Box $bx ($base - 4) 96 4 $script:CORAL 0)
            $o += (Ts 'c5-vz' $bx ($base - 36) 96 30 '0' 24 $script:MONO $script:CORAL 'CENTER' '')
        }
        $o += (Ts ('c5-d' + $k) ($bx - 20) ($base + 14) 136 30 $dec[$k].n 18 $script:MONO $script:MUTE 'CENTER' '')
    }

    $o += (HR $M 700 $IW 1 $script:HAIR)

    # ---------- chart 2: by year ----------
    $o += (Ts 'c5-h2' $M 724 $IW 34 '按年份分布（1972 – 2026，共 55 年）' 20 $script:MONO $script:AMBER 'LEFT' '')
    $cnt = @{}
    foreach ($l in $ls) { if ($cnt.ContainsKey([int]$l.Y)) { $cnt[[int]$l.Y] += 1 } else { $cnt[[int]$l.Y] = 1 } }
    $cw2 = 74.0; $stepX = 80.6; $ch2 = 60.0; $stepY = 66.0
    $mx0 = 150.0; $my0 = 770.0
    $rowLbl = @('72–82', '83–93', '94–04', '05–15', '16–26')
    for ($r2 = 0; $r2 -lt 5; $r2++) {
        $o += (Ts ('c5-rl' + $r2) $M ($my0 + $r2 * $stepY + 20) 72 24 $rowLbl[$r2] 15 $script:MONO $script:MUTE 'RIGHT' '')
        for ($c2 = 0; $c2 -lt 11; $c2++) {
            $yr = 1972 + $r2 * 11 + $c2
            $cx2 = $mx0 + $c2 * $stepX
            $cy2 = $my0 + $r2 * $stepY
            $has = $cnt.ContainsKey($yr)
            if ($has) { $bg2 = '#2E2415'; $fg2 = $script:AMBER; $dot = $script:AMBER }
            else { $bg2 = '#141C24'; $fg2 = $script:MUTE; $dot = $script:HAIR2 }
            $o += (Box $cx2 $cy2 $cw2 $ch2 $bg2 6)
            $lbl = ([string]($yr - 2000 + 2000)).Substring(2)
            if ($has -and $cnt[$yr] -gt 1) { $lbl = $lbl + '·' + [string]$cnt[$yr] }
            $o += (Ts ('c5-y' + $yr) $cx2 ($cy2 + 8) $cw2 24 $lbl 16 $script:MONO $fg2 'CENTER' '')
            $o += (Circ ($cx2 + ($cw2 - 14) / 2.0) ($cy2 + 34) 14 $dot '')
        }
    }

    $lgY = 1120.0
    $o += (Box $M $lgY 18 18 '#2E2415' 4)
    $o += (Circ ($M + 3) ($lgY + 3) 12 $script:AMBER '')
    $o += (Ts 'c5-lg1' ($M + 28) $lgY 200 24 '该年有闰秒' 18 $script:SANS $script:NIGHT 'LEFT' '')
    $o += (Box ($M + 240) $lgY 18 18 '#141C24' 4)
    $o += (Circ ($M + 243) ($lgY + 3) 12 $script:HAIR2 '')
    $o += (Ts 'c5-lg2' ($M + 268) $lgY 160 24 '无闰秒' 18 $script:SANS $script:NIGHT 'LEFT' '')
    $o += (Ts 'c5-lg3' ($M + 470) $lgY 490 24 '（1972 年有 2 次：6-30 与 12-31）' 18 $script:SANS $script:MUTE 'LEFT' '')

    $o += (TBlock 'c5-in' $M 1164 $IW 20 @(
        '1970 年代 9 次，1990 年代 7 次；2000 年代降到 2 次。',
        '2020 年代 0 次 —— 自 2017-01-01 起没有再加过一秒。',
        '按年看，2017 年之后的格子全是空的。'
    ) 32 $script:SANS $script:NIGHT 'LEFT' '')

    $o += (Card $M 1286 $IW 108 $script:INK2 8 ('1 SOLID ' + $script:HAIR) '')
    $o += (TBlock 'c5-fc' ($M + 24) 1306 ($IW - 48) 20 @(
        '只用过两个月的最后一天：6 月 11 次，12 月 16 次。',
        '平均间隔 625 天；最长 2 557 天（1998-12-31 → 2005-12-31）。'
    ) 32 $script:SANS $script:AMBER 'LEFT' '')

    $o += (HR $M 1430 $IW 1 $script:HAIR)
    $o += (Ts 'c5-src' $M 1442 $IW 30 '来源：IERS Leap_Second.dat（Bulletin C 72，抓取 2026-10-07）· 分组与间隔由本编辑据表计算' 17 $script:SANS $script:MUTE 'LEFT' '')

    return (Page4 $W $H $script:INK $o)
}
