# scan-probe.ps1 -- where did each hatch colour actually land?
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b6 = Join-Path $root 'tmp\run-20261002-220723-mimo\B06'
Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::FromFile((Join-Path $b6 'probe-hatch.png'))
Write-Output ("png {0}x{1}" -f $bmp.Width, $bmp.Height)

$targets = @{
    'blue'   = [System.Drawing.Color]::FromArgb(76, 95, 213)
    'orange' = [System.Drawing.Color]::FromArgb(224, 163, 60)
    'red'    = [System.Drawing.Color]::FromArgb(229, 72, 77)
    'greyBG' = [System.Drawing.Color]::FromArgb(233, 229, 220)
    'pageBG' = [System.Drawing.Color]::FromArgb(244, 242, 237)
}
foreach ($name in @('blue','orange','red','greyBG','pageBG')) {
    $c = $targets[$name]
    $minX = 99999; $maxX = -1; $minY = 99999; $maxY = -1; $n = 0
    for ($y = 0; $y -lt $bmp.Height; $y += 2) {
        for ($x = 0; $x -lt $bmp.Width; $x += 2) {
            $p = $bmp.GetPixel($x, $y)
            if ($p.R -eq $c.R -and $p.G -eq $c.G -and $p.B -eq $c.B -and $p.A -eq $c.A) {
                $n++
                if ($x -lt $minX) { $minX = $x }
                if ($x -gt $maxX) { $maxX = $x }
                if ($y -lt $minY) { $minY = $y }
                if ($y -gt $maxY) { $maxY = $y }
            }
        }
    }
    if ($n -eq 0) { Write-Output ("{0,-8}  none" -f $name) }
    else { Write-Output ("{0,-8}  x {1}..{2}   y {3}..{4}   px={5}" -f $name, $minX, $maxX, $minY, $maxY, $n) }
}
$bmp.Dispose()
