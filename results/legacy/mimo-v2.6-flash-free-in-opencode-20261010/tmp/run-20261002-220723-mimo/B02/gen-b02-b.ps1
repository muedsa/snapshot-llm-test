# gen-b02-b.ps1 -- B02 cases 06..10
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $root 'tmp\run-20261002-220723-mimo\B02\lib-b02.ps1')
$script:PROBLEMS = New-Object System.Collections.Generic.List[string]

# ============================================================ case-06 野外记录表 830x1170
New-Case '06'
Seg (Box 0 0 830 12 $DEEP 0)
Seg (Box 0 12 830 4 $SUN 0)
Seg (Mark 50 42 40 $TIDE $SUN $PAPER)
Seg (T 'c6-brand' 102 42 420 30 '候鸟湾观鸟站' 21 $DEEP 'LEFT' 'BOLD')
Seg (T 'c6-brand2' 102 72 430 22 '野外记录表 · FIELD LOG' 12 '#4A6B67' 'LEFT' '')
$w6 = [Math]::Ceiling((TW '打印后手写' 14) + 28)
$c6 = Chip 'c6-chip' (780 - $w6) 50 '打印后手写' $DEEP $GULL 14 14 999
Seg $c6[0]
Seg (RuleBand 50 114 730 $LINE_L '#0B3B3A')
Seg (T 'c6-title' 50 140 730 46 '野外记录表' 34 $DEEP 'LEFT' 'BOLD')
Seg (T 'c6-sub' 50 190 730 24 '五要素缺一不可：时间 / 种类 / 数量 / 行为 / 备注' 13 '#4A6B67' 'LEFT' '')

$f6 = @('日期', '天气', '观察者', '样线 / 样点')
for ($i = 0; $i -lt 4; $i++) {
  $x = 50 + ($i * 186)
  Seg (T ("c6-f" + $i) $x 232 172 22 $f6[$i] 13 '#4A6B67' 'LEFT' '')
  Seg (Box $x 266 172 1 '#0B3B3A66' 0)
}
Seg (Box 50 292 730 36 $DEEP 8)
$c0 = 50;   $w0 = 76
$c1 = 134;  $w1 = 170
$c2 = 312;  $w2 = 64
$c3 = 384;  $w3 = 140
$c4 = 532;  $w4 = 248
Seg (T 'c6-h0' ($c0 + 10) 299 ($w0 - 16) 24 '时间' 13 $GULL 'LEFT' 'BOLD')
Seg (T 'c6-h1' ($c1 + 10) 299 ($w1 - 16) 24 '物种' 13 $GULL 'LEFT' 'BOLD')
Seg (T 'c6-h2' ($c2 - 8) 299 ($w2 + 4) 24 '数量' 13 $GULL 'RIGHT' 'BOLD')
Seg (T 'c6-h3' ($c3 + 10) 299 ($w3 - 16) 24 '行为' 13 $GULL 'LEFT' 'BOLD')
Seg (T 'c6-h4' ($c4 + 10) 299 ($w4 - 16) 24 '备注' 13 $GULL 'LEFT' 'BOLD')

