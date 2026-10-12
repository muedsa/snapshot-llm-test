param([string]$Src, [string]$Dst, [int]$X, [int]$Y, [int]$W, [int]$H, [double]$Zoom)
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile($Src)
$rw = [int]([Math]::Round($W * $Zoom, 0))
$rh = [int]([Math]::Round($H * $Zoom, 0))
$bmp = New-Object System.Drawing.Bitmap($rw, $rh)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$g.DrawImage($img, (New-Object System.Drawing.Rectangle(0, 0, $rw, $rh)), (New-Object System.Drawing.Rectangle($X, $Y, $W, $H)), [System.Drawing.GraphicsUnit]::Pixel)
$g.Dispose()
$bmp.Save($Dst, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
$img.Dispose()
Write-Output ("wrote " + $Dst + "  " + $rw + "x" + $rh)
