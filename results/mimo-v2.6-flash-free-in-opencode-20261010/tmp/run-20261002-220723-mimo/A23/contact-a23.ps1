# contact-a23.ps1 - compose the 6 DELIVERED frame PNGs into one contact sheet so the
# whole sequence (and the real transparency) can be inspected in a single view.
# Viewing aid only: written to tmp/, never a deliverable and never embedded anywhere.
param(
  [string]$OutDir = 'outputs\run-20261002-220723-mimo\A23',
  [string]$OutPath = 'tmp\run-20261002-220723-mimo\A23\contact-sheet.png'
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
Add-Type -AssemblyName System.Drawing

$TILE = 300; $GAP = 16; $MARGIN = 20; $LABEL = 26
$COLS = 3; $ROWS = 2
$W = $MARGIN * 2 + $COLS * $TILE + ($COLS - 1) * $GAP
$H = $MARGIN * 2 + $ROWS * ($TILE + $LABEL) + ($ROWS - 1) * $GAP

$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

# checkerboard so that alpha=0 (real transparency) is unambiguous in the screenshot
$cell = 12
$cA = [System.Drawing.Color]::FromArgb(255, 228, 231, 238)
$cB = [System.Drawing.Color]::FromArgb(255, 246, 247, 250)
$g.Clear($cB)
for ($y = 0; $y -lt $H; $y += $cell) {
  for ($x = 0; $x -lt $W; $x += $cell) {
    if (([int][Math]::Floor($x / $cell) + [int][Math]::Floor($y / $cell)) % 2 -eq 0) {
      $g.FillRectangle((New-Object System.Drawing.SolidBrush($cA)), $x, $y, $cell, $cell)
    }
  }
}

$font = New-Object System.Drawing.Font('Segoe UI', 13, [System.Drawing.FontStyle]::Bold)
$brushLbl = [System.Drawing.Brushes]::DarkSlateBlue
$pen = New-Object System.Drawing.Pen(([System.Drawing.Color]::FromArgb(255, 140, 148, 170)), 1)

$notes = @(
  @{ f = 'frame-01'; t = 't = 0.0  最分散' },
  @{ f = 'frame-02'; t = 't = 0.2' },
  @{ f = 'frame-03'; t = 't = 0.4' },
  @{ f = 'frame-04'; t = 't = 0.6' },
  @{ f = 'frame-05'; t = 't = 0.8' },
  @{ f = 'frame-06'; t = 't = 1.0  成图' }
)

for ($k = 0; $k -lt 6; $k++) {
  $col = $k % $COLS; $row = [int][Math]::Floor($k / $COLS)
  $tx = $MARGIN + $col * ($TILE + $GAP)
  $ty = $MARGIN + $row * ($TILE + $LABEL + $GAP)
  $p = Join-Path $OutDir ($notes[$k].f + '.png')
  $img = [System.Drawing.Image]::FromFile((Resolve-Path $p).Path)
  $g.DrawImage($img, $tx, $ty, $TILE, $TILE)
  $img.Dispose()
  $g.DrawRectangle($pen, $tx, $ty, $TILE, $TILE)
  $g.DrawString(('{0}   {1}' -f $notes[$k].f, $notes[$k].t), $font, $brushLbl, $tx, $ty + $TILE + 4)
}
$font.Dispose(); $pen.Dispose(); $g.Dispose()
$bmp.Save((Join-Path (Split-Path $OutPath -Parent) (Split-Path $OutPath -Leaf)),
  [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
$i = Get-Item $OutPath
"contact sheet: {0}  {1}x{2}  {3} bytes" -f $OutPath, $W, $H, $i.Length
