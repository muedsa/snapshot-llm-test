$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
Add-Type -AssemblyName System.Drawing
$PNG = $args[0]; $X = [int]$args[1]; $Y0 = [int]$args[2]; $Y1 = [int]$args[3]
$bmp = New-Object System.Drawing.Bitmap((Resolve-Path $PNG).Path)
$prev = $null
for ($y = $Y0; $y -le $Y1; $y++) {
  $p = $bmp.GetPixel($X,$y)
  $hex = '#{0:X2}{1:X2}{2:X2}' -f $p.R,$p.G,$p.B
  $d = ''
  if ($prev) {
    $delta = [math]::Abs($p.R-$prev[0]) + [math]::Abs($p.G-$prev[1]) + [math]::Abs($p.B-$prev[2])
    $d = 'delta=' + $delta
  }
  $prev = @($p.R,$p.G,$p.B)
  Write-Output ("y{0}  {1}  {2}" -f $y,$hex,$d)
}
$bmp.Dispose()
