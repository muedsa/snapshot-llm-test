# lib-b04.ps1 -- DSL helpers for B04 (researched visual special, 10 works)
# Dot-source. Builds on lib-b03.ps1 -> lib-b01.ps1 (proven primitives).
# PS 5.1: no ??, no ternary, always parenthesize arithmetic, never name a helper H
# (collides with Get-History alias), never use $r together with $R (case-insensitive).
$ErrorActionPreference = 'Stop'

$script:B04ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$script:B04OUT  = Join-Path $script:B04ROOT 'outputs\run-20261002-220723-mimo\B04'
$script:B04TMP  = Join-Path $script:B04ROOT 'tmp\run-20261002-220723-mimo\B04'

. (Join-Path $script:B04ROOT 'tmp\run-20261002-220723-mimo\B03\lib-b03.ps1')

# re-point the shared globals at B04
$script:FAM = 'Noto Sans CJK SC'
$script:OUT = $script:B04OUT
$script:PROBLEMS.Clear()
$script:SEG.Clear()
$script:CURRENT = 'none'

$script:SANS  = 'Noto Sans CJK SC'
$script:SERIF = 'Noto Serif CJK SC'
$script:MONO  = 'Noto Sans Mono CJK SC'
$script:DISP  = 'Inter Black'
$script:BODY  = 'Inter'

# ---------- B04 editorial palette: "time instrument" ----------
$script:INK    = '#0B1015'   # deep night ground
$script:INK2   = '#121A22'   # raised panel
$script:INK3   = '#1A242E'   # panel 2
$script:HAIR   = '#27323E'   # hairline on ink
$script:HAIR2  = '#3A4855'   # stronger rule on ink
$script:PAPER  = '#F3EFE5'   # warm paper ground
$script:PAPER2 = '#E6E0D2'   # paper shade
$script:PAPER3 = '#D6CEBC'   # paper rule
$script:AMBER  = '#FFB100'   # the leap second (positive insertion)
$script:AMBER2 = '#FF7A1A'
$script:CYAN   = '#49C9DC'   # atomic scale TAI
$script:CORAL  = '#FF5C4D'   # risk / negative leap second
$script:GREEN  = '#5FBF6B'   # "no leap second" confirmation
$script:MUTE   = '#8B97A4'   # secondary on ink
$script:MUTE2  = '#6E675A'   # secondary on paper
$script:WHITE  = '#FFFFFF'
$script:NIGHT  = '#C9D6E3'   # soft text on ink

# ---------- family-aware text ----------
function TFam([string]$f) { $script:FAM = $f }

function Ts([string]$id, [double]$l, [double]$t, [double]$w, [double]$h, [string]$s, [int]$fs,
            [string]$fam, [string]$c, [string]$a = 'LEFT', [string]$bold = '') {
    Fit $id $s $w $fs ('Ts@' + (Fmt $l) + ',' + (Fmt $t)) | Out-Null
    $b = ''
    if ($null -ne $bold -and $bold -ne '') { $b = ' fontStyle="' + $bold + '"' }
    return '<Positioned left="' + (Fmt $l) + '" top="' + (Fmt $t) + '" width="' + (Fmt $w) +
           '" height="' + (Fmt $h) + '"><Text fontSize="' + $fs.ToString() + '" fontFamily="' + $fam +
           '" color="' + $c + '"' + $b + ' textAlign="' + $a + '" maxLines="1">' + (E $s) + '</Text></Positioned>'
}

# guarded multi-line block, family aware.
# positional order: id, l, t, w, fs, lines, lineH, fam, c, a, bold
function TBlock([string]$id, [double]$l, [double]$t, [double]$w, [int]$fs, [object]$lines,
                [double]$lineH, [string]$fam, [string]$c, [string]$a = 'LEFT', [string]$bold = '') {
    $out = ''
    $i = 0
    foreach ($ln in $lines) {
        $s = ([string]$ln)
        if ($s -ne '') {
            Fit $id $s $w $fs ('TBlock#' + $i.ToString()) | Out-Null
            $out += Ts $id ($l) ($t + $i * $lineH) $w ($lineH * 0.98) $s $fs $fam $c $a $bold
        }
        $i++
    }
    return $out
}