$s6 = @(
  @('06:12', '绿头鸭',   '24', '取食', '左侧浅滩，雌雄混群'),
  @('06:18', '苍鹭',     '2',  '伫立', '距栈道约 30 m'),
  @('06:25', '白鹭',     '8',  '飞行', '沿潮沟向北'),
  @('06:31', '黑水鸡',   '5',  '游动', '苇丛边缘'),
  @('06:40', '小䴙䴘',   '3',  '潜水', '连续 4 次'),
  @('06:47', '珠颈斑鸠', '4',  '停栖', '北侧防护林')
)
for ($i = 0; $i -lt 14; $i++) {
  $y = 328 + ($i * 38)
  if (($i % 2) -eq 1) { Seg (Box 50 $y 730 38 '#0B3B3A0D' 0) }
  Seg (Box 50 ($y + 37) 730 1 '#0B3B3A4D' 0)
  if ($i -lt 6) {
    $r = $s6[$i]
    Seg (T ("c6-t" + $i) ($c0 + 10) ($y + 7) ($w0 - 16) 24 $r[0] 14 $DEEP 'LEFT' 'BOLD')
    Seg (T ("c6-n" + $i) ($c1 + 10) ($y + 7) ($w1 - 16) 24 $r[1] 14 $DEEP 'LEFT' '')
    Seg (T ("c6-q" + $i) ($c2 - 8) ($y + 7) ($w2 + 4) 24 $r[2] 14 $DEEP 'RIGHT' 'BOLD')
    Seg (T ("c6-b" + $i) ($c3 + 10) ($y + 7) ($w3 - 16) 24 $r[3] 14 $DEEP 'LEFT' '')
    Seg (T ("c6-m" + $i) ($c4 + 10) ($y + 7) ($w4 - 16) 24 $r[4] 14 '#4A6B67' 'LEFT' '')
  }
}
Seg (Box 50 874 730 44 '#E9E3D2' 10)
Seg (T 'c6-sum' 72 884 320 26 '合计 46 只 · 6 种' 16 $DEEP 'LEFT' 'BOLD')
Seg (T 'c6-sig' 420 884 340 26 '记录人签名 ____________' 15 '#4A6B67' 'RIGHT' '')
Seg (T 'c6-nt' 50 938 730 26 '备注 / 异常（受伤、网具、人为干扰）' 15 $DEEP 'LEFT' 'BOLD')
Seg (DashH 50 988 730 1 '#0B3B3A33' 20 16)
Seg (DashH 50 1014 730 1 '#0B3B3A33' 20 16)
Seg (DashH 50 1040 730 1 '#0B3B3A33' 20 16)
Seg (RuleBand 50 1062 730 $LINE_L '#0B3B3A')
Seg (FooterLine 'c6-f' 50 1084 730 'CENTER' '#4A6B67' 12)
$l6 = Finish-Case '06' 830 1170 $PAPER

# ============================================================ case-07 志愿者证 1040x660
New-Case '07'
Seg (Box 0 0 1040 86 $INK 0)
Seg (Mark 40 20 44 $TIDE $SUN $INK)
Seg (T 'c7-brand' 96 18 520 32 '候鸟湾观鸟站' 21 $GULL 'LEFT' 'BOLD')
Seg (T 'c7-brand2' 96 48 520 24 'MIGRANT BAY BIRD OBSERVATORY' 12 $TIDE 'LEFT' '')
$w7 = [Math]::Ceiling((TW '志愿者证' 18) + 30)
$c7 = Chip 'c7-chip' (1000 - $w7) 26 '志愿者证' $SUN '#FFFFFF' 18 15 999
Seg $c7[0]

Seg (Box 40 116 240 260 $SAND 12)
Seg (Box 88 244 144 100 '#7FB2A8' 44)
Seg (Circle 110 150 100 '#7FB2A8' $null)
Seg (T 'c7-ph' 40 386 240 22 '照片位 35 x 45 mm' 12 '#4A6B67' 'CENTER' '')

