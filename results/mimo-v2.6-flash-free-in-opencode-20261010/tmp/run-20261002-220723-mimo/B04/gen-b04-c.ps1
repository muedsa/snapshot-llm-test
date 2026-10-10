# gen-b04-c.ps1 -- B04 cases 06..08 (dot-source after lib-b04.ps1)

function Get-B04-Case06 {
    Use-Case 'case-06'
    $W = 1080; $H = 1080; $M = 60
    $IW = $W - 2 * $M
    $o = ''

    $mh = Masthead '06' '算术 / ARITHMETIC' $M 56 $IW $script:HAIR $script:MUTE $script:NIGHT 18 18
    $o += $mh[0]; $y = $mh[1]

    $o += (Ts 'c6-t1' $M ($y + 24) 760 70 '为什么步长必须是 1 秒' 50 $script:SERIF $script:WHITE 'LEFT' '')
    $o += (Ts 'c6-ld' $M ($y + 104) $IW 34 '常见的解释只对了一半。真正的约束写在 CGPM 的决议里。' 21 $script:SANS $script:MUTE 'LEFT' '')

    # ---- panel A: the half-right explanation ----
    $o += (Card $M 270 468 300 $script:INK2 10 ('1 SOLID ' + $script:CORAL) '')
    $o += (Ts 'c6-at' ($M + 24) 294 420 36 '常见的解释' 24 $script:SERIF $script:CORAL 'LEFT' '')
    $o += (Box ($M + 24) 338 46 3 $script:CORAL 0)
    $o += (TBlock 'c6-ab' ($M + 24) 362 420 19 @(
        '0.2 毫秒 / 天 × 5 000 天 = 1 秒，',
        '听起来自洽，也确实是地球变慢的量级。',
        '但它不是闰秒的触发条件。',
        '真正的门槛写在另一处。'
    ) 30 $script:SANS $script:NIGHT 'LEFT' '')
    $o += (Box ($M + 24) 508 116 30 '#2E1A18' 4)
    $o += (Ts 'c6-atch' ($M + 24) 508 116 30 '只对了一半' 17 $script:SANS $script:CORAL 'CENTER' '')

    # ---- panel B: the real constraint ----
    $bx = $M + 468 + 24
    $o += (Card $bx 270 468 300 $script:INK2 10 ('1 SOLID ' + $script:AMBER) '')
    $o += (Ts 'c6-bt' ($bx + 24) 294 420 36 '真正的约束' 24 $script:SERIF $script:AMBER 'LEFT' '')
    $o += (Box ($bx + 24) 338 46 3 $script:AMBER 0)
    $o += (TBlock 'c6-bb' ($bx + 24) 362 420 19 @(
        'CGPM 决议 4：UTC 与 TAI 只相差',
        '一个整数秒。',
        '所以偏移量只能取 0、1、2、3……',
        '永远不能是 0.5 或 0.1。'
    ) 30 $script:SANS $script:NIGHT 'LEFT' '')
    $o += (Box ($bx + 24) 508 132 30 '#2C2410' 4)
    $o += (Ts 'c6-bch' ($bx + 24) 508 132 30 'CGPM 2022' 17 $script:SANS $script:AMBER 'CENTER' '')

    # ---- integer ruler ----
    $o += (Ts 'c6-rt' $M 610 $IW 34 '整数秒：允许的落点只有整数' 20 $script:MONO $script:AMBER 'LEFT' '')
    $axY = 740.0; $ax0 = $M; $ax1 = $M + $IW
    $o += (Box $ax0 $axY $IW 1 $script:HAIR 0)
    for ($i = 0; $i -le 100; $i++) {
        $x = $ax0 + $i * (($ax1 - $ax0) / 100.0)
        $o += (Box $x ($axY - 14) 2 14 '#4A5764' 0)
    }
    for ($k = 0; $k -le 10; $k++) {
        $x = $ax0 + $k * (($ax1 - $ax0) / 10.0)
        $tx = $x - 6
        if ($k -eq 10) { $tx = $ax0 + $IW - 12 }
        $o += (Box ($x - 2) ($axY - 46) 4 46 $script:AMBER 0)
        $o += (Box $tx ($axY - 58) 12 12 $script:AMBER 0)
        $o += (Ts ('c6-n' + $k) ($x - 30) ($axY + 16) 60 24 ([string]$k) 16 $script:MONO $script:MUTE 'CENTER' '')
    }
    $o += (Ts 'c6-cap' $M ($axY + 50) $IW 30 '灰色细刻度是 0.1 秒，琥珀色的粗刻度才是允许的落点。' 18 $script:SANS $script:MUTE 'LEFT' '')

    # ---- editorial calculation ----
    $o += (HR $M 836 $IW 1 $script:HAIR)
    $o += (Ts 'c6-eh' $M 852 400 34 '编辑按 · 量级估算' 20 $script:MONO $script:AMBER 'LEFT' '')
    $o += (TBlock 'c6-e1' $M 890 $IW 19 @(
        '0.2 毫秒 / 天 × 4 500 天 ≈ 0.9 秒：若地球匀速变慢，约 12 年触及阈值。',
        '但 UT1−UTC 的漂移并不匀速，真正的节奏由不规则波动决定。',
        '上式是本编辑的算术演示，不是任何来源的结论。'
    ) 30 $script:SANS $script:NIGHT 'LEFT' '')

    $o += (HR $M 990 $IW 1 $script:HAIR)
    $o += (Ts 'c6-src' $M 1002 $IW 30 '来源：IERS 常用常数（0.2 ms/天）· IERS 闰秒页（0.9 秒阈值）· BIPM CGPM 决议 4（整数秒）' 17 $script:SANS $script:MUTE 'LEFT' '')

    return (Page4 $W $H $script:INK $o)
}