# wrapped paragraph, family aware. returns ,@(dsl, lineCount)
function PPara([string]$id, [double]$l, [double]$t, [double]$w, [string]$s, [int]$fs,
               [double]$lineH, [string]$fam, [string]$c, [string]$bold = '') {
    $ls = WrapTW $s $w $fs
    $out = ''
    $i = 0
    foreach ($ln in $ls) {
        $out += Ts $id $l ($t + $i * $lineH) $w ($lineH * 0.98) $ln $fs $fam $c 'LEFT' $bold
        $i++
    }
    return ,@($out, $i)
}

# ---------- surfaces ----------
function Card([double]$l, [double]$t, [double]$w, [double]$h, [string]$bg, [int]$r,
               [string]$border, [string]$sh) {
    $a = [ordered]@{ width = (Fmt $w); height = (Fmt $h); color = $bg }
    if ($r -gt 0) { $a.borderRadius = $r.ToString() }
    if ($null -ne $border -and $border -ne '') { $a.border = $border }
    if ($null -ne $sh -and $sh -ne '') { $a.boxShadow = $sh }
    $s = '<Container'
    foreach ($k in $a.Keys) { $s += ' ' + $k + '="' + [string]$a[$k] + '"' }
    $s += '/>'
    return (P $l $t $w $h $s)
}

# hairline / rule -- parameter order matches Box(l,t,w,h,c): thickness before colour
function HR([double]$l, [double]$t, [double]$w, [double]$th, [string]$c) { return (Box $l $t $w $th $c 0) }
function VR([double]$l, [double]$t, [double]$h, [double]$th, [string]$c) { return (Box $l $t $th $h $c 0) }

# small uppercase-style label
function Kicker([string]$id, [double]$l, [double]$t, [double]$w, [string]$s, [int]$fs,
                [string]$fam, [string]$c) {
    return (Ts $id $l $t $w ($fs * 1.8) $s $fs $fam $c 'LEFT' '')
}

# rectangular tag (no rounded corners, sits on a rule)
function Tag([double]$l, [double]$t, [string]$s, [int]$fs, [string]$bg, [string]$fg,
             [string]$fam, [int]$padX = 10, [int]$h = 34) {
    $w = [int][Math]::Ceiling((TW $s $fs) + ($padX * 2))
    $box = Box $l $t $w $h $bg 0
    $txt = Ts ('tag-' + $s) $l $t $w $h $s $fs $fam $fg 'CENTER' ''
    return ($box + $txt)
}

# ---------- chart primitives ----------
# vertical bar growing upward from baseY
function BarUp([double]$x, [double]$baseY, [double]$w, [double]$hh, [string]$c, [int]$r = 0) {
    return (Box $x ($baseY - $hh) $w $hh $c $r)
}
# horizontal bar growing rightward from x0
function BarRight([double]$x0, [double]$y, [double]$w, [double]$h, [string]$c, [int]$r = 0) {
    return (Box $x0 $y $w $h $c $r)
}
# axis tick below the baseline
function TickD([double]$x, [double]$y, [double]$len, [double]$th, [string]$c) {
    return (Box $x $y $th $len $c 0)
}
function TickU([double]$x, [double]$y, [double]$len, [double]$th, [string]$c) {
    return (Box $x ($y - $len) $th $len $c 0)
}
function TickL([double]$x, [double]$y, [double]$len, [double]$th, [string]$c) {
    return (Box ($x - $len) $y $len $th $c 0)
}

# dotted horizontal reference line (evenly spaced 1px dots)
function DotH([double]$l, [double]$t, [double]$w, [string]$c, [int]$pitch = 8) {
    $out = ''
    $x = 0.0
    while ($x -le $w) {
        $out += Box ($l + $x) $t 2 2 $c 0
        $x += $pitch
    }
    return $out
}
function DotV([double]$l, [double]$t, [double]$h, [string]$c, [int]$pitch = 8) {
    $out = ''
    $y = 0.0
    while ($y -le $h) {
        $out += Box $l ($t + $y) 2 2 $c 0
        $y += $pitch
    }
    return $out
}

# evenly spaced vertical ticks along a horizontal band (61-second minute strip)
function Strip61([double]$l, [double]$t, [double]$w, [double]$hh, [int]$n, [string]$c,
                 [double]$minH, [double]$maxH, [int]$th) {
    # n ticks from x=l to x=l+w inclusive spacing
    $out = ''
    for ($i = 0; $i -lt $n; $i++) {
        $x = $l + ($w * $i / [double]($n - 1))
        $f = [double]$i / [double]($n - 1)
        $th2 = $minH + ($maxH - $minH) * $f
        $out += Box $x ($t + ($hh - $th2)) $th $th2 $c 0
    }
    return $out
}