Seg (Eyebrow 'c7-eb' 320 116 680 'ID CARD' '候鸟湾观鸟站 · 志愿者证' 17 $TIDE '#9FC0BA')
Seg (T 'c7-name' 320 176 680 68 '林之遥' 50 $GULL 'LEFT' 'BOLD')
Seg (T 'c7-latin' 320 248 680 26 'LIN ZHIYAO' 15 $TIDE 'LEFT' '')
Seg (RuleBand 320 290 680 $LINE_D $TIDE)
$info = @(
  @('编号',     'MB-V-0062',            $GULL),
  @('有效期',   '2026-12-31',           $GULL),
  @('加入日期', '2024-04-12',           $GULL),
  @('班次',     '每周六 06:00-10:00',   $GULL),
  @('岗位',     '退潮巡护 · 数据录入',  $GULL),
  @('服务时长', '412 h · 本届 68 h',     $SUN)
)
for ($i = 0; $i -lt 6; $i++) {
  $col = $i % 2
  $row = [Math]::Floor($i / 2)
  $x = 320 + ($col * 350)
  $y = 322 + ($row * 70)
  Seg (T ("c7-il" + $i) $x $y 330 20 $info[$i][0] 13 $TIDE 'LEFT' '')
  Seg (T ("c7-iv" + $i) $x ($y + 22) 330 30 $info[$i][1] 19 $info[$i][2] 'LEFT' 'BOLD')
  if ($row -lt 2) { Seg (Box 320 ($y + 58) 680 1 $LINE_D 0) }
}
Seg (RuleBand 40 530 960 $LINE_D $TIDE)
$chx = 40
foreach ($t7 in @('可入缓冲区', '可借用望远镜', '需跟队出勤')) {
  $c = Chip 'c7-r' $chx 552 $t7 '#16514F' $GULL 14 14 999
  Seg $c[0]
  $chx = $chx + $c[1] + 12
}
Seg (T 'c7-rt' 600 554 400 24 '证号 MB-V-0062 · 演示数据 DEMO' 13 $TIDE 'RIGHT' '')
Seg (T 'c7-f' 40 592 960 20 '候鸟湾湿地公园北门 · 望潮路 128 号 · 每日 06:00-18:00 免费开放' 12 '#9FC0BA' 'LEFT' '')
$l7 = Finish-Case '07' 1040 660 $DEEP

# ============================================================ case-08 月度活动日程 1748x760
New-Case '08'
Seg (Mark 46 40 52 $TIDE $SUN $DEEP)
Seg (T 'c8-brand' 112 38 760 40 '候鸟湾观鸟站 · 10 月活动日程' 26 $GULL 'LEFT' 'BOLD')
Seg (T 'c8-brand2' 112 76 760 24 'OCTOBER 2026 PROGRAMME' 13 $TIDE 'LEFT' '')
$w8 = [Math]::Ceiling((TW '免费 · 需预约' 16) + 30)
$c8 = Chip 'c8-chip' (1702 - $w8) 44 '免费 · 需预约' $SUN '#FFFFFF' 16 15 999
Seg $c8[0]
Seg (T 'c8-note' 1050 86 652 24 '共 9 场 · 名额实时更新 · 演示数据 DEMO' 14 '#9FC0BA' 'RIGHT' '')
Seg (RuleBand 46 116 1656 $LINE_D $TIDE)

