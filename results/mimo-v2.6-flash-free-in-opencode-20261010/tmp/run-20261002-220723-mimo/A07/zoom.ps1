param([string]$Src, [int]$X, [int]$Y, [int]$W, [int]$H, [double]$Z, [string]$Out)
Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::FromFile($Src)
try {
  $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
  $crop = $bmp.Clone($rect, $bmp.PixelFormat)
  $nw = [int]($W * $Z); $nh = [int]($H * $Z)
  $out2 = New-Object System.Drawing.Bitmap($nw, $nh)
  $g = [System.Drawing.Graphics]::FromImage($out2)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
  $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
  $g.DrawImage($crop, 0, 0, $nw, $nh)
  $g.Dispose(); $crop.Dispose()
  $out2.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
  $out2.Dispose()
  "zoom -> $Out ($nw x $nh)"
} finally { $bmp.Dispose() }
