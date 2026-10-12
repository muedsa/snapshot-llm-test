$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
Add-Type -AssemblyName System.Drawing
$PNG = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A17\probe-02.png'
$bmp = New-Object System.Drawing.Bitmap($PNG)
$bands = @(
  [pscustomobject]@{ name = 'mono  fs20  100 zeros';    y0 = 6;   y1 = 42;  n = 100; fs = 20 },
  [pscustomobject]@{ name = 'mono  fs22  100 zeros';    y0 = 44;  y1 = 80;  n = 100; fs = 22 },
  [pscustomobject]@{ name = 'Inter fs20  100 zeros';    y0 = 82;  y1 = 118; n = 100; fs = 20 },
  [pscustomobject]@{ name = 'CJK   fs24  100 zeros';    y0 = 120; y1 = 158; n = 100; fs = 24 },
  [pscustomobject]@{ name = 'mono  fs21  100 zeros';    y0 = 158; y1 = 196; n = 100; fs = 21 },
  [pscustomobject]@{ name = 'mono  fs22  sample line';  y0 = 196; y1 = 234; n = -1;  fs = 22 },
  [pscustomobject]@{ name = 'CJK   fs24  100 zeros b';  y0 = 236; y1 = 274; n = 100; fs = 24 },
  [pscustomobject]@{ name = 'CJK   fs30  4cjk+sp+36z';  y0 = 274; y1 = 305; n = -1;  fs = 30 }
)
foreach ($b in $bands) {
  $minx = -1; $maxx = -1
  for ($x = 0; $x -lt $bmp.Width; $x++) {
    $hit = $false
    for ($y = $b.y0; $y -le $b.y1; $y++) {
      if ($y -ge $bmp.Height) { break }
      $p = $bmp.GetPixel($x, $y)
      $lum = 0.299 * $p.R + 0.587 * $p.G + 0.114 * $p.B
      if ($lum -lt 150) { $hit = $true; break }
    }
    if ($hit) { if ($minx -lt 0) { $minx = $x }; $maxx = $x }
  }
  if ($minx -lt 0) { Write-Output ("{0}: no ink" -f $b.name); continue }
  $w = $maxx - $minx + 1
  if ($b.n -gt 0) {
    $adv = [math]::Round($w / $b.n, 3)
    Write-Output ("{0}: x {1}..{2}  ink={3}px  n={4}  advance={5}px/char  = {6} em" -f $b.name, $minx, $maxx, $w, $b.n, $adv, [math]::Round($adv / $b.fs, 4))
  } else {
    $adv20 = 10.0
    Write-Output ("{0}: x {1}..{2}  ink={3}px  -> implied n at 10.0px/char = {4}; at 13.2px/char = {5}" -f $b.name, $minx, $maxx, $w, [math]::Round($w / 10.0, 1), [math]::Round($w / 13.2, 1))
  }
}
$bmp.Dispose()