$ev = @(
  @('10-10','周六','06:30','秋季同步调查（第 5 次）','北门集合','走完整条样线，回传地方记录中心',     '余 6 席',  '需 3 小时'),
  @('10-11','周日','09:00','芦苇荡亲子场','北门集合','认 10 种常见水鸟，含望远镜使用课',     '余 4 席',  '6-12 岁'),
  @('10-15','周四','19:30','线上分享：星辰与迁徙','腾讯会议','导航机制与城市光污染的影响',         '已满',     '线上'),
  @('10-17','周六','06:00','潮间带早潮','北门集合','涨潮前 1 小时看雁鸭群起飞',             '余 9 席',  '需雨鞋'),
  @('10-18','周日','14:00','数据整理日','站内工作间','把本周记录并入地方鸟类记录中心',       '余 2 席',  '站内'),
  @('10-22','周四','18:30','志愿者例会','站内工作间','排 11 月班次，复盘设备报修',           '限 12 人', '站内'),
  @('10-24','周六','07:00','棕背伯劳专题','北门集合','沿防护林走 1.2 km，找伯劳与隼',        '余 5 席',  '轻徒步'),
  @('10-25','周日','21:00','夜宿观鸟','北门集合','21:00-05:00，听夜行性鸟与潮声',          '余 3 席',  '18 岁以上'),
  @('10-31','周六','10:00','自然手作：落羽与标记环','北门服务台','用落羽做标记环与羽毛画',          '余 12 席', '亲子')
)
for ($i = 0; $i -lt 9; $i++) {
  $col = $i % 3
  $row = [Math]::Floor($i / 3)
  $x = 46 + ($col * 560)
  $y = 156 + ($row * 180)
  $acc = $TIDE
  if ($i -eq 0) { $acc = $SUN }
  Seg (ShadowBox $x $y 536 160 '#0F4A48' 14 '0 6 18 #00000044')
  Seg (Box $x $y 6 160 $acc 3)
  Seg (T ("c8-d" + $i) ($x + 24) ($y + 16) 176 40 $ev[$i][0] 30 $GULL 'LEFT' 'BOLD')
  Seg (T ("c8-w" + $i) ($x + 24) ($y + 58) 176 24 $ev[$i][1] 14 $TIDE 'LEFT' '')
  Seg (T ("c8-t" + $i) ($x + 24) ($y + 84) 176 28 $ev[$i][2] 18 $SUN 'LEFT' 'BOLD')
  Seg (Box ($x + 210) ($y + 22) 1 74 $LINE_D 0)
  Seg (T ("c8-n" + $i) ($x + 230) ($y + 18) 282 32 $ev[$i][3] 20 $GULL 'LEFT' 'BOLD')
  Seg (T ("c8-p" + $i) ($x + 230) ($y + 54) 282 24 $ev[$i][4] 14 $TIDE 'LEFT' '')
  Seg (T ("c8-s" + $i) ($x + 230) ($y + 82) 282 24 $ev[$i][5] 13 '#9FC0BA' 'LEFT' '')
  $c = Chip ("c8-c" + $i) ($x + 24) ($y + 124) $ev[$i][6] '#16514F' $GULL 13 12 999
  Seg $c[0]
  Seg (T ("c8-g" + $i) ($x + 230) ($y + 126) 282 24 $ev[$i][7] 13 '#9FC0BA' 'RIGHT' '')
}
Seg (FooterLine 'c8-f' 46 692 1656 'CENTER' '#9FC0BA' 13)
$l8 = Finish-Case '08' 1748 760 $DEEP

# ============================================================ case-09 年度数据年报卡 1080x1080
New-Case '09'
Seg (Mark 65 65 48 $TIDE $SUN $DEEP)
Seg (T 'c9-brand' 129 64 500 34 '候鸟湾观鸟站' 24 $GULL 'LEFT' 'BOLD')
Seg (T 'c9-brand2' 129 96 500 24 'ANNUAL REPORT' 13 $TIDE 'LEFT' '')
$w9 = [Math]::Ceiling((TW '2025-2026 年度' 15) + 30)
$c9 = Chip 'c9-chip' (1015 - $w9) 74 '2025-2026 年度' '#16514F' $GULL 15 15 999
Seg $c9[0]
Seg (RuleBand 65 142 950 $LINE_D $TIDE)
Seg (Eyebrow 'c9-eb' 65 168 950 'ANNUAL MIGRATION SEASON' '年度迁徙季小结 · 数据回传地方鸟类记录中心' 17 $TIDE '#9FC0BA')

