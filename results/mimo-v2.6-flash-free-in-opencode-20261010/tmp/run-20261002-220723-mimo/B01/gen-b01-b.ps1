# gen-b01-b.ps1 -- B01 showcase cases 06..07
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib-b01.ps1')

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

# dotted polyline helper -- the DSL has no line element, so any diagonal is dots
function DotLine([double]$x1,[double]$y1,[double]$x2,[double]$y2,[double]$d,[string]$c,[double]$step) {
    $out = ''
    $dx = $x2 - $x1; $dy = $y2 - $y1
    $len = [Math]::Sqrt($dx * $dx + $dy * $dy)
    if ($len -le 0) { return $out }
    $ux = $dx / $len; $uy = $dy / $len
    $t = 0.0
    while ($t -le $len) {
        $out += Box ($x1 + $ux * $t - $d / 2.0) ($y1 + $uy * $t - $d / 2.0) $d $d $c ([int][Math]::Round($d / 2.0))
        $t += $step
    }
    return $out
}

# =====================================================================
# case-06  锂电 PACK 装配工艺指导  1600x1000  产线工位看板
# =====================================================================
New-Case '06'
$W = 1600; $H = 1000; $BG = '#0E1014'
$YEL = '#FFC107'; $PAN = '#171A1F'; $CARD = '#1B1F26'; $BDR = '#2A2F38'
$TXT = '#E8ECF2'; $MUT = '#8B96A6'; $GRN = '#22C55E'; $ORG = '#FF9C3F'

Seg (Box 0 0 $W $H $BG 0)
Seg (Box 0 0 $W 6 $YEL 0)
Seg (Panel 40 26 1520 88 $PAN 12 $BDR)
Seg (CircleGrad 64 48 44 '#FFC107,#FF8A00' 'SWEEP' '' '' $null); $script:SEG[$script:SEG.Count-1] += '/></Positioned>'
Seg (T '06' 64 58 44 30 '启' 22 '#101215' 'CENTER' 'BOLD')
Seg (T '06' 124 42 720 36 '启源新能源 QY ENERGY · P2 车间' 26 $TXT 'LEFT' 'BOLD')
Seg (T '06' 124 82 720 28 'PACK 模组装配工艺指导书 · 工位 P2-07 · 作业前请通读全部步骤' 17 $MUT 'LEFT' '')
Seg (T '06' 1090 42 446 32 '文件 QY-P2-WI-0413' 21 $YEL 'RIGHT' 'BOLD')
Seg (T '06' 1090 82 446 26 '版本 C · 2026-10-09 生效 · 受控文件' 16 $MUT 'RIGHT' '')

# ---- left: process steps ----
Seg (Panel 40 134 940 816 $PAN 14 $BDR)
Seg (T '06' 60 150 500 30 '工序步骤 · WORK STEPS' 19 $TXT 'LEFT' 'BOLD')
Seg (T '06' 640 152 320 28 '共 5 步 · 单件节拍 96 s' 16 $MUT 'RIGHT' '')

$steps = @(
    @('01', '模组入壳', 'LOADING',      '按极性箭头推入 12 只模芯，确认 4 个定位销全部到位', '12',      '模芯数'),
    @('02', '螺栓预紧', 'PRE-TIGHTEN',  '四角 M6 螺栓手动预紧至贴合贴合面，禁止使用风动工具', '3.0',     'N·m 预紧'),
    @('03', '电动拧紧', 'FINAL TORQUE', '沿 1 到 5 对角顺序一次终拧到位，曲线超差即声光报警', '6.5±0.3', 'N·m 终拧'),
    @('04', '绝缘检测', 'INSULATION',   '施加 500 V 直流，稳压 5 s 后读取壳体与模芯绝缘电阻', '≥20',     'MΩ 绝缘'),
    @('05', '终检贴标', 'LABELING',     '扫码绑定模组 SN，打印追溯标签并粘贴于壳体右上角',    '100%',    '扫码绑定')
)
for ($i = 0; $i -lt 5; $i++) {
    $y = 186 + $i * 116
    Seg (Panel 60 $y 900 104 $CARD 10 $BDR)
    Seg (Panel 78 ($y + 20) 64 64 $YEL 14 $null)
    Seg (T '06' 78 ($y + 34) 64 40 $steps[$i][0] 28 '#101215' 'CENTER' 'BOLD')
    Seg (T '06' 162 ($y + 16) 250 32 $steps[$i][1] 21 $TXT 'LEFT' 'BOLD')
    Seg (T '06' 162 ($y + 54) 250 26 $steps[$i][2] 15 $MUT 'LEFT' '')
    $r = TPara '06' 430 ($y + 30) 360 $steps[$i][3] 16 30 '#B9C2CE' ''
    Seg $r[0]
    Seg (T '06' 810 ($y + 26) 130 34 $steps[$i][4] 24 $GRN 'RIGHT' 'BOLD')
    Seg (T '06' 810 ($y + 64) 130 22 $steps[$i][5] 14 $MUT 'RIGHT' '')
}

# ---- left bottom: poka-yoke ----
Seg (Panel 60 776 900 158 $CARD 10 $BDR)
Seg (T '06' 84 794 400 30 '防错要点 · POKA-YOKE' 19 $TXT 'LEFT' 'BOLD')
$poka = @(
    '极性箭头必须朝上，装反将触发线束短路保护',
    '终拧后禁止二次复拧，复拧须填异常单并更换螺栓',
    '拧紧枪每 2 小时点检一次，超差立即停线呼叫工艺'
)
for ($i = 0; $i -lt 3; $i++) {
    $y = 836 + $i * 32
    Seg (Panel 84 $y 20 20 $ORG 5 $null)
    Seg (T '06' 84 ($y - 3) 20 26 '!' 15 '#101215' 'CENTER' 'BOLD')
    Seg (T '06' 118 ($y - 2) 820 26 $poka[$i] 16 '#C9D3E0' 'LEFT' '')
}

