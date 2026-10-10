# gen-b04-d.ps1 -- B04 cases 09..10 (dot-source after lib-b04.ps1)

function Get-B04-Case09 {
    Use-Case 'case-09'
    $W = 800; $H = 2000; $M = 64
    $IW = $W - 2 * $M
    $o = ''

    $mh = Masthead '09' '决策 / DECISION' $M 64 $IW $script:HAIR $script:MUTE $script:NIGHT 18 18
    $o += $mh[0]; $y = $mh[1]

    $o += (Ts 'c9-t1' $M ($y + 24) $IW 64 '决定：从 0.9 秒到 2035' 46 $script:SERIF $script:WHITE 'LEFT' '')
    $o += (Ts 'c9-ld' $M ($y + 96) $IW 34 '谁在决定，以及 2035 年到底会发生什么。' 20 $script:SANS $script:MUTE 'LEFT' '')

    $spineX = 110.0
    $o += (Box $spineX 290 3 1320 $script:HAIR2 0)

    $nodes = @(
        @{ y = '1972'; c = $script:CYAN; l = @(
            'UTC 改用原子时标：TAI−UTC = 10 s，',
            '并规定 |UT1 − UTC| 必须小于 0.9 秒。') },
        @{ y = '2012'; c = $script:CYAN; l = @(
            '6 月 30 日插入闰秒，TAI−UTC 变为 35 s。',
            '这是 1972 年以来的第 25 次。') },
        @{ y = '2016'; c = $script:CYAN; l = @(
            '12 月 31 日第 27 次，也是至今最后一次。',
            'TAI−UTC 由 36 秒变为 37 秒。') },
        @{ y = '2017'; c = $script:CYAN; l = @(
            '1 月 1 日起 UTC−TAI = −37 s，至今未变。',
            '至此共加过 27 秒，此后一直空窗。') },
        @{ y = '2018'; c = $script:AMBER; l = @(
            '第 26 届 CGPM：UTC 是唯一推荐的国际参考时标。',
            '民用时间与国际参考均以它为准。') },
        @{ y = '2022'; c = $script:AMBER; l = @(
            '第 27 届 CGPM 决议 4：|UT1−UTC| 上限将在 2035 年',
            '之前提高；并指出可能出现首次负闰秒。') },
        @{ y = '2026'; c = $script:AMBER; l = @(
            '第 28 届 CGPM：决议 4 要求提交实施计划。',
            '同届会议还要审定新的秒定义物种。') },
        @{ y = '2030'; c = $script:AMBER; l = @(
            '第 29 届 CGPM：通过新的秒定义（决议 5）。',
            '决议 5 把通过时间定在这一年。') },
        @{ y = '2035'; c = $script:CORAL; l = @(
            '闰秒机制的调整目标年份。',
            '目标：提高 |UT1−UTC| 上限，改变 UTC 的调整方式。') }
    )

    for ($k = 0; $k -lt $nodes.Count; $k++) {
        $ny = 290 + $k * 165
        $o += (Circ ($spineX - 8) ($ny - 8) 19 $nodes[$k].c ('3 SOLID ' + $script:INK))
        $o += (Ts ('c9-y' + $k) 140 ($ny - 10) 130 34 $nodes[$k].y 24 $script:MONO $nodes[$k].c 'LEFT' '')
        $o += (TBlock ('c9-l' + $k) 140 ($ny + 30) 596 19 $nodes[$k].l 28 $script:SANS $script:NIGHT 'LEFT' '')
    }

    $o += (Card $M 1770 $IW 130 $script:INK2 10 ('1 SOLID ' + $script:CORAL) '')
    $o += (TBlock 'c9-cl' ($M + 24) 1794 ($IW - 48) 20 @(
        '决议 4 同时提醒：地球自转的近期观测显示，',
        '可能出现有史以来第一次「负闰秒」——',
        '它的插入从未被预见，也从未被测试过。'
    ) 32 $script:SANS $script:AMBER 'LEFT' '')

    $o += (HR $M 1910 $IW 1 $script:HAIR)
    $o += (TBlock 'c9-src' $M 1918 $IW 17 @(
        '来源：BIPM 第 27 届 CGPM 决议 4 / 5（2022）',
        'DOI 10.59161/CGPM2022RES4E · IERS 闰秒页 · Bulletin C 72',
        '· 抓取 2026-10-07 · 时间线由本编辑整理，节点均为来源原话'
    ) 24 $script:SANS $script:MUTE 'LEFT' '')

    return (Page4 $W $H $script:INK $o)
}

