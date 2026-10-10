# lib-b06.ps1 -- DSL helpers for B06 (everyday information, reinvented)
# Dot-source. Chains lib-b05.ps1 -> lib-b04 -> lib-b03 -> lib-b01 (proven primitives).
# PS 5.1 rules honoured: no ??, no ternary, parenthesise arithmetic, no inline `if`
# in argument position, never name a helper H, never reuse $r beside $R,
# never use $d beside $D (case-insensitive collisions silently overwrite),
# never name a length local $L beside a left parameter $l (that one silently moved
# a clip box from x=24 to x=130 and produced a real 200 OK with wrong geometry).
$ErrorActionPreference = 'Stop'

$script:B06ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$script:B06OUT  = Join-Path $script:B06ROOT 'outputs\run-20261002-220723-mimo\B06'
$script:B06TMP  = Join-Path $script:B06ROOT 'tmp\run-20261002-220723-mimo\B06'

. (Join-Path $script:B06ROOT 'tmp\run-20261002-220723-mimo\B05\lib-b05.ps1')

# re-point shared globals at B06
$script:FAM = 'Noto Sans CJK SC'
$script:OUT = $script:B06OUT
$script:PROBLEMS.Clear()
$script:SEG.Clear()
$script:CURRENT = 'none'
$script:CALC = $null

# ---------- B06 surfaces ----------
$script:INK6     = '#0E1317'   # primary text on light
$script:SUB6     = '#5C6674'   # secondary on light
$script:PAGE6    = '#F4F2ED'   # light ground
$script:PANELL6  = '#FFFFFF'   # raised panel on light
$script:SHADE6   = '#E9E5DC'   # light shade / track
$script:HAIRL6   = '#D8D2C6'   # hairline on light
$script:HAIRL6b  = '#B6AE9E'   # stronger rule on light

$script:DARK6    = '#0E1319'   # deep ground
$script:PANELD6  = '#161C24'   # raised panel on dark
$script:PANELD6b = '#1E2631'   # panel 2 on dark
$script:HAIRD6   = '#2A333F'   # hairline on dark
$script:HAIRD6b  = '#3E4A59'   # stronger rule on dark
$script:PAPER6   = '#F1EEE7'   # primary text on dark
$script:MUTED6   = '#95A1B0'   # secondary on dark

# ---------- B06 accents (per-topic, never global) ----------
$script:PRICELIME = '#3FA34D'   # 01 蔬果绿
$script:PRICEAMT  = '#F26B21'   # 01 价签橙
$script:PHARM     = '#2563EB'   # 02 药房蓝
$script:DOSE      = '#D9A21B'   # 02 服药金
$script:JADE      = '#37B7A5'   # 03 青瓷
$script:AMBER6    = '#F0A93B'   # 03 琥珀
$script:CORAL6    = '#EF5B4C'   # 03 珊瑚
$script:ELEC      = '#2D7FF9'   # 04 电光蓝
$script:JUMP      = '#FF7A18'   # 04 跳档橙
$script:LINERED   = '#E5484D'   # 05 线路红
$script:LINEGRN   = '#30A46C'   # 05 线路绿
$script:LINEBLU   = '#4C6EF5'   # 05 线路蓝
$script:LINEORG   = '#F76B15'   # 05 线路橙
$script:MAG       = '#E84393'   # 06 玫红
$script:WARN      = '#F5C518'   # 06 警示黄
$script:INDIGO    = '#4C5FD5'   # 07 靛蓝
$script:CLAIM     = '#E0A33C'   # 07 争回金
$script:RAIN      = '#22B8CF'   # 08 降雨青
$script:UMB       = '#FFD43B'   # 08 伞黄
$script:ASPHALT   = '#2E333B'   # 09 柏油
$script:PARK      = '#F5B301'   # 09 车位黄
$script:LATE      = '#E5484D'   # 09 超时红
$script:PARCEL    = '#FF7A29'   # 10 快递橙
$script:DELIV     = '#2DD4BF'   # 10 送达青

# ---------- data ----------
function Get-Calc6() {
    if ($null -eq $script:CALC) {
        $p = Join-Path $script:B06TMP 'calc-b06.json'
        $script:CALC = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8) | ConvertFrom-Json
    }
    return $script:CALC
}
function D2([object]$v) { return ([double]$v).ToString('0.00') }   # 12.34
function D1([object]$v) { return ([double]$v).ToString('0.0') }    # 12.3
function D4([object]$v) { return ([double]$v).ToString('0.0000') } # 0.5880
function D0([object]$v) { return ([int]$v).ToString('N0') }        # 1,234
# laboratory value: integers lose their trailing zeros, decimals keep two places
function LabN([object]$v) {
    $d = [double]$v
    if ($d -eq [Math]::Round($d, 0)) { return ([int][Math]::Round($d, 0)).ToString() }
    return $d.ToString('0.00')
}

