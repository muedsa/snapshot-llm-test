$ErrorActionPreference = 'Stop'
. (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03\lib-b03.ps1')
$OUT = $script:B03OUT
$SANS = $script:SANS
$SERIF = $script:SERIF
$MONO = $script:MONO
$DISP = $script:DISP
$BODY = $script:BODY
$script:FAM = $SANS

# ============================ case-06  《折叠城市》杂志封面（出血巨字） ============================
Use-Case 'case-06'
$s = ''
$s += Box 0 0 1080 1440 '#EDE7DC' 0
# masthead runs off the right page edge.
# Two findings drove this shape:
#  * SizedOverflowBox passes its OWN width as a wrapping constraint, so a
#    page-width box broke the word after FOLD and dropped CITY onto a clipped
#    second line - measured ink x63..891, no bleed at all.
#  * maxLines="1" is accepted into the DSL but ignored by the renderer
#    (adding it produced a byte-identical PNG, sha 516CCB8B...).
# So the clip box is widened to 2000: the 1610px word no longer wraps, the
# ClipRect no longer cuts, and the 1080px page edge crops it mid-'C'.
$mast = TX ([ordered]@{ fontSize = 320; fontFamily = $DISP; color = '#1B1B1B' }) 'FOLDCITY'
$s += Bleed 48 0 2000 360 'TOP_LEFT' $mast
$s += TXW 'c06-cn' 64 348 520 93 '折叠城市' 64 $SERIF '#1B1B1B' 'letterSpacing=10'
$s += TXW 'c06-iss' 620 372 396 30 '第 42 期 . 2026 年 10 月 . 定价 38' 20 $SANS '#7A6A52' 'textAlign=RIGHT;fontFeatures=+tnum'
$s += HLine 64 456 952 3 '#1B1B1B'
# cover image: skewed "folded city" strips
$img = '<ClipRect><Stack clipBehavior="NONE">'
$strip = @('#2E4A63', '#E4622C', '#3E6B5A', '#8C7BC0', '#2A3B55', '#D9A441', '#4F7A45')
for ($i = 0; $i -lt $strip.Count; $i++) {
    $x = ($i * 90) - 40
    $k = 0.28; if ($i % 2 -eq 1) { $k = -0.28 }
    $m = IsoM 1.0 $k 0.0 1.0 0.0 0.0
    $img += '<Positioned left="' + $x + '" top="0" width="130" height="660">' +
            '<Transform matrix="' + $m + '"><Container width="130" height="660" color="' + $strip[$i] + '"/></Transform></Positioned>'
}
$img += '<Positioned left="392" top="70" width="132" height="132"><Container width="132" height="132" shape="CIRCLE" color="#F2C14E"/></Positioned>'
$img += '<Positioned left="0" top="470" width="616" height="6"><Container width="616" height="6" color="#FBF7EF99"/></Positioned>'
$img += '<Positioned left="0" top="486" width="616" height="6"><Container width="616" height="6" color="#FBF7EF55"/></Positioned>'
$img += '</Stack></ClipRect>'
$s += P 64 490 616 660 $img
# cover lines column
$cl = @(@('当高楼开始折叠', '一座城市的 17 种切面'), @('屋顶农场年报', '产量、土壤与守夜人'), @('夜班公交 42 站', '凌晨三点的通勤图谱'))
for ($i = 0; $i -lt $cl.Count; $i++) {
    $y = 490 + ($i * 224)
    $t = TPara ('c06-cl' + $i) 712 $y 304 $cl[$i][0] 34 46 '#1B1B1B' ''
    $s += $t[0]
    $s += HLine 712 ($y + ($t[1] * 46) + 14) 304 1 '#C9BFA8'
    $s += TXW ('c06-cs' + $i) 712 ($y + ($t[1] * 46) + 28) 304 56 $cl[$i][1] 18 $SANS '#7A6A52' ''
}
$s += HLine 64 1180 952 3 '#1B1B1B'
# barcode
$bx = 64; $bw = @(4,2,6,3,2,5,3,6,2,4,3,5,2,6,4,2,3,5)
foreach ($w in $bw) { $s += Box $bx 1210 $w 96 '#1B1B1B' 0; $bx += ($w + 6) }
$s += TXW 'c06-bc' 64 1318 400 24 '9 772026 042017' 17 $MONO '#1B1B1B' 'letterSpacing=2'
$s += TXW 'c06-dm' 64 1356 500 24 'DEMO . 演示数据 . FICTIONAL MAGAZINE' 16 $BODY '#7A6A52' 'letterSpacing=3'
$big42 = TX ([ordered]@{ fontSize = 260; fontFamily = $DISP; color = 'transparent'; foregroundColor = '#C9BFA8'; foregroundMode = 'STROKE'; foregroundStrokeWidth = '4' }) '42'
$s += Bleed 780 1200 300 190 'BOTTOM_RIGHT' $big42
Write-Dsl (Join-Path $OUT 'case-06\final.snapshot') (Page 1080 1440 '#EDE7DC' $s)

# ============================ case-07  夜航登机牌（渐变平铺纹样） ============================
Use-Case 'case-07'
$s = ''
$s += Grad 0 0 1748 760 'LINEAR' '#16294A,#0C1729' '0,1' 'gradientTileMode="REPEAT" gradientBegin="(-1,0)" gradientEnd="(-0.8,0)" gradientRotation="0.7853982"'
$s += P 48 56 1652 648 ('<Container width="1652" height="648" color="#F7F9FC" borderRadius="20" boxShadow="0 18 44 -8 #00000066"/>')
# patterned accent strip inside the card
$s += Grad 96 88 1054 56 'LINEAR' '#E4622C,#F2C14E,#E4622C' '0,0.5,1' 'gradientTileMode="REPEAT" gradientBegin="(-1,0)" gradientEnd="(-0.88,0)" gradientRotation="0.5235988" '
# left main
$s += TXW 'c07-a1' 96 168 520 35 '潮汐航空 TIDE AIR' 24 $SANS '#1B2B45' ''
$s += TXW 'c07-a2' 700 164 450 50 'TA 216' 34 $DISP '#E4622C' 'textAlign=RIGHT;letterSpacing=3'
$s += TXW 'c07-f1' 96 206 240 110 'SZX' 76 $DISP '#0C1729' ''
$s += TXW 'c07-ar' 336 236 90 70 '→' 50 $BODY '#E4622C' 'textAlign=CENTER'
$s += TXW 'c07-f2' 440 206 240 110 'KIX' 76 $DISP '#0C1729' ''
$s += TXW 'c07-c1' 96 322 260 26 '深圳 SHENZHEN' 18 $SANS '#6B7A90' ''
$s += TXW 'c07-c2' 440 322 260 26 '大阪 OSAKA' 18 $SANS '#6B7A90' ''
$s += TXW 'c07-t1' 96 356 240 73 '22:40' 50 $MONO '#0C1729' 'fontFeatures=+tnum'
$s += TXW 'c07-t2' 440 356 240 73 '02:15' 50 $MONO '#0C1729' 'fontFeatures=+tnum'
# sits on the same baseline as 02:15 instead of floating alone at x~1090
$s += TXW 'c07-tl' 604 388 170 30 '次日 +1' 20 $SANS '#E4622C' 'letterSpacing=1'
# right column: fills the empty band x880..1150 and shares the row baselines
$s += TXW 'c07-dl' 900 322 240 24 '航程 DURATION' 15 $BODY '#6B7A90' 'letterSpacing=3'
$s += TXW 'c07-dv' 900 356 240 73 '03:35' 50 $MONO '#0C1729' 'fontFeatures=+tnum'
$s += TXW 'c07-al' 900 432 240 24 '机型 AIRBUS A320' 15 $BODY '#6B7A90' 'letterSpacing=3'
$s += TXW 'c07-l1' 96 432 240 24 '起飞 DEPART' 15 $BODY '#6B7A90' 'letterSpacing=3'
$s += TXW 'c07-l2' 440 432 240 24 '抵达 ARRIVE' 15 $BODY '#6B7A90' 'letterSpacing=3'
$cells = @(@('日期 DATE', '2026-11-19'), @('登机口 GATE', 'B12'), @('座位 SEAT', '14A'), @('登机 BOARD', '22:05'))
for ($i = 0; $i -lt $cells.Count; $i++) {
    $x = 96 + ($i * 268)
    $s += TXW ('c07-gl' + $i) $x 470 240 22 $cells[$i][0] 15 $BODY '#6B7A90' 'letterSpacing=2'
    $s += TXW ('c07-gv' + $i) $x 494 240 41 $cells[$i][1] 28 $MONO '#0C1729' 'fontFeatures=+tnum'
}
$s += TXW 'c07-pl' 96 556 300 22 '乘客 PASSENGER' 15 $BODY '#6B7A90' 'letterSpacing=3'
$s += TXW 'c07-pv' 96 578 500 41 'CHEN/YI-HAN' 28 $BODY '#0C1729' 'letterSpacing=2'
$s += TXW 'c07-fl' 900 556 240 22 '常旅客 FREQ. FLYER' 15 $BODY '#6B7A90' 'letterSpacing=3'
$s += TXW 'c07-fv' 900 578 240 41 'TIDE-8842170' 28 $MONO '#0C1729' 'fontFeatures=+tnum'
$s += TXW 'c07-dm' 96 646 700 24 'DEMO . 演示数据 . FICTIONAL BOARDING PASS' 16 $BODY '#8A97AB' 'letterSpacing=3'
# stub
$s += DashV 1176 88 576 3 '#C3CCDA' 12 10
$s += TXW 'c07-s0' 1216 110 440 22 '登机存根 BOARDING STUB' 15 $BODY '#6B7A90' 'letterSpacing=3'
$s += TXW 'c07-s1' 1216 136 440 58 'TA 216' 40 $DISP '#E4622C' 'letterSpacing=2'
$s += TXW 'c07-s2' 1216 210 440 99 '14A' 68 $DISP '#0C1729' ''
# right-hand stub column: the name is the one thing a passenger keeps after the
# tear, and it also closes the 190px void that sat right of 14A / TA 216.
$s += TXW 'c07-s6' 1400 226 256 24 '旅客 PASSENGER' 15 $BODY '#6B7A90' 'letterSpacing=3;textAlign=RIGHT'
$s += TXW 'c07-s7' 1400 254 256 44 'CHEN/YI-HAN' 30 $BODY '#0C1729' 'letterSpacing=2;textAlign=RIGHT'
$s += TXW 'c07-s3' 1216 330 440 35 '2026-11-19  22:40' 24 $MONO '#3A4A63' 'fontFeatures=+tnum;textAlign=RIGHT'
# barcode now runs the full stub width (1216..1656): 230px of bars + 21x10 gaps.
$bx = 1216; $bw = @(8,17,6,11,19,8,6,14,11,6,17,8,14,6,11,8,17,6,8,14,11,4)
foreach ($w in $bw) { $s += Box $bx 390 $w 100 '#0C1729' 0; $bx += ($w + 10) }
$s += TXW 'c07-s4' 1216 512 440 30 '0481 2216 0119' 20 $MONO '#3A4A63' 'letterSpacing=2;fontFeatures=+tnum'
$s += P 1216 556 130 34 ('<Container width="130" height="34" color="#0C1729" borderRadius="17" alignment="CENTER"><Text fontSize="16" fontFamily="' + $BODY + '" color="#F7F9FC" maxLines="1" letterSpacing="2">DEMO</Text></Container>')
$s += TXW 'c07-s5' 1360 560 296 26 '演示数据' 16 $SANS '#8A97AB' 'textAlign=RIGHT'
Write-Dsl (Join-Path $OUT 'case-07\final.snapshot') (Page 1748 760 '#0C1729' $s)

# ============================ case-08  深度与材质规范页（多层阴影） ============================
Use-Case 'case-08'
$s = ''
$s += Box 0 0 1200 1500 '#F4F6F9' 0
$s += TXW 'c08-h1' 72 60 700 93 'ELEVATION' 64 $DISP '#1B2B45' 'letterSpacing=1'
$s += TXW 'c08-h2' 72 148 700 35 '深度与材质规范 v2.4' 24 $SANS '#5B6B82' ''
$s += TXW 'c08-h3' 760 76 368 26 'DEMO . 演示数据' 17 $BODY '#93A0B3' 'letterSpacing=3;textAlign=RIGHT'
$s += HLine 72 196 1056 2 '#1B2B45'
$s += TXW 'c08-a' 72 224 700 28 'A . 阴影阶梯 / ELEVATION LADDER' 20 $BODY '#5B6B82' 'letterSpacing=3'
$elev = @('1', '2', '4', '8', '16', '24')
for ($i = 0; $i -lt $elev.Count; $i++) {
    $col = $i % 3; $row = [Math]::Floor($i / 3)
    $x = 72 + ($col * 363); $y = 268 + ($row * 202)
    $s += P $x $y 330 150 ('<Container width="330" height="150" color="#FFFFFF" borderRadius="12" boxShadow="ELEVATION_' + $elev[$i] + '"/>')
    $s += TXW ('c08-en' + $i) ($x + 24) ($y + 56) 282 40 ('ELEVATION_' + $elev[$i]) 26 $DISP '#1B2B45' 'textAlign=CENTER'
    $s += TXW ('c08-el' + $i) ($x + 24) ($y + 158) 282 24 ('阴影层级 ' + $elev[$i]) 16 $SANS '#7A8699' 'textAlign=CENTER'
}
$s += TXW 'c08-b' 72 700 700 28 'B . 自定义多层阴影 / MULTI-LAYER SHADOW' 20 $BODY '#5B6B82' 'letterSpacing=3'
$s += P 72 744 560 200 ('<Container width="560" height="200" color="#FFFFFF" borderRadius="16" boxShadow="0 6 120 #0B3B3A2E,0 24 48 -8 #1B2B4533"/>')
$s += TXW 'c08-b1' 112 816 480 40 '悬浮卡片 HOVER' 28 $DISP '#1B2B45' 'textAlign=CENTER'
$s += TXW 'c08-b2' 680 748 448 26 '第 1 层  x 0  y 6  blur 120' 17 $MONO '#3A4A63' 'fontFeatures=+tnum'
$s += Box 680 782 16 16 '#0B3B3A4D' 8
$s += TXW 'c08-b3' 708 778 420 26 '#0B3B3A2E  环境光' 17 $SANS '#5B6B82' ''
$s += TXW 'c08-b4' 680 818 448 26 '第 2 层  x 0  y 24  blur 48  spread -8' 17 $MONO '#3A4A63' 'fontFeatures=+tnum'
$s += Box 680 852 16 16 '#1B2B4552' 8
$s += TXW 'c08-b5' 708 848 420 26 '#1B2B4533  接触阴影' 17 $SANS '#5B6B82' ''
$note = '大半径、低不透明度的一层负责环境光，小半径、较高不透明度的一层负责接触阴影；两层叠加才能让卡片既浮起来又不脱离页面。'
$n = TPara 'c08-bn' 680 892 448 $note 18 28 '#7A8699' ''
$s += $n[0]
$s += TXW 'c08-c' 72 1010 700 28 'C . Stack 裁剪行为 / CLIP BEHAVIOUR' 20 $BODY '#5B6B82' 'letterSpacing=3'
$panelL = '<Container width="520" height="300" color="#FFFFFF" borderRadius="10" border="1 SOLID #DDE3EC"/>'
$panelR = $panelL
$s += P 72 1054 520 300 $panelL
$s += P 608 1054 520 300 $panelR
$frameBox = '<Container width="400" height="130" color="#EEF1F5" borderRadius="10" border="1 SOLID #DDE3EC"/>'
# Probe p19 settled this section: Stack clips CONTENT (default / HARD_EDGE / +
# SizedBox all cut at the frame edge; only NONE overflowed) but NEVER clips
# boxShadow - all four shadow variants ran on past the box identically. The
# original card-and-halo demo therefore looked identical on both sides, so this
# panel shows the content case instead: an orange card is pulled half out of the
# frame, with its OVERFLOW caption below the clip line at y=1224.
$frameCard = '<Positioned left="100" top="20" width="200" height="180"><Container width="200" height="180" color="#E4622C" borderRadius="12"/></Positioned>'
$frameTag  = '<Positioned left="116" top="160" width="168" height="26"><Text fontSize="17" fontFamily="' + $SANS + '" color="#FFFFFF" textAlign="CENTER">OVERFLOW</Text></Positioned>'
$s += P 132 1094 400 130 $frameBox
$s += P 132 1094 400 130 ('<Stack clipBehavior="HARD_EDGE">' + $frameCard + $frameTag + '</Stack>')
$s += P 668 1094 400 130 $frameBox
$s += P 668 1094 400 130 ('<Stack clipBehavior="NONE">' + $frameCard + $frameTag + '</Stack>')
$s += TXW 'c08-c1' 112 1310 440 26 'clipBehavior="HARD_EDGE" 超出框体被裁切' 17 $SANS '#B4451F' 'textAlign=CENTER'
$s += TXW 'c08-c2' 648 1310 440 26 'clipBehavior="NONE" 超出框体保留' 17 $SANS '#3F7A52' 'textAlign=CENTER'
$s += TXW 'c08-c3' 72 1366 1056 26 '实测 p19：Stack 裁的是子节点本身，boxShadow 不参与裁剪（四组阴影像素完全一致）' 15 $SANS '#8A97AB' ''
$s += HLine 72 1408 1056 2 '#1B2B45'
$s += TXW 'c08-f1' 72 1428 700 26 '阴影数值按 1x 逻辑像素标注 . 本页为虚构规范演示' 17 $SANS '#7A8699' ''
$s += TXW 'c08-f2' 760 1428 368 26 'DEMO . 演示数据' 17 $BODY '#93A0B3' 'textAlign=RIGHT;letterSpacing=3'
Write-Dsl (Join-Path $OUT 'case-08\final.snapshot') (Page 1200 1500 '#F4F6F9' $s)

# ============================ case-09  东港站到发看板（等宽数字） ============================
Use-Case 'case-09'
$s = ''
$s += Box 0 0 1920 480 '#0B1020' 0
$s += Box 0 0 1920 64 '#141C33' 0
$s += TXW 'c09-h1' 72 16 620 38 '东港站 EAST HARBOR STATION' 26 $SANS '#FFFFFF' 'letterSpacing=3'
$s += TXW 'c09-h2' 720 22 500 30 '到发信息 ARRIVALS / DEPARTURES' 20 $SANS '#7FD4C1' 'letterSpacing=2'
$s += TXW 'c09-h3' 1560 14 288 46 '14:07:32' 32 $DISP '#FFD166' 'textAlign=RIGHT;fontFeatures=+tnum'
$cols = @(@('车次', 72, 200), @('始发 / 终到', 300, 520), @('计划', 840, 140), @('预计', 1000, 140), @('站台', 1160, 120), @('状态', 1320, 300), @('备注', 1660, 196))
foreach ($c in $cols) { $s += TXW ('c09-hc-' + $c[1]) ([int]$c[1]) 78 ([int]$c[2]) 24 $c[0] 16 $BODY '#5E7391' 'letterSpacing=4' }
$s += Box 72 108 1776 1 '#233047' 0
$trains = @(
    @('G7312', '东港 → 新岭', '14:12', '14:12', '06', '检票中', '#7FD4C1', '二等座 08 车'),
    @('D2244', '东港 → 云溪', '14:26', '14:26', '03', '正点', '#8892A6', '商务座 02 车'),
    @('K1180', '东港 → 北渡', '14:41', '14:45', '11', '晚点 4 分', '#FF6B6B', '硬卧 05 车'),
    @('G7596', '海门 → 东港', '14:50', '14:50', '02', '到站', '#FFD166', '出站口 C'),
    @('Z204', '东港 → 南屿', '15:03', '15:03', '08', '候车', '#4CC9F0', '软卧 07 车')
)
for ($i = 0; $i -lt $trains.Count; $i++) {
    $t = $trains[$i]; $y = 126 + ($i * 58); $cy = $y + 12
    $s += TXW ('c09-n' + $i) 72 $y 200 44 $t[0] 30 $MONO '#FFFFFF' 'fontFeatures=+tnum'
    $s += TXW ('c09-r' + $i) 300 ($y + 4) 520 38 $t[1] 26 $SANS '#C6D2E4' ''
    $s += TXW ('c09-p' + $i) 840 $y 140 49 $t[2] 34 $BODY '#FFFFFF' 'fontFeatures=+tnum'
    $s += TXW ('c09-a' + $i) 1000 $y 140 49 $t[3] 34 $BODY $t[6] 'fontFeatures=+tnum'
    $s += TXW ('c09-s' + $i) 1160 ($y + 2) 120 46 $t[4] 32 $MONO '#FFFFFF' 'fontFeatures=+tnum'
    $s += P 1320 $cy 170 34 ('<Container width="170" height="34" color="' + $t[6] + '2E" borderRadius="17" border="1 SOLID ' + $t[6] + '88" alignment="CENTER"><Text fontSize="19" fontFamily="' + $SANS + '" color="' + $t[6] + '" maxLines="1">' + $t[5] + '</Text></Container>')
    $s += TXW ('c09-m' + $i) 1660 ($y + 6) 196 32 $t[7] 20 $SANS '#7E8FA8' ''
    if ($i -lt 4) { $s += Box 72 ($y + 50) 1776 1 '#1A2334' 0 }
}
$s += Box 72 432 1776 1 '#233047' 0
$s += TXW 'c09-f1' 72 444 900 26 '数据每 30 秒刷新 . 站台信息以车站广播为准 . DEMO 演示数据' 18 $SANS '#5E7391' ''
$s += TXW 'c09-f2' 1400 444 448 26 '屏号 HGT-02 / 版本 3.1.7' 18 $MONO '#5E7391' 'textAlign=RIGHT'
Write-Dsl (Join-Path $OUT 'case-09\final.snapshot') (Page 1920 480 '#0B1020' $s)

# ============================ case-10  软木园等轴测导览（轴测矩阵） ============================
Use-Case 'case-10'
$s = ''
$s += Box 0 0 1200 1200 '#F4EFE6' 0
$s += TXW 'c10-h1' 72 56 600 64 '软木园' 44 $SERIF '#1B2B45' 'letterSpacing=6'
$s += TXW 'c10-h2' 72 124 600 30 'COORKEN PARK . 导览图' 20 $BODY '#4F7A45' 'letterSpacing=6'
$s += TXW 'c10-h3' 760 66 368 26 'DEMO . 演示数据' 17 $BODY '#9A917F' 'letterSpacing=3;textAlign=RIGHT'
$s += HLine 72 170 1056 2 '#1B2B45'
$UNIT = 92.0; $X0 = 600.0; $Y0 = 430.0
# ground grid 6x6
for ($u = 0; $u -lt 6; $u++) {
    for ($v = 0; $v -lt 6; $v++) {
        $c = '#DCE6D4'
        if (($u % 2) -eq 0 -and ($v % 2) -eq 0) { $c = '#E4EBDD' }
        if ($u -eq 2 -or $v -eq 2) { $c = '#EDE4D3' }
        if ($u -eq 4 -and $v -eq 1) { $c = '#BFD8E4' }
        $s += IsoTop $u $v 0 $UNIT $X0 $Y0 $c ''
    }
}
# masses: u, v, height, top, left, right  (5 buildings + 5 trees)
# tree (0,0) was relocated to (0,5): its footprint sat exactly behind building (1,1)
# (same screen x 520..680, y 379..522 inside the tower's 319..614), so it would be
# fully hidden once painter's order is correct.
$mass = @(
    @{ u = 1; v = 1; h = 2.2;  top = '#E9B978'; lf = '#C98A4A'; rt = '#DCA464' },
    @{ u = 3; v = 0; h = 1.4;  top = '#8FB59A'; lf = '#4F7A45'; rt = '#6E9A62' },
    @{ u = 0; v = 3; h = 1.8;  top = '#7FA8D8'; lf = '#2E6FB7'; rt = '#4E8ACD' },
    @{ u = 4; v = 3; h = 2.6;  top = '#C9AEDC'; lf = '#8C7BC0'; rt = '#A795CC' },
    @{ u = 2; v = 4; h = 1.2;  top = '#F0A18A'; lf = '#D9744F'; rt = '#E88C6C' },
    @{ u = 5; v = 1; h = 0.55; top = '#7FB07A'; lf = '#3F6B3A'; rt = '#4F7A45' },
    @{ u = 1; v = 4; h = 0.55; top = '#7FB07A'; lf = '#3F6B3A'; rt = '#4F7A45' },
    @{ u = 5; v = 4; h = 0.55; top = '#7FB07A'; lf = '#3F6B3A'; rt = '#4F7A45' },
    @{ u = 0; v = 5; h = 0.55; top = '#7FB07A'; lf = '#3F6B3A'; rt = '#4F7A45' },
    @{ u = 3; v = 5; h = 0.55; top = '#7FB07A'; lf = '#3F6B3A'; rt = '#4F7A45' }
)
# painter's algorithm for axonometric order: ascending depth (u + v), tie-break on u.
# Ground tiles stay first: a cell at depth d+1 starts exactly at the silhouette
# bottom of depth d (d*46+476 vs d*46+522), so tiles only ever touch, never cover.
$mass = @($mass | Sort-Object @{Expression = { $_.u + $_.v }}, @{Expression = { $_.u }})
foreach ($ob in $mass) {
    $s += IsoLeft $ob.u $ob.v $ob.h $UNIT $X0 $Y0 $ob.lf
    $s += IsoRight $ob.u $ob.v $ob.h $UNIT $X0 $Y0 $ob.rt
    $s += IsoTop $ob.u $ob.v $ob.h $UNIT $X0 $Y0 $ob.top ''
}
# compass + legend
$s += Circ 1040 216 88 '#F4EFE6' '2 SOLID #1B2B45'
$s += Rotate 1078 228 12 30 0 (C 12 30 '#D9744F' 6)
$s += TXW 'c10-n' 1040 262 88 29 'N' 20 $DISP '#1B2B45' 'textAlign=CENTER'
# Two keyed rows. The first version claimed one orange swatch = 展馆, which was
# false for the other four pavilions, so each building colour is now keyed by name.
# Row 3 keys the five short green masses. Round 4 fixed the pavilion colours but left
# the trees (#7FB07A, h=0.55) unkeyed, so the figure still had shapes no row explained.
# It sits at y=300 with a single item at x=140..294: the map's topmost point is the
# top face of building (1,1) at x520..680 / y319, so this row never touches it.
# NOTE: a one-pair list MUST be built as @(, $pair) — @(@('a','b')) collapses to the
# inner array, $items[0] becomes the string and [0] then indexes its first character.
$treePair = @('#7FB07A', '树木')
$legRows = @(
    @{ y = 212; cap = '地面'; items = @(@('#EDE4D3', '步道'), @('#DCE6D4', '草坪'), @('#BFD8E4', '水景')) },
    @{ y = 256; cap = '展馆'; items = @(@('#7FA8D8', '儿童馆'), @('#F0A18A', '花房'), @('#E9B978', '主展馆'), @('#C9AEDC', '观景塔'), @('#8FB59A', '茶室')) },
    @{ y = 300; cap = '绿化'; items = @(, $treePair) }
)
foreach ($lr in $legRows) {
    $s += TXW ('c10-cap' + $lr.y) 72 $lr.y 60 26 $lr.cap 16 $SANS '#9A917F' ''
    for ($i = 0; $i -lt $lr.items.Count; $i++) {
        $x = 140 + ($i * 160)
        $s += Box $x ($lr.y + 2) 34 22 $lr.items[$i][0] 4
        $s += TXW ('c10-lg' + $lr.y + '-' + $i) ($x + 44) $lr.y 110 26 $lr.items[$i][1] 18 $SANS '#4A4A3E' ''
    }
}
$s += HLine 72 1024 1056 2 '#1B2B45'
$s += TXW 'c10-f1' 72 1044 700 26 '入口在西南角 . 步道全长 1.4 km . 建筑高度按 3 层等比缩放' 18 $SANS '#7A7364' ''
$s += TXW 'c10-f2' 760 1044 368 26 '等轴测 30° / 30° 投影' 18 $MONO '#7A7364' 'textAlign=RIGHT'
$s += P 72 1100 1056 40 ('<Container width="1056" height="40" color="#1B2B45" borderRadius="6" alignment="CENTER"><Text fontSize="20" fontFamily="' + $SANS + '" color="#F4EFE6" maxLines="1" letterSpacing="2">游客中心 10:00–18:00 闭园前 30 分钟停止入场 . DEMO 演示数据</Text></Container>')
Write-Dsl (Join-Path $OUT 'case-10\final.snapshot') (Page 1200 1200 '#F4EFE6' $s)

Report-Problems
Write-Output 'gen-b03-b: 5 snapshots written'