# stepped staircase: array of pscustomobject{ x0, x1, yy, color }
function Steps([object]$segs, [double]$th) {
    $out = ''
    foreach ($sg in $segs) {
        $wd = [Math]::Max(0.0, ([double]$sg.x1 - [double]$sg.x0))
        $out += Box ([double]$sg.x0) ([double]$sg.yy) $wd $th ([string]$sg.color) 0
        # riser at the right end going up to the next step is drawn by the next seg
    }
    return $out
}

# ---------- shared editorial furniture ----------
# top masthead used by every work: returns dsl + y after the masthead
function Masthead([string]$no, [string]$kicker, [double]$l, [double]$t, [double]$w,
                  [string]$rule, [string]$cK, [string]$cT, [int]$fsK, [int]$fsT) {
    $out = ''
    $out += Ts ('mh-n' + $no) $l $t 260 ($fsK * 1.8) ('LEAP SECOND  ' + [char]0x2014 + '  ' + $no + ' / 10') $fsK $script:MONO $cK 'LEFT' ''
    $out += Ts ('mh-k' + $no) ($l + $w - 520) $t 520 ($fsK * 1.8) $kicker $fsK $script:SANS $cK 'RIGHT' ''
    $yt = $t + $fsK * 2.0
    $out += HR $l $yt $w 2 $rule
    return ,@($out, ($yt + 10))
}

# bottom source strip
function SourceLine([string]$id, [string]$no, [string]$s, [double]$l, [double]$t, [double]$w,
                    [string]$rule, [string]$c) {
    $out = HR $l $t $w 1 $rule
    $out += Ts ('src' + $no) $l ($t + 10) $w 30 $s 18 $script:SANS $c 'LEFT' ''
    return $out
}

# ---------- page assembly (B04 variant) ----------
function Page4([int]$w, [int]$h, [string]$bg, [string]$inner) {
    return '<Snapshot type="png" background="' + $bg + '">' +
           '<Container width="' + $w.ToString() + '" height="' + $h.ToString() + '" color="' + $bg + '">' +
           '<Stack clipBehavior="NONE">' + $inner + '</Stack></Container></Snapshot>'
}

function Write-Dsl4([string]$path, [string]$body) {
    $dir = Split-Path $path -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [IO.File]::WriteAllText($path, $body.Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
}

# ---------- research data ----------
# Decoded IERS Leap_Second.dat -> rows of { MJD, d, m, y, tai } (28 rows, 1972..2017)
function Get-LeapRows() {
    $p = Join-Path $script:B04TMP 'research\Leap_Second.decoded.txt'
    $txt = [IO.File]::ReadAllText($p)
    $rows = @()
    foreach ($line in ($txt -split "`r?`n")) {
        $ln = $line.Trim()
        if ($ln -eq '' -or $ln.StartsWith('#')) { continue }
        if ($ln -match '^(\d+)\.\d+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$') {
            $rows += [pscustomobject]@{
                MJD = [int]$matches[1]; D = [int]$matches[2]; M = [int]$matches[3]
                Y = [int]$matches[4]; TAI = [int]$matches[5]
            }
        }
    }
    if ($rows.Count -ne 28) { throw "Leap_Second.dat parse expected 28 rows, got $($rows.Count)" }
    return ,$rows
}

# insertion list: rows[1..27] -> the day before each effective date
function Get-LeapList() {
    $rows = Get-LeapRows
    $ls = @()
    for ($k = 1; $k -lt $rows.Count; $k++) {
        $rw = $rows[$k]
        $eff = New-Object DateTime($rw.Y, $rw.M, $rw.D)
        $ins = $eff.AddDays(-1)
        $ls += [pscustomobject]@{
            No = $k
            InsertedOn = $ins
            DateStr = $ins.ToString('yyyy-MM-dd')
            Y = $ins.Year
            Mon = $ins.Month
            EffectiveFrom = $eff.ToString('yyyy-MM-dd')
            NewTAI = $rw.TAI
            MJD = $rw.MJD
        }
    }
    return ,$ls
}

function Report-Problems4() {
    if ($script:PROBLEMS.Count -eq 0) { Write-Output 'problems = 0' }
    else { $script:PROBLEMS | ForEach-Object { Write-Output $_ } }
}
