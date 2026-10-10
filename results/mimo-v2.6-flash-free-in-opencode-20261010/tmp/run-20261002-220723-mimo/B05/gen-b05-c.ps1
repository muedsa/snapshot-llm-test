# gen-b05-c.ps1 -- build case-07, case-08, case-09, case-10
# PS 5.1: masthead result is $mh; every command-argument concat parenthesised;
# int + string must cast the int first (PowerShell does arithmetic otherwise);
# no multi-line commands; no inline `if` in argument position.
param([int]$Round = 1)
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $root 'tmp\run-20261002-220723-mimo\B05\lib-b05.ps1')

$calc = Get-Calc
$att  = $calc.attitudes
$six  = @($calc.households | Where-Object { $_.id -eq '602' })[0]

function OutPath([string]$cid) {
    return (Join-Path $script:B05TMP ("{0}\r{1:d2}.snapshot" -f $cid, $Round))
}
function Save([string]$cid, [string]$body, [int]$cw, [int]$ch) {
    Write-Dsl5 (OutPath $cid) $body
    $g = [regex]::Match($body, '<Container width="(\d+)" height="(\d+)"')
    if ($g.Groups[1].Value -ne [string]$cw -or $g.Groups[2].Value -ne [string]$ch) {
        throw "$cid canvas mismatch: expected ${cw}x${ch}"
    }
    Write-Output ("  {0} r{1:d2}  {2}x{3}  {4} bytes  problems={5}" -f
        $cid, $Round, $g.Groups[1].Value, $g.Groups[2].Value,
        (Get-Item (OutPath $cid)).Length, $script:PROBLEMS.Count)
}
function Guard([string]$cid, [double]$bottom, [int]$H) {
    if ($bottom -gt $H) { Fail "$cid content bottom $bottom exceeds canvas height $H" }
}
function StateColor([string]$s) {
    if ($s -eq '已完成' -or $s -eq '合格') { return $script:TEAL }
    if ($s -eq '进行中') { return $script:ACC }
    if ($s -eq '整改')   { return $script:CORAL }
    return $script:GREY
}

# =====================================================================
# case-07 -- 602 室最终确认 (900 x 1340, light, 平板竖)
# =====================================================================
$W = 900; $H = 1340; $M = 36
$o = ''
$o += (Box 0 0 $W 76 $script:WHITE 0)
$o += Ts 'c7-brand' $M 22 220 32 '同梯 TongTi' 22 $script:DISP $script:ACC 'LEFT' ''
$o += Ts 'c7-hdr' ($W - $M - 300) 24 300 30 '梧桐里 3 号楼 · 602 室' 19 $script:SANS $script:MUTEL 'RIGHT' ''
$o += (HR 0 76 $W 1 $script:HAIRL)

$mh = Masthead5 '07' '居民端 · 平板' $M 96 ($W - 2*$M) $script:HAIRL $script:MUTEL $script:INK 18 18
$o += $mh[0]
$o += Ts 'c7-title' $M 148 ($W - 2*$M) 46 '确认并提交签约' 36 $script:DISP $script:INK 'LEFT' ''
$s7 = '602 室 · 顶层东户 · 78.9 ㎡ · 当前态度：顾虑'
$o += Ts 'c7-sub' $M 196 ($W - 2*$M) 26 $s7 20 $script:SANS $script:MUTEL 'LEFT' ''

# ---- section motif with this household highlighted ----
$PY = 242; $PH = 316
$o += (Card $M $PY ($W - 2*$M) $PH $script:WHITE 12 ('1 SOLID ' + $script:HAIRL) '')
$o += Ts 'c7-pt' ($M + 20) ($PY + 16) 400 30 '本户在楼栋中的位置' 21 $script:SANS $script:INK 'LEFT' ''
$o += (Pill ($W - $M - 140) ($PY + 14) '602 · 顾虑' 17 $script:CORAL $script:WHITE $script:SANS)
$o += (Section5 ($M + 20) ($PY + 50) ($W - 2*$M - 40) ($PH - 74) $calc 'light' 'attitude' '602')
Guard 'case-07-top' ($PY + $PH) $H

