# lib-b03.ps1 -- DSL helpers for B03 (DSL creative frontier, 10 works)
# Dot-source this file. Reuses the tested helpers from lib-b01.ps1.
$ErrorActionPreference = 'Stop'

$script:B03ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$script:B03OUT  = Join-Path $script:B03ROOT 'outputs\run-20261002-220723-mimo\B03'
$script:B03TMP  = Join-Path $script:B03ROOT 'tmp\run-20261002-220723-mimo\B03'

. (Join-Path $script:B03ROOT 'tmp\run-20261002-220723-mimo\B01\lib-b01.ps1')

# re-point the shared globals at B03
$script:FAM = 'Noto Sans CJK SC'
$script:OUT = $script:B03OUT
$script:PROBLEMS.Clear()
$script:SEG.Clear()
$script:CURRENT = 'none'

$script:SANS = 'Noto Sans CJK SC'
$script:SERIF = 'Noto Serif CJK SC'
$script:MONO = 'Noto Sans Mono CJK SC'
$script:DISP = 'Inter Black'
$script:BODY = 'Inter'

# ---------- generic wrappers ----------
function P([double]$l, [double]$t, [double]$w, [double]$h, [string]$inner) {
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) +
           '" height="' + (Fmt $h) + '">' + $inner + '</Positioned>'
}

# text with a full attribute bag (ordered dictionary keeps DSL order stable)
function TX([object]$attrs, [string]$s) {
    $out = '<Text'
    foreach ($k in $attrs.Keys) { $out += ' ' + $k + '="' + [string]$attrs[$k] + '"' }
    $out += '>' + (E $s) + '</Text>'
    return $out
}

function TXW([string]$id, [double]$l, [double]$t, [double]$w, [double]$h, [string]$s, [int]$fs,
             [string]$fam, [string]$c, [string]$extra) {
    Fit $id $s $w $fs ('TXW@' + (Fmt $l) + ',' + (Fmt $t)) | Out-Null
    $a = [ordered]@{ fontSize = $fs; fontFamily = $fam; color = $c }
    foreach ($pair in ($extra -split ';')) {
        if ($pair.Trim() -eq '') { continue }
        $kv = $pair.Split('=')
        $a[$kv[0].Trim()] = $kv[1].Trim()
    }
    return (P $l $t $w $h (TX $a $s))
}

# unguarded (chip / decorative text where Fit would be too strict)
function TXU([double]$l, [double]$t, [double]$w, [double]$h, [string]$s, [int]$fs,
             [string]$fam, [string]$c, [string]$extra) {
    $a = [ordered]@{ fontSize = $fs; fontFamily = $fam; color = $c }
    if ($extra -ne '') {
        foreach ($pair in ($extra -split ';')) {
            if ($pair.Trim() -eq '') { continue }
            $kv = $pair.Split('=')
            $a[$kv[0].Trim()] = $kv[1].Trim()
        }
    }
    return (P $l $t $w $h (TX $a $s))
}

# ---------- shapes ----------
function Circ([double]$l, [double]$t, [double]$d, [string]$c, [string]$b) {
    $a = [ordered]@{ width = (Fmt $d); height = (Fmt $d); shape = 'CIRCLE' }
    if ($c -ne '' -and $c -ne $null) { $a.color = $c }
    if ($b -ne '' -and $b -ne $null) { $a.border = $b }
    $s = '<Container'
    foreach ($k in $a.Keys) { $s += ' ' + $k + '="' + [string]$a[$k] + '"' }
    $s += '/>'
    return (P $l $t $d $d $s)
}

function Grad([double]$l, [double]$t, [double]$w, [double]$h, [string]$type, [string]$colors,
              [string]$stops, [string]$extra) {
    $s = '<Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" gradientType="' + $type +
         '" gradientColors="' + $colors + '"'
    if ($stops -ne '') { $s += ' gradientStops="' + $stops + '"' }
    if ($extra -ne '') { $s += ' ' + $extra }
    $s += '/>'
    return (P $l $t $w $h $s)
}

