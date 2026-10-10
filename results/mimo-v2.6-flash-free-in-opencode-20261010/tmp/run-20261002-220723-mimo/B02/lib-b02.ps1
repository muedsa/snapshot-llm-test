# lib-b02.ps1 -- shared DSL helpers for B02 (one client, ten touchpoints)
# Reuses the proven B01 helper library (Fit/width estimator/TLines/matrix) by dot-sourcing,
# then re-points the output/temp roots at B02 and adds the design-system components.
# PS 5.1: no ??, no ternary, always parenthesize arithmetic.
$ErrorActionPreference = 'Stop'

$script:B02ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $script:B02ROOT 'tmp\run-20261002-220723-mimo\B01\lib-b01.ps1')

# Finish-Case writes into $script:B01OUT / $script:B01TMP; re-point them at B02.
$script:B01OUT = Join-Path $script:B02ROOT 'outputs\run-20261002-220723-mimo\B02'
$script:B01TMP = Join-Path $script:B02ROOT 'tmp\run-20261002-220723-mimo\B02'

# ---------- palette (design-system.json) ----------
$script:DEEP  = '#0B3B3A'
$script:INK   = '#082C2B'
$script:TIDE  = '#7FB2A8'
$script:GULL  = '#E8EDE9'
$script:SAND  = '#D9CBA8'
$script:SUN   = '#E4622C'
$script:NIGHT = '#132A44'
$script:PAPER = '#F6F2E8'
$script:LINE_D = '#7FB2A855'
$script:LINE_L = '#0B3B3A33'
$script:DEMO  = '演示数据 DEMO'
$script:ADDR  = '候鸟湾湿地公园北门 · 望潮路 128 号'
$script:HOURS = '每日 06:00-18:00 免费开放'

# ---------- design-system components ----------

# Mark: 5 dots + 4 slanted segments forming a 人字 bird formation.
# $s = overall width; dots scale linearly so the mark works at 24px and 300px.
function Mark([double]$l, [double]$t, [double]$s, [string]$color, [string]$ring, [string]$bg) {
    $out = ''
    $dot = [Math]::Max(3.0, $s * 0.13)
    $th  = [Math]::Max(2.0, $s * 0.045)
    $pts = @(
        @(0.50, 0.16),
        @(0.30, 0.42), @(0.09, 0.70),
        @(0.70, 0.42), @(0.91, 0.70)
    )
    $segs = @(@(0,1), @(1,2), @(0,3), @(3,4))
    foreach ($sg in $segs) {
        $p1 = $pts[$sg[0]]; $p2 = $pts[$sg[1]]
        $x1 = $p1[0] * $s; $y1 = $p1[1] * $s
        $x2 = $p2[0] * $s; $y2 = $p2[1] * $s
        $len = [Math]::Sqrt(($x2 - $x1) * ($x2 - $x1) + ($y2 - $y1) * ($y2 - $y1))
        $ang = [Math]::Atan2(($y2 - $y1), ($x2 - $x1)) * 180.0 / [Math]::PI
        $cx = ($x1 + $x2) / 2.0; $cy = ($y1 + $y2) / 2.0
        $out += Rotate ($l + $cx - $len / 2.0) ($t + $cy - $th / 2.0) $len $th $ang (C $len $th $color 0)
    }
    foreach ($p in $pts) {
        $cx = $p[0] * $s; $cy = $p[1] * $s
        $out += Circle ($l + $cx - $dot / 2.0) ($t + $cy - $dot / 2.0) $dot $color $null
    }
    if ($null -ne $ring -and $ring -ne '') {
        $d = $s * 0.20
        $out += Circle ($l + $s * 0.95 - $d / 2.0) ($t + $s * 0.90 - $d / 2.0) $d $ring $null
        $d2 = $d - [Math]::Max(3.0, $s * 0.05)
        $out += Circle ($l + $s * 0.95 - $d2 / 2.0) ($t + $s * 0.90 - $d2 / 2.0) $d2 $bg $null
    }
    return $out
}

# Eyebrow: uppercase latin label with a small chinese note under it
function Eyebrow([string]$id, [double]$l, [double]$t, [double]$w, [string]$en, [string]$zh, [int]$fs, [string]$cEn, [string]$cZh) {
    $out = T ($id + '-en') $l $t $w ($fs * 1.5) $en $fs $cEn 'LEFT' 'BOLD'
    if ($null -ne $zh -and $zh -ne '') {
        $out += T ($id + '-zh') $l ($t + $fs * 1.75) $w ($fs * 1.4) $zh ([int][Math]::Round($fs * 0.72)) $cZh 'LEFT' ''
    }
    return $out
}

# RuleBand: 1px main rule, 5px gap, 2px sub rule
function RuleBand([double]$l, [double]$t, [double]$w, [string]$c1, [string]$c2) {
    return (Box $l $t $w 1 $c1 0) + (Box $l ($t + 6.0) $w 2 $c2 0)
}

# StatChip: label / big number / unit note, left aligned on one baseline beat
function StatChip([string]$id, [double]$l, [double]$t, [double]$w, [string]$label, [string]$value, [string]$unit,
                  [int]$fs, [string]$cLabel, [string]$cValue, [string]$cUnit) {
    $h1 = [Math]::Round($fs * 1.35, 0)
    $fsV = [int][Math]::Round($fs * 2.2, 0)
    $h2 = [Math]::Round($fsV * 1.2, 0)
    $out = T ($id + '-l') $l $t $w $h1 $label $fs $cLabel 'LEFT' 'BOLD'
    $out += T ($id + '-v') $l ($t + $h1 + 4) $w $h2 $value $fsV $cValue 'LEFT' 'BOLD'
    if ($null -ne $unit -and $unit -ne '') {
        $out += T ($id + '-u') $l ($t + $h1 + 4 + $h2 + 2) $w ($fs * 1.5) $unit $fs $cUnit 'LEFT' ''
    }
    return $out
}

