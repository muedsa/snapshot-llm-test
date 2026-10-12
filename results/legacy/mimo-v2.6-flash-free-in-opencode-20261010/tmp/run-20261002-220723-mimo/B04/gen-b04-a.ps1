# gen-b04-a.ps1 -- B04 cases 01..02 (dot-source after lib-b04.ps1)

function Get-B04-Case01 {
    Use-Case 'case-01'
    $W = 1080; $H = 1528; $M = 72
    $IW = $W - 2 * $M
    $bg = $script:INK
    $o = ''

    # left ruler spine (shared instrument motif)
    $o += (Box 40 62 3 ($H - 130) $script:AMBER 0)
    $yy = 100.0; $i = 0
    while ($yy -le ($H - 90)) {
        if ($i % 5 -eq 0) { $o += (Box 46 $yy 24 1 $script:HAIR2 0) }
        else { $o += (Box 46 $yy 13 1 $script:HAIR 0) }
        $yy += 40; $i++
    }

    $mh = Masthead '01' '封面 / COVER' $M 62 $IW $script:HAIR $script:MUTE $script:NIGHT 18 18
    $o += $mh[0]; $y = $mh[1]

    $o += (Ts 'c1-kick' $M ($y + 26) 520 34 '协调世界时 UTC 专题' 20 $script:MONO $script:AMBER 'LEFT' '')
    $o += (Ts 'c1-demo' ($M + $IW - 380) ($y + 26) 380 34 '《时间的边缘》第 03 期  DEMO' 18 $script:MONO $script:MUTE 'RIGHT' '')

    $o += (Ts 'c1-lead' $M ($y + 96) $IW 44 '一个被官方承认、却不存在的时刻' 28 $script:SANS $script:NIGHT 'LEFT' '')

    # the impossible clock reading
    $o += (Ts 'c1-big' $M 268 $IW 250 '23:59:60' 200 $script:MONO $script:AMBER 'LEFT' '')

    $o += (Box $M 540 $IW 3 $script:AMBER 0)
    $o += (Ts 'c1-t1' $M 564 $IW 150 '多出来的那一秒' 100 $script:SERIF $script:WHITE 'LEFT' '')
    $o += (Ts 'c1-t2' $M 724 $IW 50 '协调世界时（UTC）与闰秒的来历、数据与结局' 28 $script:SANS $script:MUTE 'LEFT' '')

    # 61-second minute strip
    $o += (Ts 'c1-slab' $M 800 $IW 34 '一分钟 = 61 秒' 22 $script:MONO $script:AMBER 'RIGHT' '')
    $stripTop = 840.0; $base = 972.0
    $o += (Strip61 $M $stripTop ($IW - 6) 132 61 $script:HAIR2 76 76 4)
    $o += (Box ($M + $IW - 6) ($base - 124) 8 124 $script:AMBER 0)
    $o += (HR $M 982 $IW 1 $script:HAIR)
    $o += (Ts 'c1-sl1' $M 990 300 30 '23:59:00' 19 $script:MONO $script:MUTE 'LEFT' '')
    $o += (Ts 'c1-sl2' ($M + $IW - 300) 990 300 30 '23:59:60' 19 $script:MONO $script:AMBER 'RIGHT' '')
    $o += (Ts 'c1-sl3' $M 1026 $IW 30 '前 60 个刻度等长；第 61 个只出现在 6 月 30 日或 12 月 31 日的 23:59' 20 $script:SANS $script:MUTE 'LEFT' '')

    # three anchors
    $o += (HR $M 1076 $IW 1 $script:HAIR)
    $cw = [Math]::Floor(($IW - 60) / 3.0)
    $vals = @('27', '−37 s', '2035')
    $labs = @(
        @('1972 年以来', '加入 UTC 的次数'),
        @('UTC 与 TAI', '当前的固定差值'),
        @('CGPM 决议：在这一年', '之前改变闰秒机制')
    )
    for ($k = 0; $k -lt 3; $k++) {
        $cx = $M + $k * ($cw + 30)
        $o += (Ts ('c1-v' + $k) $cx 1106 $cw 100 $vals[$k] 74 $script:MONO $script:AMBER 'LEFT' '')
        $o += (TBlock ('c1-l' + $k) $cx 1216 $cw 21 $labs[$k] 30 $script:SANS $script:NIGHT 'LEFT' '')
    }

    # editorial note
    $o += (HR $M 1300 $IW 1 $script:HAIR)
    $o += (Ts 'c1-nh' $M 1320 200 34 '编辑按' 21 $script:SERIF $script:AMBER 'LEFT' '')
    $o += (Ts 'c1-nt' $M 1358 $IW 40 '自 2016-12-31 之后，世界已经 3 567 天没有再加过一秒（截至 2026-10-07）。' 22 $script:SANS $script:NIGHT 'LEFT' '')

    # source
    $o += (HR $M 1414 $IW 1 $script:HAIR)
    $o += (TBlock 'c1-src' $M 1424 $IW 17 @(
        '数据：IERS Leap_Second.dat · Bulletin C 72（2026-07-06）',
        '来源：BIPM 第 27 届 CGPM 决议 4 / 5（2022）· IERS 闰秒页',
        '编辑与设计：Snapshot 特辑编辑部（虚构署名 DEMO）'
    ) 24 $script:SANS $script:MUTE 'LEFT' '')

    return (Page4 $W $H $script:INK $o)
}

