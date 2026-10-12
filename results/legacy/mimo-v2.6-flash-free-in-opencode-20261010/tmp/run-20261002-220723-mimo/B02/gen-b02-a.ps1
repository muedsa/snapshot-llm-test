# gen-b02-a.ps1 -- B02 cases 01..05
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $root 'tmp\run-20261002-220723-mimo\B02\lib-b02.ps1')
$script:PROBLEMS = New-Object System.Collections.Generic.List[string]

# ============================================================ case-01 迁徙季开幕海报 1080x1620
New-Case '01'
Seg (Mark 64 64 56 $TIDE $SUN $DEEP)
Seg (T 'c1-brand' 140 64 460 36 '候鸟湾观鸟站' 26 $GULL 'LEFT' 'BOLD')
Seg (T 'c1-brand2' 140 98 470 24 'MIGRANT BAY BIRD OBSERVATORY' 13 $TIDE 'LEFT' '')
$chTxt = '第 9 届迁徙季'
$chW = [Math]::Ceiling((TW $chTxt 16) + 26)
$c = Chip 'c1-chip' (1016 - $chW) 72 $chTxt $INK $TIDE 16 13 999
Seg $c[0]
Seg (RuleBand 64 142 952 $LINE_D $TIDE)

Seg (Eyebrow 'c1-eb' 64 176 952 'AUTUMN MIGRATION COUNT' '2026 秋季迁徙同步调查 · 9/20 - 11/15' 20 $TIDE '#9FC0BA')
Seg (T 'c1-t1' 64 254 952 108 '它们正飞过你的城市' 84 $GULL 'LEFT' 'BOLD')
Seg (T 'c1-t2' 64 360 952 108 '而你还没抬头。' 84 $GULL 'LEFT' 'BOLD')
Seg (Box 64 476 240 6 $SUN 3)
Seg (RuleBand 64 510 952 $LINE_D $TIDE)

Seg (TLines 'c1-desc' 64 552 952 20 @(
  '从 9 月 20 日到 11 月 15 日，57 天里候鸟湾会记录到 143 种鸟。',
  '我们每天 06:00 出发，把每一种的数量与行为回传给地方鸟类记录中心。',
  '今年秋天，同步调查与新手场都开放给公众——你只要带一双眼睛。'
) 34 '#C6D6D2')

# progress dial (segmented arc, deterministic)
Seg (DialArc 64 660 180 0.28 $TIDE '#16514F' 26 100)
Seg (T 'c1-arc-v' 64 712 180 56 '28%' 44 $SUN 'CENTER' 'BOLD')
Seg (T 'c1-arc-l' 64 766 180 24 '迁徙季 · 第 16/57 天' 14 $TIDE 'CENTER' '')
$hdr = @(
  @('活动日期', '9/20 - 11/15 · 共 57 天'),
  @('集合时间', '10/10 周六 06:30 北门'),
  @('路线',     '4 个观测点 · 全程约 2.4 km')
)
for ($i = 0; $i -lt 3; $i++) {
  $y = 672 + ($i * 64)
  Seg (T ("c1-h" + $i) 290 ($y + 6) 150 26 $hdr[$i][0] 16 $TIDE 'LEFT' '')
  Seg (T ("c1-v" + $i) 450 $y 566 32 $hdr[$i][1] 22 $GULL 'RIGHT' 'BOLD')
  if ($i -lt 2) { Seg (Box 290 ($y + 44) 726 1 $LINE_D 0) }
}

# CTA
Seg (ShadowBox 64 900 952 96 $SUN 14 '0 8 24 #00000055')
Seg (T 'c1-cta' 104 926 872 52 '扫码预约名额 · 每场限 30 人' 36 '#FFFFFF' 'CENTER' 'BOLD')