# ---- self-pay card ----
$SY = 574; $SH = 146
$o += (Card $M $SY ($W - 2*$M) $SH $script:WHITE 12 ('1 SOLID ' + $script:HAIRL) '0 6 18 #15191F14')
$o += Ts 'c7-sl' ($M + 22) ($SY + 16) 400 28 '按模型 A，本户自付' 20 $script:SANS $script:MUTEL 'LEFT' ''
$o += Ts 'c7-big' ($M + 22) ($SY + 46) 340 84 (N0 $six.A) 62 $script:DISP $script:ACC 'LEFT' ''
$o += Ts 'c7-u' ($M + 300) ($SY + 92) 80 34 '元' 24 $script:SANS $script:INK 'LEFT' ''
$cmp7 = @(@('A 按楼层', $six.A), @('B 按面积', $six.B), @('C 低层免摊', $six.C))
$c7x = $M + 420
foreach ($cc in $cmp7) {
    $isA = ($cc[0][0] -eq 'A')
    if ($isA) { $bg7 = $script:ACC; $fg7 = $script:WHITE; $fg7b = '#FFFFFFCC' } else { $bg7 = $script:SHADE; $fg7 = $script:INK; $fg7b = $script:MUTEL }
    $o += (Card $c7x ($SY + 34) 128 82 $bg7 10 '')
    $o += Ts ('c7-cl' + $cc[0]) ($c7x + 10) ($SY + 44) 108 24 $cc[0] 15 $script:SANS $fg7b 'LEFT' ''
    $o += Ts ('c7-cv' + $cc[0]) ($c7x + 10) ($SY + 70) 108 40 (N0 $cc[1]) 23 $script:MONO $fg7 'LEFT' ''
    $c7x += 140
}

# ---- payment nodes ----
$NY = 740
$o += Ts 'c7-nt' $M $NY 400 30 '付款节点 · 三期' 21 $script:SANS $script:INK 'LEFT' ''
$o += Ts 'c7-nn' ($W - $M - 360) ($NY + 2) 360 28 ('合计 ' + (N0 $calc.payment602.total) + ' 元') 20 $script:MONO $script:ACC 'RIGHT' ''
$NY += 34
foreach ($nd in $calc.payment602.nodes) {
    $o += (Card $M $NY ($W - 2*$M) 50 $script:WHITE 8 ('1 SOLID ' + $script:HAIRL) '')
    $o += Ts ('c7-dn' + $nd.pct) ($M + 16) ($NY + 13) 340 28 $nd.node 19 $script:SANS $script:INK 'LEFT' ''
    $o += (Pill ($M + 380) ($NY + 11) ([string]$nd.pct + '%') 17 $script:SHADE $script:MUTEL $script:MONO)
    $o += Ts ('c7-dv' + $nd.pct) ($W - $M - 220) ($NY + 12) 204 30 ((N0 $nd.yuan) + ' 元') 22 $script:MONO $script:INK 'RIGHT' ''
    $NY += 56
}
Guard 'case-07-pay' $NY $H

# ---- checklist ----
$CY = 964
$o += Ts 'c7-ct' $M $CY 500 30 '提交前逐条核对' 21 $script:SANS $script:INK 'LEFT' ''
$o += Ts 'c7-cs' ($W - $M - 300) ($CY + 3) 300 26 '3 / 3 已确认' 17 $script:MONO $script:TEAL 'RIGHT' ''
$CY += 32
$checks7 = @(
  '已阅读分摊方案与付款节点（A 模型 42,985 元）',
  '已知悉工期 65 天与临时用水用电影响',
  '已知悉十年公共支出分摊规则（每年 13,800 元）'
)
for ($k = 0; $k -lt $checks7.Count; $k++) {
    $o += (Card $M $CY ($W - 2*$M) 56 $script:WHITE 8 ('1 SOLID ' + $script:HAIRL) '')
    $o += (CheckBox ($M + 18) ($CY + 16) 28 $true $script:TEAL $script:SHADE)
    $o += Ts ('c7-ck' + $k) ($M + 62) ($CY + 18) ($W - 2*$M - 82) 28 $checks7[$k] 19 $script:SANS $script:INK 'LEFT' ''
    $CY += 64
}