# tone: ,@(shell, hair, text, sub, panel, hair2)
function Tone6([string]$tone) {
    if ($tone -eq 'light') {
        return ,@($script:PAGE6, $script:HAIRL6, $script:INK6, $script:SUB6, $script:PANELL6, $script:HAIRL6b)
    }
    return ,@($script:DARK6, $script:HAIRD6, $script:PAPER6, $script:MUTED6, $script:PANELD6, $script:HAIRD6b)
}
function Tone([string]$tone) { return (Tone6 $tone) }   # short alias for gen scripts

# ---------- shared furniture ----------
$script:SERIES = 'PLAINSIGHT'
function Masthead6([string]$no, [string]$kicker, [double]$l, [double]$t, [double]$w,
                   [string]$rule, [string]$cK, [string]$cT, [int]$fsK, [int]$fsT) {
    $out = ''
    $kx = [Math]::Max($l, ($l + $w - 620))
    $kw = [Math]::Min(620, ($l + $w - $kx))
    $out += Ts ('mh-n' + $no) $l $t 340 ($fsK * 1.8) ($script:SERIES + '  ' + [char]0x2014 + '  ' + $no + ' / 10') $fsK $script:MONO $cK 'LEFT' ''
    $out += Ts ('mh-k' + $no) $kx $t $kw ($fsK * 1.8) $kicker $fsK $script:SANS $cT 'RIGHT' ''
    $yt = $t + $fsK * 2.0
    $out += HR $l $yt $w 2 $rule
    return ,@($out, ($yt + 10))
}

function Foot6([string]$no, [string]$s, [double]$l, [double]$t, [double]$w,
               [string]$rule, [string]$c) {
    $out = HR $l $t $w 1 $rule
    $out += Ts ('ft' + $no) $l ($t + 10) $w 30 $s 17 $script:SANS $c 'LEFT' ''
    return $out
}

function Src6([string]$no, [string]$s, [double]$l, [double]$t, [double]$w,
              [string]$rule, [string]$c) {
    $out = HR $l $t $w 1 $rule
    $out += Ts ('src' + $no) $l ($t + 9) $w 28 $s 16 $script:SANS $c 'LEFT' ''
    return $out
}

# legend row: array of @{ c = color ; t = label } laid out left to right
function Legend6([double]$l, [double]$t, [object]$items, [int]$fs, [string]$fg, [string]$fam, [double]$pitch = 0) {
    $o = ''; $x = $l
    foreach ($it in $items) {
        $o += Box $x ($t + 4) 14 14 ([string]$it.c) 3
        $lw = [double](TW ([string]$it.t) $fs)
        $o += Ts ('lg-' + [string]$it.t) ($x + 22) $t ($lw + 6) ($fs * 1.7) ([string]$it.t) $fs $fam $fg 'LEFT' ''
        $step = 22 + $lw + 18
        if ($pitch -gt 0) { $step = $pitch }
        $x += $step
    }
    return ,@($o, $x)
}

# numbered step badge + text (used to expose ordered procedure)
function Step6([double]$x, [double]$y, [double]$dd, [int]$n, [string]$bg, [string]$fg) {
    $o = Circ $x $y $dd $bg ''
    $o += Ts ('st' + $n.ToString()) $x $y $dd $dd $n.ToString() ([int]($dd * 0.56)) $script:DISP $fg 'CENTER' ''
    return $o
}

# ---------- geometry devices ----------
# bar pivoting at (cx,cy); deg measured from +x, clockwise (screen coords)
function Hand6([double]$cx, [double]$cy, [double]$len, [double]$th, [double]$deg, [string]$c) {
    $rad = $deg * [Math]::PI / 180.0
    $mx = $cx + ($len / 2.0) * [Math]::Cos($rad)
    $my = $cy + ($len / 2.0) * [Math]::Sin($rad)
    $bl = $mx - ($len / 2.0)
    $bt = $my - ($th / 2.0)
    return (Rotate $bl $bt $len $th $deg (C $len $th $c 0))
}