# three highlights
$h3t = @('望远镜免费借用', '新手 15 分钟上手', '当日数据回传')
$h3s = @(
  @('12 台双筒，押金 0，', '北门服务台登记即借'),
  @('志愿者一对一带教，', '不用先懂鸟也能来'),
  @('观测记录当天进入', '地方鸟类记录中心')
)
for ($i = 0; $i -lt 3; $i++) {
  $x = 64 + ($i * 326)
  Seg (NumChip $x 1040 36 ([string]($i + 1)) $TIDE $DEEP 8)
  Seg (T ("c1-hl" + $i) $x 1092 300 30 $h3t[$i] 20 $GULL 'LEFT' 'BOLD')
  Seg (TLines ("c1-hs" + $i) $x 1128 300 14 $h3s[$i] 22 $TIDE)
}
Seg (RuleBand 64 1230 952 $LINE_D $TIDE)

# past editions stats
$st = @(
  @('本届物种目标', '143 种', '较往届 +11'),
  @('往届累计',     '33,400 条', '2019-2025 共 8 届'),
  @('参与志愿者',   '62 名', '每周至少 1 次')
)
for ($i = 0; $i -lt 3; $i++) {
  $x = 64 + ($i * 326)
  Seg (StatChip ("c1-s" + $i) $x 1276 300 $st[$i][0] $st[$i][1] $st[$i][2] 16 $TIDE $GULL '#9FC0BA')
}
for ($i = 0; $i -lt 6; $i++) {
  Seg (Mark (64 + $i * 160) 1408 30 '#7FB2A855' '' $DEEP)
}
Seg (RuleBand 64 1470 952 $LINE_D $TIDE)
Seg (FooterLine 'c1-f' 64 1500 952 'CENTER' '#9FC0BA' 14)
$l1 = Finish-Case '01' 1080 1620 $DEEP

# ============================================================ case-02 湿地导览地图 1920x720
New-Case '02'
Seg (Grad 0 0 1920 720 '#6FA9A1,#3F7C77' 'LINEAR' 'TOP_LEFT' 'BOTTOM_RIGHT' 0)
# shallow-water shoals (translucent overlays on the water gradient)
Seg (Circle 540 150 300 '#FFFFFF12' $null)
Seg (Circle 950 430 240 '#FFFFFF0E' $null)
Seg (Circle 1560 430 200 '#FFFFFF10' $null)
Seg (Circle 700 430 160 '#FFFFFF0A' $null)
# navigation channel
Seg (DashH 620 168 560 3 '#FFFFFF66' 18 14)
Seg (T 'c2-ch' 620 132 320 26 '航道 · 禁止游泳与垂钓' 15 '#FFFFFFCC' 'LEFT' '')
# land masses
Seg (Box 430 540 1440 160 $SAND 40)
Seg (Box 740 296 430 180 '#2F5B4E' 56)
Seg (Box 1300 140 400 240 '#C9BA93' 72)
Seg (Box 1490 420 300 110 '#2F5B4E' 48)
# water sparkle texture
for ($i = 0; $i -lt 26; $i++) {
  $x = 500 + (($i * 71) % 1360)
  $y = 90 + (($i * 137) % 430)
  Seg (Box $x $y 46 3 '#FFFFFF33' 2)
}
# walking trail (dashed)
Seg (DashV 539 540 122 4 '#FFFFFFCC' 14 10)
Seg (DashH 540 539 360 4 '#FFFFFFCC' 14 10)
Seg (DashV 899 400 140 4 '#FFFFFFCC' 14 10)
Seg (DashH 900 399 400 4 '#FFFFFFCC' 14 10)
Seg (DashV 1299 300 100 4 '#FFFFFFCC' 14 10)
Seg (DashH 1300 299 262 4 '#FFFFFFCC' 14 10)

