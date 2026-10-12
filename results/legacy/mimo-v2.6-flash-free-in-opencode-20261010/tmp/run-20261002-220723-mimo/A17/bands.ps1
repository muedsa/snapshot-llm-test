$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
Add-Type -AssemblyName System.Drawing
# usage: bands.ps1 png x0 x1 y0 y1 hexBg threshold
$PNG = $args[0]; $X0 = [int]$args[1]; $X1 = [int]$args[2]; $Y0 = [int]$args[3]; $Y1 = [int]$args[4]
$bgH = $args[5]; $thr = [int]$args[6]
if ($thr -eq 0) { $thr = 40 }
$h = $bgH.TrimStart('#')
$r0 = [Convert]::ToInt32($h.Substring(0,2),16); $g0 = [Convert]::ToInt32($h.Substring(2,2),16); $b0 = [Convert]::ToInt32($h.Substring(4,2),16)
$bmp = New-Object System.Drawing.Bitmap((Resolve-Path $PNG).Path)
$rows = @()
for ($y = $Y0; $y -le $Y1 -and $y -lt $bmp.Height; $y++) {
  $ink = $false
  for ($x = $X0; $x -le $X1 -and $x -lt $bmp.Width; $x++) {
    $p = $bmp.GetPixel($x,$y)
    $d = [math]::Abs($p.R - $r0) + [math]::Abs($p.G - $g0) + [math]::Abs($p.B - $b0)
    if ($d -gt $thr) { $ink = $true; break }
  }
  $rows += ,$ink
}
$bands = New-Object System.Collections.Generic.List[object]
$start = -1
for ($i = 0; $i -lt $rows.Count; $i++) {
  if ($rows[$i] -and $start -lt 0) { $start = $i }
  if ((-not $rows[$i] -or $i -eq $rows.Count - 1) -and $start -ge 0) {
    $end = $i - 1
    if (-not $rows[$i]) { $end = $i - 1 } else { $end = $i }
    $bands.Add([pscustomobject]@{ top = ($Y0 + $start); bottom = ($Y0 + $end); h = ($end - $start + 1) })
    $start = -1
  }
}
Write-Output ("bands = {0}" -f $bands.Count)
$prev = $null
foreach ($b in $bands) {
  $pitch = ''
  if ($prev -ne $null) { $pitch = '  pitch=' + ($b.top - $prev) }
  Write-Output ("  y {0}..{1}  h={2}{3}" -f $b.top, $b.bottom, $b.h, $pitch)
  $prev = $b.top
}
$bmp.Dispose()