# SpeciesRow: colour dot + chinese name + latin + right-aligned count
function SpeciesRow([string]$id, [double]$l, [double]$t, [double]$w, [string]$name, [string]$latin, [string]$cnt,
                    [string]$dotColor, [string]$cName, [string]$cLatin, [string]$cCnt, [int]$fs, [double]$rowH) {
    $d = [Math]::Round($fs * 0.62, 0)
    $out = Circle ($l + 1) ($t + ($rowH - $d) / 2.0) $d $dotColor $null
    $nameW = $w * 0.34
    $latW  = $w * 0.44
    $out += T ($id + '-n') ($l + $d + 12) $t $nameW $rowH $name $fs $cName 'LEFT' 'BOLD'
    $out += T ($id + '-la') ($l + $d + 12 + $nameW) $t $latW $rowH $latin ([int][Math]::Round($fs * 0.86, 0)) $cLatin 'LEFT' ''
    $out += T ($id + '-c') ($l + $w - 90) $t 90 $rowH $cnt $fs $cCnt 'RIGHT' 'BOLD'
    return $out
}

# NumChip: square with a white index number
function NumChip([double]$l, [double]$t, [double]$size, [string]$n, [string]$bg, [string]$fg, [int]$rad) {
    $fs = [int][Math]::Round($size * 0.46, 0)
    return (Box $l $t $size $size $bg $rad) +
           (Txt $l ($t + ($size - $fs * 1.15) / 2.0) $size ($fs * 1.2) $n $fs $fg 'CENTER' 'BOLD')
}

# FooterLine: station address + hours + DEMO marker (or a caller-supplied short string)
function FooterLine([string]$id, [double]$l, [double]$t, [double]$w, [string]$align, [string]$c, [int]$fs, [string]$text) {
    if ($null -eq $text -or $text -eq '') { $text = $script:ADDR + '  ·  ' + $script:HOURS + '  ·  ' + $script:DEMO }
    return (T ($id + '-f') $l $t $w ($fs * 1.7) $text $fs $c $align '')
}

# Chip: pill whose width is derived from the text width
function Chip([string]$id, [double]$l, [double]$t, [string]$text, [string]$bg, [string]$fg, [int]$fs, [double]$pad, [int]$rad) {
    $w = [Math]::Ceiling((TW $text $fs) + $pad * 2)
    $h = [Math]::Ceiling($fs * 1.7)
    $out = Box $l $t $w $h $bg $rad
    $out += Txt $l ($t + ($h - $fs * 1.25) / 2.0) $w ($fs * 1.3) $text $fs $fg 'CENTER' 'BOLD'
    return ,@($out, $w, $h)
}

# DialArc: progress ring built from N rotated tick segments (fully deterministic).
# The documented SWEEP gradient was measured not to honour gradientStops/gradientStartAngle:
# with start=-pi/2, end=3pi/2 and stops 0,f,f,1 the lit arc came out as [90 deg, f*360]
# of the circle rather than [0, f*360] (measured on two independent renders, f=0.75 and
# f=0.62). Segments are drawn OFF-first then ON on top so the boundary is exactly
# round(frac*N) segments.
function DialArc([double]$l, [double]$t, [double]$d, [double]$frac, [string]$on, [string]$off, [double]$thick, [int]$N) {
    if ($N -lt 8) { $N = 8 }
    $f = [Math]::Min(1.0, [Math]::Max(0.0, $frac))
    $onN = [int][Math]::Round($f * $N)
    $cx = $l + $d / 2.0
    $cy = $t + $d / 2.0
    $rMid = ($d - $thick) / 2.0
    $step = 360.0 / $N
    $arcLen = (2.0 * [Math]::PI * $rMid) / $N * 1.28
    $inv = [System.Globalization.CultureInfo]::InvariantCulture
    $out = ''
    $pts = New-Object System.Collections.Generic.List[object]
    for ($i = 0; $i -lt $N; $i++) {
        $A = $i * $step
        $rad = $A * [Math]::PI / 180.0
        $px = $cx + $rMid * [Math]::Sin($rad)
        $py = $cy - $rMid * [Math]::Cos($rad)
        $pts.Add([pscustomobject]@{ x = $px - $thick / 2.0; y = $py - $arcLen / 2.0; a = $A - 90.0 })
    }
    for ($i = $onN; $i -lt $N; $i++) { $p = $pts[$i]; $out += Rotate $p.x $p.y $thick $arcLen $p.a (C $thick $arcLen $off 0) }
    for ($i = 0; $i -lt $onN; $i++) { $p = $pts[$i]; $out += Rotate $p.x $p.y $thick $arcLen $p.a (C $thick $arcLen $on 0) }
    return $out
}

# Section heading = eyebrow-free block title with a leading tick
function SectionTitle([string]$id, [double]$l, [double]$t, [double]$w, [string]$s, [int]$fs, [string]$cTick, [string]$cText) {
    $out = Box $l ($t + 4) 6 ($fs * 1.05) $cTick 2
    $out += T ($id + '-st') ($l + 16) $t ($w - 16) ($fs * 1.4) $s $fs $cText 'LEFT' 'BOLD'
    return $out
}

function B02-Dims([int]$w, [int]$h) { return [Math]::Max(40.0, [Math]::Round([Math]::Min($w, $h) * 0.06, 0)) }