function Get-B04-Case07 {
    Use-Case 'case-07'
    $W = 1920; $H = 480; $M = 50
    $IW = $W - 2 * $M
    $o = ''

    $mh = Masthead '07' '现场 / MOMENT' $M 36 $IW $script:HAIR $script:MUTE $script:NIGHT 16 16
    $o += $mh[0]; $y = $mh[1]

    # ---- left: title + quote ----
    $o += (Ts 'c7-t1' $M 96 550 72 '23:59:60 那一分钟' 50 $script:SERIF $script:WHITE 'LEFT' '')
    $o += (Ts 'c7-t2' $M 174 550 34 '2012 年 6 月 30 日，星期六' 22 $script:MONO $script:AMBER 'LEFT' '')
    $o += (TBlock 'c7-q' $M 216 550 18 @(
        '"On 30 June 2012, the last minute of',
        'the day has lasted 61 seconds."',
        '—— IERS 闰秒页'
    ) 26 $script:SANS $script:MUTE 'LEFT' '')

    # ---- middle: the 61-tick minute ----
    $sx = 640.0; $sw = 915.0
    $o += (Ts 'c7-sx' $sx 124 400 30 'THE 61-SECOND MINUTE' 18 $script:MONO $script:MUTE 'LEFT' '')
    $base7 = 300.0
    $o += (Strip61 $sx 160 $sw 140 61 $script:HAIR2 104 104 5)
    $o += (Box ($sx + $sw) ($base7 - 140) 8 140 $script:AMBER 0)
    $o += (HR $sx 310 920 1 $script:HAIR2)
    for ($k = 0; $k -le 5; $k++) {
        $tx7 = $sx + ($k * 10) * ($sw / 60.0)
        $o += (Ts ('c7-tk' + $k) ($tx7 - 30) 316 60 24 (':{0:d2}' -f ($k * 10)) 15 $script:MONO $script:MUTE 'CENTER' '')
    }
    $o += (Ts 'c7-l1' $sx 344 300 26 '23:59:00' 17 $script:MONO $script:MUTE 'LEFT' '')
    $o += (Ts 'c7-l2' ($sx + $sw - 300) 344 300 26 '23:59:60' 17 $script:MONO $script:AMBER 'RIGHT' '')
    $o += (Ts 'c7-l4' $sx 376 920 28 '前 60 个刻度等长；第 61 个插入在 23:59:60，次日 00:00:00 顺延到它之后' 18 $script:SANS $script:MUTE 'LEFT' '')

    # ---- right: three facts ----
    $fx = 1610.0; $fw = 260.0
    $facts = @(
        @{ v = '34 → 35';    l = 'TAI−UTC（秒）' },
        @{ v = '+1 s';       l = '生效 2012-07-01' },
        @{ v = 'Bulletin C'; l = 'IERS 半年公告' }
    )
    for ($k = 0; $k -lt 3; $k++) {
        $fy = 96 + $k * 96
        $o += (Box $fx $fy 4 72 $script:AMBER 0)
        $o += (Ts ('c7-fv' + $k) ($fx + 18) $fy $fw 44 $facts[$k].v 26 $script:MONO $script:AMBER 'LEFT' '')
        $o += (Ts ('c7-fl' + $k) ($fx + 18) ($fy + 46) $fw 28 $facts[$k].l 16 $script:SANS $script:MUTE 'LEFT' '')
    }

    $o += (HR $M 420 $IW 1 $script:HAIR)
    $o += (Ts 'c7-src' $M 430 $IW 30 '来源：IERS 闰秒页 · IERS Leap_Second.dat（第 25 次，TAI−UTC 34 → 35）· 抓取 2026-10-07' 16 $script:SANS $script:MUTE 'LEFT' '')

    return (Page4 $W $H $script:INK $o)
}

