# Crop a region of a rendered PNG at integer scale (nearest neighbour) so the
# geometry can be judged at full resolution instead of from a shrunken preview.
param(
  [Parameter(Mandatory=$true)][string]$InFile,
  [Parameter(Mandatory=$true)][string]$OutFile,
  [Parameter(Mandatory=$true)][int]$X,
  [Parameter(Mandatory=$true)][int]$Y,
  [Parameter(Mandatory=$true)][int]$W,
  [Parameter(Mandatory=$true)][int]$H,
  [double]$Scale = 2
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$b1 = [System.Drawing.Bitmap]::new($InFile)
if (($X + $W) -gt $b1.Width -or ($Y + $H) -gt $b1.Height) { throw "crop outside image" }
$nw = [int]($W * $Scale); $nh = [int]($H * $Scale)
$b2 = [System.Drawing.Bitmap]::new($nw, $nh)
$g  = [System.Drawing.Graphics]::FromImage($b2)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.PixelOffsetMode    = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$g.DrawImage($b1,
  [System.Drawing.Rectangle]::new(0, 0, $nw, $nh),
  [System.Drawing.Rectangle]::new($X, $Y, $W, $H),
  [System.Drawing.GraphicsUnit]::Pixel)
$g.Dispose()
$dir = Split-Path $OutFile -Parent
if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
$b2.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)
$b2.Dispose(); $b1.Dispose()
Write-Host "$OutFile  ${W}x${H} -> ${nw}x${nh}"