# ---- actions ----
$BY = 1206
$o += (Box $M $BY 556 60 $script:ACC 12)
$o += Ts 'c7-ok' $M $BY 556 60 '确认并提交签约' 24 $script:SANS $script:WHITE 'CENTER' ''
$o += (Card ($M + 568) $BY 260 60 $script:WHITE 12 ('1 SOLID ' + $script:HAIRL) '')
$o += Ts 'c7-back' ($M + 568) $BY 260 60 '返回修改' 22 $script:SANS $script:MUTEL 'CENTER' ''
Guard 'case-07-btn' ($BY + 60) $H

$f7 = '演示数据 DEMO · 金额、付款节点与工期为样例；补贴以当地政策核定为准。'
$o += (Foot5 'c7' '07' $f7 $M 1290 ($W - 2*$M) $script:HAIRL $script:MUTEL)
Save 'case-07' (Page5 $W $H $script:BG_L $o) $W $H

# =====================================================================
# case-08 -- 施工进度与当日现场 (1920 x 760, dark, 超宽)
# =====================================================================
$W = 1920; $H = 760; $M = 60
$o = ''
$mh = Masthead5 '08' '全体业主 · 宽屏' $M 40 ($W - 2*$M) $script:HAIRD $script:MUTED $script:PAPERW 20 20
$o += $mh[0]
$t8 = ('施工第 ' + $calc.schedule.dayIn + ' 天 / ' + $calc.schedule.totalDays + ' · 进度 ' + $calc.schedule.progressPct + '%')
$o += Ts 'c8-title' $M 96 1200 56 $t8 42 $script:DISP $script:PAPERW 'LEFT' ''
$s8 = ('当前阶段：' + $calc.schedule.current + '（第 ' + $calc.schedule.currentDayInPhase + ' 天 / 共 14 天）')
$o += Ts 'c8-sub' $M 154 900 30 $s8 21 $script:SANS $script:MUTED 'LEFT' ''
$o += Ts 'c8-rt' ($M + $W - 2*$M - 700) 154 700 30 '计划工期 65 天 · 预计交付 2026-12-23（演示）' 21 $script:MONO $script:MUTED 'RIGHT' ''

# ---- milestone timeline ----
$TL = $M; $TLY = 200; $COLW = ($W - 2*$M) / 6.0
$o += (Box ($TL + $COLW * 0.5) ($TLY + 30) (($W - 2*$M) - $COLW) 2 $script:HAIRD 0)
for ($i = 0; $i -lt 6; $i++) {
    $ms = $calc.schedule.milestones[$i]
    $cc3 = (StateColor $ms.state)
    $cxL = $TL + ($COLW * $i)
    $cxC = $cxL + ($COLW / 2.0)
    if ($ms.state -eq '进行中') {
        $o += (Card ($cxL + 14) ($TLY + 4) ($COLW - 28) 142 $script:PANEL_D2 10 ('1 SOLID ' + $script:ACC) '')
    }
    $o += (Circ ($cxC - 13) ($TLY + 18) 26 $cc3 '')
    $o += (Circ ($cxC - 9) ($TLY + 22) 18 $script:BG_D '')
    if ($ms.state -eq '已完成') { $o += (Circ ($cxC - 6) ($TLY + 25) 12 $cc3 '') }
    else { $o += (Circ ($cxC - 5) ($TLY + 26) 10 $cc3 '') }
    $o += Ts ('c8-mn' + $i) ($cxL + 20) ($TLY + 56) ($COLW - 40) 28 $ms.name 19 $script:SANS $script:PAPERW 'CENTER' ''
    $o += Ts ('c8-md' + $i) ($cxL + 20) ($TLY + 84) ($COLW - 40) 26 ([string]$ms.days + ' 天') 18 $script:MONO $cc3 'CENTER' ''
    $dr = ('第 ' + $ms.startDay + ' ' + [char]0x2013 + ' ' + $ms.endDay + ' 天 · ' + $ms.state)
    $o += Ts ('c8-mr' + $i) ($cxL + 14) ($TLY + 108) ($COLW - 28) 24 $dr 16 $script:SANS $script:MUTED 'CENTER' ''
    # gantt bar across the full 65 days
    $gx = $TL + (($W - 2*$M) * (($ms.startDay - 1) / [double]$calc.schedule.totalDays))
    $gw = (($W - 2*$M) * ($ms.days / [double]$calc.schedule.totalDays)) - 4
    $o += (Box $gx ($TLY + 138) ($gw) 8 $cc3 4)
}
Guard 'case-08-tl' ($TLY + 150) $H