# ---- right: torque spec ----
Seg (Panel 1000 134 560 250 $PAN 14 $BDR)
Seg (T '06' 1024 152 400 30 '关键扭矩 · TORQUE SPEC' 19 $TXT 'LEFT' 'BOLD')
Seg (T '06' 1024 190 512 62 '6.5 ± 0.3 N·m' 48 $YEL 'LEFT' 'BOLD')
Seg (Panel 1024 264 512 26 '#2A1B1B' 6 $null)
Seg (Box 1024 264 179 26 '#4A1E1E' 6)
Seg (Box 1357 264 179 26 '#4A1E1E' 6)
Seg (Box 1203 264 154 26 '#1E4A28' 0)
Seg (Box 1277 256 6 42 '#FFFFFF' 3)
Seg (T '06' 1024 296 100 24 '5.5' 14 $MUT 'LEFT' '')
Seg (T '06' 1200 296 160 24 '合格带 6.2 – 6.8' 14 $GRN 'CENTER' 'BOLD')
Seg (T '06' 1436 296 100 24 '7.5' 14 $MUT 'RIGHT' '')
Seg (T '06' 1024 340 512 26 '工具 ET-65 电动扭矩枪 · 校准有效期 2026-12-31' 15 $MUT 'LEFT' '')

# ---- right: tightening pattern ----
Seg (Panel 1000 404 560 310 $PAN 14 $BDR)
Seg (T '06' 1024 422 460 30 '拧紧顺序 · TIGHTENING PATTERN' 19 $TXT 'LEFT' 'BOLD')
Seg (Panel 1054 460 460 210 '#1B2028' 10 '#3A424E')
$bolts = @(@(1084,490), @(1430,610), @(1430,490), @(1084,610), @(1257,550))
for ($i = 0; $i -lt 4; $i++) {
    $x1 = $bolts[$i][0] + 27; $y1 = $bolts[$i][1] + 27
    $x2 = $bolts[$i+1][0] + 27; $y2 = $bolts[$i+1][1] + 27
    Seg (DotLine $x1 $y1 $x2 $y2 6 $ORG 16)
}
for ($i = 0; $i -lt 5; $i++) {
    Seg ('<Positioned left="' + (Fmt $bolts[$i][0]) + '" top="' + (Fmt $bolts[$i][1]) + '" width="54" height="54"><Container width="54" height="54" shape="CIRCLE" border="3 SOLID ' + $ORG + '" color="#2A3038"/></Positioned>')
    Seg (T '06' $bolts[$i][0] ($bolts[$i][1] + 12) 54 32 ($i + 1).ToString() 24 '#FFD9A0' 'CENTER' 'BOLD')
}
Seg (T '06' 1024 682 512 26 '对角交替 · 一次到位 · 禁止复拧' 15 $ORG 'CENTER' 'BOLD')

# ---- right: quality gate ----
Seg (Panel 1000 734 560 216 $PAN 14 $BDR)
Seg (T '06' 1024 752 460 30 '质量门 · QUALITY GATE' 19 $TXT 'LEFT' 'BOLD')
$gate = @(
    @('拧紧曲线全部落在公差带内', 'PASS'),
    @('壳体与模芯绝缘电阻', '24.6 MΩ'),
    @('外观无划伤、无异物残留', 'PASS'),
    @('模组 SN 已成功绑定', 'SN 已绑定')
)
for ($i = 0; $i -lt 4; $i++) {
    $y = 796 + $i * 40
    Seg (Panel 1024 ($y + 3) 22 22 '#1E3A2F' 5 '#22C55E')
    Seg (T '06' 1024 $y 22 26 '✓' 15 $GRN 'CENTER' 'BOLD')
    Seg (T '06' 1058 $y 340 28 $gate[$i][0] 17 '#C9D3E0' 'LEFT' '')
    Seg (T '06' 1394 $y 142 28 $gate[$i][1] 15 $GRN 'RIGHT' 'BOLD')
}

Seg (Box 40 966 1520 1 '#232A34' 0)
Seg (T '06' 40 974 1000 24 '工位 P2-07 · 作业指导书仅限内部使用 · 异常停线并呼叫工艺员' 15 '#6E7887' 'LEFT' '')
Seg (T '06' 1100 974 460 24 '演示数据 DEMO' 15 $YEL 'RIGHT' 'BOLD')
$L06 = Finish-Case '06' $W $H $BG

# =====================================================================
# case-07  围棋棋谱解说图  1200x1200  教学讲义
# =====================================================================
New-Case '07'
$W = 1200; $H = 1200; $BG = '#14100C'
$WOOD1 = '#E3C48E'; $WOOD2 = '#CBA163'; $GRID = '#7A5A2E'
$PAN7 = '#1F1913'; $BDR7 = '#33291F'; $TXT7 = '#F2E8DA'; $MUT7 = '#A08C74'
$RED = '#D64545'; $BLU = '#5AA9FF'; $GRN7 = '#4ADE9B'

Seg (Box 0 0 $W $H $BG 0)
Seg (Grad 0 0 $W 1200 '#1A140E,#14100C,#1A140E' 'LINEAR' 'TOP_LEFT' 'BOTTOM_RIGHT' 0)
Seg (Box 0 0 $W 5 $GRN7 0)

# header
Seg (Panel 40 30 1120 92 $PAN7 12 $BDR7)
Seg (CircleGrad 66 54 44 '#F5E6CC,#C9A96A' 'SWEEP' '' '' $null); $script:SEG[$script:SEG.Count-1] += '/></Positioned>'
Seg (T '07' 66 64 44 30 '弈' 22 '#241A10' 'CENTER' 'BOLD')
Seg (T '07' 126 46 620 36 '弈秋书院 YIQIU ACADEMY' 26 $TXT7 'LEFT' 'BOLD')
Seg (T '07' 126 86 620 26 '第 19 届新人王战 决定局 · 棋谱解说（前 20 手）' 17 $MUT7 'LEFT' '')
Seg (T '07' 760 46 376 34 '黑 沈砚 七段  vs  白 顾青 五段' 21 '#E8D5B0' 'RIGHT' 'BOLD')
Seg (T '07' 760 86 376 26 '2026-10-09 · 分先 · 贴 6.5 目' 16 $MUT7 'RIGHT' '')

