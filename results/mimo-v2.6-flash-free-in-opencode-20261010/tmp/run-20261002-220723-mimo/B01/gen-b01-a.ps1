# gen-b01-a.ps1 -- B01 showcase cases 01..05
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib-b01.ps1')

# ---------- local widgets ----------
# border must be "width style colour"; a bare colour is a PARSE_ERROR, so accept
# either the full form or a bare colour and normalise it.
function BD([string]$s) {
    if ($null -eq $s -or $s -eq '') { return '' }
    if ($s -match ' ') { return $s }
    return '1 SOLID ' + $s
}

function Panel([double]$l,[double]$t,[double]$w,[double]$h,[string]$bg,[int]$r,[string]$border) {
    $b = ''; if ($null -ne $border -and $border -ne '') { $b = ' border="' + (BD $border) + '"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" color="' + $bg + '" borderRadius="' + $r.ToString() + '"' + $b + '/></Positioned>'
}

function GradP([double]$l,[double]$t,[double]$w,[double]$h,[string]$colors,[string]$b0,[string]$e0,[int]$r,[string]$border) {
    $bd = ''; if ($null -ne $border -and $border -ne '') { $bd = ' border="' + (BD $border) + '"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" gradientType="LINEAR" gradientColors="' + $colors +
           '" gradientBegin="' + $b0 + '" gradientEnd="' + $e0 + '" borderRadius="' + $r.ToString() + '"' + $bd + '/></Positioned>'
}

function Chip([string]$id,[double]$l,[double]$t,[string]$s,[int]$fs,[string]$bg,[string]$fg,[double]$pad) {
    $w = (TW $s $fs) + 2 * $pad
    $h = [double]($fs * 1.75)
    $out = Panel $l $t $w $h $bg ([int][Math]::Round($h / 2)) $null
    $out += Txt $l ($t + ($h - $fs * 1.3) / 2) $w ($fs * 1.35) $s $fs $fg 'CENTER' ''
    return ,@($out, $w, $h)
}

# =====================================================================
# case-01  末班地铁到站屏  900x1600  站台立式 OLED
# =====================================================================
New-Case '01'
$W = 900; $H = 1600; $BG = '#060B14'
Seg (Box 0 0 $W $H $BG 0)
Seg (Grad 0 0 $W 150 '#0A1A2E,#0C2440,#0A1A2E' 'LINEAR' 'TOP_LEFT' 'BOTTOM_RIGHT' 0)
Seg (Box 0 0 $W 5 '#22F5A8' 0)

Seg (CircleGrad 44 32 44 '#38BDF8,#2563EB' 'SWEEP' '' '' $null); $script:SEG[$script:SEG.Count-1] += '/></Positioned>'
Seg (Box 54 50 24 8 '#060B14' 4)
Seg (T '01' 104 30 460 40 '临江地铁' 30 '#E8F4FF' 'LEFT' 'BOLD')
Seg (T '01' 104 74 460 28 'LINJIANG METRO · 4号线' 17 '#7FB6E8' 'LEFT' '')
Seg (T '01' 620 22 236 66 '23:47' 50 '#E8F4FF' 'RIGHT' 'BOLD')
Seg (T '01' 620 92 236 26 '周五 10月09日' 17 '#7FB6E8' 'RIGHT' '')

# hero
Seg (GradP 40 178 820 300 '#0E2E3F,#0A1B2E,#133247' 'TOP_LEFT' 'BOTTOM_RIGHT' 20 '#1E4E63')
Seg (T '01' 68 198 520 26 '下一班列车 · NEXT DEPARTURE' 18 '#6FE3FF' 'LEFT' '')
Seg (TShadow '01' 68 224 300 195 '08' 150 '#4DFFC0' '0 0 22 #35FFB8' 'LEFT' 'BOLD')
Seg (T '01' 268 336 150 46 '分钟' 34 '#CFF7E8' 'LEFT' 'BOLD')
Seg (VLine 424 208 240 2 '#1E4E63')
Seg (T '01' 452 214 380 46 '开往 机场方向' 34 '#FFFFFF' 'LEFT' 'BOLD')
Seg (T '01' 452 272 380 32 '23:55 发车 · 第 2 站台' 23 '#9FD9FF' 'LEFT' '')
Seg (T '01' 452 318 380 28 '全程 42 分钟 · 途经 11 站' 20 '#8FA8C4' 'LEFT' '')
Seg (Panel 452 366 380 14 '#0A2A38' 7 $null)
Seg (Box 452 366 304 14 '#22F5A8' 7)
Seg (T '01' 452 392 380 26 '距发车 08:00' 19 '#6FE3FF' 'LEFT' '')
Seg (Panel 68 428 300 34 '#0B3A4E' 17 $null)
Seg (T '01' 82 434 272 24 '当前站 · 市民中心' 18 '#9FFFE0' 'LEFT' 'BOLD')

# line strip
Seg (T '01' 64 506 520 32 '4号线 · 机场方向' 22 '#E8F4FF' 'LEFT' 'BOLD')
Seg (T '01' 560 506 280 32 '末班 8 分钟后发车' 20 '#4DFFC0' 'RIGHT' 'BOLD')
$nx = @(110, 350, 590, 830)
$st = @('云溪', '市民中心', '未来城', '机场')
$stSub = @('上一站', '当前站', '下一站', '终点')
$stTm = @('23:42', '23:55', '23:59', '00:11')
Seg (Box 110 596 720 6 '#1B3048' 3)
Seg (Grad 350 596 480 6 '#22F5A8,#38BDF8' 'LINEAR' 'CENTER_LEFT' 'CENTER_RIGHT' 3)
for ($i = 0; $i -lt 4; $i++) {
    $cx = $nx[$i]
    if ($i -eq 1) {
        Seg ('<Positioned left="' + (Fmt ($cx - 17)) + '" top="582" width="34" height="34"><Container width="34" height="34" shape="CIRCLE" border="4 SOLID #4DFFC0" color="#0B1626"/></Positioned>')
    } else {
        $cc = '#2A4257'
        if ($i -eq 3) { $cc = '#38BDF8' }
        Seg (Circle ($cx - 11) 588 22 $cc $null)
    }
    $fc = '#C9D8EC'; $fb = ''
    if ($i -eq 1) { $fc = '#4DFFC0'; $fb = 'BOLD' }
    Seg (T '01' ($cx - 70) 624 140 30 $st[$i] 21 $fc 'CENTER' $fb)
    Seg (T '01' ($cx - 70) 656 140 24 $stSub[$i] 16 '#6E86A6' 'CENTER' '')
    Seg (T '01' ($cx - 70) 682 140 24 $stTm[$i] 16 '#9FD9FF' 'CENTER' '')
}

# direction cards
Seg (Panel 40 740 400 250 '#0C1A2C' 18 '#1E3A52')
Seg (Box 40 740 400 5 '#22F5A8' 0)
Seg (T '01' 64 762 352 34 '开往 机场方向' 24 '#4DFFC0' 'LEFT' 'BOLD')
Seg (T '01' 64 802 352 62 '23:55' 46 '#FFFFFF' 'LEFT' 'BOLD')
Seg (T '01' 64 872 352 28 '第 2 站台 · 末班 · 4 节编组' 19 '#8FA8C4' 'LEFT' '')
$cA = Chip '01' 64 908 '末班' 16 '#103A2E' '#4DFFC0' 14; Seg $cA[0]
$cB = Chip '01' (64 + $cA[1] + 10) 908 '加开' 16 '#0E3550' '#7DD3FC' 14; Seg $cB[0]
$cC = Chip '01' (64 + $cA[1] + $cB[1] + 20) 908 '不停站' 16 '#3A2E10' '#FFD166' 14; Seg $cC[0]
Seg (T '01' 64 950 352 26 '全程 42 分钟 · 停靠 11 站 · 00:11 终到' 17 '#6E86A6' 'LEFT' '')

Seg (Panel 460 740 400 250 '#0B141F' 18 '#232F42')
Seg (Box 460 740 400 5 '#3B4A63' 0)
Seg (T '01' 484 762 352 34 '开往 江湾方向' 24 '#FF9C7A' 'LEFT' 'BOLD')
Seg (T '01' 484 802 352 62 '已发出' 46 '#5C6B84' 'LEFT' 'BOLD')
Seg (T '01' 484 872 352 28 '23:52 末班 · 该方向今日运营结束' 19 '#7C8AA2' 'LEFT' '')
$cD = Chip '01' 484 908 '运营结束' 16 '#3A1E1E' '#FF9C7A' 14; Seg $cD[0]
Seg (T '01' 484 950 352 26 '明首班 05:30 · 请留意站厅公告' 17 '#6E86A6' 'LEFT' '')

# transfer
Seg (Panel 40 1020 820 160 '#0A1626' 18 '#1E3A52')
Seg (CircleGrad 66 1046 40 '#38BDF8,#7C3AED' 'SWEEP' '' '' $null); $script:SEG[$script:SEG.Count-1] += '/></Positioned>'
Seg (T '01' 66 1054 40 30 '换' 20 '#FFFFFF' 'CENTER' 'BOLD')
Seg (T '01' 124 1044 700 34 '换乘 2 号线 · 末班 23:58' 24 '#E8F4FF' 'LEFT' 'BOLD')
Seg (T '01' 124 1086 700 30 '出站换乘（B 口）步行约 6 分钟 · 通道 23:45 后关闭' 19 '#9FD9FF' 'LEFT' '')
Seg (T '01' 124 1124 700 30 '通道关闭后请由 C 口出站绕行，约 400 米 / 6 分钟' 19 '#8FA8C4' 'LEFT' '')

# notices
Seg (T '01' 64 1212 500 32 '乘车提示' 22 '#E8F4FF' 'LEFT' 'BOLD')
Seg (Box 64 1256 4 30 '#22F5A8' 2)
Seg (T '01' 82 1256 760 30 '1 · 末班列车不设停站等待，请提前 3 分钟到达站台' 19 '#C9D8EC' 'LEFT' '')
Seg (Box 64 1302 4 30 '#38BDF8' 2)
Seg (T '01' 82 1302 760 30 '2 · 23:55 后站厅关闭，出站请由 B、C 口通行' 19 '#C9D8EC' 'LEFT' '')
Seg (Box 64 1348 4 30 '#FFD166' 2)
Seg (T '01' 82 1348 760 30 '3 · 末班时间以站内广播与调度命令为准' 19 '#C9D8EC' 'LEFT' '')

# footer
Seg (Box 40 1452 820 2 '#1E2C42' 0)
Seg (T '01' 64 1476 500 30 '临江市轨道交通集团 · 客服 96168' 18 '#7C8AA2' 'LEFT' '')
Seg (T '01' 596 1476 264 30 '演示数据 DEMO' 18 '#6FE3FF' 'RIGHT' 'BOLD')
Seg (T '01' 64 1514 780 26 'LINJIANG METRO · LAST TRAIN INFO · 屏幕编号 4-L-0712' 16 '#4A5A72' 'LEFT' '')
$L01 = Finish-Case '01' $W $H $BG

# =====================================================================
# case-02  台风应急指挥板  1920x1080  指挥中心主大屏
# =====================================================================
New-Case '02'
$W = 1920; $H = 1080; $BG = '#070A10'
Seg (Box 0 0 $W $H $BG 0)
Seg (Grad 0 0 $W 96 '#18060B,#2A0A10,#18060B' 'LINEAR' 'TOP_LEFT' 'BOTTOM_RIGHT' 0)
Seg (Box 0 96 $W 3 '#FF4D4F' 0)
Seg (T '02' 48 24 700 46 '海州市应急指挥部 · 台风 青鸾 防御' 32 '#FFE8E8' 'LEFT' 'BOLD')
Seg (T '02' 48 66 700 26 'HZ-EOC 联合值班 · 第 3 号指令 · 更新于 14:20' 17 '#F0A0A0' 'LEFT' '')
Seg (T '02' 1380 26 300 46 '14:20:00' 34 '#FFFFFF' 'RIGHT' 'BOLD')
Seg (T '02' 1380 70 300 26 '2026-10-09 周五' 16 '#F0A0A0' 'RIGHT' '')
Seg (Panel 1710 26 168 52 '#B91C1C' 10 $null)
Seg (T '02' 1710 36 168 34 'I 级响应' 24 '#FFFFFF' 'CENTER' 'BOLD')

# ---- left: typhoon track ----
Seg (Panel 48 122 820 560 '#0B1119' 14 '#26303F')
Seg (T '02' 76 144 500 32 '台风路径与风圈 · TRACKING' 21 '#E6EDF7' 'LEFT' 'BOLD')
Seg (T '02' 560 146 280 28 '中心气压 945 hPa' 18 '#FF8A8A' 'RIGHT' '')
for ($gx = 1; $gx -lt 8; $gx++) { Seg (VLine (76 + $gx * 96) 190 440 1 '#141C27') }
for ($gy = 1; $gy -lt 5; $gy++) { Seg (HLine 76 (190 + $gy * 88) 764 1 '#141C27') }
# wind circles are concentric with the storm centre at (510,340)
Seg ('<Positioned left="380" top="210" width="260" height="260"><Container width="260" height="260" shape="CIRCLE" border="2 SOLID #FF7A7C" color="#FF4D4F14"/></Positioned>')
Seg ('<Positioned left="428" top="258" width="164" height="164"><Container width="164" height="164" shape="CIRCLE" border="2 SOLID #FFB3B3" color="#FF7A7C14"/></Positioned>')
# past track runs from the lower-right up to the centre, forecast continues WNW
$tk = @(@(838,610), @(762,556), @(686,502), @(598,424), @(510,340), @(432,286), @(354,232))
for ($i = 0; $i -lt ($tk.Count - 1); $i++) {
    $x1 = [double]$tk[$i][0]; $y1 = [double]$tk[$i][1]
    $x2 = [double]$tk[$i+1][0]; $y2 = [double]$tk[$i+1][1]
    $steps = 16
    for ($k = 0; $k -lt $steps; $k++) {
        $u = $k / [double]$steps
        $px = $x1 + ($x2 - $x1) * $u
        $py = $y1 + ($y2 - $y1) * $u
        $cc = '#FF7A7C'
        if ($i -ge 4) { $cc = '#FFD166' }
        Seg (Box $px $py 7 7 $cc 4)
    }
}
for ($i = 0; $i -lt 5; $i++) { Seg (Circle ($tk[$i][0] - 7) ($tk[$i][1] - 7) 14 '#FF4D4F' $null) }
for ($i = 5; $i -lt 7; $i++) {
    Seg ('<Positioned left="' + (Fmt ($tk[$i][0] - 8)) + '" top="' + (Fmt ($tk[$i][1] - 8)) + '" width="16" height="16"><Container width="16" height="16" shape="CIRCLE" border="3 SOLID #FFD166" color="#0B1119"/></Positioned>')
}
Seg (CircleGrad 496 326 28 '#FFD166,#FF4D4F' 'SWEEP' '' '' '0 0 18 #FF4D4FAA'); $script:SEG[$script:SEG.Count-1] += '/></Positioned>'
# label sits up-right of the centre where neither the past nor the forecast leg runs
Seg (Panel 534 296 112 30 '#0B1119' 6 '#4A3020')
Seg (T '02' 540 300 100 24 '台风中心' 18 '#FFD166' 'LEFT' 'BOLD')
Seg (T '02' 76 640 400 28 '已报路径 实心 / 24h 预测 空心 / 红圈 10 级风圈' 16 '#8B9BB0' 'LEFT' '')
Seg (T '02' 480 640 360 28 '移动方向 西北西 22 km/h' 16 '#FFD166' 'RIGHT' '')

# ---- alert tiles ----
Seg (Panel 892 122 980 260 '#0B1119' 14 '#26303F')
Seg (T '02' 920 144 500 32 '预警分区 · WARNING ZONES' 21 '#E6EDF7' 'LEFT' 'BOLD')
$zones = @(
    @('滨海新区', '红色', '#FF4D4F', '风暴潮'),
    @('临港区', '橙色', '#FF9C3F', '沿海大风'),
    @('老城区', '橙色', '#FF9C3F', '城市内涝'),
    @('西山片区', '黄色', '#FFD166', '地质灾害'),
    @('高新区', '蓝色', '#5AA9FF', '短时强降水')
)
for ($i = 0; $i -lt 5; $i++) {
    $x = 920 + $i * 186
    Seg (Panel $x 190 170 168 '#0F1622' 10 $zones[$i][2])
    Seg (Box $x 190 170 6 $zones[$i][2] 0)
    Seg (T '02' $x 206 170 34 $zones[$i][1] 26 $zones[$i][2] 'CENTER' 'BOLD')
    Seg (T '02' ($x + 8) 250 154 30 $zones[$i][0] 20 '#E6EDF7' 'CENTER' 'BOLD')
    Seg (T '02' ($x + 8) 288 154 26 $zones[$i][3] 16 '#8B9BB0' 'CENTER' '')
    Seg (T '02' ($x + 8) 322 154 24 '14:00 发布' 15 '#5C6B80' 'CENTER' '')
}

# ---- risks & forces ----
Seg (Panel 892 402 480 280 '#0B1119' 14 '#26303F')
Seg (T '02' 920 424 420 32 '重点风险 · KEY RISKS' 21 '#E6EDF7' 'LEFT' 'BOLD')
$risks = @(@('西山片区 · 观澜路', '山体滑坡', '#FF4D4F'), @('老城区 · 下穿隧道 3 处', '内涝积水', '#FF9C3F'), @('滨海浴场 · 潮位 4.2 m', '风暴潮倒灌', '#FFD166'))
for ($i = 0; $i -lt 3; $i++) {
    $y = 470 + $i * 70
    Seg (Box 920 $y 5 52 $risks[$i][2] 2)
    Seg (T '02' 940 $y 400 28 $risks[$i][0] 19 '#DCE6F3' 'LEFT' 'BOLD')
    Seg (T '02' 940 ($y + 30) 400 26 $risks[$i][1] 17 $risks[$i][2] 'LEFT' '')
}

Seg (Panel 1392 402 480 280 '#0B1119' 14 '#26303F')
Seg (T '02' 1420 424 420 32 '力量部署 · FORCES' 21 '#E6EDF7' 'LEFT' 'BOLD')
$forces = @(@('2,860', '人', '应转移人员已转移'), @('14', '处', '避险安置点开放'), @('37', '支', '抢险救援队伍待命'))
for ($i = 0; $i -lt 3; $i++) {
    $y = 470 + $i * 70
    $uw = (TW $forces[$i][0] 38) + 10
    Seg (T '02' 1420 $y 240 46 $forces[$i][0] 38 '#4DFFC0' 'LEFT' 'BOLD')
    Seg (T '02' (1420 + $uw) ($y + 16) 60 28 $forces[$i][1] 19 '#8B9BB0' 'LEFT' '')
    Seg (T '02' 1420 ($y + 40) 420 26 $forces[$i][2] 17 '#AFC0D4' 'LEFT' '')
}

# ---- bottom: timeline ----
Seg (Panel 48 706 1824 326 '#0B1119' 14 '#26303F')
Seg (T '02' 76 728 560 32 '防御时间轴 · 未来 12 小时' 21 '#E6EDF7' 'LEFT' 'BOLD')
Seg (T '02' 1300 730 544 28 '预计登陆窗口 20:00 – 22:00' 18 '#FF9C3F' 'RIGHT' 'BOLD')
Seg (Box 100 826 1720 6 '#1E2A3A' 3)
$tl = @(@('14:00', 'I 级响应启动', '#FF4D4F'), @('16:30', '沿海渔船回港', '#FF9C3F'), @('18:00', '转移人员上车', '#FFD166'), @('20:30', '预计登陆', '#FF4D4F'), @('23:00', '解除沿海警戒', '#5AA9FF'))
for ($i = 0; $i -lt 5; $i++) {
    $x = 140 + $i * 400
    Seg (Circle ($x - 11) 818 22 $tl[$i][2] $null)
    Seg (T '02' ($x - 110) 776 220 34 $tl[$i][0] 24 '#FFFFFF' 'CENTER' 'BOLD')
    Seg (T '02' ($x - 110) 852 220 28 $tl[$i][1] 18 $tl[$i][2] 'CENTER' '')
}
Seg (Box 100 896 1720 1 '#1A2331' 0)
Seg (T '02' 76 910 1772 26 '数据来源：海州市气象台 / 水利站 / 交警支队联合值班室（演示数据）' 16 '#5C6B80' 'LEFT' '')
Seg (T '02' 76 946 1772 26 '值班长 陈屿 · 指挥席 A2 · 值班电话 0574-8812 3110（演示数据）' 16 '#5C6B80' 'LEFT' '')
Seg (Box 100 984 1720 1 '#1A2331' 0)
Seg (T '02' 76 996 1100 26 '海州市应急管理局 · 24 小时值守 · 本屏为演示看板 DEMO-EOC-07' 16 '#8B9BB0' 'LEFT' '')
Seg (T '02' 1200 996 648 26 '指挥席 A2 / 值班席 B1 · 切换频率 30 s' 16 '#8B9BB0' 'RIGHT' '')
$L02 = Finish-Case '02' $W $H $BG

# =====================================================================
# case-03  半程马拉松破风配速卡  1080x1440
# =====================================================================
New-Case '03'
$W = 1080; $H = 1440; $BG = '#0A0E0B'
Seg (Box 0 0 $W $H $BG 0)
Seg (Grad 0 0 $W 1440 '#0A0E0B,#0E1A12,#0A0E0B' 'LINEAR' 'TOP_LEFT' 'BOTTOM_RIGHT' 0)
# diagonal speed beams (gradient carries the fade, so no nested opacity needed)
Seg (Rotate 600 -80 300 1300 -20 (CGrad 300 1300 '#B7FF3C00,#B7FF3C33,#B7FF3C00' 'LINEAR' 'TOP_CENTER' 'BOTTOM_CENTER' 0))
Seg (Rotate 780 -60 200 1300 -20 (CGrad 200 1300 '#00E5A000,#00E5A022,#00E5A000' 'LINEAR' 'TOP_CENTER' 'BOTTOM_CENTER' 0))

Seg (Panel 48 44 984 96 '#0E1712' 16 '#1E3A28')
Seg (CircleGrad 72 68 48 '#B7FF3C,#00E5A0' 'SWEEP' '' '' $null); $script:SEG[$script:SEG.Count-1] += '/></Positioned>'
Seg (T '03' 76 80 40 30 '破' 22 '#08120C' 'CENTER' 'BOLD')
Seg (T '03' 136 62 500 36 '破风跑步俱乐部' 27 '#E9FFE0' 'LEFT' 'BOLD')
Seg (T '03' 136 100 500 26 'POFENG RUNNING · 半程马拉松配速卡' 16 '#7FA88C' 'LEFT' '')
Seg (T '03' 660 62 348 44 '1:45:00' 36 '#B7FF3C' 'RIGHT' 'BOLD')
Seg (T '03' 660 108 348 26 '目标完赛 · 净计时' 16 '#7FA88C' 'RIGHT' '')

# hero split
Seg (Panel 48 164 984 236 '#0C1510' 16 '#1E3A28')
Seg (T '03' 76 188 500 30 'PACE PLAN · 分段配速策略' 19 '#7FA88C' 'LEFT' '')
Seg (T '03' 76 224 460 96 '5''00"' 76 '#FFFFFF' 'LEFT' 'BOLD')
Seg (T '03' 76 326 460 30 '平均配速 · 每公里' 20 '#A9C7B4' 'LEFT' '')
Seg (VLine 560 200 180 2 '#1E3A28')
$kpis = @(@('10.55', '公里'), @('158', '次/分'), @('964', '米爬升'))
for ($i = 0; $i -lt 3; $i++) {
    $x = 600 + $i * 140
    Seg (T '03' $x 224 130 54 $kpis[$i][0] 34 '#B7FF3C' 'LEFT' 'BOLD')
    Seg (T '03' $x 284 130 26 $kpis[$i][1] 17 '#8FA89A' 'LEFT' '')
}
Seg (T '03' 600 330 404 30 '目标配速 5''00" / km · 波动 ±3"' 18 '#A9C7B4' 'LEFT' '')

# splits
Seg (T '03' 48 432 600 34 '分段计划 · SPLITS' 22 '#E9FFE0' 'LEFT' 'BOLD')
Seg (T '03' 640 434 392 30 '单位：分''秒" / 每 5 公里' 17 '#7FA88C' 'RIGHT' '')
$splits = @(@('05 km', '24:58', '5''00"', 0.2378), @('10 km', '49:56', '5''00"', 0.4755), @('15 km', '1:14:34', '4''56"', 0.7102), @('20 km', '1:39:20', '4''57"', 0.9460), @('21.10 km', '1:45:00', '4''58"', 1.0))
$barMax = 640.0
for ($i = 0; $i -lt 5; $i++) {
    $y = 484 + $i * 78
    Seg (T '03' 48 $y 150 34 $splits[$i][0] 23 '#E9FFE0' 'LEFT' 'BOLD')
    Seg (T '03' 48 ($y + 34) 150 26 $splits[$i][2] 17 '#B7FF3C' 'LEFT' '')
    $bw = [Math]::Round($barMax * [double]$splits[$i][3], 1)
    Seg (Panel 210 $y 640 30 '#16241B' 15 $null)
    Seg (Grad 210 $y $bw 30 '#00E5A0,#B7FF3C' 'LINEAR' 'CENTER_LEFT' 'CENTER_RIGHT' 15)
    Seg (T '03' 872 $y 160 34 $splits[$i][1] 24 '#FFFFFF' 'RIGHT' 'BOLD')
}
Seg (Box 48 878 984 1 '#1E3A28' 0)

# HR zones + fueling
Seg (Panel 48 908 480 260 '#0C1510' 16 '#1E3A28')
Seg (T '03' 76 930 420 30 '心率区间 · HR ZONES' 19 '#E9FFE0' 'LEFT' 'BOLD')
$zones3 = @(@('Z2 有氧', '148–158', '#00E5A0'), @('Z3 节奏', '159–168', '#B7FF3C'), @('Z4 阈值', '169–176', '#FFB020'), @('Z5 冲刺', '177+', '#FF5A6E'))
for ($i = 0; $i -lt 4; $i++) {
    $y = 976 + $i * 46
    Seg (Box 76 $y 14 26 $zones3[$i][2] 4)
    Seg (T '03' 104 $y 200 28 $zones3[$i][0] 18 '#CDE4D6' 'LEFT' '')
    Seg (T '03' 320 $y 180 28 $zones3[$i][1] 18 $zones3[$i][2] 'RIGHT' 'BOLD')
}
Seg (Panel 552 908 480 260 '#0C1510' 16 '#1E3A28')
Seg (T '03' 580 930 420 30 '补给与节点 · FUELING' 19 '#E9FFE0' 'LEFT' 'BOLD')
$fuel = @(@('7.5 km', '水站 · 半口水'), @('12.5 km', '能量胶 · 配水'), @('17.5 km', '盐丸 · 补水'), @('19.8 km', '冲刺前 1 km'))
for ($i = 0; $i -lt 4; $i++) {
    $y = 976 + $i * 46
    Seg (Circle 582 ($y + 4) 18 '#B7FF3C' $null)
    Seg (T '03' 614 $y 160 28 $fuel[$i][0] 18 '#B7FF3C' 'LEFT' 'BOLD')
    Seg (T '03' 760 $y 244 28 $fuel[$i][1] 17 '#A9C7B4' 'LEFT' '')
}

# notes
Seg (Panel 48 1196 984 148 '#0C1510' 16 '#1E3A28')
Seg (T '03' 76 1216 420 30 '风向与战术提示' 19 '#E9FFE0' 'LEFT' 'BOLD')
Seg (T '03' 76 1256 928 28 '前 3 km 逆风 12 km/h，配速放宽至 5''06"，跟随破风组轮换；' 18 '#CDE4D6' 'LEFT' '')
Seg (T '03' 76 1290 928 28 '15–18 km 背风段提速至 4''56"，20 km 后按体感控速，冲刺留在最后 400 m。' 18 '#CDE4D6' 'LEFT' '')

Seg (Box 48 1372 984 1 '#1E3A28' 0)
Seg (T '03' 48 1392 640 28 '第 6 届城市半程马拉松 · 2026-11-15 07:30 起跑（演示数据）' 17 '#7FA88C' 'LEFT' '')
Seg (T '03' 700 1392 332 28 '演示数据 DEMO' 17 '#B7FF3C' 'RIGHT' 'BOLD')
$L03 = Finish-Case '03' $W $H $BG

# =====================================================================
# case-04  精品咖啡烘焙曲线卡  1200x900
# =====================================================================
New-Case '04'
$W = 1200; $H = 900; $BG = '#160F0A'
Seg (Box 0 0 $W $H $BG 0)
Seg (Grad 0 0 $W 900 '#1C1109,#241610,#160F0A' 'LINEAR' 'TOP_LEFT' 'BOTTOM_RIGHT' 0)

Seg (Panel 40 36 1120 84 '#20140D' 14 '#3A2417')
Seg (CircleGrad 62 56 44 '#F59E0B,#B45309' 'SWEEP' '' '' $null); $script:SEG[$script:SEG.Count-1] += '/></Positioned>'
Seg (T '04' 66 66 36 30 '焙' 21 '#FFF7E6' 'CENTER' 'BOLD')
Seg (T '04' 124 50 620 34 '砚山烘焙 YANSHAN ROASTERY' 25 '#FFE9C7' 'LEFT' 'BOLD')
Seg (T '04' 124 88 620 26 '单品记录 · 耶加雪菲 沃卡 G1 · 水洗 · 中浅烘' 17 '#C79A6B' 'LEFT' '')
Seg (T '04' 760 50 380 34 '批次 B-2411-07' 24 '#F59E0B' 'RIGHT' 'BOLD')
Seg (T '04' 760 88 380 26 '24.0 kg 生豆 · 2026-10-09 14:06' 17 '#C79A6B' 'RIGHT' '')

# ---- chart ----
Seg (Panel 40 140 780 470 '#1E130C' 14 '#3A2417')
Seg (T '04' 64 158 460 30 '烘焙曲线 · ROAST PROFILE' 20 '#FFE9C7' 'LEFT' 'BOLD')
Seg (T '04' 500 160 300 28 '实线 BT 豆温 / 点线 ET 环境温' 16 '#C79A6B' 'RIGHT' '')
$cx0 = 100.0; $cy0 = 200.0; $cw = 690.0; $chh = 324.0
$minM = 0.0; $maxM = 11.0; $minT = 60.0; $maxT = 260.0
function Pt([double]$tm, [double]$tv) {
    $x = $script:cx0 + ($script:cw * ($tm - $script:minM) / ($script:maxM - $script:minM))
    $y = $script:cy0 + ($script:chh * (1 - ($tv - $script:minT) / ($script:maxT - $script:minT)))
    return ,@($x, $y)
}
Seg (VLine $cx0 $cy0 $chh 2 '#4A3020')
Seg (HLine $cx0 ($cy0 + $chh) $cw 2 '#4A3020')
for ($gy = 1; $gy -lt 5; $gy++) { Seg (HLine $cx0 ($cy0 + $chh * $gy / 5.0) $cw 1 '#2C1D13') }
for ($gx = 1; $gx -lt 6; $gx++) { Seg (VLine ($cx0 + $cw * $gx / 6.0) $cy0 $chh 1 '#2C1D13') }
# y-axis ticks
$yt = @(60, 110, 160, 210, 260)
for ($gy = 0; $gy -lt 5; $gy++) {
    $yy = $cy0 + $chh * (1 - ($yt[$gy] - $minT) / ($maxT - $minT))
    Seg (T '04' 56 ($yy - 12) 40 24 $yt[$gy].ToString() 14 '#8A6A4C' 'RIGHT' '')
}
$btPts = @(@(0.0,205.0),@(0.6,150.0),@(1.63,118.0),@(3.0,132.0),@(5.0,155.0),@(7.0,178.0),@(8.7,198.0),@(10.0,214.0),@(10.25,217.0))
$etPts = @(@(0.0,200.0),@(0.5,168.0),@(1.63,124.0),@(3.0,152.0),@(5.0,182.0),@(7.0,206.0),@(8.7,224.0),@(10.0,238.0),@(10.25,240.0))
for ($i = 0; $i -lt ($etPts.Count - 1); $i++) {
    $p1 = Pt $etPts[$i][0] $etPts[$i][1]; $p2 = Pt $etPts[$i+1][0] $etPts[$i+1][1]
    $steps = 20
    for ($k = 0; $k -lt $steps; $k++) {
        $u = $k / [double]$steps
        $px = $p1[0] + ($p2[0] - $p1[0]) * $u
        $py = $p1[1] + ($p2[1] - $p1[1]) * $u
        Seg (Box $px $py 5 5 '#6B7F94' 3)
    }
}
for ($i = 0; $i -lt ($btPts.Count - 1); $i++) {
    $p1 = Pt $btPts[$i][0] $btPts[$i][1]; $p2 = Pt $btPts[$i+1][0] $btPts[$i+1][1]
    $steps = 20
    for ($k = 0; $k -lt $steps; $k++) {
        $u = $k / [double]$steps
        $px = $p1[0] + ($p2[0] - $p1[0]) * $u
        $py = $p1[1] + ($p2[1] - $p1[1]) * $u
        Seg (Box $px $py 6 6 '#FFB020' 3)
    }
}
$mk = @(@('回温点 1:38', 1.63, 118.0, '#5AA9FF'), @('一爆 8:42', 8.7, 198.0, '#FF6B4A'), @('下豆 10:15', 10.25, 217.0, '#4DFFC0'))
for ($i = 0; $i -lt 3; $i++) {
    $p = Pt $mk[$i][1] $mk[$i][2]
    Seg (VLine $p[0] ($p[1] + 10) ($cy0 + $chh - $p[1] - 10) 2 $mk[$i][3])
    Seg (Circle ($p[0] - 8) ($p[1] - 8) 16 $mk[$i][3] $null)
}
# labels with their own backing plate so the curve never fights the type
Seg (Panel 178 384 160 28 '#160F0A' 6 '#4A3020')
Seg (T '04' 184 387 148 24 $mk[0][0] 15 $mk[0][3] 'LEFT' 'BOLD')
Seg (Panel 470 260 160 28 '#160F0A' 6 '#4A3020')
Seg (T '04' 476 263 148 24 $mk[1][0] 15 $mk[1][3] 'LEFT' 'BOLD')
Seg (Panel 578 224 150 28 '#160F0A' 6 '#4A3020')
Seg (T '04' 584 227 138 24 $mk[2][0] 15 $mk[2][3] 'LEFT' 'BOLD')
# x-axis ticks
$xt = @('0:00', '2:00', '4:00', '6:00', '8:00', '10:00')
for ($gx = 0; $gx -lt 6; $gx++) {
    $xx = $cx0 + $cw * $gx / 5.0
    Seg (T '04' ($xx - 45) ($cy0 + $chh + 8) 90 24 $xt[$gx] 14 '#8A6A4C' 'CENTER' '')
}
Seg (T '04' 100 566 340 26 '横轴 分:秒 · 纵轴 摄氏度' 15 '#9C7A57' 'LEFT' '')
Seg (T '04' 500 566 290 26 '本批曲线与标准区间叠合' 15 '#9C7A57' 'RIGHT' '')

# ---- right column ----
Seg (Panel 844 140 316 470 '#1E130C' 14 '#3A2417')
Seg (T '04' 868 158 268 30 '关键指标 · KEY' 20 '#FFE9C7' 'LEFT' 'BOLD')
$mets = @(@('发展率 DR', '21.4%', '#4DFFC0', '目标 18–22%'), @('失重率', '14.8%', '#FFB020', '目标 13–16%'), @('色值 Agtron', '68', '#5AA9FF', '杯测浅中烘'), @('下豆温', '217 ℃', '#FF6B4A', '一爆后 1:33'))
for ($i = 0; $i -lt 4; $i++) {
    $y = 198 + $i * 92
    Seg (T '04' 868 $y 268 24 $mets[$i][0] 16 '#C79A6B' 'LEFT' '')
    Seg (T '04' 868 ($y + 24) 268 44 $mets[$i][1] 34 $mets[$i][2] 'LEFT' 'BOLD')
    Seg (T '04' 868 ($y + 70) 268 20 $mets[$i][3] 14 '#8A6A4C' 'LEFT' '')
}
Seg (Box 868 574 268 1 '#3A2417' 0)
Seg (T '04' 868 580 268 24 '标准区间判定：全部合格' 16 '#4DFFC0' 'LEFT' 'BOLD')

# ---- process ----
Seg (Panel 40 634 1120 196 '#1E130C' 14 '#3A2417')
Seg (T '04' 64 652 400 30 '工艺节点 · PROCESS' 20 '#FFE9C7' 'LEFT' 'BOLD')
Seg (T '04' 620 654 516 28 '入豆 205 ℃ · 脱水 5''00" · 发展 2''09"' 17 '#C79A6B' 'RIGHT' '')
$steps4 = @(@('01', '入豆', '205 ℃'), @('02', '回温', '118 ℃'), @('03', '脱水段', '155 ℃'), @('04', '一爆', '198 ℃'), @('05', '下豆', '217 ℃'))
for ($i = 0; $i -lt 5; $i++) {
    $x = 64 + $i * 218
    Seg (Panel $x 698 196 106 '#241710' 10 '#3A2417')
    Seg (Box $x 698 196 5 '#F59E0B' 0)
    Seg (T '04' ($x + 14) 712 40 26 $steps4[$i][0] 17 '#F59E0B' 'LEFT' 'BOLD')
    Seg (T '04' ($x + 14) 740 168 32 $steps4[$i][1] 21 '#FFE9C7' 'LEFT' 'BOLD')
    Seg (T '04' ($x + 14) 774 168 26 $steps4[$i][2] 17 '#C79A6B' 'LEFT' '')
}
Seg (T '04' 40 850 700 26 '记录人 罗砚 · 冷却 4 分钟后封袋静置 24 h（演示数据）' 16 '#8A6A4C' 'LEFT' '')
Seg (T '04' 760 850 400 26 '演示数据 DEMO' 16 '#F59E0B' 'RIGHT' 'BOLD')
$L04 = Finish-Case '04' $W $H $BG

# =====================================================================
# case-05  独立乐队霓虹巡演海报  800x1200
# =====================================================================
New-Case '05'
$W = 800; $H = 1200; $BG = '#0A0416'
Seg (Box 0 0 $W $H $BG 0)
Seg (Grad 0 0 $W 1200 '#12062A,#26084A,#0A0416' 'LINEAR' 'TOP_LEFT' 'BOTTOM_RIGHT' 0)
Seg (Rotate 60 -300 300 1500 16 (CGrad 300 1500 '#FF2D9500,#FF2D9544,#FF2D9500' 'LINEAR' 'TOP_CENTER' 'BOTTOM_CENTER' 0))
Seg (Rotate 560 -300 220 1500 -14 (CGrad 220 1500 '#2DE2FF00,#2DE2FF3A,#2DE2FF00' 'LINEAR' 'TOP_CENTER' 'BOTTOM_CENTER' 0))
# halftone field (drawn early; every panel below sits on top of it)
for ($r = 0; $r -lt 9; $r++) {
    for ($cc = 0; $cc -lt 14; $cc++) {
        $d = [Math]::Round(3 + $r * 0.9, 1)
        Seg (Op (40 + $cc * 54) (876 + $r * 34) $d $d 0.35 (CC $d '#7A2BFF'))
    }
}

Seg (Panel 40 40 720 74 '#0A041688' 12 '#FF2D95')
Seg (T '05' 60 54 420 26 '潮汐唱片 TIDE RECORDS' 17 '#FF7ACB' 'LEFT' 'BOLD')
Seg (T '05' 60 82 420 22 '2026 全国巡演 · 城市 8 站' 15 '#9E7BD8' 'LEFT' '')
Seg (T '05' 460 60 280 36 'TOUR 2026' 24 '#2DE2FF' 'RIGHT' 'BOLD')

Seg (TStroke '05' 40 152 720 130 '北纬三十度' 96 '#FFF6FB' '#FF2D95' 3 'LEFT' '0 0 26 #FF2D95CC')
Seg (T '05' 40 286 720 40 '30°N NORTH · 巡演首站开票' 26 '#2DE2FF' 'LEFT' 'BOLD')
Seg (Box 40 344 720 4 '#FF2D95' 0)
Seg (T '05' 40 360 720 30 '主唱 韩溯 · 吉他 沈知白 · 贝斯 岑野 · 鼓 邱一鸣' 17 '#C6A9FF' 'LEFT' '')

$rows5 = @(
    @('11.07', '上海', 'MAO Livehouse', '周五 20:00', '预售 180'),
    @('11.09', '杭州', '酒球会', '周日 20:00', '预售 160'),
    @('11.14', '成都', '正火艺术中心', '周五 20:30', '预售 180'),
    @('11.16', '重庆', '坚果 NutLive', '周日 20:00', '预售 150'),
    @('11.21', '武汉', 'VOX', '周五 20:00', '预售 160'),
    @('11.23', '长沙', '46 Livehouse', '周日 20:00', '预售 150'),
    @('11.28', '深圳', '红糖罐', '周五 20:30', '预售 180'),
    @('11.30', '厦门', 'Real Live', '周日 20:00', '预售 160')
)
Seg (T '05' 40 406 400 30 '巡演场次 · DATES' 19 '#FF7ACB' 'LEFT' 'BOLD')
Seg (T '05' 400 408 360 26 '场馆 / 时间' 15 '#9E7BD8' 'RIGHT' '')
for ($i = 0; $i -lt 8; $i++) {
    $y = 446 + $i * 62
    $bgc = '#150A2B'
    if (($i % 2) -eq 1) { $bgc = '#1B0D36' }
    Seg (Panel 40 $y 720 54 $bgc 8 '#2A1650')
    Seg (Box 40 $y 5 54 '#FF2D95' 0)
    Seg (T '05' 62 ($y + 12) 100 32 $rows5[$i][0] 22 '#2DE2FF' 'LEFT' 'BOLD')
    Seg (T '05' 172 ($y + 12) 90 32 $rows5[$i][1] 22 '#FFF6FB' 'LEFT' 'BOLD')
    Seg (T '05' 272 ($y + 12) 280 32 $rows5[$i][2] 18 '#C6A9FF' 'LEFT' '')
    Seg (T '05' 556 ($y + 14) 196 28 $rows5[$i][3] 16 '#9E7BD8' 'RIGHT' '')
    Seg (T '05' 272 ($y + 34) 480 20 $rows5[$i][4] 14 '#7A5FB0' 'LEFT' '')
}
Seg (GradP 40 956 720 96 '#FF2D95,#7A2BFF' 'CENTER_LEFT' 'CENTER_RIGHT' 14 $null)
Seg (T '05' 64 972 460 34 '全站开票 · 10.20 12:00' 25 '#FFFFFF' 'LEFT' 'BOLD')
Seg (T '05' 64 1010 460 26 'VIP 380 含签名海报 · 普通票见各站' 17 '#FFE3F3' 'LEFT' '')
# QR-style block drawn from geometry (not an image asset)
$qx = 640; $qy = 968
Seg (Panel ($qx - 8) ($qy - 8) 84 84 '#FFFFFF' 8 $null)
$pat = @(@(1,1,1,1,1,0,1), @(1,0,0,0,1,0,1), @(1,0,1,0,1,1,1), @(1,0,0,0,0,0,0), @(1,1,1,0,1,1,1), @(0,0,1,1,0,1,0), @(1,1,1,0,1,0,1))
for ($r = 0; $r -lt 7; $r++) { for ($c2 = 0; $c2 -lt 7; $c2++) { if ($pat[$r][$c2] -eq 1) { Seg (Box ($qx + 4 + $c2 * 9) ($qy + 4 + $r * 9) 9 9 '#0A0416' 0) } } }
Seg (T '05' 520 992 100 26 '扫码购票' 16 '#FFE3F3' 'RIGHT' 'BOLD')

Seg (Box 40 1080 720 1 '#3A1E66' 0)
Seg (T '05' 40 1098 470 28 '演出 18:30 开场 · 19:00 暖场 · 迟到不予退换' 16 '#9E7BD8' 'LEFT' '')
Seg (T '05' 40 1132 470 28 '主办 潮汐唱片 · 协办 各城市 Livehouse' 16 '#9E7BD8' 'LEFT' '')
Seg (T '05' 520 1098 240 28 'tide.rec/tour' 17 '#2DE2FF' 'RIGHT' 'BOLD')
Seg (T '05' 520 1132 240 28 '演示数据 DEMO' 16 '#7A5FB0' 'RIGHT' '')
$L05 = Finish-Case '05' $W $H $BG

# ---------------------------------------------------------------------
"=== gen-b01-a: DSL built ==="
"case-01 = $L01 chars"
"case-02 = $L02 chars"
"case-03 = $L03 chars"
"case-04 = $L04 chars"
"case-05 = $L05 chars"
""
if ($script:PROBLEMS.Count -eq 0) { "problems = 0" } else { "problems = " + $script:PROBLEMS.Count; $script:PROBLEMS | ForEach-Object { "  " + $_ } }