# ---- today's site notes ----
$SY8 = 370
$o += Ts 'c8-st' $M $SY8 600 30 '当日现场 · 3 条记录（示意图 DEMO）' 21 $script:SANS $script:PAPERW 'LEFT' ''
$o += Ts 'c8-sd' ($M + $W - 2*$M - 500) ($SY8 + 2) 500 26 '2026-11-16 · 记录人 王工' 17 $script:MONO $script:MUTED 'RIGHT' ''
$SY8 += 34
$CW8 = (($W - 2*$M) - 48) / 3.0
$site = @(
  @('井道钢结构吊装', '主立柱 4 根已就位，横梁 12 处焊完 9 处', 'steel'),
  @('玻璃幕墙进场', '24 块中空玻璃到场，暂存 2 号楼北侧需遮阳', 'glass'),
  @('临时用电与防护', '配电箱接地复测合格；围挡 1.8 m，警示灯 2 盏', 'safe')
)
for ($k = 0; $k -lt 3; $k++) {
    $cxL = $M + ($CW8 + 24) * $k
    $o += (Card $cxL $SY8 $CW8 230 $script:PANEL_D 10 ('1 SOLID ' + $script:HAIRD) '')
    $thX = $cxL + 16; $thY = $SY8 + 16; $thW = $CW8 - 32; $thH = 118
    $o += (Box $thX $thY $thW $thH '#0E1216' 8)
    if ($site[$k][2] -eq 'steel') {
        for ($v = 0; $v -lt 4; $v++) { $o += (Box ($thX + 60 + ($v * 90)) ($thY + 14) 16 ($thH - 28) $script:TEAL 2) }
        for ($hz = 0; $hz -lt 3; $hz++) { $o += (Box ($thX + 60) ($thY + 30 + ($hz * 30)) ($thW - 150) 8 $script:ACC2 2) }
        $o += (Box ($thX + 60) ($thY + $thH - 24) ($thW - 150) 10 $script:GREY 2)
    } elseif ($site[$k][2] -eq 'glass') {
        for ($r2 = 0; $r2 -lt 3; $r2++) {
            for ($c8 = 0; $c8 -lt 6; $c8++) {
                $pc = '#2A3B45'; if (($r2 + $c8) % 4 -eq 0) { $pc = '#3E5A63' }
                $o += (Box ($thX + 40 + ($c8 * 66)) ($thY + 16 + ($r2 * 30)) 60 26 $pc 2)
            }
        }
    } else {
        for ($s2 = 0; $s2 -lt 14; $s2++) {
            $sc2 = $script:ACC; if ($s2 % 2 -eq 0) { $sc2 = '#1B1F26' }
            $o += (Box ($thX + 20 + ($s2 * 34)) ($thY + 14) 34 18 $sc2 0)
        }
        $o += (Box ($thX + 40) ($thY + 52) 110 56 $script:PANEL_D2 4)
        $o += (Box ($thX + 48) ($thY + 60) 94 10 $script:TEAL 2)
        $o += (Box ($thX + 48) ($thY + 76) 60 8 $script:AMBER 2)
        $cwz = 66
        for ($z = 0; $z -lt 5; $z++) {
            $cwz = 66 - ($z * 11)
            $o += (Box ($thX + $thW - 120 + ((66 - $cwz) / 2)) ($thY + 56 + ($z * 12)) $cwz 12 $script:ACC 1)
        }
    }
    $o += (Pill ($thX + 10) ($thY + $thH - 34) '示意图 DEMO' 14 $script:PANEL_D2 $script:MUTED $script:SANS 10 24)
    $o += Ts ('c8-it' + $k) ($cxL + 18) ($SY8 + 146) ($CW8 - 36) 30 $site[$k][0] 21 $script:SANS $script:PAPERW 'LEFT' ''
    $o += Ts ('c8-id' + $k) ($cxL + 18) ($SY8 + 178) ($CW8 - 36) 44 $site[$k][1] 18 $script:SANS $script:MUTED 'LEFT' ''
}
Guard 'case-08-site' ($SY8 + 230) $H