# observation points
$pts = @(
  @(540, 540, '1', '北门服务台'),
  @(900, 400, '2', '芦苇荡观测屋'),
  @(1300, 300, '3', '栈道尽头平台'),
  @(1562, 300, '4', '潮间带观测点')
)
foreach ($p in $pts) {
  $cx = $p[0]; $cy = $p[1]
  Seg (Circle ($cx - 30) ($cy - 30) 60 '#0B3B3A' '0 6 14 #00000055')
  Seg (Circle ($cx - 23) ($cy - 23) 46 $SUN $null)
  Seg (T ('c2-p' + $p[2]) ($cx - 30) ($cy - 17) 60 36 $p[2] 26 '#FFFFFF' 'CENTER' 'BOLD')
  $lw = [Math]::Ceiling((TW $p[3] 17) + 26)
  Seg (Box ($cx - $lw / 2.0) ($cy + 40) $lw 30 '#0B3B3ACC' 15)
  Seg (T ('c2-pl' + $p[2]) ($cx - $lw / 2.0) ($cy + 45) $lw 24 $p[3] 17 '#FFFFFF' 'CENTER' 'BOLD')
}
# entrance marker (kept clear of the left panel, which ends at x=484)
Seg (Box 500 664 140 36 $SUN 18)
Seg (T 'c2-ent' 500 670 140 26 '北门入口' 17 '#FFFFFF' 'CENTER' 'BOLD')
# north arrow: white disc, orange north dot on top, N underneath
Seg (Circle 1796 64 64 '#FFFFFFEE' $null)
Seg (Box 1821 74 14 14 $SUN 7)
Seg (T 'c2-n' 1796 92 64 30 'N' 22 '#0B3B3A' 'CENTER' 'BOLD')
# scale bar (sits on the sand strip, so use dark/light contrast)
Seg (Box 1700 660 60 8 '#0B3B3A' 0)
Seg (Box 1760 660 60 8 '#FFFFFF' 0)
Seg (T 'c2-sc' 1700 674 120 24 '0        200 m' 14 '#0B3B3A' 'CENTER' '')

# left panel
Seg (ShadowBox 44 44 440 632 $INK 14 '0 10 30 #00000066')
Seg (Mark 76 76 48 $TIDE $SUN $INK)
Seg (T 'c2-brand' 138 74 320 32 '候鸟湾观鸟站' 22 $GULL 'LEFT' 'BOLD')
Seg (T 'c2-brand2' 138 104 330 22 'MIGRANT BAY' 13 $TIDE 'LEFT' '')
Seg (Eyebrow 'c2-eb' 76 152 376 'WETLAND TRAIL MAP' '湿地导览 · 步行约 40 分钟' 17 $TIDE '#9FC0BA')
Seg (T 'c2-title' 76 214 376 46 '一条环线，四个点' 34 $GULL 'LEFT' 'BOLD')
Seg (RuleBand 76 272 376 $LINE_D $TIDE)
$lg = @(
  @('1', '北门服务台', '借镜、登记、失物招领'),
  @('2', '芦苇荡观测屋', '隐蔽屋，听声优先'),
  @('3', '栈道尽头平台', '看潮间带与雁鸭群'),
  @('4', '潮间带观测点', '涨潮前 1 小时最佳')
)
for ($i = 0; $i -lt 4; $i++) {
  $y = 300 + ($i * 58)
  Seg (NumChip 76 $y 26 $lg[$i][0] $SUN '#FFFFFF' 6)
  Seg (T ("c2-ln" + $i) 114 ($y - 2) 338 26 $lg[$i][1] 17 $GULL 'LEFT' 'BOLD')
  Seg (T ("c2-lh" + $i) 114 ($y + 24) 338 22 $lg[$i][2] 13 $TIDE 'LEFT' '')
}
Seg (RuleBand 76 540 376 $LINE_D $TIDE)
Seg (Circle 80 566 16 $SAND $null)
Seg (T 'c2-lg1' 108 562 344 24 '滩涂 / 芦苇荡' 15 $GULL 'LEFT' '')
Seg (Circle 80 596 16 $TIDE $null)
Seg (T 'c2-lg2' 108 592 344 24 '潮沟与开放水域' 15 $GULL 'LEFT' '')
Seg (DashH 76 628 24 4 '#FFFFFFCC' 8 6)
Seg (T 'c2-lg3' 108 620 344 24 '白色虚线 · 步行栈道' 15 $GULL 'LEFT' '')
Seg (FooterLine 'c2-f' 76 652 376 'LEFT' '#9FC0BA' 12 '候鸟湾湿地公园 · 演示数据 DEMO')
$l2 = Finish-Case '02' 1920 720 '#4E8B85'