# ---- board ----
Seg (GradP 40 146 660 660 ($WOOD1 + ',' + $WOOD2) 'TOP_LEFT' 'BOTTOM_RIGHT' 18 '#8A6636')
$gx0 = 72.0; $gy0 = 178.0; $span = 596.0; $gap = $span / 18.0
for ($k = 0; $k -lt 19; $k++) {
    $p = [Math]::Round($gap * $k, 2)
    Seg (VLine ($gx0 + $p) $gy0 $span 2 $GRID)
    Seg (HLine $gx0 ($gy0 + $p) $span 2 $GRID)
}
foreach ($sx in @(3, 9, 15)) { foreach ($sy in @(3, 9, 15)) {
    Seg (Circle ($gx0 + $gap * $sx - 6) ($gy0 + $gap * $sy - 6) 12 $GRID $null)
} }
# moves: @(colIdx, rowIdxFromTop, colour)
$moves = @(
    @(3,3,'B'), @(15,15,'W'), @(15,3,'B'), @(3,15,'W'), @(2,5,'B'),
    @(4,4,'W'), @(4,6,'B'), @(2,4,'W'), @(16,12,'B'), @(14,14,'W'),
    @(14,12,'B'), @(16,14,'W'), @(9,9,'B'), @(6,9,'W'), @(6,11,'B'),
    @(12,9,'W'), @(12,7,'B'), @(9,14,'W'), @(3,9,'B'), @(15,6,'W')
)
$letters = 'ABCDEFGHJKLMNOPQRST'
for ($i = 0; $i -lt 20; $i++) {
    $cxi = [int]$moves[$i][0]; $cyi = [int]$moves[$i][1]; $col = [string]$moves[$i][2]
    $cx = $gx0 + $gap * $cxi; $cy = $gy0 + $gap * $cyi
    $sx = $cx - 15.0; $sy = $cy - 15.0
    if ($col -eq 'B') {
        Seg (CircleGrad $sx $sy 30 '#4A4A4A,#050505' 'LINEAR' 'TOP_LEFT' 'BOTTOM_RIGHT' $null); $script:SEG[$script:SEG.Count-1] += '/></Positioned>'
        $fg = '#FFFFFF'
    } else {
        Seg (CircleGrad $sx $sy 30 '#FFFFFF,#D2D2D2' 'LINEAR' 'TOP_LEFT' 'BOTTOM_RIGHT' $null); $script:SEG[$script:SEG.Count-1] += '/></Positioned>'
        $fg = '#141414'
    }
    $num = ($i + 1).ToString()
    $fs = 16
    if ($num.Length -gt 1) { $fs = 14 }
    $th = [Math]::Round($fs * 1.3, 1)
    Seg (Txt $sx ($sy + (30 - $th) / 2.0) 30 $th $num $fs $fg 'CENTER' 'BOLD')
}
# highlight the last move
$lcx = $gx0 + $gap * [int]$moves[19][0]; $lcy = $gy0 + $gap * [int]$moves[19][1]
Seg ('<Positioned left="' + (Fmt ($lcx - 20)) + '" top="' + (Fmt ($lcy - 20)) + '" width="40" height="40"><Container width="40" height="40" shape="CIRCLE" border="3 SOLID ' + $RED + '" color="#00000000"/></Positioned>')

# ---- move index ----
Seg (Panel 40 824 660 314 $PAN7 12 $BDR7)
Seg (T '07' 64 844 400 30 '手数索引 · MOVE LIST' 19 $TXT7 'LEFT' 'BOLD')
Seg (T '07' 400 846 276 26 '黑先 · 序盘 20 手' 15 $MUT7 'RIGHT' '')
for ($i = 0; $i -lt 20; $i++) {
    $colI = $i % 5; $rowI = [Math]::Floor($i / 5.0)
    $cx = 64 + $colI * 124; $cy = 892 + $rowI * 60
    Seg (Panel $cx $cy 114 48 '#271F17' 8 '#33291F')
    Seg (T '07' ($cx + 8) ($cy + 9) 34 30 ($i + 1).ToString() 18 '#E8D5B0' 'LEFT' 'BOLD')
    $cc = '#101010'; $ring = '#5A5A5A'
    if ($moves[$i][2] -eq 'B') { $cc = '#141414'; $ring = '#4A4A4A' } else { $cc = '#FFFFFF'; $ring = '#D8D8D8' }
    Seg ('<Positioned left="' + (Fmt ($cx + 44)) + '" top="' + (Fmt ($cy + 18)) + '" width="14" height="14"><Container width="14" height="14" shape="CIRCLE" border="1 SOLID ' + $ring + '" color="' + $cc + '"/></Positioned>')
    $coord = $letters[[int]$moves[$i][0]].ToString() + (19 - [int]$moves[$i][1]).ToString()
    Seg (T '07' ($cx + 64) ($cy + 11) 44 28 $coord 16 '#C6B393' 'LEFT' 'BOLD')
}

