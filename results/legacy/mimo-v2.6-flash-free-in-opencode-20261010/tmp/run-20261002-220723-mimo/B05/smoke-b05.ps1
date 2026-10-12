# smoke-b05.ps1 -- validate lib-b05 helpers parse and the section motif lays out
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
. (Join-Path $root 'tmp\run-20261002-220723-mimo\B05\lib-b05.ps1')

$calc = Get-Calc
$w = 1200; $h = 760
$o = ''
$m = Masthead5 'XX' 'smoke test' 60 48 ($w - 120) $script:HAIRD $script:MUTED $script:PAPERW 20 20
$o += $m[0]; $y = $m[1]

$o += Ts 'title' 60 $y ($w - 120) 60 'section motif smoke test' 40 $script:DISP $script:PAPERW 'LEFT' ''
$y += 70

$o += (Section5 60 $y 460 460 $calc 'dark' 'attitude' '602')
$o += (Section5 560 $y 460 460 $calc 'dark' 'fee' '')
$y += 480

$o += (Pill 60 $y '已签约 7' 18 $script:TEAL $script:WHITE $script:SANS)
$o += (Pill 200 $y '已同意 2' 18 $script:AMBER $script:INK $script:SANS)
$o += (Pill 340 $y '顾虑 3' 18 $script:CORAL $script:WHITE $script:SANS)
$o += (CheckBox 470 ($y + 2) 26 $true $script:ACC $script:PANEL_D)
$o += (CheckBox 510 ($y + 2) 26 $false $script:MUTED $script:PANEL_D)
$o += (Prog 560 ($y + 8) 300 14 0.431 $script:PANEL_D2 $script:ACC 999)
$o += (Stack1 880 ($y + 8) 260 14 @(
        @{ v = 18.6; c = $script:ACC }, @{ v = 10.2; c = $script:ACC2 },
        @{ v = 13.4; c = $script:TEAL }, @{ v = 3.6; c = $script:CORAL },
        @{ v = 2.6; c = $script:GREY }, @{ v = 4.4; c = $script:HAIRD2 }) 52.8)

$y += 60
$o += (Foot5 'x' 'XX' 'smoke: DEMO data only' 60 $y ($w - 120) $script:HAIRD $script:MUTED)

$body = Page5 $w $h $script:BG_D $o
$testDir = Join-Path $root 'tmp\run-20261002-220723-mimo\B05\smoke'
Write-Dsl5 (Join-Path $testDir 'smoke.snapshot') $body

"  dsl bytes = " + (Get-Item (Join-Path $testDir 'smoke.snapshot')).Length
"  problems  = " + $script:PROBLEMS.Count
$script:PROBLEMS | Select-Object -First 12 | ForEach-Object { "    " + $_ }
"  first container = " + [regex]::Match($body, '<Container width="\d+" height="\d+"').Value
