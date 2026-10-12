# inspect-a23.ps1 - PNG technical verification for the A23 delivery.
param(
  [string]$OutDir = 'outputs\run-20261002-220723-mimo\A23'
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
Add-Type -AssemblyName System.Drawing

function Ihdr($p) {
  $fs = [IO.File]::OpenRead((Resolve-Path $p).Path)
  $buf = New-Object byte[] 30
  [void]$fs.Read($buf, 0, 30)
  $fs.Close()
  return @{
    w     = [BitConverter]::ToUInt32(@($buf[19], $buf[18], $buf[17], $buf[16]), 0)
    h     = [BitConverter]::ToUInt32(@($buf[23], $buf[22], $buf[21], $buf[20]), 0)
    depth = $buf[24]
    ct    = $buf[25]
  }
}

Write-Output ('{0,-20} {1,11}  {2,4} {3,4}  {4,8}  {5}' -f 'file', 'size', 'ct', 'dp', 'bytes', 'sha256[0..15]')
foreach ($f in (Get-ChildItem $OutDir -Filter *.png | Sort-Object Name)) {
  $i = Ihdr $f.FullName
  $sha = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.Substring(0, 16)
  Write-Output ('{0,-20} {1}x{2}      ct={3} dp={4} {5,8}  {6}' -f $f.Name, $i.w, $i.h, $i.ct, $i.depth, $f.Length, $sha)
}

Write-Output ''
Write-Output '--- frame alpha sweep (every 3rd pixel, 40000 samples per frame) ---'
Write-Output ('{0,-10} {1,8} {2,8} {3,9} {4,7} {5,7}' -f 'frame', 'cornerA', 'centreA', 'opaque', 'semi', 'clear')
$alphaStats = @()
foreach ($n in 1..6) {
  $name = 'frame-{0:D2}' -f $n
  $bmp = [System.Drawing.Bitmap]::FromFile((Resolve-Path "$OutDir\$name.png").Path)
  $corner = $bmp.GetPixel(2, 2).A
  $centre = $bmp.GetPixel(300, 300).A
  $op = 0; $semi = 0; $clr = 0
  for ($y = 0; $y -lt 600; $y += 3) {
    for ($x = 0; $x -lt 600; $x += 3) {
      $a = $bmp.GetPixel($x, $y).A
      if ($a -eq 255) { $op++ }
      elseif ($a -eq 0) { $clr++ }
      else { $semi++ }
    }
  }
  $bmp.Dispose()
  Write-Output ('{0,-10} {1,8} {2,8} {3,9} {4,7} {5,7}' -f $name, $corner, $centre, $op, $semi, $clr)
  $alphaStats += [pscustomobject]@{ f = $name; corner = $corner; op = $op; semi = $semi; clr = $clr }
}

Write-Output ''
Write-Output '--- cover RGB / opacity ---'
$cv = [System.Drawing.Bitmap]::FromFile((Resolve-Path "$OutDir\cover.png").Path)
foreach ($pt in @(@(5, 5), @(1195, 795), @(600, 90), @(74, 300))) {
  $c = $cv.GetPixel($pt[0], $pt[1])
  Write-Output ('  ({0},{1})  R={2,3} G={3,3} B={4,3} A={5,3}' -f $pt[0], $pt[1], $c.R, $c.G, $c.B, $c.A)
}
$minA = 255
for ($y = 0; $y -lt 800; $y += 10) {
  for ($x = 0; $x -lt 1200; $x += 10) {
    $a = $cv.GetPixel($x, $y).A
    if ($a -lt $minA) { $minA = $a }
  }
}
$cv.Dispose()
Write-Output ('  cover min alpha over 9600 samples = {0}  (255 means fully opaque RGB)' -f $minA)

Write-Output ''
Write-Output ('frames all corner alpha 0      : {0}' -f (($alphaStats | Where-Object { $_.corner -ne 0 }).Count -eq 0))
Write-Output ('frames all contain clear pixels: {0}' -f (($alphaStats | Where-Object { $_.clr -eq 0 }).Count -eq 0))
Write-Output ('frame sizes all 600x600 RGBA   : {0}' -f (@(1..6 | ForEach-Object {
      $i = Ihdr (Join-Path $OutDir ('frame-{0:D2}.png' -f $_))
      ($i.w -eq 600 -and $i.h -eq 600 -and $i.ct -eq 6 -and $i.depth -eq 8)
    }) -notcontains $false))