function Get-B04-Case10 {
    Use-Case 'case-10'
    $W = 1600; $H = 640; $M = 60
    $IW = $W - 2 * $M
    $o = ''

    $mh = Masthead '10' '收尾 / CLOSING' $M 48 $IW $script:PAPER3 $script:MUTE2 $script:INK 17 17
    $o += $mh[0]; $y = $mh[1]

    # ---------------- left: the negative leap second ----------------
    $lx = 60.0; $lw = 710.0
    $o += (Card $lx 120 $lw 420 $script:INK2 12 ('1 SOLID ' + $script:CORAL) '')
    $o += (Ts 'c10-lt' ($lx + 28) 148 654 40 '反向的一秒：负闰秒' 28 $script:SERIF $script:CORAL 'LEFT' '')
    $o += (Box ($lx + 28) 194 60 3 $script:CORAL 0)
    $o += (TBlock 'c10-lb' ($lx + 28) 216 654 19 @(
        'CGPM 决议 4（2022）写道：地球自转的',
        '近期观测显示，可能需要首次「负闰秒」，',
        '而它的插入「从未被预见，也未被测试过」。',
        '—— 以下为编辑解释，非引文：',
        '负闰秒意味着删掉一个 23:59:59，世界时',
        '第一次跳过一秒钟。目前没有现成系统、',
        '没有历史样本，也没有可以照抄的先例。'
    ) 30 $script:SANS $script:NIGHT 'LEFT' '')

    # mini diagram: the skipped tick
    $mxx = $lx + 28; $mw = 654.0
    $o += (HR $mxx 440 $mw 1 $script:HAIR2)
    $tk = @('23:59:58', '23:59:59', '00:00:00')
    for ($k = 0; $k -lt 3; $k++) {
        $tx = $mxx + $k * 224
        if ($k -eq 1) {
            $o += (Card $tx 454 44 44 '#241614' 4 ('2 SOLID ' + $script:CORAL) '')
            $o += (Box ($tx + 8) 474 28 3 $script:CORAL 0)
            $o += (Ts ('c10-mx' + $k) $tx 506 210 24 '跳过（拟议）' 16 $script:SANS $script:CORAL 'LEFT' '')
        } else {
            $o += (Card $tx 454 44 44 '#182128' 4 ('2 SOLID ' + $script:HAIR) '')
            $o += (Box ($tx + 20) 464 4 24 $script:NIGHT 0)
            $o += (Ts ('c10-mx' + $k) $tx 506 210 24 '保留' 16 $script:SANS $script:MUTE 'LEFT' '')
        }
        $o += (Ts ('c10-mt' + $k) ($tx + 58) 462 160 26 $tk[$k] 17 $script:MONO $script:NIGHT 'LEFT' '')
    }

    # ---------------- right: the toolbox ----------------
    $rx = 830.0; $rw = 710.0
    $o += (Card $rx 120 $rw 420 $script:INK2 12 ('1 SOLID ' + $script:AMBER) '')
    $o += (Ts 'c10-rt' ($rx + 28) 148 460 40 '工具箱：给工程师的 6 条' 28 $script:SERIF $script:AMBER 'LEFT' '')
    $o += (Box ($rx + 28) 194 60 3 $script:AMBER 0)
    $o += (Box ($rx + $rw - 28 - 108) 148 108 32 '#2C2410' 4)
    $o += (Ts 'c10-rtag' ($rx + $rw - 28 - 108) 148 108 32 '编辑建议' 16 $script:SANS $script:AMBER 'CENTER' '')

    $items = @(
        '别假设一天总是 86 400 秒：按 UTC 语义处理。',
        '存储与比对用连续时标（TAI 或 Unix 秒），并写明口径。',
        '显示层与本地时区分开，闰秒只发生在 UTC 层。',
        '测试用例里放一个 23:59:60，也放一个不存在的 23:59:59。',
        '长周期（超过 27 年）调度按 TAI 计算，避免累积偏差。',
        '每年 1 月与 7 月查 IERS Bulletin C；关注 2026 年 CGPM。'
    )
    for ($k = 0; $k -lt 6; $k++) {
        $iy = 216 + $k * 52
        $o += (Box ($rx + 28) $iy 26 26 $script:AMBER 3)
        $o += (Ts ('c10-in' + $k) ($rx + 28) $iy 26 26 ([string]($k + 1)) 16 $script:MONO $script:INK 'CENTER' '')
        $o += (Ts ('c10-it' + $k) ($rx + 66) ($iy + 2) 614 26 $items[$k] 18 $script:SANS $script:NIGHT 'LEFT' '')
    }

    $o += (HR $M 566 $IW 1 $script:PAPER3)
    $o += (Ts 'c10-src' $M 576 $IW 30 '来源：BIPM CGPM 决议 4 / 5（2022）· IERS Bulletin C 72（2026-07-06）· 工具箱 6 条为编辑建议，非来源结论' 16 $script:SANS $script:MUTE2 'LEFT' '')

    return (Page4 $W $H $script:PAPER $o)
}
