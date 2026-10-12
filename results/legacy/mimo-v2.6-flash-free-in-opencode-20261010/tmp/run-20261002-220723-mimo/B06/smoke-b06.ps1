# smoke-b06.ps1 -- validate lib-b06 helpers parse and lay out, then write one
# smoke snapshot that exercises every B06-only device.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $root 'tmp\run-20261002-220723-mimo\B06\lib-b06.ps1')

$calc = Get-Calc6
if ($null -eq $calc) { throw 'calc-b06.json missing' }

$W = 1400; $H = 900
$M = 56
$Wt = Tone6 'light'
$shell = $Wt[0]; $hair = $Wt[1]; $txtC = $Wt[2]; $subC = $Wt[3]; $pan = $Wt[4]; $hair2 = $Wt[5]

$o = ''
$mh = Masthead6 'SM' 'lib smoke test' $M 40 ($W - 2 * $M) $hair2 $subC $txtC 20 20
$o += $mh[0]
$y = $mh[1] + 16

$o += Ts 'sm-title' $M $y 700 56 'device smoke' 40 $script:DISP $txtC 'LEFT' ''
$y += 66

# ---- Ruler6 (case-03 / case-06 scale) ----
$o += Ts 'sm-rk' $M $y 400 28 'Ruler6 · reference interval scale' 20 $script:SANS $subC 'LEFT' ''
$ry = $y + 34
$rr = Ruler6 'sm-ruler' $M $ry 640 80 170 5 90 139 142 $script:SHADE6 $script:JADE $script:HAIRL6b $script:CORAL6 18 22
$o += $rr[0]
$o += Ts 'sm-rv' ($rr[1] - 70) ($ry + 58) 140 34 '142 mmHg' 22 $script:MONO $script:CORAL6 'CENTER' ''

# ---- Pct100 (case-08) ----
$o += Ts 'sm-pk' 780 $y 400 28 'Pct100 · 40 of 100' 20 $script:SANS $subC 'LEFT' ''
$o += (Pct100 780 ($y + 34) 260 40 $script:RAIN $script:SHADE6 3 4)

# ---- Wedge6 + Arc6 + Hand6 (case-09 dial) ----
$dy = $y + 130
$cx = 210.0; $cy = [double]($dy + 150)
$o += Ts 'sm-dk' $M $dy 400 28 'Wedge6 / Arc6 / Hand6 · 120-min dial' 20 $script:SANS $subC 'LEFT' ''
$o += (Wedge6 $cx $cy 120 -90 -45 $script:PARK 24)
$o += (Wedge6 $cx $cy 120 -45 90 $script:PARK 44)
$o += (Wedge6 $cx $cy 120 90 270 $script:SHADE6 70)
$o += (Arc6 $cx $cy 134 -90 270 13 8 $script:HAIRL6b)
$o += (Hand6 $cx $cy 116 5 (Dial-Map 27 120) $script:LATE)
$o += (Circ ($cx - 11) ($cy - 11) 22 $script:LATE '')
$o += Ts 'sm-dt' ($cx - 60) ($cy - 16) 120 34 '27' 24 $script:DISP $script:WHITE 'CENTER' ''

# ---- Legend6 + Step6 ----
$o += Ts 'sm-lk' 470 $dy 400 28 'Legend6 + Step6' 20 $script:SANS $subC 'LEFT' ''
$lg = Legend6 470 ($dy + 38) @(
    @{ c = $script:INDIGO; t = '固定可扣' }
    @{ c = $script:CLAIM; t = '有争议' }
    @{ c = $script:ASPHALT; t = '退回' }
) 18 $txtC $script:SANS
$o += $lg[0]
for ($i = 1; $i -le 4; $i++) {
    $sx = 470 + (($i - 1) * 56)
    $o += (Step6 $sx ($dy + 76) 40 $i $script:PHARM $script:WHITE)
}

# ---- Waterfall6 (case-07) ----
$o += Ts 'sm-wk' $M ($dy + 150) 400 28 'Waterfall6 · deposit deductions' 20 $script:SANS $subC 'LEFT' ''
$wf = Waterfall6 'sm-wf' $calc.case07.flow $M ($dy + 186) 700 190 6000 4200 `
        $script:INDIGO $script:INDIGO $script:CLAIM $script:ASPHALT 66 18 $script:HAIRL6b
$o += $wf

# ---- ColStack6 (case-04) ----
$o += Ts 'sm-ck' 800 ($dy + 150) 400 28 'ColStack6 · tier stack' 20 $script:SANS $subC 'LEFT' ''
$parts = @(
    @{ v = 111.72; c = $script:ELEC }
    @{ v = 57.42; c = $script:JUMP }
    @{ v = 67.49; c = $script:CORAL6 }
)
$cs = ColStack6 820 ($dy + 376) 150 190 $parts 236.63 2
$o += $cs[0]
$o += Ts 'sm-cv' 990 ($dy + 340) 220 40 '236.63 元' 26 $script:MONO $txtC 'LEFT' ''

$y = $dy + 400
$o += (Foot6 'SM' 'smoke footer' $M $y ($W - 2 * $M) $hair $subC)

Report-Problems6

$Path = Join-Path (Join-Path $script:B06TMP 'smoke') 'smoke.snapshot'
Write-Dsl6 $Path (Page6 $W $H $shell $o)
Write-Output "wrote $Path  $((Get-Item $Path).Length) bytes"