# ---- commentary ----
Seg (Panel 724 146 436 660 $PAN7 12 $BDR7)
Seg (T '07' 748 166 380 30 '解说 · COMMENTARY' 19 $TXT7 'LEFT' 'BOLD')
$notes = @(
    @('序盘构思', '#5AA9FF', @(
        '黑先占 D16、Q16 上边两角星位，',
        '白以 Q4、D4 下边两角对应；',
        '第 5 手黑沿左边拆出抢占大场，南北分治。')),
    @('定式选择', '#4ADE9B', @(
        '左上白 6 挂、黑 7 夹，白 8 沿边拆开；',
        '右下黑 9 先挂，白 10 应、黑 11 拆、',
        '白 12 定形。两处两分，白稍厚。')),
    @('关键手',   '#FF9C3F', @(
        '第 13 手占据天元为全局要点：',
        '既限制白中腹扩张，又与左边 19 位拆边呼应，',
        '白随即于 14 位应。'))
)
for ($i = 0; $i -lt 3; $i++) {
    $y = 214 + $i * 146
    Seg (Box 748 $y 4 28 $notes[$i][1] 2)
    Seg (T '07' 766 $y 364 30 $notes[$i][0] 19 $TXT7 'LEFT' 'BOLD')
    Seg (TLines '07' 766 ($y + 40) 364 16 $notes[$i][2] 27 '#CBBBA4' '')
}
Seg (Box 748 646 388 1 '#33291F' 0)
Seg (T '07' 748 660 388 26 '本图为前 20 手序盘讲解，非全局棋谱' 15 $MUT7 'LEFT' '')
Seg (T '07' 748 694 388 26 '讲解：顾岚 初段 · 弈秋书院周三晚班' 15 $MUT7 'LEFT' '')
Seg (T '07' 748 748 388 30 '后续手数见讲义第 2 页' 16 $GRN7 'LEFT' 'BOLD')

# ---- result ----
Seg (Panel 724 824 436 314 $PAN7 12 $BDR7)
Seg (T '07' 748 844 380 30 '形势判断 · RESULT' 19 $TXT7 'LEFT' 'BOLD')
Seg (T '07' 748 886 388 56 '白胜 1.5 目' 40 '#F5E6CC' 'LEFT' 'BOLD')
Seg (Panel 748 956 388 26 '#2B231A' 13 $null)
Seg (Box 748 956 201 26 '#3A3A3A' 13)
Seg (Box 949 956 187 26 '#EDEDED' 13)
Seg (T '07' 748 992 190 26 '黑 地 71 目' 16 '#C6B393' 'LEFT' '')
Seg (T '07' 946 992 190 26 '白 地 66 目' 16 '#F0E6D6' 'RIGHT' '')
Seg (Box 748 1028 388 1 '#33291F' 0)
Seg (T '07' 748 1042 388 26 '全局 208 手 · 贴目 6.5 目' 16 $MUT7 'LEFT' '')
Seg (T '07' 748 1076 388 26 '数子：白 72.5 · 黑 71，白胜 1.5 目' 16 $GRN7 'LEFT' 'BOLD')

Seg (T '07' 40 1152 700 26 '弈秋书院 · 围棋教室讲义 · 演示数据 DEMO' 15 '#7A6A55' 'LEFT' '')
Seg (T '07' 760 1152 400 26 '第 19 届新人王战 决定局' 15 '#7A6A55' 'RIGHT' '')
$L07 = Finish-Case '07' $W $H $BG

# NOTE (post-closure correction): RingProg below was B01 case-08's original ring builder.
# It was replaced on 2026-10-06 after an objective pixel measurement (see lib-b01.ps1 DialArc)
# proved the SWEEP gradient ignores gradientStops/gradientStartAngle: the delivered render
# showed a 50.14% arc starting at 90 deg (3 o'clock), not the claimed 75% arc from 12 o'clock.
# RingProg is kept for the record; case-08 now uses DialArc.
function RingProg([double]$l,[double]$t,[double]$d,[double]$frac,[string]$on,[string]$off,[string]$hole,[double]$thick) {
    $cols = $on + ',' + $on + ',' + $off + ',' + $off
    $st = '0,' + (Fmt $frac) + ',' + (Fmt $frac) + ',1'
    $o = '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $d) + '" height="' + (Fmt $d) +
         '"><Container width="' + (Fmt $d) + '" height="' + (Fmt $d) + '" shape="CIRCLE" gradientType="SWEEP" gradientColors="' + $cols +
         '" gradientStops="' + $st + '" gradientStartAngle="-1.5707963" gradientEndAngle="4.7123890"/></Positioned>'
    $o += Circle ($l + $thick) ($t + $thick) ($d - 2 * $thick) $hole $null
    return $o
}

# =====================================================================
# case-08  宠物疫苗接种提醒  1080x1080  诊后推送卡片
# =====================================================================
New-Case '08'
$W = 1080; $H = 1080; $BG = '#FFF7EE'
$OR8 = '#FF8A5B'; $INK8 = '#3E2A1E'; $BR8 = '#6B3F2A'; $MU8 = '#A8846A'; $TN8 = '#E0662E'; $GRN8 = '#17A45B'

Seg (Box 0 0 $W $H $BG 0)
Seg (Circle 840 -110 360 '#FFE7D4' $null)
Seg (Circle -100 860 300 '#FFF1E4' $null)

# header
Seg (Circle 56 56 54 $OR8 $null)
Seg (T '08' 56 68 54 36 '毛' 24 '#FFFFFF' 'CENTER' 'BOLD')
Seg (T '08' 130 54 520 34 '毛星球宠物医院 PAWPLANET' 26 $BR8 'LEFT' 'BOLD')
Seg (T '08' 130 94 520 26 '滨江店 · 接种完成回执（电子卡）' 17 $MU8 'LEFT' '')
Seg (T '08' 700 56 324 30 '2026-10-09' 20 $BR8 'RIGHT' 'BOLD')
Seg (T '08' 700 94 324 26 '卡号 P-20261009-0372' 15 $MU8 'RIGHT' '')
Seg (Box 56 136 968 2 '#F0E0D2' 0)

