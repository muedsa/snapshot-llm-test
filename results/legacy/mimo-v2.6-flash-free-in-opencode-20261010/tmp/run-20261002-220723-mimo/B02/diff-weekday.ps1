$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$out  = "$root\outputs\run-20261002-220723-mimo\B02"
$att  = "$root\tmp\run-20261002-220723-mimo\B02\attempts"
Add-Type -AssemblyName System.Drawing

function Compare-Png([string]$oldPath, [string]$newPath, [string]$label) {
    $a = [System.Drawing.Bitmap]::FromFile($oldPath)
    $b = [System.Drawing.Bitmap]::FromFile($newPath)
    Write-Output ("{0}: old {1}x{2} -> new {3}x{4}" -f $label, $a.Width, $a.Height, $b.Width, $b.Height)
    if (($a.Width -ne $b.Width) -or ($a.Height -ne $b.Height)) {
        Write-Output "  SIZE MISMATCH"
        $a.Dispose(); $b.Dispose()
        return
    }
    $minX = [int]::MaxValue; $minY = [int]::MaxValue; $maxX = -1; $maxY = -1; $n = 0
    $band = @{}
    for ($y = 0; $y -lt $a.Height; $y += 2) {
        for ($x = 0; $x -lt $a.Width; $x += 2) {
            $pa = $a.GetPixel($x, $y); $pb = $b.GetPixel($x, $y)
            $d = [Math]::Abs($pa.R - $pb.R) + [Math]::Abs($pa.G - $pb.G) + [Math]::Abs($pa.B - $pb.B)
            if ($d -gt 60) {
                $n++
                if ($x -lt $minX) { $minX = $x }
                if ($x -gt $maxX) { $maxX = $x }
                if ($y -lt $minY) { $minY = $y }
                if ($y -gt $maxY) { $maxY = $y }
                $k = [int][Math]::Floor($y / 50.0) * 50
                if ($band.ContainsKey($k)) { $band[$k] = $band[$k] + 1 } else { $band[$k] = 1 }
            }
        }
    }
    if ($n -eq 0) {
        Write-Output "  IDENTICAL pixels"
    } else {
        Write-Output ("  diff samples = {0}  bbox = [{1}..{2}] x [{3}..{4}]" -f $n, $minX, $maxX, $minY, $maxY)
        foreach ($k in ($band.Keys | Sort-Object)) {
            Write-Output ("    y {0}-{1} : {2}" -f $k, ($k + 49), $band[$k])
        }
    }
    $a.Dispose(); $b.Dispose()
}

Compare-Png "$att\case-08.pre-weekdayfix.png" "$out\case-08\final.png" 'case-08'
Compare-Png "$att\case-04.pre-weekdayfix.png" "$out\case-04\final.png" 'case-04'
