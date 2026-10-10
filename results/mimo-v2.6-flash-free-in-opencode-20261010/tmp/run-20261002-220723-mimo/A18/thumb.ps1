param(
  [Parameter(Mandatory=$true)][string]$In,
  [Parameter(Mandatory=$true)][string]$Out,
  [int]$Width = 400
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$inPath = (Resolve-Path $In).Path
$outDir = Split-Path $Out -Parent
if ($outDir -and !(Test-Path $outDir)) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }
$outPath = Join-Path $outDir (Split-Path $Out -Leaf)

$src = New-Object System.Drawing.Bitmap($inPath)
$w = $Width
$h = [int][Math]::Round($src.Height * $Width / $src.Width)
$dst = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($dst)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$g.DrawImage($src, 0, 0, $w, $h)
$g.Dispose()
$dst.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$dst.Dispose()
$src.Dispose()
Write-Output ("thumbnail {0} -> {1}  {2}x{3}" -f $inPath, $outPath, $w, $h)
