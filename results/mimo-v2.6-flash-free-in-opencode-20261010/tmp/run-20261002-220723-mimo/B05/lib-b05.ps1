# lib-b05.ps1 -- DSL helpers for B05 (product from zero, 10 usage screens)
# Dot-source. Chains lib-b04.ps1 -> lib-b03.ps1 -> lib-b01.ps1 (proven primitives).
# PS 5.1 rules honoured: no ??, no ternary, parenthesize arithmetic,
# never name a helper H (Get-History alias), never reuse $r beside $R,
# never use $d beside $D (case-insensitive collision -> silent null overwrite),
# never put an inline `if` statement where an expression is required.
$ErrorActionPreference = 'Stop'

$script:B05ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$script:B05OUT  = Join-Path $script:B05ROOT 'outputs\run-20261002-220723-mimo\B05'
$script:B05TMP  = Join-Path $script:B05ROOT 'tmp\run-20261002-220723-mimo\B05'

. (Join-Path $script:B05ROOT 'tmp\run-20261002-220723-mimo\B04\lib-b04.ps1')

# re-point shared globals at B05
$script:FAM = 'Noto Sans CJK SC'
$script:OUT = $script:B05OUT
$script:PROBLEMS.Clear()
$script:SEG.Clear()
$script:CURRENT = 'none'

$script:SANS  = 'Noto Sans CJK SC'
$script:SERIF = 'Noto Serif CJK SC'
$script:MONO  = 'Noto Sans Mono CJK SC'
$script:DISP  = 'Inter Black'
$script:BODY  = 'Inter'

# ---------- B05 palette: "concrete + riser" ----------
$script:BG_D    = '#12161B'   # deep ground
$script:PANEL_D = '#1A2028'   # raised panel on dark
$script:PANEL_D2= '#232B36'   # panel 2 on dark
$script:SHAFT_D = '#0E1216'   # shaft void on dark
$script:HAIRD   = '#2E3742'   # hairline on dark
$script:HAIRD2  = '#414C5A'   # stronger rule on dark
$script:BG_L    = '#EDEAE3'   # concrete ground
$script:WHITE   = '#FFFFFF'
$script:SHADE   = '#E1DCD2'   # paper shade
$script:SHAFT_L = '#F1EEE7'   # shaft void on light
$script:HAIRL   = '#C7BFB0'   # hairline on light
$script:HAIRL2  = '#A9A093'

$script:ACC     = '#E4632A'   # riser orange -- primary accent
$script:ACC2    = '#F2A03C'   # amber
$script:TEAL    = '#1E9B8A'   # 已签约
$script:AMBER   = '#E0A32E'   # 已同意
$script:CORAL   = '#DC5238'   # 顾虑
$script:GREY    = '#8A93A0'   # 未表态

$script:INK     = '#15191F'   # primary text on light
$script:MUTEL   = '#676E7A'   # secondary on light
$script:PAPERW  = '#F4F1EA'   # primary text on dark
$script:MUTED   = '#94A0AE'   # secondary on dark

$script:TINTD = @{ '已签约'='#1E2A2E'; '已同意'='#2B2720'; '顾虑'='#2E2321'; '未表态'='#242A32' }
$script:TINTL = @{ '已签约'='#E6F3F1'; '已同意'='#FBF2E1'; '顾虑'='#FBEAE5'; '未表态'='#EDEFF2' }

function AttColor([string]$a) {
  switch ($a) {
    '已签约' { return $script:TEAL }
    '已同意' { return $script:AMBER }
    '顾虑'   { return $script:CORAL }
    default  { return $script:GREY }
  }
}
function AttTint([string]$tone, [string]$a) {
  if ($tone -eq 'light') { $m = $script:TINTL } else { $m = $script:TINTD }
  if ($null -eq $m[$a]) { return $m['未表态'] }
  return $m[$a]
}
function ToneVars([string]$tone) {
  # returns ,@(shell, edge, text, sub, shaft)
  if ($tone -eq 'light') { return ,@($script:WHITE, $script:HAIRL, $script:INK, $script:MUTEL, $script:SHAFT_L) }
  return ,@($script:PANEL_D, $script:HAIRD, $script:PAPERW, $script:MUTED, $script:SHAFT_D)
}

# ---------- data ----------
$script:CALC = $null
function Get-Calc() {
  if ($null -eq $script:CALC) {
    $p = Join-Path $script:B05TMP 'calc-b05.json'
    $script:CALC = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8) | ConvertFrom-Json
  }
  return $script:CALC
}
function N0([object]$v) { return ([int]$v).ToString('N0') }          # 12,896
function W1([object]$v) { return ([double]$v).ToString('0.0') }      # 52.8

