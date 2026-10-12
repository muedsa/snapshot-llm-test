# lib-b01.ps1 -- shared DSL helpers for the B01 open-creation portfolio
# Dot-source this file. PS 5.1: no ??, no ternary, always parenthesize arithmetic,
# function names must not start with "r" (alias for Invoke-History).
$ErrorActionPreference = 'Stop'

$script:B01ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$script:B01OUT  = Join-Path $B01ROOT 'outputs\run-20261002-220723-mimo\B01'
$script:B01TMP  = Join-Path $B01ROOT 'tmp\run-20261002-220723-mimo\B01'
$script:FAM     = 'Noto Sans CJK SC'

$script:PROBLEMS = New-Object System.Collections.Generic.List[string]
$script:SEG      = New-Object System.Collections.Generic.List[string]
$script:CURRENT  = 'none'

function Use-Case([string]$id) { $script:CURRENT = $id }

function Fail([string]$msg) {
    $script:PROBLEMS.Add("[$($script:CURRENT)] $msg")
}

function Fmt([double]$v) {
    if ($v -eq [Math]::Round($v, 0)) { return ([int][Math]::Round($v,0)).ToString() }
    return $v.ToString('0.##', [System.Globalization.CultureInfo]::InvariantCulture)
}

function E([string]$s) {
    if ($null -eq $s) { return '' }
    return $s.Replace('&','&amp;').Replace('<','&lt;').Replace('>','&gt;')
}