# ============================================================ case-03 观鸟须知与望远镜使用 900x1600
New-Case '03'
Seg (Mark 54 54 48 $TIDE $SUN $DEEP)
Seg (T 'c3-brand' 116 54 400 32 '候鸟湾观鸟站' 22 $GULL 'LEFT' 'BOLD')
Seg (T 'c3-brand2' 116 84 420 22 '站外立牌 · 望远镜使用' 13 $TIDE 'LEFT' '')
$ch3 = '免费借用'
$w3 = [Math]::Ceiling((TW $ch3 15) + 26)
$c3 = Chip 'c3-chip' (846 - $w3) 62 $ch3 $SUN '#FFFFFF' 15 13 999
Seg $c3[0]
Seg (RuleBand 54 132 792 $LINE_D $TIDE)

Seg (Eyebrow 'c3-eb' 54 164 792 'HOW TO USE THE BINOCULARS' '先调清楚，再走出去' 18 $TIDE '#9FC0BA')
Seg (T 'c3-t' 54 232 792 60 '三分钟，学会调焦' 44 $GULL 'LEFT' 'BOLD')

# binocular diagram: eyepiece tubes over objective barrels, hinge + focus wheel between
Seg (Box 210 315 150 100 '#0A2E2D' 26)
Seg (Box 540 315 150 100 '#0A2E2D' 26)
Seg (Box 150 400 260 160 $INK 44)
Seg (Box 490 400 260 160 $INK 44)
Seg (Circle 244 444 72 '#1E5C59' $null)
Seg (Circle 584 444 72 '#1E5C59' $null)
Seg (Box 175 420 210 6 '#2A6E6B' 3)
Seg (Box 515 420 210 6 '#2A6E6B' 3)
Seg (Box 400 435 100 85 '#0F4A48' 24)
Seg (Box 430 392 40 58 $SUN 12)
# interpupillary-distance arrow in the gap between the eyepieces
Seg (Box 375 370 150 4 $TIDE 2)
Seg (Box 375 362 4 20 $TIDE 2)
Seg (Box 521 362 4 20 $TIDE 2)
# numbered call-outs
Seg (NumChip 472 398 30 '1' $SUN '#FFFFFF' 15)
Seg (NumChip 665 285 30 '2' $TIDE $DEEP 15)
Seg (NumChip 435 285 30 '3' $TIDE $DEEP 15)
Seg (T 'c3-cap' 54 590 792 26 '站内为 12x42 双筒；借出前请先检查目镜有无划痕与霉点。' 13 $TIDE 'LEFT' '')
$steps = @(
  @('1', '调焦轮', '中间前后推，先让右眼清楚'),
  @('2', '屈光度环', '右眼近视的人先调这一圈'),
  @('3', '目镜间距', '推到刚好合成一个圆')
)
for ($i = 0; $i -lt 3; $i++) {
  $x = 54 + ($i * 264)
  Seg (NumChip $x 618 34 $steps[$i][0] $SUN '#FFFFFF' 8)
  Seg (T ("c3-sn" + $i) ($x + 46) 620 218 30 $steps[$i][1] 19 $GULL 'LEFT' 'BOLD')
  Seg (T ("c3-sh" + $i) $x 662 250 46 $steps[$i][2] 14 $TIDE 'LEFT' '')
}
Seg (RuleBand 54 730 792 $LINE_D $TIDE)

Seg (SectionTitle 'c3-sb' 54 764 792 '观鸟礼仪 · 5 条' 26 $SUN $GULL)
$et = @(
  '不追、不喂、不放音乐；退到它先动为止。',
  '穿灰绿或棕色，别穿白、黄、红。',
  '无人机与闪光灯全程禁用。',
  '狗不进栈道；婴儿车走无障碍支线。',
  '看到受伤或落单的鸟，先叫志愿者，别自己碰。'
)
for ($i = 0; $i -lt 5; $i++) {
  $y = 826 + ($i * 62)
  Seg (NumChip 54 $y 32 ([string]($i + 1)) '#16514F' $TIDE 8)
  Seg (T ("c3-e" + $i) 102 ($y + 2) 744 34 $et[$i] 18 $GULL 'LEFT' '')
}
Seg (RuleBand 54 1152 792 $LINE_D $TIDE)