Seg (T '08' 56 168 700 64 '疫苗接种提醒' 48 $INK8 'LEFT' 'BOLD')
Seg (T '08' 56 240 968 32 '布丁 · 2 岁 3 个月 · 比雄犬 · 体重 5.4 kg' 22 '#8A6A52' 'LEFT' '')

# ---- progress ----
Seg (ShadowBox 56 300 460 460 '#FFFFFF' 28 '0 8 28 #C9A88A33')
# deterministic 75% ring: white hole first, then OFF/ON tick segments from 12 o'clock
Seg (Circle 188 392 196 '#FFFFFF' $null)
Seg (DialArc 156 360 260 0.75 $OR8 '#F6E4D6' 32 100)
Seg (T '08' 188 436 196 74 '3/4' 54 $INK8 'CENTER' 'BOLD')
Seg (T '08' 188 516 196 26 '免疫程序完成' 16 $MU8 'CENTER' '')

$chips = @(@('首免 ✓', 1), @('二免 ✓', 1), @('三免 ✓', 1), @('加强 待', 0))
for ($i = 0; $i -lt 4; $i++) {
    $x = 74 + $i * 108
    if ($chips[$i][1] -eq 1) { $cbg = '#DFF5E7'; $cfg = $GRN8 } else { $cbg = '#F2ECE6'; $cfg = $MU8 }
    Seg (Panel $x 646 100 40 $cbg 20 $null)
    Seg (T '08' $x 657 100 26 $chips[$i][0] 14 $cfg 'CENTER' 'BOLD')
}
Seg (T '08' 74 706 424 26 '共 4 针 · 已完成 3 针 · 下一针 11 月 06 日' 15 $MU8 'CENTER' '')

# ---- today's shots ----
Seg (ShadowBox 544 300 480 460 '#FFFFFF' 28 '0 8 28 #C9A88A33')
Seg (T '08' 572 324 420 32 '本次接种 · TODAY' 22 $BR8 'LEFT' 'BOLD')
$shots = @(
    @('狂犬病疫苗', 'Rabies · 批号 RB-2610', '左后颈皮下', '#FFF1E7'),
    @('犬四联疫苗', 'DHPP · 批号 DP-2609', '右后颈皮下', '#EAF6FF')
)
for ($i = 0; $i -lt 2; $i++) {
    $y = 372 + $i * 116
    Seg (Panel 572 $y 424 100 $shots[$i][3] 18 $null)
    Seg (T '08' 596 ($y + 16) 260 32 $shots[$i][0] 22 $INK8 'LEFT' 'BOLD')
    Seg (T '08' 596 ($y + 54) 260 26 $shots[$i][1] 15 $MU8 'LEFT' '')
    Seg (T '08' 856 ($y + 16) 120 26 $shots[$i][2] 16 '#5B463A' 'RIGHT' 'BOLD')
    Seg (T '08' 856 ($y + 52) 120 26 '已接种' 15 $GRN8 'RIGHT' 'BOLD')
}
Seg (Box 572 616 424 1 '#F0E4D8' 0)
Seg (T '08' 572 632 424 28 '下次预约' 18 $INK8 'LEFT' 'BOLD')
Seg (T '08' 572 664 424 56 '2026-11-06' 42 $TN8 'LEFT' 'BOLD')
Seg (T '08' 572 722 424 26 '周四 · 四联第 2 针 + 体况检查' 16 $MU8 'LEFT' '')

# ---- care notes ----
Seg (ShadowBox 56 784 968 240 '#FFFFFF' 28 '0 8 28 #C9A88A33')
Seg (T '08' 84 808 500 32 '术后注意事项 · CARE' 22 $BR8 'LEFT' 'BOLD')
Seg (T '08' 600 812 396 26 '打印后请随回执一并保存' 15 $MU8 'RIGHT' '')
$care = @(
    @('观察 30 分钟', '离院前须留观，确认无过敏反应'),
    @('当天不洗澡', '接种后 48 h 内避免洗澡与剧烈运动'),
    @('留意食欲', '出现呕吐、面部肿胀立即联系医院'),
    @('按时复诊', '四联第 2 针不可延迟超过 7 天')
)
for ($i = 0; $i -lt 4; $i++) {
    $cx = 84 + ($i % 2) * 476
    $cy = 856 + [Math]::Floor($i / 2.0) * 88
    Seg (Panel $cx $cy 36 36 '#FFE3D2' 12 $null)
    Seg (T '08' $cx ($cy + 5) 36 26 ($i + 1).ToString() 17 $TN8 'CENTER' 'BOLD')
    Seg (T '08' ($cx + 50) ($cy - 2) 400 30 $care[$i][0] 17 $INK8 'LEFT' 'BOLD')
    Seg (T '08' ($cx + 50) ($cy + 30) 400 26 $care[$i][1] 15 $MU8 'LEFT' '')
}
Seg (T '08' 56 1044 800 26 '林漾 医师主诊 · 0571-8832 6677 · 毛星球宠物医院滨江店' 15 '#C0A48E' 'LEFT' '')
Seg (T '08' 870 1044 154 26 '演示数据 DEMO' 15 '#C0A48E' 'RIGHT' 'BOLD')
$L08 = Finish-Case '08' $W $H $BG

# =====================================================================
# case-09  潮汐与海泳安全牌  1080x1350  浴场立牌
# =====================================================================
New-Case '09'
$W = 1080; $H = 1350; $BG = '#032B3A'
$PAN9 = '#053A4C'; $ACC9 = '#3FE0C0'; $TXT9 = '#EAF7F8'; $MUT9 = '#7FB6C2'
$WAN = '#FFC857'; $DAN = '#FF6B6B'

Seg (Box 0 0 $W $H $BG 0)
Seg (Grad 0 0 $W 200 '#0A6E86,#04495E' 'LINEAR' 'TOP_LEFT' 'TOP_RIGHT' 0)
Seg (Box 0 0 $W 8 $ACC9 0)

