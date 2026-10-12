$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Add-Type -AssemblyName System.Drawing
$out = "$root\outputs\run-20261002-220723-mimo\B02"
$vd = "$root\tmp\run-20261002-220723-mimo\B02\view"
$ts = Get-Date -Format 'yyyyMMddHHmmssfff'
$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters(1)
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]95)
$names = @{ '01'='case-01 migration-season poster 1080x1620'; '02'='case-02 wetland trail map 1920x720';
            '03'='case-03 binocular sign 900x1600'; '04'='case-04 daily board 1920x1080';
            '05'='case-05 workshop cover 1000x1400' }
$strip = 64
foreach ($n in @('01','02','03','04','05')) {
  $img = [System.Drawing.Image]::FromFile("$out\case-$n\final.png")
  $bmp = New-Object System.Drawing.Bitmap($img.Width, ($img.Height + $strip))
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.Clear([System.Drawing.Color]::FromArgb(255, 30, 30, 30))
  $g.DrawImage($img, 0, $strip, $img.Width, $img.Height)
  $font = New-Object System.Drawing.Font('Consolas', 28, [System.Drawing.FontStyle]::Bold)
  $g.DrawString(('>>> B02 ' + $names[$n] + ' <<<'), $font, [System.Drawing.Brushes]::Yellow, 14, 16)
  $g.Dispose()
  $img.Dispose()
  $dst = "$vd\chk" + $n + "-" + $ts + ".jpg"
  $bmp.Save($dst, $enc, $ep)
  $bmp.Dispose()
  Write-Output $dst
}