Seg (SectionTitle 'c3-sc' 54 1186 792 '借用须知' 26 $SUN $GULL)
$chx = 54
foreach ($t3 in @('12 台双筒 · 押金 0', '登记姓名 + 手机后四位', '当日 17:30 前归还')) {
  $c = Chip 'c3-c' $chx 1238 $t3 '#16514F' $GULL 16 14 999
  Seg $c[0]
  $chx = $chx + $c[1] + 16
}
Seg (T 'c3-note' 54 1300 792 30 '雨天或 6 级以上大风暂停外借，服务台会挂出牌子。' 15 $TIDE 'LEFT' '')
Seg (ShadowBox 54 1372 792 88 $SUN 14 '0 8 24 #00000055')
Seg (T 'c3-cta' 84 1396 732 46 '第一次来？先去北门领一张新手卡' 30 '#FFFFFF' 'CENTER' 'BOLD')
Seg (RuleBand 54 1500 792 $LINE_D $TIDE)
Seg (FooterLine 'c3-f' 54 1530 792 'CENTER' '#9FC0BA' 13)
$l3 = Finish-Case '03' 900 1600 $DEEP

# ============================================================ case-04 每日观测看板 1920x1080
New-Case '04'
Seg (Box 0 0 1920 112 $INK 0)
Seg (Mark 64 32 44 $TIDE $SUN $INK)
Seg (T 'c4-brand' 122 34 420 34 '候鸟湾观鸟站 · 今日观测看板' 22 $GULL 'LEFT' 'BOLD')
Seg (T 'c4-brand2' 122 70 460 22 'MIGRANT BAY · DAILY BOARD' 13 $TIDE 'LEFT' '')
$dw = [Math]::Ceiling((TW '17:42 更新' 16) + 28)
$c4 = Chip 'c4-live' (1856 - $dw) 42 '17:42 更新' $SUN '#FFFFFF' 16 14 999
Seg $c4[0]
Seg (T 'c4-date' 1000 44 600 34 '2026-10-05 · 周一 · 多云 18°C' 20 $GULL 'RIGHT' '')

# ---- left column
Seg (Eyebrow 'c4-e1' 64 150 460 'TODAY AT A GLANCE' '今日概览' 17 $TIDE '#9FC0BA')
$g = @(
  @('今日鸟种', '16', '种 · 较昨日 +3'),
  @('今日个体', '412', '只 · 雁鸭为主'),
  @('在站观鸟人', '21', '人 · 17:42 当前'),
  @('借出望远镜', '9/12', '台 · 在架 3 台')
)
for ($i = 0; $i -lt 4; $i++) {
  $x = 64 + (($i % 2) * 240)
  $y = 210 + ([Math]::Floor($i / 2) * 150)
  Seg (StatChip ("c4-g" + $i) $x $y 220 $g[$i][0] $g[$i][1] $g[$i][2] 15 $TIDE $GULL '#9FC0BA')
}
Seg (RuleBand 64 480 436 $LINE_D $TIDE)
Seg (SectionTitle 'c4-s1' 64 512 436 '观鸟人潮 · 每小时（人）' 18 $SUN $GULL)
$bars = @(28, 41, 37, 34, 31, 28, 25, 21)
for ($i = 0; $i -lt 8; $i++) {
  $bh = [Math]::Round($bars[$i] / 41.0 * 132, 0)
  $bx = 64 + ($i * 56)
  Seg (Box $bx (700 - $bh) 36 $bh $TIDE 4)
  if ($bars[$i] -eq 41) { Seg (Box $bx (700 - $bh) 36 5 $SUN 2) }
  Seg (T ("c4-b" + $i) $bx 708 36 22 ('{0:d2}' -f (10 + $i)) 13 '#9FC0BA' 'CENTER' '')
}
Seg (Box 64 700 436 2 $LINE_D 0)
Seg (T 'c4-peak' 64 736 436 22 '峰值 11:00 为 41 人，之后逐小时回落至当前 21 人' 13 '#9FC0BA' 'LEFT' '')