# ---------- width estimator ----------
# code-point ranges (case-sensitive by construction; never use -match here:
# PowerShell -match is case-insensitive by default and would map a-z to A-Z widths)
function TW([string]$s, [int]$fs) {
    if ($null -eq $s) { return 0.0 }
    $w = 0.0
    foreach ($ch in $s.ToCharArray()) {
        $c = [int][char]$ch
        if     ($c -eq 0x2192 -or $c -eq 0x2190 -or $c -eq 0x2194) { $w += 1.00 }   # arrows
        elseif ($c -eq 0x2192) { $w += 1.00 }
        elseif ($c -eq 0x2013 -or $c -eq 0x2014) { $w += 0.55 }   # en/em dash
        elseif ($c -eq 0x00B7 -or $c -eq 0x2022) { $w += 0.35 }   # middle dot / bullet
        elseif ($c -eq 0x00B0) { $w += 0.45 }                      # degree
        elseif ($c -eq 0x00D7) { $w += 0.60 }                      # multiply
        elseif ($c -eq 0x00B1) { $w += 0.65 }                      # plus-minus
        elseif ($c -eq 0x2248) { $w += 0.70 }                      # almost equal
        elseif ($c -ge 0x2E80) { $w += 1.00 }                      # CJK + fullwidth + CJK punct
        elseif ($c -ge 0xFF01) { $w += 1.00 }                      # fullwidth forms
        elseif ($c -ge 65 -and $c -le 90)  { $w += 0.70 }          # A-Z
        elseif ($c -ge 97 -and $c -le 122) { $w += 0.56 }          # a-z
        elseif ($c -ge 48 -and $c -le 57)  { $w += 0.60 }          # 0-9
        elseif ($ch -eq ' ')  { $w += 0.30 }
        elseif ($ch -eq ',' -or $ch -eq ':' -or $ch -eq '.' -or $ch -eq '/' -or $ch -eq '\' -or $ch -eq '|' -or $ch -eq '!' -or $ch -eq '?' -or $ch -eq "'" -or $ch -eq '"') { $w += 0.30 }
        elseif ($ch -eq '-')  { $w += 0.40 }
        elseif ($ch -eq '(' -or $ch -eq ')' -or $ch -eq '[' -or $ch -eq ']' -or $ch -eq '{' -or $ch -eq '}' -or $ch -eq '<' -or $ch -eq '>') { $w += 0.35 }
        elseif ($ch -eq '=' -or $ch -eq '+' -or $ch -eq '*' -or $ch -eq '~' -or $ch -eq '_' -or $ch -eq '#' -or $ch -eq '&amp;' -or $ch -eq '@' -or $ch -eq '%' -or $ch -eq '^' -or $ch -eq '$') { $w += 0.55 }
        else { $w += 0.55 }
    }
    return $w * $fs
}

function Fit([string]$id, [string]$s, [double]$w, [int]$fs, [string]$where) {
    $need = (TW $s $fs) * 1.02
    if ($need -gt $w) {
        Fail "$id text too wide in ${where}: need $([int][Math]::Ceiling($need)) > box $([int]$w)  fs=$fs  `"$s`""
    }
    return $need
}

function MaxTW([object]$arr, [int]$fs) {
    $m = 0.0
    foreach ($x in $arr) { $v = (TW ([string]$x) $fs); if ($v -gt $m) { $m = $v } }
    return $m
}

# naive but reliable CJK-aware wrap to a pixel width
function WrapTW([string]$s, [double]$maxW, [int]$fs) {
    $lines = New-Object System.Collections.Generic.List[string]
    if ([string]::IsNullOrEmpty($s)) { $lines.Add(''); return ,$lines }
    $buf = ''
    foreach ($ch in $s.ToCharArray()) {
        $t = $buf + [string]$ch
        if ((TW $t $fs) -gt $maxW -and $buf -ne '') { $lines.Add($buf); $buf = [string]$ch }
        else { $buf = $t }
    }
    if ($buf -ne '') { $lines.Add($buf) }
    return ,$lines
}

# ---------- emitters ----------
function Seg([string]$s) { $script:SEG.Add($s) }

function Box([double]$l,[double]$t,[double]$w,[double]$h,[string]$c,[int]$r = 0) {
    $rr = ''; if ($r -gt 0) { $rr = ' borderRadius="' + $r.ToString() + '"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" color="' + $c + '"' + $rr + '/></Positioned>'
}

function ShadowBox([double]$l,[double]$t,[double]$w,[double]$h,[string]$c,[int]$r,[string]$sh) {
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" color="' + $c + '" borderRadius="' + $r.ToString() +
           '" boxShadow="' + $sh + '"/></Positioned>'
}

function Grad([double]$l,[double]$t,[double]$w,[double]$h,[string]$colors,[string]$type,[string]$r0,[string]$r1,[int]$rad) {
    $a = '<Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" gradientType="' + $type + '" gradientColors="' + $colors + '"'
    if ($type -eq 'LINEAR') { $a += ' gradientBegin="' + $r0 + '" gradientEnd="' + $r1 + '"' }
    if ($type -eq 'RADIAL') { $a += ' gradientCenter="' + $r0 + '" gradientRadius="' + $r1 + '"' }
    if ($rad -gt 0) { $a += ' borderRadius="' + $rad.ToString() + '"' }
    $a += '/>'
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) + '">' + $a + '</Positioned>'
}

function Circle([double]$l,[double]$t,[double]$d,[string]$c,[string]$sh) {
    $s = ''
    if ($null -ne $sh -and $sh -ne '') { $s = ' boxShadow="' + $sh + '"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $d) + '" height="' + (Fmt $d) +
           '"><Container width="' + (Fmt $d) + '" height="' + (Fmt $d) + '" shape="CIRCLE" color="' + $c + '"' + $s + '/></Positioned>'
}

function CircleGrad([double]$l,[double]$t,[double]$d,[string]$colors,[string]$type,[string]$r0,[string]$r1,[string]$sh) {
    $s = ''
    if ($null -ne $sh -and $sh -ne '') { $s = ' boxShadow="' + $sh + '"' }
    return ('<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $d) + '" height="' + (Fmt $d) +
           '"><Container width="' + (Fmt $d) + '" height="' + (Fmt $d) + '" shape="CIRCLE" gradientType="' + $type +
           '" gradientColors="' + $colors + '"' + $s)
}

# ring: outer disc with a sweep gradient, inner disc painted with the page background
function Ring([double]$l,[double]$t,[double]$d,[double]$thick,[string]$colors,[string]$bg,[string]$sh) {
    $outer = CircleGrad $l $t $d $colors 'SWEEP' '' '' $sh
    $outer += '/></Positioned>'
    $innerD = $d - 2 * $thick
    $inner = Circle ($l + $thick) ($t + $thick) $innerD $bg $null
    return $outer + $inner
}

# DialArc -- deterministic segmented progress ring (added during the B02 cross-task
# measurement pass).  The SWEEP gradient + gradientStops approach used by Ring()/RingProg()
# was measured on the real service NOT to honour gradientStops or gradientStartAngle:
# with stops 0,f,f,1 and start=-pi/2 / end=3pi/2 the lit arc came out as
# [90 deg, f*360 deg] instead of [0, f*360 deg] (f=0.75 measured 50.14% starting at
# 90 deg on B01 case-08; f=0.62 measured starting at 138 deg on B02 case-01).
# DialArc draws N rotated tick segments, OFF first then ON on top, so the boundary is
# exactly round(frac*N) segments starting at 12 o'clock.
function DialArc([double]$l,[double]$t,[double]$d,[double]$frac,[string]$on,[string]$off,[double]$thick,[int]$N) {
    if ($N -lt 8) { $N = 8 }
    $f = [Math]::Min(1.0, [Math]::Max(0.0, $frac))
    $onN = [int][Math]::Round($f * $N)
    $cx = $l + $d / 2.0
    $cy = $t + $d / 2.0
    $rMid = ($d - $thick) / 2.0
    $step = 360.0 / $N
    $arcLen = (2.0 * [Math]::PI * $rMid) / $N * 1.28
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

function Txt([double]$l,[double]$t,[double]$w,[double]$h,[string]$s,[int]$fs,[string]$c,[string]$a,[string]$boldAttr) {
    $b = ''
    if ($null -ne $boldAttr -and $boldAttr -ne '') { $b = ' fontStyle="' + $boldAttr + '"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Text fontSize="' + $fs.ToString() + '" fontFamily="' + $script:FAM + '" color="' + $c + '"' + $b +
           ' textAlign="' + $a + '" maxLines="1">' + (E $s) + '</Text></Positioned>'
}

# guarded single-line text: verifies the string fits the box
function T([string]$id,[double]$l,[double]$t,[double]$w,[double]$h,[string]$s,[int]$fs,[string]$c,[string]$a = 'LEFT',[string]$bold = '') {
    Fit $id $s $w $fs ('T@' + (Fmt $l) + ',' + (Fmt $t)) | Out-Null
    return (Txt $l $t $w $h $s $fs $c $a $bold)
}

# outlined / glowing display text
function TStroke([string]$id,[double]$l,[double]$t,[double]$w,[double]$h,[string]$s,[int]$fs,[string]$fill,[string]$stroke,[int]$sw,[string]$a = 'LEFT',[string]$shadow) {
    Fit $id $s $w $fs 'TStroke' | Out-Null
    $g = ' foregroundColor="' + $stroke + '" foregroundMode="STROKE" foregroundStrokeWidth="' + $sw.ToString() + '"'
    if ($null -ne $shadow -and $shadow -ne '') { $g += ' textShadow="' + $shadow + '"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Text fontSize="' + $fs.ToString() + '" fontFamily="' + $script:FAM + '" color="' + $fill + '"' + $g +
           ' textAlign="' + $a + '" maxLines="1">' + (E $s) + '</Text></Positioned>'
}

function TShadow([string]$id,[double]$l,[double]$t,[double]$w,[double]$h,[string]$s,[int]$fs,[string]$c,[string]$sh,[string]$a = 'LEFT',[string]$bold = '') {
    Fit $id $s $w $fs 'TShadow' | Out-Null
    $b = ''
    if ($null -ne $bold -and $bold -ne '') { $b = ' fontStyle="' + $bold + '"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Text fontSize="' + $fs.ToString() + '" fontFamily="' + $script:FAM + '" color="' + $c + '"' + $b +
           ' textShadow="' + $sh + '" textAlign="' + $a + '" maxLines="1">' + (E $s) + '</Text></Positioned>'
}

# multi-line block from an explicit array of lines
function TLines([string]$id,[double]$l,[double]$t,[double]$w,[int]$fs,[object]$lines,[double]$lineH,[string]$c,[string]$bold = '') {
    $out = ''
    $i = 0
    foreach ($ln in $lines) {
        $s = ([string]$ln)
        if ($s -ne '') {
            Fit $id $s $w $fs ('TLines#' + $i.ToString()) | Out-Null
            $out += Txt $l ($t + $i * $lineH) $w ($lineH * 0.95) $s $fs $c 'LEFT' $bold
        }
        $i++
    }
    return $out
}

# wrapped paragraph: returns DSL and the number of lines actually used
function TPara([string]$id,[double]$l,[double]$t,[double]$w,[string]$s,[int]$fs,[double]$lineH,[string]$c,[string]$bold = '') {
    $ls = WrapTW $s $w $fs
    $out = ''
    $i = 0
    foreach ($ln in $ls) {
        $out += Txt $l ($t + $i * $lineH) $w ($lineH * 0.95) $ln $fs $c 'LEFT' $bold
        $i++
    }
    return ,@($out, $i)
}

function HLine([double]$l,[double]$t,[double]$w,[double]$th,[string]$c) { return (Box $l $t $w $th $c 0) }
function VLine([double]$l,[double]$t,[double]$h,[double]$th,[string]$c) { return (Box $l $t $th $h $c 0) }

# dashed line made of small rects (the DSL has no line element)
function DashH([double]$l,[double]$t,[double]$w,[double]$th,[string]$c,[int]$seg,[int]$gap) {
    $out = ''
    $x = 0.0
    while ($x -lt $w) {
        $w2 = [Math]::Min([double]$seg, $w - $x)
        $out += Box ($l + $x) $t $w2 $th $c 0
        $x += ($seg + $gap)
    }
    return $out
}

function DashV([double]$l,[double]$t,[double]$h,[double]$th,[string]$c,[int]$seg,[int]$gap) {
    $out = ''
    $y = 0.0
    while ($y -lt $h) {
        $h2 = [Math]::Min([double]$seg, $h - $y)
        $out += Box $l ($t + $y) $th $h2 $c 0
        $y += ($seg + $gap)
    }
    return $out
}

# rotate a rectangle by degrees about its own centre (column-major 4x4, no spaces).
# $inner must be a raw widget (C / CGrad / CC ...), never a Box/Circle/T result.
function RotM([double]$l,[double]$t,[double]$w,[double]$h,[double]$deg) {
    $r = $deg * [Math]::PI / 180.0
    $cs = [Math]::Cos($r); $sn = [Math]::Sin($r)
    $cx = $w / 2.0; $cy = $h / 2.0
    $tx = $cx - ($cs * $cx - $sn * $cy)
    $ty = $cy - ($sn * $cx + $cs * $cy)
    $f = [System.Globalization.CultureInfo]::InvariantCulture
    $n = @($cs, $sn, 0.0, 0.0, -$sn, $cs, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, $tx, $ty, 0.0, 1.0)
    $parts = @()
    foreach ($v in $n) {
        if ($v -eq 0.0) { $parts += '0' }
        elseif ($v -eq 1.0) { $parts += '1' }
        else { $parts += ([Math]::Round($v, 6)).ToString('0.######', $f) }
    }
    return '(' + ($parts -join ',') + ')'
}

function Rotate([double]$l,[double]$t,[double]$w,[double]$h,[double]$deg,[string]$inner) {
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Transform matrix="' + (RotM $l $t $w $h $deg) + '">' + $inner + '</Transform></Positioned>'
}

function Blur([double]$l,[double]$t,[double]$w,[double]$h,[double]$sig,[string]$inner) {
    $s = ([Math]::Round($sig, 2)).ToString('0.##', [System.Globalization.CultureInfo]::InvariantCulture)
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><ImageFiltered sigmaX="' + $s + '" sigmaY="' + $s + '">' + $inner + '</ImageFiltered></Positioned>'
}

function Op([double]$l,[double]$t,[double]$w,[double]$h,[double]$o,[string]$inner) {
    $s = ([Math]::Round($o, 3)).ToString('0.###', [System.Globalization.CultureInfo]::InvariantCulture)
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><Opacity opacity="' + $s + '">' + $inner + '</Opacity></Positioned>'
}

function TBlend([double]$l,[double]$t,[double]$w,[double]$h,[string]$color,[string]$mode,[string]$inner) {
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><ColorFiltered color="' + $color + '" blendMode="' + $mode + '">' + $inner + '</ColorFiltered></Positioned>'
}

function ClipOv([double]$l,[double]$t,[double]$w,[double]$h,[string]$inner) {
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><ClipOval clipBehavior="ANTI_ALIAS">' + $inner + '</ClipOval></Positioned>'
}

function ClipR([double]$l,[double]$t,[double]$w,[double]$h,[int]$rad,[string]$inner) {
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) + '" height="' + (Fmt $h) +
           '"><ClipRRect clipBehavior="ANTI_ALIAS" borderRadius="' + $rad.ToString() + '">' + $inner + '</ClipRRect></Positioned>'
}

# ---------- raw widget emitters (NO <Positioned> wrapper) ----------
# Required as children of Transform / Opacity / ImageFiltered / ColorFiltered /
# Clip* -- those take a single child widget and <Positioned> is only legal as a
# direct child of <Stack>, so nesting Box/Circle inside them would be a PARSE_ERROR.
function C([double]$w,[double]$h,[string]$color,[int]$r) {
    $rr = ''; if ($r -gt 0) { $rr = ' borderRadius="' + $r.ToString() + '"' }
    return '<Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" color="' + $color + '"' + $rr + '/>'
}
# raw (unwrapped) single-child wrappers -- composable, no <Positioned> of their own
function OpX([double]$o,[string]$inner) {
    $s = ([Math]::Round($o, 3)).ToString('0.###', [System.Globalization.CultureInfo]::InvariantCulture)
    return '<Opacity opacity="' + $s + '">' + $inner + '</Opacity>'
}
function RotX([double]$w,[double]$h,[double]$deg,[string]$inner) {
    $r = $deg * [Math]::PI / 180.0
    $cs = [Math]::Cos($r); $sn = [Math]::Sin($r)
    $cx = $w / 2.0; $cy = $h / 2.0
    $tx = $cx - ($cs * $cx - $sn * $cy)
    $ty = $cy - ($sn * $cx + $cs * $cy)
    $f = [System.Globalization.CultureInfo]::InvariantCulture
    $n = @($cs, $sn, 0.0, 0.0, -$sn, $cs, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, $tx, $ty, 0.0, 1.0)
    $parts = @()
    foreach ($v in $n) {
        if ($v -eq 0.0) { $parts += '0' }
        elseif ($v -eq 1.0) { $parts += '1' }
        else { $parts += ([Math]::Round($v, 6)).ToString('0.######', $f) }
    }
    return '<Transform matrix="(' + ($parts -join ',') + ')">' + $inner + '</Transform>'
}
function BlurX([double]$sig,[string]$inner) {
    $s = ([Math]::Round($sig, 2)).ToString('0.##', [System.Globalization.CultureInfo]::InvariantCulture)
    return '<ImageFiltered sigmaX="' + $s + '" sigmaY="' + $s + '">' + $inner + '</ImageFiltered>'
}
function BlendX([string]$color,[string]$mode,[string]$inner) {
    return '<ColorFiltered color="' + $color + '" blendMode="' + $mode + '">' + $inner + '</ColorFiltered>'
}
function CC([double]$d,[string]$color) {
    return '<Container width="' + (Fmt $d) + '" height="' + (Fmt $d) + '" shape="CIRCLE" color="' + $color + '"/>'
}
function CGrad([double]$w,[double]$h,[string]$colors,[string]$type,[string]$a1,[string]$a2,[int]$r) {
    $s = '<Container width="' + (Fmt $w) + '" height="' + (Fmt $h) + '" gradientType="' + $type + '" gradientColors="' + $colors + '"'
    if ($type -eq 'LINEAR') { $s += ' gradientBegin="' + $a1 + '" gradientEnd="' + $a2 + '"' }
    if ($type -eq 'RADIAL') { $s += ' gradientCenter="' + $a1 + '" gradientRadius="' + $a2 + '"' }
    if ($r -gt 0) { $s += ' borderRadius="' + $r.ToString() + '"' }
    return $s + '/>'
}

# ---------- assembly ----------
function New-Case([string]$id) {
    Use-Case $id
    $script:SEG = New-Object System.Collections.Generic.List[string]
}

function Finish-Case([string]$id, [int]$w, [int]$h, [string]$bg) {
    $body = [string]::Join('', $script:SEG)
    $dsl = '<Snapshot type="png" background="' + $bg + '"><Container width="' + $w.ToString() + '" height="' + $h.ToString() +
           '" color="' + $bg + '"><Stack>' + $body + '</Stack></Container></Snapshot>'
    $dir = Join-Path $script:B01OUT ("case-" + $id)
    $tdir = Join-Path $script:B01TMP ("case-" + $id)
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    if (!(Test-Path $tdir)) { New-Item -ItemType Directory -Force -Path $tdir | Out-Null }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText((Join-Path $tdir 'final.snapshot'), $dsl, $utf8)
    [IO.File]::WriteAllText((Join-Path $dir 'final.snapshot'), $dsl, $utf8)
    return $dsl.Length
}