# solid pie wedge built from thin radiating bars (proven Rotate + C only)
function Wedge6([double]$cx, [double]$cy, [double]$rr, [double]$a0, [double]$a1, [string]$c, [int]$n) {
    $span = [Math]::Abs($a1 - $a0)
    if ($n -lt 3) { $n = 3 }
    $arc = $span * [Math]::PI / 180.0 * $rr
    $th = [Math]::Max(2.0, ($arc / ($n - 1)) * 1.7)
    $o = ''
    for ($i = 0; $i -lt $n; $i++) {
        $a = $a0 + ($a1 - $a0) * ($i / [double]($n - 1))
        $o += (Hand6 $cx $cy $rr $th $a $c)
    }
    return $o
}

# run of dots along an arc; deg from +x, clockwise
function Arc6([double]$cx, [double]$cy, [double]$rr, [double]$a0, [double]$a1,
              [int]$n, [double]$dd, [string]$c) {
    $o = ''
    if ($n -lt 1) { return $o }
    for ($i = 0; $i -lt $n; $i++) {
        $f = 0.5
        if ($n -gt 1) { $f = $i / [double]($n - 1) }
        $a = ($a0 + (($a1 - $a0) * $f)) * [Math]::PI / 180.0
        $x = ($cx + $rr * [Math]::Cos($a)) - ($dd / 2.0)
        $y = ($cy + $rr * [Math]::Sin($a)) - ($dd / 2.0)
        $o += (Circ $x $y $dd $c '')
    }
    return $o
}

# diagonal hatch confined to a rounded rect.
# Bars are laid out in the INNER Stack's local coordinates (ClipR's Positioned moves
# the origin to l,t) and the whole group is clipped, so the corners stay covered and
# nothing spills past the box. A bar's vertical extent at 45deg is exactly its length
# times sin45, so length (h+2)*sqrt2 guarantees it crosses the full band.
function Hatch6([double]$l, [double]$t, [double]$w, [double]$h, [int]$rad,
                [string]$c, [double]$pitch, [double]$thick) {
    if ($pitch -le 0) { $pitch = 14.0 }
    if ($thick -le 0) { $thick = 3.0 }
    if ($w -le 4 -or $h -le 4) { return '' }
    $rt = 0.70710678
    $barLen = ($h + 2.0) / $rt
    $halfSpan = (($barLen / 2.0) + ($thick / 2.0)) * $rt
    $bars = ''
    $yc = $h / 2.0
    $xc = -$halfSpan
    $guard = 0
    while ($xc -le ($w + $halfSpan)) {
        $bars += (Rotate ($xc - ($barLen / 2.0)) ($yc - ($thick / 2.0)) $barLen $thick 45 (C $barLen $thick $c 0))
        $xc += $pitch
        $guard++
        if ($guard -gt 600) { break }
    }
    if ($bars -eq '') { return '' }
    return (ClipR $l $t $w $h $rad ('<Stack clipBehavior="NONE">' + $bars + '</Stack>'))
}

# minute-of-window -> degrees on a dial whose full circle = $windowMin
function Dial-Map([double]$minute, [double]$windowMin) {
    return (-90.0 + (360.0 * $minute / $windowMin))
}

# horizontal scale: track + reference band + ticks + a value pin
function Ruler6([string]$id, [double]$l, [double]$t, [double]$w, [double]$lo, [double]$hi,
                [double]$step, [double]$bandLo, [double]$bandHi, [double]$val,
                [string]$cTrack, [string]$cBand, [string]$cTick, [string]$cVal,
                [double]$trackH, [double]$tickH) {
    $o = ''
    $span = $hi - $lo
    if ($span -le 0) { Fail "$id ruler span must be > 0"; return $o }
    $bx = $l + ($w * (($bandLo - $lo) / $span))
    $bw = $w * (($bandHi - $bandLo) / $span)
    $o += Box $l $t $w $trackH $cTrack ([int]$trackH)
    $o += Box $bx $t $bw $trackH $cBand 0
    $steps = [int][Math]::Round($span / $step)
    if ($steps -lt 1) { $steps = 1 }
    for ($i = 0; $i -le $steps; $i++) {
        $x = $l + ($w * ($i / [double]$steps))
        $maj = ($i % 2 -eq 0)
        $hh = $tickH
        if ($maj) { $hh = $tickH * 1.55 }
        $o += Box ($x - 1) ($t + $trackH) 1 $hh $cTick 0
    }
    $vx = $l + ($w * (($val - $lo) / $span))
    $o += Box ($vx - 2.5) ($t - 9) 5 ($trackH + $tickH * 1.55 + 18) $cVal 0
    $o += Circ ($vx - 9) ($t - 27) 18 $cVal ''
    return ,@($o, $vx)
}