Seg (RuleBand 64 774 436 $LINE_D $TIDE)
Seg (SectionTitle 'c4-s2' 64 806 436 '今日潮汐与下一步' 18 $SUN $GULL)
$trow = @(
  @('涨潮',     '11:20 满 3.4 m', $GULL),
  @('落潮转向', '17:50',           $SUN),
  @('下次同步', '周六 06:30',      $GULL)
)
for ($i = 0; $i -lt 3; $i++) {
  $y = 852 + ($i * 50)
  Seg (T ("c4-tl" + $i) 64 ($y + 4) 150 26 $trow[$i][0] 15 $TIDE 'LEFT' '')
  Seg (T ("c4-tv" + $i) 210 $y 290 30 $trow[$i][1] 19 $trow[$i][2] 'RIGHT' 'BOLD')
  if ($i -lt 2) { Seg (Box 64 ($y + 36) 436 1 $LINE_D 0) }
}

# ---- centre column: species list
Seg (Eyebrow 'c4-e2' 560 150 760 'SPECIES TODAY' '今日鸟种 · 按记录先后' 17 $TIDE '#9FC0BA')
Seg (RuleBand 560 212 760 $LINE_D $TIDE)
Seg (T 'c4-th' 560 226 260 24 '物种' 13 $TIDE 'LEFT' '')
Seg (T 'c4-th2' 840 226 340 24 '学名' 13 $TIDE 'LEFT' '')
Seg (T 'c4-th3' 1230 226 90 24 '数量' 13 $TIDE 'RIGHT' '')
$sp = @(
  @('绿头鸭', 'Anas platyrhynchos', '96'),
  @('苍鹭',   'Ardea cinerea',       '12'),
  @('白鹭',   'Egretta garzetta',     '28'),
  @('黑水鸡', 'Gallinula chloropus',  '36'),
  @('小䴙䴘', 'Tachybaptus ruficollis','18'),
  @('普通鸬鹚','Phalacrocorax carbo',  '9'),
  @('斑嘴鸭', 'Anas zonorhyncha',     '44'),
  @('凤头麦鸡','Vanellus vanellus',    '27'),
  @('金眶鸻', 'Charadrius dubius',    '14'),
  @('矶鹬',   'Actitis hypoleucos',    '8'),
  @('棕背伯劳','Lanius schach',         '3'),
  @('白头鹎', 'Pycnonotus sinensis',   '16'),
  @('珠颈斑鸠','Streptopelia chinensis','22'),
  @('普通翠鸟','Alcedo atthis',         '4'),
  @('夜鹭',   'Nycticorax nycticorax', '11'),
  @('红嘴鸥', 'Chroicocephalus ridibundus','64')
)
for ($i = 0; $i -lt $sp.Count; $i++) {
  $y = 260 + ($i * 42)
  if (($i % 2) -eq 1) { Seg (Box 560 ($y - 4) 760 40 '#FFFFFF0A' 4) }
  Seg (SpeciesRow ("c4-s" + $i) 560 $y 760 $sp[$i][0] $sp[$i][1] $sp[$i][2] $TIDE $GULL '#8FA9A5' $SUN 17 40)
}