# ---------- effect wrappers ----------
function CTint([double]$l, [double]$t, [double]$w, [double]$h, [string]$color, [string]$mode, [string]$inner) {
    return (P $l $t $w $h ('<ColorFiltered color="' + $color + '" blendMode="' + $mode + '">' + $inner + '</ColorFiltered>'))
}

function IBlur([double]$l, [double]$t, [double]$w, [double]$h, [double]$sx, [double]$sy, [string]$inner) {
    return (P $l $t $w $h ('<ImageFiltered sigmaX="' + (Fmt $sx) + '" sigmaY="' + (Fmt $sy) + '">' + $inner + '</ImageFiltered>'))
}

function Glass([double]$l, [double]$t, [double]$w, [double]$h, [int]$r, [double]$sig,
               [string]$tint, [string]$innerTint) {
    $inner = '<ClipRRect borderRadius="' + $r.ToString() + '">' +
             '<Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" color="' + $tint + '">' +
             '<BackdropFilter sigmaX="' + (Fmt $sig) + '" sigmaY="' + (Fmt $sig) + '">' +
             '<Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" color="' + $innerTint + '"/>' +
             '</BackdropFilter></Container></ClipRRect>'
    return (P $l $t $w $h $inner)
}

# CORRECT frost (probes p14-p18): the clip must wrap BackdropFilter directly -
# any Container(color) in between kills the backdrop read - and only the FIRST
# BackdropFilter in a document reads the full backdrop.
function Frost([double]$l, [double]$t, [double]$w, [double]$h, [int]$r, [double]$sig,
               [string]$tint) {
    $inner = '<ClipRRect borderRadius="' + $r.ToString() + '">' +
             '<BackdropFilter sigmaX="' + (Fmt $sig) + '" sigmaY="' + (Fmt $sig) + '">' +
             '<Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" color="' + $tint + '"/>' +
             '</BackdropFilter></ClipRRect>'
    return (P $l $t $w $h $inner)
}

function ClipAt([double]$l, [double]$t, [double]$w, [double]$h, [string]$inner) {
    return (P $l $t $w $h ('<ClipRect>' + $inner + '</ClipRect>'))
}

# oversized content anchored inside a fixed box, clipped at the box edge
function Bleed([double]$l, [double]$t, [double]$w, [double]$h, [string]$align, [string]$inner) {
    $x = '<ClipRect><SizedOverflowBox width="' + (Fmt $w) + '" height="' + (Fmt $h) +
         '" alignment="' + $align + '">' + $inner + '</SizedOverflowBox></ClipRect>'
    return (P $l $t $w $h $x)
}

# ---------- inline widgets (Text children) ----------
function Chip([string]$txt, [int]$fs, [string]$bg, [string]$fg, [int]$padX, [int]$h, [string]$fam, [int]$radius) {
    $w = [int][Math]::Ceiling((TW $txt $fs) + ($padX * 2))
    $inner = '<Container width="' + $w.ToString() + '" height="' + $h.ToString() + '" color="' + $bg +
             '" borderRadius="' + $radius.ToString() + '" alignment="CENTER">' +
             '<Text fontSize="' + $fs.ToString() + '" fontFamily="' + $fam + '" color="' + $fg +
             '" maxLines="1">' + (E $txt) + '</Text></Container>'
    return '<WidgetSpan alignment="MIDDLE">' + $inner + '</WidgetSpan>'
}

function RW([string]$s) { return '<Raw>' + (E $s) + '</Raw>' }

# ---------- isometric projection (case-10) ----------
# screen: x = (u - v) * K * UNIT + X0 ; y = (u + v) * 0.5 * UNIT - w * UNIT + Y0
# The matrix coefficients are unit-independent: local pixels map 1 UNIT per grid step.
$script:ISOK = 0.8660254037844386
$script:ISOH = 0.5