Seg (T 'c9-big' 65 230 460 92 '4,180' 74 $SUN 'LEFT' 'BOLD')
Seg (T 'c9-big2' 65 326 460 30 '条鸟的记录' 20 $GULL 'LEFT' '')
Seg (T 'c9-big3' 65 358 460 26 '较上届 +18%' 15 $TIDE 'LEFT' '')
Seg (StatChip 'c9-s1' 600 236 190 '观测物种' '132' '种 · 新增 11' 15 $TIDE $GULL '#9FC0BA')
Seg (StatChip 'c9-s2' 825 236 190 '参与人数' '86' '人 · 志愿者 62' 15 $TIDE $GULL '#9FC0BA')
Seg (RuleBand 65 404 950 $LINE_D $TIDE)
Seg (SectionTitle 'c9-st' 65 430 950 '记录物种（按条数，前六）' 21 $SUN $GULL)
Seg (T 'c9-th1' 88 466 300 22 '物种' 12 $TIDE 'LEFT' '')
Seg (T 'c9-th2' 411 466 340 22 '学名' 12 $TIDE 'LEFT' '')
Seg (T 'c9-th3' 905 466 110 22 '记录数' 12 $TIDE 'RIGHT' '')
$top = @(
  @('红嘴鸥',   'Chroicocephalus ridibundus',  '642'),
  @('斑嘴鸭',   'Anas zonorhyncha',            '517'),
  @('绿头鸭',   'Anas platyrhynchos',          '448'),
  @('黑水鸡',   'Gallinula chloropus',         '386'),
  @('苍鹭',     'Ardea cinerea',               '214'),
  @('白鹭',     'Egretta garzetta',            '197')
)
for ($i = 0; $i -lt 6; $i++) {
  $y = 494 + ($i * 44)
  if (($i % 2) -eq 1) { Seg (Box 65 ($y - 4) 950 42 '#FFFFFF0A' 4) }
  Seg (SpeciesRow ("c9-r" + $i) 65 $y 950 $top[$i][0] $top[$i][1] $top[$i][2] $TIDE $GULL '#8FA9A5' $SUN 17 42)
}
Seg (RuleBand 65 776 950 $LINE_D $TIDE)
Seg (SectionTitle 'c9-st2' 65 802 950 '这一年' 21 $SUN $GULL)
Seg (DialArc 65 848 134 0.78 $TIDE '#16514F' 20 100)
Seg (T 'c9-dv' 65 884 134 44 '78%' 34 $SUN 'CENTER' 'BOLD')
Seg (T 'c9-dl' 65 932 134 20 '岗位填补率' 12 $TIDE 'CENTER' '')
Seg (T 'c9-h1' 240 852 775 26 '协助地方记录中心完成 4 次同步调查' 16 $GULL 'LEFT' '')
Seg (T 'c9-h2' 240 886 775 26 '12 台望远镜全年出借 1,043 次' 16 $GULL 'LEFT' '')
Seg (T 'c9-h3' 240 920 775 26 '零伤害事件；3 次设备报修当日修复' 16 $GULL 'LEFT' '')
Seg (T 'c9-h4' 240 954 775 26 '新认养 341 人，每月约 1.7 万元' 16 $GULL 'LEFT' '')
Seg (FooterLine 'c9-f' 65 992 950 'CENTER' '#9FC0BA' 12)
$l9 = Finish-Case '09' 1080 1080 $DEEP

# ============================================================ case-10 认养滩涂捐赠页 1080x1526
New-Case '10'
Seg (Box 0 0 1080 10 $DEEP 0)
Seg (Box 0 10 1080 4 $SUN 0)
Seg (Mark 65 52 48 $DEEP $SUN $PAPER)
Seg (T 'c10-brand' 129 52 520 34 '候鸟湾观鸟站' 23 $DEEP 'LEFT' 'BOLD')
Seg (T 'c10-brand2' 129 84 520 24 'MIGRANT BAY BIRD OBSERVATORY' 12 '#4A6B67' 'LEFT' '')
$wa = [Math]::Ceiling((TW '月捐 · 可随时停' 15) + 30)
$ca = Chip 'c10-chip' (1015 - $wa) 60 '月捐 · 可随时停' $DEEP $GULL 15 15 999
Seg $ca[0]
Seg (RuleBand 65 136 950 $LINE_L '#0B3B3A')
Seg (Eyebrow 'c10-eb' 65 164 950 'ADOPT A MUDFLAT' '认养滩涂 · 季度账目公示' 18 $DEEP '#4A6B67')
Seg (T 'c10-t1' 65 234 950 64 '你的 30 元，' 46 $DEEP 'LEFT' 'BOLD')
Seg (T 'c10-t2' 65 296 950 64 '够半亩滩涂吃一个月' 46 $DEEP 'LEFT' 'BOLD')
Seg (Box 65 368 200 6 $SUN 3)
Seg (TLines 'c10-desc' 65 404 950 17 @(
  '候鸟湾的滩涂每月要清理一次互花米草，一台潮位计每季度校准一次。',
  '认养金全额用于这两件事，账目每季度在公众号公示。'
) 30 '#4A6B67')

