$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$out = "$root\outputs\run-20261002-220723-mimo\B02"
$vw  = "$root\tmp\run-20261002-220723-mimo\B02\view"
Add-Type -AssemblyName System.Drawing
$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters(1)
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]97)

# --- case-08: three date cells (cards 2, 5, 8) ---
$src = New-Object System.Drawing.Bitmap("$out\case-08\final.png")
$crops = @(
  @{ n='card2 (10-11)'; x=610; y=164; w=230; h=56 },
  @{ n='card5 (10-18)'; x=610; y=344; w=230; h=56 },
  @{ n='card8 (10-25)'; x=610; y=524; w=230; h=56 }
)
$scale = 2
$w = 260 * $scale
$h = ($crops.Count * (56 * $scale + 46)) + 70
$bmp = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::FromArgb(255, 24, 24, 24))
$font = New-Object System.Drawing.Font('Consolas', 15, [System.Drawing.FontStyle]::Bold)
$g.DrawString('>>> B02 case-08 weekday fix (r2) date cells  2026-10 = Sat/Sun check <<<', $font, [System.Drawing.Brushes]::Yellow, 8, 8)
$y = 46
foreach ($c in $crops) {
  $r = New-Object System.Drawing.Rectangle($c.x, $c.y, $c.w, $c.h)
  $part = $src.Clone($r, $src.PixelFormat)
  $g.DrawString($c.n, $font, [System.Drawing.Brushes]::Lime, 4, $y + 6)
  $g.DrawImage($part, 0, $y + 4, ($c.w * $scale), ($c.h * $scale))
  $y = $y + (56 * $scale) + 46
  $part.Dispose()
}
$g.Dispose(); $src.Dispose()
$ts = Get-Date -Format 'yyyyMMddHHmmssfff'
$dst = "$vw\c08-weekday-$ts.jpg"
$bmp.Save($dst, $enc, $ep); $bmp.Dispose()
Write-Output $dst

# --- case-04: header date + NEXT UP 4th entry ---
$src2 = New-Object System.Drawing.Bitmap("$out\case-04\final.png")
$crops2 = @(
  @{ n='header date'; x=1330; y=40; w=300; h=48 },
  @{ n='NEXT UP #4';  x=1350; y=436; w=320; h=84 }
)
$w2 = 340 * $scale
$tot2 = 0; foreach ($c in $crops2) { $tot2 = $tot2 + ($c.h * $scale) + 46 }
$h2 = $tot2 + 70
$bmp2 = New-Object System.Drawing.Bitmap($w2, $h2)
$g2 = [System.Drawing.Graphics]::FromImage($bmp2)
$g2.Clear([System.Drawing.Color]::FromArgb(255, 24, 24, 24))
$g2.DrawString('>>> B02 case-04 weekday fix (r9) header + NEXT UP <<<', $font, [System.Drawing.Brushes]::Yellow, 8, 8)
$y2 = 46
foreach ($c in $crops2) {
  $r = New-Object System.Drawing.Rectangle($c.x, $c.y, $c.w, $c.h)
  $part = $src2.Clone($r, $src2.PixelFormat)
  $g2.DrawString($c.n, $font, [System.Drawing.Brushes]::Lime, 4, $y2 + 6)
  $g2.DrawImage($part, 0, $y2 + 4, ($c.w * $scale), ($c.h * $scale))
  $y2 = $y2 + ($c.h * $scale) + 46
  $part.Dispose()
}
$g2.Dispose(); $src2.Dispose()
$ts2 = Get-Date -Format 'yyyyMMddHHmmssfff'
$dst2 = "$vw\c04-weekday-$ts2.jpg"
$bmp2.Save($dst2, $enc, $ep); $bmp2.Dispose()
Write-Output $dst2