# ---- safety strip ----
$FY = 650
$o += (Box $M $FY ($W - 2*$M) 44 $script:PANEL_D2 8)
$o += (Box $M $FY 6 44 $script:ACC2 0)
$saf = '安全提示：施工时段 08:30' + [char]0x2013 + '12:00 / 14:00' + [char]0x2013 + '18:00；单元门临时通道净宽 1.2 m；请勿在围挡内停留、堆放杂物。'
$o += Ts 'c8-sf' ($M + 22) $FY ($W - 2*$M - 44) 44 $saf 19 $script:SANS $script:AMBER 'LEFT' ''

$f8 = '演示数据 DEMO · 天数、日期与现场记录均为样例。'
$o += (Foot5 'c8' '08' $f8 $M 706 ($W - 2*$M) $script:HAIRD $script:MUTED)
Guard 'case-08' 746 $H
Save 'case-08' (Page5 $W $H $script:BG_D $o) $W $H

# =====================================================================
# case-09 -- 交付验收与首次运行 (1000 x 1560, light, 竖屏)
# =====================================================================
$W = 1000; $H = 1560; $M = 40
$o = ''
$o += (Box 0 0 $W 76 $script:WHITE 0)
$o += Ts 'c9-brand' $M 22 220 32 '同梯 TongTi' 22 $script:DISP $script:ACC 'LEFT' ''
$o += Ts 'c9-hdr' ($W - $M - 320) 24 320 30 '梧桐里 3 号楼 · 电梯编号 WT-3' 18 $script:SANS $script:MUTEL 'RIGHT' ''
$o += (HR 0 76 $W 1 $script:HAIRL)

$mh = Masthead5 '09' '验收组 · 竖屏' $M 96 ($W - 2*$M) $script:HAIRL $script:MUTEL $script:INK 18 18
$o += $mh[0]
$o += Ts 'c9-title' $M 148 ($W - 2*$M) 50 '验收清单 · 12 项' 38 $script:DISP $script:INK 'LEFT' ''
$o += Ts 'c9-sub' $M 200 ($W - 2*$M) 26 '2026-12-19 · 居委会 + 业委会 + 特检院联合验收（演示）' 19 $script:SANS $script:MUTEL 'LEFT' ''

# ---- summary ----
$SY9 = 242
$sw = (($W - 2*$M) - 32) / 3.0
$sums = @(@('合格', $calc.acceptance.ok, $script:TEAL), @('待检', 1, $script:AMBER), @('整改', 1, $script:CORAL))
for ($k = 0; $k -lt 3; $k++) {
    $sx = $M + ($sw + 16) * $k
    $o += (Card $sx $SY9 $sw 110 $script:WHITE 12 ('1 SOLID ' + $script:HAIRL) '')
    $o += (Box $sx $SY9 $sw 6 $sums[$k][2] 0)
    $o += Ts ('c9-kl' + $k) ($sx + 18) ($SY9 + 22) ($sw - 36) 26 $sums[$k][0] 19 $script:SANS $script:MUTEL 'LEFT' ''
    $o += Ts ('c9-kv' + $k) ($sx + 18) ($SY9 + 48) ($sw - 36) 52 ([string]$sums[$k][1]) 46 $script:DISP $sums[$k][2] 'LEFT' ''
    $o += Ts ('c9-ku' + $k) ($sx + 84) ($SY9 + 68) ($sw - 102) 30 '项' 20 $script:SANS $script:INK 'LEFT' ''
}
Guard 'case-09-sum' ($SY9 + 110) $H

