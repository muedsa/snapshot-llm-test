param([string]$File = 'probe-hatch.png')
# runscan.ps1 -- print colour runs along a scanline so we know exactly where each
# box and each hatch landed (ground truth, not eyeballed).
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b6 = Join-Path $root 'tmp\run-20261002-220723-mimo\B06'
Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::FromFile((Join-Path $b6 $File))
Write-Output ("file = {0}   {1}x{2}" -f $File, $bmp.Width, $bmp.Height)

function Name($p) {
    if ($p.R -eq 244 -and $p.G -eq 242 -and $p.B -eq 237) { return 'pageBG' }
    if ($p.R -eq 233 -and $p.G -eq 229 -and $p.B -eq 220) { return 'boxBG' }
    if ($p.R -eq 76 -and $p.G -eq 95 -and $p.B -eq 213) { return 'blue' }
    if ($p.R -eq 224 -and $p.G -eq 163 -and $p.B -eq 60) { return 'orange' }
    if ($p.R -eq 229 -and $p.G -eq 72 -and $p.B -eq 77) { return 'red' }
    if ($p.R -eq 255 -and $p.G -eq 255 -and $p.B -eq 255) { return 'white' }
    return ('rgb({0},{1},{2})' -f $p.R, $p.G, $p.B)
}

foreach ($yy in @(110, 232)) {
    Write-Output ("--- y = {0} ---" -f $yy)
    $x = 0
    while ($x -lt $bmp.Width) {
        $nm = Name ($bmp.GetPixel($x, $yy))
        $x2 = $x
        while (($x2 + 1) -lt $bmp.Width) {
            $nm2 = Name ($bmp.GetPixel(($x2 + 1), $yy))
            if ($nm2 -ne $nm) { break }
            $x2++
        }
        if (($x2 - $x) -ge 6) { Write-Output ("  {0,4}..{1,-4}  {2}" -f $x, $x2, $nm) }
        $x = $x2 + 1
    }
}
$bmp.Dispose()