$tier = @(
  @('30',  '护滩人',   '214 人', $SUN,   '推荐', @('每月清理 0.5 亩互花米草', '季度潮位计校准 1 次', '电子认养牌 + 季度账目')),
  @('68',  '潮汐伙伴', '96 人',  '#0B3B3A', '',    @('每月清理 1.2 亩 + 步道补漆', '认养一段 30 m 栈道名牌', '季度账目 + 年度开放日')),
  @('128', '守望者',   '31 人',  '#0B3B3A', '',    @('每月清理 2.5 亩与全年巡护', '带 4 人参加一次同步调查', '姓名刻在北门守望牌'))
)
$eq = @('约 3 杯咖啡', '约 7 杯咖啡', '约 13 杯咖啡')
for ($i = 0; $i -lt 3; $i++) {
  $y = 480 + ($i * 222)
  Seg (ShadowBox 65 $y 950 200 '#FFFFFF' 16 '0 6 20 #0B3B3A1F')
  Seg (Box 65 $y 8 200 $tier[$i][3] 4)
  Seg (T ("c10-p" + $i) 100 ($y + 34) 300 70 ('¥' + $tier[$i][0]) 52 $DEEP 'LEFT' 'BOLD')
  Seg (T ("c10-pu" + $i) 100 ($y + 108) 300 24 '/ 每月' 15 '#4A6B67' 'LEFT' '')
  Seg (T ("c10-tn" + $i) 100 ($y + 140) 300 32 $tier[$i][1] 22 $tier[$i][3] 'LEFT' 'BOLD')
  Seg (Box 385 ($y + 30) 1 98 '#0B3B3A26' 0)
  Seg (TLines ("c10-b" + $i) 430 ($y + 30) 555 15 $tier[$i][5] 26 '#4A6B67')
  Seg (Box 385 ($y + 128) 600 1 '#0B3B3A33' 0)
  Seg (T ("c10-c" + $i) 430 ($y + 146) 260 26 ('已有 ' + $tier[$i][2] + ' 认养') 15 $DEEP 'LEFT' '')
  if ($i -eq 0) {
    $cw = [Math]::Ceiling((TW '推荐' 13) + 26)
    $cc = Chip 'c10-rec' (985 - $cw) ($y + 144) '推荐' $SUN '#FFFFFF' 13 13 999
    Seg $cc[0]
  } else {
    Seg (T ("c10-e" + $i) 700 ($y + 146) 285 26 $eq[$i] 14 '#4A6B67' 'RIGHT' '')
  }
}
Seg (ShadowBox 65 1174 950 100 $SUN 14 '0 8 24 #0B3B3A33')
Seg (T 'c10-cta' 105 1200 870 52 '扫码认养 · 首月可随时取消' 36 '#FFFFFF' 'CENTER' 'BOLD')
Seg (TLines 'c10-note' 65 1314 950 15 @(
  '· 认养金不用于人员开支，协调员薪资由政府购买服务覆盖',
  '· 每季度首周公示收支明细与滩涂清理进度照片',
  '· 想换档或停止，公众号回复「改档」即可'
) 28 '#4A6B67')
Seg (RuleBand 65 1420 950 $LINE_L '#0B3B3A')
Seg (FooterLine 'c10-f' 65 1444 950 'CENTER' '#4A6B67' 13)
$l10 = Finish-Case '10' 1080 1526 $PAPER

# ---- report ----
"problems = " + $script:PROBLEMS.Count
foreach ($p in $script:PROBLEMS) { "  " + $p }
"lens: c06=$l6 c07=$l7 c08=$l8 c09=$l9 c10=$l10"