# ---- checklist ----
$CY = 372
$o += Ts 'c9-ct' $M $CY 500 28 '逐项验收结果' 21 $script:SANS $script:INK 'LEFT' ''
$o += Ts 'c9-cs' ($W - $M - 400) ($CY + 3) 400 26 '共 12 项 · 10 项合格' 17 $script:MONO $script:MUTEL 'RIGHT' ''
$CY += 32
$cols9 = @(46, 78, 386, 410)
$cx9 = $M
$hdr9 = @('#', '状态', '验收项目', '结论 / 备注')
$o += (Box $M $CY ($W - 2*$M) 32 $script:SHADE 0)
for ($k = 0; $k -lt 4; $k++) {
    $hx9 = $cx9 + 12
    $o += Ts ('c9-h' + $k) $hx9 $CY ($cols9[$k] - 16) 32 $hdr9[$k] 16 $script:SANS $script:MUTEL 'LEFT' ''
    $cx9 += $cols9[$k]
}
$CY += 32
for ($k = 0; $k -lt $calc.acceptance.items.Count; $k++) {
    $it = $calc.acceptance.items[$k]
    $sc4 = (StateColor $it.state)
    if ($it.state -eq '合格') { $rbg = $script:WHITE } else { $rbg = '#FDF0EC' }
    $o += (Box $M $CY ($W - 2*$M) 56 $rbg 0)
    $cx9 = $M
    $o += Ts ('c9-i' + $k) ($cx9 + 12) $CY ($cols9[0] - 16) 56 ([string]($k + 1)) 17 $script:MONO $script:MUTEL 'LEFT' ''
    $cx9 += $cols9[0]
    $o += (Pill ($cx9 + 8) ($CY + 15) $it.state 15 $sc4 $script:WHITE $script:SANS 10 26)
    $cx9 += $cols9[1]
    $o += Ts ('c9-n' + $k) ($cx9 + 12) $CY ($cols9[2] - 16) 56 $it.item 19 $script:SANS $script:INK 'LEFT' ''
    $cx9 += $cols9[2]
    $o += Ts ('c9-r' + $k) ($cx9 + 12) $CY ($cols9[3] - 20) 56 $it.note 16 $script:SANS $script:MUTEL 'LEFT' ''
    $o += (Box $M ($CY + 55) ($W - 2*$M) 1 $script:HAIRL 0)
    $CY += 56
}
Guard 'case-09-list' $CY $H

# ---- two open items ----
$PY9 = $CY + 20
$o += Ts 'c9-ot' $M $PY9 500 28 '尚未通过的 2 项 · 责任与期限' 21 $script:SANS $script:INK 'LEFT' ''
$PY9 += 32
$opens = @(
  @('电梯监督检验合格证', '待检', $script:AMBER, '已预约 2026-12-19 特检院到场，报告出具后补录', '负责人 陈主任 · 12-21'),
  @('单元门口高差与坡道', '整改', $script:CORAL, '实测高差 35 mm，要求 ≤ 15 mm，施工方返工后复验', '负责人 王工 · 12-21')
)
foreach ($op in $opens) {
    $o += (Card $M $PY9 ($W - 2*$M) 96 $script:WHITE 10 ('1 SOLID ' + $op[2]) '')
    $o += Ts ('c9-oo' + $op[0]) ($M + 20) ($PY9 + 14) 460 30 $op[0] 21 $script:SANS $script:INK 'LEFT' ''
    $o += Ts ('c9-o2' + $op[0]) ($M + 20) ($PY9 + 44) ($W - 2*$M - 40) 26 $op[3] 17 $script:SANS $script:MUTEL 'LEFT' ''
    $o += Ts ('c9-o3' + $op[0]) ($M + 20) ($PY9 + 68) ($W - 2*$M - 40) 24 $op[4] 16 $script:MONO $op[2] 'LEFT' ''
    $PY9 += 108
}

# ---- first run ----
$FR = $PY9 + 12
$o += (Card $M $FR ($W - 2*$M) 110 $script:TINTD['已签约'] 12 ('1 SOLID ' + $script:TEAL) '')
$o += Ts 'c9-ft' ($M + 22) ($FR + 14) 500 30 '首次运行记录' 21 $script:SANS $script:INK 'LEFT' ''
$o += Ts 'c9-fd' ($M + 22) ($FR + 44) ($W - 2*$M - 44) 26 '2026-12-19 09:12 · 空载 6 个往返 + 额定载荷 1 次（演示）' 17 $script:MONO $script:MUTEL 'LEFT' ''
$o += Ts 'c9-fe' ($M + 22) ($FR + 70) ($W - 2*$M - 44) 26 '平层偏差 ≤ 3 mm，应急通话 2 s 接通，语音报站正常' 17 $script:SANS $script:MUTEL 'LEFT' ''
Guard 'case-09-first' ($FR + 110) $H