Seg (Circle 60 56 54 $ACC9 $null)
Seg (T '09' 60 68 54 36 '蓝' 24 '#02303E' 'CENTER' 'BOLD')
Seg (T '09' 134 54 520 34 '蓝湾海滨浴场 BLUEBAY' 26 '#FFFFFF' 'LEFT' 'BOLD')
Seg (T '09' 134 94 560 28 '2026-10-09 · 周五 · 日出 06:34 / 日落 18:22' 17 '#CFEAEF' 'LEFT' '')
Seg (T '09' 60 132 560 46 '今日潮汐与安全' 36 '#FFFFFF' 'LEFT' 'BOLD')

Seg (Panel 744 44 276 110 '#0B4B5C' 18 '#3FE0C0')
Seg (T '09' 764 58 236 42 '当前 · 可下水' 30 '#5FFFC8' 'LEFT' 'BOLD')
Seg (T '09' 764 104 236 26 '安全窗口 至 17:30' 16 '#9FD9E4' 'LEFT' '')
Seg (T '09' 764 130 236 24 '潮位 1.9 m · 涨潮中' 15 '#9FD9E4' 'LEFT' '')

# ---- tide chart ----
Seg (Panel 60 230 960 420 $PAN9 16 '#0A5568')
Seg (T '09' 88 252 520 32 '24 小时潮位曲线 · TIDE LEVEL' 22 $TXT9 'LEFT' 'BOLD')
Seg (T '09' 600 254 392 28 '单位：米 · 2026-10-09' 17 $MUT9 'RIGHT' '')

$PX0 = 140.0; $PX1 = 970.0; $PY0 = 330.0; $PY1 = 566.0; $VMAX = 4.5
function TideV([double]$tt) {
    $sg = @(@(0.0, 6.2, 1.0, 3.8), @(6.2, 12.4667, 3.8, 0.6), @(12.4667, 18.6833, 0.6, 3.6), @(18.6833, 24.0, 3.6, 1.1))
    foreach ($s in $sg) {
        if ($tt -ge $s[0] -and $tt -le $s[1]) {
            $u = ($tt - $s[0]) / ($s[1] - $s[0])
            $vm = ($s[2] + $s[3]) / 2.0
            $am = ($s[2] - $s[3]) / 2.0
            return $vm + $am * [Math]::Cos([Math]::PI * $u)
        }
    }
    return 1.1
}
function TY([double]$v) { return $script:PY1 - ($v / $script:VMAX) * ($script:PY1 - $script:PY0) }
function TX([double]$tt) { return $script:PX0 + ($tt / 24.0) * ($script:PX1 - $script:PX0) }

for ($v = 0; $v -le 4; $v++) {
    $gy = TY $v
    Seg (HLine 140 $gy 830 1 '#0A5568')
    Seg (T '09' 88 ($gy - 14) 44 26 $v.ToString() 14 $MUT9 'RIGHT' '')
}
for ($k = 0; $k -le 6; $k++) {
    $tt = [double]$k * 4.0
    $gx = TX $tt
    Seg (VLine $gx 330 236 1 '#0A5568')
    if ($k -eq 0) { Seg (T '09' $gx 574 90 26 '00:00' 14 $MUT9 'LEFT' '') }
    elseif ($k -eq 6) { Seg (T '09' ($gx - 90) 574 90 26 '24:00' 14 $MUT9 'RIGHT' '') }
    else { Seg (T '09' ($gx - 45) 574 90 26 ('{0:d2}:00' -f ($k * 4)) 14 $MUT9 'CENTER' '') }
}

# filled area + bright surface line (the DSL has no line element: dots make the curve)
$N = 96
$bw = ($PX1 - $PX0) / $N
for ($i = 0; $i -lt $N; $i++) {
    $tt = $i * 0.25
    $x = TX $tt
    $yv = TY (TideV $tt)
    Seg (Box $x $yv ($bw + 1.4) ($PY1 - $yv) '#0A6E86' 0)
}
for ($i = 0; $i -le $N; $i++) {
    $tt = $i * 0.25
    $x = TX $tt
    $yv = TY (TideV $tt)
    Seg (Circle ($x - 3) ($yv - 3) 6 '#5FFFE0' $null)
}

$marks = @(@(6.2, 3.8, '高潮 06:12 · 3.8 m'), @(12.4667, 0.6, '低潮 12:28 · 0.6 m'), @(18.6833, 3.6, '高潮 18:41 · 3.6 m'))
for ($i = 0; $i -lt 3; $i++) {
    $mx = TX $marks[$i][0]; $my = TY $marks[$i][1]
    Seg (Circle ($mx - 8) ($my - 8) 16 $WAN $null)
    Seg (Panel ($mx - 85) ($my - 46) 170 28 '#04222D' 8 '#0A5568')
    Seg (T '09' ($mx - 85) ($my - 43) 170 24 $marks[$i][2] 14 '#FFE0A3' 'CENTER' 'BOLD')
}
$nowX = TX 15.3333
$nowV = TideV 15.3333
$nowY = TY $nowV
Seg (VLine $nowX 330 236 2 $DAN)
Seg (Circle ($nowX - 8) ($nowY - 8) 16 $DAN $null)
Seg (Panel ($nowX - 62) 300 124 26 $DAN 7 $null)
Seg (T '09' ($nowX - 62) 302 124 24 '现在 15:20' 14 '#2A0A0A' 'CENTER' 'BOLD')

Seg (T '09' 88 610 884 28 '橙点为高/低潮位，红线为当前时刻；15:20 潮位 1.9 m，正在涨向 18:41 高潮' 15 '#9FD9E4' 'LEFT' '')

