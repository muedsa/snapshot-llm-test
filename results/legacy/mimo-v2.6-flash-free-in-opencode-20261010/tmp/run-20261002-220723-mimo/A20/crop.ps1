param(
  [Parameter(Mandatory=$true)][string]$Src,
  [Parameter(Mandatory=$true)][string]$Out,
  [Parameter(Mandatory=$true)][double]$X,
  [Parameter(Mandatory=$true)][double]$Y,
  [Parameter(Mandatory=$true)][double]$W,
  [Parameter(Mandatory=$true)][double]$H,
  [double]$Scale = 2.0
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$fullSrc = (Resolve-Path -LiteralPath $Src).Path
$image = [System.Drawing.Image]::FromFile($fullSrc)
$dw = [int][Math]::Round($W * $Scale)
$dh = [int][Math]::Round($H * $Scale)
$bmp = [System.Drawing.Bitmap]::new($dw, $dh)
$gr = [System.Drawing.Graphics]::FromImage($bmp)
$gr.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$gr.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$gr.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$gr.Clear([System.Drawing.Color]::White)
$destRect = [System.Drawing.Rectangle]::new(0, 0, $dw, $dh)
$srcRect  = [System.Drawing.Rectangle]::new([int]$X, [int]$Y, [int]$W, [int]$H)
$gr.DrawImage($image, $destRect, $srcRect, [System.Drawing.GraphicsUnit]::Pixel)
$gr.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
$image.Dispose()
"crop -> $Out  ($dw x $dh)  src[$X,$Y,$W,$H] x$Scale"
