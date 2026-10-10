$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Add-Type -AssemblyName System.Drawing
$src = New-Object System.Drawing.Bitmap("$root\outputs\$RUN\A10\compositing-lab.png")

function CropZoom([string]$name, [int]$sx, [int]$sy, [int]$w, [int]$h, [double]$k) {
  $nw = [int]($w * $k); $nh = [int]($h * $k)
  $dst = New-Object System.Drawing.Bitmap($nw, $nh)
  $g = [System.Drawing.Graphics]::FromImage($dst)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
  $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
  $g.DrawImage($src, (New-Object System.Drawing.Rectangle(0,0,$nw,$nh)), (New-Object System.Drawing.Rectangle($sx,$sy,$w,$h)), [System.Drawing.GraphicsUnit]::Pixel)
  $g.Dispose()
  $out = "$root\tmp\$RUN\A10\$name"
  $dst.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
  $dst.Dispose()
  "$out  $nw x $nh"
}

# 1: panels 1 and 2 overlap + crosshair + the marked sampling point
CropZoom 'zoom-sample.png' 290 330 500 140 2.2
# 2: panel 3 card left edge (sharp outside / blurred inside) and the caption
CropZoom 'zoom-card3.png' 180 300 300 180 3
# 3: panel 5 vs panel 6 filter boundary
CropZoom 'zoom-clip.png' 570 700 700 220 1.8
# 4: full experiment zone of panel 3 and of panel 4 (sharp text vs blurred text)
CropZoom 'zoom-zone3.png' 960 270 320 240 2.6
CropZoom 'zoom-zone4.png' 160 690 320 240 2.6
$src.Dispose()