# ---------- shared furniture ----------
function Masthead5([string]$no, [string]$kicker, [double]$l, [double]$t, [double]$w,
                   [string]$rule, [string]$cK, [string]$cT, [int]$fsK, [int]$fsT) {
    $out = ''
    $kx = [Math]::Max($l, ($l + $w - 560))
    $kw = [Math]::Min(560, ($l + $w - $kx))
    $out += Ts ('mh-n' + $no) $l $t 300 ($fsK * 1.8) ('TONGTI  ' + [char]0x2014 + '  ' + $no + ' / 10') $fsK $script:MONO $cK 'LEFT' ''
    $out += Ts ('mh-k' + $no) $kx $t $kw ($fsK * 1.8) $kicker $fsK $script:SANS $cT 'RIGHT' ''
    $yt = $t + $fsK * 2.0
    $out += HR $l $yt $w 2 $rule
    return ,@($out, ($yt + 10))
}

function Foot5([string]$id, [string]$no, [string]$s, [double]$l, [double]$t, [double]$w,
               [string]$rule, [string]$c) {
    $out = HR $l $t $w 1 $rule
    $out += Ts ('ft' + $no) $l ($t + 10) $w 30 $s 17 $script:SANS $c 'LEFT' ''
    return $out
}

function Pill([double]$l, [double]$t, [string]$s, [int]$fs, [string]$bg, [string]$fg,
              [string]$fam, [int]$padX = 12, [int]$hh = 30) {
    $w = [int][Math]::Ceiling((TW $s $fs) + ($padX * 2))
    $box = Box $l $t $w $hh $bg 999
    $txt = Ts ('pl-' + $s) $l $t $w $hh $s $fs $fam $fg 'CENTER' ''
    return ($box + $txt)
}

# outlined box (proven primitives only -- no transparent container fills)
function Outline([double]$x, [double]$y, [double]$w, [double]$hh, [string]$c, [int]$th) {
    $o = Box $x $y $w $th $c 0
    $o += Box $x ($y + $hh - $th) $w $th $c 0
    $o += Box $x $y $th $hh $c 0
    $o += Box ($x + $w - $th) $y $th $hh $c 0
    return $o
}

# diagonal tick, drawn from two rotated bars (proven Rotate + C primitives)
function Tick([double]$x, [double]$y, [double]$dd, [string]$c) {
    $th = $dd * 0.17
    # short stroke: (0.20,0.52) -> (0.42,0.74), centre (0.31,0.63), angle +45
    $la = $dd * 0.311
    $ax = ($x + $dd * 0.31) - ($la / 2.0)
    $ay = ($y + $dd * 0.63) - ($th / 2.0)
    $a = Rotate $ax $ay $la $th 45 (C $la $th $c 0)
    # long stroke: (0.42,0.74) -> (0.80,0.26), centre (0.61,0.50), angle -51.6
    $lb = $dd * 0.612
    $bx = ($x + $dd * 0.61) - ($lb / 2.0)
    $by = ($y + $dd * 0.50) - ($th / 2.0)
    $b = Rotate $bx $by $lb $th (-51.6) (C $lb $th $c 0)
    return $a + $b
}

# checkbox with a diagonal tick
function CheckBox([double]$x, [double]$y, [double]$dd, [bool]$on, [string]$stroke, [string]$fill) {
    $o = Box $x $y $dd $dd $fill 6
    $o += Outline $x $y $dd $dd $stroke 2
    if ($on) { $o += (Tick ($x + $dd * 0.16) ($y + $dd * 0.16) ($dd * 0.68) $stroke) }
    return $o
}

# small badge dot (number is drawn on top by the caller)
function MarkDot([double]$x, [double]$y, [double]$dd, [string]$c, [string]$inner) {
    $out = Circ $x $y $dd $c ''
    if ($inner -ne '') { $out += (Circ ($x + $dd * 0.3) ($y + $dd * 0.3) ($dd * 0.4) $inner '') }
    return $out
}

function Prog([double]$l, [double]$t, [double]$w, [double]$hh, [double]$frac, [string]$bg, [string]$fg, [int]$rad) {
    $o = Box $l $t $w $hh $bg $rad
    $ww = [math]::Max($hh, $w * $frac)
    $o += Box $l $t $ww $hh $fg $rad
    return $o
}

# horizontal stacked bar; items = array of @{ v=; c= }
function Stack1([double]$l, [double]$t, [double]$w, [double]$hh, [object]$items, [double]$total) {
    $o = ''; $x = $l
    foreach ($it in $items) {
        $seg = $w * ([double]$it.v / $total)
        $o += Box $x $t $seg $hh ([string]$it.c) 0
        $x += $seg
    }
    return $o
}

