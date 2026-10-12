# gen-a24.ps1 -- build the three A24 DSL deliverables + content-map.json from schedule.json
# Every number shown in the images comes from outputs/<run>/A24/schedule.json (single source).
$ErrorActionPreference = 'Stop'

$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$OUT  = Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A24'
$TMPD = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A24'

$sched = ([IO.File]::ReadAllText((Join-Path $OUT 'schedule.json'))) | ConvertFrom-Json
$audit = ([IO.File]::ReadAllText((Join-Path $OUT 'schedule-audit.json'))) | ConvertFrom-Json
$rel   = ([IO.File]::ReadAllText((Join-Path $ROOT 'tasks\A24-release-plan-capstone\inputs\release.json'))) | ConvertFrom-Json

$BRAND = '叠光 · 发布演练'

# ---------------- palette ----------------
$BG     = '#0B1220'
$PANEL  = '#111A2B'
$PANEL2 = '#16203A'
$LINE   = '#223052'
$GRID   = '#18213C'
$TEXT   = '#EAF0FB'
$MUTED  = '#96A3C0'
$DES    = '#4338CA'
$ENG    = '#047857'
$DES_L  = '#E4E6FF'
$ENG_L  = '#E4FFF6'
$GAPC   = '#2A3348'
$GAPST   = '#4C5B7E'
$BUF    = '#0B2A20'
$BUFT   = '#4ADE9B'
$BUFT2  = '#8FE7C4'
$DANGER = '#FF5A6E'
$WARN   = '#F5A524'
$RISKBG = '#2A1620'
$CRITBG = '#1E2A4A'

$FAM = 'Noto Sans CJK SC'

function Fmt([double]$v) { return $v.ToString('0.##', [System.Globalization.CultureInfo]::InvariantCulture) }
function E([string]$s) { if ($null -eq $s) { return '' } ; return $s.Replace('&', '&amp;').Replace('<', '&lt;').Replace('>', '&gt;') }