function Get-B04-Case08 {
    Use-Case 'case-08'
    $W = 1400; $H = 1050; $M = 70
    $IW = $W - 2 * $M
    $o = ''
    $ls = Get-LeapList

    $mh = Masthead '08' '比较 / COMPARISON' $M 52 $IW $script:PAPER3 $script:MUTE2 $script:INK 18 18
    $o += $mh[0]; $y = $mh[1]

    $o += (Ts 'c8-t1' $M ($y + 24) 760 72 '一段创纪录的静默' 52 $script:SERIF $script:INK 'LEFT' '')
    $o += (Ts 'c8-ld' $M ($y + 104) $IW 34 '两次相邻闰秒的间隔，最长的一次是 2 557 天；而现在这次更长。' 21 $script:SANS $script:MUTE2 'LEFT' '')

    # ---- aligned comparison bars ----
    $o += (Ts 'c8-h1' $M 268 $IW 30 '同一起点对齐比较（天）' 19 $script:MONO $script:MUTE2 'LEFT' '')
    $bx0 = 140.0; $scale = 880.0 / 3567.0
    $wA = 2557 * $scale; $wB = 3567 * $scale

    $o += (Ts 'c8-d1' $bx0 304 500 30 '1998-12-31 → 2005-12-31' 19 $script:MONO $script:MUTE2 'LEFT' '')
    $o += (Box $bx0 334 $wA 44 '#A79E8C' 3)
    $o += (Ts 'c8-v1' ($bx0 + $wA + 14) 342 260 34 '2 557 天' 24 $script:MONO '#7A7264' 'LEFT' '')

    $o += (Ts 'c8-d2' $bx0 396 500 30 '2016-12-31 → 2026-10-07' 19 $script:MONO $script:INK 'LEFT' '')
    $o += (Box $bx0 426 $wB 44 $script:AMBER 3)
    $o += (Ts 'c8-v2' ($bx0 + $wB + 14) 434 260 34 '3 567 天' 24 $script:MONO '#8A5A10' 'LEFT' '')

    $o += (Ts 'c8-ann' $M 486 $IW 30 '当前空窗比上一纪录长 1 010 天，约 2 年 9 个月。' 19 $script:SANS $script:CORAL 'LEFT' '')

    # ---- all 26 gaps ----
    $gaps = @()
    for ($i = 1; $i -lt $ls.Count; $i++) { $gaps += ($ls[$i].InsertedOn - $ls[$i - 1].InsertedOn).Days }
    $o += (Ts 'c8-h2' $M 540 $IW 30 '全部 26 个间隔（天）' 19 $script:MONO $script:MUTE2 'LEFT' '')

    $px0 = 140.0; $px1 = 1330.0; $base8 = 800.0
    $gmax = 2557.0; $unit8 = 220.0 / $gmax
    foreach ($g in @(500, 1000, 1500, 2000, 2500)) {
        $gy = $base8 - $g * $unit8
        $o += (DotH $px0 $gy ($px1 - $px0) '#D6CEBC' 10)
        $o += (Ts ('c8-g' + $g) $M ($gy - 10) 62 22 ([string]$g) 15 $script:MONO $script:MUTE2 'RIGHT' '')
    }
    $meanY = $base8 - 625.2 * $unit8
    $o += (DashH $px0 $meanY ($px1 - $px0) 2 $script:AMBER 10 7)
    $o += (Ts 'c8-mean' ($px0 + 6) ($meanY - 26) 190 24 '平均 625 天' 15 $script:MONO '#8A5A10' 'LEFT' '')
    $o += (Box $px0 $base8 ($px1 - $px0) 2 $script:INK 0)

    $slot8 = ($px1 - $px0) / 26.0
    $maxIdx = 0
    for ($i = 1; $i -lt $gaps.Count; $i++) { if ($gaps[$i] -gt $gaps[$maxIdx]) { $maxIdx = $i } }
    for ($i = 0; $i -lt $gaps.Count; $i++) {
        $gx = $px0 + $i * $slot8 + ($slot8 - 34) / 2.0
        $gh = $gaps[$i] * $unit8
        $col = if ($i -eq $maxIdx) { $script:CORAL } else { '#8F8674' }
        $o += (Box $gx ($base8 - $gh) 34 $gh $col 2)
    }
    $o += (Ts 'c8-x0' $px0 810 200 24 '1972-06' 15 $script:MONO $script:MUTE2 'LEFT' '')
    $o += (Ts 'c8-x1' ($px1 - 200) 810 200 24 '2016-12' 15 $script:MONO $script:MUTE2 'RIGHT' '')
    $o += (Ts 'c8-xm' ($px0 + $maxIdx * $slot8 - 60) ($base8 - $gaps[$maxIdx] * $unit8 - 26) 154 24 '2 557 天' 15 $script:MONO $script:CORAL 'CENTER' '')

    # ---- three stats ----
    $o += (HR $M 856 $IW 1 $script:PAPER3)
    $sw = [Math]::Floor(($IW - 60) / 3.0)
    $stats = @(
        @{ v = '184 天';    l = '最短：1972-06-30 → 1972-12-31' },
        @{ v = '625 天';    l = '26 个间隔的算术平均' },
        @{ v = '2 557 天';  l = '上一纪录：1998 → 2005' }
    )
    for ($k = 0; $k -lt 3; $k++) {
        $cx = $M + $k * ($sw + 30)
        $o += (Ts ('c8-sv' + $k) $cx 876 $sw 52 $stats[$k].v 44 $script:MONO $script:INK 'LEFT' '')
        $o += (Ts ('c8-sl' + $k) $cx 932 $sw 28 $stats[$k].l 16 $script:SANS $script:MUTE2 'LEFT' '')
    }

    $o += (HR $M 974 $IW 1 $script:PAPER3)
    $o += (Ts 'c8-src' $M 986 $IW 30 '来源：IERS Leap_Second.dat（抓取 2026-10-07）· 间隔、平均值与比较由本编辑据表计算' 17 $script:SANS $script:MUTE2 'LEFT' '')

    return (Page4 $W $H $script:PAPER $o)
}
