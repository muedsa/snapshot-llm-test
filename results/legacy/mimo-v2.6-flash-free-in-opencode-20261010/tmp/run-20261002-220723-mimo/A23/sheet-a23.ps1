# sheet-a23.ps1 - one-shot verification sheet: the delivered cover plus all 6 delivered
# frames.  Viewing aid only (tmp/), never a deliverable and never embedded in any output.
param(
  [string]$OutDir  = 'outputs\run-20261002-220723-mimo\A23',
  [string]$OutPath = 'tmp\run-20261002-220723-mimo\A23\delivery-sheet.png'
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
Add-Type -AssemblyName System.Drawing

$M = 20
$CW = 1080; $CH = 720                # cover 1200x800 @ 0.9
$TILE = 171; $GAP = 10              # 6*171 + 5*10 = 1076 <= 1080 available
$W = $M * 2 + $CW                     # 1120
$H = $M * 2 + 40 + $CH + 30 + $TILE + 34

$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$g.Clear([System.Drawing.Color]::FromArgb(255, 18, 20, 28))

$font = New-Object System.Drawing.Font('Segoe UI', 14, [System.Drawing.FontStyle]::Bold)
$fontS = New-Object System.Drawing.Font('Segoe UI', 11)
$wht = [System.Drawing.Brushes]::White
$gry = [System.Drawing.Brushes]::Gray

$g.DrawString('A23 交付预览：cover.png（1200x800 RGB，全文可读）+ frame-01..06.png（600x600 透明）  --  仅用于核对，不是交付物',
  $fontS, $gry, $M, $M)

$y0 = $M + 40
$cv = [System.Drawing.Image]::FromFile((Resolve-Path (Join-Path $OutDir 'cover.png')).Path)
$g.DrawImage($cv, $M, $y0, $CW, $CH)
$cv.Dispose()
$g.DrawString('cover.png', $font, $wht, $M, $y0 + $CH + 6)

$y1 = $y0 + $CH + 34
$x = $M
for ($i = 1; $i -le 6; $i++) {
  $n = 'frame-{0:D2}.png' -f $i
  $im = [System.Drawing.Image]::FromFile((Resolve-Path (Join-Path $OutDir $n)).Path)
  # checkerboard behind each frame so real alpha is visible
  $cell = 10
  for ($yy = 0; $yy -lt $TILE; $yy += $cell) {
    for ($xx = 0; $xx -lt $TILE; $xx += $cell) {
      $c = if (([int][Math]::Floor($xx / $cell) + [int][Math]::Floor($yy / $cell)) % 2 -eq 0) {
        [System.Drawing.Color]::FromArgb(255, 70, 74, 86) } else { [System.Drawing.Color]::FromArgb(255, 58, 62, 74) }
      $g.FillRectangle((New-Object System.Drawing.SolidBrush($c)), $x + $xx, $y1 + $yy, $cell, $cell)
    }
  }
  $g.DrawImage($im, $x, $y1, $TILE, $TILE)
  $im.Dispose()
  $g.DrawString(('frame-0{0}' -f $i), $font, $wht, $x, $y1 + $TILE + 6)
  $x += $TILE + $GAP
}

$font.Dispose(); $fontS.Dispose(); $g.Dispose()
$bmp.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
$i2 = Get-Item $OutPath
"delivery sheet: {0}  {1}x{2}  {3} bytes" -f $OutPath, $W, $H, $i2.Length
