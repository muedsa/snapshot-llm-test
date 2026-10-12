$ErrorActionPreference = 'Stop'
. (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03\lib-b03.ps1')
$OUT = $script:B03OUT
$SANS = $script:SANS
$SERIF = $script:SERIF
$MONO = $script:MONO
$DISP = $script:DISP
$BODY = $script:BODY
$script:FAM = $SANS

# ============================ case-01  蓝调不在场 演出海报 ============================
Use-Case 'case-01'
$s = ''
$s += Grad 0 0 1080 1000 'RADIAL' '#2B5C8F,#14273C,#080C16' '0,0.5,1' 'gradientCenter="TOP_CENTER" gradientRadius="0.95"'
$s += Box 56 0 1 1528 '#23364D' 0
$s += Box 1022 0 1 1528 '#23364D' 0
$s += TXW 'c01-eyebrow' 88 76 700 32 'TIDE BAR . LIVE SESSION 047' 22 $BODY '#7FD4C1' 'letterSpacing=6'
$s += HLine 88 124 902 2 '#2E4A63'
$s += TXW 'c01-wm' 560 178 460 218 '047' 150 $DISP 'transparent' 'letterSpacing=6;foregroundColor=#1C3346;foregroundMode=STROKE;foregroundStrokeWidth=3;textAlign=RIGHT'
$s += TXW 'c01-t1' 88 170 902 334 '蓝调' 230 $SERIF '#F2C14E' 'letterSpacing=4;textShadow=6 8 0 #A03C10,16 20 30 #00000099'
$s += TXW 'c01-t2' 88 506 902 334 '不在场' 230 $SERIF 'transparent' 'letterSpacing=4;foregroundColor=#7FD4C1;foregroundMode=STROKE;foregroundStrokeWidth=6'
$s += TXW 'c01-sub' 88 856 760 58 'BLUES IN ABSENTIA' 40 $DISP '#E8EEF5' 'letterSpacing=8'
$s += P 856 862 164 44 ('<Container width="164" height="44" color="#E4622C" borderRadius="22" alignment="CENTER"><Text fontSize="17" fontFamily="' + $SANS + '" color="#140A05" maxLines="1" letterSpacing="1">售票中 ON SALE</Text></Container>')
$blurb = '三组演出，无间断即兴。入场含一杯酒水，22:30 开门，演毕不设返场。'
$bp = TPara 'c01-blurb' 88 936 640 $blurb 24 38 '#8FA6BC' '' ; $s += $bp[0]
$s += HLine 88 1046 902 1 '#24394F'
$rows = @(@('DATE','2026-10-24 SAT'), @('TIME','23:00 - 02:00'), @('PRICE','预售 120 . 现场 160'), @('ADDR','潮汐里 3 号仓 B1'))
$ri = 0
foreach ($r in $rows) {
    $y = 1076 + ($ri * 62)
    $s += TXW ('c01-l' + $ri) 88 $y 110 29 $r[0] 20 $BODY '#5E7F9B' 'letterSpacing=3'
    $s += TXW ('c01-v' + $ri) 214 $y 470 38 $r[1] 26 $SANS '#E8EEF5' ''
    $ri++
}
$s += Circ 730 1076 240 '#0F1B2C' '2 SOLID #2E4A63'
$s += Circ 766 1116 168 '' '1 SOLID #24394F'
$s += Circ 802 1152 96 '#E4622C' ''
$s += Circ 841 1191 18 '#080C16' ''
$s += TXW 'c01-f1' 88 1348 902 32 '票务 . 潮汐票务小程序 . 现场不设售票' 22 $SANS '#7FD4C1' ''
$s += TXW 'c01-f2' 88 1390 902 26 'DEMO . 演示数据 . FICTIONAL EVENT' 18 $BODY '#5E7F9B' 'letterSpacing=3'
$s += Grad 0 1452 1080 76 'LINEAR' '#E4622C,#F2C14E,#7FD4C1' '0,0.5,1' 'gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT"'
Write-Dsl (Join-Path $OUT 'case-01\final.snapshot') (Page 1080 1528 '#080C16' $s)

# ============================ case-02  大堂楼层导视（毛玻璃） ============================
Use-Case 'case-02'
$s = ''
$s += Grad 0 0 1920 720 'LINEAR' '#0A1020,#17243D,#22385A,#2E4668,#7A5A50' '0,0.4,0.65,0.85,1' 'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"'
# vertical mullions - every one crosses the glass edge at y=240 (sharp above, blurred below)
foreach ($x in @(0, 300, 600, 900, 1200, 1500, 1800)) {
    $s += Box $x 0 96 720 '#2A3E63' 0
    $s += Box ($x + 94) 0 2 720 '#7E9CC966' 0
}
# pendant lights: glow + core straddling y=240 so the frost reads on the same object
foreach ($g in @(@(560,170,150), @(860,50,210), @(1180,140,170), @(1560,30,190), @(1700,150,160))) {
    $s += Circ ([int]$g[0]) ([int]$g[1]) ([int]$g[2]) '#FFD79A33' ''
}
foreach ($g in @(@(590,200,90), @(900,90,130), @(1212,172,106), @(1597,67,116), @(1730,180,100))) {
    $s += Circ ([int]$g[0]) ([int]$g[1]) ([int]$g[2]) '#FFD79A' ''
}
$s += Box 0 640 1920 80 '#C8794F33' 0
$s += Box 0 692 1920 3 '#F0B27A55' 0
# ONE frosted card (p14-p18: the clip must wrap BackdropFilter directly, and only the
# first BackdropFilter in a document reads the full backdrop)
$s += Frost 36 240 1848 444 32 32 '#0B152485'
$s += P 36 240 1848 444 ('<Container width="1848" height="444" borderRadius="32" gradientType="LINEAR" gradientColors="#FFFFFF1A,#FFFFFF00" gradientStops="0,1" gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/>')
$s += P 36 240 1848 444 ('<Container width="1848" height="444" borderRadius="32" color="transparent" border="1 SOLID #FFFFFF33"/>')
# ---- sharp zone (y 0..240): brand + title, outside the glass ----
$s += TXW 'c02-brand' 76 40 760 34 '环贸中心 HUANMAO CENTER . 大堂导视' 24 $SANS '#FFFFFF' 'letterSpacing=2'
$s += TXW 'c02-demo' 1420 44 424 26 'DEMO . 演示数据' 18 $BODY '#FFD166' 'letterSpacing=4;textAlign=RIGHT'
$s += TXW 'c02-title' 76 96 560 96 '大堂导视' 72 $DISP '#FFFFFF' 'letterSpacing=8'
$s += TXW 'c02-en' 440 128 400 40 'LOBBY DIRECTORY' 26 $BODY '#FFD166' 'letterSpacing=6'
$s += TXW 'c02-sub' 76 196 700 32 'L1 主入口 . 东侧电梯厅 . 无障碍通道' 19 $SANS '#9FB6D0' ''
# ---- frosted card content (everything below is painted AFTER the single BackdropFilter) ----
$s += Box 746 274 1 400 '#FFFFFF26' 0
$s += Box 1336 274 1 400 '#FFFFFF26' 0
# column A - floor directory
$s += TXW 'c02-a0' 76 274 640 30 '楼层导视 FLOOR DIRECTORY' 20 $SANS '#CFE0F5' 'letterSpacing=3'
$s += HLine 76 312 640 1 '#FFFFFF33'
$fl = @(@('28F','潮汐资本','Tide Capital'), @('21F','海图设计','Chart Studio'), @('17F','蓝盒影像','BlueBox Film'), @('12F','中庭花园','Atrium Garden'), @('01F','大堂 . 快递 . 咖啡','Lobby Atrium'))
$fi = 0
foreach ($f in $fl) {
    $y = 326 + ($fi * 62)
    $s += TXW ('c02-f' + $fi) 76 $y 100 46 $f[0] 34 $DISP '#7FD4C1' ''
    $s += TXW ('c02-n' + $fi) 190 $y 526 34 $f[1] 23 $SANS '#FFFFFF' ''
    $s += TXW ('c02-s' + $fi) 190 ($y + 30) 526 26 $f[2] 15 $BODY '#9FB6D0' 'letterSpacing=1'
    $fi++
}
$s += TXW 'c02-af' 76 640 640 26 '电梯厅 LIFT LOBBY 直行 12m' 17 $SANS '#7FD4C1' ''
# column B - lift + shuttle
$s += TXW 'c02-b0' 776 274 530 30 '电梯 ETA LIFT STATUS' 19 $SANS '#CFE0F5' 'letterSpacing=3'
$s += HLine 776 312 530 1 '#FFFFFF33'
$s += TXW 'c02-b1' 776 326 220 100 '42s' 72 $DISP '#FFD166' ''
$s += TXW 'c02-b2' 1010 348 300 34 'B 区 . 3 号梯' 21 $SANS '#FFFFFF' ''
$s += TXW 'c02-b2b' 1010 390 300 30 '预计 12 秒后到达' 17 $SANS '#9FB6D0' ''
$s += P 776 438 116 34 ('<Container width="116" height="34" color="#06D6A0" borderRadius="17" alignment="CENTER"><Text fontSize="16" fontFamily="' + $SANS + '" color="#06241E" maxLines="1">运行中</Text></Container>')
$s += P 908 438 126 34 ('<Container width="126" height="34" color="#FFFFFF22" borderRadius="17" alignment="CENTER"><Text fontSize="16" fontFamily="' + $SANS + '" color="#E8EEF5" maxLines="1">无障碍</Text></Container>')
$s += TXW 'c02-c0' 776 494 530 30 '接驳车 SHUTTLE' 19 $SANS '#CFE0F5' 'letterSpacing=3'
$s += HLine 776 530 530 1 '#FFFFFF33'
$s += TXW 'c02-c1' 776 544 530 38 '14:20 东门 - 城际快线' 26 $SANS '#FFFFFF' 'fontFeatures=+tnum'
$s += TXW 'c02-c2' 776 588 530 28 '每 15 分钟一班 . 末班 23:40' 17 $SANS '#9FB6D0' 'fontFeatures=+tnum'
$s += Box 776 628 64 6 '#7FD4C1' 3
$s += Box 850 628 64 6 '#7FD4C1' 3
$s += Box 924 628 64 6 '#FFFFFF3D' 3
$s += TXW 'c02-c3' 776 648 530 26 '下一班还有 6 分钟' 16 $SANS '#7FD4C1' ''
# column C - now / weather / today
$s += TXW 'c02-d0' 1366 274 478 30 '现在 NOW' 19 $SANS '#CFE0F5' 'letterSpacing=3'
$s += HLine 1366 312 478 1 '#FFFFFF33'
$s += TXW 'c02-d1' 1366 326 478 76 '14:07:32' 54 $DISP '#FFFFFF' 'fontFeatures=+tnum'
$s += TXW 'c02-d2' 1366 406 478 30 '2026-10-06 周二' 19 $SANS '#9FB6D0' 'fontFeatures=+tnum'
$s += HLine 1366 446 478 1 '#FFFFFF33'
$s += TXW 'c02-d3' 1366 456 478 60 '晴 24°' 44 $SANS '#FFD166' ''
$s += TXW 'c02-d4' 1366 518 478 28 '湿度 61% . 东南风 2 级' 17 $SANS '#9FB6D0' ''
$s += HLine 1366 554 478 1 '#FFFFFF33'
$s += TXW 'c02-d5' 1366 562 478 28 '今日活动 TODAY' 17 $SANS '#CFE0F5' 'letterSpacing=3'
$s += TXW 'c02-d6' 1366 594 478 32 '15:00 中庭爵士' 21 $SANS '#FFFFFF' 'fontFeatures=+tnum'
$s += TXW 'c02-d7' 1366 628 478 32 '19:30 屋顶放映' 21 $SANS '#FFFFFF' 'fontFeatures=+tnum'
$s += TXW 'c02-d8' 1366 662 478 22 'DEMO . 演示数据' 15 $BODY '#7A8CA3' 'letterSpacing=3'
Write-Dsl (Join-Path $OUT 'case-02\final.snapshot') (Page 1920 720 '#141C3B' $s)

# ============================ case-03  丝网印票根（双色套印） ============================
Use-Case 'case-03'
$s = ''
$s += Box 0 0 1600 640 '#F2E8D5' 0
# --- layer 1: grayscale scene, MULTIPLY amber ---
$scene = '<Stack clipBehavior="NONE">'
$scene += '<Positioned left="0" top="0" width="1180" height="300"><Container width="1180" height="300" color="#E9E9E9"/></Positioned>'
$scene += '<Positioned left="0" top="0" width="1180" height="210"><Container width="1180" height="210" color="#CFCFCF"/></Positioned>'
$scene += '<Positioned left="140" top="60" width="150" height="150"><Container width="150" height="150" shape="CIRCLE" color="#6E6E6E"/></Positioned>'
$scene += '<Positioned left="0" top="210" width="1180" height="90"><Container width="1180" height="90" color="#A8A8A8"/></Positioned>'
$scene += '<Positioned left="60" top="230" width="700" height="16"><Container width="700" height="16" color="#5A5A5A" borderRadius="8"/></Positioned>'
$scene += '<Positioned left="260" top="254" width="540" height="16"><Container width="540" height="16" color="#7E7E7E" borderRadius="8"/></Positioned>'
$scene += '<Positioned left="140" top="278" width="860" height="16"><Container width="860" height="16" color="#3E3E3E" borderRadius="8"/></Positioned>'
$scene += '<Positioned left="900" top="130" width="34" height="10"><Container width="34" height="10" color="#4A4A4A" borderRadius="5"/></Positioned>'
$scene += '<Positioned left="950" top="112" width="26" height="8"><Container width="26" height="8" color="#5E5E5E" borderRadius="4"/></Positioned>'
$scene += '</Stack>'
$s += CTint 0 0 1180 300 '#E86A3A' 'MULTIPLY' $scene
# --- layer 2: mis-registered blue patch over the right half of the sun ---
$patch = '<ClipRect><Stack clipBehavior="NONE">'
$patch += '<Positioned left="0" top="0" width="100" height="160"><Container width="100" height="160" color="#E9E9E9"/></Positioned>'
$patch += '<Positioned left="-56" top="4" width="150" height="150"><Container width="150" height="150" shape="CIRCLE" color="#6E6E6E"/></Positioned>'
$patch += '</Stack></ClipRect>'
$s += CTint 196 56 100 160 '#2E6FB7' 'MULTIPLY' $patch
$s += Box 0 300 1180 4 '#1B1B1B' 0
# --- ticket body ---
$s += TXW 'c03-t' 56 332 700 82 '潮汐音乐节' 56 $SERIF '#1B1B1B' 'letterSpacing=4'
$s += TXW 'c03-s' 56 424 700 32 'TIDE FEST 2026' 22 $DISP '#B4451F' 'letterSpacing=7'
$s += TXW 'c03-i1' 56 474 350 35 '2026-11-07 SAT 14:00' 24 $BODY '#2B2B2B' 'fontFeatures=+tnum'
$s += TXW 'c03-i2' 424 474 300 35 '西湾沙滩 WEST BAY' 24 $SANS '#2B2B2B' ''
$s += TXW 'c03-i3' 744 474 300 35 'GATE C . 站席' 24 $SANS '#2B2B2B' ''
$s += TXW 'c03-p' 56 524 300 64 '480' 46 $DISP '#B4451F' ''
$s += Box 52 546 4 40 '#B4451F' 0
$s += TXW 'c03-p2' 176 546 260 26 '含服务费 . 不退不换' 16 $SANS '#7A6A52' ''
$s += TXW 'c03-d' 56 596 700 24 'DEMO . 演示数据 . FICTIONAL TICKET' 16 $BODY '#8A7A62' 'letterSpacing=3'
# second duotone plate: fills the empty right band of the ticket body (x960..1160)
# and repeats the two-colour mis-registration motif of the header sun.
$panel = '<Stack clipBehavior="NONE">'
$panel += '<Positioned left="0" top="0" width="200" height="200"><Container width="200" height="200" color="#E9E9E9"/></Positioned>'
$panel += '<Positioned left="0" top="0" width="200" height="112"><Container width="200" height="112" color="#CFCFCF"/></Positioned>'
$panel += '<Positioned left="112" top="26" width="58" height="58"><Container width="58" height="58" shape="CIRCLE" color="#5A5A5A"/></Positioned>'
$panel += '<Positioned left="0" top="112" width="200" height="88"><Container width="200" height="88" color="#A8A8A8"/></Positioned>'
$panel += '<Positioned left="18" top="130" width="150" height="10"><Container width="150" height="10" color="#5A5A5A" borderRadius="5"/></Positioned>'
$panel += '<Positioned left="42" top="148" width="120" height="10"><Container width="120" height="10" color="#7E7E7E" borderRadius="5"/></Positioned>'
$panel += '<Positioned left="10" top="166" width="176" height="10"><Container width="176" height="10" color="#3E3E3E" borderRadius="5"/></Positioned>'
$panel += '</Stack>'
$s += CTint 960 400 200 200 '#2E6FB7' 'MULTIPLY' $panel
$s += TXW 'c03-pn' 960 606 200 24 '二色套印 PLATE 02' 15 $BODY '#7A6A52' 'letterSpacing=2'
$s += DashV 1180 312 306 3 '#C9B99A' 10 10
# header kept on ONE line: the old 存根 STUB / NO. split read as an accidental wrap
$s += TXW 'c03-st' 1220 332 324 30 '存根 STUB NO.' 18 $SANS '#7A6A52' 'letterSpacing=4'
$s += TXW 'c03-num' 1220 372 324 82 '04812' 56 $MONO '#1B1B1B' 'fontFeatures=+tnum'
$bx = 1220; $n = 0
$bw = @(3,5,2,6,3,2,5,4,2,6,3,3,5,2,6,4,2,5,3,6,2,4,5,3)
foreach ($w in $bw) {
    $s += Box $bx 470 $w 64 '#1B1B1B' 0
    $bx += ($w + 5); $n++
}
$s += TXW 'c03-bc' 1220 546 324 24 'TA-FST-2026-1107' 17 $MONO '#2B2B2B' 'letterSpacing=2'
$s += TXW 'c03-bd' 1220 578 324 24 'DEMO . 演示数据' 16 $BODY '#8A7A62' 'letterSpacing=3'
Write-Dsl (Join-Path $OUT 'case-03\final.snapshot') (Page 1600 640 '#F2E8D5' $s)

# ============================ case-04  圈速计时板（各向异性速度残影） ============================
Use-Case 'case-04'
$s = ''
$s += Box 0 0 1920 1080 '#0A0B10' 0
# speed streaks behind the timing
$streaks = '<Stack clipBehavior="NONE">'
$sx = @(0, 340, 120, 620, 0, 760, 260, 480, 90, 540)
$sw = @(1500, 1180, 1720, 980, 1340, 1460, 1600, 860, 1750, 1120)
$sc = @('#E4622CB3','#E4622CB3','#FFD16680','#E4622CB3','#FFFFFF14','#FFD16666','#E4622C99','#FFFFFF1A','#FFD16680','#E4622CB3')
# tops are RELATIVE to the IBlur box at y=360, so 40 => absolute y=400. The old
# value 396 put the band at y756..1102, straight through GHOST and the stats row.
$st = 40
for ($i = 0; $i -lt $sx.Count; $i++) {
    $streaks += '<Positioned left="' + $sx[$i] + '" top="' + $st + '" width="' + $sw[$i] + '" height="22">' +
                '<Container width="' + $sw[$i] + '" height="22" color="' + $sc[$i] + '" borderRadius="11"/></Positioned>'
    $st += 28
}
$streaks += '</Stack>'
$s += IBlur 0 360 1920 400 140 3 $streaks
# header
$s += TXW 'c04-h1' 72 26 900 36 'HANKO SPEEDWAY . LAP 24 / 58' 24 $BODY '#8892A6' 'letterSpacing=5'
$s += TXW 'c04-h2' 1500 30 348 26 'DEMO . 演示数据' 18 $BODY '#FFD166' 'letterSpacing=4;textAlign=RIGHT'
$s += HLine 72 78 1776 1 '#22262F'
# driver block
$s += TXW 'c04-n1' 72 132 300 96 '#' 92 $DISP '#E4622C' ''
$s += TXW 'c04-n2' 190 152 600 46 'NORI KAZAMA' 34 $DISP '#FFFFFF' 'letterSpacing=3'
$s += TXW 'c04-n3' 190 200 600 30 'TA-RETRO . 干胎 MEDIUM' 20 $SANS '#8892A6' ''
# lap time
$s += TXW 'c04-l0' 72 348 300 30 '本圈 CURRENT LAP' 20 $BODY '#7FD4C1' 'letterSpacing=5'
$s += TXW 'c04-l1' 72 384 1200 306 '1:32.847' 200 $DISP '#FFFFFF' ''
$s += P 72 700 460 40 ('<Container width="460" height="40" color="#E4622C" borderRadius="6" alignment="CENTER"><Text fontSize="24" fontFamily="' + $DISP + '" color="#0A0B10" maxLines="1">FASTEST LAP</Text></Container>')
$s += TXW 'c04-l2' 560 706 600 34 '较最佳 -0.264' 24 $SANS '#7FD4C1' 'fontFeatures=+tnum'
# ghost lap (slightly blurred)
$ghostAttrs = [ordered]@{ fontSize = 34; fontFamily = $BODY; color = '#4A5568'; letterSpacing = '4'; fontFeatures = '+tnum' }
$s += IBlur 72 764 700 46 2.5 2.5 (TX $ghostAttrs 'GHOST 1:33.102')
# sector cards
$sx2 = @(1300, 1300, 1300); $sy2 = @(150, 288, 426)
$sl = @('SECTOR 1', 'SECTOR 2', 'SECTOR 3'); $sv = @('31.204', '38.662', '22.981')
$sd = @('-0.120', '+0.041', '-0.185'); $sdc = @('#7FD4C1', '#FF6B6B', '#7FD4C1')
for ($i = 0; $i -lt 3; $i++) {
    $s += P $sx2[$i] $sy2[$i] 548 116 ('<Container width="548" height="116" color="#14161D" borderRadius="10" border="1 SOLID #22262F"/>')
    $s += TXW ('c04-sl' + $i) 1324 ($sy2[$i] + 16) 300 26 $sl[$i] 18 $BODY '#8892A6' 'letterSpacing=4'
    $s += TXW ('c04-sv' + $i) 1324 ($sy2[$i] + 44) 300 52 $sv[$i] 40 $DISP '#FFFFFF' 'fontFeatures=+tnum'
    $s += TXW ('c04-sd' + $i) 1660 ($sy2[$i] + 52) 164 44 $sd[$i] 32 $DISP $sdc[$i] 'textAlign=RIGHT;fontFeatures=+tnum'
}
# delta bar - now on its own card so the streaks cannot wash out the label.
# Same 24px inset and 22px card gap as the three sector cards above.
$s += P 1300 564 548 116 ('<Container width="548" height="116" color="#14161D" borderRadius="10" border="1 SOLID #22262F"/>')
$s += TXW 'c04-db' 1324 580 500 26 'DELTA TO LEADER' 18 $BODY '#8892A6' 'letterSpacing=4'
$s += Box 1324 618 500 14 '#22262F' 7
$s += Box 1324 618 294 14 '#7FD4C1' 7
$s += Box 1618 612 3 26 '#FFFFFF' 0
$s += TXW 'c04-dv' 1324 642 500 30 'P2 . -0.418s' 24 $SANS '#7FD4C1' 'fontFeatures=+tnum'
# bottom stats
$s += HLine 72 856 1776 1 '#22262F'
$bs = @(@('TOP SPEED', '318 km/h'), @('AVG LAP', '1:33.402'), @('TYRE STINT', '18 laps'), @('FUEL', '96.4 kg'), @('POSITION', 'P2'))
$bi = 0
foreach ($b in $bs) {
    $x = 72 + ($bi * 360)
    $s += TXW ('c04-bl' + $bi) $x 886 340 26 $b[0] 18 $BODY '#8892A6' 'letterSpacing=4'
    $s += TXW ('c04-bv' + $bi) $x 916 340 52 $b[1] 38 $DISP '#FFFFFF' 'fontFeatures=+tnum'
    $bi++
}
$s += Box 72 1000 1776 6 '#E4622C' 3
$s += TXW 'c04-ft' 72 1024 1776 26 'SECTOR 3 最佳 . 实时更新 4 Hz . DEMO 演示数据' 18 $SANS '#4A5568' 'letterSpacing=2'
Write-Dsl (Join-Path $OUT 'case-04\final.snapshot') (Page 1920 1080 '#0A0B10' $s)

# ============================ case-05  城市鸟类图鉴内页（行内 WidgetSpan） ============================
Use-Case 'case-05'
$s = ''
$s += Box 0 0 1000 1414 '#FBF7EF' 0
$s += TXW 'c05-h1' 80 64 620 30 '城市鸟类图鉴 / URBAN BIRD FIELD GUIDE' 19 $BODY '#4F7A45' 'letterSpacing=4'
$s += TXW 'c05-h2' 700 64 220 30 'PLATE 03' 19 $BODY '#9A917F' 'letterSpacing=4;textAlign=RIGHT'
$s += HLine 80 106 840 2 '#1D2A24'
$s += TXW 'c05-no' 640 116 300 230 '03' 160 $DISP 'transparent' 'foregroundColor=#C9D6C9;foregroundMode=STROKE;foregroundStrokeWidth=3;textAlign=RIGHT'
$s += TXW 'c05-t1' 80 150 560 122 '普通雨燕' 84 $SERIF '#1D2A24' 'letterSpacing=4'
$s += TXW 'c05-t2' 80 282 560 40 'COMMON SWIFT . APEX APUS' 24 $BODY '#4F7A45' 'letterSpacing=6'
# ---- figure box: flight-path arc + measurement bars ----
$s += P 80 350 840 350 ('<Container width="840" height="350" color="#F2F5EF" border="1 SOLID #C9D6C9" borderRadius="6"/>')
$s += TXW 'c05-f0' 104 372 500 26 '图 A . 飞行轨迹与翼展测量' 18 $SANS '#4F7A45' 'letterSpacing=2'
$arc = ''
for ($i = 0; $i -lt 15; $i++) {
    $u = $i / 14.0
    $x = 120.0 + ($u * 560.0)
    $y = 470.0 - [Math]::Sin($u * [Math]::PI) * 74.0
    $dy = -[Math]::Cos($u * [Math]::PI) * 74.0
    $dx = 560.0 / 14.0
    $ang = [Math]::Atan2($dy, $dx) * 180.0 / [Math]::PI
    $arc += Rotate $x $y 34 7 $ang (C 34 7 '#4F7A45' 3)
}
$s += $arc
$s += Box 120 560 640 1 '#C9D6C9' 0
for ($i = 0; $i -le 4; $i++) {
    $x = 120 + ($i * 160)
    $s += Box $x 554 1 13 '#C9D6C9' 0
    $s += TXW ('c05-ax' + $i) ($x - 30) 572 60 24 ([string]($i * 10) + ' cm') 15 $BODY '#9A917F' 'textAlign=CENTER'
}
$s += Box 120 470 288 18 '#4F7A45' 4
$s += TXW 'c05-b1' 424 466 300 26 '体长 18 cm' 18 $SANS '#1D2A24' ''
$s += Box 120 504 640 18 '#B4451F' 4
$s += TXW 'c05-b2' 772 500 148 26 '翼展 40 cm' 18 $SANS '#1D2A24' ''
# figure footnote - fills the empty lower band of the chart box (y600..700)
$s += HLine 120 618 760 1 '#E4DED0'
$s += TXW 'c05-fn' 120 632 560 26 '横轴＝水平距离 0–40 cm . 纵轴＝相对高度 . 取 12 次连续观测均值' 16 $SANS '#5A5346' ''
$s += TXW 'c05-fu' 120 666 500 24 '采样 4 Hz . 2026-09-12 07:14 起 . 单位 cm' 15 $MONO '#9A917F' 'letterSpacing=1'
# ---- measurement table ----
$s += HLine 80 730 840 1 '#C9D6C9'
$tb = @(@('体长 BODY', '18.0 cm'), @('翼展 WINGSPAN', '40.5 cm'), @('体重 MASS', '38 g'), @('寿命 LIFESPAN', '9.2 yr'))
for ($i = 0; $i -lt $tb.Count; $i++) {
    $y = 748 + ($i * 44)
    $s += TXW ('c05-tl' + $i) 80 $y 400 32 $tb[$i][0] 21 $SANS '#4F7A45' ''
    $s += TXW ('c05-tv' + $i) 540 $y 380 32 $tb[$i][1] 21 $MONO '#1D2A24' 'textAlign=RIGHT;fontFeatures=+tnum'
    if ($i -lt 3) { $s += Box 80 ($y + 36) 840 1 '#E4DED0' 0 }
}
$s += HLine 80 934 840 1 '#C9D6C9'
# ---- the paragraph with inline WidgetSpan chips ----
$para = '<Positioned left="80" top="960" width="840" height="230"><Text fontSize="25" fontFamily="' + $SANS +
        '" color="#1D2A24" height="1.85">' +
        (RW '雨燕常在 ') + (Chip '老屋顶' 17 '#2E6FB7' '#EAF2FF' 14 32 $SANS 16) +
        (RW ' 与 ') + (Chip '桥墩' 17 '#2E6FB7' '#EAF2FF' 14 32 $SANS 16) +
        (RW ' 下筑巢，繁殖期为 ') + (Chip '4-5 月' 17 '#E4622C' '#FFFFFF' 14 32 $SANS 16) +
        (RW '；本页环志编号 ') + (Chip 'B-0317' 16 '#0B3B3A' '#7FD4C1' 14 32 $MONO 16) +
        (RW '，体长 ') + (Chip '18 cm' 17 '#4F7A45' '#FFFFFF' 14 32 $SANS 16) +
        (RW '、翼展 ') + (Chip '40 cm' 17 '#4F7A45' '#FFFFFF' 14 32 $SANS 16) +
        (RW '，遇雨转为 ') + (Chip '低空掠食' 17 '#2E6FB7' '#EAF2FF' 14 32 $SANS 16) +
        (RW '。') +
        '</Text></Positioned>'
$s += $para
# identification block - closes the dead band y1053..1190 and adds more inline chips
$s += HLine 80 1064 840 1 '#E4DED0'
$s += TXW 'c05-id' 80 1076 500 26 '辨识要点 IDENTIFICATION' 17 $BODY '#4F7A45' 'letterSpacing=3'
$idp = '<Positioned left="80" top="1108" width="840" height="92"><Text fontSize="22" fontFamily="' + $SANS +
       '" color="#1D2A24" height="1.8">' +
       (RW '初级飞羽 ') + (Chip '9 枚' 15 '#4F7A45' '#FFFFFF' 12 30 $SANS 15) +
       (RW '，尾羽 ') + (Chip '深叉' 15 '#2E6FB7' '#EAF2FF' 12 30 $SANS 15) +
       (RW '，飞行时呈 ') + (Chip '镰刀形' 15 '#B4451F' '#FFFFFF' 12 30 $SANS 15) +
       (RW '；停栖时贴附墙面，') +
       (Chip '几乎不落地' 15 '#1D2A24' '#FBF7EF' 12 30 $SANS 15) +
       (RW '，晨间集中出现在软木园上空。') +
       '</Text></Positioned>'
$s += $idp
$para2 = '<Positioned left="80" top="1200" width="840" height="110"><Text fontSize="22" fontFamily="' + $SANS +
         '" color="#5A5346" height="1.8">' +
         (RW '记录时段 ') + (Chip '06:30-08:00' 15 '#1D2A24' '#FBF7EF' 12 30 $MONO 15) +
         (RW '，样点为 ') + (Chip '软木园' 15 '#B4451F' '#FFFFFF' 12 30 $SANS 15) +
         (RW ' 上空，本页共 12 条记录，全部与明细一致。') +
         '</Text></Positioned>'
$s += $para2
$s += HLine 80 1330 840 2 '#1D2A24'
$s += TXW 'c05-f1' 80 1344 500 26 'DEMO . 演示数据 . 数据仅供版式演示' 16 $SANS '#9A917F' ''
$s += TXW 'c05-f2' 620 1344 300 26 '12 / 64' 16 $MONO '#9A917F' 'textAlign=RIGHT;fontFeatures=+tnum'
Write-Dsl (Join-Path $OUT 'case-05\final.snapshot') (Page 1000 1414 '#FBF7EF' $s)

Report-Problems
Write-Output 'gen-b03-a: 5 snapshots written'