function IsoM([double]$a, [double]$b, [double]$c, [double]$d, [double]$tx, [double]$ty) {
    $f = [System.Globalization.CultureInfo]::InvariantCulture
    $n = @($a, $b, 0.0, 0.0, $c, $d, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, $tx, $ty, 0.0, 1.0)
    $parts = @()
    foreach ($v in $n) {
        if ($v -eq 0.0) { $parts += '0' }
        elseif ($v -eq 1.0) { $parts += '1' }
        else { $parts += ([Math]::Round($v, 6)).ToString('0.######', $f) }
    }
    return '(' + ($parts -join ',') + ')'
}

# top face of a UNIT x UNIT footprint at (u0,v0), top surface at height wTop (grid units)
function IsoTop([double]$u0, [double]$v0, [double]$wTop, [double]$unit, [double]$X0, [double]$Y0,
                [string]$color, [string]$border) {
    $K = $script:ISOK; $H = $script:ISOH
    $tx = ($u0 - $v0) * $K * $unit + $X0
    $ty = ($u0 + $v0) * $H * $unit - $wTop * $unit + $Y0
    # NO translation here: the Positioned above already carries (tx,ty). Putting it
    # in the matrix too drew everything at 2*(tx,ty). Verified with probe p10.
    $m = IsoM $K $H (-$K) $H 0.0 0.0
    $a = [ordered]@{ width = (Fmt $unit); height = (Fmt $unit); color = $color }
    if ($border -ne '') { $a.border = $border }
    $c = '<Container'
    foreach ($kk in $a.Keys) { $c += ' ' + $kk + '="' + [string]$a[$kk] + '"' }
    $c += '/>'
    return (P $tx $ty $unit $unit ('<Transform matrix="' + $m + '">' + $c + '</Transform>'))
}

# front-left face (edge at v = v0+1), from height wTop down to the ground
function IsoLeft([double]$u0, [double]$v0, [double]$wTop, [double]$unit, [double]$X0, [double]$Y0,
                 [string]$color) {
    $K = $script:ISOK; $H = $script:ISOH
    $hpx = [Math]::Max(1.0, $wTop * $unit)
    $tx = ($u0 - ($v0 + 1)) * $K * $unit + $X0
    $ty = ($u0 + $v0 + 1) * $H * $unit - $wTop * $unit + $Y0
    $m = IsoM $K $H 0.0 1.0 0.0 0.0
    $c = '<Container width="' + (Fmt $unit) + '" height="' + (Fmt $hpx) + '" color="' + $color + '"/>'
    return (P $tx $ty $unit $hpx ('<Transform matrix="' + $m + '">' + $c + '</Transform>'))
}

# front-right face (edge at u = u0+1), from height wTop down to the ground
function IsoRight([double]$u0, [double]$v0, [double]$wTop, [double]$unit, [double]$X0, [double]$Y0,
                  [string]$color) {
    $K = $script:ISOK; $H = $script:ISOH
    $hpx = [Math]::Max(1.0, $wTop * $unit)
    $tx = (($u0 + 1) - $v0) * $K * $unit + $X0
    $ty = ($u0 + 1 + $v0) * $H * $unit - $wTop * $unit + $Y0
    $m = IsoM (-$K) $H 0.0 1.0 0.0 0.0
    $c = '<Container width="' + (Fmt $unit) + '" height="' + (Fmt $hpx) + '" color="' + $color + '"/>'
    return (P $tx $ty $unit $hpx ('<Transform matrix="' + $m + '">' + $c + '</Transform>'))
}

# ---------- page assembly ----------
function Page([int]$w, [int]$h, [string]$bg, [string]$inner) {
    return '<Snapshot type="png" background="' + $bg + '">' +
           '<Container width="' + $w.ToString() + '" height="' + $h.ToString() + '" color="' + $bg + '">' +
           '<Stack clipBehavior="NONE">' + $inner + '</Stack></Container></Snapshot>'
}

function Write-Dsl([string]$path, [string]$body) {
    $dir = Split-Path $path -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [IO.File]::WriteAllText($path, $body.Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
}

function Report-Problems() {
    if ($script:PROBLEMS.Count -eq 0) { Write-Output 'problems = 0' }
    else { $script:PROBLEMS | ForEach-Object { Write-Output $_ } }
}