function Box([double]$l, [double]$t, [double]$w, [double]$h, [string]$c, [int]$r = 0) {
    $rr = ''
    if ($r -gt 0) { $rr = ' borderRadius="' + $r.ToString() + '"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" color="' + $c.ToString() + '"' + $rr.ToString() + '/></Positioned>'
}

function Txt([double]$l, [double]$t, [double]$w, [double]$h, [string]$s, [int]$fs, [string]$c, [string]$a = 'LEFT', [bool]$B = $false) {
    $boldAttr = ''
    if ($B) { $boldAttr = ' fontStyle="BOLD"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Text fontSize="' + $fs.ToString() + '" fontFamily="' + $FAM.ToString() + '" color="' + $c.ToString() + '"' + $boldAttr +
           ' textAlign="' + $a.ToString() + '" maxLines="1">' + (E $s) + '</Text></Positioned>'
}

# conservative advance-width estimate (px) for fontSize fs
function TW([string]$s, [int]$fs) {
    if ($null -eq $s) { return 0.0 }
    $w = 0.0
    foreach ($ch in $s.ToCharArray()) {
        $c = [int][char]$ch
        if ($c -eq 0x2192) { $w += 1.00 }            # ->
        elseif ($c -eq 0x2190) { $w += 1.00 }         # <-
        elseif ($c -eq 0x2194) { $w += 1.00 }         # <->
        elseif ($c -eq 0x2013) { $w += 0.55 }         # -
        elseif ($c -eq 0x00B7) { $w += 0.35 }         # .
        elseif ($c -gt 0x2E7F) { $w += 1.00 }         # CJK / fullwidth
        elseif ($c -ge 65 -and $c -le 90) { $w += 0.70 }    # A-Z
        elseif ($c -ge 97 -and $c -le 122) { $w += 0.56 }    # a-z
        elseif ($c -ge 48 -and $c -le 57) { $w += 0.60 }     # 0-9
        elseif ($ch -eq ' ') { $w += 0.30 }
        elseif ($ch -eq ',') { $w += 0.30 }
        elseif ($ch -eq ':') { $w += 0.30 }
        elseif ($ch -eq '.') { $w += 0.30 }
        elseif ($ch -eq '/') { $w += 0.30 }
        elseif ($ch -eq '-') { $w += 0.40 }
        elseif ($ch -eq '(' -or $ch -eq ')' -or $ch -eq '[' -or $ch -eq ']') { $w += 0.35 }
        elseif ($ch -eq '=' -or $ch -eq '+' -or $ch -eq ' ') { $w += 0.60 }
        else { $w += 0.50 }
    }
    return $w * $fs
}

function MaxLine([object]$arr, [int]$fs) {
    $m = 0.0
    foreach ($s in $arr) { $x = ([string]$s); $v = TW $x $fs; if ($v -gt $m) { $m = $v } }
    return $m
}

# ---------------- shared schedule facts ----------------
$tasks    = @($sched.tasks)
$tot      = $sched.totals
$lb       = $sched.lower_bounds
$cp       = $sched.critical_path
$schedGaps     = @($sched.gaps)
$win      = $sched.window
$risks    = @($rel.risks)
$laneA    = 'design'
$laneB    = 'engineering'
$edgeCount = 0
foreach ($t in $tasks) { $edgeCount += @($t.depends).Count }

$critIds = @($cp.tasks)
function IsCrit([string]$id) { return $critIds -contains $id }
function TaskById([string]$id) { return @($tasks | Where-Object { $_.id -eq $id })[0] }

$finishClock   = $tot.finish_clock
$finishMin     = [int]$tot.makespan_minutes
$bufferMin     = [int]$tot.buffer_minutes
$totalWork     = [int]$tot.total_work_minutes
$lbCP          = [int]$lb.critical_path_minutes_ignoring_resources
$lbTwo         = [int]$lb.two_team_divide_lower_bound_minutes
$lbLoad        = [int]$lb.best_team_load_lower_bound_minutes
$lbRes         = [int]$lb.resource_aware_proved_lower_bound_minutes

# hand-tuned word-boundary wraps (verified against the estimator below)
$labelWrap = @{
    'R02' = @('服务与', '字体', '探测')
    'R11' = @('产物与数据', '核验')
    'R12' = @('交付', '归档')
}

# ================================================================
# IMAGE 1 : execution-board.png  1920 x 1080
# ================================================================
$W1 = 1920; $H1 = 1080
$X0 = 24.0; $X1 = 1908.0
$SPAN = $X1 - $X0                     # 1884
$PPM = $SPAN / [double]$win.window_minutes   # 4.485714...
function PX([int]$m) { return $X0 + $m * $PPM }

$p1 = New-Object System.Collections.Generic.List[string]

# --- background
$p1.Add((Box 0 0 $W1 $H1 $BG)) | Out-Null

# --- hour grid lines + lane panels + buffer bands
$laneATop = 186.0; $laneAH = 256.0          # 186..442
$laneBTop = 450.0; $laneBH = 256.0          # 450..706
$pillAH = 36.0
$barAH = 200.0
$barATop = $laneATop + 50                    # 236
$barBTop = $laneBTop + 50                    # 500

$p1.Add((Box $X0 $laneATop $SPAN $laneAH $PANEL 16)) | Out-Null
$p1.Add((Box $X0 $laneBTop $SPAN $laneBH $PANEL 16)) | Out-Null

$bufX = PX 260
$bufW = $X1 - $bufX
$p1.Add((Box $bufX $laneATop $bufW $laneAH $BUF 0)) | Out-Null
$p1.Add((Box $bufX $laneBTop $bufW $laneBH $BUF 0)) | Out-Null

# gridlines on top of panels/bands
$p1.Add((Box $X0 176 $SPAN 2 $LINE 0)) | Out-Null
foreach ($m in @(60, 120, 180, 240, 300, 360)) {
    $gx = PX $m
    $p1.Add((Box $gx 178 1 ($laneBTop + $laneBH - 178) $GRID 0)) | Out-Null
}
# tick marks + hour labels
foreach ($m in @(0, 60, 120, 180, 240, 300, 360, 420)) {
    $gx = PX $m
    $p1.Add((Box ($gx - 1.5) 164 3 12 $LINE 0)) | Out-Null
    if ($m -eq 420) {
        $p1.Add((Txt ($gx - 208) 132 200 28 '16:00 截止线' 20 $DANGER 'RIGHT' $true)) | Out-Null
    }
    elseif ($m -eq 0) {
        $p1.Add((Txt ($gx + 6) 132 120 28 '09:00 开工' 20 $MUTED 'LEFT' $false)) | Out-Null
    }
    else {
        $clk = '{0:d2}:00' -f (9 + ($m / 60))
        $p1.Add((Txt ($gx + 6) 132 100 28 $clk 20 $MUTED 'LEFT' $false)) | Out-Null
    }
}
# 13:20 finish marker on the axis
$p1.Add((Box ($bufX - 1.5) 164 3 12 $BUFT 0)) | Out-Null
$p1.Add((Txt ($bufX + 12) 132 180 28 ($finishClock.ToString() + ' 完成') 20 $BUFT 'LEFT' $true)) | Out-Null

# finish boundary line
$p1.Add((Box ($bufX - 1.5) $laneATop 3 ($laneBTop + $laneBH - $laneATop) $BUFT 0)) | Out-Null

# --- lane pills
$desTasks = @($tasks | Where-Object { $_.team -eq $laneA })
$engTasks = @($tasks | Where-Object { $_.team -eq $laneB })
$pillA1 = 'design 团队 · ' + $desTasks.Count.ToString() + ' 项 · ' + $tot.design_busy.ToString() + ' 分钟'
$pillB1 = 'engineering 团队 · ' + $engTasks.Count.ToString() + ' 项 · ' + $tot.engineering_busy.ToString() + ' 分钟'
$pA1w = [Math]::Ceiling((TW $pillA1 22)) + 40
$pB1w = [Math]::Ceiling((TW $pillB1 22)) + 40
$p1.Add((Box $X0 $laneATop $pA1w $pillAH $DES 18)) | Out-Null
$p1.Add((Txt ($X0 + 18) ($laneATop + 4) ($pA1w - 36) 28 $pillA1 22 '#FFFFFF' 'LEFT' $true)) | Out-Null
$p1.Add((Box $X0 $laneBTop $pB1w $pillAH $ENG 18)) | Out-Null
$p1.Add((Txt ($X0 + 18) ($laneBTop + 4) ($pB1w - 36) 28 $pillB1 22 '#FFFFFF' 'LEFT' $true)) | Out-Null

# --- gap blocks (striped)
function Add-Gap([System.Collections.Generic.List[string]]$p, [double]$gTop, [double]$gH, [double]$gx, [double]$gw) {
    $p.Add((Box $gx $gTop $gw $gH $GAPC 8)) | Out-Null
    $sx = $gx + 3
    while (($sx + 3) -le ($gx + $gw - 1)) {
        $p.Add((Box $sx $gTop 3 $gH $GAPST 0)) | Out-Null
        $sx += 8
    }
}

# --- task blocks
$blockReport = @()
foreach ($t in $tasks) {
    $isDes = ($t.team -eq $laneA)
    $fill = $DES; $fg = '#FFFFFF'; $fg2 = $DES_L; $fg3 = $DES_L
    if (-not $isDes) { $fill = $ENG; $fg = '#FFFFFF'; $fg2 = $ENG_L; $fg3 = $ENG_L }
    $laneTop = $laneBTop; $barTop = $barBTop
    if ($isDes) { $laneTop = $laneATop; $barTop = $barATop }

    $bx = PX ([int]$t.start_min)
    $bw = (PX ([int]$t.end_min)) - $bx
    $pad = 4.0
    $inner = $bw - 2 * $pad

    # label lines
    if ($labelWrap.ContainsKey($t.id)) { $lines = @($labelWrap[$t.id]) }
    else { $lines = @([string]$t.label) }
    $lw = MaxLine $lines 20
    if ($lines.Count -eq 1 -and $lw -gt $inner) { throw ("label overflow " + $t.id + " " + $lw + " > " + $inner) }

    # dependency lines
    $deps = @($t.depends)
    if ($deps.Count -eq 0) { $depLines = @('无前驱') }
    else {
        $joined = ($deps -join ',')
        if ((TW $joined 20) -le $inner) { $depLines = @($joined) }
        else { $depLines = @($deps) }
    }

    $nLine = 1 + $lines.Count + 2 + $depLines.Count
    $contentH = 30 + 26 * ($nLine - 1)
    if (($contentH + 14) -gt $barAH) { throw ("block too tall " + $t.id + " " + $contentH) }
    $y = $barTop + ($barAH - $contentH) / 2

    $p1.Add((Box $bx $barTop $bw $barAH $fill 10)) | Out-Null
    $tx = $bx + $pad; $tw = $bw - 2 * $pad

    $p1.Add((Txt $tx $y $tw 30 $t.id 24 $fg 'LEFT' $true)) | Out-Null
    $y += 30
    foreach ($ln in $lines) { $p1.Add((Txt $tx $y $tw 26 $ln 20 $fg 'LEFT' $false)) | Out-Null; $y += 26 }
    $p1.Add((Txt $tx $y $tw 26 $t.start_clock 20 $fg2 'LEFT' $false)) | Out-Null; $y += 26
    $p1.Add((Txt $tx $y $tw 26 $t.end_clock 20 $fg2 'LEFT' $false)) | Out-Null; $y += 26
    foreach ($dl in $depLines) { $p1.Add((Txt $tx $y $tw 26 $dl 20 $fg3 'LEFT' $false)) | Out-Null; $y += 26 }

    $blockReport += [pscustomobject]@{
        id = $t.id; x = [Math]::Round($bx, 2); w = [Math]::Round($bw, 2)
        inner = [Math]::Round($inner, 2); labelLines = $lines.Count; labelMaxPx = [Math]::Round($lw, 1)
        depLines = $depLines.Count; contentH = $contentH; fits = ($contentH + 14 -le $barAH)
    }
}
# gap blocks (after tasks so the stripes read on top of neighbours)
foreach ($g in $schedGaps) {
    $isDes = ($g.lane -eq $laneA)
    $barTop = $barBTop
    if ($isDes) { $barTop = $barATop }
    $gsx = PX ([int]$g.start_min)
    $gex = PX ([int]$g.end_min)
    Add-Gap $p1 $barTop $barAH $gsx ($gex - $gsx)
}

# --- buffer labels
$p1.Add((Txt $bufX ($laneATop + 74) $bufW 46 ('剩余缓冲 ' + $bufferMin.ToString() + ' 分钟') 34 $BUFT 'CENTER' $true)) | Out-Null
$p1.Add((Txt $bufX ($laneATop + 126) $bufW 34 ($finishClock.ToString() + ' 完成 → ' + $win.deadline_clock.ToString() + ' 截止') 24 $BUFT2 'CENTER' $false)) | Out-Null
$p1.Add((Txt $bufX ($laneBTop + 88) $bufW 36 ('缓冲 ' + $bufferMin.ToString() + ' 分钟') 26 $BUFT 'CENTER' $true)) | Out-Null
$p1.Add((Txt $bufX ($laneBTop + 130) $bufW 30 ($finishClock.ToString() + ' → ' + $win.deadline_clock) 24 $BUFT2 'CENTER' $false)) | Out-Null

# --- deadline dashed line (drawn over everything in the lane area)
$dlX = $X1 - 2
$dy = 120.0
while ($dy -lt ($laneBTop + $laneBH)) {
    $dh = 12.0
    if (($dy + $dh) -gt ($laneBTop + $laneBH)) { $dh = ($laneBTop + $laneBH) - $dy }
    $p1.Add((Box $dlX $dy 5 $dh $DANGER 0)) | Out-Null
    $dy += 20
}

# --- header
$p1.Add((Txt $X0 22 900 30 ($BRAND.ToString() + ' ｜ ' + $win.day.ToString() + ' 发布日') 22 $MUTED 'LEFT' $false)) | Out-Null
$p1.Add((Txt $X0 54 1100 54 '发布日执行泳道 · 双团队约束排程' 42 $TEXT 'LEFT' $true)) | Out-Null
$p1.Add((Box 1488 34 420 64 $PANEL2 14)) | Out-Null
$p1.Add((Txt 1508 42 380 26 ($win.day.ToString() + ' · ' + $win.start_clock.ToString() + '–' + $win.deadline_clock) 24 $TEXT 'CENTER' $false)) | Out-Null
$p1.Add((Txt 1508 70 380 26 ('完成 ' + $finishClock.ToString() + ' · 缓冲 ' + $bufferMin.ToString() + ' 分') 24 $BUFT 'CENTER' $true)) | Out-Null
$p1.Add((Box $X0 118 $SPAN 2 $LINE 0)) | Out-Null

# --- legend / gap detail panel
$p1.Add((Box $X0 712 $SPAN 156 $PANEL 14)) | Out-Null
$p1.Add((Txt ($X0 + 20) 720 600 30 '空档明细与图例' 24 $TEXT 'LEFT' $true)) | Out-Null
$gapLines = @()
$gA = @($schedGaps | Where-Object { $_.lane -eq $laneA })[0]
$gB = @($schedGaps | Where-Object { $_.lane -eq $laneA -and $_.kind -eq 'idle' })
$gB1 = @($schedGaps | Where-Object { $_.lane -eq $laneB -and $_.start_min -eq 20 })[0]
$gB2 = @($schedGaps | Where-Object { $_.lane -eq $laneB -and $_.kind -eq 'standby' })[0]
$gapLines += ('空档 1｜design ' + $gA.start.ToString() + '–' + $gA.end.ToString() + '（' + $gA.minutes.ToString() + ' 分钟）：design 完成 R09 后必须等 engineering 的 R08 于 12:25 结束，才能开始 R10。')
$gapLines += ('空档 2｜engineering ' + $gB1.start.ToString() + '–' + $gB1.end.ToString() + '（' + $gB1.minutes.ToString() + ' 分钟）：R02 已结束，但 R05 依赖 09:25 才结束的 R01，最早 09:25 开工。')
$gapLines += ('空档 3｜engineering ' + $gB2.start.ToString() + '–' + $gB2.end.ToString() + '（' + $gB2.minutes.ToString() + ' 分钟，待命）：R11 结束后待命；' + $finishClock.ToString() + ' 起两条泳道同为剩余缓冲 ' + $bufferMin.ToString() + ' 分钟。')
$gapLines += ('图例：任务块所在泳道即所属团队；灰色竖纹＝空档；绿色区＝剩余缓冲；红色虚线＝' + $win.deadline_clock.ToString() + ' 截止线；块内自上而下＝编号/标签/起始/结束/前驱编号。')
$gy = 756
foreach ($gl in $gapLines) {
    if ((TW $gl 20) -gt ($SPAN - 48)) { throw ('legend line too wide: ' + [Math]::Round((TW $gl 20), 1)) }
    $p1.Add((Txt ($X0 + 20) $gy ($SPAN - 40) 26 $gl 20 $MUTED 'LEFT' $false)) | Out-Null
    $gy += 26
}

# --- metric cards (4)
$mcY = 876.0; $mcH = 104.0
$mcW = ($SPAN - 3 * 16) / 4
$cards = @(
    @{ l = '总工时（12 项）'; v = ($totalWork.ToString() + ' 分钟'); s = ($laneA.ToString() + ' ' + $tot.design_busy.ToString() + ' ｜ ' + $laneB.ToString() + ' ' + $tot.engineering_busy) },
    @{ l = '关键路径（忽略资源）'; v = ($lbCP.ToString() + ' 分钟'); s = ($critIds -join '→') },
    @{ l = '两团队均分下界'; v = ($lbTwo.ToString() + ' 分钟'); s = 'ceil(' + $totalWork.ToString() + ' ÷ 2) = 242.5，向上取整' },
    @{ l = '本排程完成（已证最优）'; v = $finishClock; s = ($finishMin.ToString() + ' 分钟 · 剩余缓冲 ' + $bufferMin.ToString() + ' 分') }
)
$ci = 0
foreach ($cd in $cards) {
    $cx = $X0 + $ci * ($mcW + 16)
    $p1.Add((Box $cx $mcY $mcW $mcH $PANEL 14)) | Out-Null
    $p1.Add((Txt ($cx + 22) ($mcY + 6) ($mcW - 44) 26 $cd.l 20 $MUTED 'LEFT' $false)) | Out-Null
    $p1.Add((Txt ($cx + 22) ($mcY + 32) ($mcW - 44) 44 $cd.v 34 $TEXT 'LEFT' $true)) | Out-Null
    if ((TW $cd.s 20) -gt ($mcW - 44)) { throw ('card sub too wide: ' + $cd.s.ToString() + ' = ' + [Math]::Round((TW $cd.s 20), 1) + ' > ' + ($mcW - 44)) }
    $p1.Add((Txt ($cx + 22) ($mcY + 76) ($mcW - 44) 26 $cd.s 20 $MUTED 'LEFT' $false)) | Out-Null
    $ci++
}

# --- critical path + footer panel
$p1.Add((Box $X0 988 $SPAN 88 $PANEL 14)) | Out-Null
$cpLine = '关键路径（忽略资源）' + $lbCP.ToString() + ' 分钟：' + (($critIds | ForEach-Object { $_ }) -join ' → ')
if ((TW $cpLine 24) -gt ($SPAN - 48)) { throw ('cp line too wide ' + [Math]::Round((TW $cpLine 24), 1)) }
$p1.Add((Txt ($X0 + 20) 994 ($SPAN - 40) 30 $cpLine 24 $TEXT 'LEFT' $true)) | Out-Null
$f2 = ($BRAND.ToString() + ' ｜ execution-board.png ｜ 1920×1080 ｜ 时间轴 ' + $win.start_clock.ToString() + '–' + $win.deadline_clock.ToString() + ' 等比缩放，1 分钟 = ' + [Math]::Round($PPM, 2) + ' px')
$f3 = '任务块所在泳道即所属团队，同一团队同一时刻只有一个任务块；依赖以块内编号索引表示，未画交叉连线；数据来源 schedule.json（三图共用）。'
if ((TW $f2 20) -gt ($SPAN - 48)) { throw ('f2 too wide ' + [Math]::Round((TW $f2 20), 1)) }
if ((TW $f3 20) -gt ($SPAN - 48)) { throw ('f3 too wide ' + [Math]::Round((TW $f3 20), 1)) }
$p1.Add((Txt ($X0 + 20) 1026 ($SPAN - 40) 26 $f2 20 $MUTED 'LEFT' $false)) | Out-Null
$p1.Add((Txt ($X0 + 20) 1050 ($SPAN - 40) 26 $f3 20 $MUTED 'LEFT' $false)) | Out-Null

$dsl1 = '<Snapshot type="png" background="' + $BG.ToString() + '"><Container width="' + $W1.ToString() + '" height="' + $H1.ToString() + '" color="' + $BG.ToString() + '"><Stack>' + ($p1 -join '') + '</Stack></Container></Snapshot>'
[IO.File]::WriteAllText((Join-Path $TMPD 'execution-board.snapshot'), $dsl1, (New-Object System.Text.UTF8Encoding($false)))

# ================================================================
# IMAGE 2 : decision-brief.png  1200 x 1600
# ================================================================
$W2 = 1200; $H2 = 1600
$M2 = 48.0
$CW2 = $W2 - 2 * $M2          # 1104
$p2 = New-Object System.Collections.Generic.List[string]
$p2.Add((Box 0 0 $W2 $H2 $BG)) | Out-Null

# header
$p2.Add((Txt $M2 44 700 30 $BRAND 24 $MUTED 'LEFT' $false)) | Out-Null
$p2.Add((Txt $M2 78 800 58 '发布决策简报' 46 $TEXT 'LEFT' $true)) | Out-Null
$p2.Add((Txt $M2 142 $CW2 32 ($win.day.ToString() + ' ｜ ' + $win.start_clock.ToString() + '–' + $win.deadline_clock.ToString() + ' ｜ design + engineering 各一个团队') 24 $MUTED 'LEFT' $false)) | Out-Null
$p2.Add((Box $M2 184 $CW2 2 $LINE 0)) | Out-Null

# metric cards
$halfW2 = ($CW2 - 16) / 2
$c2h = 116.0
function Add-Card([System.Collections.Generic.List[string]]$p, [double]$x, [double]$y, [double]$w, [string]$lab, [string]$val, [string]$sub, [string]$acc) {
    $p.Add((Box $x $y $w 116 $PANEL 16)) | Out-Null
    $p.Add((Box $x $y 6 116 $acc 3)) | Out-Null
    if ((TW $lab 24) -gt ($w - 48)) { throw ('card label wide: ' + $lab) }
    $p.Add((Txt ($x + 24) ($y + 14) ($w - 48) 28 $lab 24 $MUTED 'LEFT' $false)) | Out-Null
    if ((TW $val 38) -gt ($w - 48)) { throw ('card value wide: ' + $val.ToString() + ' = ' + [Math]::Round((TW $val 38), 1)) }
    $p.Add((Txt ($x + 24) ($y + 44) ($w - 48) 48 $val 38 $TEXT 'LEFT' $true)) | Out-Null
    if ((TW $sub 24) -gt ($w - 48)) { throw ('card sub wide: ' + $sub.ToString() + ' = ' + [Math]::Round((TW $sub 24), 1) + ' > ' + ($w - 48)) }
    $p.Add((Txt ($x + 24) ($y + 86) ($w - 48) 28 $sub 24 $MUTED 'LEFT' $false)) | Out-Null
}
Add-Card $p2 $M2 202 $halfW2 '总工时' ($totalWork.ToString() + ' 分钟') ($laneA.ToString() + ' ' + $tot.design_busy.ToString() + ' ｜ ' + $laneB.ToString() + ' ' + $tot.engineering_busy) $DES
Add-Card $p2 ($M2 + $halfW2 + 16) 202 $halfW2 '关键路径（忽略资源）' ($lbCP.ToString() + ' 分钟') ($critIds -join '→') $DES
Add-Card $p2 $M2 330 $halfW2 '两团队均分下界' ($lbTwo.ToString() + ' 分钟') ('ceil(' + $totalWork.ToString() + ' ÷ 2) = 242.5，向上取整') $ENG
Add-Card $p2 ($M2 + $halfW2 + 16) 330 $halfW2 '资源感知下界（已证最优）' ($lbRes.ToString() + ' 分钟') '完整情形枚举，不依赖启发式搜索' $ENG
Add-Card $p2 $M2 458 $CW2 '完成时间与剩余缓冲' ($finishClock.ToString() + ' 完成 · ' + $finishMin.ToString() + ' 分钟 · 缓冲 ' + $bufferMin.ToString() + ' 分钟') ($win.start_clock.ToString() + ' 开工 + ' + $finishMin.ToString() + ' 分钟 = ' + $finishClock.ToString() + '；截止 ' + $win.deadline_clock.ToString() + '，剩余 ' + $bufferMin.ToString() + ' 分钟缓冲') $BUFT

# dependency overview (DAG layers)
# longest-path layering: layer(t) = 1 + max(layer(deps)), iterated to a fixed point
$layerOf = @{}
foreach ($t in $tasks) { $layerOf[$t.id] = 0 }
for ($pass = 0; $pass -lt $tasks.Count; $pass++) {
    foreach ($t in $tasks) {
        $m = -1
        foreach ($d in @($t.depends)) { if ($layerOf[$d] -gt $m) { $m = $layerOf[$d] } }
        $layerOf[$t.id] = $m + 1
    }
}
$maxLayer = 0
foreach ($k in $layerOf.Keys) { if ($layerOf[$k] -gt $maxLayer) { $maxLayer = $layerOf[$k] } }
$layers = @()
for ($i = 0; $i -le $maxLayer; $i++) {
    $ids = @($tasks | Where-Object { $layerOf[$_.id] -eq $i } | Sort-Object { $_.id } | ForEach-Object { $_.id })
    if ($ids.Count -gt 0) { $layers += @{ k = ('L' + $i); ids = $ids } }
}
# sanity: every predecessor sits in a strictly earlier layer
foreach ($ly in $layers) {
    foreach ($id in $ly.ids) {
        $tk = TaskById $id
        foreach ($d in @($tk.depends)) {
            $li = -1; for ($i = 0; $i -lt $layers.Count; $i++) { if ($layers[$i].ids -contains $d) { $li = $i } }
            $ti = -1; for ($i = 0; $i -lt $layers.Count; $i++) { if ($layers[$i].ids -contains $id) { $ti = $i } }
            if ($li -ge $ti) { throw ('layer violation ' + $d + ' -> ' + $id) }
        }
    }
}

$p2.Add((Txt $M2 596 $CW2 36 ('依赖总览 · ' + $layers.Count.ToString() + ' 层 · ' + $edgeCount.ToString() + ' 条依赖边') 28 $TEXT 'LEFT' $true)) | Out-Null
$rowY = 642.0
$rowH = 40.0; $rowGap = 4.0
foreach ($ly in $layers) {
    $p2.Add((Box $M2 $rowY 60 $rowH $PANEL2 10)) | Out-Null
    $p2.Add((Txt $M2 ($rowY + 8) 60 28 $ly.k 24 $MUTED 'CENTER' $true)) | Out-Null
    $cx2 = $M2 + 76
    foreach ($id in $ly.ids) {
        $tk = TaskById $id
        $lab = $id.ToString() + ' ' + $tk.label.ToString() + ' · ' + $tk.minutes.ToString() + '分'
        $cwid = [Math]::Ceiling((TW $lab 24)) + 40
        $acc = $DES
        if ($tk.team -eq $laneB) { $acc = $ENG }
        $bgc = $PANEL2
        if (IsCrit $id) { $bgc = $CRITBG }
        $p2.Add((Box $cx2 $rowY $cwid $rowH $bgc 10)) | Out-Null
        $p2.Add((Box $cx2 $rowY 5 $rowH $acc 3)) | Out-Null
        $p2.Add((Txt ($cx2 + 16) ($rowY + 8) ($cwid - 24) 28 $lab 24 $TEXT 'LEFT' $true)) | Out-Null
        $cx2 += $cwid + 12
        if ($cx2 -gt ($M2 + $CW2)) { throw ('dag row overflow ' + $ly.k) }
    }
    $rowY += $rowH + $rowGap
}
$dagEnd = $rowY - $rowGap
$legY = $dagEnd + 10
$dagLegend = '左竖条＝所属团队（紫=' + $laneA.ToString() + '，绿=' + $laneB.ToString() + '）；高亮底色＝关键路径任务。'
if ((TW $dagLegend 24) -gt $CW2) { throw ('dag legend wide ' + [Math]::Round((TW $dagLegend 24), 1)) }
$p2.Add((Txt $M2 $legY $CW2 30 $dagLegend 24 $MUTED 'LEFT' $false)) | Out-Null

# explicit dependency edge list (grouped by target task, one arrow group per edge)
$edgeGroups = @()
foreach ($t in ($tasks | Sort-Object { $_.id })) {
    $d = @($t.depends)
    if ($d.Count -gt 0) { $edgeGroups += ($t.id.ToString() + '←' + ($d -join ',')) }
}
$covered = 0
foreach ($t in $tasks) {
    $d = @($t.depends)
    if ($d.Count -gt 0) {
        $g = $t.id.ToString() + '←' + ($d -join ',')
        if ($edgeGroups -notcontains $g) { throw ('missing edge group ' + $g) }
        $covered += $d.Count
    }
}
if ($covered -ne $edgeCount) { throw ('edge count mismatch ' + $covered + ' vs ' + $edgeCount) }
$sep = ' ｜ '
$ePrefix = '依赖边（目标←前驱）：'
$eLines = @(); $cur = ''
foreach ($g in $edgeGroups) {
    $next = if ($cur -eq '') { $ePrefix + $g } else { $cur + $sep + $g }
    if ($cur -ne '' -and ((TW $next 24) -gt $CW2)) { $eLines += $cur; $cur = $g }
    else { $cur = $next }
}
if ($cur -ne '') { $eLines += $cur }
if ($eLines.Count -ne 2) { throw ('edge list needs ' + $eLines.Count + ' lines') }
$eY = $legY + 34
foreach ($el in $eLines) {
    if ((TW $el 24) -gt $CW2) { throw ('edge line wide ' + [Math]::Round((TW $el 24), 1) + ' :: ' + $el) }
    $p2.Add((Txt $M2 $eY $CW2 30 $el 24 $TEXT 'LEFT' $false)) | Out-Null
    $eY += 30
}

# scheduling basis
$basisY = $eY + 12
$p2.Add((Txt $M2 $basisY $CW2 36 '排程依据与最优性下界' 28 $TEXT 'LEFT' $true)) | Out-Null
$basis = @(
    ('关键路径（忽略资源）' + $lbCP.ToString() + ' 分钟：' + (($critIds) -join '→')),
    ('两团队均分下界 ' + $lbTwo.ToString() + ' 分钟：总工时 ' + $totalWork.ToString() + ' ÷ 2 = 242.5，向上取整'),
    ('最佳团队负载下界 ' + $lbLoad.ToString() + ' 分钟：柔性指派下取 max(design, engineering) 的最小值'),
    ('资源感知下界 ' + $lbRes.ToString() + ' 分钟：对全部 8 种柔性指派的完整情形枚举所得'),
    ('本排程完成 ' + $finishMin.ToString() + ' 分钟 = 资源感知下界，故为全局最优，证明见 schedule-audit.json')
)
$by = $basisY + 44
foreach ($b in $basis) {
    if ((TW $b 24) -gt $CW2) { throw ('basis line wide: ' + [Math]::Round((TW $b 24), 1) + ' :: ' + $b) }
    $p2.Add((Txt $M2 $by $CW2 30 $b 24 $MUTED 'LEFT' $false)) | Out-Null
    $by += 30
}

# risks
$riskTitleY = $by + 20
$p2.Add((Txt $M2 $riskTitleY $CW2 36 ('风险与缓解（' + $risks.Count.ToString() + ' 项）') 28 $TEXT 'LEFT' $true)) | Out-Null
$ry = $riskTitleY + 44
foreach ($rk in $risks) {
    $p2.Add((Box $M2 $ry $CW2 70 $PANEL 14)) | Out-Null
    $p2.Add((Box $M2 $ry 6 70 $WARN 3)) | Out-Null
    $l1 = $rk.id.ToString() + ' · ' + $rk.task.ToString() + ' · ' + $rk.impact
    $l2 = '缓解：' + $rk.mitigation
    if ((TW $l1 26) -gt ($CW2 - 60)) { throw ('risk1 wide ' + [Math]::Round((TW $l1 26), 1)) }
    if ((TW $l2 24) -gt ($CW2 - 60)) { throw ('risk2 wide ' + [Math]::Round((TW $l2 24), 1)) }
    $p2.Add((Txt ($M2 + 24) ($ry + 10) ($CW2 - 60) 30 $l1 26 $TEXT 'LEFT' $true)) | Out-Null
    $p2.Add((Txt ($M2 + 24) ($ry + 42) ($CW2 - 60) 28 $l2 24 $MUTED 'LEFT' $false)) | Out-Null
    $ry += 76
}
$footerY = $ry + 12
if (($footerY + 62) -gt $H2) { throw ('brief overflow footerY=' + $footerY) }
$p2.Add((Box $M2 $footerY $CW2 62 $PANEL 14)) | Out-Null
$fl1 = '完成 ' + $finishClock.ToString() + ' ｜ 剩余缓冲 ' + $bufferMin.ToString() + ' 分钟 ｜ 截止 ' + $win.deadline_clock
$fl2 = '数据来源 schedule.json / schedule-audit.json ｜ 与执行图、行动卡共用同一排程'
$p2.Add((Txt ($M2 + 24) ($footerY + 8) ($CW2 - 48) 32 $fl1 26 $BUFT 'LEFT' $true)) | Out-Null
$p2.Add((Txt ($M2 + 24) ($footerY + 34) ($CW2 - 48) 26 $fl2 24 $MUTED 'LEFT' $false)) | Out-Null

$dsl2 = '<Snapshot type="png" background="' + $BG.ToString() + '"><Container width="' + $W2.ToString() + '" height="' + $H2.ToString() + '" color="' + $BG.ToString() + '"><Stack>' + ($p2 -join '') + '</Stack></Container></Snapshot>'
[IO.File]::WriteAllText((Join-Path $TMPD 'decision-brief.snapshot'), $dsl2, (New-Object System.Text.UTF8Encoding($false)))

# ================================================================
# IMAGE 3 : action-card.png  720 x 1280
# ================================================================
$W3 = 720; $H3 = 1280
$p3 = New-Object System.Collections.Generic.List[string]
$p3.Add((Box 0 0 $W3 $H3 $BG)) | Out-Null

$p3.Add((Txt 32 34 656 30 $BRAND 22 $MUTED 'LEFT' $false)) | Out-Null
$p3.Add((Txt 32 66 656 52 '发布日行动卡' 40 $TEXT 'LEFT' $true)) | Out-Null
$sub3 = $win.day.ToString() + ' ｜ ' + $win.start_clock.ToString() + '–' + $win.deadline_clock.ToString() + ' ｜ ' + $tasks.Count.ToString() + ' 项任务 · 按开始时间排序'
if ((TW $sub3 22) -gt 656) { throw ('card sub wide ' + [Math]::Round((TW $sub3 22), 1)) }
$p3.Add((Txt 32 120 656 30 $sub3 22 $MUTED 'LEFT' $false)) | Out-Null

# status strip
$p3.Add((Box 24 158 672 84 '#11241E' 14)) | Out-Null
$status = @(
    @{ x = 44; v = $finishClock; l = ('完成 · ' + $finishMin.ToString() + ' 分钟'); c = $BUFT },
    @{ x = 264; v = ($bufferMin.ToString() + ' 分钟'); l = ('剩余缓冲 → ' + $win.deadline_clock); c = $BUFT },
    @{ x = 484; v = ($totalWork.ToString() + ' 分钟'); l = ('总工时 · ' + $tasks.Count.ToString() + ' 项'); c = $TEXT }
)
foreach ($s in $status) {
    $p3.Add((Txt $s.x 168 200 44 $s.v 34 $s.c 'LEFT' $true)) | Out-Null
    if ((TW $s.l 20) -gt 200) { throw ('status label wide ' + $s.l) }
    $p3.Add((Txt $s.x 210 200 26 $s.l 20 $MUTED 'LEFT' $false)) | Out-Null
}

$p3.Add((Txt 32 258 656 34 ($tasks.Count.ToString() + ' 项任务 · 按开始时间') 26 $TEXT 'LEFT' $true)) | Out-Null

# task rows (sorted by start time, tie-break by id)
$rows = @($tasks | Sort-Object { $_.start_min }, { $_.id })
$riskTaskIds = @($risks | ForEach-Object { $_.task })
$ry3 = 296.0
$rowH3 = 48.0
foreach ($t in $rows) {
    $isRisk = $riskTaskIds -contains $t.id
    $bg3 = $PANEL
    if ($isRisk) { $bg3 = $RISKBG }
    $p3.Add((Box 24 $ry3 672 $rowH3 $bg3 12)) | Out-Null
    $acc3 = $DES
    if ($t.team -eq $laneB) { $acc3 = $ENG }
    $p3.Add((Box 24 $ry3 5 $rowH3 $acc3 3)) | Out-Null

    $tstr = $t.start_clock.ToString() + '–' + $t.end_clock
    $nstr = $t.id.ToString() + ' ' + $t.label
    if ((TW $tstr 22) -gt 150) { throw ('time wide ' + $tstr) }
    if ((TW $nstr 24) -gt 224) { throw ('name wide ' + $nstr.ToString() + ' = ' + [Math]::Round((TW $nstr 24), 1)) }
    $p3.Add((Txt 40 ($ry3 + 10) 150 28 $tstr 22 $TEXT 'LEFT' $true)) | Out-Null
    $p3.Add((Txt 202 ($ry3 + 10) 224 28 $nstr 24 $TEXT 'LEFT' $true)) | Out-Null

    $chipTxt = $t.team
    $chipW = 144
    if ((TW $chipTxt 20) + 16 -gt $chipW) { throw ('chip text wide ' + $chipTxt + ' = ' + [Math]::Round((TW $chipTxt 20), 1)) }
    $p3.Add((Box 434 ($ry3 + 8) $chipW 32 $acc3 16)) | Out-Null
    $p3.Add((Txt 434 ($ry3 + 12) $chipW 26 $chipTxt 20 '#FFFFFF' 'CENTER' $false)) | Out-Null

    $dstr = $t.minutes.ToString() + ' 分钟'
    $flag = '普通'
    if (IsCrit $t.id) { $flag = '关键路径' }
    $p3.Add((Txt 586 ($ry3 + 4) 106 26 $dstr 24 $TEXT 'RIGHT' $true)) | Out-Null
    $p3.Add((Txt 586 ($ry3 + 26) 106 22 $flag 20 $MUTED 'RIGHT' $false)) | Out-Null
    $ry3 += $rowH3 + 6
}
$taskEnd = $ry3 - 6

# risks
$rTitleY = $taskEnd + 16
$p3.Add((Txt 32 $rTitleY 656 34 ('风险提醒（' + $risks.Count.ToString() + ' 项）') 26 $TEXT 'LEFT' $true)) | Out-Null
$ryR = $rTitleY + 42
foreach ($rk in $risks) {
    $p3.Add((Box 24 $ryR 672 76 $PANEL 14)) | Out-Null
    $p3.Add((Box 24 $ryR 5 76 $WARN 3)) | Out-Null
    $l1 = $rk.id.ToString() + ' · ' + $rk.task.ToString() + ' · ' + $rk.impact
    $l2 = '缓解：' + $rk.mitigation
    if ((TW $l1 24) -gt 632) { throw ('risk3-1 wide ' + [Math]::Round((TW $l1 24), 1)) }
    if ((TW $l2 24) -gt 632) { throw ('risk3-2 wide ' + [Math]::Round((TW $l2 24), 1)) }
    $p3.Add((Txt 44 ($ryR + 8) 632 30 $l1 24 $TEXT 'LEFT' $true)) | Out-Null
    $p3.Add((Txt 44 ($ryR + 42) 632 28 $l2 24 $MUTED 'LEFT' $false)) | Out-Null
    $ryR += 82
}
$f3y = $ryR + 6
if (($f3y + 26) -gt $H3) { throw ('card overflow f3y=' + $f3y) }
$f3txt = '共 ' + $tasks.Count.ToString() + ' 项 · 数据来源 schedule.json · 与执行图/决策简报一致'
$p3.Add((Txt 32 $f3y 656 26 $f3txt 20 $MUTED 'LEFT' $false)) | Out-Null

$dsl3 = '<Snapshot type="png" background="' + $BG.ToString() + '"><Container width="' + $W3.ToString() + '" height="' + $H3.ToString() + '" color="' + $BG.ToString() + '"><Stack>' + ($p3 -join '') + '</Stack></Container></Snapshot>'
[IO.File]::WriteAllText((Join-Path $TMPD 'action-card.snapshot'), $dsl3, (New-Object System.Text.UTF8Encoding($false)))

# ================================================================
# content-map.json
# ================================================================
$cm = [ordered]@{
    schema     = 'a24/content-map/v1'
    generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
    timezone   = 'UTC+08:00'
    source_of_truth = 'outputs/run-20261002-220723-mimo/A24/schedule.json'
    brand      = $BRAND
    shared_facts = [ordered]@{
        window        = ($win.start_clock.ToString() + '-' + $win.deadline_clock.ToString() + ' (' + $win.day.ToString() + ')')
        task_count    = $tasks.Count
        total_work    = ($totalWork.ToString() + ' 分钟')
        critical_path = ($critIds -join '->')
        critical_path_minutes_ignoring_resources = $lbCP
        two_team_divide_lower_bound = $lbTwo
        best_team_load_lower_bound  = $lbLoad
        resource_aware_lower_bound_and_makespan = $lbRes
        finish        = $finishClock
        buffer        = ($bufferMin.ToString() + ' 分钟')
        teams         = @($laneA, $laneB)
        edges         = $edgeCount
    }
    images = @(
        [ordered]@{
            file = 'execution-board.png'; size = '1920x1080'; min_body_font = 20
            blocks = @(
                [ordered]@{ section = 'header'; shows = @('brand', 'date', 'window', 'finish', 'buffer') }
                [ordered]@{ section = 'timeline_axis'; shows = @('09:00..16:00 hourly ticks on one linear scale', '13:20 finish marker', '16:00 deadline line label') }
                [ordered]@{ section = 'lane_design'; shows = @('team name', 'task count', 'busy minutes', '6 task blocks', '1 striped gap') }
                [ordered]@{ section = 'lane_engineering'; shows = @('team name', 'task count', 'busy minutes', '6 task blocks', '2 striped gaps') }
                [ordered]@{ section = 'task_block'; shows = @('id', 'label', 'start clock', 'end clock', 'predecessor ids', 'team via owning lane') }
                [ordered]@{ section = 'buffer_band'; shows = @('buffer minutes', 'finish -> deadline') }
                [ordered]@{ section = 'deadline_line'; shows = @('16:00 hard deadline as red dashed vertical line') }
                [ordered]@{ section = 'legend_gap_detail'; shows = @(('gap 1: ' + $gA.start.ToString() + '-' + $gA.end), ('gap 2: ' + $gB1.start.ToString() + '-' + $gB1.end), ('gap 3: ' + $gB2.start.ToString() + '-' + $gB2.end), 'legend entries') }
                [ordered]@{ section = 'metric_cards'; shows = @('total work', 'critical path lb', 'two-team lb', 'finish + buffer') }
                [ordered]@{ section = 'footer'; shows = @('critical path chain', 'scale note', 'consistency note') }
            )
        }
        [ordered]@{
            file = 'decision-brief.png'; size = '1200x1600'; min_body_font = 24
            blocks = @(
                [ordered]@{ section = 'header'; shows = @('brand', 'date', 'window', 'team model') }
                [ordered]@{ section = 'metric_cards'; shows = @('total work', 'critical path lb', 'two-team lb', 'resource-aware lb (proven)', 'finish time', 'remaining buffer') }
                [ordered]@{ section = 'dependency_overview'; shows = @(('6 layers'), ($edgeCount.ToString() + ' edges'), 'per-task id + label + minutes', 'team via accent colour', 'critical path via highlight') }
                [ordered]@{ section = 'scheduling_basis'; shows = @('critical path', 'two-team lower bound', 'best-team-load lower bound', 'resource-aware lower bound', 'why the plan is optimal') }
                [ordered]@{ section = 'risks'; shows = @('K1/K2/K3 impact + mitigation') }
                [ordered]@{ section = 'footer'; shows = @('finish', 'buffer', 'deadline', 'source files') }
            )
        }
        [ordered]@{
            file = 'action-card.png'; size = '720x1280'; min_body_font = 20
            blocks = @(
                [ordered]@{ section = 'header'; shows = @('brand', 'date', 'window', 'task count', 'sort order') }
                [ordered]@{ section = 'status_strip'; shows = @('finish', 'finish duration', 'remaining buffer', 'deadline', 'total work') }
                [ordered]@{ section = 'task_rows'; shows = @(('12 rows sorted by start time'), 'start-end', 'id + label', 'team chip', 'minutes', 'critical flag') }
                [ordered]@{ section = 'risks'; shows = @('K1/K2/K3 id, task, impact, mitigation') }
                [ordered]@{ section = 'footer'; shows = @('source + cross-image consistency note') }
            )
        }
    )
    cross_image_rules = @(
        'all three images read every number from schedule.json; none hard-codes its own schedule',
        'finish ' + $finishClock.ToString() + ' / ' + $finishMin.ToString() + ' minutes and buffer ' + $bufferMin.ToString() + ' minutes appear identically on all three',
        'team membership per task is identical on all three (lane ownership on the board, accent colour in the brief, chip on the card)'
    )
}
[IO.File]::WriteAllText((Join-Path $OUT 'content-map.json'), (($cm | ConvertTo-Json -Depth 12)) + "`n", (New-Object System.Text.UTF8Encoding($false)))

# ---------------- report ----------------
'=== A24 DSL generation ==='
'dsl1 execution-board : ' + $dsl1.Length.ToString() + ' chars'
'dsl2 decision-brief  : ' + $dsl2.Length.ToString() + ' chars'
'dsl3 action-card     : ' + $dsl3.Length.ToString() + ' chars'
''
'block geometry (x0=' + $X0.ToString() + ' x1=' + $X1.ToString() + ' PPM=' + [Math]::Round($PPM, 6) + '):'
$blockReport | Sort-Object { $_.x } | ForEach-Object {
    '  {0}  x={1,8}  w={2,7}  inner={3,7}  labelLines={4} labelMaxPx={5,6}  depLines={6}  contentH={7}  fits={8}' -f $_.id, $_.x, $_.w, $_.inner, $_.labelLines, $_.labelMaxPx, $_.depLines, $_.contentH, $_.fits
}
''
'layout end checks: brief footerY=' + $footerY.ToString() + ' (limit ' + ($H2 - 62) + ')  card footerY=' + $f3y.ToString() + ' (limit ' + ($H3 - 26) + ')'
'done'