# ---- tide times ----
Seg (Panel 60 680 460 300 $PAN9 16 '#0A5568')
Seg (T '09' 88 704 400 30 '潮时表 · TIDE TIMES' 20 $TXT9 'LEFT' 'BOLD')
$rows9 = @(
    @('高潮', '06:12', '3.8 m', $ACC9),
    @('低潮', '12:28', '0.6 m', '#5AA9FF'),
    @('高潮', '18:41', '3.6 m', $ACC9),
    @('低潮', '00:40', '0.9 m · 次日', '#5AA9FF')
)
for ($i = 0; $i -lt 4; $i++) {
    $y = 746 + $i * 58
    if ($i -gt 0) { Seg (Box 88 ($y - 12) 404 1 '#0A5568' 0) }
    Seg (T '09' 88 $y 80 30 $rows9[$i][0] 17 $rows9[$i][3] 'LEFT' 'BOLD')
    Seg (T '09' 178 ($y - 4) 140 38 $rows9[$i][1] 26 '#FFFFFF' 'LEFT' 'BOLD')
    Seg (T '09' 330 $y 162 30 $rows9[$i][2] 17 $MUT9 'RIGHT' '')
}

# ---- sea conditions ----
Seg (Panel 560 680 460 300 $PAN9 16 '#0A5568')
Seg (T '09' 588 704 400 30 '海况 · SEA CONDITIONS' 20 $TXT9 'LEFT' 'BOLD')
$sea = @(
    @('浪高', '0.8 m'), @('水温', '22.4 ℃'),
    @('风向风力', '东北 4 级'), @('能见度', '良好'),
    @('水质', '一类 · 优'), @('紫外线', '中等')
)
for ($i = 0; $i -lt 6; $i++) {
    $cx = 588 + ($i % 2) * 208
    $cy = 750 + [Math]::Floor($i / 2.0) * 68
    Seg (T '09' $cx $cy 196 24 $sea[$i][0] 15 $MUT9 'LEFT' '')
    Seg (T '09' $cx ($cy + 24) 196 36 $sea[$i][1] 25 $TXT9 'LEFT' 'BOLD')
}

# ---- safety ----
Seg (Panel 60 1000 960 230 $PAN9 16 '#0A5568')
Seg (T '09' 88 1024 500 30 '安全提示 · SAFETY' 20 $TXT9 'LEFT' 'BOLD')
Seg (T '09' 640 1026 352 28 '救生员值班 08:00–18:30' 16 $MUT9 'RIGHT' '')
$safe = @(
    @('1', '只在救生员值班时段下水，红旗时段严禁入水', $WAN),
    @('2', '儿童与不擅泳者请佩戴浮具，勿越过浮标警戒线', $ACC9),
    @('3', '涨潮时离岸流较强，如被卷走请侧向游出并举手示意', $DAN)
)
for ($i = 0; $i -lt 3; $i++) {
    $y = 1070 + $i * 54
    Seg (Panel 88 $y 36 34 '#04222D' 10 $safe[$i][2])
    Seg (T '09' 88 ($y + 4) 36 26 $safe[$i][0] 17 $safe[$i][2] 'CENTER' 'BOLD')
    Seg (T '09' 140 ($y + 2) 840 30 $safe[$i][1] 18 $TXT9 'LEFT' '')
}

Seg (Panel 60 1246 960 64 '#063B4C' 16 '#0A5568')
Seg (T '09' 84 1262 640 30 '服务电话 0898-8866 1220 · 蓝湾海滨浴场管理处' 17 '#9FD9E4' 'LEFT' '')
Seg (T '09' 760 1262 236 30 '演示数据 DEMO' 17 $WAN 'RIGHT' 'BOLD')
$L09 = Finish-Case '09' $W $H $BG

# =====================================================================
# case-10  社区旧物集市导览横幅  1920x640  广场入口横屏
# =====================================================================
New-Case '10'
$W = 1920; $H = 640; $BG = '#FBF3E4'
$ORA = '#E86A3A'; $INK10 = '#3B2A1E'; $BRN = '#5B463A'; $MU10 = '#7A6450'; $LT10 = '#9A7B5C'; $RED10 = '#C7431F'

Seg (Box 0 0 $W $H $BG 0)
Seg (Box 0 0 $W 8 $ORA 0)
Seg (Box 0 632 $W 8 $ORA 0)

# ---- identity ----
Seg (Circle 40 40 64 $ORA $null)
Seg (T '10' 40 56 64 40 '青' 30 '#FFFFFF' 'CENTER' 'BOLD')
Seg (T '10' 124 46 400 32 '青禾社区 QINGHE' 24 $INK10 'LEFT' 'BOLD')
Seg (T '10' 124 82 400 26 '社区营造计划 · 2026 秋季' 16 $LT10 'LEFT' '')
Seg (T '10' 40 150 520 76 '第 6 届旧物集市' 56 $RED10 'LEFT' 'BOLD')
Seg (T '10' 40 234 520 34 'SWAP MARKET · 摊位导览' 24 $BRN 'LEFT' '')

Seg (Panel 40 288 520 88 '#FFF8EC' 16 '#E8C99A')
Seg (T '10' 64 302 472 32 '10 月 12 日 周日' 23 $INK10 'LEFT' 'BOLD')
Seg (T '10' 64 340 472 28 '09:00 – 16:00 · 晴间多云' 19 $MU10 'LEFT' '')

$stats = @(@('48', '交换席位'), @('4', '摊区数量'), @('3', '集中兑换场'))
for ($i = 0; $i -lt 3; $i++) {
    $x = 40 + $i * 170
    Seg (T '10' $x 400 160 56 $stats[$i][0] 42 $ORA 'LEFT' 'BOLD')
    Seg (T '10' $x 460 160 26 $stats[$i][1] 16 $LT10 'LEFT' '')
}
Seg (T '10' 40 512 520 28 '青禾社区中心广场 · 北门 / 南门进入' 19 $BRN 'LEFT' '')
Seg (T '10' 40 550 520 26 '演示数据 DEMO · 青禾社区居民自治委员会' 16 '#B99A78' 'LEFT' '')