# ---------- THE MOTIF: building section ----------
# 6 floors / 12 units cross-section: one cell per household, colour = attitude.
#   mode: 'attitude' -> id + attitude word
#         'fee'      -> id + model-A self-pay
#         'mini'     -> cells only (repeated small motif)
function Section5([double]$l, [double]$t, [double]$w, [double]$hh, [object]$calc,
                  [string]$tone, [string]$mode, [string]$highlight) {
    $tv = ToneVars $tone
    $shell = $tv[0]; $edge = $tv[1]; $txtC = $tv[2]; $subC = $tv[3]; $shaft = $tv[4]

    $o = ''
    $gutL  = 44.0
    $shaftW = 80.0
    $innerL = $l + $gutL
    $innerW = $w - $gutL
    $cw = ($innerW - $shaftW) / 2.0
    $shX = $innerL + $cw

    $o += Box $l $t $w $hh $shell 6
    $o += Box $l $t $w 3 $edge 0
    $o += Box $l ($t + $hh - 3) $w 3 $edge 0

    $fh = ($hh - 6) / 6.0
    # shaft void + rungs + two cars
    $o += Box $shX ($t + 3) $shaftW ($hh - 9) $shaft 0
    for ($g = 0; $g -lt 14; $g++) {
        $gy = $t + 3 + (($hh - 9) * $g / 13.0)
        $o += Box $shX $gy $shaftW 1 $edge 0
    }
    $o += Box ($shX + 12) ($t + $fh * 1.55) ($shaftW - 24) ($fh * 0.60) $script:TEAL 4
    $o += Box ($shX + 12) ($t + $fh * 4.15) ($shaftW - 24) ($fh * 0.60) $script:TEAL 4

    for ($i = 0; $i -lt 6; $i++) {
        $floor = 6 - $i
        $fy = $t + 3 + ($fh * $i)
        $o += Box $l $fy $w 1 $edge 0
        $numY = $fy + (($fh - 22) / 2.0)
        $o += Ts ('fl' + $floor + '-' + $mode) $l $numY ($gutL - 12) 24 ([string]$floor) 20 $script:MONO $subC 'CENTER' ''

        foreach ($side in 0,1) {
            $uid = ('{0}0{1}' -f $floor, ($side + 1))
            $u  = @($calc.households | Where-Object { $_.id -eq $uid })[0]
            if ($null -eq $u) { continue }
            $cx = if ($side -eq 0) { $innerL } else { $shX + $shaftW }
            $cellW = $cw
            $pad = 6.0
            $bx = $cx + $pad
            $bw = $cellW - ($pad * 2)
            $by = $fy + 6
            $bh = $fh - 12
            if ($bw -le 8 -or $bh -le 8) { continue }

            $tint = AttTint $tone $u.attitude
            $o += Box $bx $by $bw $bh $tint 4
            $o += Box $bx $by 5 $bh (AttColor $u.attitude) 0

            if ($mode -eq 'mini') { continue }

            $subTxt = $u.attitude; $subFs = 17; $subCol = (AttColor $u.attitude); $subFam = $script:SANS
            if ($mode -eq 'fee') { $subTxt = (N0 $u.A) + ' 元'; $subFs = 19; $subCol = $subC; $subFam = $script:MONO }
            if ($bh -ge 60) {
                # tall cell: stack id over the attitude word
                $o += Ts ('u' + $uid + $mode) ($bx + 12) ($by + 5) ($bw - 20) 24 $uid 20 $script:MONO $txtC 'LEFT' ''
                $o += Ts ('s' + $uid) ($bx + 12) ($by + $bh - 27) ($bw - 20) 24 $subTxt $subFs $subFam $subCol 'LEFT' ''
            } else {
                # short cell: id and attitude share one centred line
                $idy = $by + (($bh - 24) / 2.0)
                $idW2 = 56.0
                $o += Ts ('u' + $uid + $mode) ($bx + 12) $idy $idW2 24 $uid 20 $script:MONO $txtC 'LEFT' ''
                $o += Ts ('s' + $uid) ($bx + 12 + $idW2) $idy ($bw - 20 - $idW2) 24 $subTxt $subFs $subFam $subCol 'LEFT' ''
            }
        }
    }

    if ($highlight -ne '') {
        $fl = 6; $sd = 1
        if ($highlight -match '^(\d)\d(\d)$') { $fl = [int]$matches[1]; $sd = [int]$matches[2] - 1 }
        $idx = 6 - $fl
        $hy = $t + 3 + ($fh * $idx)
        $cx = if ($sd -eq 0) { $innerL } else { $shX + $shaftW }
        $bx = $cx + 6
        $bw = $cw - 12
        $by = $hy + 6
        $bh = $fh - 12
        $o += Outline ($bx - 5) ($by - 5) ($bw + 10) ($bh + 10) $script:ACC 3
    }
    return $o
}

function SectionMini([double]$l, [double]$t, [double]$w, [double]$hh, [object]$calc, [string]$tone) {
    return (Section5 $l $t $w $hh $calc $tone 'mini' '')
}

# ---------- page assembly ----------
function Page5([int]$w, [int]$h, [string]$bg, [string]$inner) {
    return '<Snapshot type="png" background="' + $bg + '">' +
           '<Container width="' + $w.ToString() + '" height="' + $h.ToString() + '" color="' + $bg + '">' +
           '<Stack clipBehavior="NONE">' + $inner + '</Stack></Container></Snapshot>'
}
function Write-Dsl5([string]$path, [string]$body) {
    $dir = Split-Path $path -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [IO.File]::WriteAllText($path, $body.Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
}
function Report-Problems5() {
    if ($script:PROBLEMS.Count -eq 0) { Write-Output 'problems = 0' }
    else { $script:PROBLEMS | ForEach-Object { Write-Output $_ } }
}