function Get-B04-Case02 {
    Use-Case 'case-02'
    $W = 1748; $H = 760; $M = 60
    $IW = $W - 2 * $M
    $o = ''

    $mh = Masthead '02' '定义演变' $M 50 $IW $script:PAPER3 $script:MUTE2 $script:INK 18 18
    $o += $mh[0]; $y = $mh[1]

    $o += (Ts 'c2-t1' $M ($y + 26) 700 90 '一秒有多长？' 58 $script:SERIF $script:INK 'LEFT' '')
    $o += (Ts 'c2-t2' ($M + $IW - 700) ($y + 44) 700 40 '从天文到原子：定义的五次落点' 26 $script:SANS $script:MUTE2 'RIGHT' '')
    $o += (Ts 'c2-lead' $M ($y + 126) $IW 40 '「秒」不是量出来的，是约定出来的。今天这个约定正在被再次改写。' 23 $script:SANS $script:MUTE2 'LEFT' '')

    $spineY = 370
    $o += (HR $M $spineY $IW 2 $script:INK)

    $cardW = 300; $gap = 42
    $startX = [Math]::Round(($W - (5 * $cardW + 4 * $gap)) / 2.0)

    $years = @('1820', '1967', '2018', '2022', '2026 / 2030')
    $heads = @('平太阳日 ÷ 86 400', '铯-133 原子', '铯频率固定', '光学钟超出 100 倍', '下一次定义')
    $bodies = @(
        @(
            '秒最初被定义为 1820',
            '年平太阳日的 1/86400。',
            '天文时的单位，随地球',
            '自转的快慢而抖动。'
        ),
        @(
            '第 13 届 CGPM：一秒是',
            '铯 133 原子基态两个超精细',
            '能级之间跃迁辐射的',
            '9 192 631 770 个周期。'
        ),
        @(
            '第 26 届 CGPM 修订了 SI：',
            '把铯频率的数值固定为',
            '9 192 631 770 Hz。',
            '这是秒的第二次重定义。'
        ),
        @(
            '第 27 届 CGPM 决议 5：',
            '光学频率标准的精度已比',
            '现行定义的实现高出最多',
            '100 倍，启动路线图。'
        ),
        @(
            '2026 第 28 届 CGPM 选定',
            '候选物种；2030 第 29 届',
            'CGPM 通过新的秒定义。',
            '时间表由 BIPM 公布。'
        )
    )
    $tags = @('IERS 闰秒页', 'CGPM 1967', 'CGPM 2018', 'CGPM 2022', 'CGPM 2026 / 2030')
    $tagBg = @('#EFE7D4', '#E1EEF1', '#E1EEF1', '#F5E9CE', '#E6E9DE')
    $tagFg = @('#8A6A18', '#1B6A79', '#1B6A79', '#8A5A10', '#3E6B43')

    for ($k = 0; $k -lt 5; $k++) {
        $cx = $startX + $k * ($cardW + $gap)
        $mid = $cx + ($cardW / 2)
        $o += (Ts ('c2-y' + $k) $cx 290 $cardW 56 $years[$k] 40 $script:MONO $script:INK 'CENTER' '')
        $o += (Circ ($mid - 11) ($spineY - 11) 22 $script:AMBER ('2 SOLID ' + $script:INK))
        $o += (Card $cx 410 $cardW 300 $script:WHITE 10 ('1 SOLID ' + $script:PAPER3) '0 4 14 #C9C2B233')
        $o += (Ts ('c2-h' + $k) ($cx + 22) 434 ($cardW - 44) 40 $heads[$k] 25 $script:SERIF $script:INK 'LEFT' '')
        $o += (Box ($cx + 22) 484 46 3 $script:AMBER 0)
        $o += (TBlock ('c2-b' + $k) ($cx + 22) 504 ($cardW - 44) 19 $bodies[$k] 30 $script:SANS $script:MUTE2 'LEFT' '')
        $tgW = [int][Math]::Ceiling((TW $tags[$k] 17) + 22)
        $o += (Box ($cx + 22) 666 $tgW 30 $tagBg[$k] 4)
        $o += (Ts ('c2-tg' + $k) ($cx + 22) 666 $tgW 30 $tags[$k] 17 $script:SANS $tagFg[$k] 'CENTER' '')
    }

    $o += (HR $M 720 $IW 1 $script:PAPER3)
    $o += (Ts 'c2-src' $M 730 $IW 30 '来源：BIPM 第 27 届 CGPM 决议 5（2022，DOI 10.59161/CGPM2022RES5E）· BIPM《秒的重定义》· IERS 闰秒页' 17 $script:SANS $script:MUTE2 'LEFT' '')

    return (Page4 $W $H $script:PAPER $o)
}
