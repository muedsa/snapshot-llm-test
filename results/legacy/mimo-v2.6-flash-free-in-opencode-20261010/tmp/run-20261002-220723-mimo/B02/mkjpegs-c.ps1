$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Add-Type -AssemblyName System.Drawing
$out = "$root\outputs\run-20261002-220723-mimo\B02"
$vd = "$root\tmp\run-20261002-220723-mimo\B02\view"
$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters(1)
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]95)
$targets = @{}
$targets['04'] = 'case-04 daily board 1920x1080 r8'
$targets['07'] = 'case-07 volunteer card 1040x660 r6'
$targets['08'] = 'case-08 october programme 1748x760 r1'
$targets['09'] = 'case-09 annual report 1080x1080 r6'
$strip = 64
$only = $args[0]
foreach ($n in @('04','07','08','09')) {
  if ($only -and $n -ne $only) { continue }
  $img = [System.Drawing.Image]::FromFile("$out\case-$n\final.png")
  $bmp = New-Object System.Drawing.Bitmap($img.Width, ($img.Height + $strip))
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.Clear([System.Drawing.Color]::FromArgb(255, 30, 30, 30))
  $g.DrawImage($img, 0, $strip, $img.Width, $img.Height)
  $font = New-Object System.Drawing.Font('Consolas', 26, [System.Drawing.FontStyle]::Bold)
  $g.DrawString(('>>> B02 ' + $targets[$n] + '  sha=' + (Get-FileHash "$out\case-$n\final.png" -Algorithm SHA256).Hash.Substring(0,12) + ' <<<'), $font, [System.Drawing.Brushes]::Yellow, 14, 18)
  $g.Dispose()
  $img.Dispose()
  $ts = Get-Date -Format 'yyyyMMddHHmmssfff'
  $dst = "$vd\v" + $n + "-" + $ts + ".jpg"
  $bmp.Save($dst, $enc, $ep)
  $bmp.Dispose()
  Write-Output $dst
}