# ---- right column
Seg (Eyebrow 'c4-e3' 1360 150 496 'NEXT UP' '接下来' 17 $TIDE '#9FC0BA')
$nx = @(
  @('17:50', '潮汐转向', '栈道尽头看雁鸭群起飞'),
  @('18:00', '站点关闭', '请把望远镜归还北门服务台'),
  @('10/10 06:30', '同步调查', '还缺 6 名志愿者'),
  @('10/11 09:00', '亲子场',   '余 4 席 · 6-12 岁')
)
for ($i = 0; $i -lt 4; $i++) {
  $y = 208 + ($i * 92)
  Seg (T ("c4-nt" + $i) 1360 $y 496 30 $nx[$i][0] 20 $SUN 'LEFT' 'BOLD')
  Seg (T ("c4-nn" + $i) 1360 ($y + 32) 496 28 $nx[$i][1] 18 $GULL 'LEFT' 'BOLD')
  Seg (T ("c4-nh" + $i) 1360 ($y + 58) 496 24 $nx[$i][2] 14 $TIDE 'LEFT' '')
  if ($i -lt 3) { Seg (Box 1360 ($y + 84) 496 1 $LINE_D 0) }
}
Seg (RuleBand 1360 592 496 $LINE_D $TIDE)
Seg (SectionTitle 'c4-s2' 1360 624 496 '望远镜借用 · 12 台' 18 $SUN $GULL)
for ($i = 0; $i -lt 12; $i++) {
  $dx = 1360 + (($i % 6) * 42)
  $dy = 674 + ([Math]::Floor($i / 6) * 44)
  if ($i -lt 9) { Seg (Circle $dx $dy 30 $SUN $null) }
  else { Seg (Circle $dx $dy 30 '#16514F' $null) }
}
Seg (T 'c4-lg' 1630 676 226 26 '借出 9 · 在架 3' 15 $TIDE 'LEFT' '')
Seg (RuleBand 1360 776 496 $LINE_D $TIDE)
Seg (SectionTitle 'c4-s3' 1360 808 496 '近 7 日记录数（条）' 18 $SUN $GULL)
$trend = @(58, 64, 51, 73, 69, 82, 76)
$tw0 = 496.0 / 7.0
for ($i = 0; $i -lt 7; $i++) {
  $x = 1360 + ($i * $tw0) + ($tw0 / 2.0)
  $y = 950 - (($trend[$i] - 45) / 40.0 * 84)
  Seg (Circle ($x - 7) ($y - 7) 14 $SUN $null)
  if ($i -gt 0) {
    $px = 1360 + (($i - 1) * $tw0) + ($tw0 / 2.0)
    $py = 950 - (($trend[$i - 1] - 45) / 40.0 * 84)
    $len = [Math]::Sqrt(($x - $px) * ($x - $px) + ($y - $py) * ($y - $py))
    $ang = [Math]::Atan2(($y - $py), ($x - $px)) * 180.0 / [Math]::PI
    Seg (Rotate (($x + $px) / 2.0 - $len / 2.0) (($y + $py) / 2.0 - 2) $len 4 $ang (C $len 4 $TIDE 0))
  }
}
Seg (Box 1360 958 496 1 $LINE_D 0)

Seg (Box 0 1004 1920 76 $INK 0)
Seg (FooterLine 'c4-f' 64 1030 1792 'CENTER' '#9FC0BA' 14)
$l4 = Finish-Case '04' 1920 1080 $DEEP

# ============================================================ case-05 新手工作坊手册封面 1000x1400
New-Case '05'
Seg (Box 0 0 1000 14 $DEEP 0)
Seg (Box 0 14 1000 4 $SUN 0)
Seg (Mark 60 66 56 $DEEP $SUN $PAPER)
Seg (T 'c5-brand' 132 66 400 34 '候鸟湾观鸟站' 24 $DEEP 'LEFT' 'BOLD')
Seg (T 'c5-brand2' 132 98 420 24 'MIGRANT BAY BIRD OBSERVATORY' 13 '#4A6B67' 'LEFT' '')
$w5 = [Math]::Ceiling((TW '学员手册 · 第 1 版' 15) + 28)
$c5 = Chip 'c5-chip' (940 - $w5) 74 '学员手册 · 第 1 版' $DEEP $GULL 15 14 999
Seg $c5[0]
Seg (RuleBand 60 154 880 $LINE_L '#0B3B3A')