# ---- site map ----
Seg (ShadowBox 600 40 800 560 '#FFFFFF' 20 '0 6 22 #C9A88A2E')
Seg (T '10' 632 64 400 32 '摊位分布 · SITE MAP' 22 $INK10 'LEFT' 'BOLD')
Seg (T '10' 1060 66 316 28 '北门在上 · 南门在下' 16 $LT10 'RIGHT' '')
Seg (Panel 632 116 736 444 '#FBF6EA' 16 '#E0CDB0')

Seg (Panel 656 122 132 30 '#E7F6EC' 15 '#3FA96B')
Seg (T '10' 656 125 132 26 '北门入口' 15 '#2C7F51' 'CENTER' 'BOLD')
Seg (Panel 1204 122 140 30 '#FFF3DC' 15 '#E8A33A')
Seg (T '10' 1204 125 140 26 '服务台' 15 '#A4701A' 'CENTER' 'BOLD')

$zones = @(
    @('A', '书籍文具', 'A01–A12', '12 席', '旧书 · 文具 · 手账素材', '#4A90D9', '#E8F1FB'),
    @('B', '厨房器物', 'B01–B14', '14 席', '锅具 · 餐具 · 小家电', '#E86A3A', '#FDEDE4'),
    @('C', '绿植多肉', 'C01–C10', '10 席', '多肉 · 苗木 · 花器', '#3FA96B', '#E8F6EE'),
    @('D', '玩具童书', 'D01–D12', '12 席', '绘本 · 积木 · 毛绒', '#B06FC9', '#F6EBFA')
)
for ($i = 0; $i -lt 4; $i++) {
    $zx = 656 + ($i % 2) * 368
    $zy = 168 + [Math]::Floor($i / 2.0) * 180
    Seg (Panel $zx $zy 320 156 '#FFFFFF' 14 $zones[$i][5])
    Seg (Panel ($zx + 20) ($zy + 22) 52 52 $zones[$i][6] 16 $null)
    Seg (T '10' ($zx + 20) ($zy + 34) 52 40 $zones[$i][0] 30 $zones[$i][5] 'CENTER' 'BOLD')
    Seg (T '10' ($zx + 86) ($zy + 26) 160 32 $zones[$i][1] 23 $INK10 'LEFT' 'BOLD')
    Seg (T '10' ($zx + 86) ($zy + 64) 160 26 $zones[$i][2] 16 $MU10 'LEFT' '')
    Seg (T '10' ($zx + 248) ($zy + 28) 56 30 $zones[$i][3] 17 $zones[$i][5] 'RIGHT' 'BOLD')
    Seg (Box ($zx + 20) ($zy + 96) 280 1 '#EFE4D2' 0)
    Seg (T '10' ($zx + 20) ($zy + 108) 280 30 $zones[$i][4] 16 $MU10 'LEFT' '')
}

Seg (Panel 656 522 132 30 '#E7F6EC' 15 '#3FA96B')
Seg (T '10' 656 525 132 26 '南门入口' 15 '#2C7F51' 'CENTER' 'BOLD')
Seg (Panel 1204 522 140 30 '#EFEAF6' 15 '#8A72A8')
Seg (T '10' 1204 525 140 26 '旧物回收箱' 15 '#6B559A' 'CENTER' 'BOLD')

# ---- rules ----
Seg (ShadowBox 1440 40 440 380 '#FFFFFF' 20 '0 6 22 #C9A88A2E')
Seg (T '10' 1472 64 380 30 '参与规则 · RULES' 22 $INK10 'LEFT' 'BOLD')
$rules = @(
    @('一件换一件', '摊主与来客按物易物，不设现金找零，贵重物品自行议价'),
    @('先登记后上架', '08:30 前到服务台登记，超时席位让给候补家庭'),
    @('闭市即清场', '16:00 收市，未交换物品请自行带回或投入回收箱')
)
for ($i = 0; $i -lt 3; $i++) {
    $y = 110 + $i * 100
    Seg (Panel 1472 $y 36 36 '#FDE8D8' 12 $null)
    Seg (T '10' 1472 ($y + 6) 36 26 ($i + 1).ToString() 18 $RED10 'CENTER' 'BOLD')
    Seg (T '10' 1522 ($y + 2) 320 28 $rules[$i][0] 19 $INK10 'LEFT' 'BOLD')
    $r = TPara '10' 1522 ($y + 34) 320 $rules[$i][1] 16 26 $MU10 ''
    Seg $r[0]
}

# ---- legend ----
Seg (ShadowBox 1440 440 440 160 '#FFFFFF' 20 '0 6 22 #C9A88A2E')
Seg (T '10' 1472 462 380 28 '摊区图例 · LEGEND' 20 $INK10 'LEFT' 'BOLD')
$leg = @(@('A 书籍文具', '#4A90D9'), @('B 厨房器物', '#E86A3A'), @('C 绿植多肉', '#3FA96B'), @('D 玩具童书', '#B06FC9'))
for ($i = 0; $i -lt 4; $i++) {
    $lx = 1472 + ($i % 2) * 200
    $ly = 506 + [Math]::Floor($i / 2.0) * 44
    Seg (Panel $lx ($ly + 4) 18 18 $leg[$i][1] 4 $null)
    Seg (T '10' ($lx + 28) $ly 170 26 $leg[$i][0] 16 $BRN 'LEFT' '')
}
$L10 = Finish-Case '10' $W $H $BG

"=== gen-b01-b: DSL built ==="
"case-06 = $L06 chars"
"case-07 = $L07 chars"
"case-08 = $L08 chars"
"case-09 = $L09 chars"
"case-10 = $L10 chars"
""
if ($script:PROBLEMS.Count -eq 0) { "problems = 0" } else { "problems = " + $script:PROBLEMS.Count; $script:PROBLEMS | ForEach-Object { "  " + $_ } }
