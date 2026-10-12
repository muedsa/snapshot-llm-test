# ascii-a23.ps1 - text-mode rendering of a PNG so the composition can be inspected when
# the image viewer buffer is unreliable.  Samples real pixels; no guessing.
param(
  [string]$Path = 'outputs\run-20261002-220723-mimo\A23\cover.png',
  [int]$Cols = 150
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
Add-Type -AssemblyName System.Drawing

$bmp = [System.Drawing.Bitmap]::FromFile((Resolve-Path $Path).Path)
$W = $bmp.Width; $H = $bmp.Height
$step = $W / [double]$Cols
$Rows = [int][Math]::Floor($H / ($step * 2.1))     # 2.1 = character cell aspect

function Classify([System.Drawing.Color]$c) {
  if ($c.A -lt 8) { return '.' }                     # transparent
  $r = $c.R; $g = $c.G; $b = $c.B
  # background / panel plates
  if ($r -lt 25 -and $g -lt 32 -and $b -lt 60) { return ':' }
  # near-white text
  if ($r -gt 180 -and $g -gt 180 -and $b -gt 190) { return '#' }
  # orange  #FF8A3D
  if ($r -gt 200 -and $g -gt 100 -and $g -lt 180 -and $b -lt 110) { return 'O' }
  # sky blue  #38BDF8
  if ($r -lt 130 -and $g -gt 150 -and $b -gt 200) { return 'C' }
  # teal  #2DD4BF / #22B8A6
  if ($r -lt 110 -and $g -gt 150 -and $b -gt 130) { return 'T' }
  # purples  #5B4FE8 / #6E63FF / #8A7DFF
  if ($r -gt 60 -and $r -lt 175 -and $b -gt 190) { return 'B' }
  # muted text greys
  if ([Math]::Abs($r - $g) -lt 30 -and [Math]::Abs($g - $b) -lt 45 -and $b -gt 60) { return 'x' }
  return '?'
}

for ($ry = 0; $ry -lt $Rows; $ry++) {
  $line = ''
  for ($cx = 0; $cx -lt $Cols; $cx++) {
    $x0 = [int]($cx * $step); $x1 = [Math]::Min($W - 1, [int](($cx + 1) * $step))
    $y0 = [int]($ry * $step * 2.1); $y1 = [Math]::Min($H - 1, [int](($ry + 1) * $step * 2.1))
    $best = '.'; $rank = 0
    $map = @{ '.' = 0; ':' = 1; 'x' = 2; 'B' = 3; 'T' = 3; 'C' = 3; 'O' = 3; '#' = 4; '?' = 5 }
    for ($y = $y0; $y -le $y1; $y += 3) {
      for ($x = $x0; $x -le $x1; $x += 3) {
        $ch = Classify $bmp.GetPixel($x, $y)
        if ($map[$ch] -gt $rank) { $rank = $map[$ch]; $best = $ch }
      }
    }
    $line += $best
  }
  $line
}
$bmp.Dispose()