Seg (Eyebrow 'c5-eb' 60 186 880 'BEGINNER FIELD WORKSHOP' '新手观鸟工作坊 · 户外课学员手册' 19 $DEEP '#4A6B67')
Seg (T 'c5-t1' 60 258 880 70 '第一次出门，' 52 $DEEP 'LEFT' 'BOLD')
Seg (T 'c5-t2' 60 326 880 70 '带这四页就够' 52 $DEEP 'LEFT' 'BOLD')
Seg (Box 60 404 200 6 $SUN 3)
Seg (TLines 'c5-desc' 60 440 780 17 @(
  '本手册配合 2 小时户外课使用，四个环节对应四页。',
  '每页底部有「完成勾选」，课后连同野外记录表一起交给带教志愿者。'
) 28 '#4A6B67')

$mod = @(
  @('1', '认识你的望远镜', @('调焦轮、屈光度、目镜间距三件事', '先在站内对清楚墙上的字，再出门')),
  @('2', '听，比看更快',   @('闭眼 30 秒，说出你听到的 3 种声音', '鸟鸣图谱在附页，不必提前背')),
  @('3', '记录五要素',     @('时间 / 种类 / 数量 / 行为 / 备注', '五项与野外记录表逐列对应，别记在自己手背上')),
  @('4', '把数据交出去',   @('当天 17:30 前交给北门服务台', '志愿者当晚汇总进地方鸟类记录中心'))
)
for ($i = 0; $i -lt 4; $i++) {
  $y = 536 + ($i * 120)
  Seg (NumChip 60 $y 42 $mod[$i][0] $DEEP $GULL 10)
  Seg (T ("c5-mn" + $i) 122 ($y + 2) 620 36 $mod[$i][1] 23 $DEEP 'LEFT' 'BOLD')
  Seg (TLines ("c5-mh" + $i) 122 ($y + 42) 700 15 $mod[$i][2] 25 '#4A6B67')
  Seg (Box 838 $y 62 42 '#E9E3D2' 8)
  Seg (T ("c5-mp" + $i) 838 ($y + 11) 62 24 ('P.' + (2 + $i * 2)) 15 $DEEP 'CENTER' 'BOLD')
}
Seg (RuleBand 60 1018 880 $LINE_L '#0B3B3A')

Seg (Box 60 1050 880 172 '#E9E3D2' 14)
Seg (Box 60 1050 8 172 $SUN 4)
Seg (T 'c5-gt' 92 1074 400 34 '你的小组' 21 $DEEP 'LEFT' 'BOLD')
$gx = 92
foreach ($g5 in @('A · 芦苇荡', 'B · 栈道', 'C · 潮间带', 'D · 观测屋')) {
  $c = Chip 'c5-g' $gx 1118 $g5 $DEEP $GULL 16 16 999
  Seg $c[0]
  $gx = $gx + $c[1] + 14
}
Seg (T 'c5-gn' 92 1164 816 30 '小组号见报名短信；迟到请直接到北门服务台，不要自行追队。' 15 '#4A6B67' 'LEFT' '')

Seg (T 'c5-ck' 60 1246 200 30 '完成勾选' 17 $DEEP 'LEFT' 'BOLD')
$ck = @('调焦', '静音', '记录', '交表')
for ($i = 0; $i -lt 4; $i++) {
  $x = 190 + ($i * 190)
  Seg (Box ($x - 1) 1245 28 28 '#0B3B3A' 6)
  Seg (Box $x 1246 26 26 '#FFFFFF' 5)
  Seg (T ("c5-c" + $i) ($x + 36) 1248 140 26 $ck[$i] 16 $DEEP 'LEFT' '')
}
Seg (Box 60 1300 880 2 '#0B3B3A' 0)
Seg (FooterLine 'c5-f' 60 1318 880 'CENTER' '#4A6B67' 13)
$l5 = Finish-Case '05' 1000 1400 $PAPER

# ---- report ----
"problems = " + $script:PROBLEMS.Count
foreach ($p in $script:PROBLEMS) { "  " + $p }
"lens: c01=$l1 c02=$l2 c03=$l3 c04=$l4 c05=$l5"