$f9 = '演示数据 DEMO · 检验结论、日期与责任人为样例，不构成任何真实检验意见。'
$o += (Foot5 'c9' '09' $f9 $M ($FR + 126) ($W - 2*$M) $script:HAIRL $script:MUTEL)
Save 'case-09' (Page5 $W $H $script:BG_L $o) $W $H

# =====================================================================
# case-10 -- 十年总账 (1560 x 900, dark, 桌面)
# =====================================================================
$W = 1560; $H = 900; $M = 56
$o = ''
$mh = Masthead5 '10' '全体业主 · 桌面' $M 40 ($W - 2*$M) $script:HAIRD $script:MUTED $script:PAPERW 20 20
$o += $mh[0]
$t10 = '十年到底花多少'
$o += Ts 'c10-title' $M 96 800 56 $t10 42 $script:DISP $script:PAPERW 'LEFT' ''
$s10 = '一次性自付 288,000 元 + 每年公共支出 13,800 元 · 十年全楼合计 426,000 元（演示）'
$o += Ts 'c10-sub' $M 154 1100 30 $s10 21 $script:SANS $script:MUTED 'LEFT' ''

# ---- left: cumulative curve ----
$LX = $M; $LW = 860; $LY = 210; $LH = 520
$o += (Card $LX $LY $LW $LH $script:PANEL_D 10 ('1 SOLID ' + $script:HAIRD) '')
$o += Ts 'c10-lt' ($LX + 24) ($LY + 18) 500 30 '全楼累计成本 · 第 0 至第 10 年' 21 $script:SANS $script:PAPERW 'LEFT' ''
$o += Ts 'c10-lg' ($LX + 24) ($LY + 48) 620 26 '橙 = 一次性自付 288,000 ｜ 青 = 当年新增公共支出' 17 $script:SANS $script:MUTED 'LEFT' ''
$chX = $LX + 96; $chY = $LY + 92; $chW = $LW - 136; $chH = 340
$axisMax = 500000.0
# gridlines every 10 万 so the tick labels stay round numbers
foreach ($gl in @(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)) {
    $gy10 = $chY + ($chH * (1.0 - $gl))
    $o += (Box $chX $gy10 $chW 1 $script:HAIRD 0)
    $lbl10 = ([string][int][math]::Round($axisMax * $gl / 10000.0)) + ' 万'
    $o += Ts ('c10-gl' + $gl) ($LX + 24) ($gy10 - 13) 66 26 $lbl10 15 $script:MONO $script:MUTED 'RIGHT' ''
}
$bw10 = ($chW / 11.0) - 10
for ($n = 0; $n -le 10; $n++) {
    $tot10 = [double]$calc.cost.net + ([double]$calc.recurring.perYear * $n)
    $hAll = $chH * ($tot10 / $axisMax)
    $hBase = $chH * ([double]$calc.cost.net / $axisMax)
    $bx10 = $chX + (($chW / 11.0) * $n) + 5
    $o += (Box $bx10 ($chY + $chH - $hBase) $bw10 $hBase $script:ACC 0)
    if ($n -gt 0) { $o += (Box $bx10 ($chY + $chH - $hAll) $bw10 ($hAll - $hBase) $script:TEAL 0) }
    $o += Ts ('c10-y' + $n) $bx10 ($chY + $chH + 8) $bw10 26 ([string]$n) 16 $script:MONO $script:MUTED 'CENTER' ''
}
$o += Ts 'c10-xl' ($chX + $chW - 260) ($chY + $chH + 34) 260 26 '年' 16 $script:SANS $script:MUTED 'RIGHT' ''
$endX = $chX + (($chW / 11.0) * 10) + 5
$o += (Outline ($endX - 6) ($chY - 6) ($bw10 + 12) ($chH + 12) $script:AMBER 3)
$o += Ts 'c10-peak' ($endX - 150) ($chY - 40) 240 30 ('42.6 万元') 21 $script:MONO $script:AMBER 'RIGHT' ''
Guard 'case-10-left' ($LY + $LH) $H