# 10x10 probability field; fills the first $filled cells
function Pct100([double]$l, [double]$t, [double]$size, [int]$filled, [string]$cFill,
                [string]$cEmpty, [double]$gap, [int]$rad) {
    $o = ''
    $cell = ($size - ($gap * 9)) / 10.0
    for ($r = 0; $r -lt 10; $r++) {
        for ($k = 0; $k -lt 10; $k++) {
            $idx = ($r * 10) + $k
            $c = $cEmpty
            if ($idx -lt $filled) { $c = $cFill }
            $x = $l + ($k * ($cell + $gap))
            $y = $t + ($r * ($cell + $gap))
            $o += Box $x $y $cell $cell $c $rad
        }
    }
    return $o
}

# vertical column split into stacked blocks (shares of $total)
function ColStack6([double]$x, [double]$baseY, [double]$w, [double]$totalH, [object]$parts, [double]$total, [double]$gap) {
    $o = ''; $y = $baseY
    foreach ($p in $parts) {
        $hh = $totalH * ([double]$p.v / $total)
        $y -= $hh
        $o += Box $x $y $w $hh ([string]$p.c) 0
        if ($gap -gt 0) { $y -= $gap }
    }
    return ,@($o, $y)
}

# horizontal waterfall: each step is a bar floating at its running value
# items: @{ amt = ; running = ; kind = 'start'|'fixed'|'dispute'|'end' }
function Waterfall6([string]$id, [object]$items, [double]$l, [double]$t, [double]$w, [double]$h,
                    [double]$maxV, [double]$minV, [string]$cStart, [string]$cFix, [string]$cDisp,
                    [string]$cEnd, [double]$barW, [double]$gapX, [string]$cConn) {
    $o = ''
    $arr = @($items)
    $n = $arr.Count
    if ($n -lt 2) { return $o }
    $slot = ($w - (($n - 1) * $gapX)) / $n
    if ($barW -gt $slot) { $barW = $slot }
    $span = $maxV - $minV
    if ($span -le 0) { return $o }
    $base = $t + $h
    for ($i = 0; $i -lt $n; $i++) {
        $it = $arr[$i]
        $kind = [string]$it.kind
        $c = $cStart
        if ($kind -eq 'fixed') { $c = $cFix }
        if ($kind -eq 'dispute') { $c = $cDisp }
        if ($kind -eq 'end') { $c = $cEnd }
        $x = $l + ($i * ($slot + $gapX)) + (($slot - $barW) / 2.0)
        $runV = [double]$it.running
        if ($kind -eq 'start' -or $kind -eq 'end') {
            $top = $base - ($h * (($runV - $minV) / $span))
            $o += Box $x $top $barW ($base - $top) $c 4
        } else {
            $loV = $runV - [double]$it.amt
            $hiV = $runV
            if ($loV -gt $hiV) { $tv = $loV; $loV = $hiV; $hiV = $tv }
            $top = $base - ($h * (($hiV - $minV) / $span))
            $bot = $base - ($h * (($loV - $minV) / $span))
            $hh = $bot - $top
            if ($hh -lt 5) { $hh = 5; $top = $bot - 5 }
            $o += Box $x $top $barW $hh $c 3
        }
        # connector at the running level reached after this step
        if ($i -lt ($n - 1)) {
            $nx = $l + (($i + 1) * ($slot + $gapX)) + (($slot - $barW) / 2.0)
            $cy = $base - ($h * (($runV - $minV) / $span))
            $o += DashH $x $cy (($nx + $barW) - $x) 2 $cConn 7 5
        }
    }
    return $o
}

# ---------- page assembly ----------
function Page6([int]$w, [int]$h, [string]$bg, [string]$inner) {
    return '<Snapshot type="png" background="' + $bg + '">' +
           '<Container width="' + $w.ToString() + '" height="' + $h.ToString() + '" color="' + $bg + '">' +
           '<Stack clipBehavior="NONE">' + $inner + '</Stack></Container></Snapshot>'
}
function Write-Dsl6([string]$path, [string]$body) {
    $dir = Split-Path $path -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [IO.File]::WriteAllText($path, $body.Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
}
function Report-Problems6() {
    if ($script:PROBLEMS.Count -eq 0) { Write-Output 'problems = 0' }
    else { $script:PROBLEMS | ForEach-Object { Write-Output $_ } }
}
