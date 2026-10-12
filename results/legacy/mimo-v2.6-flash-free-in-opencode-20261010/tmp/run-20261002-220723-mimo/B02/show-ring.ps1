$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Add-Type -AssemblyName System.Drawing
function Show-Ring([string]$tag, [string]$src, [double]$cx, [double]$cy, [double]$r) {
  $img = New-Object System.Drawing.Bitmap($src)
  Write-Output ("--- " + $tag + "  r=" + $r)
  foreach ($a in @(0,45,90,135,180,225,270,315,350)) {
    $rad = $a * [Math]::PI / 180.0
    $px = [int]([Math]::Round($cx + $r * [Math]::Sin($rad)))
    $py = [int]([Math]::Round($cy - $r * [Math]::Cos($rad)))
    $c = $img.GetPixel($px, $py)
    $hex = '#{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B
    Write-Output ("  " + $a.ToString().PadLeft(3) + " deg -> (" + $px + "," + $py + ") " + $hex)
  }
  $img.Dispose()
}
Show-Ring 'B01 c08 ring' "$root\outputs\run-20261002-220723-mimo\B01\case-08\final.png" 286 490 114
Show-Ring 'B01 c08 inner edge r=104' "$root\outputs\run-20261002-220723-mimo\B01\case-08\final.png" 286 490 104
Show-Ring 'B01 c08 outer edge r=124' "$root\outputs\run-20261002-220723-mimo\B01\case-08\final.png" 286 490 124
Show-Ring 'B02 c01 ring' "$root\outputs\run-20261002-220723-mimo\B02\case-01\final.png" 154 750 77