# ---- right: 602 across models ----
$RX = 940; $RW = 564; $RY = 210; $RH = 520
$o += (Card $RX $RY $RW $RH $script:PANEL_D 10 ('1 SOLID ' + $script:HAIRD) '')
$o += Ts 'c10-rt' ($RX + 24) ($RY + 18) 516 30 '602 室 · 十年总额（三种模型）' 21 $script:SANS $script:PAPERW 'LEFT' ''
$ten = @(@('A 按楼层', $calc.tenYear602.A, $script:ACC), @('B 按面积', $calc.tenYear602.B, $script:TEAL), @('C 低层免摊', $calc.tenYear602.C, $script:AMBER))
$maxT = [double]$calc.tenYear602.C
$ry10 = $RY + 62
foreach ($tt in $ten) {
    $o += Ts ('c10-tl' + $tt[0]) ($RX + 24) $ry10 300 28 $tt[0] 19 $script:SANS $script:PAPERW 'LEFT' ''
    $o += Ts ('c10-tv' + $tt[0]) ($RX + $RW - 264) $ry10 240 28 ((N0 $tt[1]) + ' 元') 21 $script:MONO $tt[2] 'RIGHT' ''
    $barW = ($RW - 48) * ([double]$tt[1] / $maxT)
    $o += (Box ($RX + 24) ($ry10 + 34) ($RW - 48) 24 $script:PANEL_D2 6)
    $o += (Box ($RX + 24) ($ry10 + 34) $barW 24 $tt[2] 6)
    $mo = ([string][int][math]::Round([double]$tt[1] / 10 / 12)) + ' 元 / 月'
    $o += Ts ('c10-tm' + $tt[0]) ($RX + 24) ($ry10 + 62) ($RW - 48) 26 $mo 17 $script:MONO $script:MUTED 'LEFT' ''
    $ry10 += 100
}
$o += (HR ($RX + 24) ($ry10 + 4) ($RW - 48) 1 $script:HAIRD)
$o += Ts 'c10-sp' ($RX + 24) ($ry10 + 18) 516 30 ('三种模型相差 ' + (N0 $calc.tenYear602.spread) + ' 元 / 十年') 19 $script:SANS $script:AMBER 'LEFT' ''
$o += Ts 'c10-sn' ($RX + 24) ($ry10 + 48) 516 44 '每年 13,800 元按所选模型的同一权重分摊' 17 $script:SANS $script:MUTEL 'LEFT' ''
Guard 'case-10-right' ($RY + $RH) $H

# ---- bottom KPI row ----
$KY = 750
$kw10 = (($W - 2*$M) - 60) / 4.0
$kps = @(
  @('一次性自付', ((N0 $calc.cost.net) + ' 元'), $script:ACC),
  @('十年运行支出', ((N0 $calc.recurring.tenYear) + ' 元'), $script:TEAL),
  @('十年合计', ((N0 $calc.recurring.wholeTenYear) + ' 元'), $script:AMBER),
  @('每户十年', ((N0 $calc.recurring.perHouseholdTenYearAvg) + ' 元'), $script:PAPERW)
)
for ($k = 0; $k -lt 4; $k++) {
    $kx = $M + (($kw10 + 20) * $k)
    $o += (Box $kx $KY $kw10 70 $script:PANEL_D2 8)
    $o += (Box $kx $KY 5 70 $kps[$k][2] 0)
    $o += Ts ('c10-kl' + $k) ($kx + 18) ($KY + 10) ($kw10 - 36) 26 $kps[$k][0] 17 $script:SANS $script:MUTED 'LEFT' ''
    $o += Ts ('c10-kv' + $k) ($kx + 18) ($KY + 34) ($kw10 - 36) 30 $kps[$k][1] 24 $script:MONO $kps[$k][2] 'LEFT' ''
}
$f10 = '演示数据 DEMO · 维保、电费、年检与大修准备金均为样例价格，未做任何真实采购询价。'
$o += (Foot5 'c10' '10' $f10 $M 836 ($W - 2*$M) $script:HAIRD $script:MUTED)
Guard 'case-10' 876 $H
Save 'case-10' (Page5 $W $H $script:BG_D $o) $W $H

Report-Problems5
